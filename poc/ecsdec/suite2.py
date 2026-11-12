"""ED2: ECS-Decision with sketched geometry on GPT-2 base (docs/math-track-ed2-prereg.md).

  /usr/bin/python3 -m poc.ecsdec.suite2 pilot      the declared pilot's first block (teacher scan, fit curves)
  /usr/bin/python3 -m poc.ecsdec.suite2 pilot2     its second block (exhausted students, sketches, fits, real data)
  /usr/bin/python3 -m poc.ecsdec.suite2 run        the frozen suite -> poc/results/ed2/ed2.json
  /usr/bin/python3 -m poc.ecsdec.suite2 real       the real-data case alone -> poc/results/ed2/real.json

State: for each probe context (16 tokens from this repository's documents), the model's next-token
probabilities on the base model's top-256 tokens with the document's actual next token swapped in; flattened.
Targets: teacher adapters (a LoRA of known module and rank fitted briefly on the documents, so the truth is
known and the delta lies in directions the model is sensitive to), or the documents' next tokens themselves
(one-hot on the support) for the real-data case.
"""
from __future__ import annotations
import json, sys, time, glob
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import sketch as SK

OUT = Path(__file__).resolve().parents[2] / "poc/results/ed2"; OUT.mkdir(parents=True, exist_ok=True)
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
CTX, SUPPORT = 16, 256
LIBRARY = [f"{n}@{l}" for l in (3, 7, 11) for n in ("v", "o", "fc", "proj")]


def corpus(seed, n_tr, n_ho, tok):
    """Probe contexts: n_tr from even-indexed docs, n_ho from odd-indexed docs (held out by file)."""
    files = sorted(glob.glob(str(Path(__file__).resolve().parents[2] / "docs/*.md"))); rng = np.random.default_rng(seed)
    def draw(fs, n):
        toks = [np.array(tok.encode(open(f).read())) for f in fs]; out = []
        while len(out) < n:
            t = toks[rng.integers(len(toks))]
            if len(t) < CTX + 2: continue
            i = rng.integers(0, len(t) - CTX - 1); out.append(t[i:i + CTX + 1])
        return np.stack(out)
    return draw(files[::2], n_tr), draw(files[1::2], n_ho)


