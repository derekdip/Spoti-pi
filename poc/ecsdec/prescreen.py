"""A pre-screen for where to put a LoRA adapter, in cross-entropy, from the base model (ED4,
docs/math-track-ed4-prereg.md).

  /usr/bin/python3 -m poc.ecsdec.prescreen pilot            the declared pilot (nothing scored)
  /usr/bin/python3 -m poc.ecsdec.prescreen run              the frozen conditions -> poc/results/ed4/ed4.json
  /usr/bin/python3 -m poc.ecsdec.prescreen tool altcaps     the tool: go/no-go and the modules to try, no fits

The model is GPT-2 base (poc/ecsdec/gpt2.py); the data is this repository's documents under a format
transform, split by file; the loss is next-token cross-entropy on the full vocabulary at every position.
For each library module m, with G_tr and G_ho the gradients of the training and held-out loss with respect
to the module's weights at the base model (two backward passes serve every module):

  slope     <G_ho, R> / ||R||, R the rank-r truncation of G_tr: the first-order rate at which the held-out
            loss falls along the best rank-r training direction. No further model call.
  step      the held-out gain of that direction at a fixed step eta (one held-out JVP)
  line      the same at the eta that minimises the training loss with logits linearised (two JVPs)
  full      a rank-r adapter fitted in the linearised-logits model by Adam (a JVP and a VJP per step), then
            its held-out gain with logits linearised (ED3's score moved to cross-entropy)
  rgn       ||G_ho|| / ||W||            (Auto-RGN, Lee et al. 2023)
  gradnorm  ||G_tr|| / ||W||            (a training-gradient probe)
  trainline the training gain at the line-search eta (the training-only analogue of `line`)

The sweep fits a rank-r LoRA on each module alone (Adam, a frozen budget, best iterate by training loss) with
one compiled program for every module, and every selector's outcome is read off it.
"""
from __future__ import annotations
import json, sys, time, glob, subprocess
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM

OUT = Path(__file__).resolve().parents[2] / "poc/results/ed4"; OUT.mkdir(parents=True, exist_ok=True)
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
CTX = 16
LIBRARY = [f"{n}@{l}" for l in (2, 5, 8, 11) for n in ("v", "o", "fc", "proj")]


# ---- format transforms
def _altcaps(t):
    out = []; up = False
    for ch in t:
        if ch.isalpha(): out.append(ch.upper() if up else ch.lower()); up = not up
        else: out.append(ch)
    return "".join(out)


def _words(t, f):
    out = []; w = []
    for ch in t + "\0":
        if ch.isalpha(): w.append(ch)
        else:
            if w: out.append(f("".join(w))); w = []
            if ch != "\0": out.append(ch)
    return "".join(out)


_LEET = str.maketrans("aeiostAEIOST", "431057431057")
TRANSFORMS = {"none": lambda t: t, "upper": lambda t: t.upper(), "altcaps": _altcaps, "leet": lambda t: t.translate(_LEET),
              "devowel": lambda t: _words(t, lambda w: w[0] + "".join(c for c in w[1:] if c.lower() not in "aeiou")),
              "reverse": lambda t: _words(t, lambda w: w[::-1])}


CORPUS_COMMIT = None        # None: docs/*.md of the working tree (the pilot ran so); `run` sets it from config.json
_DOCS = {}


def docs_text(commit=None):
    """The corpus: the texts of docs/*.md in name order, from the working tree or from a named commit (git show),
    read once per process, so a run cannot see the files change under it and a scored run can be repeated after
    the docs have grown."""
    if commit not in _DOCS:
        root = Path(__file__).resolve().parents[2]
        if commit is None: _DOCS[commit] = [open(p).read() for p in sorted(glob.glob(str(root / "docs/*.md")))]
        else:
            git = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True, text=True).stdout
            _DOCS[commit] = [git("show", f"{commit}:{p}") for p in sorted(x for x in git("ls-tree", "--name-only", commit, "docs/").split("\n") if x.endswith(".md"))]
    return _DOCS[commit]


