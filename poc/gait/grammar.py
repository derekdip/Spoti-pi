"""The gait grammar: the cheap side of the locomotion case. A phase clock drives every joint of the
planar biped in closed form; the root is grounded on whatever part of the body is lowest, plus an
explicit lift for flight. A walk base and one class per contact pattern the teacher showed
(docs/gait-feasibility.md): stiff leg, short-leg limp, kneel-and-step, one-leg hop, arm vault, and a
weak hip. Each class has parameters, a range, a canonical on-state and a finite-difference
direction, exactly as the fire's classes did. Nothing here is fitted to any teacher.

G2 (docs/math-track-g1-results.md): G1's left and right versions of a class could each fit the
other side's damage, and identity was lost between them. Every sided class now has ONE signed side
parameter in [-1, 1]: negative acts on the left, positive on the right, with weight |side| on that
side and nothing on the other. A body's damage is then named by a class and the sign of its side.

Joint sign convention, from the model: every hinge is about +y, so for a hanging segment a positive
angle swings its far end backward. Hip flexion (thigh forward) is negative; knee flexion is positive;
the arms swing with the same sign convention as the hips.
"""
from __future__ import annotations
from dataclasses import dataclass, fields, replace
import numpy as np
import mujoco
from . import biped

FPS = 50.0
WINDOW = (1.0, 5.0)         # the scored window of the teacher's five seconds
SIDES = ("l", "r")


@dataclass(frozen=True)
class GaitState:
    # ---- the walk base, live on every body (fitted once on the intact teacher: V0)
    freq: float = 1.2            # Hz of the leg cycle
    duty: float = 0.6            # stance fraction of the cycle: the hip extends slowly in stance and
                                 # flexes quickly in swing, which a plain sinusoid cannot do
    speed: float = 0.7           # m/s forward
    phase0: float = 0.0          # phase at the start of the window
    hip_off: float = -0.15       # rad, mean hip angle
    hip_amp: float = 0.35        # rad, hip swing amplitude
    knee_off: float = 0.15       # rad, stance knee flexion
    knee_amp: float = 0.7        # rad, swing knee flexion
    knee_lag: float = 0.6        # rad, where in the cycle the knee bends
    ankle_amp: float = 0.2       # rad
    ankle_lag: float = 0.0
    phase_r: float = 3.1416      # rad, right leg's phase against the left
    lean: float = 0.05           # rad, torso pitch (positive leans forward)
    pitch_amp: float = 0.0       # rad, pitch oscillation at twice the cycle
    pitch_lag: float = 0.0
    bob_amp: float = 0.02        # m, root vertical oscillation at twice the cycle
    arm_amp: float = 0.3         # rad
    arm_lag: float = 3.1416      # rad, arm swing against the same-side hip
    arm_off: float = 0.0         # rad
    elbow_off: float = -0.3      # rad (negative is flexed)
    # ---- stiff leg (locked knee): the knee's swing scaled away on one side, the hip lifted to clear
    stiff_side: float = 0.0      # signed side, -1 left .. +1 right; 0 is off
    stiff_knee: float = 1.0      # scale on that side's knee swing (1 = unchanged)
    stiff_lift: float = 0.0      # rad, extra hip amplitude on that side
    # ---- short-leg limp. The side is the SHORT side, and everything the class does is on the LONG
    # side: its knee flexes more in stance, to keep the pelvis level, and more in swing, to clear the
    # ground while the body stands low on the short leg. The teacher's long knee has the larger mean
    # and the larger range on both short-shank bodies; the first two drafts split lift and sink
    # across the sides and the fit chose the wrong sign on both bodies.
    limp_side: float = 0.0
    limp_lift: float = 0.0       # rad, extra knee flexion in swing on the LONG side
    limp_sink: float = 0.0       # rad, extra stance knee flexion on the LONG side
    limp_hitch: float = 0.0      # m, vertical rise during the LONG side's stance
    limp_duty: float = 0.0       # the SHORT side's stance fraction, reduced by this: a limp is unequal
                                 # stance times before it is anything else (the short-shank teacher's
                                 # short foot is down 0.4 less of the time), and no knee term makes that
    # ---- kneel-and-step: one side kneels (its thigh is the contact), the other leg steps bent
    kneel_side: float = 0.0
    kneel_hip: float = 0.0       # rad, hip offset of the kneeling side
    kneel_amp: float = 0.0       # rad, swing of the kneeling side's hip
    kneel_other: float = 0.0     # rad, stance knee flexion added to the stepping leg
    # ---- one-leg hop: both legs in phase, a crouch, a flight
    hop_sync: float = 0.0        # 0..1, pulls the right leg's phase toward the left's
    hop_crouch: float = 0.0      # rad, knee flexion added to both legs
    hop_flight: float = 0.0      # m, lift amplitude
    hop_rate: float = 1.0        # multiplies the cycle frequency
    # ---- arm vault: the arms drive, the torso pitches, the body lifts on the arms
    vault_drive: float = 0.0     # rad, shoulder amplitude added
    vault_off: float = 0.0       # rad, shoulder offset toward the floor ahead
    vault_pitch: float = 0.0     # rad, torso pitch offset
    vault_lift: float = 0.0      # m, lift amplitude
    vault_elbow: float = 0.0     # rad, elbow offset
    # ---- weak hip: one side's hip swing scaled and delayed
    weak_side: float = 0.0
    weak_scale: float = 1.0
    weak_lag: float = 0.0

    def cost(self):
        """Parameters that are not at their default: the deployable size of the state."""
        return sum(1 for f in fields(self) if getattr(self, f.name) != f.default)


