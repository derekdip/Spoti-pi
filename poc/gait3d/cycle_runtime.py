"""The cycle runtime: a body played from its teacher's own motion, with the runtime's clock, root
motion, blending and body switch. Six objectives for fitting the parametric grammar to the 3D
teacher each gave a motion a viewer faulted (docs/gait3d-runtime.md); the teacher itself reads
right, so the deployable description is a clip of it:

  CycleProfile.from_teacher(morph, seed)        the mean cycle: the teacher's frames cut at a foot's
                                                touchdowns, resampled to NB phase bins and averaged
                                                (joint angles, root height, orientation, root
                                                displacement); right for the bodies that walk
  CycleProfile.from_teacher_loop(morph, seed)   the whole window as one looping clip with a crossfaded
                                                seam; for the gaits with no clean cycle (the stump's
                                                kneel-step, the one-leg hop, the legless crawl)
  CyclePlayer(profile).advance(dt)              a frame: the profile interpolated at the clock's phase,
                                                the root moved by the profile's own displacement
                                                (root motion), never below the floor
  player.transition(profile, seconds)           blend to another clip and body in profile space
  styled(profile)                               the style layer: arms forward and stiff, head down

Orientation is the teacher's quaternion per bin, blended by normalised interpolation; no Euler
angles, since the crawl is pitched to the floor with a heading.
"""
from __future__ import annotations
import json
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
from .grammar3d import Body, FPS
from . import rgre_gait3d as RG

NB = 32
STYLE = dict(shoulder_l=-1.35, shoulder_r=-1.35, elbow_l=-0.35, elbow_r=-0.35)
STYLE_PITCH = 0.22


def _qmean(quats):
    """Mean of unit quaternions (w, x, y, z), sign-aligned to the first, renormalised."""
    q = np.asarray(quats, float).copy()
    for i in range(1, len(q)):
        if np.dot(q[i], q[0]) < 0: q[i] = -q[i]
    m = q.mean(0); return m / np.linalg.norm(m)


def _qlerp(a, b, w):
    b = b if np.dot(a, b) >= 0 else -b
    m = (1 - w) * a + w * b; return m / max(np.linalg.norm(m), 1e-9)


