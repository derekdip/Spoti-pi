"""GPU-side questions for the shipped cornfield.

1. How few terms can we ship? Refit wake + presence only and score it on the
   training and held-out walks against the six-term model.
2. What cell size does a baked bend texture need at corn spacing? Sweep the
   Level-1 grid and report error and bake cost per cell.

Usage: python poc/gpu_sweep.py [--results poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout import evaluate, parse_model  # noqa: E402
from reactive.causes import bank_path, emit_stride_events, holdout_walk, s_curve_walk  # noqa: E402
from reactive.field import bake_and_sample  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.metrics import coarse_rel_rmse, rel_rmse  # noqa: E402
from reactive.model import CheapModel, make_term  # noqa: E402
from reactive.search import Objective, optimise  # noqa: E402
from reactive.teacher import TeacherParams, run_teacher  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.results)
    summary = json.loads((out / "summary.json").read_text())
    full = parse_model(summary["model"]["description"])
    tp = TeacherParams()
    train = s_curve_walk(t_total=tp.duration)
    test = holdout_walk(t_total=tp.duration)
    rec = run_teacher(train, tp)
    events = emit_stride_events(train, stride=0.5)
    ptoken = bank_path(train, hz=20.0)
    g_all = build_geometry(rec.pos, events, ptoken, train)
    late = rec.times >= train.t_walk + 1.0

    # ---- 1. two-term refit ----
    rng = np.random.default_rng(0)
    near = np.flatnonzero(g_all.path_dperp < 1.0)
    far = rng.choice(np.flatnonzero(g_all.path_dperp >= 1.0), size=60, replace=False)
    fit_stalks = np.sort(np.concatenate([near, far]))
    fit_frames = np.arange(0, len(rec.times), 2)
    g_fit = build_geometry(rec.pos[fit_stalks], events, ptoken, train)
    obj = Objective(g_fit, rec.times[fit_frames], rec.bend[fit_frames][:, fit_stalks], late[fit_frames])
    two = CheapModel([make_term("wake"), make_term("presence")])
    # warm start from the six-term fit
    for t in two.terms:
        src = next(s for s in full.terms if s.prim.name == t.prim.name)
        t.params.update(src.params)
    optimise(two, obj, maxfev=800)
    one = CheapModel([make_term("wake")])
    one.terms[0].params.update(two.terms[0].params)
    optimise(one, obj, maxfev=600)

    models = {"six terms (as discovered)": full, "wake + presence": two, "wake only": one}
    keys = ["E_all", "E_late", "E_coarse16_all", "E_coarse16_late", "coarse16_late_corr", "cost"]
    lines = ["# GPU sweep", "", "## How few terms to ship", "",
             "Scored on all 1600 stalks and all frames. Cost is ops per stalk per frame for direct token evaluation.", "",
             "| model | walk | " + " | ".join(keys) + " |", "|---|---|" + "---|" * len(keys)]
    report = {"terms": {}}
    for name, m in models.items():
        report["terms"][name] = {"description": m.describe()}
        for wname, path in (("training", train), ("held-out", test)):
            r = evaluate(m, path, tp)
            report["terms"][name][wname] = r
            lines.append(f"| {name} | {wname} | " + " | ".join(f"{r[k]:.3f}" for k in keys) + " |")
    lines += ["", "```", "wake + presence:", two.describe(), "wake only:", one.describe(), "```", ""]

    # ---- 2. bake resolution sweep ----
    lines += ["## Baked bend texture: cell size versus error", "",
              "Two-term model baked to a grid over the 10 m field each frame, then bilinearly sampled per stalk.",
              "Bake cost is per cell per frame; divide by your stalk count for the per-stalk share. Sampling adds ~12 ops per vertex (or per instance).", "",
              "| grid | cell (m) | E_all | E_late | E coarse16 late | bake ops per cell |", "|---|---|---|---|---|---|"]
    pred_direct, cost_direct = two.evaluate(g_all, rec.times)
    lines.append(f"| direct tokens | - | {rel_rmse(pred_direct, rec.bend):.3f} | {rel_rmse(pred_direct[late], rec.bend[late]):.3f} | "
                 f"{coarse_rel_rmse(pred_direct[late], rec.bend[late], rec.pos, 16, tp.extent):.3f} | {cost_direct:.0f} per stalk |")
    report["bake"] = {}
    for grid in (10, 16, 20, 25, 32, 40, 50, 64, 80):
        s, _ = bake_and_sample(two, rec.pos, rec.times, grid, tp.extent, events, ptoken, train)
        row = {"cell_m": tp.extent / grid, "E_all": rel_rmse(s, rec.bend), "E_late": rel_rmse(s[late], rec.bend[late]),
               "E_coarse16_late": coarse_rel_rmse(s[late], rec.bend[late], rec.pos, 16, tp.extent),
               "bake_ops_per_cell": cost_direct}
        report["bake"][str(grid)] = row
        lines.append(f"| {grid}x{grid} | {row['cell_m']:.2f} | {row['E_all']:.3f} | {row['E_late']:.3f} | "
                     f"{row['E_coarse16_late']:.3f} | {cost_direct:.0f} |")
    text = "\n".join(lines) + "\n"
    (out / "gpu_sweep.md").write_text(text)
    (out / "gpu_sweep.json").write_text(json.dumps(report, indent=2))
    print(text)


if __name__ == "__main__":
    main()
