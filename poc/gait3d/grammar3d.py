"""The 3D gait grammar: poc/gait/grammar.py's phase clock on the free-rooted body, with a lateral
base class (sway, hip abduction, ankle roll) and torso roll, the root grounded on the lowest part
plus an explicit lift, the orientation from pitch and roll. Five base classes and five impairment
classes, each with parameters, a range, a canonical on-state; nothing fitted to any teacher here.

Carried from the 2D arc (docs/math-track-g6-results.md): the hop class is not here, being a
combination of base parameters; vault keeps only what the arm and torso base cannot do, a lift
at the arm cycle with its own phase; the class that holds one leg is named for what it does
(hold), not for kneeling, which the 3D stump does not do. Sided classes carry one signed side in
[-1, 1] as in 2D.

Sign conventions from the model: hinges about +y, so hip flexion (thigh forward) is negative and
knee flexion positive; hip_x about +x, so a positive left hip_x abducts the left leg and a positive
right hip_x adducts the right, which is why the lateral terms carry a side sign.
"""
from __future__ import annotations
from dataclasses import dataclass, fields, replace
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
from . import biped3d

FPS = 50.0
WINDOW = (1.0, 5.0)
SIDES = ("l", "r")
SGN = {"l": 1.0, "r": -1.0}


@dataclass(frozen=True)
class GaitState:
    # ---- rhythm
    freq: float = 1.2
    duty: float = 0.6
    phase0: float = 0.0
    phase_r: float = 3.1416
    # ---- legs (sagittal)
    hip_off: float = -0.15
    hip_amp: float = 0.35
    knee_off: float = 0.15
    knee_amp: float = 0.7
    knee_lag: float = 0.6
    ankle_amp: float = 0.2
    ankle_lag: float = 0.0
    # ---- lateral: the body sways over the stance leg, the hips abduct, the ankles roll
    sway_amp: float = 0.02       # m, root y at the cycle frequency
    sway_lag: float = 0.0
    abd_off: float = 0.0         # rad, hip abduction offset, both legs outward
    abd_amp: float = 0.05        # rad, abduction oscillation at the cycle frequency, per leg
    abd_lag: float = 0.0
    ankle_x_amp: float = 0.0     # rad, ankle roll oscillation, per leg, at the abduction phase
    # ---- torso
    lean: float = 0.05           # rad, pitch offset (positive forward); the range reaches the prone body
    pitch_amp: float = 0.0
    pitch_lag: float = 0.0
    bob_amp: float = 0.02        # m, vertical oscillation at twice the cycle
    roll_amp: float = 0.0        # rad, torso roll at the cycle frequency
    roll_lag: float = 0.0
    # ---- arms
    arm_amp: float = 0.3
    arm_lag: float = 3.1416
    arm_off: float = 0.0
    elbow_off: float = -0.3
    # ---- stiff leg
    stiff_side: float = 0.0
    stiff_knee: float = 1.0
    stiff_lift: float = 0.0
    # ---- short-leg limp, as 2D: the side is the short side, the terms act on the long side
    limp_side: float = 0.0
    limp_lift: float = 0.0
    limp_sink: float = 0.0
    limp_duty: float = 0.0
    # ---- one leg held: that side's hip at an offset with its own small swing. (The first draft also
    # bent the other knee, which is limp's sink term on the same side; the exclusivity table put limp
    # absorbing hold at 0.56 and it was removed before the freeze. Likewise limp's hitch, a half-wave
    # lift during the long side's stance, was vault's lift at a lag, absorption 0.98, and is gone.)
    hold_side: float = 0.0
    hold_hip: float = 0.0
    hold_amp: float = 0.0
    # ---- arm vault: a lift at the arm cycle with its own phase (what the arm and torso base cannot do)
    vault_lift: float = 0.0
    vault_lag: float = 0.0
    # ---- weak hip: that side's swing scaled and delayed, and the torso rolls during its stance
    weak_side: float = 0.0
    weak_scale: float = 1.0
    weak_lag: float = 0.0
    weak_roll: float = 0.0

    def cost(self):
        return sum(1 for f in fields(self) if getattr(self, f.name) != f.default)


