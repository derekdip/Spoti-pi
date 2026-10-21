"""Why does the legless body not crawl? Four short runs of the nolegs body, three seconds each:
predictive sampling from the sitting start; the same from a prone start with the arms forward
(hands on the floor ahead of the head, a crawl-ready rest pose); the same without the pose term;
the same with twice the sampling noise. Diagnostic only."""
from __future__ import annotations
import sys, time
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import biped, mpc
from poc.gait.feasibility import metrics, strip

def prone_start(m, d):
    """Lay the body face down with the arms pointing ahead of the head, hands on the floor."""
    d.qpos[:] = 0
    d.qpos[2] = np.pi / 2                      # pitch: head forward
    mujoco.mj_forward(m, d)
    best = None
    hid = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, s) for s in ("hand_l", "hand_r")]
    for a in np.linspace(-np.pi, np.radians(60), 61):
        d.qpos[3] = d.qpos[5] = a; d.qpos[4] = d.qpos[6] = 0.0
        mujoco.mj_forward(m, d)
        x = d.site_xpos[hid[0]][0]
        if best is None or x > best[0]:
            best = (x, a)
    d.qpos[3] = d.qpos[5] = best[1]
    mujoco.mj_forward(m, d)
    # drop the body so the lowest geom sits on the floor
    lowest = min(d.geom_xpos[g][2] - m.geom_rbound[g] for g in range(m.ngeom) if m.geom_type[g] != mujoco.mjtGeom.mjGEOM_PLANE)
    d.qpos[1] -= lowest - 0.01
    d.qvel[:] = 0
    mujoco.mj_forward(m, d)

def run(label, start, pose_w, sigma, seconds=3.0):
    mpc.W_POSE, mpc.SIGMA = pose_w, sigma
    m, d = biped.make("nolegs")
    if start == "prone":
        prone_start(m, d)
    t0 = time.time()
    sens, qpos, ctrl, cost, contacts = mpc.run(m, d, seconds, seed=0)
    import poc.gait.feasibility as F
    F.SETTLE = 1.0
    met = metrics(m, sens, qpos, contacts)
    strip(m, qpos, f"poc/results/gait_probe_{label}.png", f"nolegs {label}: speed {met['speed']:.2f}")
    print(f"{label:<22} speed {met['speed']:.2f} torso z {met['torso_z']:.2f} head z {met['head_z']:.2f} pitch {met['pitch_abs']:.2f} "
          f"hands {met['hands_any']:.2f} pelvis {met['stance'].get('pelvis', 0):.2f} head-down {met['stance'].get('head', 0):.2f} [{time.time()-t0:.0f}s]", flush=True)

if __name__ == "__main__":
    run("sit_base", "sit", 0.1, 0.35)
    run("prone_armsfwd", "prone", 0.1, 0.35)
    run("sit_nopose", "sit", 0.0, 0.35)
    run("sit_sigma06", "sit", 0.1, 0.6)
