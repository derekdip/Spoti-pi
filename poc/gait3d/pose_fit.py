"""The runtime fit: a grammar state fitted to the teacher's motion directly, for the deployable
states. The consumer objective scores what a game reads (contacts, statistics, orientation); five
rounds of adding to it each fixed one thing a viewer saw and left the next (sliding, stepping back,
lunging), because a viewer reads the whole motion. This objective reads the whole motion as one
cycle: the teacher's frames are cut into cycles at a foot's touchdowns and averaged into one cycle of
sixteen phase bins, and so are the student's, and the two cycles are compared with the amplitude
kept (a frame-by-frame fit against an irregular teacher averaged its swings into a shuffle). Per
bin: every present joint's angle, each foot's position relative to the root (forward and up, the
stride and the lift), the root's height and up axis; and two scalars, the cycle duration and the
forward speed. All in their own units with fixed weights, no self-scaling. Every grammar
parameter is free (base and impairment), since the state is a deployable description and not a
name. Planted grounding with the support foot from the clock, as in the grammar.

  python3 poc/gait3d/pose_fit.py [morph ...]   ->  poc/results/gait3d_pose_{morph}.json, a picture each

The fit is differential evolution over all parameters, seeded from the consumer V0 where that helps.
Not preregistered: a design fit for the runtime, recorded in docs/gait3d-runtime.md."""
from __future__ import annotations
import json, sys, time
from dataclasses import asdict, replace, fields
from pathlib import Path
import numpy as np
import mujoco
from scipy.optimize import differential_evolution
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, grammar3d as G, rgre_gait3d as RG

W_JOINT, W_FOOT, W_ROOT_Z, W_UP, W_SPEED, W_CYCLE = 1.0, 3.0, 3.0, 1.0, 2.0, 1.0
NB = 16
PARAMS = [f.name for f in fields(G.GaitState)]


def cycle_profile(body, qs):
    """One cycle of the motion: per phase bin the joint angles, the feet's positions relative to the
    root (x forward, z up), the root height and up axis; and the mean cycle duration and speed."""
    m, d = body.m, body.d; T = len(qs)
    torso = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso")
    feet = [body.gid[g] for g in ("foot_l", "foot_r") if g in body.gid]
    parts = [body.gid[g] for g in body.contact_geoms]
    contact = np.zeros((T, len(parts))); fxz = np.zeros((T, 2 * len(feet))); up = np.zeros((T, 2)); z = qs[:, 2]
    for k in range(T):
        d.qpos[:] = qs[k]; mujoco.mj_kinematics(m, d)
        contact[k] = body.lowest(parts) <= RG.CONTACT_EPS
        R = d.xmat[torso].reshape(3, 3); up[k] = R[0, 2], R[1, 2]
        for i, g in enumerate(feet):
            fxz[k, 2 * i] = d.geom_xpos[g][0] - qs[k, 0]; fxz[k, 2 * i + 1] = d.geom_xpos[g][2]
    cyc = None
    for g in ("foot_l", "foot_r", "thigh_l", "thigh_r", "hand_l", "hand_r"):
        if g in body.gid:
            cyc = RG.cycles_from_contact(contact[:, body.contact_geoms.index(g)] > 0.5)
            if cyc: break
    if not cyc:
        cyc = RG.cycles(qs[:, body.jadr[next(n for n in ("hip_y_l", "hip_y_r", "shoulder_l") if n in body.jadr)]])
    series = np.concatenate([qs[:, 7:], fxz, z[:, None], up], 1)
    prof = RG.phase_mean(series, cyc, NB)
    dur = float(np.mean([(b - a) / G.FPS for a, b in cyc])); speed = float((qs[-1, 0] - qs[0, 0]) / ((T - 1) / G.FPS))
    nj = qs.shape[1] - 7
    return dict(joints=prof[:, :nj], feet=prof[:, nj:nj + 2 * len(feet)], z=prof[:, nj + 2 * len(feet)], up=prof[:, nj + 2 * len(feet) + 1:], dur=dur, speed=speed)


class PoseCase:
    def __init__(self, morph, seed=0):
        self.morph, self.seed = morph, seed
        self.body = G.Body(morph); self.q = RG.teacher_qpos(morph, seed)
        self.t = cycle_profile(self.body, self.q); self.evals = 0

    def terms(self, st: G.GaitState):
        p = cycle_profile(self.body, G.trajectory(st, self.body)); t = self.t; self.evals += 1
        rms = lambda a, b: float(np.sqrt(((a - b) ** 2).mean())) if a.size else 0.0
        return dict(joints=rms(p["joints"], t["joints"]), feet=rms(p["feet"], t["feet"]), z=rms(p["z"], t["z"]), up=rms(p["up"], t["up"]),
                    speed=abs(p["speed"] - t["speed"]), dur=abs(p["dur"] - t["dur"]), p_speed=p["speed"], p_dur=p["dur"])

    def error(self, st: G.GaitState):
        e = self.terms(st)
        return W_JOINT * e["joints"] + W_FOOT * e["feet"] + W_ROOT_Z * e["z"] + W_UP * e["up"] + W_SPEED * e["speed"] + W_CYCLE * e["dur"]

    def breakdown(self, st):
        e = self.terms(st)
        return dict(joint_rms=e["joints"], foot_rms=e["feet"], root_z_rms=e["z"], up_rms=e["up"], speed=e["p_speed"], teacher_speed=self.t["speed"], cycle=e["p_dur"], teacher_cycle=self.t["dur"])


def fit(case, seed=0, maxiter=60, popsize=8, x0=None):
    names = [p for p in PARAMS if not (p.endswith("_side") and False)]
    bounds = [G.RANGES[p] for p in names]
    def f(x):
        return case.error(replace(G.GaitState(), **{n: float(v) for n, v in zip(names, x)}))
    kw = dict(seed=seed, maxiter=maxiter, popsize=popsize, tol=1e-6, polish=False)
    if x0 is not None:
        kw["x0"] = np.clip([getattr(x0, n) for n in names], [b[0] for b in bounds], [b[1] for b in bounds])
    r = differential_evolution(f, bounds, **kw)
    st = replace(G.GaitState(), **{n: float(v) for n, v in zip(names, r.x)})
    return st, float(r.fun)


def main(morphs, seed=0):
    from poc.gait3d.compare3d import compare
    for morph in morphs:
        T0 = time.time(); case = PoseCase(morph, seed)
        v0 = RG.load_v0()
        st, e = fit(case, x0=v0)
        bd = case.breakdown(st)
        json.dump(dict(morph=morph, seed=seed, state=asdict(st), error=e, breakdown=bd, evals=case.evals, seconds=round(time.time() - T0)), open(f"poc/results/gait3d_pose_{morph}.json", "w"), indent=1)
        cc = RG.GaitCase(morph, seed)
        compare(cc, st, f"poc/results/gait3d_pose_{morph}.png", f"{morph}: teacher vs pose-fitted state, joint rms {bd['joint_rms']:.2f} rad, speed {bd['speed']:.2f} vs {bd['teacher_speed']:.2f} m/s")
        print(f"{morph}: pose error {e:.3f}, joint rms {bd['joint_rms']:.2f} rad, foot rms {bd['foot_rms']:.3f} m, speed {bd['speed']:.2f} (teacher {bd['teacher_speed']:.2f}), cycle {bd['cycle']:.2f} s (teacher {bd['teacher_cycle']:.2f}), consumer error {cc.error(st):.3f}, {case.evals} evals [{time.time()-T0:.0f}s]", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["intact"])
