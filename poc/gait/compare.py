"""Teacher against student: two rows of stick figures at the same instants, and the per-joint pose
error, for one body and one grammar state."""
from __future__ import annotations
import json, sys
from dataclasses import replace
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import grammar as G, rgre_gait as RG
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def draw(ax, m, d, cx):
    for g in range(m.ngeom):
        if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_PLANE: continue
        pos = d.geom_xpos[g]; R = d.geom_xmat[g].reshape(3, 3)
        if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_CAPSULE:
            ax_ = R[:, 2] * m.geom_size[g, 1]; a, b = pos - ax_, pos + ax_
            ax.plot([a[0] - cx, b[0] - cx], [a[2], b[2]], lw=2 + 40 * m.geom_size[g, 0], color="k", solid_capstyle="round")
        elif m.geom_type[g] == mujoco.mjtGeom.mjGEOM_SPHERE:
            ax.add_patch(plt.Circle((pos[0] - cx, pos[2]), m.geom_size[g, 0], color="k"))
        elif m.geom_type[g] == mujoco.mjtGeom.mjGEOM_BOX:
            h = m.geom_size[g]; c = [pos + R @ np.array([sx * h[0], 0, sz * h[2]]) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            ax.add_patch(plt.Polygon([(p[0] - cx, p[2]) for p in c], color="k"))
    ax.axhline(0, color="0.6", lw=1); ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.05, 1.7); ax.set_aspect("equal"); ax.axis("off")


def compare(case, st, path, title, n=8):
    m, d = case.body.m, case.body.d
    qt = case.q_teacher; qs = G.trajectory(st, case.body)
    idx = np.linspace(0, len(qt) - 1, n).astype(int)
    fig, axes = plt.subplots(2, n, figsize=(2.0 * n, 5.6))
    for row, (q, lab) in enumerate(((qt, "teacher"), (qs, "student"))):
        for ax, k in zip(axes[row], idx):
            d.qpos[:] = q[k]; mujoco.mj_kinematics(m, d); draw(ax, m, d, q[k, 0])
            ax.set_title(f"{lab} {G.WINDOW[0] + k / G.FPS:.1f}s", fontsize=8)
    fig.suptitle(title, fontsize=10); fig.tight_layout(); fig.savefig(path, dpi=80); plt.close(fig)


def pose_breakdown(case, st):
    qt = case.q_teacher; qs = G.trajectory(st, case.body)
    names = case.body.jnames[3:]
    return {n: float(np.sqrt(((qt[:, 3 + i] - qs[:, 3 + i]) ** 2).mean())) for i, n in enumerate(names)}


if __name__ == "__main__":
    morph = sys.argv[1] if len(sys.argv) > 1 else "intact"
    v0 = json.load(open("poc/results/gait_v0.json"))["state"]
    st = replace(G.GaitState(), **v0)
    case = RG.GaitCase(morph, 0)
    compare(case, st, f"poc/results/gait_compare_{morph}_v0.png", f"{morph}: teacher vs V0 grammar, error {case.error(st):.3f}")
    print("per-joint rms error (rad):", {k: round(v, 2) for k, v in pose_breakdown(case, st).items()})
    print("teacher root: speed", round(float(case.target['root'][0]), 3), "z bins", np.round(case.target['root'][1:7], 2), "pitch bins", np.round(case.target['root'][7:13], 2))
    print("student root: speed", round(float(case._consumers(st)['root'][0]), 3), "z bins", np.round(case._consumers(st)['root'][1:7], 2), "pitch bins", np.round(case._consumers(st)['root'][7:13], 2))
    print("teacher contact by part (mean):", {g: round(float(v), 2) for g, v in zip(case.body.contact_geoms, case.target['contact'].reshape(RG.BINS, -1).mean(0))})
    print("student contact by part (mean):", {g: round(float(v), 2) for g, v in zip(case.body.contact_geoms, case._consumers(st)['contact'].reshape(RG.BINS, -1).mean(0))})
