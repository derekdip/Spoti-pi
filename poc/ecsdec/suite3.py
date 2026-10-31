"""ED3: adapter placement on GPT-2 under a format shift (docs/math-track-ed3-prereg.md).

  /usr/bin/python3 -m poc.ecsdec.suite3 pilot            the declared pilot (nothing scored)
  /usr/bin/python3 -m poc.ecsdec.suite3 run              the frozen cases -> poc/results/ed3/ed3.json

The world is suite2's (GPT-2 base, this repository's documents, every position a target on its support)
with the documents passed through a format transform (`cfg["transform"]`: "upper" upper-cases them), so
that an adapter learns a rule it can generalise rather than memorise. Cases:
  extend     teacher: a rank-2 adapter on cfg["teacher_module"] fitted on the format targets, doubled;
             student: rank-2 on cfg["student_module"], best of cfg["student_restarts"] fits;
             truth EXPAND on the teacher's module; the sweep is run too so every selector is read off it
  real       the format targets themselves; the rule with the sweep; no truth; every selector read off it
"""
from __future__ import annotations
import json, sys, time, glob
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import sketch as SK
from poc.ecsdec import suite2 as S2

OUT = Path(__file__).resolve().parents[2] / "poc/results/ed3"; OUT.mkdir(parents=True, exist_ok=True)
log = S2.log
def _altcaps(t):
    """Alternating capitalisation of letters, the case of each letter the opposite of the previous letter's."""
    out = []; up = False
    for ch in t:
        if ch.isalpha(): out.append(ch.upper() if up else ch.lower()); up = not up
        else: out.append(ch)
    return "".join(out)


TRANSFORMS = {"none": (lambda t: t), "upper": (lambda t: t.upper()), "altcaps": _altcaps}


def corpus(seed, n_tr, n_ho, tok, transform):
    files = sorted(glob.glob(str(Path(__file__).resolve().parents[2] / "docs/*.md"))); rng = np.random.default_rng(seed); f = TRANSFORMS[transform]
    def draw(fs, n):
        toks = [np.array(tok.encode(f(open(p).read()))) for p in fs]; out = []
        while len(out) < n:
            t = toks[rng.integers(len(toks))]
            if len(t) < S2.CTX + 2: continue
            i = rng.integers(0, len(t) - S2.CTX - 1); out.append(t[i:i + S2.CTX + 1])
        return np.stack(out)
    return draw(files[::2], n_tr), draw(files[1::2], n_ho)


def make_world(seed, n, transform):
    P = GM.load_params(); tok = GM.tokenizer(); tr, ho = corpus(seed, n, n, tok, transform); return S2.World(P, tr, ho, "all")


def student(W, fam, x, key, steps, lr, restarts):
    """Best of `restarts` fits; returns the student and how many restarts beat the first fit by better_frac."""
    fits = [SK.fit(W.G(fam), x, SK.init_theta(fam, k, W.shape_of), steps, lr, W.P) for k in jax.random.split(key, restarts)]
    F0 = fits[0][1]; best = min(fits, key=lambda f: f[1]); return best[0], sum(1 for f in fits[1:] if f[1] < (1 - SK.TH["better_frac"]) * F0), [f[1] for f in fits]


def build_case(name, W, key, cfg):
    ks = jax.random.split(key, 4); x1, xh1 = W.onehot("tr"), W.onehot("ho"); steps, lr = cfg["steps"], cfg["lr"]
    if name == "extend":
        tf = [(cfg["teacher_module"], 2)]; th_t, _ = SK.fit(W.G(tf), x1, SK.init_theta(tf, ks[0], W.shape_of), cfg["teacher_steps"], cfg["teacher_lr"], W.P)
        delta = {cfg["teacher_module"]: cfg["teacher_amp"] * SK.deltas_of(tf, th_t, W.shape_of)[cfg["teacher_module"]]}; x, xh = S2.target(W, delta)
        fam = [(cfg["student_module"], 2)]; th, n_better, Fs = student(W, fam, x, ks[2], steps, lr, cfg["student_restarts"])
        return f"EXPAND:{cfg['teacher_module']}", fam, th, x, xh, dict(restarts_better=n_better, restart_F=Fs, base_to_target=SK.normD(x, W.base["tr"]), base_to_target_held=SK.normD(xh, W.base["ho"]))
    if name == "real":
        fam = [(cfg["student_module"], 2)]; th, n_better, Fs = student(W, fam, x1, ks[2], steps, lr, cfg["student_restarts"])
        return "?", fam, th, x1, xh1, dict(restarts_better=n_better, restart_F=Fs)
    raise ValueError(name)


