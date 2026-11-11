#!/usr/bin/env python3
"""ED11: the online real share measured on the step Adam actually takes, with two consecutive readings to stop.

  python lora_online2.py run CONFIG.json OUT_DIR
  python lora_online2.py score OUT_DIR

ED10 estimated the real share from the raw gradients of two halves of the training contexts. Section 12's
identity is about the step taken: along the update u, the test gain grows per unit of training gain at
<g_pop, u> / <g_tr, u>. Adam's update is (up to momentum) P g with P = diag(1 / (sqrt(v_hat) + eps)) from its
second-moment state, and on 48 matrices P weights coordinates very unequally, so the raw-gradient share stayed
positive past the test peak (docs/math-track-ed10-results.md). Here, with g_A, g_B the raw gradients on the two
halves and <x, y>_P = sum_k P_k x_k y_k:

  share_adam = <g_A, g_B>_P / (<g_A, g_B>_P + |g_A - g_B|_P^2 / 4),

the real share of the preconditioned direction (momentum ignored); P is read from the optimiser before each
evaluation (all ones before the first step). Also recorded: the raw share of ED10, and relative disparity.
Stopping: the second of two consecutive evaluations at or below zero (ED10's single crossing stopped a fit at a
one-off dip). Fits, half-fits, adapters, corpus and the rule's g* are ED10's (lora_online.py, lora_big.py).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lora_knee as LK, lora_big as LB, lora_online as LO


def signals(model, los, tr, P):
    h = len(tr) // 2; gA, gB = LO.grads(model, los, tr[:h]), LO.grads(model, los, tr[h:2 * h]); d = gA - gB
    sh = lambda dot, d2: dot / (dot + d2 / 4) if dot + d2 / 4 != 0 else 0.0
    return dict(share=sh(float(gA @ gB), float(d @ d)), share_adam=sh(float((P * gA) @ gB), float((P * d) @ d)),
                disparity_rel=float(d.norm()) / max(float(gA.norm() + gB.norm()) / 2, 1e-30))


def precond(opt, los):
    ps = [t for lo in los for t in (lo.A, lo.B)]; out = []
    for p in ps:
        st = opt.state.get(p)
        if not st: out.append(torch.ones(p.numel())); continue
        b1, b2 = opt.param_groups[0]["betas"]; eps = opt.param_groups[0]["eps"]; t = float(st["step"])
        out.append((1.0 / ((st["exp_avg_sq"] / (1 - b2 ** t)).sqrt() + eps)).flatten())
    return torch.cat(out)


def fit(model, targets, data, lr, cap, rank, seed, seg, patience=5, drop=0.25):
    los = [LK.Lora(model, t, rank, seed + 7919 * i) for i, t in enumerate(targets)]; opt = torch.optim.Adam([p for lo in los for p in (lo.A, lo.B)], lr=lr)
    inst = lambda: [lo.install() for lo in los]
    def losses():
        inst()
        with torch.no_grad(): return {s: float(LK.ce(model, t)) for s, t in data.items()}
    try:
        base = losses(); out = dict(step=[0], stopped="cap", sig={k: [v] for k, v in signals(model, los, data["tr"], precond(opt, los)).items()}, **{s: [v] for s, v in base.items()}); peak, kp = -np.inf, 0
        for k in range(cap // seg):
            for _ in range(seg): inst(); opt.zero_grad(); LK.ce(model, data["tr"]).backward(); opt.step()
            cur = losses(); out["step"].append((k + 1) * seg)
            for s, v in cur.items(): out[s].append(v)
            for s, v in signals(model, los, data["tr"], precond(opt, los)).items(): out["sig"][s].append(v)
            g = base["te"] - cur["te"]
            if g > peak: peak, kp = g, k
            if k - kp >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    finally:
        for lo in los: lo.restore()
    return out


def run(cfg_path, out_dir):
    LO.fit = fit; LO.run(cfg_path, out_dir)   # ED10's loop, with this fit


def stops(tj, warm=1, patience=3):
    sg = tj["sig"]; K = len(tj["step"]); S = {}
    two = lambda v: next((k for k in range(warm + 1, K) if v[k] <= 0 and v[k - 1] <= 0), None)
    S["share_adam"] = two(sg["share_adam"]); S["share"] = two(sg["share"]); S["share_single"] = next((k for k in range(warm, K) if sg["share"][k] <= 0), None)
    r = sg["disparity_rel"]; S["disparity_rel"] = None; lo = np.inf
    for k in range(warm, K):
        if r[k] < lo: lo, since = r[k], k
        if k - since >= patience and all(r[since + q + 1] > r[since + q] for q in range(patience)): S["disparity_rel"] = since; break
    return S


def score(out_dir):
    out_dir = Path(out_dir); rows = json.load(open(out_dir / "rows.json"))["rows"]; cfg = json.load(open(out_dir / "config.json")); recs = []
    SIG = ["share_adam", "share", "share_single", "disparity_rel"]
    L = ["# ED11: the online share on Adam's step\n", "Share of each fit's peak test gain kept (stopping step; `none`: never fired, the last step is used).\n",
         "| condition | adapter | peak (step) | rule | " + " | ".join(SIG) + " | validation minimum |", "|" + "---|" * (5 + len(SIG))]
    for r in rows:
        ads = LO.adapters_of(cfg, r["cond"]); hk = {k: tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for k, tj in r["half"].items()}
        g_one = float(np.median([v for k, v in hk.items() if ads[k.split(" ", 3)[-1]]["group"] == "one"] or [np.nan]))
        for name, tj in r["full"].items():
            ge = tj["te"][0] - np.array(tj["te"]); gt = tj["tr"][0] - np.array(tj["tr"]); pk = ge.max(); grp = ads[name]["group"]
            gstar = g_one if grp == "one" else float(np.mean([v for k, v in hk.items() if k.endswith(" " + name)]))
            v, i = LO.at_gain(gt, ge, gstar); x = dict(cond=r["name"], adapter=name, group=grp, peak=float(pk), peak_step=tj["step"][int(np.argmax(ge))], rule=v / pk, rule_step=tj["step"][i])
            for k, s in stops(tj).items(): j = len(ge) - 1 if s is None else s; x[k] = float(ge[j] / pk); x[k + "_step"] = None if s is None else tj["step"][s]
            j = int(np.argmin(tj["ho"])); x["val"] = float(ge[j] / pk); x["val_step"] = tj["step"][j]; recs.append(x)
            f = lambda a: f"{x[a]:.2f} ({x[a + '_step'] if x.get(a + '_step') is not None else 'none'})"
            L.append(f"| {x['cond']} | {name} | {pk:+.3f} ({x['peak_step']}) | {f('rule')} | " + " | ".join(f(a) for a in SIG) + f" | {f('val')} |")
    arms = ["rule"] + SIG + ["val"]
    L += ["\n| stop | mean share kept | lowest | at least 2/3 of the peak | positive |", "|---|---|---|---|---|"]
    for a in arms:
        v = [x[a] for x in recs]; L.append(f"| {a} | {np.mean(v):.2f} | {min(v):.2f} | {sum(t >= 2 / 3 for t in v)} of {len(v)} | {sum(t > 0 for t in v)} of {len(v)} |")
    L += ["\n| condition | reach | " + " | ".join(arms) + " |", "|" + "---|" * (2 + len(arms))]
    for c in dict.fromkeys(x["cond"] for x in recs):
        for g in ("one", "all"):
            xs = [x for x in recs if x["cond"] == c and x["group"] == g]
            if xs: L.append(f"| {c} | {g} | " + " | ".join(f"{np.mean([x[a] for x in xs]):.2f}" for a in arms) + " |")
    B = cfg.get("bars")
    if B:
        n = len(recs); sh = [x["share_adam"] for x in recs]; need = int(np.ceil(B["keep_share"] * n)); mean = lambda a: float(np.mean([x[a] for x in recs]))
        O1 = all(t > 0 for t in sh) and sum(t >= B["keep"] for t in sh) >= need; O2 = mean("share_adam") >= mean("rule") - B["rule_margin"]
        allr = [x["share_adam"] for x in recs if x["group"] == "all"]; O3 = sum(t >= B["keep"] for t in allr) >= int(np.ceil(B["keep_share"] * len(allr)))
        L += ["\n## Bars (docs/math-track-ed11-prereg.md)\n",
              f"- **P1**, share_adam is safe: positive in {sum(t > 0 for t in sh)} of {n} (needs all), at least {B['keep']:.0%} of the peak in {sum(t >= B['keep'] for t in sh)} (needs {need}): **{'holds' if O1 else 'fails'}**",
              f"- **P2**, close to the cross-fitted rule: mean {mean('share_adam'):.3f} against {mean('rule'):.3f} (needs no more than {B['rule_margin']} below): **{'holds' if O2 else 'fails'}**",
              f"- **P3**, it works on the all-matrix adapters, where ED10's raw share failed: at least {B['keep']:.0%} of the peak in {sum(t >= B['keep'] for t in allr)} of {len(allr)} (needs {int(np.ceil(B['keep_share'] * len(allr)))}): **{'holds' if O3 else 'fails'}**",
              f"- **Outcome: {'A' if O1 and O2 and O3 else 'B' if O1 or O3 else 'C'}**"]
    (out_dir / "report.md").write_text("\n".join(L) + "\n"); json.dump(recs, open(out_dir / "scores.json", "w"), indent=1); print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "score": score(sys.argv[2])
    else: print(__doc__)
