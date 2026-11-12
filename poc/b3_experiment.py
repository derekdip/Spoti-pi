"""Math Track B3: smooth + singular causal path complexity. Implements docs/math-track-b3-prereg.md.

Usage: python poc/b3_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))

import b2_experiment as b2  # noqa: E402
from holdout import parse_model  # noqa: E402
from reactive.causes import PathToken  # noqa: E402
from reactive.teacher import TeacherParams, stalk_grid  # noqa: E402
from reactive.worldlines import corner_probe, family  # noqa: E402

THRESHOLDS = b2.THRESHOLDS
PRIMARY = b2.PRIMARY
TOLS = np.geomspace(1.0, 0.0001, 64)
THETA_DOT_C = 3.0
N_BINS = 12
H4_EPS = 0.00261
HOLDOUT = ("straight", "s_curve", "stop_start", "slalom", "zigzag", "wandering")


def frenet(w):
    """Tangential and normal acceleration magnitudes from the analytic worldline."""
    a_par = np.gradient(w.speed, w.times)  # v' (analytic v sampled at 200 Hz; gradient of exact samples)
    a_perp = w.speed * w.heading_rate
    return a_par, a_perp


def corners(w):
    """Maximal intervals with |theta'| > THETA_DOT_C: list of (i0, i1, Theta)."""
    fast = np.abs(w.heading_rate) > THETA_DOT_C
    out = []
    i = 0
    n = len(fast)
    while i < n:
        if fast[i]:
            j = i
            while j < n and fast[j]:
                j += 1
            dt = w.times[1] - w.times[0]
            theta = float(np.trapezoid(np.abs(w.heading_rate[i:j]), dx=dt))
            out.append((i, j, theta))
            i = j
        else:
            i += 1
    return out


