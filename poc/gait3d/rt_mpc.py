"""Can the predictive-sampling teacher itself run in real time? (docs/gait3d-distill.md, part 2)

The teacher (mpc3d.py) samples N_SAMPLES rollouts of HORIZON seconds every 20 ms tick. This sweeps smaller
planners on the intact body: fewer samples, a shorter horizon, and replanning only every `every` ticks (between
replans the last plan is played forward, as a game engine would while the planner runs). Each setting walks for
`seconds` and is scored as distill.py scores the student, plus the planner's wall time per 20 ms of simulated
time. Real time on this machine means at most 20 ms of planning per 20 ms simulated.

  python3 -m poc.gait3d.rt_mpc OUT.json [seconds]
"""
from __future__ import annotations
import json, sys, time
import numpy as np, mujoco
from . import biped3d, mpc3d

SETTINGS = [  # (samples, horizon s, replan every k ticks)
    (160, 1.0, 1), (64, 1.0, 1), (32, 1.0, 1), (64, 0.6, 1), (32, 0.6, 1), (16, 0.6, 1),
    (64, 1.0, 2), (32, 0.6, 2), (64, 1.0, 3), (32, 0.6, 3)]


def walk(samples, horizon, every, seconds, morph="intact", seed=0, plan_dt=None):
    """plan_dt: the planner simulates its samples on its own copy of the body with this timestep (the body
    itself keeps 2 ms); the plan's controls are held across the finer steps."""
    mpc3d.N_SAMPLES, mpc3d.HORIZON = samples, horizon
    m, d = biped3d.make(morph); mp = m
    if plan_dt: mp, _ = biped3d.make(morph); mp.opt.timestep = plan_dt
    ps = mpc3d.PredictiveSampler(mp, seed); rep = int(round(mp.opt.timestep / m.opt.timestep))
    n_ctrl = int(round(mpc3d.CTRL_DT / m.opt.timestep)); steps = int(round(seconds / mpc3d.CTRL_DT))
    head = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "head"); z0 = d.qpos[2]; x0 = d.qpos[0]; plan_s = 0.0; fell = None; u = None; k_plan = -1
    for k in range(steps):
        if k % every == 0:
            t0 = time.perf_counter(); u_full, _ = ps.plan(d, k * mpc3d.CTRL_DT); plan_s += time.perf_counter() - t0; k_plan = k
            if rep > 1: u_full = np.repeat(u_full, rep, 0)
        off = (k - k_plan) * n_ctrl; seg = u_full[off:off + n_ctrl] if off + n_ctrl <= len(u_full) else np.repeat(u_full[-1:], n_ctrl, 0)
        for i in range(n_ctrl): d.ctrl[:] = seg[i]; mujoco.mj_step(m, d)
        ps.shift()
        if d.qpos[2] < 0.5 * z0 or d.geom_xpos[head][2] < mpc3d.HEAD_LOW: fell = (k + 1) * mpc3d.CTRL_DT; break
    T = fell or steps * mpc3d.CTRL_DT
    return dict(samples=samples, horizon=horizon, every=every, plan_dt=mp.opt.timestep, survived=T, fell=fell is not None, speed=float((d.qpos[0] - x0) / T), drift=float(d.qpos[1]),
                plan_ms_per_tick=1000 * plan_s / (k + 1), realtime_factor=(1000 * plan_s / (k + 1)) / (1000 * mpc3d.CTRL_DT))


FOLLOW_UP = [(n, 1.0, k) for n in (32, 24, 16) for k in (2, 3, 4)]   # after the first sweep: the 1.0 s horizon held in all five tries, 0.6 s in none


COARSE = [(32, 1.0, 1, 0.004), (32, 1.0, 2, 0.004), (48, 1.0, 2, 0.004), (64, 1.0, 2, 0.004), (64, 1.0, 3, 0.004), (32, 1.0, 2, 0.005), (64, 1.0, 2, 0.005)]


def main(out, seconds=10.0, settings=None, seeds=(0,)):
    res = []
    for s in settings or SETTINGS:
      for seed in seeds:
        r = walk(*s[:3], seconds, seed=seed, plan_dt=s[3] if len(s) > 3 else None); r["seed"] = seed; res.append(r); json.dump(res, open(out, "w"), indent=1)
        print(f"seed {seed} samples {r['samples']:3d} horizon {r['horizon']:.1f}s every {r['every']} plan step {1000 * r['plan_dt']:.0f} ms: survived {r['survived']:.1f}s, speed {r['speed']:.2f} m/s, drift {r['drift']:+.2f}, "
              f"{r['plan_ms_per_tick']:.1f} ms planning per 20 ms ({r['realtime_factor']:.2f}x real time)", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["heading"]:   # the 48-sample walks all turned round and fell near 19 s; W_HEADING was 1.0
        res = []
        for w in (5.0, 10.0):
            mpc3d.W_HEADING = w
            for seed in (20, 21, 22):
                r = walk(48, 1.0, 2, 30.0, seed=seed, plan_dt=0.004); r.update(seed=seed, w_heading=w); res.append(r); json.dump(res, open(sys.argv[2], "w"), indent=1)
                print(f"heading weight {w}: seed {seed}: survived {r['survived']:.1f}s, speed {r['speed']:.2f}, drift {r['drift']:+.2f}, {r['realtime_factor']:.2f}x real time", flush=True)
        sys.exit()
    if sys.argv[1:2] == ["long"]: main(sys.argv[2], 30.0, [(48, 1.0, 2, 0.004), (32, 1.0, 1, 0.004)], (20, 21, 22, 23, 24)); sys.exit()
    if sys.argv[1:2] == ["coarse"]: main(sys.argv[2], 10.0, COARSE, (0, 1)); sys.exit()
    if sys.argv[1:2] == ["followup"]: main(sys.argv[2], 10.0, FOLLOW_UP, (0, 1))
    else: main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/rt_mpc.json", float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