CLASSES = {
    "rhythm":  ["freq", "duty", "phase0", "phase_r"],
    "legs":    ["hip_off", "hip_amp", "knee_off", "knee_amp", "knee_lag", "ankle_amp", "ankle_lag"],
    "lateral": ["sway_amp", "sway_lag", "abd_off", "abd_amp", "abd_lag", "ankle_x_amp"],
    "torso":   ["lean", "pitch_amp", "pitch_lag", "bob_amp", "roll_amp", "roll_lag"],
    "arms":    ["arm_amp", "arm_lag", "arm_off", "elbow_off"],
    "stiff": ["stiff_side", "stiff_knee", "stiff_lift"],
    "limp":  ["limp_side", "limp_lift", "limp_sink", "limp_duty"],
    "hold":  ["hold_side", "hold_hip", "hold_amp"],
    "vault": ["vault_lift", "vault_lag"],
    "weak":  ["weak_side", "weak_scale", "weak_lag", "weak_roll"],
}
V0_CLASSES = ("rhythm", "legs", "lateral", "torso", "arms")
BASE_PARAMS = [p for c in V0_CLASSES for p in CLASSES[c]]
IMPAIRMENTS = ("stiff", "limp", "hold", "vault", "weak")
SIDED = ("stiff", "limp", "hold", "weak")

RANGES = {
    "freq": (0.4, 3.0), "duty": (0.3, 0.85), "phase0": (-3.2, 3.2), "phase_r": (0.0, 6.3),
    "hip_off": (-1.2, 0.4), "hip_amp": (0.0, 1.0), "knee_off": (0.0, 1.5), "knee_amp": (0.0, 1.8), "knee_lag": (-3.2, 3.2), "ankle_amp": (0.0, 0.7), "ankle_lag": (-3.2, 3.2),
    "sway_amp": (0.0, 0.1), "sway_lag": (-3.2, 3.2), "abd_off": (-0.3, 0.3), "abd_amp": (0.0, 0.3), "abd_lag": (-3.2, 3.2), "ankle_x_amp": (0.0, 0.3),
    "lean": (-0.5, 2.0), "pitch_amp": (0.0, 0.5), "pitch_lag": (-3.2, 3.2), "bob_amp": (0.0, 0.1), "roll_amp": (0.0, 0.4), "roll_lag": (-3.2, 3.2),
    "arm_amp": (0.0, 1.5), "arm_lag": (-3.2, 3.2), "arm_off": (-2.5, 0.8), "elbow_off": (-2.4, 0.0),
    "stiff_side": (-1.0, 1.0), "stiff_knee": (0.0, 1.0), "stiff_lift": (0.0, 0.6),
    "limp_side": (-1.0, 1.0), "limp_lift": (0.0, 1.0), "limp_sink": (0.0, 0.8), "limp_duty": (0.0, 0.35),
    "hold_side": (-1.0, 1.0), "hold_hip": (-1.0, 0.5), "hold_amp": (0.0, 0.8),
    "vault_lift": (0.0, 0.3), "vault_lag": (-3.2, 3.2),
    "weak_side": (-1.0, 1.0), "weak_scale": (0.0, 1.0), "weak_lag": (-1.5, 1.5), "weak_roll": (-0.4, 0.4),
}
ON = {
    "stiff": {"stiff_side": -1.0, "stiff_knee": 0.1, "stiff_lift": 0.15},
    "limp":  {"limp_side": -1.0, "limp_lift": 0.4, "limp_sink": 0.3, "limp_duty": 0.12},
    "hold":  {"hold_side": -1.0, "hold_hip": -0.4, "hold_amp": 0.2},
    "vault": {"vault_lift": 0.05, "vault_lag": 0.0},
    "weak":  {"weak_side": -1.0, "weak_scale": 0.6, "weak_lag": 0.3, "weak_roll": 0.1},
}
EPS = {p: 0.04 * (hi - lo) for p, (lo, hi) in RANGES.items()}


def is_on(st: GaitState, cls):
    return cls in V0_CLASSES or any(getattr(st, p) != getattr(GaitState(), p) for p in CLASSES[cls])


def turn_on(st: GaitState, cls):
    return replace(st, **ON[cls]) if cls in ON and not is_on(st, cls) else st


def side_sign(st: GaitState, cls):
    if cls not in SIDED:
        return 0
    v = getattr(st, f"{cls}_side")
    return -1 if v < 0 else (1 if v > 0 else 0)


def _w(side, s):
    return max(0.0, -side) if s == "l" else max(0.0, side)