# The walk base is four live classes rather than one, so that growth can re-fit the part of the walk
# a damaged body changed (the short-shank teacher swings both knees twice as far as the intact one)
# before the impairment classes are asked to explain what is left. Fire's V0 classes were
# re-fittable per step in the same way. Identity counts impairment repairs only.
CLASSES = {
    "rhythm": ["freq", "duty", "speed", "phase0", "phase_r"],
    "legs":   ["hip_off", "hip_amp", "knee_off", "knee_amp", "knee_lag", "ankle_amp", "ankle_lag"],
    "torso":  ["lean", "pitch_amp", "pitch_lag", "bob_amp"],
    "arms":   ["arm_amp", "arm_lag", "arm_off", "elbow_off"],
    "stiff": ["stiff_side", "stiff_knee", "stiff_lift"],
    "limp":  ["limp_side", "limp_lift", "limp_sink", "limp_hitch", "limp_duty"],
    "kneel": ["kneel_side", "kneel_hip", "kneel_amp", "kneel_other"],
    "hop":   ["hop_sync", "hop_crouch", "hop_flight", "hop_rate"],
    "vault": ["vault_drive", "vault_off", "vault_pitch", "vault_lift", "vault_elbow"],
    "weak":  ["weak_side", "weak_scale", "weak_lag"],
}
V0_CLASSES = ("rhythm", "legs", "torso", "arms")
BASE_PARAMS = [p for c in V0_CLASSES for p in CLASSES[c]]
IMPAIRMENTS = ("stiff", "limp", "kneel", "hop", "vault", "weak")
SIDED = ("stiff", "limp", "kneel", "weak")

