"""Math Track B4: corner law under the local supremum score. Implements docs/math-track-b4-prereg.md.

Usage: python poc/b4_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))

import b2_experiment as b2  # noqa: E402
import b3_experiment as b3  # noqa: E402
from holdout import parse_model  # noqa: E402
from reactive.causes import PathToken  # noqa: E402
from reactive.teacher import TeacherParams, stalk_grid  # noqa: E402
from reactive.worldlines import embedded_corner, family, tangential_probe  # noqa: E402

SUP = (0.00484, 0.00968, 0.01935, 0.03870)
PRIMARY_SUP = (0.00968, 0.01935)
RMS = b2.THRESHOLDS
RMS_PRIMARY = (0.00130, 0.00261)
TOLS = b3.TOLS
LENGTHS = (4, 8, 16, 32)
HOLDOUT = b3.HOLDOUT
H4_EPS = 0.01935
N_BINS = 12


def strip_grid(w, margin=2.0, spacing=0.25):
    lo = w.points.min(0) - margin
    hi = w.points.max(0) + margin
    xs = np.arange(lo[0], hi[0] + spacing, spacing)
    ys = np.arange(lo[1], hi[1] + spacing, spacing)
    gx, gy = np.meshgrid(xs, ys, indexing="xy")
    pts = np.stack([gx.ravel(), gy.ravel()], -1)
    d, _ = cKDTree(w.points).query(pts)
    return pts[d <= margin]


def errors(pred, ref, mask):
    d = np.linalg.norm(pred - ref, axis=-1)[:, mask]
    return float(d.max()), float(np.sqrt((d ** 2).mean()))


def sweep(w, cons):
    ref, g = cons.field(w, PathToken(w.points, w.times))
    mask = g.path_dperp < b2.LOCAL_R
    forced = b2.event_vertices(w.speed)
    rows = []
    for tol in TOLS:
        idx = b2.weighted_time_dp(w.points, w.times, np.ones(len(w.times)), tol, forced)
        pred, _ = cons.field(w, PathToken(w.points[idx], w.times[idx]))
        s, r = errors(pred, ref, mask)
        rows.append({"tol": float(tol), "N": int(len(idx)), "sup": s, "rms": r, "idx": idx})
    return rows, int(len(forced))


def n_at(rows, eps, key):
    ok = [r for r in rows if r[key] <= eps]
    if not ok:
        return None, None
    best = min(ok, key=lambda r: r["N"])
    return best["N"], best["idx"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    two = parse_model(json.loads((out / "gpu_sweep.json").read_text())["terms"]["wake + presence"]["description"])
    tp = TeacherParams()
    pos10 = stalk_grid(tp)
    times10 = np.arange(int(tp.duration * b2.FPS) + 1) / b2.FPS
    cons10 = b2.Consumer(two, pos10, times10)

    data = {}

    def record(w, cons):
        rows, n_event = sweep(w, cons)
        cs = b3.corners(w)
        cmask = np.zeros(len(w.times), dtype=bool)
        for i0, i1, _ in cs:
            cmask[i0:i1] = True
        dt = w.times[1] - w.times[0]
        data[w.name] = {"w": w, "rows": rows, "N_event": n_event, "corners": cs, "cmask": cmask,
                        "K": float(sum(2 * np.sin(abs(th) / 2) for _, _, th in cs)),
                        "turning": float(np.trapezoid(np.abs(w.heading_rate) * (w.speed > 1e-6), dx=dt)),
                        "N_sup": {str(e): n_at(rows, e, "sup")[0] for e in SUP},
                        "N_rms": {str(e): n_at(rows, e, "rms")[0] for e in RMS},
                        "IDX_sup": {str(e): n_at(rows, e, "sup")[1] for e in SUP}}
        d = data[w.name]
        print(f"{w.name:14s} N_sup={[d['N_sup'][str(e)] for e in SUP]} N_rms={[d['N_rms'][str(e)] for e in RMS]} N_event={n_event} K={d['K']:.2f} turning={d['turning']:.2f}")

    # holdouts and 10 m field probes
    for w in family():
        if w.name in HOLDOUT or w.name == "circle":
            record(w, cons10)
    record(tangential_probe(), cons10)
    # transfer probes on their own strips
    for L in LENGTHS:
        for wc in (True, False):
            w = embedded_corner(L, wc)
            pos = strip_grid(w)
            times = np.arange(int((w.times[-1]) * b2.FPS) + 1) / b2.FPS
            record(w, b2.Consumer(two, pos, times))

    # ---- H0 transfer invariance ----
    h0 = {"sup": {}, "rms": {}}
    for e in SUP:
        vals = {}
        for L in LENGTHS:
            a, b = data[f"corner_L{L}"]["N_sup"][str(e)], data[f"straight_L{L}"]["N_sup"][str(e)]
            vals[L] = None if (a is None or b is None) else a - b
        h0["sup"][str(e)] = vals
        ok = [v for v in vals.values() if v is not None]
        ratio = (max(ok) / min(ok)) if ok and min(ok) > 0 else None
        h0["sup"][str(e) + "_ratio"] = ratio
        h0["sup"][str(e) + "_pass"] = bool(ratio is not None and ratio <= 1.5 and len(ok) == len(LENGTHS))
        print(f"H0 sup eps {e*1000:.2f} mm: N_corner by L {vals} ratio {ratio}")
    for e in RMS:
        vals = {}
        for L in LENGTHS:
            a, b = data[f"corner_L{L}"]["N_rms"][str(e)], data[f"straight_L{L}"]["N_rms"][str(e)]
            vals[L] = None if (a is None or b is None) else a - b
        h0["rms"][str(e)] = vals
        r = None if (vals[32] is None or vals[4] in (None, 0)) else vals[32] / vals[4]
        h0["rms"][str(e) + "_ratio_32_over_4"] = r
        print(f"H0 rms control eps {e*1000:.2f} mm: N_corner by L {vals} ratio 32/4 {r}")
    h0["pass"] = bool(all(h0["sup"][str(e) + "_pass"] for e in SUP if h0["sup"][str(e) + "_ratio"] is not None))
    h0["control_pass"] = bool(all((h0["rms"][str(e) + "_ratio_32_over_4"] or 0) >= 1.5 for e in RMS_PRIMARY))

    # ---- calibration under sup ----
    def S_par(name):
        w = data[name]["w"]
        a_par, _ = b3.frenet(w)
        return float(np.trapezoid(np.sqrt(np.abs(a_par)) * (~data[name]["cmask"]), dx=w.times[1] - w.times[0]))

    m_par_est = {}
    for e in SUP:
        Nt, Nc = data["tangential_probe"]["N_sup"][str(e)], data["circle"]["N_sup"][str(e)]
        if Nt is None or Nc is None:
            m_par_est[str(e)] = None
            continue
        Nt_s = Nt - data["tangential_probe"]["N_event"]
        Nc_s = Nc - data["circle"]["N_event"]
        St = S_par("tangential_probe")

        def resid(log_m):
            m = np.exp(log_m)
            A = Nt_s / (m ** 0.25 * St)
            Sc, _ = b3.smooth_integral(data["circle"]["w"], m, data["circle"]["cmask"])
            return A * Sc - Nc_s
        lo, hi = np.log(1e-4), np.log(10.0)
        m_par_est[str(e)] = None if resid(lo) * resid(hi) > 0 else float(np.exp(brentq(resid, lo, hi)))
        print(f"  m_par at {e*1000:.2f} mm: {m_par_est[str(e)]}")
    valid = [v for v in m_par_est.values() if v is not None]
    m_par = float(np.exp(np.mean(np.log(valid)))) if valid else float("nan")
    print(f"frozen m_par = {m_par:.4f}")
    calib = {}
    for e in SUP:
        Nc, Nk = data["circle"]["N_sup"][str(e)], data["corner_L8"]["N_sup"][str(e)]
        if Nc is None or Nk is None or not np.isfinite(m_par):
            continue
        Sc, _ = b3.smooth_integral(data["circle"]["w"], m_par, data["circle"]["cmask"])
        A = (Nc - data["circle"]["N_event"]) / Sc
        Sk, _ = b3.smooth_integral(data["corner_L8"]["w"], m_par, data["corner_L8"]["cmask"])
        B = (Nk - data["corner_L8"]["N_event"] - A * Sk) / data["corner_L8"]["K"]
        calib[str(e)] = {"A": float(A), "B": float(B)}
        print(f"  eps {e*1000:.2f} mm: A={A:.2f} B={B:.2f}")

    # ---- holdout tests ----
    tests = {"H0": h0, "H1": {}, "H2": {}, "H4": {}, "predictions": {}}
    for e in SUP:
        if str(e) not in calib:
            continue
        A, B = calib[str(e)]["A"], calib[str(e)]["B"]
        rows = []
        for name in HOLDOUT:
            d = data[name]
            Nobs = d["N_sup"][str(e)]
            if Nobs is None:
                rows = None
                break
            Cs, _ = b3.smooth_integral(d["w"], m_par, d["cmask"])
            Nhat = A * Cs + B * d["K"] + d["N_event"]
            rows.append({"name": name, "N": Nobs, "N_hat": float(Nhat), "C_smooth": Cs, "K": d["K"], "N_event": d["N_event"],
                         "turning": d["turning"], "rel_resid": float(abs(Nobs - Nhat) / Nobs)})
        tests["predictions"][str(e)] = rows
        if rows is None:
            continue
        Nobs = np.array([r["N"] for r in rows], float)
        Nhat = np.array([r["N_hat"] for r in rows])
        turn = np.array([r["turning"] for r in rows])
        sp, st = spearmanr(Nhat, Nobs), spearmanr(turn, Nobs)
        r2 = float(1 - ((Nobs - Nhat) ** 2).sum() / ((Nobs - Nobs.mean()) ** 2).sum())
        tests["H1"][str(e)] = {"rho_model": float(sp.correlation), "p_model": float(sp.pvalue), "rho_turning": float(st.correlation),
                               "R2": r2, "pass": bool(sp.correlation > 0.8 and sp.correlation > st.correlation)}
        zz = next(r for r in rows if r["name"] == "zigzag")["rel_resid"]
        ss = next(r for r in rows if r["name"] == "stop_start")["rel_resid"]
        tests["H2"][str(e)] = {"zigzag": zz, "stop_start": ss, "pass": bool(zz <= 0.35 and ss <= 0.30)}
        print(f"eps {e*1000:.2f} mm: rho model {sp.correlation:.3f} turning {st.correlation:.3f} R2 {r2:.3f}; "
              + "; ".join(f"{r['name']} N={r['N']} N_hat={r['N_hat']:.0f}" for r in rows))
    # H4 at 19.35 mm
    for name in HOLDOUT:
        d = data[name]
        idx = d["IDX_sup"][str(H4_EPS)]
        if idx is None:
            tests["H4"][name] = None
            continue
        w = d["w"]
        edges = np.linspace(0, w.t_walk, N_BINS + 1)
        tv = w.times[idx]
        tv = tv[(tv > 0) & (tv < w.t_walk)]
        dens = np.histogram(tv, bins=edges)[0] / np.diff(edges)
        _, pred_dens = b3.smooth_integral(w, m_par, np.zeros(len(w.times), dtype=bool))
        moving = w.speed > b2.STOP_SPEED
        bp, bc, bs = [], [], []
        for k in range(N_BINS):
            sel = (w.times >= edges[k]) & (w.times < edges[k + 1])
            bp.append(float(pred_dens[sel].mean()))
            bc.append(bool(d["cmask"][sel].any()))
            bs.append(bool((~moving[sel]).any()))
        bp, bc, bs = np.array(bp), np.array(bc), np.array(bs)
        clean = ~bc & ~bs
        rho = float(spearmanr(dens[clean], bp[clean]).correlation) if clean.sum() >= 6 and np.std(bp[clean]) > 1e-9 else None
        ratio = float(dens[clean].sum() / max(bp[clean].sum(), 1e-9)) if clean.any() else None
        excess = [bool(dens[k] > ratio * bp[k]) for k in range(N_BINS) if bc[k]] if (bc.any() and ratio is not None) else None
        tests["H4"][name] = {"rho_clean": rho, "n_clean": int(clean.sum()), "corner_excess": excess}
    ex = [x for v in tests["H4"].values() if isinstance(v, dict) and v.get("corner_excess") for x in v["corner_excess"]]
    tests["H4"]["corner_excess_fraction"] = float(np.mean(ex)) if ex else None
    tests["H4"]["pass"] = bool(tests["H4"]["corner_excess_fraction"] is not None and tests["H4"]["corner_excess_fraction"] >= 0.75)

    report = {"sup_thresholds": SUP, "m_par": m_par, "m_par_per_threshold": m_par_est, "calibration": calib, "tests": tests,
              "per_trajectory": {n: {"N_sup": d["N_sup"], "N_rms": d["N_rms"], "N_event": d["N_event"], "K": d["K"], "turning": d["turning"],
                                     "curve": [{k: v for k, v in r.items() if k != "idx"} for r in d["rows"]]} for n, d in data.items()}}
    (out / "b4.json").write_text(json.dumps(report, indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    write_md(report, out / "b4.md")
    try:
        make_figure(report, out / "b4.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(json.dumps({"H0": {"pass": h0["pass"], "control": h0["control_pass"]}, "H1": tests["H1"], "H2": tests["H2"], "H4": tests["H4"]["corner_excess_fraction"]}, indent=2, default=str))
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    t = r["tests"]
    L = ["# Math Track B4 results: corner law under the local supremum", "", "Preregistration: `docs/math-track-b4-prereg.md`.", "",
         "## H0 transfer invariance (sup score; RMS on the same runs as the dilution control)", "",
         "| threshold | N_corner L=4 | L=8 | L=16 | L=32 | max/min | pass |", "|---|---|---|---|---|---|---|"]
    for e in r["sup_thresholds"]:
        v = t["H0"]["sup"][str(e)]
        ratio = t["H0"]["sup"][str(e) + "_ratio"]
        L.append(f"| sup {e*1000:.2f} mm | {v[4]} | {v[8]} | {v[16]} | {v[32]} | {'-' if ratio is None else round(ratio, 2)} | {t['H0']['sup'][str(e) + '_pass']} |")
    for e in RMS:
        v = t["H0"]["rms"][str(e)]
        ratio = t["H0"]["rms"][str(e) + "_ratio_32_over_4"]
        L.append(f"| rms {e*1000:.2f} mm (control) | {v[4]} | {v[8]} | {v[16]} | {v[32]} | 32/4 = {'-' if ratio is None else round(ratio, 2)} | |")
    L += ["", f"H0 pass: {t['H0']['pass']}; dilution control (RMS ratio >= 1.5 at primaries): {t['H0']['control_pass']}.", "",
          f"## Calibration: m_par = {r['m_par']:.4f} (per threshold: " + ", ".join(f"{float(k)*1000:.2f} mm: {v if v is None else round(v, 4)}" for k, v in r["m_par_per_threshold"].items()) + ")", "",
          "| eps (mm) | A | B |", "|---|---|---|"]
    for k, v in r["calibration"].items():
        L.append(f"| {float(k)*1000:.2f} | {v['A']:.2f} | {v['B']:.2f} |")
    L += ["", "## Per trajectory (N at sup thresholds, then RMS thresholds)", "", "| trajectory | N_event | K | turning | " + " | ".join(f"sup {e*1000:.1f}" for e in r["sup_thresholds"]) + " | " + " | ".join(f"rms {e*1000:.2f}" for e in RMS) + " |",
          "|---|---|---|---|" + "---|" * (len(r["sup_thresholds"]) + len(RMS))]
    for n, d in r["per_trajectory"].items():
        L.append(f"| {n} | {d['N_event']} | {d['K']:.2f} | {d['turning']:.2f} | " + " | ".join(str(d["N_sup"][str(e)]) for e in r["sup_thresholds"]) + " | " + " | ".join(str(d["N_rms"][str(e)]) for e in RMS) + " |")
    L += ["", "## Holdout predictions and tests", ""]
    for k, rows in t["predictions"].items():
        if rows is None:
            L.append(f"eps {float(k)*1000:.2f} mm: not evaluable for all six.")
            continue
        h1, h2 = t["H1"][k], t["H2"][k]
        L += [f"### sup eps = {float(k)*1000:.2f} mm: rho model {h1['rho_model']:.3f} (p {h1['p_model']:.3f}), turning {h1['rho_turning']:.3f}, R^2 {h1['R2']:.3f}, H1 pass {h1['pass']}; zigzag resid {h2['zigzag']:.2f}, stop_start resid {h2['stop_start']:.2f}, H2 pass {h2['pass']}", "",
              "| trajectory | N | N_hat | C_smooth | K | N_event | rel resid |", "|---|---|---|---|---|---|---|"]
        for x in rows:
            L.append(f"| {x['name']} | {x['N']} | {x['N_hat']:.0f} | {x['C_smooth']:.2f} | {x['K']:.2f} | {x['N_event']} | {x['rel_resid']:.2f} |")
        L.append("")
    h4 = t["H4"]
    L += [f"## H4 at 19.35 mm: corner-bin excess fraction = {h4['corner_excess_fraction']}, pass {h4['pass']}", "", "| trajectory | rho clean | clean bins | corner excess |", "|---|---|---|---|"]
    for n in HOLDOUT:
        v = h4.get(n)
        L.append(f"| {n} | {'-' if not v or v['rho_clean'] is None else round(v['rho_clean'], 2)} | {'-' if not v else v['n_clean']} | {'-' if not v else v['corner_excess']} |")
    path.write_text("\n".join(L) + "\n")


def make_figure(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = r["tests"]
    preds = {k: v for k, v in t["predictions"].items() if v}
    fig, axes = plt.subplots(1, 1 + len(preds), figsize=(5 * (1 + len(preds)), 4.5), squeeze=False)
    ax = axes[0][0]
    for e, col in zip(r["sup_thresholds"], ("C0", "C1", "C2", "C3")):
        v = t["H0"]["sup"][str(e)]
        Ls = [L for L in LENGTHS if v[L] is not None]
        ax.plot(Ls, [v[L] for L in Ls], "o-", color=col, label=f"sup {e*1000:.1f} mm")
    for e, col in zip(RMS_PRIMARY, ("C4", "C5")):
        v = t["H0"]["rms"][str(e)]
        Ls = [L for L in LENGTHS if v[L] is not None]
        ax.plot(Ls, [v[L] for L in Ls], "s--", color=col, label=f"rms {e*1000:.2f} mm (control)")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("surrounding straight path length L (m)")
    ax.set_ylabel("vertices attributed to the corner")
    ax.set_title("H0: transfer invariance")
    ax.legend(fontsize=7)
    for ax, (k, rows) in zip(axes[0][1:], preds.items()):
        N = [x["N"] for x in rows]
        Nh = [x["N_hat"] for x in rows]
        ax.scatter(Nh, N)
        for x in rows:
            ax.annotate(x["name"], (x["N_hat"], x["N"]), fontsize=8, xytext=(3, 3), textcoords="offset points")
        m = max(max(N), max(Nh)) * 1.1
        ax.plot([0, m], [0, m], "k--", lw=0.8)
        ax.set_xlabel("predicted N_hat")
        ax.set_ylabel("measured N (sup score)")
        h1 = t["H1"][k]
        ax.set_title(f"sup eps {float(k)*1000:.1f} mm: rho {h1['rho_model']:.2f} (turning {h1['rho_turning']:.2f})")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