def corpus(seed, n, tok, transform):
    texts = docs_text(CORPUS_COMMIT); rng = np.random.default_rng(seed); f = TRANSFORMS[transform]
    def draw(ts):
        toks = [np.array(tok.encode(f(t))) for t in ts]; out = []
        while len(out) < n:
            t = toks[rng.integers(len(toks))]
            if len(t) < CTX + 2: continue
            i = rng.integers(0, len(t) - CTX - 1); out.append(t[i:i + CTX + 1])
        return np.stack(out)
    return draw(texts[::2]), draw(texts[1::2])


def _ce(z, y):
    return -jnp.take_along_axis(jax.nn.log_softmax(z, -1), y[..., None], -1).mean()


class CEWorld:
    """Tokens, the base logits and losses, and one compiled program each for the gradients, the logit JVP and
    VJP over dense deltas on every library module, the loss along a logit direction, and the masked LoRA fit.
    The weights P are a runtime argument of every program."""
    def __init__(self, P, tr, ho, library=LIBRARY, rank=2, steps=60):
        self.P = P; self.lib = list(library); self.rank = rank; self.steps = steps
        self.x = dict(tr=jnp.asarray(tr[:, :CTX]), ho=jnp.asarray(ho[:, :CTX])); self.y = dict(tr=jnp.asarray(tr[:, 1:CTX + 1]), ho=jnp.asarray(ho[:, 1:CTX + 1]))
        zeros = {m: jnp.zeros(GM.shape_of(m), jnp.float32) for m in self.lib}; self.zeros = zeros; lib = self.lib
        logits = lambda P, x, D: GM.forward(P, x, D); loss = lambda P, x, y, D: _ce(logits(P, x, D), y)
        self._logits = jax.jit(lambda P, x: logits(P, x, {})); self._grad = jax.jit(lambda P, x, y: jax.grad(lambda D: loss(P, x, y, D))(zeros))
        self._jvp = jax.jit(lambda P, x, T: jax.jvp(lambda D: logits(P, x, D), (zeros,), (T,))[1])
        self._vjp = jax.jit(lambda P, x, Y: jax.vjp(lambda D: logits(P, x, D), zeros)[1](Y)[0])
        self._line = jax.jit(lambda z0, u, y, eta: _ce(z0 + eta * u, y)); self._pgrad = jax.jit(lambda z, y: (jax.nn.softmax(z, -1) - jax.nn.one_hot(y, z.shape[-1])) / (y.shape[0] * y.shape[1]))
        def lora(params, mask): return {m: mask[i] * (params[m][1] @ params[m][0]) for i, m in enumerate(lib)}
        def fit_run(P, x, y, params0, mask, lr):
            F = lambda p: loss(P, x, y, lora(p, mask)); vg = jax.value_and_grad(F); tm = jax.tree_util.tree_map
            def body(c, i):
                p, m, v, bF, bp = c; L, g = vg(p); m = tm(lambda a, b: 0.9 * a + 0.1 * b, m, g); v = tm(lambda a, b: 0.999 * a + 0.001 * b ** 2, v, g)
                better = L < bF; bF = jnp.where(better, L, bF); bp = tm(lambda a, b: jnp.where(better, b, a), bp, p)
                p = tm(lambda a, mm, vv: a - lr * (mm / (1 - 0.9 ** i)) / (jnp.sqrt(vv / (1 - 0.999 ** i)) + 1e-8), p, m, v); return (p, m, v, bF, bp), L
            z = tm(jnp.zeros_like, params0)
            (p, m, v, bF, bp), _ = jax.lax.scan(body, (params0, z, z, jnp.inf, params0), jnp.arange(1, steps + 1).astype(jnp.float32))
            Lf = F(p); best = tm(lambda a, b: jnp.where(Lf <= bF, a, b), p, bp); return best, jnp.minimum(Lf, bF)
        self._fit = jax.jit(fit_run); self._lora = lora; self._loss_lora = jax.jit(lambda P, x, y, p, mask: loss(P, x, y, lora(p, mask)))
        self.z0 = {s: self._logits(P, self.x[s]) for s in ("tr", "ho")}; self.L0 = {s: float(_ce(self.z0[s], self.y[s])) for s in ("tr", "ho")}
        self.G = {s: self._grad(P, self.x[s], self.y[s]) for s in ("tr", "ho")}

    def direction(self, m):
        """The unit rank-r truncation of minus the training gradient on the module."""
        U, S, Vt = np.linalg.svd(-np.asarray(self.G["tr"][m], np.float64), full_matrices=False); r = self.rank
        R = (U[:, :r] * S[:r]) @ Vt[:r]; return jnp.asarray(R / np.linalg.norm(R), jnp.float32)

    def cheap_scores(self, m):
        """Scores that need no model call beyond the two gradient passes."""
        R = self.direction(m); Gh = self.G["ho"][m]; Gt = self.G["tr"][m]; W = self.P[m]
        return dict(slope=float(-jnp.vdot(Gh, R)), trainslope=float(-jnp.vdot(Gt, R)), rgn=float(jnp.linalg.norm(Gh) / jnp.linalg.norm(W)), gradnorm=float(jnp.linalg.norm(Gt) / jnp.linalg.norm(W)))

    def step_scores(self, m, eta_fixed):
        """The held-out gain along the direction at a fixed step and at the training line-search step."""
        R = self.direction(m); T = dict(self.zeros); T[m] = R; u = {s: self._jvp(self.P, self.x[s], T) for s in ("tr", "ho")}
        f = lambda s, eta: float(self._line(self.z0[s], u[s], self.y[s], eta))
        lo, hi = 0.0, eta_fixed
        while f("tr", hi * 2) < f("tr", hi) and hi < 1e4: hi *= 2                    # bracket the training minimum
        hi *= 2; g = (np.sqrt(5) - 1) / 2; a, b = hi - g * (hi - lo), lo + g * (hi - lo); fa, fb = f("tr", a), f("tr", b)
        for _ in range(14):
            if fa < fb: hi, b, fb = b, a, fa; a = hi - g * (hi - lo); fa = f("tr", a)
            else: lo, a, fa = a, b, fb; b = lo + g * (hi - lo); fb = f("tr", b)
        eta = (lo + hi) / 2
        return dict(step=self.L0["ho"] - f("ho", eta_fixed), line=self.L0["ho"] - f("ho", eta), trainline=self.L0["tr"] - f("tr", eta), eta_line=float(eta))

    def full_score(self, m, key, steps=30, lr=3e-3):
        """A rank-r adapter fitted in the linearised-logits model, then its held-out gain there."""
        a, b = GM.shape_of(m); r = self.rank; A = jax.random.normal(key, (r, b)) * 0.02; B = jnp.zeros((a, r)); mA = 0 * A; vA = 0 * A; mB = 0 * B; vB = 0 * B
        best = (self.L0["tr"], A, B)
        for i in range(1, steps + 1):
            T = dict(self.zeros); T[m] = B @ A; z = self.z0["tr"] + self._jvp(self.P, self.x["tr"], T); L = float(_ce(z, self.y["tr"]))
            if L < best[0]: best = (L, A, B)
            gD = self._vjp(self.P, self.x["tr"], self._pgrad(z, self.y["tr"]))[m]; gB = gD @ A.T; gA = B.T @ gD
            mA = 0.9 * mA + 0.1 * gA; vA = 0.999 * vA + 0.001 * gA ** 2; A = A - lr * (mA / (1 - 0.9 ** i)) / (jnp.sqrt(vA / (1 - 0.999 ** i)) + 1e-8)
            mB = 0.9 * mB + 0.1 * gB; vB = 0.999 * vB + 0.001 * gB ** 2; B = B - lr * (mB / (1 - 0.9 ** i)) / (jnp.sqrt(vB / (1 - 0.999 ** i)) + 1e-8)
        L, A, B = best; T = dict(self.zeros); T[m] = B @ A
        return dict(full=self.L0["ho"] - float(_ce(self.z0["ho"] + self._jvp(self.P, self.x["ho"], T), self.y["ho"])), full_train=self.L0["tr"] - L, full_norm=float(jnp.linalg.norm(B @ A)))

    def fit(self, m, key, lr):
        """The real thing: a rank-r LoRA on the module alone, fitted on the training loss."""
        ks = jax.random.split(key, len(self.lib)); params = {k: (jax.random.normal(ks[i], (self.rank, GM.shape_of(k)[1])) * 0.02, jnp.zeros((GM.shape_of(k)[0], self.rank))) for i, k in enumerate(self.lib)}
        mask = jnp.asarray([1.0 if k == m else 0.0 for k in self.lib]); p, Ltr = self._fit(self.P, self.x["tr"], self.y["tr"], params, mask, lr)
        Lho = float(self._loss_lora(self.P, self.x["ho"], self.y["ho"], p, mask))
        return dict(train=float(Ltr), held=Lho, gain=self.L0["ho"] - Lho, train_gain=self.L0["tr"] - float(Ltr), norm=float(jnp.linalg.norm(p[m][1] @ p[m][0])))


