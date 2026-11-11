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
import lora_knee as LK, lora_big as LB


def grads(model, los, toks):
    for lo in los: lo.install(); lo.A.grad = lo.B.grad = None
    LK.ce(model, toks).backward()
    return torch.cat([t.grad.flatten() for lo in los for t in (lo.A, lo.B)]).detach().clone()


def signals(model, los, tr):
    n = len(tr); h = n // 2; gA, gB = grads(model, los, tr[:h]), grads(model, los, tr[h:2 * h])
    dot = float(gA @ gB); d2 = float(((gA - gB) ** 2).sum()); na, nb = float(gA.norm()), float(gB.norm())
    m = torch.zeros_like(gA); q = torch.zeros_like(gA)
    for i in range(n): g = grads(model, los, tr[i:i + 1]); m += g; q += g * g
    m /= n; s = (q - n * m * m) / (n - 1) + 1e-30
    eb = float(1 - (n / m.numel()) * (m ** 2 / s).sum())
    return dict(share=dot / (dot + d2 / 4) if dot + d2 / 4 != 0 else 0.0, disparity=d2 ** 0.5, disparity_rel=d2 ** 0.5 / max((na + nb) / 2, 1e-30), eb=eb)


def fit(model, targets, data, lr, cap, rank, seed, seg, patience=5, drop=0.25):
    targets = [targets] if isinstance(targets, str) else targets
    los = [LK.Lora(model, t, rank, seed + 7919 * i) for i, t in enumerate(targets)]; opt = torch.optim.Adam([p for lo in los for p in (lo.A, lo.B)], lr=lr)
    inst = lambda: [lo.install() for lo in los]
    def losses():
        inst()
        with torch.no_grad(): return {s: float(LK.ce(model, t)) for s, t in data.items()}
    try:
        base = losses(); out = dict(step=[0], stopped="cap", sig={k: [v] for k, v in signals(model, los, data["tr"]).items()}, **{s: [v] for s, v in base.items()}); peak, kp = -np.inf, 0
        for k in range(cap // seg):
            for _ in range(seg): inst(); opt.zero_grad(); LK.ce(model, data["tr"]).backward(); opt.step()
            cur = losses(); out["step"].append((k + 1) * seg)
            for s, v in cur.items(): out[s].append(v)
            for s, v in signals(model, los, data["tr"]).items(): out["sig"][s].append(v)
            g = base["te"] - cur["te"]
            if g > peak: peak, kp = g, k
            if k - kp >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    finally:
        for lo in los: lo.restore()
    return out



def adapters_of(cfg, c):
    """{name: dict(targets, rank, lr, seg, group)}: the config's adapters, or (the pilot's form) one rank-r adapter
    per target of the condition."""
    if "adapters" in c: return {a: cfg["adapters"][a] for a in c["adapters"]}
    return {t: dict(targets=[t], rank=cfg["rank"], lr=cfg["lr"], seg=cfg.get("seg", 10), group="one") for t in c["targets"]}


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); torch.set_num_threads(cfg.get("threads", 4)); T0 = time.time()
    cp = out_dir / "config.json"
    if cp.resolve() != Path(cfg_path).resolve():
        assert not cp.exists() or json.load(open(cp)) == cfg, f"{cp} differs from {cfg_path}"
        json.dump(cfg, open(cp, "w"), indent=1)
    texts = LK.docs_text(cfg["repo"], cfg["corpus_commit"]); model, enc = LK.load_model(cfg["model"]); res = out_dir / "rows.json"
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}
    T = lambda a: torch.tensor(np.asarray(a), dtype=torch.long)
    for c in cfg["conditions"]:
        if c["name"] in done: LK.log(f"  {c['name']}: already done"); continue
        tr, ho, te = LK.corpus3(texts, enc, c["seed"], c["n"], c["n_val"], c["n_test"], c["transform"]); tokens = LK.fingerprint(tr, ho, te); h = c["n"] // 2
        ck = out_dir / f"{c['name']}.ckpt.json"; row = json.load(open(ck)) if ck.exists() else dict(name=c["name"], cond=c, tokens=tokens, full={}, half={}, seconds=0.0)
        assert row["tokens"] == tokens, f"{ck} was written for other contexts"
        for i, (name, ad) in enumerate(adapters_of(cfg, c).items()):
            tg = LB.expand(model, ad["targets"]); seg = ad.get("seg", cfg.get("seg", 10))
            if name not in row["full"]:
                t = time.time(); row["full"][name] = fit(model, tg, dict(tr=T(tr), ho=T(ho), te=T(te)), ad["lr"], cfg["cap_full"], ad["rank"], c["seed"] * 1000 + i, seg); row["seconds"] += time.time() - t
                json.dump(row, open(ck, "w"), indent=1); LK.log(f"  {c['name']} {name}: {row['full'][name]['step'][-1]} steps, {row['full'][name]['stopped']} ({time.time() - t:.0f}s)")
            for j, (hn, A, B) in enumerate((("A to B", tr[:h], tr[h:2 * h]), ("B to A", tr[h:2 * h], tr[:h]))):
                tag = f"{hn} {name}"
                if tag in row["half"]: continue
                t = time.time(); row["half"][tag] = LB.long_fit(model, tg, ad["rank"], dict(tr=T(A), ho=T(B)), "ho", ad["lr"], cfg["cap_half"], c["seed"] * 1000 + 100 + 10 * i + j, seg, drop=0.5)
                row["seconds"] += time.time() - t; json.dump(row, open(ck, "w"), indent=1)
        out.append(row); json.dump(dict(rows=out), open(res, "w"), indent=1); LK.log(f"{c['name']} done [{time.time() - T0:.0f}s]")
    LK.log(f"done in {time.time() - T0:.0f}s")