class CycleProfile:
    def __init__(self, morph, joints, angles, z, quat, dur, dx, dy):
        self.morph = morph; self.joints = list(joints); self.angles = np.asarray(angles, float); self.z = np.asarray(z, float)
        self.quat = np.asarray(quat, float); self.dur = float(dur)
        self.dx = np.asarray(dx, float); self.dy = np.asarray(dy, float)      # root displacement from the clip's start at nb + 1 phase edges

    # ---- from the teacher
    @staticmethod
    def _contacts(body, q):
        m, d = body.m, body.d; parts = [body.gid[g] for g in body.contact_geoms]; T = len(q); contact = np.zeros((T, len(parts)))
        for k in range(T):
            d.qpos[:] = q[k]; mujoco.mj_kinematics(m, d); contact[k] = body.lowest(parts) <= RG.CONTACT_EPS
        return contact

    @staticmethod
    def _root_motion(q, a, b, n):
        idx = np.linspace(a, b, n + 1).round().astype(int).clip(0, len(q) - 1)
        x = q[idx, 0] - q[a, 0]; y = q[idx, 1] - q[a, 1]; y = y - np.linspace(0, y[-1], n + 1)
        return x, y

    @classmethod
    def from_teacher(cls, morph, seed=0, nb=NB):
        body = Body(morph); q = RG.teacher_qpos(morph, seed); T = len(q)
        contact = cls._contacts(body, q); cyc = None
        for g in ("foot_l", "foot_r", "thigh_l", "thigh_r", "hand_l", "hand_r"):
            if g in body.gid:
                cyc = RG.cycles_from_contact(contact[:, body.contact_geoms.index(g)] > 0.5)
                if cyc: break
        if not cyc:
            cyc = RG.cycles(q[:, body.jadr[next(n for n in ("hip_y_l", "hip_y_r", "shoulder_l") if n in body.jadr)]])
        ang = RG.phase_mean(q[:, 7:], cyc, nb); z = RG.phase_mean(q[:, 2:3], cyc, nb)[:, 0]
        quats = []
        for b in range(nb):
            rows = []
            for a, e in cyc:
                idx = np.linspace(a, e - 1, nb).round().astype(int); rows.append(q[idx[b], 3:7])
            quats.append(_qmean(rows))
        rm = [cls._root_motion(q, a, e, nb) for a, e in cyc]
        return cls(morph, body.joints, ang, z, np.array(quats), float(np.mean([(e - a) / FPS for a, e in cyc])), np.mean([x for x, _ in rm], 0), np.mean([y for _, y in rm], 0))

    @classmethod
    def from_teacher_loop(cls, morph, seed=0, seam=0.3):
        body = Body(morph); q = RG.teacher_qpos(morph, seed); T = len(q); n = int(seam * FPS)
        ang = q[:, 7:].copy(); z = q[:, 2].copy(); quat = q[:, 3:7].copy()
        for i in range(n):                                       # overlay the first n frames on the last n, then drop the first n
            w = (i + 1) / (n + 1)
            ang[T - n + i] = (1 - w) * ang[T - n + i] + w * ang[i]; z[T - n + i] = (1 - w) * z[T - n + i] + w * z[i]; quat[T - n + i] = _qlerp(quat[T - n + i], quat[i], w)
        ang, z, quat = ang[n:], z[n:], quat[n:]; L = T - n
        x = q[n:, 0] - q[n, 0]; dx = np.concatenate([x, [x[-1] + (x[-1] - x[-2])]])
        y = q[n:, 1] - q[n, 1]; y = y - np.linspace(0, y[-1], L); dy = np.concatenate([y, [0.0]])
        return cls(morph, body.joints, ang, z, quat, L / FPS, dx, dy)

    # ---- reading
    def at(self, phase):
        nb = len(self.angles); x = (phase % 1.0) * nb; i = int(np.floor(x)) % nb; j = (i + 1) % nb; w = x - np.floor(x)
        lerp = lambda a: (1 - w) * a[i] + w * a[j]
        return dict(zip(self.joints, lerp(self.angles))), float(lerp(self.z)), _qlerp(self.quat[i], self.quat[j], w)

    def root_at(self, phase):
        x = min(max(phase, 0.0), 1.0) * (len(self.dx) - 1); i = int(np.floor(x)); j = min(i + 1, len(self.dx) - 1); w = x - i
        return float((1 - w) * self.dx[i] + w * self.dx[j]), float((1 - w) * self.dy[i] + w * self.dy[j])

    def resampled(self, nb):
        ph = np.arange(nb) / nb; rows = [self.at(p) for p in ph]
        ang = np.array([[r[0][j] for j in self.joints] for r in rows]); z = np.array([r[1] for r in rows]); quat = np.array([r[2] for r in rows])
        edges = np.arange(nb + 1) / nb
        return CycleProfile(self.morph, self.joints, ang, z, quat, self.dur, [self.root_at(p)[0] for p in edges], [self.root_at(p)[1] for p in edges])

    def to_json(self):
        return dict(morph=self.morph, joints=self.joints, angles=self.angles.round(5).tolist(), z=self.z.round(5).tolist(), quat=self.quat.round(5).tolist(), dur=self.dur, dx=self.dx.round(5).tolist(), dy=self.dy.round(5).tolist())


def styled(p: CycleProfile) -> CycleProfile:
    """The style layer on a clip: the arms forward and stiff with a quarter of their swing, the torso
    pitched further forward; the legless body keeps its arms."""
    ang = p.angles.copy(); quat = p.quat.copy()
    if p.morph != "nolegs":
        for j, off in STYLE.items():
            if j in p.joints:
                k = p.joints.index(j); ang[:, k] = off + 0.25 * (p.angles[:, k] - p.angles[:, k].mean())
    tilt = Rotation.from_euler("y", STYLE_PITCH if p.morph != "nolegs" else 0.0)
    for b in range(len(quat)):
        r = Rotation.from_quat([quat[b, 1], quat[b, 2], quat[b, 3], quat[b, 0]]) * tilt          # the pitch in the body's own frame
        qq = r.as_quat(); quat[b] = [qq[3], qq[0], qq[1], qq[2]]
    return CycleProfile(p.morph, p.joints, ang, p.z, quat, p.dur, p.dx, p.dy)