def make_world(seed, n, transform, library=LIBRARY, rank=2, steps=60, P=None, tok=None):
    P = P if P is not None else GM.load_params(); tok = tok or GM.tokenizer(); tr, ho = corpus(seed, n, tok, transform); return CEWorld(P, tr, ho, library, rank, steps)


SELECTORS = ("slope", "step", "line", "full", "rgn", "gradnorm", "trainline", "trainslope")


def read_off(scores, fits, beam=3, seed=0):
    """Every selector's outcome from the sweep: its top-`beam` modules, the best held-out loss among them, and its
    rank correlation with the fitted held-out gain; random placement as one draw's expectation; the sweep's best."""
    mods = list(fits); fitted = np.array([fits[m]["gain"] for m in mods]); out = {}; rk = lambda a: np.argsort(np.argsort(a))
    for s in SELECTORS:
        if any(s not in scores[m] for m in mods): continue
        v = np.array([scores[m][s] for m in mods]); top = [mods[i] for i in np.argsort(-v)[:beam]]
        out[s] = dict(beam=top, best_held=min(fits[m]["held"] for m in top), hit=bool(max(mods, key=lambda m: fits[m]["gain"]) in top),
                      spearman=float(np.corrcoef(rk(v), rk(fitted))[0, 1]), pearson=float(np.corrcoef(v, fitted)[0, 1]))
    rng = np.random.default_rng(seed); draws = [min(fits[m]["held"] for m in rng.choice(mods, size=beam, replace=False)) for _ in range(5000)]
    out["random"] = dict(best_held=float(np.mean(draws)), hit=beam / len(mods)); best = max(mods, key=lambda m: fits[m]["gain"])
    out["sweep"] = dict(best_held=fits[best]["held"], module=best, gain=fits[best]["gain"]); return out


