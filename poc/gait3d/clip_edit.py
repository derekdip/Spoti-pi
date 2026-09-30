"""G13: the grammar's classes as edits on the teacher's own cycle. Prereg: docs/math-track-g13-prereg.md.

The base is the intact teacher's mean cycle (poc/gait3d/cycle_runtime.py, seed 0, 32 phase bins), the
description that plays. A grammar state S is read as an edit of it, relative to a fixed reference R
(the G11 V0 walk base), each parameter acting on the clip's own curves the way it acts in the
grammar's closed form: an amplitude scales the clip's oscillation by S/R (the knee's flexion above
its minimum; the hip's, ankle's, abduction's and arm's swing about their means), an offset adds
S - R, a lag shifts the curve by the difference, a stance fraction or a side's delay re-times that
side's curves through the grammar's warp (S's warp, then R's inverse, about the clip's own stance
start), the right leg's phase shifts its curves, the frequency scales the duration. The root's pitch,
roll, lateral offset and lift take the grammar's difference S - R added to the clip's (the rotation
composed); the root and the arms follow the legs' re-timing by the mean of the two sides'. Progress follows the stance feet: the clip's own root displacement is scaled by the ratio
of the edited to the raw kinematic stride, each foot's position relative to the root at touchdown
minus at toe-off (the raw clip's contact pattern, re-timed with the legs); a leg without a foot uses
its thigh. (The planted rule's travel, tried first, turned a clamped knee into a
stop and a lifted knee into a sprint through the handoff geometry: the pre-build check in the
prereg.) At S = R every operator is the identity and
the clip plays as the teacher did; the round's V0 is the raw clip on every body, with the joints the
body lacks dropped. A base class is an edit through the same operators as an impairment.
"""
from __future__ import annotations
from dataclasses import replace
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
from .grammar3d import GaitState, Body, joint_angles, Ground, SIDES, SGN, FPS, WINDOW, warp, _w as G_w
from .cycle_runtime import CycleProfile, CyclePlayer, NB, _qlerp
from . import rgre_gait3d as RG

CLIP_MORPH, CLIP_SEED = "intact", 0
_cache = {}


def base_clip(nb=NB) -> CycleProfile:
    if ("clip", nb) not in _cache:
        _cache[("clip", nb)] = CycleProfile.from_teacher(CLIP_MORPH, CLIP_SEED, nb)
    return _cache[("clip", nb)]


def _pose(body: Body, q, quat, y, z):
    """Pose the body at root x = 0, never below the floor; returns the z used."""
    m, d = body.m, body.d
    d.qpos[:] = 0.0; d.qpos[3:7] = quat
    for n, a in body.jadr.items():
        if n in q: d.qpos[a] = q[n]
    mujoco.mj_kinematics(m, d)
    low = float(body.lowest(body.all_gids).min()); z = max(z, -low)
    d.qpos[1] = y; d.qpos[2] = z; mujoco.mj_kinematics(m, d)
    return z


def clip_stance(nb=NB):
    """Which feet the raw clip has on the floor per bin, read on the intact body."""
    if ("stance", nb) not in _cache:
        clip = base_clip(nb); body = Body(CLIP_MORPH); out = []
        for b in range(nb):
            q, z, quat = clip.at(b / nb); _pose(body, q, quat, clip.root_at(b / nb)[1], z)
            lows = body.lowest([body.gid[f"foot_{s}"] for s in SIDES])
            out.append({s: bool(lows[i] <= RG.CONTACT_EPS) for i, s in enumerate(SIDES)})
        _cache[("stance", nb)] = out
    return _cache[("stance", nb)]


def grammar_root(st: GaitState, body: Body, nb):
    """The grammar's root curves at the clip's phase bins (the left foot's phase 2*pi*b/nb)."""
    t = (2 * np.pi * np.arange(nb) / nb - st.phase0) / (2 * np.pi * st.freq)
    q, pitch, roll, y, lift = joint_angles(st, body, t)
    return pitch, roll, y, np.maximum(0.0, lift)