RANGES = {
    "freq": (0.4, 3.0), "duty": (0.3, 0.85), "speed": (0.0, 1.5), "phase0": (-3.2, 3.2), "hip_off": (-1.2, 0.4), "hip_amp": (0.0, 1.0),
    "knee_off": (0.0, 1.5), "knee_amp": (0.0, 1.8), "knee_lag": (-3.2, 3.2), "ankle_amp": (0.0, 0.7), "ankle_lag": (-3.2, 3.2),
    "phase_r": (0.0, 6.3), "lean": (-0.5, 1.2), "pitch_amp": (0.0, 0.5), "pitch_lag": (-3.2, 3.2), "bob_amp": (0.0, 0.1),
    "arm_amp": (0.0, 1.5), "arm_lag": (-3.2, 3.2), "arm_off": (-2.5, 0.8), "elbow_off": (-2.4, 0.0),
    "stiff_side": (-1.0, 1.0), "stiff_knee": (0.0, 1.0), "stiff_lift": (0.0, 0.6),
    "limp_side": (-1.0, 1.0), "limp_lift": (0.0, 1.0), "limp_sink": (0.0, 0.8), "limp_hitch": (0.0, 0.1), "limp_duty": (0.0, 0.35),
    "kneel_side": (-1.0, 1.0), "kneel_hip": (-1.0, 0.5), "kneel_amp": (0.0, 0.8), "kneel_other": (0.0, 1.6),
    "hop_sync": (0.0, 1.0), "hop_crouch": (0.0, 1.2), "hop_flight": (0.0, 0.25), "hop_rate": (0.5, 2.5),
    "vault_drive": (0.0, 2.0), "vault_off": (-3.0, 0.5), "vault_pitch": (-0.5, 1.6), "vault_lift": (0.0, 0.3), "vault_elbow": (-2.0, 0.0),
    "weak_side": (-1.0, 1.0), "weak_scale": (0.0, 1.0), "weak_lag": (-1.5, 1.5),
}
# canonical on-states: sided classes come on on the left; the fit carries the side where it belongs
ON = {
    "stiff": {"stiff_side": -1.0, "stiff_knee": 0.1, "stiff_lift": 0.15},
    "limp":  {"limp_side": -1.0, "limp_lift": 0.4, "limp_sink": 0.3, "limp_hitch": 0.03, "limp_duty": 0.12},
    "kneel": {"kneel_side": -1.0, "kneel_hip": -0.2, "kneel_amp": 0.3, "kneel_other": 1.0},
    "hop":   {"hop_sync": 1.0, "hop_crouch": 0.5, "hop_flight": 0.08, "hop_rate": 1.5},
    "vault": {"vault_drive": 1.0, "vault_off": -1.2, "vault_pitch": 0.4, "vault_lift": 0.05, "vault_elbow": -0.5},
    "weak":  {"weak_side": -1.0, "weak_scale": 0.6, "weak_lag": 0.3},
}
EPS = {p: 0.04 * (hi - lo) for p, (lo, hi) in RANGES.items()}


def is_on(st: GaitState, cls):
    return cls in V0_CLASSES or any(getattr(st, p) != getattr(GaitState(), p) for p in CLASSES[cls])


def turn_on(st: GaitState, cls):
    return replace(st, **ON[cls]) if cls in ON and not is_on(st, cls) else st


def side_sign(st: GaitState, cls):
    """-1, +1 or 0: which side a sided class acts on in this state."""
    if cls not in SIDED:
        return 0
    v = getattr(st, f"{cls}_side")
    return -1 if v < 0 else (1 if v > 0 else 0)


def _w(side, s):
    """Weight of a signed side parameter on side s: |side| on its own side, 0 on the other."""
    return max(0.0, -side) if s == "l" else max(0.0, side)


# ---------------------------------------------------------------- kinematics
class Body:
    """The morphology's model and the joint layout the grammar writes into."""
    def __init__(self, morph):
        self.morph = morph
        self.m = mujoco.MjModel.from_xml_string(biped.build_xml(morph))
        self.d = mujoco.MjData(self.m)
        self.jnames = [mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(self.m.njnt)]
        self.jadr = {n: int(self.m.jnt_qposadr[j]) for j, n in enumerate(self.jnames)}
        self.has = {n: (n in self.jadr) for n in ("hip_l", "knee_l", "ankle_l", "hip_r", "knee_r", "ankle_r")}
        self.contact_geoms = [g for g in ("foot_l", "foot_r", "thigh_l", "thigh_r", "hand_l", "hand_r", "pelvis")
                              if mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_GEOM, g) >= 0]
        self.gid = {g: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in self.contact_geoms}
        self.all_gids = [g for g in range(self.m.ngeom) if self.m.geom_type[g] != mujoco.mjtGeom.mjGEOM_PLANE]

    def lowest(self, gids):
        """Lowest point of each geom in the current kinematic state."""
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
    """Phase warped so that stance occupies `duty` of the cycle: u in [0, pi) is stance, [pi, 2pi) swing."""
    x = np.mod(phi, 2 * np.pi) / (2 * np.pi)
    return np.where(x < duty, x / duty * np.pi, np.pi + (x - duty) / (1.0 - duty) * np.pi)


