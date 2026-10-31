"""Math Track W3: amplitude-conditioned unary token vs pair interaction. Implements docs/math-track-w3-prereg.md.

Usage: python poc/w3_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reactive.metrics import rel_rmse  # noqa: E402
from w1_experiment import CENTRE, NL, region  # noqa: E402
from water.teacher import SpectralWater, WaterParams, _record, run_splash  # noqa: E402
from water.tokens import KERNELS  # noqa: E402

AMPS = (0.5, 1.0, 2.0, 4.0, 8.0)
CAL_A = 4.0
HOLD = (0.5, 2.0, 8.0)
SCORED = (2.0, 8.0)
ORDER = ["lam", "g_eff", "v_max", "k_cut"]
PAIR_D = (0.28125, 0.609375)
PAIR_A = (2.0, 8.0)
chirp = KERNELS["chirp"][0]


def token_field(theta0, slopes, gain_s1, A, pts, times, centres):
    """Superposition of conditioned tokens at `centres` with amplitude A each."""
    p = dict(theta0)
    la = np.log(A)
    for k, s in slopes.items():
        p[k] = theta0[k] + s * la
    amp = A ** (1.0 + gain_s1)
    out = np.zeros((len(times), pts.shape[0]))
    for c in centres:
        r = np.linalg.norm(pts - np.asarray(c)[None, :], axis=1)[None, :]
        out += amp * np.stack([chirp(r, np.array([[t]]), p)[0] for t in times])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    w1 = json.loads((out / "w1.json").read_text())
    theta0 = w1["token"]["params"]
    I12 = {float(v["a"]): v["I12_height"] for k, v in w1["Q3"]["cells"].items() if abs(v["D"] - 0.28125) < 1e-6}

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

    singles = {}
    for A in AMPS:
        singles[A] = run_splash(p, *CENTRE, v0=A, sigma=0.03).eta.astype(float)
        print(f"single A={A} done")

    def score_single(slopes, s1, A):
        pred = token_field(theta0, slopes, s1, A, eval_pts, t_eval, [CENTRE])
        return rel_rmse(pred, singles[A][ok][:, ev])

    def fit_model(keys, with_gain):
        """Fit gain slope (if with_gain) and the slopes of `keys` on the A = 4 single, fit subset."""
        ref = singles[CAL_A][fit_frames][:, sub]

        def loss(z):
            s1 = z[0] if with_gain else 0.0
            slopes = {k: z[(1 if with_gain else 0) + i] for i, k in enumerate(keys)}
            return rel_rmse(token_field(theta0, slopes, s1, CAL_A, fit_pts, t_fit, [CENTRE]), ref)

        n = len(keys) + (1 if with_gain else 0)
        if n == 0:
            return {}, 0.0, loss(np.zeros(0))
        res = minimize(loss, np.zeros(n), method="Powell", options={"maxfev": 600, "xtol": 1e-3, "ftol": 1e-5})
        s1 = float(res.x[0]) if with_gain else 0.0
        slopes = {k: float(res.x[(1 if with_gain else 0) + i]) for i, k in enumerate(keys)}
        return slopes, s1, float(res.fun)

    models = {"M0": ([], False), "M_gain": ([], True)}
    for i in range(1, 5):
        models[f"M{i}"] = (ORDER[:i], True)
    fitted, errors = {}, {}
    for name, (keys, gain) in models.items():
        slopes, s1, jfit = fit_model(keys, gain)
        fitted[name] = {"slopes": slopes, "gain_s1": s1, "fit_error_A4": jfit, "n_params": len(keys) + int(gain)}
        errors[name] = {A: score_single(slopes, s1, A) for A in AMPS}
        print(f"{name:7s} params {fitted[name]['n_params']}  " + " ".join(f"A={A}:{errors[name][A]:.3f}" for A in AMPS) + f"  slopes {slopes} gain {s1:.3f}")
    E_floor = errors["M0"][1.0]
    rec = {name: {A: max(errors[name][A] - E_floor, 0.0) for A in AMPS} for name in models}

    # H1, H2, H5
    def med(vals):
        return float(np.median(vals))
    h1_gain = med([(rec["M0"][A] - rec["M4"][A]) / rec["M0"][A] for A in SCORED])
    h1 = bool(h1_gain >= 0.5 and errors["M4"][0.5] <= 1.1 * errors["M0"][0.5])
    R_fixed = {A: rec["M0"][A] / I12[A] for A in SCORED}
    R_cond = {A: rec["M4"][A] / I12[A] for A in SCORED}
    h2_ratio = med([R_cond[A] / R_fixed[A] for A in SCORED])
    h2 = bool(h2_ratio <= 0.25)
    h5 = bool(all(med([rec[f"M{i}"][A] for A in SCORED]) < med([rec["M_gain"][A] for A in SCORED]) for i in range(1, 5)))
    knee = {"gain_curve": {name: med([rec[name][A] for A in SCORED]) for name in ("M0", "M_gain", "M1", "M2", "M3", "M4")}}
    tot = rec["M0"] and (knee["gain_curve"]["M_gain"] - knee["gain_curve"]["M4"])
    knee["M1_fraction_of_M4_gain"] = float((knee["gain_curve"]["M_gain"] - knee["gain_curve"]["M1"]) / tot) if tot > 0 else None

    # ---- pairs for H3 / H4 ----
    pairs = {}
    for D in PAIR_D:
        for A in (CAL_A,) + PAIR_A:
            sim = SpectralWater(p)
            sim.add_impulse(CENTRE[0] - D / 2, CENTRE[1], A, 0.03)
            sim.add_impulse(CENTRE[0] + D / 2, CENTRE[1], A, 0.03)
            pairs[(D, A)] = _record(sim, p, None).eta.astype(float)
            print(f"pair D={D:.3f} A={A} done")
    mid_mask = region(xs, CENTRE, 2.0)
    mpts = np.stack([X[mid_mask], Y[mid_mask]], -1)

    def pair_centres(D):
        return [(CENTRE[0] - D / 2, CENTRE[1]), (CENTRE[0] + D / 2, CENTRE[1])]

    def unary_pair(name, D, A, pts, times):
        return token_field(theta0, fitted[name]["slopes"], fitted[name]["gain_s1"], A, pts, times, pair_centres(D))

    def pair_term(c, D, A, pts, times, own_decay=None):
        pp = dict(theta0)
        if own_decay is not None:
            pp["lam"] = own_decay
        rmid = np.linalg.norm(pts - np.array(CENTRE)[None, :], axis=1)[None, :]
        return c * (A * A) * np.stack([chirp(rmid, np.array([[t]]), pp)[0] for t in times])

    # fit P1, P2 on the (A=4, D=0.281) residual of the fixed unary pair model, fit subset
    Dc = PAIR_D[0]
    sub_pts = np.stack([X[sub], Y[sub]], -1)
    resid_cal = pairs[(Dc, CAL_A)][fit_frames][:, sub] - unary_pair("M0", Dc, CAL_A, sub_pts, t_fit)
    target = pairs[(Dc, CAL_A)][fit_frames][:, sub]

    def loss_p1(z):
        return rel_rmse(unary_pair("M0", Dc, CAL_A, sub_pts, t_fit) + pair_term(z[0], Dc, CAL_A, sub_pts, t_fit), target)

    def loss_p2(z):
        return rel_rmse(unary_pair("M0", Dc, CAL_A, sub_pts, t_fit) + pair_term(z[0], Dc, CAL_A, sub_pts, t_fit, own_decay=np.exp(z[1])), target)

    r1 = minimize(loss_p1, [0.0], method="Powell", options={"maxfev": 300})
    r2 = minimize(loss_p2, [0.0, np.log(max(theta0["lam"], 1e-3))], method="Powell", options={"maxfev": 600})
    P1 = {"c1": float(r1.x[0])}
    P2 = {"c1": float(r2.x[0]), "lam": float(np.exp(r2.x[1]))}
    print(f"pair models: P1 {P1}  P2 {P2}")

    held = [(D, A) for D in PAIR_D for A in PAIR_A]
    pair_err = {}
    for name in ("M0", "M_gain", "M1", "M4"):
        pair_err[name] = {f"{D:.3f}_{A}": rel_rmse(unary_pair(name, D, A, mpts, t_eval), pairs[(D, A)][ok][:, mid_mask]) for D, A in held}
    pair_err["P1"] = {f"{D:.3f}_{A}": rel_rmse(unary_pair("M0", D, A, mpts, t_eval) + pair_term(P1["c1"], D, A, mpts, t_eval), pairs[(D, A)][ok][:, mid_mask]) for D, A in held}
    pair_err["P2"] = {f"{D:.3f}_{A}": rel_rmse(unary_pair("M0", D, A, mpts, t_eval) + pair_term(P2["c1"], D, A, mpts, t_eval, own_decay=P2["lam"]), pairs[(D, A)][ok][:, mid_mask]) for D, A in held}
    base = np.mean(list(pair_err["M0"].values()))
    eta = {name: float((base - np.mean(list(pair_err[name].values()))) / fitted.get(name, {"n_params": {"P1": 1, "P2": 2}[name] if name in ("P1", "P2") else 1})["n_params"])
           for name in ("M_gain", "M1", "M4", "P1", "P2")}
    h3 = bool(eta["M_gain"] >= 2 * eta["P1"] and eta["M1"] >= 2 * eta["P2"])
    # H4: cross-term share of the remaining residual
    h4_rows = {}
    for D, A in held:
        shift = int(round(D / 2 / p.dx))
        s1 = np.roll(singles[A], -shift, axis=1)[ok][:, mid_mask]
        s2 = np.roll(singles[A], shift, axis=1)[ok][:, mid_mask]
        pr = pairs[(D, A)][ok][:, mid_mask]
        cross = np.sqrt(((pr - s1 - s2) ** 2).mean())
        res_fixed = np.sqrt(((pr - unary_pair("M0", D, A, mpts, t_eval)) ** 2).mean())
        res_cond = np.sqrt(((pr - unary_pair("M4", D, A, mpts, t_eval)) ** 2).mean())
        h4_rows[f"{D:.3f}_{A}"] = {"cross_share_fixed": float(cross / res_fixed), "cross_share_cond": float(cross / res_cond)}
    h4 = bool(all(v["cross_share_cond"] > v["cross_share_fixed"] for v in h4_rows.values()))

    report = {"theta0": theta0, "E_floor": E_floor, "models": fitted, "single_errors": {n: {str(A): e for A, e in d.items()} for n, d in errors.items()},
              "recoverable": {n: {str(A): e for A, e in d.items()} for n, d in rec.items()},
              "H1": {"median_recovered_fraction": h1_gain, "no_degradation_at_0.5": bool(errors["M4"][0.5] <= 1.1 * errors["M0"][0.5]), "pass": h1},
              "H2": {"R_fixed": {str(A): v for A, v in R_fixed.items()}, "R_cond": {str(A): v for A, v in R_cond.items()}, "median_ratio": h2_ratio, "pass": h2},
              "H3": {"pair_models": {"P1": P1, "P2": P2}, "pair_errors": pair_err, "eta": eta, "pass": h3},
              "H4": {"rows": h4_rows, "pass": h4}, "H5": {"pass": h5}, "knee": knee,
              "verdict": "strong" if (h1 and h2 and h3 and h5) else ("partial" if (h1 and h5) else "failure")}
    (out / "w3.json").write_text(json.dumps(report, indent=2, default=float))
    write_md(report, out / "w3.md")
    print(json.dumps({"H1": report["H1"], "H2": {"median_ratio": h2_ratio, "pass": h2}, "H3": {"eta": eta, "pass": h3}, "H4": h4, "H5": h5, "knee": knee, "verdict": report["verdict"]}, indent=2, default=float))
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    L = ["# Math Track W3 results: unary conditioning before interaction complexity", "", "Preregistration: `docs/math-track-w3-prereg.md`.", "",
         f"Token family floor (fixed token at A = 1): {r['E_floor']:.3f}.", "", "## Single-splash error by model and amplitude (holdout: 0.5, 2, 8; calibration: 1, 4)", "",
         "| model | params | " + " | ".join(f"A={A}" for A in AMPS) + " | conditioned slopes |", "|---|---|" + "---|" * len(AMPS) + "---|"]
    for name, m in r["models"].items():
        L.append(f"| {name} | {m['n_params']} | " + " | ".join(f"{r['single_errors'][name][str(A)]:.3f}" for A in AMPS) + f" | gain {m['gain_s1']:+.3f}; " + ", ".join(f"{k} {v:+.3f}" for k, v in m["slopes"].items()) + " |")
    L += ["", f"## H1: median recovered fraction of amplitude-shaped error over A in {{2, 8}} = {r['H1']['median_recovered_fraction']:.2f} (bar 0.5); no degradation at 0.5: {r['H1']['no_degradation_at_0.5']}; pass {r['H1']['pass']}", "",
          f"## H2: R = E_rec / I12; fixed {r['H2']['R_fixed']}; conditioned {r['H2']['R_cond']}; median ratio {r['H2']['median_ratio']:.3f} (bar 0.25); pass {r['H2']['pass']}", "",
          "## H3: held-out pair errors and efficiency per parameter", "", "| model | " + " | ".join(r["H3"]["pair_errors"]["M0"].keys()) + " | eta |", "|---|" + "---|" * (len(r["H3"]["pair_errors"]["M0"]) + 1)]
    for name, d in r["H3"]["pair_errors"].items():
        L.append(f"| {name} | " + " | ".join(f"{v:.3f}" for v in d.values()) + f" | {r['H3']['eta'].get(name, float('nan')):.4f} |")
    L += ["", f"Pair models: {r['H3']['pair_models']}. H3 pass {r['H3']['pass']} (needs eta(M_gain) >= 2 eta(P1) and eta(M1) >= 2 eta(P2)).", "",
          "## H4: cross-term share of the remaining pair residual", "", "| pair | fixed unary | conditioned unary |", "|---|---|---|"]
    for k, v in r["H4"]["rows"].items():
        L.append(f"| {k} | {v['cross_share_fixed']:.3f} | {v['cross_share_cond']:.3f} |")
    L += ["", f"H4 pass {r['H4']['pass']}.", "", f"## H5 (shape beats gain on recoverable error): {r['H5']['pass']}", "",
          "## Knee: median recoverable error over {2, 8} by model: " + ", ".join(f"{k} {v:.3f}" for k, v in r["knee"]["gain_curve"].items()) + f"; M1 recovers {r['knee']['M1_fraction_of_M4_gain']} of M4's gain over M_gain.", "",
          f"## Verdict: {r['verdict']}", ""]
    path.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