def _sample(curve, phases):
    """A periodic curve on nb bins, linearly interpolated at phases in cycles."""
    nb = len(curve); x = np.mod(phases, 1.0) * nb; i = np.floor(x).astype(int) % nb; j = (i + 1) % nb; w = x - np.floor(x)
    return (1 - w) * curve[i] + w * curve[j]


def _warp_inv(u, duty):
    """The phase in cycles whose warp (grammar3d.warp) is u."""
    return np.where(u < np.pi, u / np.pi * duty, duty + (u - np.pi) / np.pi * (1.0 - duty))


def stance_start(nb=NB):
    """Where each foot's stance begins in the raw clip and how much of the cycle it lasts, in cycles
    (the longest run of that foot's contact flags with gaps of up to two bins closed; the left foot's
    start is 0 by the cut)."""
    fl = clip_stance(nb); out = {}
    for s_ in SIDES:
        run = _longest_run([f[s_] for f in fl])
        out[s_] = ((run[0] % nb) / nb, (run[1] - run[0] + 1) / nb) if run else (0.0, 0.5)
    return out


def leg_phases(st: GaitState, ref: GaitState, nb):
    """For each side, the raw clip's phase to read at every bin, after the state's re-timing: the
    right leg's phase shift, that side's delay (weak) and stance fraction (duty, limp) through the
    grammar's warp about the clip's own stance start, the state's change of stance fraction against
    the reference applied to the clip's own stance fraction (the clip's feet are down for more of the
    cycle than the grammar's duty says, and a warp about the grammar's duty moved the clip's real
    toe-off into the stance run: the prereg's pre-build check)."""
    phi = np.arange(nb) / nb; st0 = stance_start(nb); out = {}
    for s_ in SIDES:
        dr = ((st.phase_r - ref.phase_r) / (2 * np.pi)) if s_ == "r" else 0.0
        w_limp, w_weak = G_w(st.limp_side, s_), G_w(st.weak_side, s_)
        start, duty_clip = st0[s_]
        duty_s = float(np.clip(duty_clip + (st.duty - st.limp_duty * w_limp - ref.duty), 0.05, 0.95))
        psi = np.mod(phi - dr - start, 1.0)
        u = warp(2 * np.pi * psi - st.weak_lag * w_weak, duty_s)
        out[s_] = start + _warp_inv(u, duty_clip)
    return out


def _qsample(quats, phases):
    """Unit quaternions (w, x, y, z) on nb bins, interpolated at phases in cycles."""
    nb = len(quats); x = np.mod(phases, 1.0) * nb; i = np.floor(x).astype(int) % nb; j = (i + 1) % nb; w = x - np.floor(x)
    return np.array([_qlerp(quats[ii], quats[jj], ww) for ii, jj, ww in zip(i, j, w)])