def smooth_integral(w, m_par, corner_mask):
    a_par, a_perp = frenet(w)
    dens = (m_par * a_par ** 2 + a_perp ** 2) ** 0.25
    dens = np.where(corner_mask, 0.0, dens)
    return float(np.trapezoid(dens, dx=w.times[1] - w.times[0])), dens


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    two = parse_model(json.loads((out / "gpu_sweep.json").read_text())["terms"]["wake + presence"]["description"])
    tp = TeacherParams()
    pos = stalk_grid(tp)
    times = np.arange(int(tp.duration * b2.FPS) + 1) / b2.FPS
    cons = b2.Consumer(two, pos, times)
    worldlines = family() + [corner_probe()]

    data = {}
    for w in worldlines:
        ref, g = cons.field(w, PathToken(w.points, w.times))
        mask = g.path_dperp < b2.LOCAL_R
        forced = b2.event_vertices(w.speed)
        rows = []
        for tol in TOLS:
            idx = b2.weighted_time_dp(w.points, w.times, np.ones(len(w.times)), tol, forced)
            pred, _ = cons.field(w, PathToken(w.points[idx], w.times[idx]))
            e, s = b2.rms_error(pred, ref, mask)
            rows.append({"tol": float(tol), "N": int(len(idx)), "err": e, "idx": idx})
        N, IDX = {}, {}
        for eps in THRESHOLDS:
            N[str(eps)], IDX[str(eps)] = b2.n_at(rows, eps)
        cs = corners(w)
        cmask = np.zeros(len(w.times), dtype=bool)
        for i0, i1, _ in cs:
            cmask[i0:i1] = True
        K = float(sum(2 * np.sin(abs(th) / 2) for _, _, th in cs))
        dt = w.times[1] - w.times[0]
        turning = float(np.trapezoid(np.abs(w.heading_rate) * (w.speed > 1e-6), dx=dt))
        c_iso = float(np.trapezoid(np.sqrt(np.linalg.norm(w.accel, axis=1)), dx=dt))
        data[w.name] = {"w": w, "N": N, "IDX": IDX, "N_event": int(len(forced)), "corners": cs, "cmask": cmask,
                        "K": K, "turning": turning, "C_iso": c_iso, "curve": [{k: v for k, v in r.items() if k != "idx"} for r in rows]}
        print(f"{w.name:13s} N(eps)={[N[str(e)] for e in THRESHOLDS]} N_event={len(forced)} corners={[(round(w.times[i0],2), round(th,2)) for i0,_,th in cs]} K={K:.2f} turning={turning:.2f}")

    # ---- calibration on probes ----
    def S_par(name):
        w = data[name]["w"]
        a_par, _ = frenet(w)
        return float(np.trapezoid(np.sqrt(np.abs(a_par)) * (~data[name]["cmask"]), dx=w.times[1] - w.times[0]))

    m_par_est = {}
    for eps in THRESHOLDS:
        Nt = data["two_speed"]["N"][str(eps)]
        Nc = data["circle"]["N"][str(eps)]
        if Nt is None or Nc is None:
            continue
        Nt_star = Nt - data["two_speed"]["N_event"]
        Nc_star = Nc - data["circle"]["N_event"]
        St = S_par("two_speed")

        def resid(log_m):
            m = np.exp(log_m)
            A = Nt_star / (m ** 0.25 * St)
            Sc, _ = smooth_integral(data["circle"]["w"], m, data["circle"]["cmask"])
            return A * Sc - Nc_star

        lo, hi = np.log(1e-4), np.log(10.0)
        if resid(lo) * resid(hi) > 0:
            m_par_est[str(eps)] = None
            print(f"  eps {eps*1000:.2f} mm: no root for m_par (resid {resid(lo):.1f}, {resid(hi):.1f})")
            continue
        m = float(np.exp(brentq(resid, lo, hi)))
        m_par_est[str(eps)] = m
        print(f"  eps {eps*1000:.2f} mm: m_par estimate {m:.4f}")
    valid = [v for v in m_par_est.values() if v is not None]
    m_par = float(np.exp(np.mean(np.log(valid))))
    print(f"frozen m_par = {m_par:.4f} (geometric mean of {len(valid)} thresholds)")

    calib = {}
    for eps in THRESHOLDS:
        Nc = data["circle"]["N"][str(eps)]
        Nk = data["corner_probe"]["N"][str(eps)]
        if Nc is None or Nk is None:
            continue
        Sc, _ = smooth_integral(data["circle"]["w"], m_par, data["circle"]["cmask"])
        A = (Nc - data["circle"]["N_event"]) / Sc
        Sk, _ = smooth_integral(data["corner_probe"]["w"], m_par, data["corner_probe"]["cmask"])
        B = (Nk - data["corner_probe"]["N_event"] - A * Sk) / data["corner_probe"]["K"]
        calib[str(eps)] = {"A": float(A), "B": float(B)}
        print(f"  eps {eps*1000:.2f} mm: A={A:.2f} B={B:.2f}")

    # ---- holdout predictions and tests ----
    b2_fit = json.loads((out / "b2.json").read_text())["analysis"]["H2"]
    b2_res = json.loads((out / "b2.json").read_text())["results"]
    tests = {"H1": {}, "H2": {}, "H4": {}, "predictions": {}}
    for eps in THRESHOLDS:
        if str(eps) not in calib:
            continue
        A, B = calib[str(eps)]["A"], calib[str(eps)]["B"]
        rows = []
        for name in HOLDOUT:
            d = data[name]
            Nobs = d["N"][str(eps)]
            if Nobs is None:
                rows = None
                break
            Cs, _ = smooth_integral(d["w"], m_par, d["cmask"])
            Nhat = A * Cs + B * d["K"] + d["N_event"]
            rows.append({"name": name, "N": Nobs, "N_hat": float(Nhat), "C_smooth": Cs, "K": d["K"], "N_event": d["N_event"],
                         "turning": d["turning"], "C_iso": d["C_iso"], "rel_resid": float(abs(Nobs - Nhat) / Nobs)})
        if rows is None:
            tests["predictions"][str(eps)] = None
            continue
        tests["predictions"][str(eps)] = rows
        Nobs = np.array([r["N"] for r in rows], float)
        Nhat = np.array([r["N_hat"] for r in rows])
        turn = np.array([r["turning"] for r in rows])
        ciso = np.array([r["C_iso"] for r in rows])
        sp = spearmanr(Nhat, Nobs)
        st = spearmanr(turn, Nobs)
        si = spearmanr(ciso, Nobs)
        r2 = float(1 - ((Nobs - Nhat) ** 2).sum() / ((Nobs - Nobs.mean()) ** 2).sum())
        tests["H1"][str(eps)] = {"rho_model": float(sp.correlation), "p_model": float(sp.pvalue), "rho_turning": float(st.correlation),
                                 "rho_iso_C_G": float(si.correlation), "R2_model": r2,
                                 "pass": bool(sp.correlation > 0.8 and sp.correlation > st.correlation)}
        # H2: residual repair for zigzag and stop_start vs B2 linear fit
        h2 = {}
        if str(eps) in b2_fit:
            a_b2, b_b2 = b2_fit[str(eps)]["a"], b2_fit[str(eps)]["b"]
            for name in ("zigzag", "stop_start"):
                r = next(x for x in rows if x["name"] == name)
                b2_pred = a_b2 + b_b2 * b2_res[name]["C_analytic"]
                b2_rel = abs(r["N"] - b2_pred) / r["N"]
                h2[name] = {"B2_rel_resid": float(b2_rel), "B3_rel_resid": r["rel_resid"], "shrinks": bool(r["rel_resid"] < b2_rel)}
            h2["pass"] = bool(all(h2[n]["shrinks"] for n in ("zigzag", "stop_start")))
        tests["H2"][str(eps)] = h2
        print(f"eps {eps*1000:.2f} mm: rho model {sp.correlation:.3f} (p {sp.pvalue:.3f}), turning {st.correlation:.3f}, iso C_G {si.correlation:.3f}, R2 {r2:.3f}; "
              + "; ".join(f"{r['name']} N={r['N']} N_hat={r['N_hat']:.0f}" for r in rows))

    # H4: local density at 2.61 mm
    for name in HOLDOUT:
        d = data[name]
        idx = d["IDX"][str(H4_EPS)]
        if idx is None:
            tests["H4"][name] = None
            continue
        w = d["w"]
        edges = np.linspace(0, w.t_walk, N_BINS + 1)
        tv = w.times[idx]
        tv = tv[(tv > 0) & (tv < w.t_walk)]
        dens = np.histogram(tv, bins=edges)[0] / np.diff(edges)
        _, pred_dens = smooth_integral(w, m_par, np.zeros(len(w.times), dtype=bool))
        bins_pred, bins_corner, bins_stop = [], [], []
        moving = w.speed > b2.STOP_SPEED
        for k in range(N_BINS):
            sel = (w.times >= edges[k]) & (w.times < edges[k + 1])
            bins_pred.append(float(pred_dens[sel].mean()))
            bins_corner.append(bool(d["cmask"][sel].any()))
            bins_stop.append(bool((~moving[sel]).any()))
        bins_pred, bins_corner, bins_stop = np.array(bins_pred), np.array(bins_corner), np.array(bins_stop)
        clean = ~bins_corner & ~bins_stop
        rho = None
        if clean.sum() >= 6 and np.std(bins_pred[clean]) > 1e-9:
            rho = float(spearmanr(dens[clean], bins_pred[clean]).correlation)
        ratio = float(dens[clean].sum() / max(bins_pred[clean].sum(), 1e-9)) if clean.any() else None
        excess = None
        if bins_corner.any() and ratio is not None:
            excess = [bool(dens[k] > ratio * bins_pred[k]) for k in range(N_BINS) if bins_corner[k]]
        tests["H4"][name] = {"rho_clean": rho, "n_clean_bins": int(clean.sum()), "corner_bins_excess": excess,
                             "density": dens.tolist(), "pred": bins_pred.tolist(), "corner_bins": bins_corner.tolist()}
    rhos = [v["rho_clean"] for v in tests["H4"].values() if v and v["rho_clean"] is not None]
    tests["H4"]["median_rho_clean"] = float(np.median(rhos)) if rhos else None
    ex = [e for v in tests["H4"].values() if isinstance(v, dict) and v.get("corner_bins_excess") for e in v["corner_bins_excess"]]
    tests["H4"]["corner_excess_fraction"] = float(np.mean(ex)) if ex else None

    report = {"m_par": m_par, "m_par_per_threshold": m_par_est, "calibration": calib, "tests": tests,
              "per_trajectory": {n: {"N": d["N"], "N_event": d["N_event"], "K": d["K"], "turning": d["turning"], "C_iso": d["C_iso"],
                                     "corners": [(float(d["w"].times[i0]), float(d["w"].times[i1 - 1]), th) for i0, i1, th in d["corners"]],
                                     "curve": d["curve"]} for n, d in data.items()}}
    (out / "b3.json").write_text(json.dumps(report, indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    write_md(report, out / "b3.md")
    try:
        make_figure(report, out / "b3.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(json.dumps({"H1": tests["H1"], "H2": tests["H2"], "H4_median": tests["H4"]["median_rho_clean"], "corner_excess": tests["H4"]["corner_excess_fraction"]}, indent=2, default=str))
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    t = r["tests"]
    L = ["# Math Track B3 results: smooth + singular causal path complexity", "",
         "Preregistration: `docs/math-track-b3-prereg.md`.", "",
         f"Frozen m_par = {r['m_par']:.4f} (per-threshold estimates: " + ", ".join(f"{float(k)*1000:.2f} mm: {v if v is None else round(v, 4)}" for k, v in r["m_par_per_threshold"].items()) + ").", "",
         "| eps (mm) | A | B |", "|---|---|---|"]
    for k, v in r["calibration"].items():
        L.append(f"| {float(k)*1000:.2f} | {v['A']:.2f} | {v['B']:.2f} |")
    L += ["", "## Per trajectory", "", "| trajectory | N_event | K | turning | iso C_G | " + " | ".join(f"N({e*1000:.2f})" for e in THRESHOLDS) + " | corners (t, Theta) |", "|---|---|---|---|---|" + "---|" * len(THRESHOLDS) + "---|"]
    for n, d in r["per_trajectory"].items():
        L.append(f"| {n} | {d['N_event']} | {d['K']:.2f} | {d['turning']:.2f} | {d['C_iso']:.2f} | " + " | ".join(str(d["N"][str(e)]) for e in THRESHOLDS)
                 + " | " + ", ".join(f"({a:.2f}s, {th:.2f})" for a, _, th in d["corners"]) + " |")
    L += ["", "## Holdout predictions", ""]
    for k, rows in t["predictions"].items():
        if rows is None:
            L.append(f"eps {float(k)*1000:.2f} mm: not evaluable for all six.")
            continue
        L += [f"### eps = {float(k)*1000:.2f} mm", "", "| trajectory | N | N_hat | C_smooth | K | N_event | rel resid |", "|---|---|---|---|---|---|---|"]
        for x in rows:
            L.append(f"| {x['name']} | {x['N']} | {x['N_hat']:.0f} | {x['C_smooth']:.2f} | {x['K']:.2f} | {x['N_event']} | {x['rel_resid']:.2f} |")
        L.append("")
    L += ["## B3-H1 ranking (bar: rho > 0.8 and rho > turning's)", "", "| eps (mm) | rho model | p | rho turning | rho iso C_G | R^2 | pass |", "|---|---|---|---|---|---|---|"]
    for k, v in t["H1"].items():
        L.append(f"| {float(k)*1000:.2f} | {v['rho_model']:.3f} | {v['p_model']:.3f} | {v['rho_turning']:.3f} | {v['rho_iso_C_G']:.3f} | {v['R2_model']:.3f} | {v['pass']} |")
    L += ["", "## B3-H2 residual repair (relative residual, B2 linear fit vs B3 calibrated law)", "", "| eps (mm) | zigzag B2 | zigzag B3 | stop_start B2 | stop_start B3 | pass |", "|---|---|---|---|---|---|"]
    for k, v in t["H2"].items():
        if "zigzag" in v:
            L.append(f"| {float(k)*1000:.2f} | {v['zigzag']['B2_rel_resid']:.2f} | {v['zigzag']['B3_rel_resid']:.2f} | {v['stop_start']['B2_rel_resid']:.2f} | {v['stop_start']['B3_rel_resid']:.2f} | {v['pass']} |")
    h4 = t["H4"]
    L += ["", f"## B3-H4 local density: median Spearman on clean bins = {h4['median_rho_clean']} (bar 0.6); fraction of corner bins with excess density = {h4['corner_excess_fraction']}", "",
          "| trajectory | rho clean | clean bins | corner bins with excess |", "|---|---|---|---|"]
    for n in HOLDOUT:
        v = h4.get(n)
        if not v:
            L.append(f"| {n} | - | - | - |")
            continue
        L.append(f"| {n} | {'-' if v['rho_clean'] is None else round(v['rho_clean'], 2)} | {v['n_clean_bins']} | {v['corner_bins_excess']} |")
    path.write_text("\n".join(L) + "\n")


def make_figure(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    preds = {k: v for k, v in r["tests"]["predictions"].items() if v}
    fig, axes = plt.subplots(1, len(preds), figsize=(5 * len(preds), 4.5), squeeze=False)
    for ax, (k, rows) in zip(axes[0], preds.items()):
        N = [x["N"] for x in rows]
        Nh = [x["N_hat"] for x in rows]
        ax.scatter(Nh, N)
        for x in rows:
            ax.annotate(x["name"], (x["N_hat"], x["N"]), fontsize=8, xytext=(3, 3), textcoords="offset points")
        m = max(max(N), max(Nh)) * 1.1
        ax.plot([0, m], [0, m], "k--", lw=0.8)
        ax.set_xlabel("predicted N_hat (probe-calibrated)")
        ax.set_ylabel("measured N")
        h1 = r["tests"]["H1"][k]
        ax.set_title(f"eps = {float(k)*1000:.2f} mm: rho {h1['rho_model']:.2f} (turning {h1['rho_turning']:.2f})")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
