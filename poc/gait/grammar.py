"""The gait grammar: the cheap side of the locomotion case. A phase clock drives every joint of the
planar biped in closed form; the root is grounded on whatever part of the body is lowest, plus an
explicit lift for flight. A walk base and one class per contact pattern the teacher showed
(docs/gait-feasibility.md): stiff leg, short leg, kneel-and-step, one-leg hop, arm vault, and a weak
hip. Each class has parameters, a range, a canonical on-state and a finite-difference direction,
exactly as the fire's classes did. Nothing here is fitted to any teacher.

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
WINDOW = (1.0, 5.0)         # the scored window of the teacher's five seconds (pilot: four seconds, more cycles)
SIDES = ("l", "r")


@dataclass(frozen=True)
class GaitState:
    # ---- the walk base, live on every body (fitted once on the intact teacher: V0)
    freq: float = 1.2            # Hz of the leg cycle
    duty: float = 0.6            # stance fraction of the cycle: the hip extends slowly in stance and
                                 # flexes quickly in swing, which a plain sinusoid cannot do (pilot fix 2)
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
    pitch_amp: float = 0.0       # rad, pitch oscillation at twice the cycle (pilot fix 4: the teacher's
    pitch_lag: float = 0.0       # pitch has a spread, and a constant pitch cannot score on it)
    bob_amp: float = 0.02        # m, root vertical oscillation at twice the cycle
    arm_amp: float = 0.3         # rad
    arm_lag: float = 3.1416      # rad, arm swing against the same-side hip
    arm_off: float = 0.0         # rad
    elbow_off: float = -0.3      # rad (negative is flexed)
    # ---- stiff leg (locked knee): the knee's swing scaled away, the hip lifted to clear the foot
    stiff_knee_l: float = 1.0    # scale on the left knee's swing amplitude (1 = unchanged)
    stiff_lift_l: float = 0.0    # rad, extra hip amplitude on the stiff side
    stiff_knee_r: float = 1.0
    stiff_lift_r: float = 0.0
    # ---- short leg: extra swing flexion on the short side, a sink on the long side, a hitch
    short_lift_l: float = 0.0    # rad, extra knee flexion in swing
    short_sink_l: float = 0.0    # rad, extra stance knee flexion on the OTHER leg
    short_hitch_l: float = 0.0   # m, vertical hitch at the short side's stance
    short_lift_r: float = 0.0
    short_sink_r: float = 0.0
    short_hitch_r: float = 0.0
    # ---- kneel-and-step: the named side kneels (its thigh is the contact), the other leg steps bent
    kneel_hip_l: float = 0.0     # rad, hip offset of the kneeling side (toward the thigh pointing down)
    kneel_amp_l: float = 0.0     # rad, swing of the kneeling side's hip
    kneel_other_l: float = 0.0   # rad, stance knee flexion added to the stepping leg
    kneel_hip_r: float = 0.0
    kneel_amp_r: float = 0.0
    kneel_other_r: float = 0.0
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
    # ---- weak hip: the hip's swing scaled and delayed on one side
    weak_scale_l: float = 1.0
    weak_lag_l: float = 0.0
    weak_scale_r: float = 1.0
    weak_lag_r: float = 0.0

    def cost(self):
        """Parameters that are not at their default: the deployable size of the state."""
        return sum(1 for f in fields(self) if getattr(self, f.name) != f.default)


CLASSES = {
    "gait":    ["freq", "duty", "speed", "phase0", "hip_off", "hip_amp", "knee_off", "knee_amp", "knee_lag", "ankle_amp",
                "ankle_lag", "phase_r", "lean", "pitch_amp", "pitch_lag", "bob_amp", "arm_amp", "arm_lag", "arm_off", "elbow_off"],
    "stiff_l": ["stiff_knee_l", "stiff_lift_l"],
    "stiff_r": ["stiff_knee_r", "stiff_lift_r"],
    "short_l": ["short_lift_l", "short_sink_l", "short_hitch_l"],
    "short_r": ["short_lift_r", "short_sink_r", "short_hitch_r"],
    "kneel_l": ["kneel_hip_l", "kneel_amp_l", "kneel_other_l"],
    "kneel_r": ["kneel_hip_r", "kneel_amp_r", "kneel_other_r"],
    "hop":     ["hop_sync", "hop_crouch", "hop_flight", "hop_rate"],
    "vault":   ["vault_drive", "vault_off", "vault_pitch", "vault_lift", "vault_elbow"],
    "weak_l":  ["weak_scale_l", "weak_lag_l"],
    "weak_r":  ["weak_scale_r", "weak_lag_r"],
}
V0_CLASSES = ("gait",)

RANGES = {
    "freq": (0.4, 3.0), "duty": (0.3, 0.85), "speed": (0.0, 1.5), "phase0": (-3.2, 3.2), "hip_off": (-1.2, 0.4), "hip_amp": (0.0, 1.0),
    "knee_off": (0.0, 1.5), "knee_amp": (0.0, 1.8), "knee_lag": (-3.2, 3.2), "ankle_amp": (0.0, 0.7), "ankle_lag": (-3.2, 3.2),
    "phase_r": (0.0, 6.3), "lean": (-0.5, 1.2), "pitch_amp": (0.0, 0.5), "pitch_lag": (-3.2, 3.2), "bob_amp": (0.0, 0.1), "arm_amp": (0.0, 1.5), "arm_lag": (-3.2, 3.2),
    "arm_off": (-2.5, 0.8), "elbow_off": (-2.4, 0.0),
    "stiff_knee_l": (0.0, 1.0), "stiff_lift_l": (0.0, 0.6), "stiff_knee_r": (0.0, 1.0), "stiff_lift_r": (0.0, 0.6),
    "short_lift_l": (0.0, 1.0), "short_sink_l": (0.0, 0.8), "short_hitch_l": (0.0, 0.1),
    "short_lift_r": (0.0, 1.0), "short_sink_r": (0.0, 0.8), "short_hitch_r": (0.0, 0.1),
    "kneel_hip_l": (-1.0, 0.5), "kneel_amp_l": (0.0, 0.8), "kneel_other_l": (0.0, 1.6),
    "kneel_hip_r": (-1.0, 0.5), "kneel_amp_r": (0.0, 0.8), "kneel_other_r": (0.0, 1.6),
    "hop_sync": (0.0, 1.0), "hop_crouch": (0.0, 1.2), "hop_flight": (0.0, 0.25), "hop_rate": (0.5, 2.5),
    "vault_drive": (0.0, 2.0), "vault_off": (-3.0, 0.5), "vault_pitch": (-0.5, 1.6), "vault_lift": (0.0, 0.3), "vault_elbow": (-2.0, 0.0),
    "weak_scale_l": (0.0, 1.0), "weak_lag_l": (-1.5, 1.5), "weak_scale_r": (0.0, 1.0), "weak_lag_r": (-1.5, 1.5),
}
ON = {
    "stiff_l": {"stiff_knee_l": 0.1, "stiff_lift_l": 0.15},
    "stiff_r": {"stiff_knee_r": 0.1, "stiff_lift_r": 0.15},
    "short_l": {"short_lift_l": 0.4, "short_sink_l": 0.3, "short_hitch_l": 0.03},
    "short_r": {"short_lift_r": 0.4, "short_sink_r": 0.3, "short_hitch_r": 0.03},
    "kneel_l": {"kneel_hip_l": -0.2, "kneel_amp_l": 0.3, "kneel_other_l": 1.0},
    "kneel_r": {"kneel_hip_r": -0.2, "kneel_amp_r": 0.3, "kneel_other_r": 1.0},
    "hop":     {"hop_sync": 1.0, "hop_crouch": 0.5, "hop_flight": 0.08, "hop_rate": 1.5},
    "vault":   {"vault_drive": 1.0, "vault_off": -1.2, "vault_pitch": 0.4, "vault_lift": 0.05, "vault_elbow": -0.5},
    "weak_l":  {"weak_scale_l": 0.6, "weak_lag_l": 0.3},
    "weak_r":  {"weak_scale_r": 0.6, "weak_lag_r": 0.3},
}
EPS = {p: 0.04 * (hi - lo) for p, (lo, hi) in RANGES.items()}


def is_on(st: GaitState, cls):
    return cls in V0_CLASSES or any(getattr(st, p) != getattr(GaitState(), p) for p in CLASSES[cls])


def turn_on(st: GaitState, cls):
    return replace(st, **ON[cls]) if cls in ON and not is_on(st, cls) else st


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
        scale = getattr(st, f"weak_scale_{s}"); lag = getattr(st, f"weak_lag_{s}")
        u = warp(phi[s] - lag, st.duty)
        hip_amp = st.hip_amp * scale + getattr(st, f"stiff_lift_{s}") + getattr(st, f"kneel_amp_{s}")
        # stance: the hip goes from flexed (forward, negative) to extended; swing brings it back
        hip = st.hip_off + getattr(st, f"kneel_hip_{s}") - hip_amp * np.cos(u)
        swing = np.maximum(0.0, -np.sin(u + st.knee_lag))
        knee = (st.knee_off + st.hop_crouch + getattr(st, f"short_sink_{o}") + getattr(st, f"kneel_other_{o}")
                + (st.knee_amp * getattr(st, f"stiff_knee_{s}") + getattr(st, f"short_lift_{s}")) * swing)
        ankle = st.ankle_amp * np.sin(u + st.ankle_lag)
        q[f"hip_{s}"] = hip; q[f"knee_{s}"] = knee; q[f"ankle_{s}"] = ankle
        q[f"shoulder_{s}"] = st.arm_off + st.vault_off + (st.arm_amp + st.vault_drive) * np.sin(phi[s] + st.arm_lag)
        q[f"elbow_{s}"] = np.full_like(t, st.elbow_off + st.vault_elbow)
    pitch = st.lean + st.vault_pitch + st.pitch_amp * np.sin(2 * phi_l + st.pitch_lag)
    lift = (st.hop_flight * np.maximum(0.0, np.sin(2 * phi_l)) + st.vault_lift * np.maximum(0.0, np.sin(phi_l))
            + getattr(st, "short_hitch_l") * np.maximum(0.0, np.sin(phi["r"])) + getattr(st, "short_hitch_r") * np.maximum(0.0, np.sin(phi["l"])))
    bob = st.bob_amp * np.sin(2 * phi_l)
    return q, pitch, lift + bob


def trajectory(st: GaitState, body: Body, t=None):
    """qpos over the window at FPS, grounded: the lowest point of the body touches the floor unless
    lifted. (T, nq) in the model's qpos order."""
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
        # no clipping to the body's joint ranges: the student does not know which joint the damage
        # locked, the teacher's behaviour has to reveal it (pilot fix 5: with the clip, the stiff
        # class was inert on the locked-knee body because the clip had already stiffened the leg)
        mujoco.mj_kinematics(m, d)
        low = body.lowest(body.all_gids).min()
        d.qpos[0] = x[k]
        d.qpos[1] = -low + max(0.0, lift[k])
        out[k] = d.qpos
    return out
