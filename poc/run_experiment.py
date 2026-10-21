"""End-to-end: teacher -> record -> greedy search over cheap grammar -> report.

Usage: python poc/run_experiment.py [--quick] [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reactive.causes import bank_path, emit_stride_events, s_curve_walk  # noqa: E402
from reactive.field import bake_and_sample  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.metrics import coarse_corr, coarse_rel_rmse, rel_rmse, rel_rmse_smoothed, trail_iou  # noqa: E402
from reactive.search import Objective, greedy_search, optimise  # noqa: E402
from reactive.teacher import TeacherParams, run_teacher  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="smaller teacher, fewer optimiser evals")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    # 1. causes and teacher
    tp = TeacherParams(nx=24, ny=24) if args.quick else TeacherParams()
    path = s_curve_walk(t_total=tp.duration)
    print(f"teacher: {tp.nx * tp.ny} stalks, {tp.duration}s at {tp.fps} fps x {tp.substeps} substeps")
    rec = run_teacher(path, tp)
    print(f"  wall {rec.wall_time:.2f}s, ~{rec.flops_per_stalk_frame:.0f} ops/stalk/frame, "
          f"peak |bend| {np.linalg.norm(rec.bend, axis=-1).max():.3f} m")

    # 2. banked causes (what the runtime keeps)
    events = emit_stride_events(path, stride=0.5)
    ptoken = bank_path(path, hz=20.0)
    token_floats = len(events) * 5 + ptoken.points.size + ptoken.times.size
    state_floats = rec.pos.shape[0] * 4  # (b, v) per stalk in a stateful runtime
    print(f"banked causes: {len(events)} stride events + {len(ptoken.times)}-point path "
          f"= {token_floats} floats vs {state_floats} floats of per-stalk state")

    # 3. fit subset (frames x stalks) and full-eval geometry
    n = rec.pos.shape[0]
    frame_step = 2
    fit_frames = np.arange(0, len(rec.times), frame_step)
    g_all = build_geometry(rec.pos, events, ptoken, path)
    # fit on every stalk within 1 m of the path (where >99% of the energy is) plus a few far ones
    near = np.flatnonzero(g_all.path_dperp < 1.0)
    far = np.flatnonzero(g_all.path_dperp >= 1.0)
    far = rng.choice(far, size=min(len(far), 60), replace=False)
    fit_stalks = np.sort(np.concatenate([near, far]))
    g_fit = build_geometry(rec.pos[fit_stalks], events, ptoken, path)
    print(f"fit subset: {len(fit_stalks)} stalks x {len(fit_frames)} frames")
    late = rec.times >= path.t_walk + 1.0  # persistence phase (after walking stops)
    obj = Objective(g_fit, rec.times[fit_frames], rec.bend[fit_frames][:, fit_stalks],
                    late[fit_frames], w_late=0.5, lambda_cost=0.01)

    # 4. search
    t0 = time.perf_counter()
    model, history = greedy_search(obj, max_terms=5)
    print(f"search took {time.perf_counter() - t0:.1f}s")
    print("discovered model:\n" + model.describe())

    # 5. full evaluation on every stalk and frame
    t0 = time.perf_counter()
    pred, cost = model.evaluate(g_all, rec.times)
    cheap_wall = time.perf_counter() - t0
    walk = rec.times <= path.t_walk
    report = {
        "teacher": {"stalks": n, "frames": len(rec.times), "wall_s": rec.wall_time,
                    "ops_per_stalk_frame": rec.flops_per_stalk_frame},
        "tokens": {"events": len(events), "path_points": len(ptoken.times), "floats": token_floats,
                   "per_stalk_state_floats": state_floats},
        "model": {"terms": model.names, "description": model.describe(), "ops_per_stalk_frame": cost,
                  "eval_wall_s": cheap_wall},
        "errors": {
            "E_all": rel_rmse(pred, rec.bend),
            "E_walk": rel_rmse(pred[walk], rec.bend[walk]),
            "E_late": rel_rmse(pred[late], rec.bend[late]),
            "E_all_smoothed_150ms": rel_rmse_smoothed(pred, rec.bend, 9),
            "E_coarse16_all": coarse_rel_rmse(pred, rec.bend, rec.pos, 16, tp.extent),
            "E_coarse16_late": coarse_rel_rmse(pred[late], rec.bend[late], rec.pos, 16, tp.extent),
            "coarse16_late_corr": coarse_corr(pred[late], rec.bend[late], rec.pos, 16, tp.extent),
            "trail_iou_16": trail_iou(pred[late], rec.bend[late], rec.pos, 16, tp.extent),
        },
        "history": history,
    }

    # 6. ablation: error/cost of each prefix of the discovered model (Pareto sketch)
    pareto = []
    for h in history:
        pareto.append({"terms": h["terms"], "E_all_fit": h["E_all"], "E_late_fit": h["E_late"], "cost": h["cost"]})
    report["pareto"] = pareto

    # 7. coarse-field bake: cost independent of token count, but blurs narrow features
    bake = {}
    for grid in (16, 32, 64):
        s, c = bake_and_sample(model, rec.pos, rec.times, grid, tp.extent, events, ptoken, path)
        bake[str(grid)] = {"E_all": rel_rmse(s, rec.bend), "E_late": rel_rmse(s[late], rec.bend[late]),
                           "E_coarse16_late": coarse_rel_rmse(s[late], rec.bend[late], rec.pos, 16, tp.extent),
                           "ops_per_stalk_frame": c}
    report["field_bake"] = bake

    # 8. single-primitive baselines (what each piece of the grammar can do alone)
    solo = {}
    from reactive.model import CheapModel, make_term  # noqa: E402
    for name in ("presence", "radial_impulse", "ring_wave", "wake", "crush"):
        m = CheapModel([make_term(name)])
        optimise(m, obj, maxfev=300)
        p_all, c_all = m.evaluate(g_all, rec.times)
        solo[name] = {"E_all": rel_rmse(p_all, rec.bend), "E_late": rel_rmse(p_all[late], rec.bend[late]),
                      "cost": c_all, "params": m.describe().strip()}
    report["solo"] = solo

    (out / "summary.json").write_text(json.dumps(report, indent=2))
    np.savez_compressed(out / "trajectories.npz", times=rec.times, pos=rec.pos, teacher=rec.bend,
                        cheap=pred, player=rec.player)
    write_markdown(report, out / "summary.md")
    try:
        make_figure(rec, pred, path, out / "comparison.png")
    except Exception as exc:  # matplotlib optional
        print(f"(figure skipped: {exc})")
    print(json.dumps(report["errors"], indent=2))
    print(f"wrote {out}")


def write_markdown(r: dict, path: Path) -> None:
    e = r["errors"]
    lines = [
        "# Experiment summary", "",
        f"Teacher: {r['teacher']['stalks']} stalks, {r['teacher']['frames']} frames, "
        f"~{r['teacher']['ops_per_stalk_frame']:.0f} ops/stalk/frame (stateful, neighbour-coupled, substepped).", "",
        f"Banked causes: {r['tokens']['events']} events + {r['tokens']['path_points']}-point path = "
        f"{r['tokens']['floats']} floats (vs {r['tokens']['per_stalk_state_floats']} floats of per-stalk state).", "",
        "## Discovered model", "", "```", r["model"]["description"], "```", "",
        f"Cost ~{r['model']['ops_per_stalk_frame']:.0f} ops/stalk/frame (stateless, no neighbour reads).", "",
        "## Errors (relative RMS vs teacher, all stalks, all frames)", "",
        "| metric | value |", "|---|---|",
        f"| E_all | {e['E_all']:.3f} |", f"| E_walk (player moving) | {e['E_walk']:.3f} |",
        f"| E_late (persistence phase) | {e['E_late']:.3f} |",
        f"| E_all after 150 ms temporal smoothing | {e['E_all_smoothed_150ms']:.3f} |",
        f"| E on 16x16 coarse field, all frames | {e['E_coarse16_all']:.3f} |",
        f"| E on 16x16 coarse field, persistence phase | {e['E_coarse16_late']:.3f} |",
        f"| correlation of late coarse fields (AI trail query) | {e['coarse16_late_corr']:.3f} |",
        f"| trail IoU on 16x16 query (25% of max threshold) | {e['trail_iou_16']:.3f} |", "",
        "## Greedy search path (fit subset)", "",
        "| terms | E_all | E_late | cost |", "|---|---|---|---|",
    ]
    for h in r["pareto"]:
        lines.append(f"| {' + '.join(h['terms']) or '(none)'} | {h['E_all_fit']:.3f} | {h['E_late_fit']:.3f} | {h['cost']:.0f} |")
    lines += ["", "## Single-primitive baselines", "", "| primitive | E_all | E_late | cost |", "|---|---|---|---|"]
    for k, v in r["solo"].items():
        lines.append(f"| {k} | {v['E_all']:.3f} | {v['E_late']:.3f} | {v['cost']:.0f} |")
    lines += ["", "## Coarse-field bake (Level 1) instead of direct token evaluation", "",
              "| grid | E_all | E_late | E coarse16 late | ops/stalk/frame |", "|---|---|---|---|---|"]
    for k, v in r["field_bake"].items():
        lines.append(f"| {k}x{k} | {v['E_all']:.3f} | {v['E_late']:.3f} | {v['E_coarse16_late']:.3f} | {v['ops_per_stalk_frame']:.0f} |")
    path.write_text("\n".join(lines) + "\n")


def make_figure(rec, pred, path, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    frames = [int(len(rec.times) * f) for f in (0.3, 0.55, 0.95)]
    fig, axes = plt.subplots(2, len(frames), figsize=(4.2 * len(frames), 8.2))
    vmax = np.linalg.norm(rec.bend, axis=-1).max()
    nx = int(np.sqrt(rec.pos.shape[0]))
    for col, f in enumerate(frames):
        for row, (name, b) in enumerate((("teacher", rec.bend[f]), ("cheap model", pred[f]))):
            ax = axes[row, col]
            mag = np.linalg.norm(b, axis=-1).reshape(nx, nx)
            ax.imshow(mag, origin="lower", extent=(0, rec.params.extent, 0, rec.params.extent),
                      vmin=0, vmax=vmax, cmap="viridis")
            step = max(1, nx // 20)
            P = rec.pos.reshape(nx, nx, 2)[::step, ::step].reshape(-1, 2)
            B = b.reshape(nx, nx, 2)[::step, ::step].reshape(-1, 2)
            ax.quiver(P[:, 0], P[:, 1], B[:, 0], B[:, 1], color="w", scale=6, width=0.004)
            ax.plot(*path.points.T, "r--", lw=0.8, alpha=0.6)
            ax.plot(*rec.player[f], "ro", ms=5)
            ax.set_title(f"{name}  t={rec.times[f]:.1f}s")
            ax.set_xticks([])
            ax.set_yticks([])
    fig.suptitle("|bend| (colour) and bend direction (arrows): expensive teacher vs discovered cheap model")
    fig.tight_layout()
    fig.savefig(out, dpi=110)


if __name__ == "__main__":
    main()
