"""Predictive sampling for the 3D biped: poc/gait/mpc.py's sampler with a cost that reads the torso's
up and forward axes instead of a planar pitch. One cost for every morphology:

  speed toward SPEED_TARGET along x, lateral velocity toward zero, torso upright (its z axis
  vertical), heading along x (its x axis with no y component), the head as high as the body's own
  initial pose holds it, a heavy penalty on the head near the floor, and a small pose term.
"""
from __future__ import annotations
import time
import numpy as np
import mujoco
from mujoco import rollout
from .biped3d import sensor_index, SPEED_TARGET

HORIZON = 1.0
KNOTS = 8
N_SAMPLES = 160
SIGMA = 0.35
CTRL_DT = 0.02
# iteration 5 (docs/gait3d-feasibility.md): the heading term was fy^2 alone, which let the one-leg body hop
# facing backwards for free; it is now the distance of the torso's forward axis from +x
# iteration 2 (docs/gait3d-feasibility.md): head weight 3 let the body settle on its knees; at 20 it walks
# iteration 4: at 20 the weak hip and the stump end on their knees; at 40 they stay up
W_SPEED, W_LAT, W_UP, W_HEAD, W_HEADLOW, W_HEADING, W_POSE = 5.0, 2.0, 4.0, 40.0, 50.0, 1.0, 0.1
HEAD_LOW = 0.25


class PredictiveSampler:
    def __init__(self, m, seed=0, n_threads=4):
        self.m = m
        self.rng = np.random.default_rng(seed)
        self.datas = [mujoco.MjData(m) for _ in range(n_threads)]
        self.nstep = int(round(HORIZON / m.opt.timestep))
        self.nu = m.nu
        self.knots = np.zeros((KNOTS, self.nu))
        self.si = sensor_index(m)
        self.nstate = mujoco.mj_stateSize(m, mujoco.mjtState.mjSTATE_FULLPHYSICS)
        self.knot_t = np.linspace(0, HORIZON, KNOTS)
        self.step_t = np.arange(self.nstep) * m.opt.timestep
        self.head_target = None
        self.lo = m.actuator_ctrlrange[:, 0].copy(); self.hi = m.actuator_ctrlrange[:, 1].copy()
        self.q_idx = [self.si[n][0] for n in self.si if n.startswith("q_")]

    def _controls(self, knots):
        N = knots.shape[0]
        out = np.empty((N, self.nstep, self.nu))
        for j in range(self.nu):
            for i in range(N):
                out[i, :, j] = np.interp(self.step_t, self.knot_t, knots[i, :, j])
        return np.clip(out, self.lo, self.hi)

    def cost(self, sens, ctrl):
        v, _ = self.si["torso_vel"]; vx = sens[:, :, v]; vy = sens[:, :, v + 1]
        u, _ = self.si["torso_up"]; ux = sens[:, :, u]; uy = sens[:, :, u + 1]
        f, _ = self.si["torso_fwd"]; fx = sens[:, :, f]; fy = sens[:, :, f + 1]
        h, _ = self.si["head_pos"]; head_z = sens[:, :, h + 2]
        q = sens[:, :, self.q_idx]
        c = (W_SPEED * (vx - SPEED_TARGET) ** 2 + W_LAT * vy ** 2 + W_UP * (ux ** 2 + uy ** 2) + W_HEADING * ((fx - 1.0) ** 2 + fy ** 2)
             + W_HEAD * (self.head_target - head_z) ** 2 + W_HEADLOW * np.maximum(0.0, HEAD_LOW - head_z) ** 2
             + W_POSE * (q ** 2).sum(2))
        return c.sum(1)

    def plan(self, d):
        if self.head_target is None:
            h, _ = self.si["head_pos"]
            mujoco.mj_forward(self.m, d)
            self.head_target = float(d.sensordata[h + 2])
        state = np.empty(self.nstate)
        mujoco.mj_getState(self.m, d, state, mujoco.mjtState.mjSTATE_FULLPHYSICS)
        noise = self.rng.normal(0, SIGMA, size=(N_SAMPLES, KNOTS, self.nu))
        noise[0] = 0.0
        knots = np.clip(self.knots[None] + noise, self.lo, self.hi)
        ctrl = self._controls(knots)
        init = np.repeat(state[None], N_SAMPLES, 0)
        _, sens = rollout.rollout(self.m, self.datas, init, ctrl, nstep=self.nstep)
        c = self.cost(sens, ctrl)
        best = int(np.argmin(c))
        self.knots = knots[best]
        u = self._controls(self.knots[None])[0]
        return u, float(c[best])

    def shift(self):
        t = self.knot_t + CTRL_DT
        for j in range(self.nu):
            self.knots[:, j] = np.interp(t, self.knot_t, self.knots[:, j])


TRACKED = ("foot_l", "foot_r", "hand_l", "hand_r", "thigh_l", "thigh_r", "shank_l", "shank_r", "torso", "pelvis", "head")


def floor_contacts(m, d, floor_id, geom_ids):
    out = np.zeros(len(geom_ids), bool)
    for i in range(d.ncon):
        c = d.contact[i]
        other = c.geom2 if c.geom1 == floor_id else (c.geom1 if c.geom2 == floor_id else -1)
        if other >= 0 and other in geom_ids:
            out[geom_ids.index(other)] = True
    return out


def run(m, d, duration, seed=0, log=None):
    ps = PredictiveSampler(m, seed)
    n_ctrl = int(round(CTRL_DT / m.opt.timestep))
    steps = int(round(duration / CTRL_DT))
    floor_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    names = [g for g in TRACKED if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, g) >= 0]
    gids = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in names]
    sens_log, qpos_log, ctrl_log, cost_log, con_log = [], [], [], [], []
    T0 = time.time()
    for k in range(steps):
        u, c = ps.plan(d)
        for i in range(n_ctrl):
            d.ctrl[:] = u[i]
            mujoco.mj_step(m, d)
            sens_log.append(d.sensordata.copy())
            con_log.append(floor_contacts(m, d, floor_id, gids))
        qpos_log.append(d.qpos.copy()); ctrl_log.append(u[:n_ctrl].copy()); cost_log.append(c)
        ps.shift()
        if log and (k % 25 == 0):
            log(f"    t={k*CTRL_DT:.2f}s x={d.qpos[0]:.2f} y={d.qpos[1]:.2f} z={d.qpos[2]:.2f} cost {c:.1f} [{time.time()-T0:.0f}s]")
    return np.array(sens_log), np.array(qpos_log), np.array(ctrl_log), np.array(cost_log), (names, np.array(con_log))