class Body:
    def __init__(self, morph):
        self.morph = morph
        self.m = mujoco.MjModel.from_xml_string(biped3d.build_xml(morph))
        self.d = mujoco.MjData(self.m)
        self.jnames = [mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(self.m.njnt)]
        self.jadr = {n: int(self.m.jnt_qposadr[j]) for j, n in enumerate(self.jnames)}
        self.joints = [n for n in self.jnames if n != "root"]          # in qpos order from index 7
        self.has = {n: (n in self.jadr) for n in [f"{j}_{s}" for s in SIDES for j in biped3d.LEG_JOINTS]}
        self.contact_geoms = [g for g in ("foot_l", "foot_r", "thigh_l", "thigh_r", "hand_l", "hand_r", "pelvis")
                              if mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_GEOM, g) >= 0]
        self.gid = {g: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in self.contact_geoms}
        self.all_gids = [g for g in range(self.m.ngeom) if self.m.geom_type[g] != mujoco.mjtGeom.mjGEOM_PLANE]

    def lowest(self, gids):
        m, d = self.m, self.d
        out = np.empty(len(gids))
        for i, g in enumerate(gids):
            pos = d.geom_xpos[g]; R = d.geom_xmat[g].reshape(3, 3); t = m.geom_type[g]
            if t == mujoco.mjtGeom.mjGEOM_CAPSULE:
                ax = R[:, 2] * m.geom_size[g, 1]
                out[i] = min(pos[2] - ax[2], pos[2] + ax[2]) - m.geom_size[g, 0]
            elif t == mujoco.mjtGeom.mjGEOM_SPHERE:
                out[i] = pos[2] - m.geom_size[g, 0]
            elif t == mujoco.mjtGeom.mjGEOM_BOX:
                h = m.geom_size[g]
                out[i] = pos[2] - (abs(R[2, 0]) * h[0] + abs(R[2, 1]) * h[1] + abs(R[2, 2]) * h[2])
            else:
                out[i] = pos[2] - m.geom_rbound[g]
        return out


def warp(phi, duty):
    x = np.mod(phi, 2 * np.pi) / (2 * np.pi)
    return np.where(x < duty, x / duty * np.pi, np.pi + (x - duty) / (1.0 - duty) * np.pi)


def stance_phase(st: GaitState, t):
    """Whether each side is in the grammar's stance half of its cycle at times t (the warped phase in
    [0, pi)), with the same lag and duty terms joint_angles uses. Bodies without a leg on a side
    still get a value; the caller ignores sides that have no foot."""
    phi_l = st.phase0 + 2 * np.pi * st.freq * t
    phi = {"l": phi_l, "r": phi_l + st.phase_r}
    out = {}
    for s in SIDES:
        w_limp, w_weak = _w(st.limp_side, s), _w(st.weak_side, s)
        u = warp(phi[s] - st.weak_lag * w_weak, st.duty - st.limp_duty * w_limp)
        out[s] = u < np.pi
    return out


def joint_angles(st: GaitState, body: Body, t):
    """Every present joint's angle over the time grid, the root's pitch, roll, lateral offset and lift."""
    phi_l = st.phase0 + 2 * np.pi * st.freq * t
    phi = {"l": phi_l, "r": phi_l + st.phase_r}
    q = {}
    for s in SIDES:
        o = "r" if s == "l" else "l"
        w_stiff, w_limp, w_hold, w_weak = (_w(st.stiff_side, s), _w(st.limp_side, s), _w(st.hold_side, s), _w(st.weak_side, s))
        w_limp_o = _w(st.limp_side, o)
        scale = 1.0 - (1.0 - st.weak_scale) * w_weak
        lag = st.weak_lag * w_weak
        u = warp(phi[s] - lag, st.duty - st.limp_duty * w_limp)
        hip_amp = st.hip_amp * scale * (1.0 - w_hold) + st.stiff_lift * w_stiff + st.hold_amp * w_hold
        hip = st.hip_off + st.hold_hip * w_hold - hip_amp * np.cos(u)
        swing = np.maximum(0.0, -np.sin(u + st.knee_lag))
        knee_scale = 1.0 - (1.0 - st.stiff_knee) * w_stiff
        knee = st.knee_off + st.limp_sink * w_limp_o + (st.knee_amp * knee_scale + st.limp_lift * w_limp_o) * swing
        ankle = st.ankle_amp * np.sin(u + st.ankle_lag)
        abd = SGN[s] * (st.abd_off + st.abd_amp * np.sin(phi[s] + st.abd_lag))
        q[f"hip_x_{s}"] = abd; q[f"hip_y_{s}"] = hip; q[f"knee_{s}"] = knee
        q[f"ankle_y_{s}"] = ankle; q[f"ankle_x_{s}"] = SGN[s] * st.ankle_x_amp * np.sin(phi[s] + st.abd_lag)
        q[f"shoulder_{s}"] = st.arm_off + st.arm_amp * np.sin(phi[s] + st.arm_lag)
        q[f"elbow_{s}"] = np.full_like(t, st.elbow_off)
    pitch = st.lean + st.pitch_amp * np.sin(2 * phi_l + st.pitch_lag)
    roll = st.roll_amp * np.sin(phi_l + st.roll_lag) + st.weak_roll * (_w(st.weak_side, "l") * np.maximum(0.0, np.sin(phi["l"])) + _w(st.weak_side, "r") * np.maximum(0.0, np.sin(phi["r"])))
    lift = st.vault_lift * np.maximum(0.0, np.sin(phi_l + st.vault_lag)) + st.bob_amp * np.sin(2 * phi_l)
    y = st.sway_amp * np.sin(phi_l + st.sway_lag)
    return q, pitch, roll, y, lift


