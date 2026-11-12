"""Math Track W2: predictive representation selection from W1 data. Implements docs/math-track-w2-prereg.md.

Usage: python poc/w2_analysis.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

import numpy as np

GRIDS = [12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
CAL = [64, 96]
HELD = [128, 192, 256]
TARGETS = [0.3, 0.2, 0.14, 0.1, 0.07, 0.05, 0.035, 0.025, 0.018, 0.0125, 0.009, 0.006, 0.004, 0.003, 0.002]
ALPHA = {("bilinear", "height"): 1.0, ("bilinear", "slope"): 0.5, ("bicubic", "height"): 2.0, ("bicubic", "slope"): 1.5}
REPS = ("bilinear", "bicubic")
CONS = ("height", "slope")


def load(out: Path):
    q2 = json.loads((out / "w1.json").read_text())["Q2"]["errors"]
    E = {}
    for R in REPS:
        for G in CONS:
            E[(R, G)] = {n: q2[R][str(n)]["E_" + G] for n in GRIDS}
    return E


def calibrate(E, alpha_of):
    a = {}
    for key, curve in E.items():
        al = alpha_of[key]
        a[key] = float(np.exp(np.mean([np.log(curve[n]) + al * np.log(n * n) for n in CAL])))
    return a


def two_point(E):
    """Baseline D: unconstrained power law through the two calibration points."""
    a, al = {}, {}
    for key, curve in E.items():
        n1, n2 = CAL
        s = (np.log(curve[n2]) - np.log(curve[n1])) / (np.log(n2 * n2) - np.log(n1 * n1))
        al[key] = float(-s)
        a[key] = float(np.exp(np.log(curve[n1]) + al[key] * np.log(n1 * n1)))
    return a, al


def n_hat(a, al, eps):
    need = (a / eps) ** (1.0 / al)
    for n in GRIDS:
        if n * n >= need:
            return n
    return None


def n_star(curve, eps):
    for n in GRIDS:
        if curve[n] <= eps:
            return n
    return None


def rank(n):
    return GRIDS.index(n)


def evaluate(E, a, al, name):
    res = {"name": name, "H1": {}, "H2": {}, "logerr": {}, "meanD": None}
    Ds = []
    for key, curve in E.items():
        for eps in TARGETS:
            ns = n_star(curve, eps)
            if ns is None:
                continue
            nh = n_hat(a[key], al[key], eps)
            D = None if nh is None else abs(rank(nh) - rank(ns))
            res["H1"][f"{key[0]}/{key[1]}@{eps}"] = {"n_star": ns, "n_hat": nh, "D": D}
            Ds.append(D if D is not None else len(GRIDS))
    res["H1_frac_within_1"] = float(np.mean([d <= 1 for d in Ds])) if Ds else None
    res["meanD"] = float(np.mean(Ds)) if Ds else None
    # held-out log error
    le = []
    for key, curve in E.items():
        for n in HELD:
            le.append(abs(np.log(a[key] * (n * n) ** (-al[key])) - np.log(curve[n])))
    res["held_out_log_error"] = float(np.mean(le))
    # winner per consumer and target
    hits, tot = 0, 0
    for G in CONS:
        for eps in TARGETS:
            ns = {R: n_star(E[(R, G)], eps) for R in REPS}
            if any(v is None for v in ns.values()) or ns["bilinear"] == ns["bicubic"]:
                continue
            actual = min(ns, key=ns.get)
            nh = {R: n_hat(a[(R, G)], al[(R, G)], eps) for R in REPS}
            if any(v is None for v in nh.values()):
                pred = None
            elif nh["bilinear"] == nh["bicubic"]:
                pred = "tie"
            else:
                pred = min(nh, key=nh.get)
            res["H2"][f"{G}@{eps}"] = {"actual": actual, "predicted": pred}
            tot += 1
            hits += int(pred == actual)
    res["H2_accuracy"] = float(hits / tot) if tot else None
    res["H2_n"] = tot
    return res


def winner_rule(E, rule):
    """Baselines A, B, C as winner predictors; returns accuracy on the same non-tied targets."""
    hits, tot = 0, 0
    for G in CONS:
        for eps in TARGETS:
            ns = {R: n_star(E[(R, G)], eps) for R in REPS}
            if any(v is None for v in ns.values()) or ns["bilinear"] == ns["bicubic"]:
                continue
            actual = min(ns, key=ns.get)
            if rule == "A":
                pred = "bilinear"
            elif rule == "B":
                pred = "bicubic"
            else:
                pred = "bilinear" if E[("bilinear", G)][64] <= E[("bicubic", G)][64] else "bicubic"
            tot += 1
            hits += int(pred == actual)
    return float(hits / tot) if tot else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    E = load(out)
    a = calibrate(E, ALPHA)
    model = evaluate(E, a, ALPHA, "frozen-exponent model")
    a2, al2 = two_point(E)
    base_d = evaluate(E, a2, al2, "two-point power law (baseline D)")
    base = {"A_always_bilinear": winner_rule(E, "A"), "B_always_bicubic": winner_rule(E, "B"), "C_lower_at_64": winner_rule(E, "C")}

    # H3 / H4 crossovers
    cross = {}
    for G in CONS:
        aA, aB = a[("bilinear", G)], a[("bicubic", G)]
        alA, alB = ALPHA[("bilinear", G)], ALPHA[("bicubic", G)]
        eps_pred = float(np.exp((alB * np.log(aA) - alA * np.log(aB)) / (alB - alA)))
        # empirical: sequence of actual winners along the targets (loose -> tight)
        seq = []
        for eps in TARGETS:
            ns = {R: n_star(E[(R, G)], eps) for R in REPS}
            if any(v is None for v in ns.values()):
                seq.append(None)
            elif ns["bilinear"] == ns["bicubic"]:
                seq.append("tie")
            else:
                seq.append(min(ns, key=ns.get))
        emp = None
        for i in range(1, len(TARGETS)):
            if seq[i - 1] in REPS and seq[i] in REPS and seq[i - 1] != seq[i]:
                emp = (TARGETS[i - 1], TARGETS[i])
                break
        if emp is None:
            ok = None
            wins = [s for s in seq if s in REPS]
            if wins:
                dominant = max(set(wins), key=wins.count)
                # bicubic wins at tight eps (below eps*); bilinear at loose (above)
                ok = bool((dominant == "bicubic" and eps_pred > max(TARGETS)) or (dominant == "bilinear" and eps_pred < min(TARGETS)))
            cross[G] = {"eps_pred": eps_pred, "empirical_interval": None, "winner_sequence": seq, "H3_pass": ok}
        else:
            lo, hi = min(emp), max(emp)
            # within one target interval: between the neighbours of the empirical interval
            i_lo, i_hi = TARGETS.index(hi), TARGETS.index(lo)
            wide_hi = TARGETS[max(i_lo - 1, 0)]
            wide_lo = TARGETS[min(i_hi + 1, len(TARGETS) - 1)]
            cross[G] = {"eps_pred": eps_pred, "empirical_interval": [lo, hi], "winner_sequence": seq,
                        "H3_pass": bool(wide_lo <= eps_pred <= wide_hi)}
    h4 = bool(cross["slope"]["eps_pred"] > cross["height"]["eps_pred"])

    # H6 binding consumer over target pairs
    hits, tot, cells = 0, 0, []
    for eps_h, eps_n in product(TARGETS, TARGETS):
        act_req, pred_req, act_bind, pred_bind = {}, {}, {}, {}
        for R in REPS:
            nsh, nsn = n_star(E[(R, "height")], eps_h), n_star(E[(R, "slope")], eps_n)
            nhh, nhn = n_hat(a[(R, "height")], ALPHA[(R, "height")], eps_h), n_hat(a[(R, "slope")], ALPHA[(R, "slope")], eps_n)
            act_req[R] = None if (nsh is None or nsn is None) else max(nsh, nsn)
            act_bind[R] = None if act_req[R] is None else ("tie" if nsh == nsn else ("height" if nsh > nsn else "slope"))
            pred_req[R] = None if (nhh is None or nhn is None) else max(nhh, nhn)
            pred_bind[R] = None if pred_req[R] is None else ("tie" if nhh == nhn else ("height" if nhh > nhn else "slope"))
        reach = [R for R in REPS if act_req[R] is not None]
        if not reach:
            cells.append({"eps_h": eps_h, "eps_n": eps_n, "actual": None, "predicted": None})
            continue
        actual_R = min(reach, key=lambda R: act_req[R])
        preach = [R for R in REPS if pred_req[R] is not None]
        pred_R = min(preach, key=lambda R: pred_req[R]) if preach else None
        cells.append({"eps_h": eps_h, "eps_n": eps_n, "actual": actual_R, "predicted": pred_R,
                      "actual_binding": act_bind[actual_R], "predicted_binding": pred_bind.get(actual_R)})
        if act_bind[actual_R] in CONS and pred_bind.get(actual_R) in CONS:
            tot += 1
            hits += int(act_bind[actual_R] == pred_bind[actual_R])
    h6 = float(hits / tot) if tot else None
    map_hits = [c for c in cells if c["actual"] and c["predicted"]]
    map_acc = float(np.mean([c["actual"] == c["predicted"] for c in map_hits])) if map_hits else None

    report = {"alpha": {f"{k[0]}/{k[1]}": v for k, v in ALPHA.items()}, "a": {f"{k[0]}/{k[1]}": v for k, v in a.items()},
              "two_point": {"a": {f"{k[0]}/{k[1]}": v for k, v in a2.items()}, "alpha": {f"{k[0]}/{k[1]}": v for k, v in al2.items()}},
              "model": model, "baseline_D": base_d, "baselines_winner": base, "crossover": cross, "H4": h4,
              "H6": {"accuracy": h6, "n": tot, "map_accuracy": map_acc}, "map": cells,
              "verdict": {"H1": bool(model["H1_frac_within_1"] is not None and model["H1_frac_within_1"] >= 0.75),
                          "H2": bool(model["H2_accuracy"] is not None and model["H2_accuracy"] >= 0.8),
                          "H5": bool(model["held_out_log_error"] < base_d["held_out_log_error"] or model["meanD"] < base_d["meanD"]),
                          "H6": bool(h6 is not None and h6 >= 0.8)}}
    (out / "w2.json").write_text(json.dumps(report, indent=2, default=str))
    write_md(report, E, out / "w2.md")
    try:
        make_map(report, out / "w2.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(json.dumps({"verdict": report["verdict"], "H1": model["H1_frac_within_1"], "H2": model["H2_accuracy"], "H2_n": model["H2_n"],
                      "H5": {"model_logerr": model["held_out_log_error"], "D_logerr": base_d["held_out_log_error"], "model_meanD": model["meanD"], "D_meanD": base_d["meanD"]},
                      "H3": {G: (cross[G]["eps_pred"], cross[G]["empirical_interval"], cross[G]["H3_pass"]) for G in CONS}, "H4": h4, "H6": h6, "baselines": base}, indent=2, default=str))
    print(f"wrote {out}")


def write_md(r, E, path: Path) -> None:
    m, d = r["model"], r["baseline_D"]
    L = ["# Math Track W2 results: predictive representation selection", "", "Preregistration: `docs/math-track-w2-prereg.md`. Data: W1 run 2, Q2.", "",
         "## Calibration (n = 64, 96 only)", "", "| curve | frozen alpha | a | two-point alpha (baseline D) |", "|---|---|---|---|"]
    for k in r["alpha"]:
        L.append(f"| {k} | {r['alpha'][k]} | {r['a'][k]:.4g} | {r['two_point']['alpha'][k]:.2f} |")
    L += ["", "## H1 resolution prediction (reachable targets)", "", "| curve @ eps | actual n* | predicted n-hat | D |", "|---|---|---|---|"]
    for k, v in m["H1"].items():
        L.append(f"| {k} | {v['n_star']} | {v['n_hat']} | {v['D']} |")
    L += ["", f"Fraction with D <= 1: {m['H1_frac_within_1']:.2f} (bar 0.75). Mean D: {m['meanD']:.2f} (two-point baseline {d['meanD']:.2f}).", "",
          "## H2 representation winner (both reachable, non-tied)", "", "| consumer @ eps | actual | predicted |", "|---|---|---|"]
    for k, v in m["H2"].items():
        L.append(f"| {k} | {v['actual']} | {v['predicted']} |")
    b = r["baselines_winner"]
    L += ["", f"Winner accuracy: model {m['H2_accuracy']:.2f} over {m['H2_n']} targets (bar 0.80); two-point baseline {d['H2_accuracy']:.2f}; "
          f"always bilinear {b['A_always_bilinear']:.2f}; always bicubic {b['B_always_bicubic']:.2f}; lower-at-64 {b['C_lower_at_64']:.2f}.", "",
          "## H3 / H4 crossovers", ""]
    for G, c in r["crossover"].items():
        L.append(f"- {G}: predicted eps* = {c['eps_pred']:.4f}; empirical crossover interval {c['empirical_interval']}; winners loose to tight: {c['winner_sequence']}; H3 pass {c['H3_pass']}")
    L += ["", f"H4 (slope crossover looser than height): {r['H4']}.", "",
          "## H5 held-out log error (grids 128, 192, 256)", "", f"Frozen-exponent model {m['held_out_log_error']:.3f} vs two-point power law {d['held_out_log_error']:.3f}; mean D {m['meanD']:.2f} vs {d['meanD']:.2f}.", "",
          f"## H6 binding consumer: {r['H6']['accuracy']:.2f} over {r['H6']['n']} non-tied target pairs (bar 0.80); deployment-map winner accuracy {r['H6']['map_accuracy']:.2f}.", "",
          "## Verdict", "", "| hypothesis | pass |", "|---|---|"]
    for k, v in r["verdict"].items():
        L.append(f"| {k} | {v} |")
    path.write_text("\n".join(L) + "\n")


def make_map(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cells = r["map"]
    eps = sorted({c["eps_h"] for c in cells}, reverse=True)
    idx = {e: i for i, e in enumerate(eps)}
    code = {"bilinear": 0, "bicubic": 1, None: np.nan}
    P = np.full((len(eps), len(eps)), np.nan)
    A = np.full((len(eps), len(eps)), np.nan)
    for c in cells:
        P[idx[c["eps_n"]], idx[c["eps_h"]]] = code[c["predicted"]]
        A[idx[c["eps_n"]], idx[c["eps_h"]]] = code[c["actual"]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, M, title in ((axes[0], P, "predicted cheapest representation"), (axes[1], A, "actual cheapest representation (W1)")):
        ax.imshow(M, cmap="coolwarm", vmin=0, vmax=1, origin="lower")
        ax.set_xticks(range(len(eps)))
        ax.set_xticklabels([f"{e:g}" for e in eps], rotation=90, fontsize=7)
        ax.set_yticks(range(len(eps)))
        ax.set_yticklabels([f"{e:g}" for e in eps], fontsize=7)
        ax.set_xlabel("height tolerance eps_h (loose -> tight)")
        ax.set_ylabel("slope tolerance eps_n (loose -> tight)")
        ax.set_title(title + "  (blue = bilinear, red = bicubic, blank = unreachable)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
