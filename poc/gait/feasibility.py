"""Gait feasibility: does one objective give a walk, a limp, a hop and a crawl as legs are removed?
Criteria are written in docs/gait-feasibility.md before this runs. Output: poc/results/gait_feasibility.{json,log}
and one stick-figure strip per morphology under poc/results/gait_*.png."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import biped, mpc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DURATION = 5.0
SETTLE = 2.0        # metrics over [SETTLE, DURATION]
TAG = "iter5"       # output files carry the iteration; earlier iterations' files are kept beside them


def metrics(m, sens, qpos, contacts):
    """Contacts are with the floor only, from the contact list (see mpc.floor_contacts)."""
    si = biped.sensor_index(m)
    dt = m.opt.timestep
    lo = int(SETTLE / dt)
    S = sens[lo:]
    names, con = contacts; C = con[lo:]
    a, _ = si["torso_pos"]; v, _ = si["torso_vel"]; h, _ = si["head_pos"]; p, _ = si["pitch"]
    out = dict(speed=float(S[:, v].mean()), torso_z=float(S[:, a + 2].mean()), head_z=float(S[:, h + 2].mean()),
               pitch_abs=float(np.abs(S[:, p]).mean()), distance=float(sens[-1, a] - sens[0, a]))
    contact = {n: C[:, i] for i, n in enumerate(names)}
    out["stance"] = {k: float(c.mean()) for k, c in contact.items()}
    if "foot_l" in contact and "foot_r" in contact:
        l, r = contact["foot_l"], contact["foot_r"]
    elif "foot_r" in contact and "thigh_l" in contact and "shank_l" not in contact:      # the stump
        l, r = contact["thigh_l"], contact["foot_r"]
    else:
        l = r = None
    if l is not None:
        out["alternation"] = float((l ^ r).mean())
        out["double_support"] = float((l & r).mean())
        out["flight"] = float((~l & ~r).mean())
        out["stance_asymmetry"] = float(abs(l.mean() - r.mean()) / max(l.mean() + r.mean(), 1e-9))
    hands = [contact[k] for k in contact if k.startswith("hand")]
    out["hands_any"] = float(np.logical_or.reduce(hands).mean()) if hands else 0.0
    ground = [contact[k] for k in contact]
    out["no_contact"] = float((~np.logical_or.reduce(ground)).mean()) if ground else 0.0
    return out


def strip(m, qpos, path, title, n=8):
    d = mujoco.MjData(m)
    T = len(qpos); idx = np.linspace(int(SETTLE / mpc.CTRL_DT), T - 1, n).astype(int)
    fig, axes = plt.subplots(1, n, figsize=(2.2 * n, 3.2))
    for ax, k in zip(axes, idx):
        d.qpos[:] = qpos[k]; mujoco.mj_forward(m, d)
        cx = d.qpos[0]
        for g in range(m.ngeom):
            if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_PLANE:
                continue
            pos = d.geom_xpos[g]; R = d.geom_xmat[g].reshape(3, 3)
            if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_CAPSULE:
                ax_ = R[:, 2] * m.geom_size[g, 1]
                a, b = pos - ax_, pos + ax_
                ax.plot([a[0] - cx, b[0] - cx], [a[2], b[2]], lw=2 + 40 * m.geom_size[g, 0], color="k", solid_capstyle="round")
            elif m.geom_type[g] == mujoco.mjtGeom.mjGEOM_SPHERE:
                ax.add_patch(plt.Circle((pos[0] - cx, pos[2]), m.geom_size[g, 0], color="k"))
        ax.axhline(0, color="0.6", lw=1)
        ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.05, 1.7); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"{k * mpc.CTRL_DT:.1f}s", fontsize=9)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=90); plt.close(fig)


def main(morphs=biped.MORPHS, seed=0):
    out = {}
    lines = []
    def log(s):
        print(s, flush=True); lines.append(s)
    for morph in morphs:
        T0 = time.time()
        m, d = biped.make(morph)
        log(f"{morph}: nq {m.nq} nu {m.nu} mass {float(sum(m.body_mass)):.1f} kg")
        sens, qpos, ctrl, cost, contacts = mpc.run(m, d, DURATION, seed=seed, log=log)
        met = metrics(m, sens, qpos, contacts)
        np.save(f"poc/results/gait_{TAG}_{morph}_qpos.npy", qpos)
        met["seconds"] = round(time.time() - T0)
        met["mean_cost"] = float(cost[int(SETTLE / mpc.CTRL_DT):].mean())
        out[morph] = met
        strip(m, qpos, f"poc/results/gait_{TAG}_{morph}.png", f"{morph}: speed {met['speed']:.2f} m/s, torso z {met['torso_z']:.2f}")
        log(f"  {morph}: speed {met['speed']:.2f} m/s over {DURATION-SETTLE:.0f}s, torso z {met['torso_z']:.2f}, head z {met['head_z']:.2f}, |pitch| {met['pitch_abs']:.2f} rad, "
            f"stance {{{', '.join(f'{k} {v:.2f}' for k, v in met['stance'].items())}}}"
            + (f", alternation {met['alternation']:.2f}, asymmetry {met['stance_asymmetry']:.2f}" if "alternation" in met else "")
            + f", hands {met['hands_any']:.2f}, airborne {met['no_contact']:.2f} [{met['seconds']}s]")
        json.dump(out, open(f"poc/results/gait_{TAG}_feasibility.json", "w"), indent=1)
    Path(f"poc/results/gait_{TAG}_feasibility.log").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    ms = sys.argv[1].split(",") if len(sys.argv) > 1 else biped.MORPHS
    main(ms)
