"""A tiny decoder-only transformer language model in JAX, with additive adapters on named modules, for
the ECS-Decision benchmark (docs/math-track-ed1-prereg.md).

The state the decision rule reads is the model's predictive distribution on a fixed probe set of
contexts: x = probabilities of the next token, one vocab-sized row per probe, flattened. An adapter
family parameterises additive deltas on named weight matrices (LoRA factors B A on a module, a dense
delta, or a logit bias); G(theta) is the adapted model's probe distribution; the target is a model
with planted deltas, so every case's right action is known by construction.

Module keys: wq@l, wk@l, wv@l, wo@l (d x d), w1@l (d x hidden), w2@l (hidden x d); plus out_bias (vocab).
Pre-norm layer norm without learned scale, GELU, causal attention, learned positions. Double precision.
"""
from __future__ import annotations
import os
os.environ.setdefault("XLA_FLAGS", "--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import jax, jax.numpy as jnp, numpy as np
from jax.flatten_util import ravel_pytree
jax.config.update("jax_enable_x64", True)

CFG = dict(vocab=16, d=32, heads=1, layers=2, hidden=64, ctx=16)       # one head: wv@l and wo@l then share one first-order span exactly


def init_params(key, cfg=CFG):
    k = jax.random.split(key, 16); p = {}; s = 0.3
    p["emb"] = jax.random.normal(k[0], (cfg["vocab"], cfg["d"])) * s
    p["pos"] = jax.random.normal(k[1], (cfg["ctx"], cfg["d"])) * s
    for l in range(cfg["layers"]):
        kk = jax.random.split(k[2 + l], 6); d, h = cfg["d"], cfg["hidden"]
        p[f"wq@{l}"] = jax.random.normal(kk[0], (d, d)) / np.sqrt(d); p[f"wk@{l}"] = jax.random.normal(kk[1], (d, d)) / np.sqrt(d)
        p[f"wv@{l}"] = jax.random.normal(kk[2], (d, d)) / np.sqrt(d); p[f"wo@{l}"] = jax.random.normal(kk[3], (d, d)) / np.sqrt(d)
        p[f"w1@{l}"] = jax.random.normal(kk[4], (d, h)) / np.sqrt(d); p[f"w2@{l}"] = jax.random.normal(kk[5], (h, d)) / np.sqrt(h)
    p["unemb"] = jax.random.normal(k[10], (cfg["d"], cfg["vocab"])) / np.sqrt(cfg["d"]); p["out_bias"] = jnp.zeros(cfg["vocab"])
    return p


def _ln(x):
    m = x.mean(-1, keepdims=True); v = ((x - m) ** 2).mean(-1, keepdims=True); return (x - m) / jnp.sqrt(v + 1e-5)


def forward(params, tokens, deltas=None, cfg=CFG):
    """Logits (B, T, vocab). `deltas` maps a module key to an additive delta of the same shape."""
    deltas = deltas or {}
    W = lambda key: params[key] + deltas[key] if key in deltas else params[key]
    B, T = tokens.shape; d, H = cfg["d"], cfg["heads"]; hd = d // H
    h = W("emb")[tokens] + W("pos")[:T][None]
    mask = jnp.tril(jnp.ones((T, T)))
    for l in range(cfg["layers"]):
        x = _ln(h)
        q = (x @ W(f"wq@{l}")).reshape(B, T, H, hd); k = (x @ W(f"wk@{l}")).reshape(B, T, H, hd); v = (x @ W(f"wv@{l}")).reshape(B, T, H, hd)
        att = jnp.einsum("bthd,bshd->bhts", q, k) / np.sqrt(hd); att = jnp.where(mask[None, None] > 0, att, -1e9); att = jax.nn.softmax(att, -1)
        o = jnp.einsum("bhts,bshd->bthd", att, v).reshape(B, T, d); h = h + o @ W(f"wo@{l}")
        x = _ln(h); h = h + jax.nn.gelu(x @ W(f"w1@{l}")) @ W(f"w2@{l}")
    return _ln(h) @ W("unemb") + W("out_bias")


# ---- synthetic language: a sparse Markov chain with a copy rule, enough structure for attention to matter
def make_generator(seed, cfg=CFG):
    rng = np.random.default_rng(seed); V = cfg["vocab"]
    M = rng.random((V, V)) ** 3; M[rng.random((V, V)) < 0.5] = 0; M += 1e-3; M /= M.sum(1, keepdims=True)
    return dict(M=M, p_copy=0.3, offsets=(2, 3))


def sample_sequences(gen, rng, n, T):
    V = gen["M"].shape[0]; out = np.zeros((n, T), int); out[:, 0] = rng.integers(0, V, n)
    for t in range(1, T):
        nxt = np.array([rng.choice(V, p=gen["M"][a]) for a in out[:, t - 1]])
        for i in range(n):
            if t >= 3 and rng.random() < gen["p_copy"]:
                nxt[i] = out[i, t - rng.choice(gen["offsets"])]
        out[:, t] = nxt
    return out


def train_base(key, gen, steps=1500, batch=64, lr=3e-3, cfg=CFG, seed=0, log=None):
    """Train the base model on the generator's sequences with Adam; returns params and the loss curve."""
    params = init_params(key, cfg); rng = np.random.default_rng(seed)
    flat, unflat = ravel_pytree(params)
    def loss(theta, toks):
        logits = forward(unflat(theta), toks[:, :-1], cfg=cfg); lp = jax.nn.log_softmax(logits, -1)
        return -jnp.take_along_axis(lp, toks[:, 1:, None], -1).mean()
    g = jax.jit(jax.value_and_grad(loss)); m = jnp.zeros_like(flat); v = jnp.zeros_like(flat); curve = []
    for i in range(1, steps + 1):
        toks = jnp.asarray(sample_sequences(gen, rng, batch, cfg["ctx"] + 1)); L, grad = g(flat, toks)
        m = 0.9 * m + 0.1 * grad; v = 0.999 * v + 0.001 * grad ** 2; mh = m / (1 - 0.9 ** i); vh = v / (1 - 0.999 ** i)
        flat = flat - lr * mh / (jnp.sqrt(vh) + 1e-8); curve.append(float(L))
        if log and i % 500 == 0: log(f"base step {i} loss {float(L):.3f}")
    return unflat(flat), curve


# ---- adapter families: a list of (module key, kind, rank); kind 'lora' (B A), 'full' (dense delta), 'bias'
def shape_of(key, cfg=CFG):
    if key == "out_bias": return (cfg["vocab"],)
    name = key.split("@")[0]; d, h = cfg["d"], cfg["hidden"]
    return {"wq": (d, d), "wk": (d, d), "wv": (d, d), "wo": (d, d), "w1": (d, h), "w2": (h, d)}[name]


def family_size(fam, cfg=CFG):
    n = 0
    for key, kind, r in fam:
        shp = shape_of(key, cfg)
        n += (r * (shp[0] + shp[1]) if kind == "lora" else (shp[0] * shp[1] if kind == "full" else shp[0]))
    return n


def deltas_of(fam, theta, cfg=CFG):
    """The deltas a family's flat parameter vector encodes."""
    out = {}; i = 0
    for key, kind, r in fam:
        shp = shape_of(key, cfg)
        if kind == "lora":
            A = theta[i:i + r * shp[1]].reshape(r, shp[1]); i += r * shp[1]; Bm = theta[i:i + shp[0] * r].reshape(shp[0], r); i += shp[0] * r
            out[key] = out.get(key, 0) + Bm @ A
        elif kind == "full":
            n = shp[0] * shp[1]; out[key] = out.get(key, 0) + theta[i:i + n].reshape(shp); i += n
        else:
            out[key] = out.get(key, 0) + theta[i:i + shp[0]]; i += shp[0]
    return out


def init_theta(fam, key, scale=0.05, b_scale=0.0, cfg=CFG):
    """LoRA: A random, B zero by default (the usual init); full and bias: zero."""
    parts = []; ks = jax.random.split(key, 2 * len(fam) + 1)
    for j, (k_, kind, r) in enumerate(fam):
        shp = shape_of(k_, cfg)
        if kind == "lora": parts += [jax.random.normal(ks[2 * j], (r * shp[1],)) * scale, jax.random.normal(ks[2 * j + 1], (shp[0] * r,)) * b_scale]
        elif kind == "full": parts.append(jnp.zeros(shp[0] * shp[1]))
        else: parts.append(jnp.zeros(shp[0]))
    return jnp.concatenate(parts)


def probe_fn(params, probes, cfg=CFG):
    """G_of(fam, extra_deltas) -> G: theta -> flattened next-token probabilities on the probe contexts."""
    def G_of(fam, extra_deltas=None):
        def G(theta):
            d = deltas_of(fam, theta, cfg)
            if extra_deltas:
                for k_, v in extra_deltas.items(): d[k_] = d.get(k_, 0) + v
            return jax.nn.softmax(forward(params, probes, d, cfg)[:, -1, :], -1).reshape(-1)
        return G
    return G_of


def fit(G, x, theta0, steps=300, lr=0.02):
    """Least squares F(theta) = 0.5 ||x - G(theta)||^2 by Adam for a frozen number of steps (a jitted scan);
    returns the best iterate seen and its F."""
    F = lambda th: 0.5 * jnp.sum((x - G(th)) ** 2); vg = jax.value_and_grad(F)
    def body(c, i):
        th, m, v, bF, bth = c; L, g = vg(th); m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g ** 2
        better = L < bF; bF = jnp.where(better, L, bF); bth = jnp.where(better, th, bth)
        th = th - lr * (m / (1 - 0.9 ** i)) / (jnp.sqrt(v / (1 - 0.999 ** i)) + 1e-8); return (th, m, v, bF, bth), L
    @jax.jit
    def run(th0):
        (th, m, v, bF, bth), _ = jax.lax.scan(body, (th0, 0 * th0, 0 * th0, jnp.inf, th0), jnp.arange(1, steps + 1).astype(jnp.float64))
        Lf = F(th); return jnp.where(Lf <= bF, th, bth), jnp.minimum(Lf, bF)
    th, Lf = run(theta0); return th, float(Lf)


def jacobian(G, theta, chunk=64):
    """dG/dtheta as a dense (n_out, n_theta) array, by forward-mode in chunks of tangent directions
    (the unchunked jacfwd needs tens of gigabytes on the dense families)."""
    n = theta.shape[0]; jvp = jax.jit(lambda V: jax.vmap(lambda v: jax.jvp(G, (theta,), (v,))[1])(V)); E = jnp.eye(n)
    return np.concatenate([np.asarray(jvp(E[i:i + chunk])) for i in range(0, n, chunk)], 0).T
