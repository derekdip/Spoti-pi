"""Teacher against student in 3D: side and front views at the same instants, for one body and one
grammar state; and the per-joint pose error."""
from __future__ import annotations
import json, sys
from dataclasses import replace
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import grammar3d as G, rgre_gait3d as RG
from poc.gait3d.feasibility3d import _draw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def compare(case, st, path, title, n=6):
    m, d = case.body.m, case.body.d
    qt = case.q_teacher; qs = G.trajectory(st, case.body)
    idx = np.linspace(0, len(qt) - 1, n).astype(int)
    fig, axes = plt.subplots(4, n, figsize=(2.0 * n, 10.5))
    for r0, (q, lab) in enumerate(((qt, "teacher"), (qs, "student"))):
        for j, k in enumerate(idx):
            d.qpos[:] = q[k]; mujoco.mj_kinematics(m, d)
            for rr, view in ((0, "side"), (1, "front")):
                ax = axes[2 * r0 + rr, j]; _draw(ax, m, d, q[k, 0], q[k, 1], view)
                ax.axhline(0, color="0.6", lw=1); ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.05, 1.7); ax.set_aspect("equal"); ax.axis("off")
                if rr == 0: ax.set_title(f"{lab} {G.WINDOW[0] + k / G.FPS:.1f}s", fontsize=8)
    fig.suptitle(title, fontsize=10); fig.tight_layout(); fig.savefig(path, dpi=70); plt.close(fig)


def pose_breakdown(case, st):
    qt = case.q_teacher; qs = G.trajectory(st, case.body)
    return {n: float(np.sqrt(((qt[:, 7 + i] - qs[:, 7 + i]) ** 2).mean())) for i, n in enumerate(case.body.joints)}


if __name__ == "__main__":
    morph = sys.argv[1] if len(sys.argv) > 1 else "intact"
    st = RG.load_v0()
    case = RG.GaitCase(morph, 0)
    compare(case, st, f"poc/results/gait3d_compare_{morph}_v0.png", f"{morph}: teacher vs V0 grammar, error {case.error(st):.3f}")
    print("per-joint rms error (rad):", {k: round(v, 2) for k, v in pose_breakdown(case, st).items()})
    print("per consumer:", {k: round(v, 2) for k, v in case.per_consumer(st).items()})