def stops(tj, patience=3, warm=1):
    """Evaluation index at which each signal stops a fit (None: never). Defined from ED10's pilot before any
    scored fit. share: first evaluation after the first at which share <= 0. disparity (raw, as recalled):
    first point after which |g_A - g_B| rises `patience` times in a row. disparity_rel: the same for
    |g_A - g_B| / mean(|g_A|, |g_B|), counted from its running minimum. eb: the second of two consecutive
    evaluations with eb > 0."""
    st = tj["step"]; sg = tj["sig"]; S = {}; K = len(st)
    S["share"] = next((k for k in range(warm, K) if sg["share"][k] <= 0), None)
    d = sg["disparity"]; S["disparity"] = next((k for k in range(warm, K - patience) if all(d[k + q + 1] > d[k + q] for q in range(patience))), None)
    if "disparity_rel" in sg:
        r = sg["disparity_rel"]; S["disparity_rel"] = None; lo = np.inf
        for k in range(warm, K):
            if r[k] < lo: lo, since = r[k], k
            if k - since >= patience and all(r[since + q + 1] > r[since + q] for q in range(patience)): S["disparity_rel"] = since; break
    S["eb"] = next((k for k in range(warm + 1, K) if sg["eb"][k] > 0 and sg["eb"][k - 1] > 0), None)
    return S


def at_gain(gt, ge, g):
    if not (gt >= g).any(): return float(ge[-1]), len(gt) - 1
    i = int(np.argmax(gt >= g))
    if i == 0: return 0.0, 0
    w = (g - gt[i - 1]) / (gt[i] - gt[i - 1]); return float(ge[i - 1] + w * (ge[i] - ge[i - 1])), i


