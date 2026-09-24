"""Math Track W4: event-coordinate conditioning. Implements docs/math-track-w4-prereg.md.

Usage: python poc/w4_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, minimize_scalar

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reactive.metrics import rel_rmse  # noqa: E402
from w1_experiment import CENTRE, NL  # noqa: E402
from water.teacher import WaterParams, run_splash  # noqa: E402
from water.tokens import KERNELS  # noqa: E402

AMPS = (1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0)
NEW = (3.0, 6.0, 10.0)
CAL = 4.0
DT = 1.0 / 240.0
DT_GRID = np.arange(-0.200, 0.0201, 0.002)
G_GRID = np.arange(8.0, 14.001, 0.05)
PARAMS = ["A", "lam", "m", "n", "g_eff", "phi", "v_max", "k_cut"]
SHAPE = ["lam", "g_eff", "v_max", "k_cut", "m", "n", "phi"]
W3COND = ["lam", "g_eff", "v_max", "k_cut"]
chirp = KERNELS["chirp"][0]


def K_field(p: dict, pts: np.ndarray, times: np.ndarray, dt: float = 0.0) -> np.ndarray:
    r = np.linalg.norm(pts - np.asarray(CENTRE)[None, :], axis=1)[None, :]
    return np.stack([chirp(r, np.array([[t - dt]]), p)[0] for t in times])


def ls_gain(target: np.ndarray, K: np.ndarray) -> float:
    return float((target * K).sum() / max((K * K).sum(), 1e-30))


def profiled(target: np.ndarray, K: np.ndarray) -> tuple[float, float]:
    s = ls_gain(target, K)
    return rel_rmse(s * K, target), s


def explained(R: np.ndarray, basis: list[np.ndarray]) -> tuple[float, np.ndarray]:
    B = np.stack([b.ravel() for b in basis], 1)
    coef, *_ = np.linalg.lstsq(B, R.ravel(), rcond=None)
    fit = B @ coef
    return float(1.0 - ((R.ravel() - fit) ** 2).sum() / (R.ravel() ** 2).sum()), coef


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    theta0 = json.loads((out / "w1.json").read_text())["token"]["params"]
    g0 = theta0["g_eff"]

    p = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **NL)
    xs = np.arange(p.n) * p.dx
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    times_all = np.arange(int(p.duration * p.fps) + 1) / p.fps
    ok = times_all >= 0.15
    r = np.sqrt((X - CENTRE[0]) ** 2 + (Y - CENTRE[1]) ** 2)
    sub = (r < 1.6) & (np.arange(p.n)[:, None] % 3 == 0) & (np.arange(p.n)[None, :] % 3 == 0)
    ev = r < 2.0
    fit_pts, eval_pts = np.stack([X[sub], Y[sub]], -1), np.stack([X[ev], Y[ev]], -1)
    fit_frames = np.flatnonzero(ok)[::2]
    t_fit, t_eval = times_all[fit_frames], times_all[ok]

    # base token and tangents on the evaluation set (theta_0, A = 1)
    K0_eval = K_field(theta0, eval_pts, t_eval)
    K0_fit = K_field(theta0, fit_pts, t_fit)
    dK_eval = (K_field(theta0, eval_pts, t_eval + DT) - K_field(theta0, eval_pts, t_eval - DT)) / (2 * DT)
    tangents = {}
    for name in PARAMS:
        h = 1e-3 * abs(theta0[name]) if theta0[name] != 0 else 1e-4
        pp, pm = dict(theta0), dict(theta0)
        pp[name] += h
        pm[name] -= h
        tangents[name] = (K_field(pp, eval_pts, t_eval) - K_field(pm, eval_pts, t_eval)) / (2 * h)
    unit = {"t": dK_eval / np.linalg.norm(dK_eval)}
    for name in PARAMS:
        unit[name] = tangents[name] / np.linalg.norm(tangents[name])
    keys = ["t"] + PARAMS
    gram = {a: {b: float(abs((unit[a] * unit[b]).sum())) for b in keys} for a in keys}
    chi = {name: gram["t"][name] for name in PARAMS}
    print("tangent coherence with time: " + ", ".join(f"{k} {v:.3f}" for k, v in chi.items()))
    t1 = bool(chi["g_eff"] > 0.5 and chi["g_eff"] >= 2 * max(chi[k] for k in ("lam", "v_max", "k_cut")))

    cells: dict[float, dict] = {}
    dropped = []
    for A in AMPS:
        eta = run_splash(p, *CENTRE, v0=A, sigma=0.03).eta.astype(float)
        if not np.isfinite(eta).all():
            dropped.append(A)
            print(f"A={A}: non-finite teacher field, dropped")
            continue
        ref, tgt = eta[fit_frames][:, sub], eta[ok][:, ev]
        del eta
        c: dict = {}
        # M_gain
        E_gain_fit, s_gain = profiled(ref, K0_fit)
        c["E_gain"] = rel_rmse(s_gain * K0_eval, tgt)
        c["s_gain"] = s_gain
        # H1: residual after the least-squares gain on the evaluation set, before any shift is fitted
        s_ev = ls_gain(tgt, K0_eval)
        R = tgt - s_ev * K0_eval
        c["P_t"] = float((R * dK_eval).sum() ** 2 / ((R ** 2).sum() * (dK_eval ** 2).sum()))
        # ordered tangent decomposition (reported)
        share_coord = c["P_t"]
        R1 = R - (R * dK_eval).sum() / (dK_eval ** 2).sum() * dK_eval
        frac_shape, _ = explained(R1, [tangents[k] for k in SHAPE])
        share_shape = frac_shape * (R1 ** 2).sum() / (R ** 2).sum()
        joint, _ = explained(R, [dK_eval] + [tangents[k] for k in SHAPE])
        c["decomp"] = {"coordinate": share_coord, "unary_shape_after": float(share_shape), "rest": float(1 - share_coord - share_shape), "joint_span": joint}
        # per-frame linearised shift b(tau) (reported)
        b = []
        for f in range(R.shape[0]):
            B = np.stack([K0_eval[f], dK_eval[f]], 1)
            coef, *_ = np.linalg.lstsq(B, R[f], rcond=None)
            b.append(-coef[1] / max(s_ev, 1e-9))  # r ~ a K - dt s dK/dt  =>  dt = -coef / s
        b = np.array(b)
        n3 = len(b) // 3
        slope = np.polyfit(t_eval, b, 1)[0]
        c["drift"] = {"dt_early_ms": float(np.median(b[:n3]) * 1e3), "dt_late_ms": float(np.median(b[-n3:]) * 1e3), "slope_ms_per_s": float(slope * 1e3), "b_ms": (b * 1e3).round(2).tolist()}
        # M_phase: grid then bounded refinement, gain profiled
        losses = [profiled(ref, K_field(theta0, fit_pts, t_fit, dt))[0] for dt in DT_GRID]
        i = int(np.argmin(losses))
        lo, hi = DT_GRID[max(i - 1, 0)], DT_GRID[min(i + 1, len(DT_GRID) - 1)]
        res = minimize_scalar(lambda dt: profiled(ref, K_field(theta0, fit_pts, t_fit, dt))[0], bounds=(lo, hi), method="bounded", options={"xatol": 1e-4})
        dt_hat = float(res.x)
        _, s_phase = profiled(ref, K_field(theta0, fit_pts, t_fit, dt_hat))
        c["dt_hat"] = dt_hat
        c["s_phase"] = s_phase
        c["E_phase"] = rel_rmse(s_phase * K_field(theta0, eval_pts, t_eval, dt_hat), tgt)
        c["grid_losses"] = [float(v) for v in losses]
        # M_disp
        def Kg(g, pts, times, dt=0.0):
            pg = dict(theta0)
            pg["g_eff"] = g
            return K_field(pg, pts, times, dt)
        lg = [profiled(ref, Kg(g, fit_pts, t_fit))[0] for g in G_GRID]
        j = int(np.argmin(lg))
        glo, ghi = G_GRID[max(j - 1, 0)], G_GRID[min(j + 1, len(G_GRID) - 1)]
        resg = minimize_scalar(lambda g: profiled(ref, Kg(g, fit_pts, t_fit))[0], bounds=(glo, ghi), method="bounded", options={"xatol": 1e-4})
        g_disp = float(resg.x)
        _, s_disp = profiled(ref, Kg(g_disp, fit_pts, t_fit))
        c["g_disp"] = g_disp
        c["s_disp"] = s_disp
        c["E_disp"] = rel_rmse(s_disp * Kg(g_disp, eval_pts, t_eval), tgt)
        # M_phase+g: Powell from the better of the two 1-D solutions (the other parameter at base)
        def loss2(z):
            return profiled(ref, Kg(z[1], fit_pts, t_fit, z[0]))[0]
        best = None
        for z0 in ((dt_hat, g0), (0.0, g_disp)):
            rr = minimize(loss2, np.array(z0), method="Powell", options={"maxfev": 400, "xtol": 1e-4, "ftol": 1e-6})
            if best is None or rr.fun < best.fun:
                best = rr
        dt2, g2 = float(best.x[0]), float(best.x[1])
        _, s2 = profiled(ref, Kg(g2, fit_pts, t_fit, dt2))
        c["dt_phase_g"], c["g_phase_g"] = dt2, g2
        c["E_phase_g"] = rel_rmse(s2 * Kg(g2, eval_pts, t_eval, dt2), tgt)
        cells[A] = c
        print(f"A={A:g}: E_gain {c['E_gain']:.3f}  E_phase {c['E_phase']:.3f} (dt {dt_hat*1e3:+.1f} ms)  E_disp {c['E_disp']:.3f} (g {g_disp:.2f})  "
              f"E_phase+g {c['E_phase_g']:.3f} (dt {dt2*1e3:+.1f} ms, g {g2:.2f})  P_t {c['P_t']:.3f}  drift early/late {c['drift']['dt_early_ms']:+.0f}/{c['drift']['dt_late_ms']:+.0f} ms")
        cells[A]["_tgt"] = tgt  # kept for the law evaluations below

    E_floor = cells[1.0]["E_gain"] if 1.0 in cells else float("nan")
    # laws calibrated at A = 4 only
    c4 = cells[CAL]
    c_log, c_lin = c4["dt_hat"] / np.log(CAL), c4["dt_hat"] / (CAL - 1)
    s1 = np.log(c4["s_phase"]) / np.log(CAL) - 1.0
    s1_disp = np.log(c4["s_disp"]) / np.log(CAL) - 1.0
    g_slope = (c4["g_disp"] - g0) / np.log(CAL)
    laws = {"log": {}, "lin": {}}
    for A, c in cells.items():
        if A == 1.0:
            continue
        tgt = c["_tgt"]
        for name, dt_law in (("log", c_log * np.log(A)), ("lin", c_lin * (A - 1))):
            E = rel_rmse(A ** (1 + s1) * K_field(theta0, eval_pts, t_eval, dt_law), tgt)
            laws[name][A] = {"dt_ms": dt_law * 1e3, "E": E, "miss_ms": (dt_law - c["dt_hat"]) * 1e3, "E_gap": E - c["E_phase"]}
        pg = dict(theta0)
        pg["g_eff"] = g0 + g_slope * np.log(A)
        c["E_disp_law"] = rel_rmse(A ** (1 + s1_disp) * K_field(pg, eval_pts, t_eval), tgt)
        c["E_phase_law_log"] = laws["log"][A]["E"]
    for c in cells.values():
        c.pop("_tgt", None)

    new = [A for A in NEW if A in cells]
    h1 = bool(8.0 in cells and cells[8.0]["P_t"] > 0.5)
    pt_seq = [cells[A]["P_t"] for A in (3.0, 4.0, 6.0, 8.0, 10.0) if A in cells]
    miss = {name: sum(abs(laws[name][A]["miss_ms"]) for A in new) for name in laws}
    winner = min(miss, key=miss.get)
    h2 = bool(all(abs(laws[winner][A]["miss_ms"]) <= 15.0 for A in new))
    h2_E = bool(all(abs(laws[winner][A]["E_gap"]) <= 0.05 for A in new))
    h3 = bool(all(cells[A]["E_phase"] < cells[A]["E_disp"] for A in new))
    h3_law = bool(all(cells[A]["E_phase_law_log"] < cells[A]["E_disp_law"] for A in new))
    h4_frac = {}
    for A in new:
        den = cells[A]["E_phase"] - E_floor
        h4_frac[A] = 0.0 if den <= 1e-3 else (cells[A]["E_phase"] - cells[A]["E_phase_g"]) / den
    h4 = bool(all(v < 0.10 for v in h4_frac.values()))
    g_after = {A: (cells[A]["g_phase_g"] - g0) / np.log(A) for A in cells if A != 1.0}
    if h1 and h2 and h3 and h4:
        verdict = "coordinate confirmed"
    elif h1 and h3 and not h2:
        verdict = "proxy"
    elif not (h1 and h3):
        verdict = "neither"
    else:
        verdict = "coordinate mechanism, H4 fails"  # H1, H2, H3 hold, H4 fails: not one of the three named outcomes; reported as such
    report = {"E_floor": E_floor, "dropped": dropped, "theta0": theta0, "chi": chi, "gram": gram, "T1": {"pass": t1},
              "cells": {str(A): c for A, c in cells.items()},
              "laws": {"c_log_ms_per_logA": c_log * 1e3, "c_lin_ms_per_unitA": c_lin * 1e3, "s1": s1, "s1_disp": s1_disp, "g_slope_per_logA": g_slope,
                       "per_amplitude": {name: {str(A): v for A, v in d.items()} for name, d in laws.items()}},
              "H1": {"P_t_8": cells[8.0]["P_t"] if 8.0 in cells else None, "P_t_sequence_3_4_6_8_10": pt_seq, "non_decreasing": bool(all(np.diff(pt_seq) >= 0)), "pass": h1},
              "H2": {"miss_sum_ms": miss, "winner": winner, "pass": h2, "error_within_0.05": h2_E},
              "H3": {"pass": h3, "extrapolated_log_law_pass": h3_law},
              "H4": {"fraction": {str(A): v for A, v in h4_frac.items()}, "g_slope_after_timing_per_logA": {str(A): v for A, v in g_after.items()}, "pass": h4},
              "verdict": verdict}
    (out / "w4.json").write_text(json.dumps(report, indent=2, default=float))
    write_md(report, out / "w4.md")
    try:
        plot(report, out / "w4.png")
    except Exception as e:  # noqa: BLE001
        print("plot failed:", e)
    print(json.dumps({k: report[k] for k in ("H1", "H2", "H3", "H4", "T1", "verdict")}, indent=1, default=float))
    print(f"wrote {out / 'w4.md'}")


def write_md(r: dict, path: Path) -> None:
    cells = {float(k): v for k, v in r["cells"].items()}
    A_list = sorted(cells)
    L = ["# Math Track W4 results: event-coordinate conditioning", "", "Preregistration: `docs/math-track-w4-prereg.md`.", "",
         f"Floor (fixed token, A = 1): {r['E_floor']:.3f}. Dropped amplitudes: {r['dropped'] or 'none'}.", "",
         "## Direct fits per amplitude (fit subset; scored on the evaluation set)", "",
         "| A | role | E gain-only | E phase (dt ms) | E disp (g_eff) | E phase+g (dt ms, g_eff) | P_t | drift early/late (ms) |", "|---|---|---|---|---|---|---|---|"]
    role = {1.0: "floor", 2.0: "seen (W3)", 3.0: "new", 4.0: "calibration", 6.0: "new", 8.0: "reproduction", 10.0: "new"}
    for A in A_list:
        c = cells[A]
        L.append(f"| {A:g} | {role.get(A, '')} | {c['E_gain']:.3f} | {c['E_phase']:.3f} ({c['dt_hat']*1e3:+.1f}) | {c['E_disp']:.3f} ({c['g_disp']:.2f}) | "
                 f"{c['E_phase_g']:.3f} ({c['dt_phase_g']*1e3:+.1f}, {c['g_phase_g']:.2f}) | {c['P_t']:.3f} | {c['drift']['dt_early_ms']:+.0f} / {c['drift']['dt_late_ms']:+.0f} |")
    lw = r["laws"]
    L += ["", f"## Delay laws calibrated at A = 4: log {lw['c_log_ms_per_logA']:.1f} ms per unit log A; linear {lw['c_lin_ms_per_unitA']:.1f} ms per unit A; gain exponent 1 + s1 = {1 + lw['s1']:.3f}", "",
          "| A | dt_hat (ms) | log law dt (ms), miss | linear law dt (ms), miss | E phase direct | E log law | E linear law | E disp direct | E disp log-law extrapolated |", "|---|---|---|---|---|---|---|---|---|"]
    for A in A_list:
        if A == 1.0:
            continue
        c = cells[A]
        lg, ln = lw["per_amplitude"]["log"][str(A)], lw["per_amplitude"]["lin"][str(A)]
        L.append(f"| {A:g} | {c['dt_hat']*1e3:+.1f} | {lg['dt_ms']:+.1f}, {lg['miss_ms']:+.1f} | {ln['dt_ms']:+.1f}, {ln['miss_ms']:+.1f} | {c['E_phase']:.3f} | {lg['E']:.3f} | {ln['E']:.3f} | {c['E_disp']:.3f} | {c['E_disp_law']:.3f} |")
    L += ["", "## Tangent coherence with time at theta_0 (T1)", "", "| parameter | chi |", "|---|---|"]
    for k, v in r["chi"].items():
        L.append(f"| {k} | {v:.3f} |")
    L += ["", f"T1 pass {r['T1']['pass']} (chi_g_eff > 0.5 and >= 2x the largest of lam, v_max, k_cut).", "",
          "## Ordered tangent decomposition of the gain-corrected residual (reported)", "", "| A | coordinate (dK/dt) | unary shape, after | rest | joint span |", "|---|---|---|---|---|"]
    for A in A_list:
        d = cells[A]["decomp"]
        L.append(f"| {A:g} | {d['coordinate']:.3f} | {d['unary_shape_after']:.3f} | {d['rest']:.3f} | {d['joint_span']:.3f} |")
    L += ["", f"## H1: P_t(8) = {r['H1']['P_t_8']:.3f} (bar 0.5); sequence over 3,4,6,8,10 = {[round(v, 3) for v in r['H1']['P_t_sequence_3_4_6_8_10']]}, non-decreasing {r['H1']['non_decreasing']}; pass {r['H1']['pass']}",
          "", f"## H2: winner {r['H2']['winner']} (sum of misses ms: { {k: round(v, 1) for k, v in r['H2']['miss_sum_ms'].items()} }); within 15 ms at every new amplitude: {r['H2']['pass']}; error within 0.05: {r['H2']['error_within_0.05']}",
          "", f"## H3: phase beats dispersion at every new amplitude (direct fits): {r['H3']['pass']}; under log-law extrapolation from A = 4: {r['H3']['extrapolated_log_law_pass']}",
          "", f"## H4: fraction recovered by g_eff after timing { {k: round(v, 3) for k, v in r['H4']['fraction'].items()} } (bar 0.10 each); g_eff slope after timing per unit log A { {k: round(v, 3) for k, v in r['H4']['g_slope_after_timing_per_logA'].items()} } (W3: +0.24); pass {r['H4']['pass']}",
          "", f"## Verdict: {r['verdict']}", ""]
    path.write_text("\n".join(L) + "\n")


def plot(r: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cells = {float(k): v for k, v in r["cells"].items()}
    A = np.array(sorted(a for a in cells if a != 1.0))
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    ax = axes[0, 0]
    ax.plot(A, [cells[a]["dt_hat"] * 1e3 for a in A], "ko", label="direct fit dt_hat")
    Ag = np.linspace(1, 10, 50)
    ax.plot(Ag, r["laws"]["c_log_ms_per_logA"] * np.log(Ag), "C0-", label="log law (from A=4)")
    ax.plot(Ag, r["laws"]["c_lin_ms_per_unitA"] * (Ag - 1), "C1-", label="linear law (from A=4)")
    ax.set_xlabel("A"); ax.set_ylabel("onset shift (ms)"); ax.set_title("H2: predicted vs fitted delay"); ax.legend(fontsize=8)
    ax = axes[0, 1]
    for key, lab, st in (("E_gain", "gain only", "C7o-"), ("E_phase", "gain + dt (direct)", "C0o-"), ("E_disp", "gain + g_eff (direct)", "C3s-"), ("E_phase_g", "gain + dt + g_eff", "C2^-"),
                         ("E_phase_law_log", "phase, log law from A=4", "C0o--"), ("E_disp_law", "disp, log law from A=4", "C3s--")):
        ax.plot(A, [cells[a][key] for a in A], st, label=lab, ms=4)
    ax.axhline(r["E_floor"], color="k", ls=":", label="floor")
    ax.set_xlabel("A"); ax.set_ylabel("relative RMS error"); ax.set_title("H3 / H4"); ax.legend(fontsize=7)
    ax = axes[0, 2]
    ax.plot(A, [cells[a]["P_t"] for a in A], "ko-")
    ax.axhline(0.5, color="C3", ls=":"); ax.set_xlabel("A"); ax.set_ylabel("P_t"); ax.set_title("H1: residual projection on dK/dt")
    ax = axes[1, 0]
    names = list(r["chi"].keys())
    ax.bar(range(len(names)), [r["chi"][k] for k in names], color=["C3" if k == "g_eff" else "C0" for k in names])
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names); ax.set_ylabel("|cos| with dK/dt"); ax.set_title("T1: tangent coherence")
    ax = axes[1, 1]
    for a, col in ((6.0, "C1"), (10.0, "C3"), (4.0, "C0")):
        if a in cells:
            b = np.array(cells[a]["drift"]["b_ms"])
            ax.plot(np.linspace(0.15, 4.0, len(b)), b, color=col, lw=0.8, label=f"A={a:g}")
            ax.axhline(cells[a]["dt_hat"] * 1e3, color=col, ls=":")
    ax.set_ylim(-250, 100); ax.set_xlabel("t (s)"); ax.set_ylabel("per-frame linearised shift (ms)"); ax.set_title("drift diagnostic (dotted: global dt_hat)"); ax.legend(fontsize=8)
    ax = axes[1, 2]
    for a in A:
        ax.plot(np.arange(-200, 20.1, 2), cells[a]["grid_losses"], label=f"A={a:g}")
    ax.set_xlabel("dt (ms)"); ax.set_ylabel("fit-subset error (gain profiled)"); ax.set_title("M_phase loss landscape"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
