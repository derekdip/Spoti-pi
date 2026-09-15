"""Puddle slosh on real MPM data (DeepMind WaterDrop): how few standing modes fit?

For each trajectory: extract the free surface h(x, t), take the window after the
drop has landed and spread, and fit
    h - mean = sum_n cos(n pi x / L) e^{-gamma_n tau} [c_n cos(w_n tau) + s_n sin(w_n tau)]
with shallow-water frequencies w_n = n pi c / L. Wave speed c and dampings are
fitted (Powell), amplitudes/phases are a linear least-squares inner solve.

Scored in-window and on a held-out second half (fit on the first half only),
which is the rollout test: do the modes keep predicting after the fit ends?

Usage: python poc/water/slosh_fit.py --data <valid.tfrecord> [--out poc/results] [--max 30]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reactive.metrics import rel_rmse  # noqa: E402
from water.gns_data import read_tfrecords, surface_profile  # noqa: E402

BOUNDS = [[0.1, 0.9], [0.1, 0.9]]
DT = 0.0025
L = 0.8


def design(x: np.ndarray, tau: np.ndarray, c: float, gammas: np.ndarray) -> np.ndarray:
    """(T*X, 2K) design matrix for K modes."""
    K = len(gammas)
    n = np.arange(1, K + 1)
    phi = np.cos(np.pi * n[None, :] * (x[:, None] - BOUNDS[0][0]) / L)  # (X, K)
    w = np.pi * n * c / L
    env = np.exp(-gammas[None, :] * tau[:, None])  # (T, K)
    C = env * np.cos(w[None, :] * tau[:, None])
    S = env * np.sin(w[None, :] * tau[:, None])
    cols = []
    for k in range(K):
        cols.append((C[:, k][:, None] * phi[:, k][None, :]).ravel())
        cols.append((S[:, k][:, None] * phi[:, k][None, :]).ravel())
    return np.stack(cols, axis=1)


def fit_modes(x, tau, d, K, shared_damping, c0):
    """Return (c, gammas, coeffs, in-window rel error)."""
    y = d.ravel()

    def unpack(z):
        c = np.exp(z[0])
        g = np.exp(z[1:]) if not shared_damping else np.full(K, np.exp(z[1]))
        return c, g

    def loss(z):
        c, g = unpack(z)
        M = design(x, tau, c, g)
        coef, *_ = np.linalg.lstsq(M, y, rcond=None)
        return rel_rmse(M @ coef, y)

    z0 = np.concatenate([[np.log(c0)], np.log(np.full(1 if shared_damping else K, 2.0))])
    res = minimize(loss, z0, method="Powell", options={"maxfev": 600, "xtol": 1e-3, "ftol": 1e-5})
    c, g = unpack(res.x)
    M = design(x, tau, c, g)
    coef, *_ = np.linalg.lstsq(M, y, rcond=None)
    return c, g, coef, float(res.fun)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "results"))
    ap.add_argument("--max", type=int, default=30)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    Ks = (1, 2, 3, 4, 6, 8)
    per_traj = []
    example = None
    for i, (ptype, pos) in enumerate(read_tfrecords(args.data, dim=2, max_records=args.max)):
        xc, h = surface_profile(pos, BOUNDS, bins=64)
        wet = np.mean(~np.isnan(h), axis=1)
        if not (wet > 0.9).any():
            continue
        t_land = int(np.argmax(wet > 0.9))
        t0 = t_land + 150
        if pos.shape[0] - t0 < 400:
            continue
        win = np.arange(t0, pos.shape[0])
        hw = h[win]
        nan_frac = float(np.isnan(hw).mean())
        mean_level = np.nanmean(hw)
        d = np.nan_to_num(hw - mean_level, nan=0.0)
        tau = (win - t0) * DT
        # initial wave speed from the dominant frequency of the first mode's coefficient
        phi1 = np.cos(np.pi * (xc - BOUNDS[0][0]) / L)
        a1 = d @ phi1 / (phi1 @ phi1)
        spec = np.abs(np.fft.rfft(a1 - a1.mean()))
        freqs = np.fft.rfftfreq(len(a1), DT)
        f1 = freqs[1:][np.argmax(spec[1:])]
        c0 = 2 * L * f1
        half = len(win) // 2
        row = {"traj": i, "t_land": t_land, "frames": len(win), "depth": float(mean_level), "nan_frac": nan_frac,
               "c0_from_spectrum": float(c0), "K": {}}
        for K in Ks:
            for shared in (False, True):
                c, g, coef, e_in = fit_modes(xc, tau, d, K, shared, c0)
                # held-out: fit on first half, score second half
                c_h, g_h, coef_h, _ = fit_modes(xc, tau[:half], d[:half], K, shared, c0)
                M2 = design(xc, tau[half:], c_h, g_h)
                e_out = rel_rmse(M2 @ coef_h, d[half:].ravel())
                key = f"{K}{'s' if shared else 'p'}"
                row["K"][key] = {"K": K, "shared_damping": shared, "c": float(c), "gammas": g.tolist(),
                                 "E_in": e_in, "E_holdout": float(e_out)}
                if example is None and K == 4 and not shared:
                    example = {"xc": xc, "tau": tau, "d": d, "pred": (design(xc, tau, c, g) @ coef).reshape(d.shape),
                               "traj": i}
        per_traj.append(row)
        best = row["K"]["4p"]
        print(f"traj {i:2d}: landed f{t_land}, depth {mean_level:.3f}, c0 {c0:.2f}, "
              f"K=4 per-mode damping: in {best['E_in']:.3f} holdout {best['E_holdout']:.3f}   "
              f"K=8: in {row['K']['8p']['E_in']:.3f} holdout {row['K']['8p']['E_holdout']:.3f}")
    keys = sorted({k for r in per_traj for k in r["K"]}, key=lambda s: (int(s[:-1]), s[-1]))
    summary = {}
    for k in keys:
        e_in = np.array([r["K"][k]["E_in"] for r in per_traj])
        e_out = np.array([r["K"][k]["E_holdout"] for r in per_traj])
        cs = np.array([r["K"][k]["c"] for r in per_traj])
        summary[k] = {"K": int(k[:-1]), "shared_damping": k[-1] == "s",
                      "E_in_median": float(np.median(e_in)), "E_in_iqr": [float(np.percentile(e_in, 25)), float(np.percentile(e_in, 75))],
                      "E_holdout_median": float(np.median(e_out)), "E_holdout_iqr": [float(np.percentile(e_out, 25)), float(np.percentile(e_out, 75))],
                      "c_median": float(np.median(cs))}
    depths = np.array([r["depth"] for r in per_traj])
    cs = np.array([r["K"]["4p"]["c"] for r in per_traj])
    # shallow water says c = sqrt(g h): recover g in dataset units from the fits
    g_est = cs ** 2 / depths
    report = {"trajectories": len(per_traj), "per_trajectory": per_traj, "summary": summary,
              "g_estimate_median": float(np.median(g_est)), "g_estimate_iqr": [float(np.percentile(g_est, 25)), float(np.percentile(g_est, 75))]}
    (out / "slosh.json").write_text(json.dumps(report, indent=2))
    lines = ["# Puddle slosh on real MPM data (DeepMind WaterDrop, validation set)", "",
             f"{len(per_traj)} trajectories. Window starts 150 frames (0.375 s) after the drop has wet 90% of the floor. "
             "Model: K standing shallow-water modes with fitted wave speed and damping; amplitudes and phases by least squares. "
             "Held-out: fit on the first half of the window, score the second half.", "",
             "| modes | damping | in-window error (median, IQR) | held-out error (median, IQR) | wave speed c (median) |",
             "|---|---|---|---|---|"]
    for k in keys:
        s = summary[k]
        lines.append(f"| {s['K']} | {'shared' if s['shared_damping'] else 'per mode'} | {s['E_in_median']:.3f} ({s['E_in_iqr'][0]:.2f}-{s['E_in_iqr'][1]:.2f}) | "
                     f"{s['E_holdout_median']:.3f} ({s['E_holdout_iqr'][0]:.2f}-{s['E_holdout_iqr'][1]:.2f}) | {s['c_median']:.2f} |")
    lines += ["", f"Shallow-water check: c^2 / depth should be the simulator's g. Median {report['g_estimate_median']:.1f} "
              f"(IQR {report['g_estimate_iqr'][0]:.1f}-{report['g_estimate_iqr'][1]:.1f}) in dataset units.", ""]
    (out / "slosh.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if example is not None:
        try:
            make_figure(example, out / "slosh.png")
        except Exception as exc:
            print(f"(figure skipped: {exc})")
    print(f"wrote {out}")


def make_figure(ex, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(11, 9))
    v = np.abs(ex["d"]).max()
    for ax, (name, img) in zip(axes[:2], (("real MPM surface, deviation from mean level", ex["d"]), ("4 standing modes, fitted", ex["pred"]))):
        ax.imshow(img.T, origin="lower", aspect="auto", extent=(ex["tau"][0], ex["tau"][-1], 0.1, 0.9), cmap="RdBu_r", vmin=-v, vmax=v)
        ax.set_ylabel("x across the box")
        ax.set_title(f"{name} (trajectory {ex['traj']})")
    col = 8
    axes[2].plot(ex["tau"], ex["d"][:, col], "k", lw=1, label="real")
    axes[2].plot(ex["tau"], ex["pred"][:, col], "r", lw=1, label="4 modes")
    axes[2].set_xlabel("time after window start (s)")
    axes[2].set_ylabel(f"height at x={ex['xc'][col]:.2f}")
    axes[2].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=100)


if __name__ == "__main__":
    main()