def score(out_dir):
    out_dir = Path(out_dir); rows = json.load(open(out_dir / "rows.json"))["rows"]; cfg = json.load(open(out_dir / "config.json")); recs = []
    SIG = ["share", "disparity", "disparity_rel", "eb"]
    L = ["# Online stopping signals against the cross-fitted knee and held-out stopping\n", "Share of each fit's peak test gain kept (stopping step in brackets; `none`: the signal never fired and the fit's last step is used).\n",
         "| condition | adapter | peak (step) | rule | " + " | ".join(SIG) + " | validation minimum |", "|" + "---|" * (5 + len(SIG))]
    for r in rows:
        ads = adapters_of(cfg, r["cond"]); hk = {k: tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for k, tj in r["half"].items()}
        g_one = float(np.median([v for k, v in hk.items() if ads[k.split(" ", 3)[-1]]["group"] == "one"] or [np.nan]))
        for name, tj in r["full"].items():
            ge = tj["te"][0] - np.array(tj["te"]); gt = tj["tr"][0] - np.array(tj["tr"]); pk = ge.max(); kpk = int(np.argmax(ge)); grp = ads[name]["group"]
            gstar = g_one if grp == "one" else float(np.mean([v for k, v in hk.items() if k.endswith(" " + name)]))
            v, i = at_gain(gt, ge, gstar); x = dict(cond=r["name"], adapter=name, group=grp, n=r["cond"]["n"], peak=float(pk), peak_step=tj["step"][kpk], gstar=gstar, rule=v / pk, rule_step=tj["step"][i])
            for k, s in stops(tj).items(): j = len(ge) - 1 if s is None else s; x[k] = float(ge[j] / pk); x[k + "_step"] = None if s is None else tj["step"][s]
            j = int(np.argmin(tj["ho"])); x["val"] = float(ge[j] / pk); x["val_step"] = tj["step"][j]; recs.append(x)
            f = lambda a: f"{x[a]:.2f} ({x[a + '_step'] if x.get(a + '_step') is not None else 'none'})" if a in x else "-"
            L.append(f"| {x['cond']} | {name} | {pk:+.3f} ({x['peak_step']}) | {f('rule')} | " + " | ".join(f(a) for a in SIG) + f" | {f('val')} |")
    arms = ["rule"] + [a for a in SIG if a in recs[0]] + ["val"]
    L += ["\n| stop | runs it needs | mean share kept | lowest | at least 2/3 of the peak | positive |", "|---|---|---|---|---|---|"]
    for a in arms:
        v = [x[a] for x in recs]; L.append(f"| {a} | {'the full fit and the half-fits' if a == 'rule' else 'one, plus held-out data' if a == 'val' else 'one'} | {np.mean(v):.2f} | {min(v):.2f} | {sum(t >= 2 / 3 for t in v)} of {len(v)} | {sum(t > 0 for t in v)} of {len(v)} |")
    L += ["\nMean share kept by condition and reach:\n", "| condition | reach | " + " | ".join(arms) + " |", "|" + "---|" * (2 + len(arms))]
    for c in dict.fromkeys(x["cond"] for x in recs):
        for g in ("one", "all"):
            xs = [x for x in recs if x["cond"] == c and x["group"] == g]
            if xs: L.append(f"| {c} | {g} | " + " | ".join(f"{np.mean([x[a] for x in xs]):.2f}" for a in arms) + " |")
    B = cfg.get("bars")
    if B:
        n = len(recs); sh = [x["share"] for x in recs]; need = int(np.ceil(B["keep_share"] * n)); mean = lambda a: float(np.mean([x[a] for x in recs]))
        O1 = all(t > 0 for t in sh) and sum(t >= B["keep"] for t in sh) >= need; O2 = mean("share") >= mean("rule") - B["rule_margin"]
        pub = [a for a in ("disparity", "disparity_rel", "eb") if a in recs[0]]; O3 = all(mean("share") > mean(a) for a in pub)
        L += ["\n## Bars (docs/math-track-ed10-prereg.md)\n",
              f"- **O1**, the online share is safe: positive in {sum(t > 0 for t in sh)} of {n} (needs all), at least {B['keep']:.0%} of the peak in {sum(t >= B['keep'] for t in sh)} (needs {need}): **{'holds' if O1 else 'fails'}**",
              f"- **O2**, it is close to the cross-fitted rule: mean {mean('share'):.3f} against {mean('rule'):.3f} (needs no more than {B['rule_margin']} below): **{'holds' if O2 else 'fails'}**",
              f"- **O3**, it beats the published signals as implemented: mean {mean('share'):.3f} against " + ", ".join(f"{a} {mean(a):.3f}" for a in pub) + f": **{'holds' if O3 else 'fails'}**",
              f"- **Outcome: {'A' if O1 and O2 and O3 else 'B' if O1 else 'C'}**"]
    (out_dir / "report.md").write_text("\n".join(L) + "\n"); json.dump(recs, open(out_dir / "scores.json", "w"), indent=1); print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "score": score(sys.argv[2])
    else: print(__doc__)