class World:
    """Probe sets, support sets and the state functions. Every state function takes the weights P as an
    argument so that jitted programs built on it receive P at run time (never folded in as constants).
    positions="last": the state is each context's last-position distribution (the planted cases);
    positions="all": every position's distribution, each on its own support (the real-data case)."""
    def __init__(self, P, toks_tr, toks_ho, positions="last"):
        self.P = P; self.shape_of = GM.shape_of; self.positions = positions
        sl = (lambda a: a[:, -1:, :]) if positions == "last" else (lambda a: a)
        f = jax.jit(lambda P, t: jax.nn.softmax(sl(GM.forward(P, t)), -1))
        self.toks = dict(tr=jnp.asarray(toks_tr[:, :CTX]), ho=jnp.asarray(toks_ho[:, :CTX]))
        self.nxt = dict(tr=toks_tr[:, CTX:CTX + 1] if positions == "last" else toks_tr[:, 1:CTX + 1], ho=toks_ho[:, CTX:CTX + 1] if positions == "last" else toks_ho[:, 1:CTX + 1]); self.idx = {}
        for s in ("tr", "ho"):
            p = np.asarray(f(P, self.toks[s])); idx = np.argsort(-p, -1)[..., :SUPPORT]
            for i in range(idx.shape[0]):
                for j in range(idx.shape[1]):
                    if self.nxt[s][i, j] not in idx[i, j]: idx[i, j, -1] = self.nxt[s][i, j]
            self.idx[s] = jnp.asarray(idx)
        self._sl = sl; self.base = {s: np.asarray(self._state(s, {}, P)) for s in ("tr", "ho")}
    def base_state(self, s): return self.base[s]
    def _state(self, s, deltas, P):
        p = jax.nn.softmax(self._sl(GM.forward(P, self.toks[s], deltas)), -1); return jnp.take_along_axis(p, self.idx[s], -1).reshape(-1)
    def _G(self, s, fam, extra):
        def G(theta, P):
            d = SK.deltas_of(fam, theta, self.shape_of)
            if extra:
                for k, v in extra.items(): d[k] = d.get(k, 0) + v
            return self._state(s, d, P)
        return G
    def G(self, fam, extra=None): return self._G("tr", fam, extra)
    def Gh(self, fam, extra=None): return self._G("ho", fam, extra)
    def state(self, s, deltas): return self._state(s, deltas, self.P)
    def delta_products(self, extra, library, s="tr"):
        """One compiled JVP and one compiled VJP for dense deltas on every library module at once (the
        tangent or cotangent is a dict over the library), so the candidate sketches compile twice per
        case rather than three times per module. Returns (jvp(module, D), vjp(module, y))."""
        zeros = {m: jnp.zeros(self.shape_of(m), jnp.float32) for m in library}
        def f(D, P):
            d = dict(extra)
            for m in library: d[m] = d.get(m, 0) + D[m]
            return self._state(s, d, P)
        jv = jax.jit(lambda T, P: jax.jvp(lambda D: f(D, P), (zeros,), (T,))[1]); vj = jax.jit(lambda y, P: jax.vjp(lambda D: f(D, P), zeros)[1](y)[0])
        def jvp(module, D): T = dict(zeros); T[module] = D; return jv(T, self.P)
        def vjp(module, y): return vj(y, self.P)[module]
        return jvp, vjp
    def onehot(self, s):
        idx = np.asarray(self.idx[s]); x = np.zeros(idx.shape, np.float32)
        for i in range(idx.shape[0]):
            for j in range(idx.shape[1]): x[i, j, np.where(idx[i, j] == self.nxt[s][i, j])[0][0]] = 1.0
        return jnp.asarray(x.reshape(-1))
    def nll(self, s, fam, theta):
        """Held-out cross-entropy on the full vocabulary over the positions the state covers."""
        d = SK.deltas_of(fam, theta, self.shape_of); lp = jax.nn.log_softmax(self._sl(jax.jit(GM.forward)(self.P, self.toks[s], d)), -1)
        return float(-jnp.take_along_axis(lp, jnp.asarray(self.nxt[s])[..., None], -1).mean())


def planted(key, module, rank, scale):
    """A random-direction delta (the first pilot showed these are directions the model is insensitive to)."""
    a, b = GM.shape_of(module); k1, k2 = jax.random.split(key)
    return {module: scale * (jax.random.normal(k2, (a, rank)) / np.sqrt(rank)) @ (jax.random.normal(k1, (rank, b)) / np.sqrt(b))}


def teacher(W, module, rank, key, steps, lr, amp=1.0):
    """A teacher adapter: a rank-`rank` LoRA on `module` fitted on the training probes' next tokens for
    `steps` steps, its delta amplified by `amp`; the target of the planted cases."""
    fam = [(module, rank)]; th, _ = SK.fit(W.G(fam), W.onehot("tr"), SK.init_theta(fam, key, W.shape_of), steps, lr, W.P)
    return {module: amp * SK.deltas_of(fam, th, W.shape_of)[module]}


def target(W, deltas):
    return jnp.asarray(np.asarray(W.state("tr", deltas))), jnp.asarray(np.asarray(W.state("ho", deltas)))


def student(W, fam, x, key, steps, lr, frac=1.0, restarts=1):
    best = None
    for k in jax.random.split(key, restarts):
        th, Fv = SK.fit(W.G(fam), x, SK.init_theta(fam, k, W.shape_of), max(1, int(frac * steps)), lr, W.P)
        if best is None or Fv < best[1]: best = (th, Fv)
    return best[0]


