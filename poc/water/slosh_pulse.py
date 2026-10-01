"""Puddle slosh as a bouncing pulse token, on the same real MPM data as slosh_fit.py.

Model: the impact launches a pulse both ways along the box; walls reflect it
(method of images: sources at x_imp + 2kL and -x_imp + 2kL). Each pulse is a
Gaussian crest plus a Gaussian trough-crest pair (two linear amplitudes),
decaying as e^{-gamma tau}, travelling at speed c. Nonlinear parameters:
c, gamma, w, x_imp, t_shift. Scored in-window and on the held-out second half.

Usage: python poc/water/slosh_pulse.py --data <valid.tfrecord> [--out poc/results] [--max 30]
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
X0 = BOUNDS[0][0]
N_IMAGES = 6


def design(x: np.ndarray, tau: np.ndarray, c: float, gamma: float, w: float, x_imp: float, t_shift: float) -> np.ndarray:
    """(T*X, 2) basis: symmetric crest pulses and antisymmetric trough-crest pulses, with images."""
    xr = x - X0  # box-relative
    xi = x_imp - X0
    tt = tau + t_shift
    env = np.exp(-gamma * tt)[:, None]
    sym = np.zeros((len(tau), len(x)))
    asym = np.zeros((len(tau), len(x)))
    for k in range(-N_IMAGES, N_IMAGES + 1):
        for src in (xi + 2 * k * L, -xi + 2 * k * L):
            for sgn in (1.0, -1.0):
                d = (xr[None, :] - src - sgn * c * tt[:, None]) / w
                g = np.exp(-0.5 * d * d)
                sym += g
                asym += sgn * d * g  # odd in the travel direction: steep front, trailing trough
    return np.stack([(env * sym).ravel(), (env * asym).ravel()], axis=1)


def fit(x, tau, d, init):
    y = d.ravel()

    def unpack(z):
        return np.exp(z[0]), np.exp(z[1]), np.exp(z[2]), X0 + L / (1 + np.exp(-z[3])), np.exp(z[4])

    def loss(z):
        if np.any(np.abs(z) > 12):  # keep parameters in a sane range; outside it the basis degenerates
            return 10.0
        M = design(x, tau, *unpack(z))
        if not np.all(np.isfinite(M)) or np.abs(M).max() < 1e-12:
            return 10.0
        try:
            coef, *_ = np.linalg.lstsq(M, y, rcond=None)
        except np.linalg.LinAlgError:
            return 10.0
        return rel_rmse(M @ coef, y)

    c0, g0, w0, xi0, ts0 = init
    z0 = np.array([np.log(c0), np.log(g0), np.log(w0), np.log((xi0 - X0) / (L - (xi0 - X0))), np.log(ts0)])
    res = minimize(loss, z0, method="Powell", options={"maxfev": 500, "xtol": 1e-3, "ftol": 1e-5})
    prm = unpack(res.x)
    M = design(x, tau, *prm)
    try:
        coef, *_ = np.linalg.lstsq(M, y, rcond=None)
    except np.linalg.LinAlgError:
        coef = np.zeros(M.shape[1])
    return prm, coef, float(res.fun)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "results"))
    ap.add_argument("--max", type=int, default=30)
    ap.add_argument("--wall-skip", type=int, default=0, help="drop this many columns at each wall (run-up is not slosh)")
    ap.add_argument("--t-after", type=int, default=150, help="window starts this many frames after the floor is 90%% wet")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    out = Path(args.out)
    rows = []
    example = None
    for i, (ptype, pos) in enumerate(read_tfrecords(args.data, dim=2, max_records=args.max)):
        xc, h = surface_profile(pos, BOUNDS, bins=64)
        wet = np.mean(~np.isnan(h), axis=1)
        if not (wet > 0.9).any():
            continue
        t_land = int(np.argmax(wet > 0.9))
        t0 = t_land + args.t_after
        if pos.shape[0] - t0 < 400:
            continue
        win = np.arange(t0, pos.shape[0])
        if args.wall_skip:
            xc = xc[args.wall_skip:-args.wall_skip]
            h = h[:, args.wall_skip:-args.wall_skip]
        hw = h[win]
        mean_level = np.nanmean(hw)
        d = np.nan_to_num(hw - mean_level, nan=0.0)
        tau = (win - t0) * DT
        x_imp0 = float(pos[max(t_land - 40, 0), :, 0].mean())  # where the drop was just before landing
        # wave speed guess from the fundamental period, as in slosh_fit
        phi1 = np.cos(np.pi * (xc - X0) / L)
        a1 = d @ phi1 / (phi1 @ phi1)
        spec = np.abs(np.fft.rfft(a1 - a1.mean()))
        f1 = np.fft.rfftfreq(len(a1), DT)[1:][np.argmax(spec[1:])]
        init = (2 * L * f1, 1.0, 0.08, x_imp0, 0.4)
        half = len(win) // 2
        prm, coef, e_in = fit(xc, tau, d, init)
        prm_h, coef_h, _ = fit(xc, tau[:half], d[:half], init)
        e_out = rel_rmse(design(xc, tau[half:], *prm_h) @ coef_h, d[half:].ravel())
        rows.append({"traj": i, "depth": float(mean_level), "c": prm[0], "gamma": prm[1], "w": prm[2], "x_imp": prm[3],
                     "t_shift": prm[4], "amp_sym": float(coef[0]), "amp_asym": float(coef[1]), "E_in": e_in, "E_holdout": float(e_out)})
        print(f"traj {i:2d}: depth {mean_level:.3f}  c={prm[0]:.2f} gamma={prm[1]:.2f} w={prm[2]:.3f} x_imp={prm[3]:.2f}  "
              f"in {e_in:.3f} holdout {e_out:.3f}")
        if example is None:
            example = {"tau": tau, "d": d, "pred": (design(xc, tau, *prm) @ coef).reshape(d.shape), "traj": i, "xc": xc}
    e_in = np.array([r["E_in"] for r in rows])
    e_out = np.array([r["E_holdout"] for r in rows])
    cs = np.array([r["c"] for r in rows])
    depths = np.array([r["depth"] for r in rows])
    summary = {"trajectories": len(rows), "E_in_median": float(np.median(e_in)),
               "E_in_iqr": [float(np.percentile(e_in, 25)), float(np.percentile(e_in, 75))],
               "E_holdout_median": float(np.median(e_out)),
               "E_holdout_iqr": [float(np.percentile(e_out, 25)), float(np.percentile(e_out, 75))],
               "g_estimate_median": float(np.median(cs ** 2 / depths)), "rows": rows}
    (out / f"slosh_pulse{args.tag}.json").write_text(json.dumps(summary, indent=2))
    lines = ["# Puddle slosh as a bouncing pulse (real MPM data, DeepMind WaterDrop)", "",
             f"Window starts {args.t_after} frames after the floor is 90% wet; {args.wall_skip} columns dropped at each wall.", "",
             f"{len(rows)} trajectories, same window as the standing-mode fit. One pulse launched both ways from the impact,",
             "reflected by the walls (method of images), Gaussian crest + trough-crest pair, exponential decay. 5 nonlinear",
             "parameters plus 2 linear amplitudes.", "",
             "| | in-window error (median, IQR) | held-out error (median, IQR) |", "|---|---|---|",
             f"| bouncing pulse | {summary['E_in_median']:.3f} ({summary['E_in_iqr'][0]:.2f}-{summary['E_in_iqr'][1]:.2f}) | "
             f"{summary['E_holdout_median']:.3f} ({summary['E_holdout_iqr'][0]:.2f}-{summary['E_holdout_iqr'][1]:.2f}) |", "",
             f"Shallow-water check c^2 / depth: median {summary['g_estimate_median']:.1f} in dataset units.", ""]
    (out / f"slosh_pulse{args.tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if example is not None:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(3, 1, figsize=(11, 9))
            v = np.abs(example["d"]).max()
            for ax, (name, img) in zip(axes[:2], (("real MPM surface, deviation from mean level", example["d"]),
                                                  ("bouncing pulse token, fitted", example["pred"]))):
                ax.imshow(img.T, origin="lower", aspect="auto", extent=(example["tau"][0], example["tau"][-1], 0.1, 0.9),
                          cmap="RdBu_r", vmin=-v, vmax=v)
                ax.set_ylabel("x across the box")
                ax.set_title(f"{name} (trajectory {example['traj']})")
            col = 8
            axes[2].plot(example["tau"], example["d"][:, col], "k", lw=1, label="real")
            axes[2].plot(example["tau"], example["pred"][:, col], "r", lw=1, label="pulse token")
            axes[2].set_xlabel("time after window start (s)")
            axes[2].legend()
            fig.tight_layout()
            fig.savefig(out / f"slosh_pulse{args.tag}.png", dpi=100)
        except Exception as exc:
            print(f"(figure skipped: {exc})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
