"""Predictive sampling: at every control step, sample action sequences around a nominal plan, roll
them all out in MuJoCo, keep the best, execute its first piece, shift. No learning, no gait prior:
the cost says move forward at a target speed without putting the head on the floor and without
wasting effort, and the body does whatever its remaining parts allow. The same cost for every
morphology is the point of the feasibility check.
"""
from __future__ import annotations
import time
import numpy as np
import mujoco
from mujoco import rollout
from .biped import sensor_index, SPEED_TARGET

HORIZON = 1.0        # s (iteration 5: 0.6 s let a legless body topple forward for the speed it gains
KNOTS = 8            #  before the crash costs anything; at 1.0 s the crash is inside the horizon)
N_SAMPLES = 160
N_ELITE = 1          # iteration 6: the nominal plan becomes the mean of the best N_ELITE samples (a
                     # cross-entropy update) instead of the single best; predictive sampling is N_ELITE = 1
SIGMA = 0.35
CTRL_DT = 0.02       # s between replans
# iteration 2 (docs/gait-feasibility.md): iteration 1's cost let every body flop forward and drag
# itself head-first, so the head term is now "keep the head as high as this body can hold it", the
# target being the head height of the body's own initial upright pose, plus a heavy penalty on the
# head near the floor, and the pitch penalty is stronger.
W_SPEED, W_PITCH, W_HEAD, W_HEADLOW, W_EFFORT = 5.0, 2.0, 3.0, 50.0, 0.0
W_POSE = 0.1         # iteration 3: joints near straight unless bending pays; actions are target angles
HEAD_LOW = 0.25      # m: the head below this is penalised heavily


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
        self.head_target = None      # set from the initial pose on the first plan
        self.lo = m.actuator_ctrlrange[:, 0].copy(); self.hi = m.actuator_ctrlrange[:, 1].copy()
        self.q_idx = [self.si[n][0] for n in self.si if n.startswith("q_")]

    def _controls(self, knots):
        """(N, nstep, nu) piecewise-linear controls from (N, KNOTS, nu) knots."""
        N = knots.shape[0]
        out = np.empty((N, self.nstep, self.nu))
        for j in range(self.nu):
            for i in range(N):
                out[i, :, j] = np.interp(self.step_t, self.knot_t, knots[i, :, j])
        return np.clip(out, self.lo, self.hi)

    def cost(self, sens, ctrl):
        """(N,) summed cost over the horizon from sensordata (N, nstep, nsens)."""
        a, _ = self.si["torso_vel"]; vx = sens[:, :, a]
        p, _ = self.si["pitch"]; pitch = sens[:, :, p]
        h, _ = self.si["head_pos"]; head_z = sens[:, :, h + 2]
        q = sens[:, :, self.q_idx]
        c = (W_SPEED * (vx - SPEED_TARGET) ** 2 + W_PITCH * pitch ** 2
             + W_HEAD * (self.head_target - head_z) ** 2 + W_HEADLOW * np.maximum(0.0, HEAD_LOW - head_z) ** 2
             + W_POSE * (q ** 2).sum(2))
        c = c.sum(1) + W_EFFORT * (ctrl ** 2).sum((1, 2))
        return c

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
        elite = np.argsort(c)[:N_ELITE]
        self.knots = knots[elite].mean(0)
        u = self._controls(self.knots[None])[0]
        return u, float(c[elite[0]])

    def shift(self):
        """Move the nominal plan forward by one control interval."""
        t = self.knot_t + CTRL_DT
        for j in range(self.nu):
            self.knots[:, j] = np.interp(t, self.knot_t, self.knots[:, j])


TRACKED = ("foot_l", "foot_r", "hand_l", "hand_r", "thigh_l", "thigh_r", "shank_l", "shank_r", "torso", "pelvis", "head")


def floor_contacts(m, d, floor_id, geom_ids):
    """Which tracked geoms touch the floor at this step, from the contact list (a touch sensor also
    counts self-contact, which iteration 3 showed: hands brushing the torso read as stance)."""
    out = np.zeros(len(geom_ids), bool)
    for i in range(d.ncon):
        c = d.contact[i]
        other = c.geom2 if c.geom1 == floor_id else (c.geom1 if c.geom2 == floor_id else -1)
        if other >= 0 and other in geom_ids:
            out[geom_ids.index(other)] = True
    return out


def run(m, d, duration, seed=0, log=None):
    """Closed loop: plan, execute CTRL_DT, repeat. Returns per-physics-step sensordata, per-control-step
    qpos, the controls applied, the plan costs, and per-physics-step floor contacts of TRACKED geoms
    (columns in the order of the returned name list)."""
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
            log(f"    t={k*CTRL_DT:.2f}s x={d.qpos[0]:.2f} z={d.qpos[1]:.2f} cost {c:.1f} [{time.time()-T0:.0f}s]")
    return np.array(sens_log), np.array(qpos_log), np.array(ctrl_log), np.array(cost_log), (names, np.array(con_log))
