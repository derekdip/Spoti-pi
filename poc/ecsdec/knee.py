"""ED5: does a LoRA fit's knee, and the stopping rule built on it, hold at larger samples?
(docs/math-track-ed5-prereg.md; background in docs/prescreen-theory.md, section 12.)

  /usr/bin/python3 -m poc.ecsdec.knee pilot     seed 0, declared pilot      -> poc/results/ed5/pilot.json
  /usr/bin/python3 -m poc.ecsdec.knee run       the scored run (config.json) -> poc/results/ed5/ed5.json

Per condition: a rank-2 LoRA is fitted alone on each matrix on all the training contexts, with its loss on
validation and test contexts every 10 steps, until its test gain has turned (or a cap); and on each half of the
training contexts with its loss on the other half, until that has turned (or a cap). The knee of a fit is its
training gain where the watched loss is lowest. The rule: g* is the median of the half-fits' knees; a full fit
is stopped when its training gain first reaches g*. Every fit is checkpointed with a hash of its contexts.
"""
from __future__ import annotations
import json, sys, time, hashlib
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import prescreen as PS

OUT = Path(__file__).resolve().parents[2] / "poc/results/ed5"; OUT.mkdir(parents=True, exist_ok=True); log = PS.log
X = lambda a: jnp.asarray(a[:, :PS.CTX]); Y = lambda a: jnp.asarray(a[:, 1:PS.CTX + 1])


def set_data(W, **sets):
    """Swap contexts into a world (its compiled programs are kept) and refresh the base losses."""
    for s, a in sets.items(): W.x[s], W.y[s] = X(a), Y(a); W.L0[s] = float(PS._ce(W._logits(W.P, W.x[s]), W.y[s]))


def long_fit(W, m, key, lr, cap, watch, sets, patience=5, drop=0.25):
    """A rank-2 LoRA on matrix m, Adam, losses on `sets` every W.seg steps; stops once the gain on `watch` has
    fallen to `drop` of its peak at least `patience` evaluations after the peak, or at `cap` steps."""
    ks = jax.random.split(key, len(W.lib)); p = {k: (jax.random.normal(ks[i], (W.rank, GM.shape_of(k)[1])) * 0.02, jnp.zeros((GM.shape_of(k)[0], W.rank))) for i, k in enumerate(W.lib)}
    mask = jnp.asarray([1.0 if k == m else 0.0 for k in W.lib]); z = jax.tree_util.tree_map(jnp.zeros_like, p); mo, vo = z, z
    out = dict(step=[0], norm=[0.0], stopped="cap", **{s: [W.L0[s]] for s in sets}); peak, kpeak = -np.inf, 0
    for k in range(cap // W.seg):
        p, mo, vo, _ = W._seg(W.P, W.x["tr"], W.y["tr"], p, mo, vo, jnp.float32(k * W.seg), mask, lr)
        out["step"].append((k + 1) * W.seg); out["norm"].append(float(jnp.linalg.norm(p[m][1] @ p[m][0])))
        for s in sets: out[s].append(float(W._loss_lora(W.P, W.x[s], W.y[s], p, mask)))
        g = W.L0[watch] - out[watch][-1]
        if g > peak: peak, kpeak = g, k
        if k - kpeak >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    return out


def knee(tj, watch):
    """The fit's training gain, watched gain and step where the watched loss is lowest."""
    k = int(np.argmin(tj[watch])); return dict(step=tj["step"][k], train_gain=tj["tr"][0] - tj["tr"][k], gain=tj[watch][0] - tj[watch][k], turned=tj["stopped"] == "turned")


def condition(W, tok, c, cfg, key, ckpt):
    tr, ho, te = PS.corpus3(c["seed"], c["n"], c["n_val"], c["n_test"], tok, c["transform"]); h = c["n"] // 2
    tokens = hashlib.sha1(b"".join(np.asarray(X(a)).tobytes() + np.asarray(Y(a)).tobytes() for a in (tr, ho, te))).hexdigest()
    st = json.load(open(ckpt)) if Path(ckpt).exists() else dict(tokens=tokens, full={}, half={}, seconds=0.0); assert st["tokens"] == tokens, f"{ckpt} was written for other contexts"
    if st["full"] or st["half"]: log(f"  {c['name']}: resumed with {len(st['full'])} full fits and {len(st['half'])} half-fits")
    save = lambda: json.dump(st, open(ckpt, "w"), indent=1, default=float)
    for i, m in enumerate(c["modules"]):
        if m not in st["full"]:
            set_data(W, tr=tr, ho=ho, te=te); t = time.time(); tj = long_fit(W, m, jax.random.fold_in(key, i), cfg["lr"], cfg["cap_full"], "te", ("tr", "ho", "te")); st["full"][m] = tj; st["seconds"] += time.time() - t; save(); kn = knee(tj, "te")
            log(f"  {c['name']} full {m}: test gain peaks at step {kn['step']} ({kn['gain']:+.3f}) at training gain {kn['train_gain']:.2f}; ran {tj['step'][-1]} steps, {tj['stopped']}; at step 60 {tj['te'][0] - tj['te'][6]:+.3f}, at the end {tj['te'][0] - tj['te'][-1]:+.3f} ({time.time() - t:.0f}s)")
        for j, (name, A, B) in enumerate((("A to B", tr[:h], tr[h:2 * h]), ("B to A", tr[h:2 * h], tr[:h]))):
            tag = f"{name} {m}"
            if tag in st["half"]: continue
            set_data(W, tr=A, ho=B); t = time.time(); tj = long_fit(W, m, jax.random.fold_in(key, 100 + 10 * i + j), cfg["lr"], cfg["cap_half"], "ho", ("tr", "ho"), drop=0.5); st["half"][tag] = tj; st["seconds"] += time.time() - t; save(); kn = knee(tj, "ho")
            log(f"  {c['name']} half {tag}: the other half's loss is lowest at step {kn['step']} ({kn['gain']:+.3f}) at training gain {kn['train_gain']:.2f}; ran {tj['step'][-1]} steps, {tj['stopped']} ({time.time() - t:.0f}s)")
    return dict(name=c["name"], cond=c, full=st["full"], half=st["half"], seconds=st["seconds"])


def main(which):
    cfg = json.load(open(OUT / ("pilot_config.json" if which == "pilot" else "config.json"))); PS.CORPUS_COMMIT = cfg["corpus_commit"]; T0 = time.time(); P = GM.load_params(); tok = GM.tokenizer()
    log(f"corpus: docs/*.md at {PS.CORPUS_COMMIT}, {len(PS.docs_text(PS.CORPUS_COMMIT))} files"); res = OUT / ("pilot.json" if which == "pilot" else "ed5.json")
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}; W = None
    for i, c in enumerate(cfg["conditions"]):
        if c["name"] in done: log(f"  {c['name']}: already done"); continue
        if W is None:
            tr, ho, te = PS.corpus3(c["seed"], c["n"], c["n_val"], c["n_test"], tok, c["transform"]); W = PS.CEWorld(P, tr, ho, library=cfg["library"], te=te)
        out.append(condition(W, tok, c, cfg, jax.random.PRNGKey(cfg["key"] + i), OUT / f"{which}_{c['name']}.ckpt.json")); json.dump(dict(rows=out), open(res, "w"), indent=1, default=float); log(f"[{time.time() - T0:.0f}s]")
    log(f"{which} done in {time.time() - T0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "pilot")
