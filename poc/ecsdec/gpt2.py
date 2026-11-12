"""GPT-2 base (124M) in JAX from the Keras NLP preset's H5 weights, with additive deltas on named modules,
for ED2 (docs/math-track-ed2-prereg.md).

Module keys per layer l (0..11): q@l, k@l, v@l, o@l (768 x 768), fc@l (768 x 3072), proj@l (3072 x 768).
Weights: WEIGHTS_DIR/model.h5, vocab.json, merges.txt (the gpt2_base_en preset, Keras NLP, Apache 2.0).
"""
from __future__ import annotations
import os, json
import numpy as np, jax, jax.numpy as jnp

WEIGHTS_DIR = os.environ.get("GPT2_DIR", "/tmp/claude-0/-home-user-Spoti-pi/1b1f644f-a664-570f-99b3-f54d941ef46d/scratchpad/gpt2_keras")
CFG = dict(vocab=50257, d=768, heads=12, layers=12, hidden=3072, ctx=1024)


def load_params(path=None):
    import h5py
    f = h5py.File(path or os.path.join(WEIGHTS_DIR, "model.h5"), "r"); g = lambda k: jnp.asarray(np.asarray(f[k]))
    P = dict(wte=g("token_embedding/token_embedding/embeddings:0"), wpe=g("position_embedding/position_embedding/embeddings:0"),
             lnf_g=g("layer_norm/layer_norm/gamma:0"), lnf_b=g("layer_norm/layer_norm/beta:0"))
    for l in range(CFG["layers"]):
        p = f"transformer_layer_{l}/transformer_layer_{l}/"; a = p + "multi_head_attention/"
        for n in ("query", "key", "value"):
            P[f"{n[0]}@{l}"] = g(a + n + "/kernel:0").reshape(768, 768); P[f"{n[0]}b@{l}"] = g(a + n + "/bias:0").reshape(768)
        P[f"o@{l}"] = g(a + "attention_output/kernel:0").reshape(768, 768); P[f"ob@{l}"] = g(a + "attention_output/bias:0")
        P[f"fc@{l}"] = g(p + "dense/kernel:0"); P[f"fcb@{l}"] = g(p + "dense/bias:0"); P[f"proj@{l}"] = g(p + "dense_1/kernel:0"); P[f"projb@{l}"] = g(p + "dense_1/bias:0")
        P[f"ln1g@{l}"] = g(p + "layer_normalization/gamma:0"); P[f"ln1b@{l}"] = g(p + "layer_normalization/beta:0")
        P[f"ln2g@{l}"] = g(p + "layer_normalization_1/gamma:0"); P[f"ln2b@{l}"] = g(p + "layer_normalization_1/beta:0")
    return P


MODULES = [f"{n}@{l}" for l in range(CFG["layers"]) for n in ("q", "k", "v", "o", "fc", "proj")]


def shape_of(key):
    n = key.split("@")[0]; return {"q": (768, 768), "k": (768, 768), "v": (768, 768), "o": (768, 768), "fc": (768, 3072), "proj": (3072, 768)}[n]


def _ln(x, g, b):
    m = x.mean(-1, keepdims=True); v = ((x - m) ** 2).mean(-1, keepdims=True); return (x - m) / jnp.sqrt(v + 1e-5) * g + b


def forward(P, toks, deltas=None, cfg=CFG):
    """Logits (B, T, vocab); `deltas` maps module keys to additive deltas."""
    deltas = deltas or {}; W = lambda k: P[k] + deltas[k] if k in deltas else P[k]
    B, T = toks.shape; H = cfg["heads"]; hd = cfg["d"] // H
    h = P["wte"][toks] + P["wpe"][:T][None]; mask = jnp.tril(jnp.ones((T, T), bool))
    for l in range(cfg["layers"]):
        x = _ln(h, P[f"ln1g@{l}"], P[f"ln1b@{l}"])
        q = (x @ W(f"q@{l}") + P[f"qb@{l}"]).reshape(B, T, H, hd); k = (x @ W(f"k@{l}") + P[f"kb@{l}"]).reshape(B, T, H, hd); v = (x @ W(f"v@{l}") + P[f"vb@{l}"]).reshape(B, T, H, hd)
        a = jnp.einsum("bthd,bshd->bhts", q, k) / np.sqrt(hd); a = jnp.where(mask[None, None], a, -1e9); a = jax.nn.softmax(a, -1)
        h = h + jnp.einsum("bhts,bshd->bthd", a, v).reshape(B, T, cfg["d"]) @ W(f"o@{l}") + P[f"ob@{l}"]
        x = _ln(h, P[f"ln2g@{l}"], P[f"ln2b@{l}"])
        h = h + jax.nn.gelu(x @ W(f"fc@{l}") + P[f"fcb@{l}"], approximate=True) @ W(f"proj@{l}") + P[f"projb@{l}"]
    return _ln(h, P["lnf_g"], P["lnf_b"]) @ P["wte"].T


def tokenizer():
    from transformers import GPT2Tokenizer
    return GPT2Tokenizer(os.path.join(WEIGHTS_DIR, "vocab.json"), os.path.join(WEIGHTS_DIR, "merges.txt"))


def nll(P, toks):
    """Mean next-token negative log-likelihood over a (B, T+1) token array."""
    lp = jax.nn.log_softmax(forward(P, toks[:, :-1]), -1)
    return -jnp.take_along_axis(lp, toks[:, 1:, None], -1).mean()


if __name__ == "__main__":
    import sys, time
    P = load_params(); tok = tokenizer(); print("loaded", sum(int(np.prod(v.shape)) for v in P.values()), "parameters")
    text = open(sys.argv[1] if len(sys.argv) > 1 else "README.md").read()
    ids = tok.encode(text)[:16 * 65]; toks = jnp.asarray(np.array(ids[:16 * 65]).reshape(16, 65)); t = time.time()
    print(f"nll on {toks.size} tokens of {sys.argv[1] if len(sys.argv) > 1 else 'README.md'}: {float(nll(P, toks)):.3f} nats ({time.time() - t:.1f}s)")
    for prompt in ("The capital of France is", "import numpy as", "The Treaty of Versailles was signed in"):
        ids = tok.encode(prompt)
        for _ in range(8):
            logits = forward(P, jnp.asarray([ids])); ids.append(int(jnp.argmax(logits[0, -1])))
        print(repr(prompt), "->", repr(tok.decode(ids[len(tok.encode(prompt)):])))