def run_case(name, W, key, cfg, library):
    truth, fam, th, x, xh, note = build_case(name, W, key, cfg); log(f"case {name}: truth {truth} ({note})")
    rec = SK.decide(W, fam, th, x, xh, library, jax.random.fold_in(key, 7), cfg["steps"], cfg["lr"], log=log, sweep=True)
    got = rec["action"] + (":" + rec["chosen"] if rec["action"] == "EXPAND" else ""); rec.update(case=name, truth=truth, got=got, note=note, correct=(got == truth) if truth != "?" else None)
    rec["nll_held"] = dict(base=W.nll("ho", [], jnp.zeros(0)), current=W.nll("ho", fam, th))
    log(f"  -> {got} ({'ok' if rec['correct'] else 'MISS' if rec['correct'] is False else 'reported'}) fits {rec['fits_run']}")
    return rec


def pilot(transform="upper"):
    """The declared pilot: the format world, the base and student numbers, the teacher's held-out effect, the
    sweep of single-module fits on the format targets (the regime check: do modules differ on held-out?)."""
    T0 = time.time(); cfg = dict(steps=60, lr=1e-3, student_restarts=3, teacher_steps=60, teacher_lr=1e-3, teacher_amp=2.0, teacher_module="fc@7", student_module="v@7")
    lib = [f"{n}@{l}" for l in (3, 7, 11) for n in ("v", "o", "fc", "proj")]
    W = make_world(0, 96, transform); x, xh = W.onehot("tr"), W.onehot("ho")
    log(f"{transform} world: state dim {x.size}, base D {SK.normD(x, W.base['tr']):.4f} held {SK.normD(xh, W.base['ho']):.4f} nll_held {W.nll('ho', [], jnp.zeros(0)):.3f} ({time.time() - T0:.0f}s)")
    for m in lib:
        t = time.time(); f = [(m, 2)]; th, Fv = SK.fit(W.G(f), x, SK.init_theta(f, jax.random.PRNGKey(5), W.shape_of), cfg["steps"], cfg["lr"], W.P)
        log(f"  rank-2 on {m}: D {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(x))):.4f} D_held {SK.normD(xh, W.Gh(f)(th, W.P)):.4f} nll_held {W.nll('ho', f, th):.3f} ({time.time() - t:.0f}s)")
    truth, fam, th, xt, xht, note = build_case("extend", W, jax.random.PRNGKey(6), cfg); log(f"extend teacher on {cfg['teacher_module']}: {note}")
    st = SK.stationarity(W.G(fam), xt, th, jax.random.PRNGKey(1), W.P); log(f"  student on {cfg['student_module']}: D {SK.normD(xt, xt - st['r']):.4f} D_held {SK.normD(xht, W.Gh(fam)(th, W.P)):.4f} s {st['stat']:.2e}")
    for m in (cfg["teacher_module"], "proj@7", "o@7", "v@11"):
        t = time.time(); jf = list(fam) + [(m, 2)]; th0 = jnp.concatenate([th, SK.init_theta([(m, 2)], jax.random.PRNGKey(12), W.shape_of)]); thj, Fv = SK.fit(W.G(jf), xt, th0, cfg["steps"], cfg["lr"], W.P)
        log(f"  joint fit with {m}: D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(xt))):.4f} D_held {SK.normD(xht, W.Gh(jf)(thj, W.P)):.4f} ({time.time() - t:.0f}s)")
    log(f"pilot done in {time.time() - T0:.0f}s")


def run():
    cfg = json.load(open(OUT / "config.json")); SK.TH.update(cfg["thresholds"]); lib = list(cfg["library"]); T0 = time.time(); out = dict(rows=[])
    W = make_world(cfg["seed"], cfg["n_probe"], cfg["transform"])
    for i, name in enumerate(cfg["cases"]):
        rec = run_case(name, W, jax.random.PRNGKey(3000 + i), cfg, lib); out["rows"].append(rec); log(f"[{time.time() - T0:.0f}s]")
    out["seconds"] = time.time() - T0
    json.dump(out, open(OUT / "ed3.json", "w"), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)); log(f"done -> ed3.json in {out['seconds']:.0f}s")


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "pilot"
    pilot(sys.argv[2] if len(sys.argv) > 2 else "upper") if a == "pilot" else run()
