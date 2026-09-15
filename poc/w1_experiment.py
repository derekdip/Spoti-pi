"""Math Track W1: transfer of the liveness, observation-order and superposition questions to water.

Implements docs/math-track-w1-prereg.md. Usage: python poc/w1_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import RectBivariateSpline, RegularGridInterpolator
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reactive.metrics import rel_rmse  # noqa: E402
from water.experiment import fit_token  # noqa: E402
from water.teacher import SpectralWater, WaterParams, _record, run_splash  # noqa: E402
from water.tokens import KERNELS, evaluate_events  # noqa: E402

NL = dict(gamma_amp=0.25, beta=1e4, eta_ref=0.02)
CENTRE = (3.0, 3.0)
RAIN_RATE, RAIN_T, RAIN_N = 2.0, 20.0, 40
EPS_FRACS = (3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5)
GRIDS = (12, 16, 24, 32, 48, 64, 96, 128, 192, 256)
FIT_GRIDS = (64, 96, 128, 192, 256)
Q2_FRAMES = (0.5, 1.0, 1.5, 2.0, 3.0)
SEPS = (0.28125, 0.609375, 1.21875, 2.390625)
AMPS = (0.5, 1.0, 2.0, 4.0, 8.0)


def slope(eta, dx):
    return np.stack([np.gradient(eta, dx, axis=-2), np.gradient(eta, dx, axis=-1)], axis=-1)


def region(xs, centre, radius):
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    return np.sqrt((X - centre[0]) ** 2 + (Y - centre[1]) ** 2) < radius


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    report = {"nonlinearity": NL}

    # ---------------- token fit on the nonlinear single splash ----------------
    p = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **NL)
    rec = run_splash(p, *CENTRE, v0=1.0, sigma=0.03)
    X, Y = np.meshgrid(rec.xs, rec.xs, indexing="ij")
    r = np.sqrt((X - CENTRE[0]) ** 2 + (Y - CENTRE[1]) ** 2)
    ok = rec.times >= 0.15
    sub = (r < 1.6) & (np.arange(len(rec.xs))[:, None] % 3 == 0) & (np.arange(len(rec.xs))[None, :] % 3 == 0)
    fit_pts = np.stack([X[sub], Y[sub]], -1)
    fit_frames = np.flatnonzero(ok)[::2]
    ev_pos, ev_t, ev_amp = np.array([CENTRE]), np.array([0.0]), np.array([1.0])
    t0 = time.perf_counter()
    prm, j = fit_token("chirp", fit_pts, rec.times[fit_frames], rec.eta[fit_frames][:, sub].astype(float), ev_pos, ev_t, ev_amp)
    eval_mask = r < 2.0
    pts = np.stack([X[eval_mask], Y[eval_mask]], -1)
    pred, _ = evaluate_events("chirp", prm, pts, rec.times[ok], ev_pos, ev_t, ev_amp)
    e_fit = rel_rmse(pred, rec.eta[ok][:, eval_mask].astype(float))
    print(f"token fit on nonlinear teacher: height error {e_fit:.3f} ({time.perf_counter() - t0:.0f}s)  " + " ".join(f"{k}={v:.3g}" for k, v in prm.items()))
    report["token"] = {"params": prm, "fit_error_height": e_fit}

    # ---------------- Q1 liveness ----------------
    fn = KERNELS["chirp"][0]
    tau_grid = np.linspace(0.0, RAIN_T, 4001)
    r_grid = np.linspace(0.02, 3.0, 300)
    hmax = np.array([np.abs(fn(r_grid[None, :], np.array([[t]]), prm)).max() for t in tau_grid])
    future = np.maximum.accumulate(hmax[::-1])[::-1]
    tail = (tau_grid >= 1.0) & (tau_grid <= 8.0) & (future > 0)
    beta, logC = np.polyfit(tau_grid[tail], np.log(future[tail]), 1)
    beta, C = -float(beta), float(np.exp(logC))
    rng = np.random.default_rng(0)
    rain_t = np.sort(rng.uniform(0, RAIN_T, RAIN_N))
    rain_p = rng.uniform(1.0, 5.0, (RAIN_N, 2))
    K0 = future[0]
    tt = np.arange(5.0, RAIN_T, 1.0 / 60)
    live_rows = []
    for f in EPS_FRACS:
        eps = f * K0
        counts = []
        for t in tt:
            tau = t - rain_t
            fut = np.interp(np.clip(tau, 0, RAIN_T), tau_grid, future) * (tau >= 0)
            counts.append(int((fut > eps).sum()))
        live_rows.append({"eps_frac": f, "eps": float(eps), "M": float(np.mean(counts)), "predicted": float(RAIN_RATE / beta * np.log(C / eps))})
    x = np.log(1.0 / np.array(EPS_FRACS))
    M = np.array([rw["M"] for rw in live_rows])
    slope_meas = float(np.polyfit(x, M, 1)[0])
    h1 = {"beta": beta, "C": C, "K0": float(K0), "rows": live_rows, "slope_measured": slope_meas, "slope_predicted": float(RAIN_RATE / beta),
          "spearman": float(spearmanr(x, M).correlation)}
    h1["pass"] = bool(h1["spearman"] > 0.95 and abs(slope_meas / h1["slope_predicted"] - 1) < 0.5)
    print(f"Q1: beta={beta:.3f} C={C:.4f}  slope measured {slope_meas:.3f} predicted {h1['slope_predicted']:.3f}  spearman {h1['spearman']:.3f}  pass {h1['pass']}")
    # pruned reconstruction vs full token field, and full token field vs teacher rain
    pr = WaterParams(n=256, size=6.0, duration=RAIN_T, record_stride=2, **NL)
    sim = SpectralWater(pr)
    frames_t = np.arange(int(RAIN_T * 60) + 1) / 60.0
    m = pr.n // 2
    eta = np.zeros((len(frames_t), m, m), dtype=np.float32)
    t = 0.0
    k_next = 0
    for fi in range(len(frames_t)):
        eta[fi] = sim.eta()[::2, ::2]
        if fi == len(frames_t) - 1:
            break
        for _ in range(pr.substeps):
            while k_next < RAIN_N and rain_t[k_next] <= t:
                sim.add_impulse(rain_p[k_next, 0], rain_p[k_next, 1], 1.0, 0.03)
                k_next += 1
            sim.step(None)
            t += pr.dt
    xs2 = np.arange(m) * pr.dx * 2
    X2, Y2 = np.meshgrid(xs2, xs2, indexing="ij")
    keep = (X2 > 0.5) & (X2 < 5.5) & (Y2 > 0.5) & (Y2 < 5.5)
    pts2 = np.stack([X2[keep], Y2[keep]], -1)[::2]
    late = frames_t >= 5.0
    full, _ = evaluate_events("chirp", prm, pts2, frames_t[late][::3], rain_p, rain_t, np.ones(RAIN_N))
    teacher_late = eta[late][::3][:, keep][:, ::2].astype(float)
    h1["token_vs_teacher_rain"] = rel_rmse(full, teacher_late)
    prune = []
    for f in EPS_FRACS:
        eps = f * K0
        pr_pred = np.zeros_like(full)
        for fi, tcur in enumerate(frames_t[late][::3]):
            tau = tcur - rain_t
            fut = np.interp(np.clip(tau, 0, RAIN_T), tau_grid, future) * (tau >= 0)
            alive = fut > eps
            if alive.any():
                pp, _ = evaluate_events("chirp", prm, pts2, np.array([tcur]), rain_p[alive], rain_t[alive], np.ones(alive.sum()))
                pr_pred[fi] = pp[0]
        prune.append({"eps_frac": f, "error_vs_full": rel_rmse(pr_pred, full)})
    h1["pruning"] = prune
    print(f"   token field vs teacher rain {h1['token_vs_teacher_rain']:.3f}; pruning errors " + ", ".join(f"{q['eps_frac']:.0e}:{q['error_vs_full']:.3f}" for q in prune))
    report["Q1"] = h1

    # ---------------- Q2 observation order ----------------
    p5 = WaterParams(n=512, size=6.0, duration=3.2, record_stride=1, **NL)
    t0 = time.perf_counter()
    rec5 = run_splash(p5, *CENTRE, v0=1.0, sigma=0.03)
    print(f"512 teacher {time.perf_counter() - t0:.0f}s")
    xs5 = rec5.xs
    msk5 = region(xs5, CENTRE, 2.0)
    fidx = [int(round(tf * p5.fps)) for tf in Q2_FRAMES]
    ref_h = rec5.eta[fidx].astype(float)
    ref_s = slope(ref_h, p5.dx)
    q2 = {"bilinear": {}, "bicubic": {}}
    for n in GRIDS:
        xc = np.arange(n) * (6.0 / n)
        # sample the reference at coarse nodes (exact where nodes coincide with fine nodes; linear otherwise)
        eh, es = {"bilinear": [], "bicubic": []}, {"bilinear": [], "bicubic": []}
        for k in range(len(fidx)):
            samp = RegularGridInterpolator((xs5, xs5), ref_h[k], method="linear", bounds_error=False, fill_value=None)
            XC, YC = np.meshgrid(xc, xc, indexing="ij")
            coarse = samp(np.stack([XC.ravel(), YC.ravel()], -1)).reshape(n, n)
            # bilinear back to the fine grid
            lin = RegularGridInterpolator((xc, xc), coarse, method="linear", bounds_error=False, fill_value=None)
            X5, Y5 = np.meshgrid(xs5, xs5, indexing="ij")
            hb = lin(np.stack([X5.ravel(), Y5.ravel()], -1)).reshape(len(xs5), len(xs5))
            sb = slope(hb[None], p5.dx)[0]
            eh["bilinear"].append(rel_rmse(hb[msk5], ref_h[k][msk5]))
            es["bilinear"].append(rel_rmse(sb[msk5], ref_s[k][msk5]))
            if n >= 4:
                spl = RectBivariateSpline(xc, xc, coarse, kx=3, ky=3)
                hc = spl(xs5, xs5)
                sc = np.stack([spl(xs5, xs5, dx=1), spl(xs5, xs5, dy=1)], -1)
                eh["bicubic"].append(rel_rmse(hc[msk5], ref_h[k][msk5]))
                es["bicubic"].append(rel_rmse(sc[msk5], ref_s[k][msk5]))
        for kind in ("bilinear", "bicubic"):
            q2[kind][str(n)] = {"N": n * n, "E_height": float(np.mean(eh[kind])), "E_slope": float(np.mean(es[kind]))}
        print(f"  n={n:3d}: bilinear h {q2['bilinear'][str(n)]['E_height']:.4f} s {q2['bilinear'][str(n)]['E_slope']:.4f} | bicubic h {q2['bicubic'][str(n)]['E_height']:.4f} s {q2['bicubic'][str(n)]['E_slope']:.4f}")
    expo = {}
    for kind in ("bilinear", "bicubic"):
        Ns = np.array([q2[kind][str(n)]["N"] for n in FIT_GRIDS], float)
        for key in ("E_height", "E_slope"):
            Es = np.array([q2[kind][str(n)][key] for n in FIT_GRIDS])
            expo[f"{kind}_{key}"] = float(np.polyfit(np.log(Ns), np.log(Es), 1)[0])
    h2 = {"exponents": expo,
          "diff_bilinear": expo["bilinear_E_slope"] - expo["bilinear_E_height"],
          "diff_bicubic": expo["bicubic_E_slope"] - expo["bicubic_E_height"],
          "predicted": {"bilinear_E_height": -1.0, "bilinear_E_slope": -0.5, "bicubic_E_height": -2.0, "bicubic_E_slope": -1.5}}
    h2["pass_H2"] = bool(0.3 <= h2["diff_bilinear"] <= 0.7 and 0.3 <= h2["diff_bicubic"] <= 0.7)
    h2["pass_H3"] = bool(expo["bicubic_E_height"] <= expo["bilinear_E_height"] - 0.5)
    print(f"Q2 exponents {json.dumps({k: round(v, 2) for k, v in expo.items()})}  diffs {h2['diff_bilinear']:.2f} / {h2['diff_bicubic']:.2f}  H2 {h2['pass_H2']} H3 {h2['pass_H3']}")
    report["Q2"] = {"errors": q2, "tests": h2}

    # ---------------- Q3 interaction ----------------
    pq = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **NL)
    xs = np.arange(pq.n) * pq.dx
    okq = np.arange(int(pq.duration * pq.fps) + 1) / pq.fps >= 0.15
    singles = {}
    for a in AMPS:
        singles[a] = run_splash(pq, *CENTRE, v0=a, sigma=0.03).eta[okq].astype(float)
    q3 = {}
    for D in SEPS:
        shift = int(round(D / 2 / pq.dx))
        for a in AMPS:
            sim = SpectralWater(pq)
            sim.add_impulse(CENTRE[0] - D / 2, CENTRE[1], a, 0.03)
            sim.add_impulse(CENTRE[0] + D / 2, CENTRE[1], a, 0.03)
            pair = _record(sim, pq, None).eta[okq].astype(float)
            s1 = np.roll(singles[a], -shift, axis=1)
            s2 = np.roll(singles[a], shift, axis=1)
            msk = region(xs, CENTRE, 2.0)
            # interaction strength ||pair - s1 - s2|| / ||pair|| (rel_rmse takes prediction, reference)
            I_h = rel_rmse((s1 + s2)[:, msk], pair[:, msk])
            I_s = rel_rmse(slope(s1 + s2, pq.dx)[:, msk], slope(pair, pq.dx)[:, msk])
            # base-fitted token pair scaled by a, against the teacher pair; and single deviation from scaled token
            ptsq = np.stack([np.meshgrid(xs, xs, indexing="ij")[0][msk], np.meshgrid(xs, xs, indexing="ij")[1][msk]], -1)
            tok_pair, _ = evaluate_events("chirp", prm, ptsq, np.arange(int(pq.duration * pq.fps) + 1)[okq] / pq.fps,
                                          np.array([[CENTRE[0] - D / 2, CENTRE[1]], [CENTRE[0] + D / 2, CENTRE[1]]]), np.array([0.0, 0.0]), np.array([a, a]))
            e_tok_pair = rel_rmse(tok_pair, pair[:, msk])
            tok_single, _ = evaluate_events("chirp", prm, ptsq, np.arange(int(pq.duration * pq.fps) + 1)[okq] / pq.fps, np.array([CENTRE]), np.array([0.0]), np.array([a]))
            e_single = rel_rmse(tok_single, singles[a][:, msk])
            q3[f"{D:.3f}_{a}"] = {"D": D, "a": a, "I12_height": I_h, "I12_slope": I_s, "token_pair_error": e_tok_pair, "single_vs_token_error": e_single}
            print(f"  D={D:.3f} a={a}: I12 h {I_h:.4f} s {I_s:.4f}  token pair err {e_tok_pair:.3f}  single-vs-token {e_single:.3f}")
    # tests
    h4_ok, h6_ok = True, True
    for D in SEPS:
        vals = [q3[f"{D:.3f}_{a}"]["I12_height"] for a in AMPS]
        if spearmanr(AMPS, vals).correlation < 0.999:
            h4_ok = False
    for a in AMPS:
        vals = [q3[f"{D:.3f}_{a}"]["I12_height"] for D in SEPS]
        if spearmanr(SEPS, vals).correlation > 0:
            h4_ok = False
    for key, v in q3.items():
        if v["I12_height"] >= v["single_vs_token_error"]:
            h6_ok = False
    h5_ok = bool(all(q3[f"{D:.3f}_1.0"]["I12_height"] < 0.05 for D in SEPS) and q3[f"{SEPS[0]:.3f}_8.0"]["I12_height"] > 0.05)
    report["Q3"] = {"cells": q3, "H4": h4_ok, "H5": h5_ok, "H6": h6_ok}
    print(f"Q3: H4 {h4_ok} H5 {h5_ok} H6 {h6_ok}")
    report["transfer_success"] = bool(h1["pass"] and h2["pass_H2"])
    (out / "w1.json").write_text(json.dumps(report, indent=2, default=float))
    write_md(report, out / "w1.md")
    try:
        make_figure(report, out / "w1.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(f"transfer success (H1 and H2): {report['transfer_success']}")
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    q1, q2, q3 = r["Q1"], r["Q2"], r["Q3"]
    L = ["# Math Track W1 results: transfer to water", "", "Preregistration: `docs/math-track-w1-prereg.md`.", "",
         f"Token fitted to the nonlinear single splash: height error {r['token']['fit_error_height']:.3f}; " + ", ".join(f"{k}={v:.3g}" for k, v in r["token"]["params"].items()), "",
         f"## Q1 liveness: beta = {q1['beta']:.3f} 1/s, C = {q1['C']:.4f}; slope measured {q1['slope_measured']:.3f} vs predicted R/beta = {q1['slope_predicted']:.3f}; Spearman {q1['spearman']:.3f}; H1 pass {q1['pass']}", "",
         "| eps / K(0) | live tokens M | predicted (R/beta) log(C/eps) | pruned-vs-full error |", "|---|---|---|---|"]
    for rw, pr in zip(q1["rows"], q1["pruning"]):
        L.append(f"| {rw['eps_frac']:.0e} | {rw['M']:.2f} | {rw['predicted']:.2f} | {pr['error_vs_full']:.3f} |")
    L += ["", f"Full token field against the teacher rain: {q1['token_vs_teacher_rain']:.3f}.", "",
          "## Q2 observation order", "", "| n | N | bilinear height | bilinear slope | bicubic height | bicubic slope |", "|---|---|---|---|---|---|"]
    for n in GRIDS:
        b, c = q2["errors"]["bilinear"][str(n)], q2["errors"]["bicubic"][str(n)]
        L.append(f"| {n} | {n*n} | {b['E_height']:.4f} | {b['E_slope']:.4f} | {c['E_height']:.4f} | {c['E_slope']:.4f} |")
    t = q2["tests"]
    L += ["", "| quantity | measured exponent | predicted |", "|---|---|---|"]
    for k, v in t["exponents"].items():
        L.append(f"| {k} | {v:.2f} | {t['predicted'][k]:.1f} |")
    L += ["", f"Slope minus height exponent: bilinear {t['diff_bilinear']:+.2f}, bicubic {t['diff_bicubic']:+.2f} (prediction +0.5, bar [0.3, 0.7]). H2 pass {t['pass_H2']}; H3 (bicubic height steeper by >= 0.5) pass {t['pass_H3']}.", "",
          "## Q3 interaction", "", "| D (m) | a | I12 height | I12 slope | token pair error | single vs token |", "|---|---|---|---|---|---|"]
    for v in q3["cells"].values():
        L.append(f"| {v['D']:.3f} | {v['a']} | {v['I12_height']:.4f} | {v['I12_slope']:.4f} | {v['token_pair_error']:.3f} | {v['single_vs_token_error']:.3f} |")
    L += ["", f"H4 (monotone in a, non-increasing in D): {q3['H4']}. H5 (base < 5% everywhere, 8x > 5% at smallest D): {q3['H5']}. H6 (cross-term below single-splash token deviation everywhere): {q3['H6']}.", "",
          f"## Transfer success (H1 and H2): {r['transfer_success']}", ""]
    path.write_text("\n".join(L) + "\n")


def make_figure(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    q1 = r["Q1"]
    x = np.log(1 / np.array([rw["eps_frac"] for rw in q1["rows"]]))
    axes[0].plot(x, [rw["M"] for rw in q1["rows"]], "o-", label="live tokens (measured)")
    axes[0].plot(x, [rw["predicted"] for rw in q1["rows"]], "--", label="(R/beta) log(C/eps)")
    axes[0].set_xlabel("log(1/eps)")
    axes[0].set_ylabel("live splash tokens")
    axes[0].set_title("Q1: liveness law on water")
    axes[0].legend(fontsize=8)
    q2 = r["Q2"]["errors"]
    for kind, ls in (("bilinear", "-"), ("bicubic", "--")):
        Ns = [q2[kind][str(n)]["N"] for n in GRIDS]
        axes[1].loglog(Ns, [q2[kind][str(n)]["E_height"] for n in GRIDS], "o" + ls, label=f"{kind} height")
        axes[1].loglog(Ns, [q2[kind][str(n)]["E_slope"] for n in GRIDS], "s" + ls, label=f"{kind} slope")
    axes[1].set_xlabel("grid cells N")
    axes[1].set_ylabel("relative error")
    axes[1].set_title("Q2: height vs slope, bilinear vs bicubic")
    axes[1].legend(fontsize=8)
    q3 = r["Q3"]["cells"]
    for D in SEPS:
        axes[2].semilogy(AMPS, [q3[f"{D:.3f}_{a}"]["I12_height"] for a in AMPS], "o-", label=f"D = {D:.2f} m")
    axes[2].axhline(0.05, color="k", lw=0.8, ls=":")
    axes[2].set_xlabel("amplitude / base")
    axes[2].set_ylabel("interaction strength I12 (height)")
    axes[2].set_title("Q3: when superposition fails")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