def edited_profile(st: GaitState, body: Body, ref: GaitState, clip: CycleProfile | None = None) -> CycleProfile:
    clip = clip or base_clip(); nb = len(clip.angles); phi = np.arange(nb) / nb; ph = leg_phases(st, ref, nb)
    dr = (st.phase_r - ref.phase_r) / (2 * np.pi)
    # the root and the arms follow the legs' re-timing, by the mean of the two sides' displacements
    # (the right leg's own phase shift excluded), so that the trunk's pitch and yaw stay with the stride
    disp = {s_: np.mod(ph[s_] - phi + (dr if s_ == "r" else 0.0) + 0.5, 1.0) - 0.5 for s_ in SIDES}
    p_root = phi + 0.5 * (disp["l"] + disp["r"])
    C = {j: clip.angles[:, clip.joints.index(j)] for j in clip.joints}
    ratio = lambda a, b: (a / b) if abs(b) > 1e-3 else 1.0
    joints = list(body.joints); ang = np.zeros((nb, len(joints)))
    for k, j in enumerate(joints):
        if j not in C: continue
        s_ = j[-1]; o = "r" if s_ == "l" else "l"; c = C[j]; m = c.mean()
        w_stiff, w_limp, w_hold, w_weak = G_w(st.stiff_side, s_), G_w(st.limp_side, s_), G_w(st.hold_side, s_), G_w(st.weak_side, s_)
        w_limp_o = G_w(st.limp_side, o); p_leg = ph[s_]; p_arm = p_root - (dr if s_ == "r" else 0.0)
        if j.startswith("hip_y"):
            scale = 1.0 - (1.0 - st.weak_scale) * w_weak
            amp = (st.hip_amp * scale * (1.0 - w_hold) + st.stiff_lift * w_stiff + st.hold_amp * w_hold) / ref.hip_amp
            ang[:, k] = m + (st.hip_off - ref.hip_off) + st.hold_hip * w_hold + amp * (_sample(c, p_leg) - m)
        elif j.startswith("knee"):
            knee_scale = 1.0 - (1.0 - st.stiff_knee) * w_stiff; kmin = c.min()
            amp = (st.knee_amp * knee_scale + st.limp_lift * w_limp_o) / ref.knee_amp
            ang[:, k] = kmin + (st.knee_off - ref.knee_off) + st.limp_sink * w_limp_o + amp * (_sample(c, p_leg + (st.knee_lag - ref.knee_lag) / (2 * np.pi)) - kmin)
        elif j.startswith("ankle_y"):
            ang[:, k] = m + ratio(st.ankle_amp, ref.ankle_amp) * (_sample(c, p_leg + (st.ankle_lag - ref.ankle_lag) / (2 * np.pi)) - m)
        elif j.startswith("hip_x"):
            ang[:, k] = m + SGN[s_] * (st.abd_off - ref.abd_off) + ratio(st.abd_amp, ref.abd_amp) * (_sample(c, p_leg + (st.abd_lag - ref.abd_lag) / (2 * np.pi)) - m)
        elif j.startswith("ankle_x"):
            ang[:, k] = m + ratio(st.ankle_x_amp, ref.ankle_x_amp) * (_sample(c, p_leg + (st.abd_lag - ref.abd_lag) / (2 * np.pi)) - m)
        elif j.startswith("shoulder"):
            ang[:, k] = m + (st.arm_off - ref.arm_off) + ratio(st.arm_amp, ref.arm_amp) * (_sample(c, p_arm + (st.arm_lag - ref.arm_lag) / (2 * np.pi)) - m)
        elif j.startswith("elbow"):
            ang[:, k] = _sample(c, p_arm) + (st.elbow_off - ref.elbow_off)
        else:
            ang[:, k] = c
    pS, rS, yS, lS = grammar_root(st, body, nb); pR, rR, yR, lR = grammar_root(ref, body, nb)
    RS = Rotation.from_euler("xyz", np.stack([rS, pS, np.zeros(nb)], 1)); RR = Rotation.from_euler("xyz", np.stack([rR, pR, np.zeros(nb)], 1))
    qc = _qsample(clip.quat, p_root)
    Rc = Rotation.from_quat(qc[:, [1, 2, 3, 0]]); Re = (RS * RR.inv() * Rc).as_quat(); quat = Re[:, [3, 0, 1, 2]]
    z = _sample(clip.z, p_root) + (lS - lR)
    y = _sample(clip.dy[:nb], p_root) + (yS - yR); dy = np.concatenate([y, y[:1]])
    dur = clip.dur * ref.freq / st.freq
    prof = CycleProfile(body.morph, joints, ang, z, quat, dur, clip.dx, dy)
    fl = clip_stance(nb); stance = [{s_: fl[int(np.floor(np.mod(ph[s_][b], 1.0) * nb + 1e-9)) % nb][s_] for s_ in SIDES} for b in range(nb)]
    key = ("raw", body.morph, nb)
    if key not in _cache:
        raw = CycleProfile(body.morph, joints, np.array([[C[j][b] if j in C else 0.0 for j in joints] for b in range(nb)]), clip.z, clip.quat, clip.dur, clip.dx, clip.dy)
        _cache[key] = stride(raw, body, fl)
    s0 = _cache[key]
    prof.dx = clip.dx * (stride(prof, body, stance) / s0 if s0 > 1e-6 else 1.0)
    return prof


