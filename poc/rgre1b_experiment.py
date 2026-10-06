"""RGRE-1b: short frozen replication of the simplified selector. Implements docs/math-track-rgre1b-prereg.md.

Usage: python poc/rgre1b_experiment.py [--out poc/results] [--seed 20260916]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout import parse_model  # noqa: E402
from rgre import bench_b, core, corn, water  # noqa: E402
from w1_experiment import CENTRE  # noqa: E402

TAU = 0.5834212065969504  # RGRE-1's calibrated threshold, carried over unchanged
DEAD = 0.01  # a repair that cuts the error by less than 1 percent is spent and cannot be renominated
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


def dom_of(case):
    return corn if isinstance(case, corn.CornCase) else water


def run_case(case, two_step):
    dom = dom_of(case)
    repairs, sets = dom.REPAIRS, dom.REPAIR_SETS
    names = [n for n, _ in repairs]
    s0 = case.state0
    E0 = case.E(s0)
    r0, pred0 = case.residual(s0)
    signed, templates = case.diagnostics(s0, pred0)
    diag = core.diagnose(r0, signed, templates)
    cls, reason, ranked = core.select_projection(diag, TAU, sets)
    cls_s, reason_s = core.select(diag, TAU)  # RGRE-1's coherence-weighted rule, reported only

    applied = {n: case.apply(s0, n) for n in names}
    cost = {n: applied[n][1] for n in names}
    dE = {n: E0 - applied[n][2] for n in names}
    value = {n: dE[n] / max(cost[n], 1e-9) for n in names}
    oracle = max(value, key=value.get)
    v_or = value[oracle]

    def cap(pick):
        if pick is None:
            return 0.0
        return (value[pick] / v_or) if v_or > 1e-12 else (1.0 if value[pick] >= v_or else 0.0)

    chosen = sets.get(cls, []) if cls else []
    pick = max(chosen, key=lambda n: value[n]) if chosen else None
    chosen_s = sets.get(cls_s, []) if cls_s else []
    pick_s = max(chosen_s, key=lambda n: value[n]) if chosen_s else None
    known = case.classes != ("unknown",)
    out = {"name": case.name, "domain": "corn" if dom is corn else "water", "classes": list(case.classes), "E0": E0,
           "q": diag["q"], "raw": diag["raw"], "q_perp": diag["q_perp"], "items": sorted(diag["items"], key=lambda t: -t[2])[:4],
           "chosen_class": cls, "reason": reason, "ranked": ranked, "N_rgre": len(chosen), "N_all": len(repairs),
           "repairs": {n: {"cost": cost[n], "dE": dE[n], "value": value[n]} for n in names},
           "oracle": oracle, "oracle_class": dict(repairs)[oracle], "pick": pick, "V_cap": cap(pick),
           "dE_rgre": dE[pick] if pick else 0.0, "dE_oracle": dE[oracle],
           "S_rule": {"class": cls_s, "reason": reason_s, "pick": pick_s, "V_cap": cap(pick_s)},
           "identity_gt": (cls in case.classes) if (known and cls) else False,
           "identity_oracle": (cls == dict(repairs)[oracle]) if cls else False,
           "abstained": cls is None}
    if two_step and known:
        out["two_step"] = run_two_step(case, dom, s0, E0, cls, chosen, pick, applied, value, dE)
    return out


def run_two_step(case, dom, s0, E0, cls1, chosen1, pick1, applied, value, dE):
    names = [n for n, _ in dom.REPAIRS]
    best_pair, best_E = None, E0
    for a in names:
        sa = applied[a][0]
        for b in names:
            if b == a:
                continue
            Eab = case.apply(sa, b)[2]
            if Eab < best_E:
                best_pair, best_E = (a, b), Eab
    dE_or2 = E0 - best_E
    res = {"oracle_pair": best_pair, "dE_oracle2": dE_or2, "cls1": cls1, "pick1": pick1}
    if pick1 is None:
        res.update({"cls2": None, "pick2": None, "dE_rgre2": 0.0, "recovery2": 0.0 if dE_or2 > 1e-12 else None, "blacklist": []})
        return res
    s1, E1 = applied[pick1][0], applied[pick1][2]
    spent = sorted(n for n in chosen1 if dE[n] < DEAD * E0)
    r1, pred1 = case.residual(s1)
    signed, templates = case.diagnostics(s1, pred1)
    diag1 = core.diagnose(r1, signed, templates)
    cls2, reason2, ranked2 = core.select_projection(diag1, TAU, dom.REPAIR_SETS, blacklist=spent)
    avail = [n for n in dom.REPAIR_SETS.get(cls2, []) if n not in spent] if cls2 else []
    E2, pick2 = E1, None
    if avail:
        ev = {n: case.apply(s1, n) for n in avail}
        pick2 = min(ev, key=lambda n: ev[n][2])
        E2 = min(E1, ev[pick2][2])
    res.update({"cls2": cls2, "reason2": reason2, "pick2": pick2, "E1": E1, "E2": E2, "dE_rgre2": E0 - E2,
                "recovery2": (E0 - E2) / dE_or2 if dE_or2 > 1e-12 else None, "blacklist": spent,
                "q_perp1": diag1["q_perp"], "N_eval2": len(chosen1) + len(avail)})
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    ap.add_argument("--seed", type=int, default=bench_b.SEED)
    args = ap.parse_args()
    out = Path(args.out)
    res_dir = Path(__file__).resolve().parent / "results"
    model0 = parse_model(json.loads((res_dir / "gpu_sweep.json").read_text())["terms"]["wake + presence"]["description"])
    theta0 = json.loads((res_dir / "w1.json").read_text())["token"]["params"]
    grid = water.Grid(water.base_params(), CENTRE)
    log("water floor field")
    floor_full = water.floor_field_full(theta0, grid)
    log(f"building the fresh benchmark (seed {args.seed})")
    iso, mix, unk, gap = bench_b.build(model0, theta0, grid, floor_full, args.seed, log)

    results = []
    for group, cases, two in (("isolated", iso, False), ("mixture", mix, True), ("unknown", unk, False), ("gap", gap, False)):
        for c in cases:
            t1 = time.time()
            r = run_case(c, two)
            c._cache.clear()
            r["group"] = group
            r["seconds"] = time.time() - t1
            results.append(r)
            ts = r.get("two_step", {})
            log(f"{group:8s} {r['name']:28s} E0 {r['E0']:.3f} q_perp {r['q_perp']:.2f} chose {str(r['chosen_class']):11s} ({r['reason']}) "
                f"oracle {r['oracle']:14s}[{r['oracle_class']:11s}] V {r['V_cap']:.2f} (S-rule {str(r['S_rule']['class']):11s} V {r['S_rule']['V_cap']:.2f})"
                + (f"  2-step {'-' if ts.get('recovery2') is None else round(ts['recovery2'], 2)} via {ts.get('cls2')}" if ts else ""))
    report = score(results)
    report["seed"] = args.seed
    report["tau_perp"] = TAU
    (out / "rgre1b.json").write_text(json.dumps(report, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    write_md(report, out / "rgre1b.md")
    try:
        make_figure(report, out / "rgre1b.png")
    except Exception as exc:  # noqa: BLE001
        log(f"(figure skipped: {exc})")
    log(json.dumps(report["tests"], indent=1, default=str))
    log(f"verdict: {report['verdict']}")
    log(f"wrote {out / 'rgre1b.md'}")


def score(results):
    med = lambda xs: float(np.median(xs)) if len(xs) else None  # noqa: E731
    known = [r for r in results if r["group"] in ("isolated", "mixture")]
    unk = [r for r in results if r["group"] == "unknown"]
    mixes = [r for r in results if r["group"] == "mixture"]
    v = [r["V_cap"] for r in known]
    ratio = [r["N_rgre"] / r["N_all"] for r in known]
    rec = [r["two_step"]["recovery2"] for r in mixes if r["two_step"].get("recovery2") is not None]
    ab_u = int(sum(r["abstained"] for r in unk))
    ab_k = int(sum(r["abstained"] for r in known))
    t = {}
    t["B1"] = {"median_V_cap": med(v), "mean_V_cap": float(np.mean(v)), "n": len(known),
               "by_domain": {d: med([r["V_cap"] for r in known if r["domain"] == d]) for d in ("corn", "water")},
               "pass": bool(med(v) >= 0.9)}
    t["B2"] = {"median_N_ratio": med(ratio), "pass": bool(med(ratio) <= 1 / 3 + 1e-9)}
    t["B3"] = {"unknown_abstained": ab_u, "n_unknown": len(unk), "known_false_abstain": ab_k, "n_known": len(known),
               "q_perp_unknown": [r["q_perp"] for r in unk],
               "pass": bool(ab_u >= 0.8 * len(unk) - 1e-9 and ab_k <= 0.10 * len(known) + 1e-9)}
    t["B4"] = {"median_recovery2": med(rec), "n": len(rec), "pass": bool(rec and med(rec) >= 0.75)}
    s_v = [r["S_rule"]["V_cap"] for r in known]
    t["reported_S_rule"] = {"median_V_cap": med(s_v), "mean_V_cap": float(np.mean(s_v)),
                            "projection_wins": int(sum(1 for r in known if r["V_cap"] > r["S_rule"]["V_cap"] + 1e-9)),
                            "projection_loses": int(sum(1 for r in known if r["V_cap"] < r["S_rule"]["V_cap"] - 1e-9))}
    gaps = [r for r in results if r["group"] == "gap"]
    t["reported_gap"] = [{"name": r["name"], "q_perp": r["q_perp"], "chosen": r["chosen_class"],
                          "oracle": r["oracle"], "dE_oracle_frac": r["dE_oracle"] / max(r["E0"], 1e-9)} for r in gaps]
    t["reported_identity"] = {"vs_injected": float(np.mean([r["identity_gt"] for r in known])),
                              "vs_oracle": float(np.mean([r["identity_oracle"] for r in known]))}
    per = {}
    for r in known:
        per.setdefault(r["classes"][0], []).append(r["V_cap"])
    t["reported_V_cap_by_class"] = {c: med(x) for c, x in per.items()}
    fails = [k for k in ("B1", "B2", "B3", "B4") if not t[k]["pass"]]
    verdict = "replicated: the simplified selector holds on fresh cases" if not fails else "not replicated: " + ", ".join(fails) + " fail"
    return {"results": results, "tests": t, "verdict": verdict}


def write_md(rep, path: Path) -> None:
    t = rep["tests"]
    L = ["# RGRE-1b results: replication of the simplified selector", "",
         "Preregistration: `docs/math-track-rgre1b-prereg.md`.", "",
         f"Threshold carried over unchanged from RGRE-1: tau = {rep['tau_perp']:.3f}. Seed {rep['seed']}.", "",
         "## Per case", "",
         "| case | injected | E0 | q_perp | chosen (reason) | oracle repair [class] | pick | V_cap | S-rule class | S-rule V | 2-step |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rep["results"]:
        ts = r.get("two_step", {})
        L.append(f"| {r['name']} | {'+'.join(r['classes'])} | {r['E0']:.3f} | {r['q_perp']:.2f} | {r['chosen_class']} ({r['reason']}) | "
                 f"{r['oracle']} [{r['oracle_class']}] | {r['pick']} | {r['V_cap']:.2f} | {r['S_rule']['class']} | {r['S_rule']['V_cap']:.2f} | "
                 f"{'-' if not ts else (None if ts.get('recovery2') is None else round(ts['recovery2'], 2))} |")
    L += ["", "## Frozen bars", "", "| bar | target | result | pass |", "|---|---|---|---|",
          f"| B1 oracle value captured | median >= 0.90 | {t['B1']['median_V_cap']:.3f} (mean {t['B1']['mean_V_cap']:.3f}, n {t['B1']['n']}) | {t['B1']['pass']} |",
          f"| B2 search reduction | median <= 1/3 | {t['B2']['median_N_ratio']:.3f} | {t['B2']['pass']} |",
          f"| B3 abstention | unknown >= 80%, known false <= 10% | {t['B3']['unknown_abstained']}/{t['B3']['n_unknown']} and {t['B3']['known_false_abstain']}/{t['B3']['n_known']} | {t['B3']['pass']} |",
          f"| B4 mixtures | median two-step >= 0.75 | {'-' if t['B4']['median_recovery2'] is None else round(t['B4']['median_recovery2'], 3)} (n {t['B4']['n']}) | {t['B4']['pass']} |",
          "", "## Reported, not scored", "",
          f"RGRE-1's coherence-weighted rule on the same cases: median {t['reported_S_rule']['median_V_cap']:.3f}, mean {t['reported_S_rule']['mean_V_cap']:.3f}; "
          f"the projection rule wins {t['reported_S_rule']['projection_wins']} cases and loses {t['reported_S_rule']['projection_loses']}.", "",
          f"Identity: {t['reported_identity']['vs_injected']:.2f} against the injected class, {t['reported_identity']['vs_oracle']:.2f} against the oracle's.", "",
          "Vocabulary-gap case (unscored): " + "; ".join(f"{g['name']} q_perp {g['q_perp']:.2f}, chose {g['chosen']}, oracle {g['oracle']} removing {g['dE_oracle_frac']*100:.0f}% of the error" for g in t["reported_gap"]), "",
          "Median value captured by injected class: " + ", ".join(f"{c} {x:.2f}" for c, x in t["reported_V_cap_by_class"].items()), "",
          f"## Verdict: {rep['verdict']}", ""]
    path.write_text("\n".join(L) + "\n")


def make_figure(rep, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    R = rep["results"]
    known = [r for r in R if r["group"] != "unknown"]
    unk = [r for r in R if r["group"] == "unknown"]
    mixes = [r for r in R if r["group"] == "mixture"]
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.6))
    ax = axes[0]
    ax.boxplot([[r["V_cap"] for r in known], [r["S_rule"]["V_cap"] for r in known]], tick_labels=["projection", "coherence (RGRE-1)"])
    ax.axhline(0.9, color="C3", ls=":")
    ax.set_ylabel("oracle value captured"); ax.set_title("B1 and the reported comparison")
    ax = axes[1]
    x = [r["S_rule"]["V_cap"] for r in known]
    y = [r["V_cap"] for r in known]
    ax.scatter(x, y, s=18)
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("coherence rule"); ax.set_ylabel("projection rule"); ax.set_title("per case")
    ax = axes[2]
    ax.scatter([r["q_perp"] for r in known], [r["V_cap"] for r in known], s=18, label="known")
    ax.scatter([r["q_perp"] for r in unk], [0] * len(unk), s=45, marker="x", color="C3", label="unknown")
    ax.axvline(rep["tau_perp"], color="k", ls=":")
    ax.set_xlabel("unexplained fraction"); ax.set_ylabel("V_cap"); ax.set_title("B3 abstention"); ax.legend(fontsize=8)
    ax = axes[3]
    xs = np.arange(len(mixes))
    ax.bar(xs - 0.2, [r["two_step"]["dE_rgre2"] for r in mixes], 0.4, label="RGRE two steps")
    ax.bar(xs + 0.2, [r["two_step"]["dE_oracle2"] for r in mixes], 0.4, label="two-step oracle")
    ax.set_xticks(xs); ax.set_xticklabels([r["name"].replace("mix_", "") for r in mixes], rotation=60, fontsize=6)
    ax.set_ylabel("error reduction"); ax.set_title("B4 mixtures"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