def blend(a: CycleProfile, b: CycleProfile, w: float) -> CycleProfile:
    """Interpolate two profiles on the joints they share (joints only in b enter at b's values), the
    shorter resampled to the longer's bins, the orientation by normalised interpolation."""
    nb = max(len(a.angles), len(b.angles))
    if len(a.angles) != nb: a = a.resampled(nb)
    if len(b.angles) != nb: b = b.resampled(nb)
    ang = np.zeros((nb, len(b.joints)))
    for k, j in enumerate(b.joints):
        ang[:, k] = ((1 - w) * a.angles[:, a.joints.index(j)] + w * b.angles[:, k]) if j in a.joints else b.angles[:, k]
    quat = np.array([_qlerp(a.quat[i], b.quat[i], w) for i in range(nb)])
    return CycleProfile(b.morph, b.joints, ang, (1 - w) * a.z + w * b.z, quat, (1 - w) * a.dur + w * b.dur, (1 - w) * a.dx + w * b.dx, (1 - w) * a.dy + w * b.dy)


class CyclePlayer:
    def __init__(self, profile: CycleProfile, phase0=0.0, body: Body | None = None):
        self.profile = profile; self.body = body if body is not None and body.morph == profile.morph else Body(profile.morph); self.morph = profile.morph
        self.phase = phase0; self.t = 0.0; self.x = 0.0; self.y = 0.0
        self.target = None; self.source = None; self.blend_t = 0.0; self.blend_T = 0.0

    def current(self) -> CycleProfile:
        if self.target is None: return self.profile
        w = min(1.0, self.blend_t / self.blend_T) if self.blend_T > 0 else 1.0
        return blend(self.source, self.target, w)

    def transition(self, profile: CycleProfile, seconds: float):
        self.source = self.current(); self.target = profile; self.blend_T = seconds; self.blend_t = 0.0
        if profile.morph != self.morph:
            self.body = Body(profile.morph); self.morph = profile.morph

    def frame(self, prof: CycleProfile):
        q, z_ref, quat = prof.at(self.phase)
        m, d = self.body.m, self.body.d
        d.qpos[:] = 0.0; d.qpos[3:7] = quat
        for n, a in self.body.jadr.items():
            if n in q: d.qpos[a] = q[n]
        mujoco.mj_kinematics(m, d)
        d.qpos[2] = max(z_ref, -self.body.lowest(self.body.all_gids).min())
        d.qpos[0] = self.x; d.qpos[1] = self.y
        return d.qpos.copy()

    def advance(self, dt: float):
        prof = self.current(); fr = self.frame(prof)
        p0 = self.phase; p1 = p0 + dt / prof.dur
        x0, y0 = prof.root_at(p0 % 1.0); x1, y1 = prof.root_at(p1 % 1.0); wraps = int(np.floor(p1)) - int(np.floor(p0))
        self.x += (x1 - x0) + wraps * prof.dx[-1]; self.y += (y1 - y0); self.phase = p1; self.t += dt
        if self.target is not None:
            self.blend_t += dt
            if self.blend_t >= self.blend_T:
                self.profile, self.target, self.source = self.target, None, None
        return fr

    def frames(self, seconds: float, fps: float):
        return np.array([self.advance(1.0 / fps) for _ in range(int(round(seconds * fps)))])


LOOP_BODIES = ("stump_left", "stump_right", "noleg_left", "noleg_right", "nolegs")     # the gaits with no clean cycle


def profile_for(morph, seed=0):
    return CycleProfile.from_teacher_loop(morph, seed) if morph in LOOP_BODIES else CycleProfile.from_teacher(morph, seed)