def build_case(name, W, key, cfg):
    steps, lr = cfg["steps"], cfg["lr"]; ks = jax.random.split(key, 4); T = lambda m, r: teacher(W, m, r, ks[0], cfg["teacher_steps"], cfg["teacher_lr"], cfg["teacher_amp"])
    if name in ("refine", "saddle", "adequate"):
        x, xh = target(W, T("v@7", 2)); fam = [("v@7", 2)]
        if name == "saddle": return "GLOBALIZE", fam, jnp.zeros(SK.family_size(fam, W.shape_of), jnp.float32), x, xh
        if name == "adequate": return "STOP", fam, student(W, fam, x, ks[2], steps, lr, cfg["adequate_frac"], cfg["student_restarts"]), x, xh
        return "REFINE", fam, student(W, fam, x, ks[2], steps, lr, cfg["refine_frac"]), x, xh
    if name == "reuse":
        x, xh = target(W, T("v@7", 3)); fam = [("v@7", 1)]; return "EXPAND:v@7", fam, student(W, fam, x, ks[2], steps, lr, 1.0, cfg["student_restarts"]), x, xh
    if name == "extend":
        x, xh = target(W, T("fc@7", 2)); fam = [("v@7", 2)]; return "EXPAND:fc@7", fam, student(W, fam, x, ks[2], steps, lr, 1.0, cfg["student_restarts"]), x, xh
    if name == "noise":
        x = jnp.asarray(W.base["tr"]); xh = jnp.asarray(W.base["ho"]); rms = float(jnp.sqrt(jnp.mean(x ** 2))); k1, k2 = jax.random.split(ks[1]); a = cfg["noise_level"] * rms
        x = x + a * jax.random.normal(k1, x.shape); xh = xh + a * jax.random.normal(k2, xh.shape); fam = [("v@7", 2)]
        return "FALLBACK", fam, student(W, fam, x, ks[2], steps, lr, 1.0, cfg["student_restarts"]), x, xh
    if name == "real":
        x, xh = W.onehot("tr"), W.onehot("ho"); fam = [("v@7", 2)]; return "?", fam, student(W, fam, x, ks[2], steps, lr, 1.0, cfg["student_restarts"]), x, xh
    raise ValueError(name)


def run_case(name, W, key, cfg):
    truth, fam, th, x, xh = build_case(name, W, key, cfg); log(f"case {name}: truth {truth}")
    rec = SK.decide(W, fam, th, x, xh, LIBRARY, jax.random.fold_in(key, 7), cfg["steps"], cfg["lr"], log=log, sweep=(name == "real"))
    got = rec["action"] + (":" + rec["chosen"] if rec["action"] == "EXPAND" else ""); rec.update(case=name, truth=truth, got=got, correct=(got == truth) if truth != "?" else None)
    if name == "real":
        rec["nll_held"] = dict(base=W.nll("ho", [], jnp.zeros(0)), current=W.nll("ho", fam, th))
    log(f"  -> {got} ({'ok' if rec['correct'] else 'MISS' if rec['correct'] is False else 'reported'}) fits {rec['fits_run']}")
    return rec


def make_world(seed, n_tr, n_ho, positions="last"):
    P = GM.load_params(); tok = GM.tokenizer(); tr, ho = corpus(seed, n_tr, n_ho, tok); return World(P, tr, ho, positions)


def pilot():
    T0 = time.time(); W = make_world(0, 48, 48); log(f"world: {len(W.toks['tr'])} train and {len(W.toks['ho'])} held-out probes, state dim {W.base['tr'].size} ({time.time() - T0:.0f}s)")
    key = jax.random.PRNGKey(100); x1 = W.onehot("tr")
    for mod, r in (("v@7", 2), ("v@7", 3), ("fc@7", 2)):
        for tsteps, tlr in ((5, 1e-3), (10, 1e-3), (20, 1e-3), (10, 3e-3)):
            t = time.time(); d = teacher(W, mod, r, key, tsteps, tlr); x, xh = target(W, d)
            log(f"teacher rank {r} on {mod}, {tsteps} steps at lr {tlr}: distance base to target {SK.normD(x, W.base['tr']):.3f} (held {SK.normD(xh, W.base['ho']):.3f}), |delta|_F {float(jnp.linalg.norm(d[mod])):.2f} ({time.time() - t:.0f}s)")
    log(f"pilot done in {time.time() - T0:.0f}s")


