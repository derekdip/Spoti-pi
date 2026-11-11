#!/usr/bin/env python3
"""Online stopping signals from the training contexts alone, recorded along one long LoRA fit, against the
cross-fitted knee and held-out stopping (the comparison planned in docs/prescreen-theory.md, section 15).

  python lora_online.py run CONFIG.json OUT_DIR
  python lora_online.py score OUT_DIR

Every `seg` steps of a full fit on all n training contexts (losses on test and validation recorded, as in
lora_knee.py), the raw gradients of the LoRA's factors are taken on the two halves A, B of the training
contexts and on each context alone. Three signals, none of which looks at held-out data:

- share: the real share of the step, estimated from the halves under g_A = g + e_A, g_B = g + e_B with
  independent noise: <g_A, g_B> estimates |g|^2 and |g_A - g_B|^2 / 4 the noise of the full-sample mean, so
  share = <g_A, g_B> / (<g_A, g_B> + |g_A - g_B|^2 / 4). It is the identity of section 12 read online.
  Stop the first time it is at or below zero.
- disparity: |g_A - g_B| (the gradient disparity of Forouzesh and Thiran, 2021, with two batches, as recalled,
  not checked against the paper). Stop at the first evaluation after which it has risen `patience` times in a
  row; the stop is taken where the rise began.
- eb: the evidence-based criterion of Mahsereci et al. (2017, as recalled): with per-context gradients, mean
  m_k and variance s_k of each parameter, eb = 1 - (n / D) * sum_k m_k^2 / s_k. Stop the first time eb > 0.

The share kept at each stop is read off the same fit's test curve, so the signals, the cross-fitted g* (from
this condition's half-fits) and held-out stopping are compared on one trajectory.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lora_knee as LK


def grads(model, lo, toks):
    lo.install(); lo.A.grad = lo.B.grad = None; LK.ce(model, toks).backward()
    return torch.cat([lo.A.grad.flatten(), lo.B.grad.flatten()]).detach().clone()


def signals(model, lo, tr):
    n = len(tr); h = n // 2; gA, gB = grads(model, lo, tr[:h]), grads(model, lo, tr[h:2 * h])
    dot = float(gA @ gB); d2 = float(((gA - gB) ** 2).sum())
    per = torch.stack([grads(model, lo, tr[i:i + 1]) for i in range(n)]); m = per.mean(0); s = per.var(0, unbiased=True) + 1e-30
    eb = float(1 - (n / m.numel()) * (m ** 2 / s).sum())
    return dict(share=dot / (dot + d2 / 4) if dot + d2 / 4 != 0 else 0.0, disparity=d2 ** 0.5, eb=eb)


def fit(model, target, data, lr, cap, rank, seed, seg, patience=5, drop=0.25):
    lo = LK.Lora(model, target, rank, seed); opt = torch.optim.Adam([lo.A, lo.B], lr=lr)
    def losses():
        lo.install()
        with torch.no_grad(): return {s: float(LK.ce(model, t)) for s, t in data.items()}
    try:
        base = losses(); out = dict(step=[0], stopped="cap", sig={k: [v] for k, v in signals(model, lo, data["tr"]).items()}, **{s: [v] for s, v in base.items()}); peak, kp = -np.inf, 0
        for k in range(cap // seg):
            for _ in range(seg): lo.install(); opt.zero_grad(); LK.ce(model, data["tr"]).backward(); opt.step()
            cur = losses(); out["step"].append((k + 1) * seg)
            for s, v in cur.items(): out[s].append(v)
            for s, v in signals(model, lo, data["tr"]).items(): out["sig"][s].append(v)
            g = base["te"] - cur["te"]
            if g > peak: peak, kp = g, k
            if k - kp >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    finally:
        lo.restore()
    return out


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); torch.set_num_threads(cfg.get("threads", 4)); T0 = time.time()
    cp = out_dir / "config.json"
    if cp.resolve() != Path(cfg_path).resolve(): json.dump(cfg, open(cp, "w"), indent=1)
    texts = LK.docs_text(cfg["repo"], cfg["corpus_commit"]); model, enc = LK.load_model(cfg["model"]); res = out_dir / "rows.json"
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}
    T = lambda a: torch.tensor(np.asarray(a), dtype=torch.long)
    for c in cfg["conditions"]:
        if c["name"] in done: continue
        tr, ho, te = LK.corpus3(texts, enc, c["seed"], c["n"], c["n_val"], c["n_test"], c["transform"]); row = dict(name=c["name"], cond=c, tokens=LK.fingerprint(tr, ho, te), full={}, half={})
        for i, m in enumerate(c["targets"]):
            t = time.time(); row["full"][m] = fit(model, m, dict(tr=T(tr), ho=T(ho), te=T(te)), cfg["lr"], cfg["cap_full"], cfg["rank"], c["seed"] * 1000 + i, cfg.get("seg", 10))
            LK.log(f"  {c['name']} {m}: {row['full'][m]['step'][-1]} steps ({time.time() - t:.0f}s)")
            h = c["n"] // 2
            for j, (hn, A, B) in enumerate((("A to B", tr[:h], tr[h:2 * h]), ("B to A", tr[h:2 * h], tr[:h]))):
                row["half"][f"{hn} {m}"] = LK.long_fit(model, m, dict(tr=T(A), ho=T(B)), "ho", cfg["lr"], cfg["cap_half"], cfg["rank"], seed=c["seed"] * 1000 + 100 + 10 * i + j, drop=0.5)
        out.append(row); json.dump(dict(rows=out), open(res, "w"), indent=1); LK.log(f"{c['name']} done [{time.time() - T0:.0f}s]")


def stops(tj, patience=3):
    st = tj["step"]; sg = tj["sig"]; S = {}
    i = next((k for k in range(1, len(st)) if sg["share"][k] <= 0), None); S["share"] = i
    d = sg["disparity"]; i = next((k for k in range(1, len(st) - patience) if all(d[k + q + 1] > d[k + q] for q in range(patience))), None); S["disparity"] = i
    i = next((k for k in range(1, len(st)) if sg["eb"][k] > 0), None); S["eb"] = i
    return S


def score(out_dir):
    out_dir = Path(out_dir); rows = json.load(open(out_dir / "rows.json"))["rows"]; recs = []
    L = ["# Online stopping signals against the cross-fitted knee and held-out stopping\n", "Share of each fit's peak test gain kept (stop step in brackets; `none` = the signal never fired, the fit's last step is used).\n",
         "| condition | matrix | peak (step) | g* (rule) | share | disparity | eb | validation minimum |", "|---|" * 1 + "---|" * 7]
    for r in rows:
        gstar = float(np.median([tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for tj in r["half"].values()]))
        for m, tj in r["full"].items():
            ge = tj["te"][0] - np.array(tj["te"]); gt = tj["tr"][0] - np.array(tj["tr"]); pk = ge.max(); kpk = int(np.argmax(ge))
            i = int(np.argmax(gt >= gstar)) if (gt >= gstar).any() else len(gt) - 1; x = dict(cond=r["name"], m=m, rule=float(ge[i] / pk), rule_step=tj["step"][i])
            for k, v in stops(tj).items(): j = len(ge) - 1 if v is None else v; x[k] = float(ge[j] / pk); x[k + "_step"] = None if v is None else tj["step"][v]
            j = int(np.argmin(tj["ho"])); x["val"] = float(ge[j] / pk); x["val_step"] = tj["step"][j]; recs.append(x)
            f = lambda a: f"{x[a]:.2f} ({x[a + '_step'] if x[a + '_step'] is not None else 'none'})"
            L.append(f"| {x['cond']} | {m} | {pk:+.3f} ({tj['step'][kpk]}) | {f('rule')} | {f('share')} | {f('disparity')} | {f('eb')} | {f('val')} |")
    L += ["\n| stop | mean share kept | lowest | at least 2/3 of the peak |", "|---|---|---|---|"]
    for a in ("rule", "share", "disparity", "eb", "val"):
        v = [x[a] for x in recs]; L.append(f"| {a} | {np.mean(v):.2f} | {min(v):.2f} | {sum(t >= 2 / 3 for t in v)} of {len(v)} |")
    (out_dir / "report.md").write_text("\n".join(L) + "\n"); json.dump(recs, open(out_dir / "scores.json", "w"), indent=1); print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "score": score(sys.argv[2])
    else: print(__doc__)