def joint_angles(st: GaitState, body: Body, t):
    """Every present joint's angle over the time grid, and the torso pitch and lift, from the grammar."""
    f = st.freq * st.hop_rate
    phi_l = st.phase0 + 2 * np.pi * f * t
    phase_r = st.phase_r * (1.0 - st.hop_sync)
    phi = {"l": phi_l, "r": phi_l + phase_r}
    q = {}
    for s in SIDES:
        o = "r" if s == "l" else "l"
        w_stiff, w_limp, w_kneel, w_weak = (_w(st.stiff_side, s), _w(st.limp_side, s), _w(st.kneel_side, s), _w(st.weak_side, s))
        w_limp_o, w_kneel_o = _w(st.limp_side, o), _w(st.kneel_side, o)
        scale = 1.0 - (1.0 - st.weak_scale) * w_weak
        lag = st.weak_lag * w_weak
        u = warp(phi[s] - lag, st.duty - st.limp_duty * w_limp)
        hip_amp = st.hip_amp * scale + st.stiff_lift * w_stiff + st.kneel_amp * w_kneel
        # stance: the hip goes from flexed (forward, negative) to extended; swing brings it back
        hip = st.hip_off + st.kneel_hip * w_kneel - hip_amp * np.cos(u)
        swing = np.maximum(0.0, -np.sin(u + st.knee_lag))
        knee_scale = 1.0 - (1.0 - st.stiff_knee) * w_stiff
        # the limp's lift and sink both act on the LONG side (the teacher's long knee flexes more in
        # stance, to keep the pelvis level, and in swing, to clear the ground while on the short leg)
        knee = (st.knee_off + st.hop_crouch + st.limp_sink * w_limp_o + st.kneel_other * w_kneel_o
                + (st.knee_amp * knee_scale + st.limp_lift * w_limp_o) * swing)
        ankle = st.ankle_amp * np.sin(u + st.ankle_lag)
        q[f"hip_{s}"] = hip; q[f"knee_{s}"] = knee; q[f"ankle_{s}"] = ankle
        q[f"shoulder_{s}"] = st.arm_off + st.vault_off + (st.arm_amp + st.vault_drive) * np.sin(phi[s] + st.arm_lag)
        q[f"elbow_{s}"] = np.full_like(t, st.elbow_off + st.vault_elbow)
    pitch = st.lean + st.vault_pitch + st.pitch_amp * np.sin(2 * phi_l + st.pitch_lag)
    # the rise comes during the long side's stance: with the short side on the left, during the right leg's cycle
    hitch = st.limp_hitch * (_w(st.limp_side, "l") * np.maximum(0.0, np.sin(phi["r"])) + _w(st.limp_side, "r") * np.maximum(0.0, np.sin(phi["l"])))
    lift = st.hop_flight * np.maximum(0.0, np.sin(2 * phi_l)) + st.vault_lift * np.maximum(0.0, np.sin(phi_l)) + hitch
    bob = st.bob_amp * np.sin(2 * phi_l)
    return q, pitch, lift + bob


def trajectory(st: GaitState, body: Body, t=None):
    """qpos over the window at FPS, grounded: the lowest point of the body touches the floor unless
    lifted. (T, nq) in the model's qpos order. No clipping to the body's joint ranges: the student
    does not know which joint the damage locked, the teacher's behaviour has to reveal it."""
    if t is None:
        t = np.arange(WINDOW[0], WINDOW[1], 1.0 / FPS)
    q, pitch, lift = joint_angles(st, body, t)
    m, d = body.m, body.d
    T = len(t); out = np.zeros((T, m.nq))
    x = st.speed * (t - t[0])
    for k in range(T):
        d.qpos[:] = 0.0
        d.qpos[2] = pitch[k]
        for n, a in body.jadr.items():
            if n in q:
                d.qpos[a] = q[n][k]
        mujoco.mj_kinematics(m, d)
        low = body.lowest(body.all_gids).min()
        d.qpos[0] = x[k]
        d.qpos[1] = -low + max(0.0, lift[k])
        out[k] = d.qpos
    return out
