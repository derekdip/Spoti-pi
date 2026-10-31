"""3D gait feasibility: the 2D harness (poc/gait/feasibility.py) on the 3D body, with lateral drift,
roll and yaw added to the metrics. Criteria in docs/gait3d-feasibility.md, written before the run.
Output: poc/results/gait3d_{TAG}_feasibility.{json,log}, strips poc/results/gait3d_{TAG}_{morph}.png."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, mpc3d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DURATION = 5.0
SETTLE = 2.0
TAG = "iter1"


def metrics(m, sens, qpos, contacts):
    si = biped3d.sensor_index(m)
    dt = m.opt.timestep
    lo = int(SETTLE / dt)
    S = sens[lo:]
    names, con = contacts; C = con[lo:]
    a, _ = si["torso_pos"]; v, _ = si["torso_vel"]; h, _ = si["head_pos"]; u, _ = si["torso_up"]; f, _ = si["torso_fwd"]
    out = dict(speed=float(S[:, v].mean()), lateral_speed=float(np.abs(S[:, v + 1]).mean()), torso_z=float(S[:, a + 2].mean()), head_z=float(S[:, h + 2].mean()),
               tilt=float(np.arccos(np.clip(S[:, u + 2], -1, 1)).mean()), yaw=float(np.abs(np.arctan2(S[:, f + 1], S[:, f])).mean()),
               distance=float(sens[-1, a] - sens[0, a]), drift=float(sens[-1, a + 1] - sens[0, a + 1]))
    contact = {n: C[:, i] for i, n in enumerate(names)}
    out["stance"] = {k: float(c.mean()) for k, c in contact.items()}
    if "foot_l" in contact and "foot_r" in contact:
        l, r = contact["foot_l"], contact["foot_r"]
    elif "foot_r" in contact and "thigh_l" in contact and "shank_l" not in contact:
        l, r = contact["thigh_l"], contact["foot_r"]
    elif "foot_l" in contact and "thigh_r" in contact and "shank_r" not in contact:
        l, r = contact["foot_l"], contact["thigh_r"]
    else:
        l = r = None
    if l is not None:
        out["alternation"] = float((l ^ r).mean()); out["double_support"] = float((l & r).mean())
        out["flight"] = float((~l & ~r).mean()); out["stance_asymmetry"] = float(abs(l.mean() - r.mean()) / max(l.mean() + r.mean(), 1e-9))
    hands = [contact[k] for k in contact if k.startswith("hand")]
    out["hands_any"] = float(np.logical_or.reduce(hands).mean()) if hands else 0.0
    ground = [contact[k] for k in contact]
    out["no_contact"] = float((~np.logical_or.reduce(ground)).mean()) if ground else 0.0
    return out


def _draw(ax, m, d, cx, cy, view):
    """Side (x-z) or front (y-z) projection of every geom."""
    X = 0 if view == "side" else 1; c0 = cx if view == "side" else cy
    for g in range(m.ngeom):
        t = m.geom_type[g]
        if t == mujoco.mjtGeom.mjGEOM_PLANE: continue
        pos = d.geom_xpos[g]; R = d.geom_xmat[g].reshape(3, 3)
        if t == mujoco.mjtGeom.mjGEOM_CAPSULE:
            ax_ = R[:, 2] * m.geom_size[g, 1]; a, b = pos - ax_, pos + ax_
            ax.plot([a[X] - c0, b[X] - c0], [a[2], b[2]], lw=2 + 40 * m.geom_size[g, 0], color="k", solid_capstyle="round")
        elif t == mujoco.mjtGeom.mjGEOM_SPHERE:
            ax.add_patch(plt.Circle((pos[X] - c0, pos[2]), m.geom_size[g, 0], color="k"))
        elif t == mujoco.mjtGeom.mjGEOM_BOX:
            s = m.geom_size[g]
            corners = np.array([[sx, sy, sz] for sx in (-s[0], s[0]) for sy in (-s[1], s[1]) for sz in (-s[2], s[2])]) @ R.T + pos
            ax.fill(corners[:, X][[0, 1, 3, 2, 6, 7, 5, 4]] - c0, corners[:, 2][[0, 1, 3, 2, 6, 7, 5, 4]], color="0.3", alpha=0.6)


def strip(m, qpos, path, title, n=8):
    d = mujoco.MjData(m)
    T = len(qpos); idx = np.linspace(int(SETTLE / mpc3d.CTRL_DT), T - 1, n).astype(int)
    fig, axes = plt.subplots(2, n, figsize=(2.2 * n, 6.4))
    for j, k in enumerate(idx):
        d.qpos[:] = qpos[k]; mujoco.mj_forward(m, d)
        for row, view in ((0, "side"), (1, "front")):
            ax = axes[row, j]; _draw(ax, m, d, d.qpos[0], d.qpos[1], view)
            ax.axhline(0, color="0.6", lw=1); ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.05, 1.7); ax.set_aspect("equal"); ax.axis("off")
            if row == 0: ax.set_title(f"{k * mpc3d.CTRL_DT:.1f}s", fontsize=9)
    fig.suptitle(title, fontsize=10); fig.tight_layout(); fig.savefig(path, dpi=80); plt.close(fig)


def main(morphs, seed=0, tag=TAG, duration=DURATION):
    out = {}; lines = []
    def log(s):
        print(s, flush=True); lines.append(s)
    for morph in morphs:
        T0 = time.time()
        m, d = biped3d.make(morph)
        log(f"{morph}: nq {m.nq} nu {m.nu} mass {float(sum(m.body_mass)):.1f} kg")
        sens, qpos, ctrl, cost, contacts = mpc3d.run(m, d, duration, seed=seed, log=log)
        met = metrics(m, sens, qpos, contacts)
        np.save(f"poc/results/gait3d_{tag}_{morph}_qpos.npy", qpos)
        met["seconds"] = round(time.time() - T0); met["mean_cost"] = float(cost[int(SETTLE / mpc3d.CTRL_DT):].mean())
        out[morph] = met
        strip(m, qpos, f"poc/results/gait3d_{tag}_{morph}.png", f"{morph}: speed {met['speed']:.2f} m/s, torso z {met['torso_z']:.2f}, tilt {met['tilt']:.2f}")
        log(f"  {morph}: speed {met['speed']:.2f} m/s, lateral {met['lateral_speed']:.2f}, drift {met['drift']:.2f} m, torso z {met['torso_z']:.2f}, head z {met['head_z']:.2f}, tilt {met['tilt']:.2f} rad, yaw {met['yaw']:.2f}, "
            f"stance {{{', '.join(f'{k} {v:.2f}' for k, v in met['stance'].items() if v > 0)}}}"
            + (f", alternation {met['alternation']:.2f}, double {met['double_support']:.2f}, flight {met['flight']:.2f}, asymmetry {met['stance_asymmetry']:.2f}" if "alternation" in met else "")
            + f", hands {met['hands_any']:.2f}, airborne {met['no_contact']:.2f} [{met['seconds']}s]")
        json.dump(out, open(f"poc/results/gait3d_{tag}_feasibility.json", "w"), indent=1)
    Path(f"poc/results/gait3d_{tag}_feasibility.log").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    ms = sys.argv[1].split(",") if len(sys.argv) > 1 else biped3d.MORPHS
    tag = sys.argv[2] if len(sys.argv) > 2 else TAG
    dur = float(sys.argv[3]) if len(sys.argv) > 3 else DURATION
    main(ms, tag=tag, duration=dur)