def condition(W, name, cfg, key, full=False):
    """One condition: every score for every module, the sweep, the read-off."""
    t0 = time.time(); scores = {}
    for i, m in enumerate(W.lib):
        s = W.cheap_scores(m); s.update(W.step_scores(m, cfg["eta"]))
        if full: s.update(W.full_score(m, jax.random.fold_in(key, 500 + i)))
        scores[m] = s
    t_scores = time.time() - t0; log(f"  {name}: scores in {t_scores:.0f}s; base loss train {W.L0['tr']:.3f} held {W.L0['ho']:.3f}")
    fits = {}; t1 = time.time()
    for i, m in enumerate(W.lib):
        fits[m] = W.fit(m, jax.random.fold_in(key, i), cfg["lr"])
        log(f"  {name} fit {m}: held {fits[m]['held']:.3f} gain {fits[m]['gain']:+.3f} (train gain {fits[m]['train_gain']:+.3f}, |delta| {fits[m]['norm']:.2f}); slope {scores[m]['slope']:+.4f} step {scores[m]['step']:+.4f} line {scores[m]['line']:+.4f}" + (f" full {scores[m]['full']:+.4f}" if full else "") + f" rgn {scores[m]['rgn']:.4f}")
    ro = read_off(scores, fits, cfg["beam"]); t_fits = time.time() - t1
    log(f"  {name}: sweep best {ro['sweep']['module']} gain {ro['sweep']['gain']:+.3f}; " + "; ".join(f"{s} {ro[s]['best_held']:.3f} hit {ro[s]['hit']} rho {ro[s]['spearman']:+.2f}" for s in SELECTORS if s in ro) + f"; random {ro['random']['best_held']:.3f}; ({t_fits:.0f}s of fits)")
    return dict(name=name, base=W.L0, scores=scores, fits=fits, read=ro, seconds=dict(scores=t_scores, fits=t_fits))


