"""Pond ripples: fit cheap ring tokens to the exact linear-wave teacher.

1. Splash: one impulse. Fit the fixed-wavelength `ring` and the dispersive
   `chirp` token to the height field; score height and slope error.
2. Wake: a pressure bump dragged across the surface. Reconstruct it as the
   Huygens superposition of the splash token along the path, at several
   emission spacings; also refit the token on the wake itself.

Usage: python poc/water/experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reactive.metrics import rel_rmse  # noqa: E402
from water.teacher import WaterParams, run_splash, run_wake  # noqa: E402
from water.tokens import KERNELS, evaluate_events  # noqa: E402


def slope(eta: np.ndarray, dx: float) -> np.ndarray:
    gx = np.gradient(eta, dx, axis=-2)
    gy = np.gradient(eta, dx, axis=-1)
    return np.stack([gx, gy], axis=-1)


def fit_token(kind: str, pts: np.ndarray, times: np.ndarray, ref: np.ndarray,
              ev_pos: np.ndarray, ev_t: np.ndarray, ev_amp: np.ndarray, seed: int = 0) -> tuple[dict, float]:
    fn, names, bounds, init, _ = KERNELS[kind]

    def loss(x):
        p = dict(zip(names, x))
        pred, _ = evaluate_events(kind, p, pts, times, ev_pos, ev_t, ev_amp)
        return rel_rmse(pred, ref)

    res = differential_evolution(loss, bounds, seed=seed, maxiter=60, popsize=12, tol=1e-6, polish=False, x0=init)
    res = minimize(loss, res.x, method="Powell", bounds=bounds, options={"maxfev": 1500})
    return dict(zip(names, res.x)), float(res.fun)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    p = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1)
    report = {"params": p.__dict__}

    # ---------------- splash ----------------
    c = (3.0, 3.0)
    rec = run_splash(p, *c, v0=1.0, sigma=0.03)
    X, Y = np.meshgrid(rec.xs, rec.xs, indexing="ij")
    r = np.sqrt((X - c[0]) ** 2 + (Y - c[1]) ** 2)
    t_ok = rec.times >= 0.15  # skip the cavity collapse: not a wave yet
    eval_mask = r < 2.0
    # fit subset: every 3rd grid point inside 1.6 m, every 2nd ok frame
    sub = (r < 1.6)
    sub[::3, :] &= True
    sub &= (np.arange(len(rec.xs))[:, None] % 3 == 0) & (np.arange(len(rec.xs))[None, :] % 3 == 0)
    fit_pts = np.stack([X[sub], Y[sub]], axis=-1)
    fit_frames = np.flatnonzero(t_ok)[::2]
    fit_ref = rec.eta[fit_frames][:, sub].astype(float)
    ev_pos, ev_t, ev_amp = np.array([c]), np.array([0.0]), np.array([1.0])
    print(f"splash: fit on {fit_pts.shape[0]} points x {len(fit_frames)} frames; eval on {eval_mask.sum()} points x {t_ok.sum()} frames")
    eval_pts = np.stack([X[eval_mask], Y[eval_mask]], axis=-1)
    ref_eval = rec.eta[t_ok][:, eval_mask].astype(float)
    ref_slope = slope(rec.eta[t_ok].astype(float), p.dx)[:, eval_mask]
    splash = {}
    fitted = {}
    for kind in ("ring", "chirp"):
        t0 = time.perf_counter()
        prm, j = fit_token(kind, fit_pts, rec.times[fit_frames], fit_ref, ev_pos, ev_t, ev_amp)
        pred, live = evaluate_events(kind, prm, eval_pts, rec.times[t_ok], ev_pos, ev_t, ev_amp)
        full = np.zeros_like(rec.eta[t_ok], dtype=float)
        full[:, eval_mask] = pred
        pred_slope = slope(full, p.dx)[:, eval_mask]
        splash[kind] = {"params": prm, "E_height": rel_rmse(pred, ref_eval), "E_slope": rel_rmse(pred_slope, ref_slope),
                        "cost_per_point": KERNELS[kind][4], "fit_seconds": time.perf_counter() - t0}
        fitted[kind] = prm
        print(f"  {kind:6s} E_height={splash[kind]['E_height']:.3f} E_slope={splash[kind]['E_slope']:.3f}  "
              + " ".join(f"{k}={v:.3g}" for k, v in prm.items()))
    report["splash"] = splash

    # ---------------- wake ----------------
    v_src, t_move = (1.0, 0.0), 3.0
    start = (1.0, 3.0)
    wrec = run_wake(p, start, v_src, t_move, p0=0.05, sigma=0.05)
    wt_ok = wrec.times >= 0.5
    band = (np.abs(Y - 3.0) < 1.2) & (X > 0.5) & (X < 5.5)
    wsub = band & (np.arange(len(rec.xs))[:, None] % 3 == 0) & (np.arange(len(rec.xs))[None, :] % 3 == 0)
    w_pts = np.stack([X[wsub], Y[wsub]], axis=-1)
    w_frames = np.flatnonzero(wt_ok)[::2]
    w_ref = wrec.eta[w_frames][:, wsub].astype(float)
    kind = min(splash, key=lambda k: splash[k]["E_height"])
    wake = {"token_used": kind, "huygens": {}}
    print(f"wake: Huygens superposition of the fitted '{kind}' token along the path")
    for ds in (0.02, 0.05, 0.1, 0.2):
        s = np.arange(0.0, v_src[0] * t_move + 1e-9, ds)
        ev_pos_w = np.stack([start[0] + s, np.full_like(s, start[1])], axis=-1)
        ev_t_w = s / v_src[0]
        base, live = evaluate_events(kind, fitted[kind], w_pts, wrec.times[w_frames], ev_pos_w, ev_t_w, np.ones_like(s))
        alpha = float((base * w_ref).sum() / max((base * base).sum(), 1e-20))  # linear amplitude fit
        wake["huygens"][str(ds)] = {"E_height": rel_rmse(alpha * base, w_ref), "tokens": int(len(s)),
                                    "live_tokens_per_point": live, "amplitude_scale": alpha}
        print(f"  spacing {ds:.2f} m: {len(s):3d} tokens, {live:5.1f} live per point, E_height={wake['huygens'][str(ds)]['E_height']:.3f}")
    # refit the token's shape on the wake itself (5 cm spacing)
    s = np.arange(0.0, v_src[0] * t_move + 1e-9, 0.05)
    ev_pos_w = np.stack([start[0] + s, np.full_like(s, start[1])], axis=-1)
    ev_t_w = s / v_src[0]
    t0 = time.perf_counter()
    prm_w, j = fit_token(kind, w_pts[::2], wrec.times[w_frames][::2], w_ref[::2, ::2], ev_pos_w, ev_t_w, np.ones_like(s))
    pred_w, live_w = evaluate_events(kind, prm_w, w_pts, wrec.times[w_frames], ev_pos_w, ev_t_w, np.ones_like(s))
    wake["refit_on_wake"] = {"params": prm_w, "E_height": rel_rmse(pred_w, w_ref), "live_tokens_per_point": live_w,
                             "fit_seconds": time.perf_counter() - t0}
    print(f"  refit on wake: E_height={wake['refit_on_wake']['E_height']:.3f} ({time.perf_counter() - t0:.0f}s)")
    report["wake"] = wake

    (out / "water.json").write_text(json.dumps(report, indent=2, default=float))
    write_md(report, out / "water.md")
    try:
        make_figure(rec, wrec, fitted, kind, prm_w, p, out / "water.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(f"wrote {out}")


def write_md(r: dict, path: Path) -> None:
    lines = ["# Pond ripples: cheap tokens against the exact linear-wave teacher", "",
             f"Teacher: {r['params']['n']}x{r['params']['n']} spectral linear waves on a {r['params']['size']} m pond, "
             f"depth {r['params']['depth']} m, exact per-mode propagation with the full dispersion relation.", "",
             "## Splash (one impulse), scored on points within 2 m for t >= 0.15 s", "",
             "| token | height error | slope error | ops per point per live token |", "|---|---|---|---|"]
    for k, v in r["splash"].items():
        lines.append(f"| {k} | {v['E_height']:.3f} | {v['E_slope']:.3f} | {v['cost_per_point']:.0f} |")
    lines += ["", "Fitted parameters:", "", "```"]
    for k, v in r["splash"].items():
        lines.append(f"{k}: " + ", ".join(f"{a}={b:.4g}" for a, b in v["params"].items()))
    lines += ["```", "", f"## Wake (a 5 cm pressure bump dragged 3 m at 1 m/s), token: {r['wake']['token_used']}", "",
              "Huygens superposition of the splash-fitted token along the path, one global amplitude fitted.", "",
              "| emission spacing | tokens | live tokens per point | height error |", "|---|---|---|---|"]
    for ds, v in r["wake"]["huygens"].items():
        lines.append(f"| {float(ds):.2f} m | {v['tokens']} | {v['live_tokens_per_point']:.1f} | {v['E_height']:.3f} |")
    w = r["wake"]["refit_on_wake"]
    lines += ["", f"Token shape refitted on the wake itself at 5 cm spacing: height error {w['E_height']:.3f}, "
              f"{w['live_tokens_per_point']:.1f} live tokens per point.", ""]
    path.write_text("\n".join(lines) + "\n")


def make_figure(rec, wrec, fitted, kind, prm_w, p, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    X, Y = np.meshgrid(rec.xs, rec.xs, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel()], axis=-1)
    frames = [int(0.5 * p.fps), int(1.5 * p.fps), int(3.0 * p.fps)]
    fig, axes = plt.subplots(3, 3, figsize=(13, 12))
    for col, f in enumerate(frames):
        t = rec.times[f]
        pred, _ = evaluate_events(kind, fitted[kind], pts, np.array([t]), np.array([[3.0, 3.0]]), np.array([0.0]), np.array([1.0]))
        v = np.abs(rec.eta[f]).max()
        for row, (name, img) in enumerate((("teacher splash", rec.eta[f]), (f"{kind} token", pred[0].reshape(X.shape)))):
            ax = axes[row, col]
            ax.imshow(img.T, origin="lower", extent=(0, p.size, 0, p.size), cmap="RdBu_r", vmin=-v, vmax=v)
            ax.set_title(f"{name}  t={t:.1f}s")
            ax.set_xlim(1, 5)
            ax.set_ylim(1, 5)
            ax.set_xticks([])
            ax.set_yticks([])
    # wake row: teacher vs Huygens at the last moving frame and 1 s after
    s = np.arange(0.0, 3.0 + 1e-9, 0.05)
    ev_pos = np.stack([1.0 + s, np.full_like(s, 3.0)], axis=-1)
    for col, t in enumerate((1.5, 3.0, 4.0)):
        f = int(t * p.fps)
        pred, _ = evaluate_events(kind, prm_w, pts, np.array([t]), ev_pos, s / 1.0, np.ones_like(s))
        v = np.abs(wrec.eta[f]).max()
        ax = axes[2, col]
        img = np.concatenate([wrec.eta[f][:, :X.shape[1] // 2], pred[0].reshape(X.shape)[:, X.shape[1] // 2:]], axis=1)
        ax.imshow(img.T, origin="lower", extent=(0, p.size, 0, p.size), cmap="RdBu_r", vmin=-v, vmax=v)
        ax.axhline(p.size / 2, color="k", lw=0.5)
        ax.set_title(f"wake t={t:.1f}s: teacher (bottom) / tokens (top)")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(path, dpi=100)


if __name__ == "__main__":
    main()