def pilot2():
    """The second declared pilot block, on the chosen teacher (10 steps at 3e-3): the exhausted students, the
    budget, the sketches, the joint fits, the real-data world."""
    T0 = time.time(); W = make_world(0, 48, 48); key = jax.random.PRNGKey(100)
    cfg = dict(steps=60, lr=3e-3, refine_frac=0.1, adequate_frac=2.0, noise_level=0.5, student_restarts=1, teacher_steps=10, teacher_lr=3e-3, teacher_amp=2.0)
    x, xh = target(W, teacher(W, "v@7", 2, key, cfg["teacher_steps"], cfg["teacher_lr"], cfg["teacher_amp"])); fam = [("v@7", 2)]
    for steps in (6, 60, 120):
        t = time.time(); th = student(W, fam, x, jax.random.PRNGKey(5), steps, cfg["lr"]); st = SK.stationarity(W.G(fam), x, th, jax.random.PRNGKey(1), W.P)
        log(f"rank-2 student on its teacher, {steps:>3} steps: D {SK.normD(x, x - st['r']):.4f} D_held {SK.normD(xh, W.Gh(fam)(th, W.P)):.4f} s {st['stat']:.2e} ({time.time() - t:.0f}s)")
    log(f"  base to target: {SK.normD(x, W.base['tr']):.4f} (held {SK.normD(xh, W.base['ho']):.4f})")
    for name, k in (("extend", 6), ("noise", 8)):
        t = time.time(); truth, f, th, xx, xxh = build_case(name, W, jax.random.PRNGKey(k), cfg); st = SK.stationarity(W.G(f), xx, th, jax.random.PRNGKey(1), W.P); cv = SK.curvature(W.G(f), xx, th, jax.random.PRNGKey(2), W.P)
        log(f"{name} student fitted: D {SK.normD(xx, xx - st['r']):.4f} D_held {SK.normD(xxh, W.Gh(f)(th, W.P)):.4f} s {st['stat']:.2e} lam_min {cv['lam_min']:.2e} |H| {cv['hnorm']:.2e} ({time.time() - t:.0f}s)")
        if name == "extend":
            F0 = 0.5 * float(st["r"] @ st["r"]); best = F0; t = time.time()
            for kk in jax.random.split(jax.random.PRNGKey(11), SK.TH["multistarts"]):
                _, Fv = SK.fit(W.G(f), xx, SK.init_theta(f, kk, W.shape_of, 0.02, 0.02), cfg["steps"], cfg["lr"], W.P); best = min(best, Fv)
            log(f"  budget of {SK.TH['multistarts']}: F {F0:.4e} -> {best:.4e} ({100 * (1 - best / F0):.1f} percent) ({time.time() - t:.0f}s)")
            t = time.time(); Q_T = SK.tangent_sketch(W.G(f), th, jax.random.PRNGKey(3), W.P); r = st["r"].astype(np.float64); r_perp = r - Q_T @ (Q_T.T @ r); log(f"  tangent sketch: tau {1 - (r_perp @ r_perp) / (r @ r):.3f} ({time.time() - t:.0f}s)")
            extra = SK.deltas_of(f, th, W.shape_of); cg = {}; t = time.time()
            jvp_d, vjp_d = W.delta_products(extra, LIBRARY)
            for i, m in enumerate(LIBRARY): cg[m] = SK.candidate_sketch(jvp_d, vjp_d, m, W.shape_of(m), jax.random.fold_in(jax.random.PRNGKey(4), i), Q_T, r_perp)
            log(f"  candidate sketches ({time.time() - t:.0f}s), eta p1/p3/p12/sketch: " + ", ".join(f"{m} {c['eta'][1]:.3f}/{c['eta'][3]:.3f}/{c['eta'][12]:.3f}/{c['eta_sketch']:.3f}" for m, c in cg.items()))
            for a, b in (("v@7", "o@7"), ("fc@7", "proj@7"), ("v@7", "fc@7")):
                pg = SK.pair_geometry(cg[a], cg[b]); log(f"  pair {a}|{b}: containment {pg['c_ij']:.2f}/{pg['c_ji']:.2f} align {pg['align']:.3f} " + " ".join(f"p{p} mu {v['mu']:.2f} d {v['d']:.2f}" for p, v in pg["p"].items()))
            rk = SK.TH["cand_rank"]
            for m in ("fc@7", "proj@7", "v@7", "o@11"):
                t = time.time(); jf = list(f) + [(m, rk)]; th0 = jnp.concatenate([th, SK.init_theta([(m, rk)], jax.random.PRNGKey(12), W.shape_of)]); thj, Fv = SK.fit(W.G(jf), xx, th0, cfg["steps"], cfg["lr"], W.P)
                log(f"  joint fit with {m}: D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(xx))):.4f} D_held {SK.normD(xxh, W.Gh(jf)(thj, W.P)):.4f} ({time.time() - t:.0f}s)")
            jf = list(f) + [(m, rk) for m in LIBRARY]; th0 = jnp.concatenate([th, SK.init_theta([(m, rk) for m in LIBRARY], jax.random.PRNGKey(12), W.shape_of)]); t = time.time(); thj, Fv = SK.fit(W.G(jf), xx, th0, cfg["steps"], cfg["lr"], W.P)
            log(f"  joint fit with the fallback ({SK.family_size(jf, W.shape_of)} params): D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(xx))):.4f} D_held {SK.normD(xxh, W.Gh(jf)(thj, W.P)):.4f} ({time.time() - t:.0f}s)")
    t = time.time(); W2 = make_world(1, 96, 96); x, xh = W2.onehot("tr"), W2.onehot("ho"); f = [("v@7", 2)]
    log(f"real world: base D {SK.normD(x, W2.base['tr']):.4f} held {SK.normD(xh, W2.base['ho']):.4f} nll_held {W2.nll('ho', [], jnp.zeros(0)):.3f} ({time.time() - t:.0f}s)")
    for lr in (1e-3, 3e-3):
        t = time.time(); th = student(W2, f, x, jax.random.PRNGKey(5), 60, lr); st = SK.stationarity(W2.G(f), x, th, jax.random.PRNGKey(1), W2.P)
        log(f"real student rank-2 v@7 lr {lr} 60 steps: D {SK.normD(x, x - st['r']):.4f} D_held {SK.normD(xh, W2.Gh(f)(th, W2.P)):.4f} s {st['stat']:.2e} nll_held {W2.nll('ho', f, th):.3f} ({time.time() - t:.0f}s)")
    log(f"pilot2 done in {time.time() - T0:.0f}s")