def pilot():
    T0 = time.time(); P = GM.load_params(); tok = GM.tokenizer(); cfg = dict(eta=1.0, lr=1e-3, beam=3)
    for tr in TRANSFORMS:
        a, b = corpus(0, 96, tok, tr); log(f"transform {tr}: sample {tok.decode(a[0][:CTX])!r}")
    out = []
    W = make_world(0, 96, "altcaps", P=P, tok=tok); out.append(condition(W, "altcaps", cfg, jax.random.PRNGKey(0), full=True))
    json.dump(out, open(OUT / "pilot.json", "w"), indent=1, default=float)
    for name, n in (("none", 96),):
        W = make_world(0, n, name, P=P, tok=tok); out.append(condition(W, name, cfg, jax.random.PRNGKey(0))); json.dump(out, open(OUT / "pilot.json", "w"), indent=1, default=float)
    W = make_world(0, 8, "none", P=P, tok=tok); out.append(condition(W, "none-8", cfg, jax.random.PRNGKey(0))); json.dump(out, open(OUT / "pilot.json", "w"), indent=1, default=float)
    log(f"pilot done in {time.time() - T0:.0f}s")


def run():
    global CORPUS_COMMIT
    cfg = json.load(open(OUT / "config.json")); T0 = time.time(); P = GM.load_params(); tok = GM.tokenizer(); out = []
    CORPUS_COMMIT = cfg["corpus_commit"]; log(f"corpus: docs/*.md at {CORPUS_COMMIT}, {len(docs_text(CORPUS_COMMIT))} files")
    for i, c in enumerate(cfg["conditions"]):
        W = make_world(cfg["seed"], c["n"], c["transform"], cfg["library"], cfg["rank"], cfg["steps"], P=P, tok=tok)
        out.append(condition(W, c["name"], cfg, jax.random.PRNGKey(4000 + i), full=c.get("full", False)))
        json.dump(dict(rows=out, seconds=time.time() - T0), open(OUT / "ed4.json", "w"), indent=1, default=float); log(f"[{time.time() - T0:.0f}s]")
    log(f"done -> ed4.json in {time.time() - T0:.0f}s")


def tool(transform="altcaps", n=96, seed=0):
    """The pre-screen as a tool: no fits. Prints whether adapting is predicted to help and which modules to try."""
    cfg = json.load(open(OUT / "config.json")) if (OUT / "config.json").exists() else dict(primary="slope", beam=3, eta=1.0, library=LIBRARY, rank=2, steps=60)
    t = time.time(); W = make_world(seed, n, transform, cfg["library"], cfg["rank"], cfg["steps"]); s = {m: W.cheap_scores(m) for m in W.lib}; key = cfg.get("primary", "slope")
    if key in ("step", "line"):
        for m in W.lib: s[m].update(W.step_scores(m, cfg["eta"]))
    order = sorted(W.lib, key=lambda m: -s[m][key]); best = s[order[0]][key]
    print(f"base held-out loss {W.L0['ho']:.3f}; pre-screen '{key}' in {time.time() - t:.0f}s")
    print("verdict:", "adapt (predicted to help)" if best > 0 else "do not adapt (no module is predicted to help)")
    for m in order[:cfg["beam"]]: print(f"  try {m}: {key} {s[m][key]:+.4f}")


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    pilot() if a == "pilot" else run() if a == "run" else tool(*sys.argv[2:3])
