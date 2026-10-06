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
# iteration 7 (docs/gait3d-feasibility.md): a gait clock in the cost. Each foot follows a half-wave
# height reference, the two half a cycle apart, and each shoulder a swing against its own leg on the
# same clock. The earlier teacher had no gait prior and shuffled with the hips nearly in phase; the
# web viewer showed that gait for what it was. Bodies without a foot have no foot term.
GAIT_FREQ = 1.0      # Hz, one full cycle (two steps)
GAIT_LIFT = 0.08     # m, peak foot height in swing, above the standing height of the foot site
GAIT_ARM = 0.35      # rad, shoulder swing amplitude
W_GAIT, W_ARM = 0.0, 0.0        # 7a to 7c: the clock on the feet and shoulders alone did not track
# iteration 7d: the prior as a full reference. Every present joint tracks a clean walk from the
# grammar's own clock (poc/gait3d/grammar3d.GaitState defaults at REF_FREQ), and physics does the rest.
W_TRACK = 5.0         # 7e tried 20 and walked sideways; 7f back to 5
REF_FREQ = 1.0
SCRIPT_ARMS = True    # 7e: on a body with legs the arm actuators follow the reference directly; the sampler plans the rest
REF_CENTRED = True    # 7g: sample around the reference at the current clock plus the last deviation, not around the last plan
SIGMA_LATERAL = 0.12  # 7g: noise on hip abduction and ankle roll


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
        self.feet = [s_ for s_ in "lr" if f"foot_pos_{s_}" in self.si]
        self.foot_z0 = None
        self.arm_idx = {s_: self.si[f"q_shoulder_{s_}"][0] for s_ in "lr" if f"q_shoulder_{s_}" in self.si}
        self.t0 = 0.0
        self.ref = None; self.ref_joints = []
        # iteration 7h: the reference is a walk, and a body without a foot has nothing to track with it;
        # the legless body under the reference lay with its head on the floor (0.03 m/s). Where there is
        # no foot the planner is iteration 6's.
        if W_TRACK > 0 and self.feet:
            from .grammar3d import GaitState, Body, joint_angles
            from dataclasses import replace
            self.ref_state = replace(GaitState(), freq=REF_FREQ)
            self.ref_body = Body(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MODEL, 0).replace("biped3d_", "") if False else self._morph_of(m))
            self.ref_joints = [(n[2:], self.si[n][0]) for n in self.si if n.startswith("q_")]
            self._joint_angles = joint_angles
        self.scripted = {}
        self.dev = np.zeros((KNOTS, self.nu))                      # 7g: the deviation from the reference the last replan kept
        self.act_joint = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0]) for a in range(m.nu)]
        self.sigma = np.array([SIGMA_LATERAL if (j.startswith("hip_x") or j.startswith("ankle_x")) else SIGMA for j in self.act_joint])
        if SCRIPT_ARMS and self.feet:
            for a in range(m.nu):
                jname = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0])
                if jname.startswith("shoulder") or jname.startswith("elbow"):
                    self.scripted[a] = jname

    @staticmethod
    def _morph_of(m):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MODEL, 0) or ""
        return name.replace("biped3d_", "") if name.startswith("biped3d_") else "intact"

    def track_cost(self, sens):
        """Every present joint against the clean walk's angle at the same clock time."""
        tt = self.t0 + self.step_t
        q, _, _, _, _ = self._joint_angles(self.ref_state, self.ref_body, tt)
        c = 0.0
        for name, idx in self.ref_joints:
            if name in q:
                c = c + W_TRACK * (sens[:, :, idx] - q[name][None, :]) ** 2
        return c

    def _controls(self, knots):
        N = knots.shape[0]
        out = np.empty((N, self.nstep, self.nu))
        for j in range(self.nu):
            for i in range(N):
                out[i, :, j] = np.interp(self.step_t, self.knot_t, knots[i, :, j])
        return np.clip(out, self.lo, self.hi)

    def gait_cost(self, sens):
        """The clock terms: foot height against its half-wave reference, shoulder against its swing."""
        c = 0.0
        ph = 2 * np.pi * GAIT_FREQ * (self.t0 + self.step_t)[None, :]
        for s_ in self.feet:
            f, _ = self.si[f"foot_pos_{s_}"]; z = sens[:, :, f + 2] - self.foot_z0[s_]
            ref = GAIT_LIFT * np.maximum(0.0, np.sin(ph + (0.0 if s_ == "l" else np.pi)))
            c = c + W_GAIT * (z - ref) ** 2
        for s_, a in self.arm_idx.items():
            ref = GAIT_ARM * np.sin(ph + (np.pi if s_ == "l" else 0.0))          # against the same-side leg
            c = c + W_ARM * (sens[:, :, a] - ref) ** 2
        return c

    def cost(self, sens, ctrl):
        v, _ = self.si["torso_vel"]; vx = sens[:, :, v]; vy = sens[:, :, v + 1]
        u, _ = self.si["torso_up"]; ux = sens[:, :, u]; uy = sens[:, :, u + 1]
        f, _ = self.si["torso_fwd"]; fx = sens[:, :, f]; fy = sens[:, :, f + 1]
        h, _ = self.si["head_pos"]; head_z = sens[:, :, h + 2]
        q = sens[:, :, self.q_idx]
        c = (W_SPEED * (vx - SPEED_TARGET) ** 2 + W_LAT * vy ** 2 + W_UP * (ux ** 2 + uy ** 2) + W_HEADING * ((fx - 1.0) ** 2 + fy ** 2)
             + W_HEAD * (self.head_target - head_z) ** 2 + W_HEADLOW * np.maximum(0.0, HEAD_LOW - head_z) ** 2
             + W_POSE * (q ** 2).sum(2))
        if (W_GAIT > 0 or W_ARM > 0) and (self.feet or self.arm_idx):
            c = c + self.gait_cost(sens)
        if self.ref_joints:
            c = c + self.track_cost(sens)
        return c.sum(1)

    def plan(self, d, t0=0.0):
        self.t0 = t0
        if self.head_target is None:
            h, _ = self.si["head_pos"]
            mujoco.mj_forward(self.m, d)
            self.head_target = float(d.sensordata[h + 2])
            self.foot_z0 = {s_: float(d.sensordata[self.si[f"foot_pos_{s_}"][0] + 2]) for s_ in self.feet}
        state = np.empty(self.nstate)
        mujoco.mj_getState(self.m, d, state, mujoco.mjtState.mjSTATE_FULLPHYSICS)
        noise = self.rng.normal(0, 1.0, size=(N_SAMPLES, KNOTS, self.nu)) * self.sigma[None, None, :]
        noise[0] = 0.0
        if REF_CENTRED and self.ref_joints:
            qk, _, _, _, _ = self._joint_angles(self.ref_state, self.ref_body, self.t0 + self.knot_t)
            ref_knots = np.zeros((KNOTS, self.nu))
            for a, jname in enumerate(self.act_joint):
                if jname in qk: ref_knots[:, a] = qk[jname]
            nominal = np.clip(ref_knots + self.dev, self.lo, self.hi)
        else:
            ref_knots = None; nominal = self.knots
        knots = np.clip(nominal[None] + noise, self.lo, self.hi)
        ctrl = self._controls(knots)
        if self.scripted:
            qref, _, _, _, _ = self._joint_angles(self.ref_state, self.ref_body, self.t0 + self.step_t)
            for a, jname in self.scripted.items():
                ctrl[:, :, a] = np.clip(qref[jname][None, :], self.lo[a], self.hi[a])
        init = np.repeat(state[None], N_SAMPLES, 0)
        _, sens = rollout.rollout(self.m, self.datas, init, ctrl, nstep=self.nstep)
        c = self.cost(sens, ctrl)
        best = int(np.argmin(c))
        self.knots = knots[best]
        if ref_knots is not None:
            self.dev = self.knots - ref_knots
        u = self._controls(self.knots[None])[0]
        if self.scripted:
            for a, jname in self.scripted.items():
                u[:, a] = np.clip(qref[jname], self.lo[a], self.hi[a])
        return u, float(c[best])

    def shift(self):
        t = self.knot_t + CTRL_DT
        for j in range(self.nu):
            self.knots[:, j] = np.interp(t, self.knot_t, self.knots[:, j])
            self.dev[:, j] = np.interp(t, self.knot_t, self.dev[:, j])


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
        u, c = ps.plan(d, k * CTRL_DT)
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