def pilot3():
    """The third declared pilot block: the linearised held-out gain as the proposal score, on the extend
    case and on the real-data world, beside the matched-p score."""
    T0 = time.time(); W = make_world(0, 48, 48); key = jax.random.PRNGKey(100)
    cfg = dict(steps=60, lr=3e-3, refine_frac=0.1, adequate_frac=2.0, noise_level=0.5, student_restarts=1, teacher_steps=10, teacher_lr=3e-3, teacher_amp=2.0)
    def gains(W, f, th, xx, xxh, tag):
        t = time.time(); st = SK.stationarity(W.G(f), xx, th, jax.random.PRNGKey(1), W.P); Q_T = SK.tangent_sketch(W.G(f), th, jax.random.PRNGKey(3), W.P)
        r = st["r"].astype(np.float64); r_perp = r - Q_T @ (Q_T.T @ r); r_held = np.asarray(xxh) - np.asarray(W.Gh(f)(th, W.P)); extra = SK.deltas_of(f, th, W.shape_of)
        jvp_d, vjp_d = W.delta_products(extra, LIBRARY); jvp_h, _ = W.delta_products(extra, LIBRARY, "ho"); out = {}
        for i, m in enumerate(LIBRARY):
            c = SK.candidate_sketch(jvp_d, vjp_d, m, W.shape_of(m), jax.random.fold_in(jax.random.PRNGKey(4), i), Q_T, r_perp)
            c.update(SK.linearised_gain(jvp_d, vjp_d, jvp_h, m, W.shape_of(m), SK.TH["cand_rank"], r_perp, r_held, jax.random.fold_in(jax.random.PRNGKey(4), 100 + i))); out[m] = c
            log(f"  {tag} {m}: eta12 {c['eta'][12]:.3f} gain train {c['gain_train']:.3f} held {c['gain_held']:.3f} |delta| {c['delta_norm']:.3f} ({time.time() - t:.0f}s)")
        rank = sorted(LIBRARY, key=lambda m: -out[m]["gain_held"]); log(f"  {tag} ranking by held gain: {rank}"); return out
    truth, f, th, xx, xxh = build_case("extend", W, jax.random.PRNGKey(6), cfg); log(f"extend: D {SK.normD(xx, W.G(f)(th, W.P)):.4f} D_held {SK.normD(xxh, W.Gh(f)(th, W.P)):.4f}")
    gains(W, f, th, xx, xxh, "extend")
    for m in ("fc@7", "proj@11", "v@11", "v@3"):
        t = time.time(); jf = list(f) + [(m, 2)]; th0 = jnp.concatenate([th, SK.init_theta([(m, 2)], jax.random.PRNGKey(12), W.shape_of)]); thj, Fv = SK.fit(W.G(jf), xx, th0, cfg["steps"], cfg["lr"], W.P)
        log(f"  extend joint fit with {m}: D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(xx))):.4f} D_held {SK.normD(xxh, W.Gh(jf)(thj, W.P)):.4f} ({time.time() - t:.0f}s)")
    t = time.time(); W2 = make_world(1, 96, 96); x, xh = W2.onehot("tr"), W2.onehot("ho"); f = [("v@7", 2)]
    log(f"real world: base D {SK.normD(x, W2.base['tr']):.4f} held {SK.normD(xh, W2.base['ho']):.4f} nll_held {W2.nll('ho', [], jnp.zeros(0)):.3f} ({time.time() - t:.0f}s)")
    t = time.time(); th = student(W2, f, x, jax.random.PRNGKey(5), 60, 3e-3); st = SK.stationarity(W2.G(f), x, th, jax.random.PRNGKey(1), W2.P); cv = SK.curvature(W2.G(f), x, th, jax.random.PRNGKey(2), W2.P)
    log(f"real student rank-2 v@7: D {SK.normD(x, x - st['r']):.4f} D_held {SK.normD(xh, W2.Gh(f)(th, W2.P)):.4f} s {st['stat']:.2e} lam_min {cv['lam_min']:.2e} |H| {cv['hnorm']:.2e} nll_held {W2.nll('ho', f, th):.3f} ({time.time() - t:.0f}s)")
    gains(W2, f, th, x, xh, "real")
    for m in ("fc@11", "v@3", "proj@7"):
        t = time.time(); jf = list(f) + [(m, 2)]; th0 = jnp.concatenate([th, SK.init_theta([(m, 2)], jax.random.PRNGKey(12), W2.shape_of)]); thj, Fv = SK.fit(W2.G(jf), x, th0, cfg["steps"], cfg["lr"], W2.P)
        log(f"  real joint fit with {m}: D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(x))):.4f} D_held {SK.normD(xh, W2.Gh(jf)(thj, W2.P)):.4f} nll_held {W2.nll('ho', jf, thj):.3f} ({time.time() - t:.0f}s)")
    log(f"pilot3 done in {time.time() - T0:.0f}s")