def quat_wxyz(roll, pitch):
    """Root orientation from roll about world x and pitch about world y, as MuJoCo's (w, x, y, z)."""
    r = Rotation.from_euler("xyz", np.stack([roll, pitch, np.zeros_like(roll)], 1))
    q = r.as_quat()                       # (x, y, z, w)
    return np.concatenate([q[:, 3:4], q[:, :3]], 1)


PLANT_EPS = 0.01     # m: a part this close to the floor after grounding is the planted one


class Ground:
    """The root's forward motion from the part that is on the floor, frame by frame: the support part
    is planted where it touched down and the root moves so that it does not slide; while nothing is
    down (a lift), the root keeps its last velocity. Speed is what the legs produce, not a parameter.
    (Before this, the root moved at a fitted speed and the stance foot skated under the body, which
    the consumers never measured and a viewer saw at once: docs/gait3d-runtime.md, G9.)

    Optional, off by default so the G9 to G11 states replay as scored: `stance` chooses the support
    among the feet the grammar's own clock has in stance (the G12 draft, docs/math-track-g12-prereg.md,
    not run: the fit under it lunged, docs/gait3d-runtime.md), `support_gid` names the part outright."""
    def __init__(self):
        self.x = 0.0; self.v = 0.0; self.planted = None; self.plant_x = 0.0

    def step(self, body: Body, dt: float, stance=None, support_gid=None):
        """Call with the body posed at root x = 0 (joints, orientation, y and z set). `stance` maps a
        side to whether the grammar has it in stance; `support_gid` names the support part outright
        (the cycle runtime, whose profile carries its own contact pattern). Returns root x."""
        m, d = body.m, body.d
        lows = body.lowest(body.all_gids); i = int(np.argmin(lows))
        if support_gid is not None and support_gid in body.all_gids:
            j = body.all_gids.index(support_gid)
            if lows[j] <= PLANT_EPS: i = j
        elif stance:
            feet = [body.gid[f"foot_{s_}"] for s_ in SIDES if stance.get(s_) and f"foot_{s_}" in body.gid]
            cands = [j for j, g_ in enumerate(body.all_gids) if g_ in feet and lows[j] <= PLANT_EPS]
            if cands:
                i = min(cands, key=lambda j: lows[j])
        g = body.all_gids[i]
        px = float(d.geom_xpos[g][0])                       # the support part's centre, relative to the root
        if lows[i] > PLANT_EPS:
            self.planted = None; x = self.x + self.v * dt   # airborne: keep going
        elif self.planted == g:
            x = self.plant_x - px                          # the same part is down: it does not move
        else:
            x = self.x + self.v * dt                       # a new part touches down: plant it here
            self.planted = g; self.plant_x = x + px
        if dt > 0:
            self.v = (x - self.x) / dt
        self.x = x
        return x


def pose_root(body: Body, q, k, quat, y, lift):
    """Set the body's joints, orientation, y and grounded z for frame k, with root x at zero."""
    m, d = body.m, body.d
    d.qpos[:] = 0.0
    d.qpos[3:7] = quat[k]
    for n, a in body.jadr.items():
        if n in q:
            d.qpos[a] = q[n][k]
    mujoco.mj_kinematics(m, d)
    low = body.lowest(body.all_gids).min()
    d.qpos[1] = y[k]; d.qpos[2] = -low + max(0.0, lift[k])
    mujoco.mj_kinematics(m, d)


def trajectory(st: GaitState, body: Body, t=None, clock_support=False):
    """qpos over the window at FPS, grounded and planted: the lowest point of the body touches the
    floor unless lifted, and the part on the floor does not slide. (T, nq) in the model's qpos order;
    no clipping to the body's joint ranges."""
    if t is None:
        t = np.arange(WINDOW[0], WINDOW[1], 1.0 / FPS)
    q, pitch, roll, y, lift = joint_angles(st, body, t)
    quat = quat_wxyz(roll, pitch)
    m, d = body.m, body.d
    T = len(t); out = np.zeros((T, m.nq)); ground = Ground(); st_ph = stance_phase(st, t) if clock_support else None
    for k in range(T):
        pose_root(body, q, k, quat, y, lift)
        d.qpos[0] = ground.step(body, (t[k] - t[k - 1]) if k else 0.0, {s_: bool(st_ph[s_][k]) for s_ in SIDES} if clock_support else None)
        out[k] = d.qpos
    return out