def _longest_run(down, close=2):
    """Start and end bins of the longest cyclic run of True, after closing gaps of up to `close` bins."""
    nb = len(down); d = np.array(down, bool).copy()
    for b in range(nb):
        if d[b]: continue
        k = 1
        while k <= close and not d[(b + k) % nb]: k += 1
        if k <= close and d[b - 1] and d[(b + k) % nb]:
            for i in range(k): d[(b + i) % nb] = True
    if d.all(): return (0, nb - 1)                    # a stance edit can cover the whole cycle: the foot's whole travel counts
    if not d.any(): return None
    starts = [b for b in range(nb) if d[b] and not d[b - 1]]; best = None
    for s0 in starts:
        e = s0
        while d[(e + 1) % nb]: e += 1
        if best is None or e - s0 > best[1] - best[0]: best = (s0, e)
    return best


def stride(prof: CycleProfile, body: Body, stance):
    """The kinematic stride over one cycle: for each leg, the extent of its foot's (or, without a foot,
    its thigh's) travel relative to the root over its stance, the longest run of that side's re-timed
    contact flags with gaps of up to two bins closed; the sum over legs. (The teacher's walk is a
    forward-leaning shuffle whose feet travel by knee flexion more than by hip swing, and its feet
    stay behind the pelvis, so touchdown-minus-toe-off does not read it: the prereg's pre-build
    check.) A body without legs has no stride and keeps the clip's progress."""
    nb = len(prof.angles); parts = {}
    for s_ in SIDES:
        for g in (f"foot_{s_}", f"thigh_{s_}"):
            if g in body.gid: parts[s_] = body.gid[g]; break
    if not parts: return 0.0
    xr = {s_: np.zeros(nb) for s_ in parts}
    for b in range(nb):
        q, z, quat = prof.at(b / nb); _pose(body, q, quat, prof.root_at(b / nb)[1], z)
        for s_, g in parts.items(): xr[s_][b] = float(body.d.geom_xpos[g][0])
    total = 0.0
    for s_ in parts:
        run = _longest_run([bool(stance[b][s_]) for b in range(nb)])
        if run is None: continue
        seg = xr[s_][[b % nb for b in range(run[0], run[1] + 1)]]
        total += float(seg.max() - seg.min())
    return float(total)


def edited_trajectory(st: GaitState, body: Body, ref: GaitState, clip: CycleProfile | None = None):
    """qpos over the window at FPS, the edited clip played by the cycle runtime. (T, nq)."""
    prof = edited_profile(st, body, ref, clip)
    return CyclePlayer(prof, body=body).frames(WINDOW[1] - WINDOW[0], FPS)


class EditedGaitCase(RG.GaitCase):
    """GaitCase with the clip as base: every state is an edit of the intact teacher's cycle."""
    def __init__(self, morph, seed=0, ref: GaitState | None = None):
        super().__init__(morph, seed)
        self.ref = ref or RG.load_v0()

    def trajectory(self, st: GaitState):
        return edited_trajectory(st, self.body, self.ref)

    def _consumers(self, st: GaitState):
        key = tuple(getattr(st, f) for f in st.__dataclass_fields__)
        if key in self._cache:
            return self._cache[key]
        out = RG.consumers(self.body, self.trajectory(st))
        self.evals += 1
        if len(self._cache) > 2000:
            self._cache.clear()
        self._cache[key] = out
        return out

    def with_target(self, target):
        c = EditedGaitCase.__new__(EditedGaitCase)
        c.__dict__.update(self.__dict__)
        c.target = dict(target); c.names = list(target)
        c.scale = RG.scales(target)
        c._cache = {}; c.evals = 0
        return c
