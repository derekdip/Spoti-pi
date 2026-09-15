"""RGRE-1: residual-guided representation expansion, first test. Implements docs/math-track-rgre1-prereg.md.

Usage: python poc/rgre1_experiment.py [--out poc/results] [--seed 20260915] [--dev]
  --dev: development smoke test (seed 1, one case per class, results in a scratch directory), declared in the prereg.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout import parse_model  # noqa: E402
from rgre import core, corn, water  # noqa: E402
from w1_experiment import CENTRE  # noqa: E402

SEED = 20260915
TAU_CAP = 0.9
CLASS_ORDER = ("coordinate", "stop", "corner", "smooth", "tail", "unary", "interaction", "floor")
BASELINES = ("cheapest_first", "largest_opportunity", "best_local_projection")
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


def domain_of(case):
    return corn if isinstance(case, corn.CornCase) else water


def costs_of(case, s0, dom):
    if dom is water:
        return dict(water.COSTS)
    return None  # corn costs are known only after applying (vertex counts)


def run_case(case, tau_perp, two_step):
    dom = domain_of(case)
    repairs = dom.REPAIRS
    s0 = case.state0
    E0 = case.E(s0)
    r0, pred0 = case.residual(s0)
    signed, templates = case.diagnostics(s0, pred0)
    diag = core.diagnose(r0, signed, templates)
    cls, reason = core.select(diag, tau_perp)
    # oracle: every repair, from s0
    applied = {name: case.apply(s0, name) for name, _ in repairs}
    costs = {name: applied[name][1] for name in applied}
    value = {name: (E0 - applied[name][2]) / max(applied[name][1], 1e-9) for name in applied}
    dE = {name: E0 - applied[name][2] for name in applied}
    oracle = max(value, key=value.get)
    oracle_class = dict(repairs)[oracle]
    chosen = dom.REPAIR_SETS.get(cls, []) if cls else []
    best = max(chosen, key=lambda n: value[n]) if chosen else None
    v_rgre = value[best] if best else 0.0
    v_or = value[oracle]
    vcap = (v_rgre / v_or) if v_or > 1e-12 else (1.0 if v_rgre >= v_or else 0.0)
    k = max(len(chosen), 1)
    rank = core.baseline_rankings(diag, repairs, costs, CLASS_ORDER)
    base_v = {}
    for b, order in rank.items():
        pick = max(order[:k], key=lambda n: value[n])
        base_v[b] = {"pick": pick, "vcap": (value[pick] / v_or) if v_or > 1e-12 else (1.0 if value[pick] >= v_or else 0.0)}
    names = [n for n, _ in repairs]
    combos = list(itertools.combinations(names, k))
    base_v["random"] = {"pick": None, "vcap": float(np.mean([(max(value[n] for n in c) / v_or) if v_or > 1e-12 else 0.0 for c in combos]))}
    top = core.ranked_classes(diag, "S")
    known = case.classes != ("unknown",)
    out = {"name": case.name, "domain": "corn" if dom is corn else "water", "classes": list(case.classes), "E0": E0,
           "q": diag["q"], "raw": diag["raw"], "mu": diag["mu"], "S": diag["S"], "q_perp": diag["q_perp"], "q_signed_joint": diag["q_signed_joint"],
           "chosen_class": cls, "reason": reason, "top2": top[:2], "evaluated": chosen, "N_rgre": len(chosen), "N_all": len(repairs),
           "repairs": {n: {"cost": costs[n], "E": applied[n][2], "dE": dE[n], "value": value[n]} for n in names},
           "oracle": oracle, "oracle_class": oracle_class, "rgre_pick": best, "V_cap": vcap, "dE_rgre": dE[best] if best else 0.0, "dE_oracle": dE[oracle],
           "baselines": base_v, "identity_gt": (cls in case.classes) if (known and cls) else False,
           "identity_oracle": (cls == oracle_class) if cls else False, "oracle_in_top2": oracle_class in top[:2],
           "mu_chosen": diag["mu"].get(cls) if cls else None, "abstained": cls is None}
    if two_step and known:
        out["two_step"] = run_two_step(case, dom, s0, E0, diag, cls, chosen, applied, value, tau_perp)
    return out


def run_two_step(case, dom, s0, E0, diag0, cls1, chosen1, applied, value, tau_perp):
    names = [n for n, _ in dom.REPAIRS]
    # oracle over ordered pairs
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
    res = {"oracle_pair": best_pair, "dE_oracle2": dE_or2}
    # RGRE: repair, re-diagnose, repair
    if chosen1:
        pick1 = max(chosen1, key=lambda n: value[n])
        s1 = applied[pick1][0]
        E1 = applied[pick1][2]
        r1, pred1 = case.residual(s1)
        signed, templates = case.diagnostics(s1, pred1)
        diag1 = core.diagnose(r1, signed, templates)
        cls2, reason2 = core.select(diag1, tau_perp)
        chosen2 = dom.REPAIR_SETS.get(cls2, []) if cls2 else []
        E2 = E1
        pick2 = None
        if chosen2:
            ev = {n: case.apply(s1, n) for n in chosen2}
            pick2 = min(ev, key=lambda n: ev[n][2])
            E2 = ev[pick2][2]
        other = [c for c in case.classes if c != cls1]
        d2 = other[0] if other else None
        res.update({"pick1": pick1, "cls1": cls1, "cls2": cls2, "reason2": reason2, "pick2": pick2, "E1": E1, "E2": E2, "dE_rgre2": E0 - E2,
                    "recovery2": (E0 - E2) / dE_or2 if dE_or2 > 1e-12 else None,
                    "q1_before": diag0["q"].get(cls1), "q1_after": diag1["q"].get(cls1),
                    "q2_before": diag0["q"].get(d2) if d2 else None, "q2_after": diag1["q"].get(d2) if d2 else None,
                    "own_shift": bool(d2 and diag1["q"].get(cls1, 0) < diag0["q"].get(cls1, 0) and diag1["q"].get(d2, 0) > diag0["q"].get(d2, 0)),
                    "N_eval2": len(chosen1) + len(chosen2)})
        # ablation: top-two classes at r0, no re-diagnosis
        top = core.ranked_classes(diag0, "S")
        clsb = next((c for c in top if c != cls1 and c in dom.REPAIR_SETS and dom.REPAIR_SETS[c]), None)
        Eb = E1
        pickb = None
        if clsb:
            ev = {n: case.apply(s1, n) for n in dom.REPAIR_SETS[clsb]}
            pickb = min(ev, key=lambda n: ev[n][2])
            Eb = ev[pickb][2]
        res.update({"ablation_cls2": clsb, "ablation_pick2": pickb, "dE_ablation2": E0 - Eb, "rediagnosis_wins": bool((E0 - E2) > (E0 - Eb) + 1e-9), "rediagnosis_ties": bool(abs((E0 - E2) - (E0 - Eb)) <= 1e-9)})
    else:
        res.update({"pick1": None, "cls1": None, "dE_rgre2": 0.0, "recovery2": 0.0 if dE_or2 > 1e-12 else None, "own_shift": False, "dE_ablation2": 0.0, "rediagnosis_wins": False, "rediagnosis_ties": True, "N_eval2": 0})
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--dev", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    tag = "rgre1_dev" if args.dev else "rgre1"
    res_dir = Path(__file__).resolve().parent / "results"
    model0 = parse_model(json.loads((res_dir / "gpu_sweep.json").read_text())["terms"]["wake + presence"]["description"])
    theta0 = json.loads((res_dir / "w1.json").read_text())["token"]["params"]
    grid = water.Grid(water.base_params(), CENTRE)
    log("computing the water floor field")
    floor_full = water.floor_field_full(theta0, grid)

    # ---- calibration of the abstention threshold on old cases ----
    log("calibration cases")
    old = corn.old_cases(model0) + water.old_cases(theta0, grid, floor_full)
    calib = {}
    for c in old:
        r0, pred0 = c.residual(c.state0)
        signed, templates = c.diagnostics(c.state0, pred0)
        d = core.diagnose(r0, signed, templates)
        calib[c.name] = {"q_perp": d["q_perp"], "q": d["q"], "S": d["S"], "mu": d["mu"]}
        log(f"  {c.name:24s} q_perp {d['q_perp']:.3f}  q {{{', '.join(f'{k} {v:.2f}' for k, v in d['q'].items())}}}")
    tau_perp = min(TAU_CAP, max(v["q_perp"] for v in calib.values()) + 0.1)
    log(f"tau_perp = {tau_perp:.3f}")

    # ---- fresh benchmark ----
    seed = 1 if args.dev else args.seed
    log(f"building corn cases (seed {seed})")
    c_iso, c_mix, c_unk = corn.fresh_cases(model0, seed)
    log("building water cases")
    w_iso, w_mix, w_unk = water.fresh_cases(theta0, grid, floor_full, log=log)
    if args.dev:
        seen = set()
        keep = []
        for c in c_iso + w_iso:
            key = (c.__class__.__name__, c.classes)
            if key not in seen:
                seen.add(key)
                keep.append(c)
        c_iso = [c for c in keep if isinstance(c, corn.CornCase)]
        w_iso = [c for c in keep if isinstance(c, water.WaterCase)]
        c_mix, w_mix, c_unk, w_unk = c_mix[:1], w_mix[:1], c_unk[:1], w_unk[:1]
    results = []
    for group, cases, two in (("isolated", c_iso + w_iso, False), ("mixture", c_mix + w_mix, True), ("unknown", c_unk + w_unk, False)):
        for c in cases:
            t1 = time.time()
            r = run_case(c, tau_perp, two)
            r["group"] = group
            r["seconds"] = time.time() - t1
            results.append(r)
            log(f"{group:8s} {r['name']:28s} E0 {r['E0']:.3f} chose {str(r['chosen_class']):11s} ({r['reason']}) q_perp {r['q_perp']:.2f} oracle {r['oracle']:16s} [{r['oracle_class']}] V_cap {r['V_cap']:.2f}  dE rgre {r['dE_rgre']:.3f} / or {r['dE_oracle']:.3f}"
                + (f"  2-step rec {r['two_step'].get('recovery2')}" if 'two_step' in r else ""))
    report = score(results, calib, tau_perp)
    report["seed"] = seed
    (out / f"{tag}.json").write_text(json.dumps(report, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    write_md(report, out / f"{tag}.md")
    try:
        make_figure(report, out / f"{tag}.png")
    except Exception as exc:  # noqa: BLE001
        log(f"(figure skipped: {exc})")
    log(json.dumps(report["tests"], indent=1, default=str))
    log(f"verdict: {report['verdict']}")
    log(f"wrote {out / (tag + '.md')}")


def score(results, calib, tau_perp):
    known = [r for r in results if r["group"] != "unknown"]
    unk = [r for r in results if r["group"] == "unknown"]
    mixes = [r for r in results if r["group"] == "mixture"]
    med = lambda xs: float(np.median(xs)) if len(xs) else None  # noqa: E731
    vcap = [r["V_cap"] for r in known]
    tests = {}
    tests["H1"] = {"median_V_cap": med(vcap), "mean_V_cap": float(np.mean(vcap)), "median_dE_rgre": med([r["dE_rgre"] for r in known]), "median_dE_oracle": med([r["dE_oracle"] for r in known]),
                   "by_domain": {d: med([r["V_cap"] for r in known if r["domain"] == d]) for d in ("corn", "water")}, "pass": bool(med(vcap) >= 0.75)}
    ratio = [r["N_rgre"] / r["N_all"] for r in known]
    tests["H2"] = {"median_N_ratio": med(ratio), "pass": bool(med(ratio) <= 1 / 3 + 1e-9 and tests["H1"]["pass"])}
    bmed = {b: med([r["baselines"][b]["vcap"] for r in known]) for b in BASELINES + ("random",)}
    tests["H3"] = {"baseline_median_V_cap": bmed, "rgre_median_V_cap": med(vcap), "pass": bool(all(med(vcap) > bmed[b] for b in BASELINES))}
    rec = [r["two_step"]["recovery2"] for r in mixes if r["two_step"].get("recovery2") is not None]
    own = [r["two_step"]["own_shift"] for r in mixes]
    tests["H4"] = {"median_recovery2": med(rec), "ownership_shift_count": int(sum(own)), "n_mixtures": len(mixes), "pass": bool(rec and med(rec) >= 0.7)}
    abst_unk = int(sum(r["abstained"] for r in unk))
    abst_known = int(sum(r["abstained"] for r in known))
    tests["H5"] = {"tau_perp": tau_perp, "unknown_abstained": abst_unk, "n_unknown": len(unk), "known_false_abstain": abst_known, "n_known": len(known),
                   "q_perp_unknown": [r["q_perp"] for r in unk], "pass": bool(len(unk) and abst_unk >= np.ceil(5 / 6 * len(unk) - 1e-9) and abst_known <= 0.10 * len(known))}
    lo = [r for r in known if r["mu_chosen"] is not None and r["mu_chosen"] < 0.5]
    hi = [r for r in known if r["mu_chosen"] is not None and r["mu_chosen"] >= 0.5]
    acc = lambda rs: float(np.mean([r["identity_oracle"] for r in rs])) if rs else None  # noqa: E731
    tests["H6"] = {"identity_low_mu": acc(lo), "identity_high_mu": acc(hi), "n_low": len(lo), "n_high": len(hi),
                   "oracle_value_low_mu": med([r["dE_oracle"] for r in lo]), "oracle_value_high_mu": med([r["dE_oracle"] for r in hi]),
                   "pass": bool(lo and hi and acc(hi) < acc(lo))}
    wins = int(sum(r["two_step"]["rediagnosis_wins"] for r in mixes))
    ties = int(sum(r["two_step"]["rediagnosis_ties"] for r in mixes))
    tests["H7"] = {"rediagnosis_wins": wins, "ties": ties, "n": len(mixes), "median_dE_rediag": med([r["two_step"]["dE_rgre2"] for r in mixes]), "median_dE_ablation": med([r["two_step"]["dE_ablation2"] for r in mixes]),
                   "pass": bool(mixes and wins > (len(mixes) - ties) / 2)}
    id_gt = float(np.mean([r["identity_gt"] for r in known]))
    id_or = float(np.mean([r["identity_oracle"] for r in known]))
    top2 = float(np.mean([r["oracle_in_top2"] for r in known]))
    tests["identity"] = {"vs_injected": id_gt, "vs_oracle": id_or, "oracle_in_top2": top2}
    per_class = {}
    for r in known:
        for c in r["classes"]:
            per_class.setdefault(c, []).append(r["V_cap"])
    tests["V_cap_by_class"] = {c: med(v) for c, v in per_class.items()}
    if tests["H1"]["pass"] and tests["H2"]["pass"] and tests["H4"]["pass"] and tests["H5"]["pass"]:
        verdict = "A: procedure supported"
    elif not tests["H3"]["pass"]:
        verdict = "D: no useful compression of search"
    elif id_gt >= 0.7 and not tests["H1"]["pass"]:
        verdict = "B: diagnosis works, selection does not"
    elif top2 >= 0.75 and id_or < 0.7 and not tests["H1"]["pass"]:
        verdict = "C: opportunity works, identity does not"
    else:
        verdict = "no named outcome: " + ", ".join(k for k in ("H1", "H2", "H4", "H5") if not tests[k]["pass"]) + " fail"
    return {"tau_perp": tau_perp, "calibration": calib, "results": results, "tests": tests, "verdict": verdict}


def write_md(rep, path: Path) -> None:
    t = rep["tests"]
    L = ["# RGRE-1 results", "", "Preregistration: `docs/math-track-rgre1-prereg.md`.", "", f"Abstention threshold tau_perp = {rep['tau_perp']:.3f} from the calibration cases: "
         + ", ".join(f"{k} {v['q_perp']:.2f}" for k, v in rep["calibration"].items()) + ".", "",
         "## Per case", "", "| case | classes | E0 | q_perp | chosen (reason) | mu | oracle repair [class] | RGRE pick | V_cap | dE RGRE / oracle | N | 2-step recovery |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rep["results"]:
        ts = r.get("two_step", {})
        L.append(f"| {r['name']} | {'+'.join(r['classes'])} | {r['E0']:.3f} | {r['q_perp']:.2f} | {r['chosen_class']} ({r['reason']}) | {'-' if r['mu_chosen'] is None else round(r['mu_chosen'], 2)} | {r['oracle']} [{r['oracle_class']}] | {r['rgre_pick']} | {r['V_cap']:.2f} | {r['dE_rgre']:.3f} / {r['dE_oracle']:.3f} | {r['N_rgre']}/{r['N_all']} | {'-' if not ts else (None if ts.get('recovery2') is None else round(ts['recovery2'], 2))} |")
    L += ["", "## Tests", "", "| test | result | pass |", "|---|---|---|"]
    for k in ("H1", "H2", "H3", "H4", "H5", "H6", "H7"):
        v = dict(t[k])
        p = v.pop("pass")
        L.append(f"| {k} | {json.dumps(v, default=str)} | {p} |")
    L += ["", f"Identity: vs injected {t['identity']['vs_injected']:.2f}; vs oracle {t['identity']['vs_oracle']:.2f}; oracle class in top-2 {t['identity']['oracle_in_top2']:.2f}.", "",
          "V_cap by injected class: " + ", ".join(f"{c} {v:.2f}" for c, v in t["V_cap_by_class"].items()), "", f"## Verdict: {rep['verdict']}", ""]
    path.write_text("\n".join(L) + "\n")


def make_figure(rep, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    R = rep["results"]
    known = [r for r in R if r["group"] != "unknown"]
    unk = [r for r in R if r["group"] == "unknown"]
    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    ax = axes[0, 0]
    labels = ["RGRE"] + list(BASELINES) + ["random"]
    vals = [[r["V_cap"] for r in known]] + [[r["baselines"][b]["vcap"] for r in known] for b in BASELINES + ("random",)]
    ax.boxplot(vals, labels=labels)
    ax.axhline(0.75, color="C3", ls=":"); ax.set_ylabel("V_cap (oracle value captured)"); ax.set_title("H1 / H3"); ax.tick_params(axis="x", rotation=25, labelsize=8)
    ax = axes[0, 1]
    ax.scatter([r["q_perp"] for r in known], [r["V_cap"] for r in known], s=14, label="known")
    ax.scatter([r["q_perp"] for r in unk], [0] * len(unk), s=40, marker="x", color="C3", label="unknown")
    ax.axvline(rep["tau_perp"], color="k", ls=":"); ax.set_xlabel("q_perp"); ax.set_ylabel("V_cap"); ax.set_title("H5: abstention"); ax.legend(fontsize=8)
    ax = axes[0, 2]
    mus = [r["mu_chosen"] for r in known if r["mu_chosen"] is not None]
    ids = [r["identity_oracle"] for r in known if r["mu_chosen"] is not None]
    ax.scatter(mus, ids, s=14); ax.set_xlabel("mu of chosen class"); ax.set_ylabel("identity vs oracle (0/1)"); ax.set_title("H6: coherence vs identity")
    ax = axes[1, 0]
    classes = sorted({c for r in known for c in r["classes"]} | {r["chosen_class"] for r in known if r["chosen_class"]})
    M = np.zeros((len(classes), len(classes) + 1))
    for r in known:
        i = classes.index(r["classes"][0])
        j = classes.index(r["chosen_class"]) if r["chosen_class"] else len(classes)
        M[i, j] += 1
    ax.imshow(M, cmap="Blues"); ax.set_xticks(range(len(classes) + 1)); ax.set_xticklabels(classes + ["abstain"], rotation=45, fontsize=7); ax.set_yticks(range(len(classes))); ax.set_yticklabels(classes, fontsize=7)
    ax.set_xlabel("chosen"); ax.set_ylabel("injected (first)"); ax.set_title("diagnosis confusion")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i, j]:
                ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=7)
    ax = axes[1, 1]
    mixes = [r for r in R if r["group"] == "mixture"]
    x = np.arange(len(mixes))
    ax.bar(x - 0.2, [r["two_step"]["dE_rgre2"] for r in mixes], 0.4, label="re-diagnose")
    ax.bar(x + 0.2, [r["two_step"]["dE_ablation2"] for r in mixes], 0.4, label="no re-diagnosis")
    ax.plot(x, [r["two_step"]["dE_oracle2"] for r in mixes], "k_", ms=12, label="2-step oracle")
    ax.set_xticks(x); ax.set_xticklabels([r["name"] for r in mixes], rotation=60, fontsize=6); ax.set_ylabel("two-step error reduction"); ax.set_title("H4 / H7"); ax.legend(fontsize=7)
    ax = axes[1, 2]
    for c, v in rep["tests"]["V_cap_by_class"].items():
        ax.bar(c, v)
    ax.axhline(0.75, color="C3", ls=":"); ax.set_ylabel("median V_cap"); ax.set_title("by injected class"); ax.tick_params(axis="x", rotation=30, labelsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