def pilot4():
    """The fourth declared pilot block: the real-data case with every position as a target."""
    T0 = time.time(); W2 = make_world(1, 96, 96, "all"); x, xh = W2.onehot("tr"), W2.onehot("ho"); f = [("v@7", 2)]
    log(f"real world (all positions): state dim {x.size}, base D {SK.normD(x, W2.base['tr']):.4f} held {SK.normD(xh, W2.base['ho']):.4f} nll_held {W2.nll('ho', [], jnp.zeros(0)):.3f} ({time.time() - T0:.0f}s)")
    for lr in (1e-3, 3e-3):
        t = time.time(); th = student(W2, f, x, jax.random.PRNGKey(5), 60, lr); st = SK.stationarity(W2.G(f), x, th, jax.random.PRNGKey(1), W2.P)
        log(f"real student rank-2 v@7 lr {lr}: D {SK.normD(x, x - st['r']):.4f} D_held {SK.normD(xh, W2.Gh(f)(th, W2.P)):.4f} s {st['stat']:.2e} nll_held {W2.nll('ho', f, th):.3f} ({time.time() - t:.0f}s)")
    th = student(W2, f, x, jax.random.PRNGKey(5), 60, 3e-3); t = time.time(); cv = SK.curvature(W2.G(f), x, th, jax.random.PRNGKey(2), W2.P); log(f"  lam_min {cv['lam_min']:.2e} |H| {cv['hnorm']:.2e} ({time.time() - t:.0f}s)")
    st = SK.stationarity(W2.G(f), x, th, jax.random.PRNGKey(1), W2.P); Q_T = SK.tangent_sketch(W2.G(f), th, jax.random.PRNGKey(3), W2.P); r = st["r"].astype(np.float64); r_perp = r - Q_T @ (Q_T.T @ r)
    r_held = np.asarray(xh) - np.asarray(W2.Gh(f)(th, W2.P)); extra = SK.deltas_of(f, th, W2.shape_of); jvp_d, vjp_d = W2.delta_products(extra, LIBRARY); jvp_h, _ = W2.delta_products(extra, LIBRARY, "ho")
    for i, m in enumerate(("fc@11", "v@3", "proj@7")):
        t = time.time(); c = SK.linearised_gain(jvp_d, vjp_d, jvp_h, m, W2.shape_of(m), 2, r_perp, r_held, jax.random.PRNGKey(100 + i)); log(f"  real {m}: gain train {c['gain_train']:.3f} held {c['gain_held']:.3f} ({time.time() - t:.0f}s)")
    for m in ("fc@11", "v@3"):
        t = time.time(); jf = list(f) + [(m, 2)]; th0 = jnp.concatenate([th, SK.init_theta([(m, 2)], jax.random.PRNGKey(12), W2.shape_of)]); thj, Fv = SK.fit(W2.G(jf), x, th0, 60, 3e-3, W2.P)
        log(f"  real joint fit with {m}: D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(x))):.4f} D_held {SK.normD(xh, W2.Gh(jf)(thj, W2.P)):.4f} nll_held {W2.nll('ho', jf, thj):.3f} ({time.time() - t:.0f}s)")
    log(f"pilot4 done in {time.time() - T0:.0f}s")


def run(mode):
    global LIBRARY
    cfg = json.load(open(OUT / "config.json")); SK.TH.update(cfg["thresholds"]); LIBRARY = list(cfg["library"]); T0 = time.time(); out = dict(rows=[])
    if mode == "run":
        W = make_world(cfg["seed"], cfg["n_probe"], cfg["n_probe"])
        for i, name in enumerate(("refine", "saddle", "extend", "noise", "adequate")):
            rec = run_case(name, W, jax.random.PRNGKey(1000 + i), cfg); out["rows"].append(rec); log(f"[{time.time() - T0:.0f}s]")
        fn = "ed2.json"
    else:
        W = make_world(cfg["seed"] + 1, cfg["n_probe_real"], cfg["n_probe_real"], "all"); rec = run_case("real", W, jax.random.PRNGKey(2000), cfg)
        out["rows"].append(rec); fn = "real.json"
    out["seconds"] = time.time() - T0
    json.dump(out, open(OUT / fn, "w"), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)); log(f"done -> {fn} in {out['seconds']:.0f}s")


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    pilot() if a == "pilot" else pilot2() if a == "pilot2" else pilot3() if a == "pilot3" else pilot4() if a == "pilot4" else run(a)
