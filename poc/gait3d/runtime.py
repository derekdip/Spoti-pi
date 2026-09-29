"""The runtime side of the locomotion case: a player that drives a body from a grammar state with
no physics and no teacher, at any frame rate, with a phase clock that stays continuous through
changes of state and of body.

  Player(morph, state)        a body and the state that describes its gait
  player.advance(dt)          move the clock and the root; returns the frame (qpos in the body's layout)
  player.transition(state, seconds, morph=None)
                              blend to another state over `seconds`, in parameter space, and if the
                              body changed (a leg removed), switch the model at the start of the
                              blend: joints that remain keep their angles, the root is re-grounded
  export(frames, body)        joint names and per-frame angles and root pose, the interface an
                              engine reads

The frame at a phase is the grammar's closed form (poc/gait3d/grammar3d.joint_angles) with the root
grounded on the body's lowest part, exactly as the fitted trajectories were; the only differences
from grammar3d.trajectory are that phase and forward position are integrated, so that frequency and
speed can change without a jump, and that the state can be a blend of two.
"""
from __future__ import annotations
import json
from dataclasses import replace, fields, asdict
import numpy as np
import mujoco
from .grammar3d import GaitState, Body, joint_angles, quat_wxyz, Ground, pose_root

CIRCULAR = {"phase0", "phase_r", "knee_lag", "ankle_lag", "sway_lag", "abd_lag", "pitch_lag", "roll_lag", "arm_lag", "vault_lag"}


def blend(a: GaitState, b: GaitState, w: float) -> GaitState:
    """Parameter-space interpolation, lags along the shorter arc."""
    out = {}
    for f in fields(a):
        x, y = getattr(a, f.name), getattr(b, f.name)
        if f.name in CIRCULAR:
            d = (y - x + np.pi) % (2 * np.pi) - np.pi
            out[f.name] = float(x + w * d)
        else:
            out[f.name] = float((1.0 - w) * x + w * y)
    return GaitState(**out)


def frame_at(st: GaitState, body: Body, phi: float, ground: Ground, dt: float):
    """qpos for the grammar state at phase phi (the left leg's); the root's x from the planted part."""
    t = np.array([(phi - st.phase0) / (2 * np.pi * st.freq)])       # the time at which the grammar's own clock reads phi
    q, pitch, roll, y, lift = joint_angles(st, body, t)
    quat = quat_wxyz(roll, pitch)
    pose_root(body, q, 0, quat, y, lift)
    body.d.qpos[0] = ground.step(body, dt)
    return body.d.qpos.copy()


class Player:
    def __init__(self, morph, state: GaitState, phi0=0.0):
        self.body = Body(morph); self.morph = morph
        self.state = state; self.target = None; self.blend_t = 0.0; self.blend_T = 0.0; self.source = None
        self.phi = phi0; self.t = 0.0; self.ground = Ground()

    def current(self) -> GaitState:
        if self.target is None:
            return self.state
        w = min(1.0, self.blend_t / self.blend_T) if self.blend_T > 0 else 1.0
        return blend(self.source, self.target, w)

    def transition(self, state: GaitState, seconds: float, morph=None):
        self.source = self.current(); self.target = state; self.blend_T = seconds; self.blend_t = 0.0
        if morph is not None and morph != self.morph:
            self.body = Body(morph); self.morph = morph          # the model changes at the start of the blend
            self.ground.planted = None                            # whatever was planted may be gone: re-plant on the next frame

    def advance(self, dt: float):
        st = self.current()
        self.phi += 2 * np.pi * st.freq * dt
        self.t += dt
        if self.target is not None:
            self.blend_t += dt
            if self.blend_t >= self.blend_T:
                self.state, self.target, self.source = self.target, None, None
        return frame_at(st, self.body, self.phi, self.ground, dt)

    def frames(self, seconds: float, fps: float):
        return np.array([self.advance(1.0 / fps) for _ in range(int(round(seconds * fps)))])


def export(frames, body: Body, fps: float):
    """The interface: root position and orientation (w, x, y, z) and every joint's angle per frame."""
    return dict(fps=fps, morph=body.morph, joints=body.joints,
                root_pos=frames[:, :3].round(5).tolist(), root_quat=frames[:, 3:7].round(5).tolist(),
                angles=frames[:, 7:].round(5).tolist())


def state_from_json(d):
    return replace(GaitState(), **{k: v for k, v in d.items() if k in GaitState.__dataclass_fields__})


def load_states(path="poc/results/g7.json"):
    """The fitted states of a growth run, by case name."""
    return {c["case"]: state_from_json(c["state"]) for c in json.load(open(path))["cases"]}
