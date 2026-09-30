"""The 3D locomotion case for RGRE: poc/gait/rgre_gait.py on the free-rooted body. The consumers are
the 2D blocks with the joints that now exist, the torso's pitch and roll read from its up axis (no
Euler angles, so the prone body has no gimbal lock), and a lateral block (the root's sway about its
drift). Yaw and drift are left out: the grammar has no heading, so they would be a floor on every
body, not a residual a class could explain.

Blocks: contact_t, coupling, travel, stance, joint_stats, asym_joints, asym_stance, speed, height,
orient, lateral, rhythm, reach, pose_phase. Scales as 2D: each block by its own rms, the asymmetry blocks in their
parent block's units."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import numpy as np
import mujoco
from scipy.optimize import differential_evolution
from .grammar3d import GaitState, CLASSES, V0_CLASSES, BASE_PARAMS, IMPAIRMENTS, RANGES, ON, EPS, Body, trajectory, is_on, turn_on, WINDOW, FPS
from . import biped3d

RESULTS = Path(__file__).resolve().parents[2] / "poc" / "results"
CONTACT_EPS = 0.015
BINS = 6
PHASE_BINS = 16
V0_PATH = "poc/results/gait3d_v0.json"


def teacher_qpos(morph, seed=0):
    q = np.load(RESULTS / f"gait3d_teacher_{morph}_s{seed}_qpos.npy")
    lo, hi = int(WINDOW[0] * FPS), int(WINDOW[1] * FPS)
    return q[lo:hi]


def cycles_from_contact(c, fps=FPS, lo=0.5, hi=2.5):
    """Cycle boundaries as the touchdowns of one contact part (rising edges of its boolean series);
    None if fewer than two touchdowns a plausible cycle apart. The lower bound is half a second: the
    intact 3D teacher's foot chatters on touchdown, and 0.3 s let a bounce count as a cycle."""
    d = np.diff(np.concatenate([[0], c.astype(int)]))
    down = np.where(d == 1)[0]
    out = [(a, b) for a, b in zip(down[:-1], down[1:]) if lo * fps <= b - a <= hi * fps]
    return out if out else None


def cycles(ref, fps=FPS, lo=0.3, hi=2.5):
    k = max(1, int(0.1 * fps))
    sm = np.convolve(ref - ref.mean(), np.ones(k) / k, mode="same")
    up = np.where((sm[:-1] < 0) & (sm[1:] >= 0))[0] + 1
    out = [(a, b) for a, b in zip(up[:-1], up[1:]) if lo * fps <= b - a <= hi * fps]
    return out if out else [(0, len(ref))]


def phase_mean(series, cyc, nb=PHASE_BINS):
    acc = np.zeros((nb,) + series.shape[1:]); n = 0
    for a, b in cyc:
        seg = series[a:b]
        idx = np.linspace(0, len(seg) - 1, nb).round().astype(int)
        acc += seg[idx]; n += 1
    return acc / max(n, 1)


def bouts(c):
    d = np.diff(np.concatenate([[0], c.astype(int), [0]]))
    starts = np.where(d == 1)[0]; ends = np.where(d == -1)[0]
    n = len(starts)
    return n, (float((ends - starts).mean()) if n else 0.0)


PAIRS_J = ("hip_x", "hip_y", "knee", "ankle_y", "ankle_x", "shoulder")
PAIRS_G = ("foot", "thigh", "hand")


def consumers(body: Body, qpos):
    m, d = body.m, body.d
    T = len(qpos)
    torso = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso"); head = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "head")
    hands = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, f"hand_{s}") for s in ("l", "r")]
    gids = [body.gid[g] for g in body.contact_geoms]
    contact = np.zeros((T, len(gids))); tz = np.zeros(T); hz = np.zeros(T); reach = np.zeros((T, 4)); up = np.zeros((T, 2))
    gx = np.zeros((T, len(gids)))                                  # world x of every contact part's centre
    for k in range(T):
        d.qpos[:] = qpos[k]; mujoco.mj_kinematics(m, d)
        contact[k] = body.lowest(gids) <= CONTACT_EPS
        gx[k] = [d.geom_xpos[g][0] for g in gids]
        tz[k] = d.xpos[torso][2]; hz[k] = d.xpos[head][2]
        R = d.xmat[torso].reshape(3, 3); up[k] = R[0, 2], R[1, 2]        # the torso's up axis: x (pitch) and y (roll) components
        for i, h in enumerate(hands):
            reach[k, 2 * i] = d.xpos[h][0] - d.xpos[torso][0]; reach[k, 2 * i + 1] = d.xpos[h][2]
    edges = np.linspace(0, T, BINS + 1).astype(int)
    binned = lambda v: np.array([v[a:b].mean(0) for a, b in zip(edges[:-1], edges[1:])])
    speed = (qpos[-1, 0] - qpos[0, 0]) / ((T - 1) / FPS)
    yy = qpos[:, 1]; tt = np.arange(T); trend = np.polyval(np.polyfit(tt, yy, 1), tt)
    # pilot fix 1 (3D): the cycle clock is the touchdowns of the first contact part that has them
    # (left foot, else right, else a hand); the intact 3D teacher's left hip crossed its mean once in
    # four seconds and a hip-angle clock read a two-second cycle, which V0 then matched with both legs
    # in phase. The joint-angle clock remains the fallback.
    cyc = None
    for g in ("foot_l", "foot_r", "thigh_l", "thigh_r", "hand_l", "hand_r"):
        if g in body.gid:
            cyc = cycles_from_contact(contact[:, body.contact_geoms.index(g)] > 0.5)
            if cyc: break
    if not cyc:
        ref_name = next(n for n in ("hip_y_l", "hip_y_r", "shoulder_l") if n in body.jadr)
        cyc = cycles(qpos[:, body.jadr[ref_name]])
    durations = np.array([(b - a) / FPS for a, b in cyc])
    joints = qpos[:, 7:]
    stance = []
    for j in range(contact.shape[1]):
        n, L = bouts(contact[:, j] > 0.5)
        stance += [contact[:, j].mean(), n / (T / FPS), L / FPS]
    # pilot fix 1 (3D), with the clock: how many parts are down at once, as fractions of time with
    # none, one, and two or more. Alternating legs and legs in phase have the same per-part stance
    # fractions and differ here.
    nparts = (contact > 0.5).sum(1)
    stance += [float((nparts == 0).mean()), float((nparts == 1).mean()), float((nparts >= 2).mean())]
    jstats = {n: np.array([joints[:, i].mean(), joints[:, i].std(), joints[:, i].min(), joints[:, i].max()]) for i, n in enumerate(body.joints)}
    asym_j = [jstats[f"{j}_l"] - jstats[f"{j}_r"] for j in PAIRS_J if f"{j}_l" in jstats and f"{j}_r" in jstats]
    pstats = {g: np.array(stance[3 * i:3 * i + 3]) for i, g in enumerate(body.contact_geoms)}      # the support counts are not paired
    asym_p = [pstats[f"{g}_l"] - pstats[f"{g}_r"] for g in PAIRS_G if f"{g}_l" in pstats and f"{g}_r" in pstats]
    # pilot fix 3 (3D): left-right coupling, timing-free. With the teacher's cycles irregular, the
    # phase-averaged pose is a smeared waveform that a small in-phase student matches better than an
    # alternating one, and no other block reads which of the two it is; the correlation of each
    # left-right joint pair and each left-right contact pair over the window does.
    def corr(a, b_):
        return float(np.corrcoef(a, b_)[0, 1]) if a.std() > 1e-9 and b_.std() > 1e-9 else 0.0
    coupling = [corr(qpos[:, body.jadr[f"{j}_l"]], qpos[:, body.jadr[f"{j}_r"]]) for j in ("hip_y", "knee", "shoulder") if f"{j}_l" in body.jadr and f"{j}_r" in body.jadr]
    coupling += [corr(contact[:, body.contact_geoms.index(f"{g}_l")], contact[:, body.contact_geoms.index(f"{g}_r")]) for g in PAIRS_G if f"{g}_l" in body.gid and f"{g}_r" in body.gid]
    # pilot fix 4 (3D, G11): where the feet go in the world. Every other block is body-relative, and
    # the G10 states swung their feet forward at a third of the teacher's speed, backward on a third of
    # the swing frames, and read as stepping in place. Per stepping part (feet, thighs, hands): its
    # forward speed while off the floor, and the forward distance between its touchdowns.
    travel = []
    for i, g in enumerate(body.contact_geoms):
        if g == "pelvis": continue
        off = contact[:, i] < 0.5; v = np.diff(gx[:, i]) * FPS; sw = v[off[1:] & off[:-1]]
        down = ~off; td = np.where(down[1:] & ~down[:-1])[0] + 1
        travel += [float(sw.mean()) if len(sw) else 0.0, float(np.diff(gx[td, i]).mean()) if len(td) > 1 else 0.0]
    out = {
        "contact_t": binned(contact).ravel(),
        "coupling": np.array(coupling) if coupling else None,
        "travel": np.array(travel) if travel else None,
        "stance": np.array(stance),
        "joint_stats": np.concatenate([joints.mean(0), joints.std(0), joints.min(0), joints.max(0)]),
        "asym_joints": np.concatenate(asym_j) if asym_j else None,
        "asym_stance": np.concatenate(asym_p) if asym_p else None,
        "speed": np.array([speed]),
        "height": np.concatenate([binned(tz), [hz.mean()]]),
        "orient": np.array([up[:, 0].mean(), up[:, 0].std(), up[:, 1].mean(), up[:, 1].std()]),
        "lateral": np.array([(yy - trend).std()]),
        "rhythm": np.array([1.0 / durations.mean(), durations.std() / durations.mean()]),
        "reach": np.array([reach[:, 0].max(), reach[:, 1].max(), reach[:, 2].max(), reach[:, 3].max()]),
        "pose_phase": phase_mean(joints, cyc).ravel(),
    }
    return {k: v for k, v in out.items() if v is not None}


def scales(target):
    sc = {k: float(np.sqrt((v ** 2).mean())) or 1.0 for k, v in target.items()}
    if "asym_joints" in sc: sc["asym_joints"] = sc["joint_stats"]
    if "asym_stance" in sc: sc["asym_stance"] = sc["stance"]
    if "coupling" in sc: sc["coupling"] = 1.0        # a correlation has its own unit; its rms on a symmetric walk is small
    return sc


class GaitCase:
    def __init__(self, morph, seed=0):
        self.name = f"{morph}_s{seed}"; self.morph = morph; self.seed = seed
        self.body = Body(morph)
        self.q_teacher = teacher_qpos(morph, seed)
        self.target = consumers(self.body, self.q_teacher)
        self.names = list(self.target)
        self.scale = scales(self.target)
        self._cache = {}; self.evals = 0

    def _consumers(self, st: GaitState):
        key = tuple(getattr(st, f) for f in st.__dataclass_fields__)
        if key in self._cache:
            return self._cache[key]
        out = consumers(self.body, trajectory(st, self.body))
        self.evals += 1
        if len(self._cache) > 2000:
            self._cache.clear()
        self._cache[key] = out
        return out

    def residual(self, st: GaitState):
        p = self._consumers(st)
        parts = [(self.target[k] - p[k]) / (self.scale[k] * np.sqrt(len(self.target[k]))) for k in self.names]
        return np.concatenate(parts)[None, :]

    def error(self, st: GaitState):
        r = self.residual(st)
        return float(np.sqrt((r ** 2).sum() / len(self.names)))

    def per_consumer(self, st: GaitState):
        p = self._consumers(st)
        return {k: float(np.sqrt(((self.target[k] - p[k]) ** 2).mean()) / self.scale[k]) for k in self.names}

    def blocks(self):
        out, i = {}, 0
        for k in self.names:
            n = len(self.target[k]); out[k] = (i, i + n); i += n
        return out, i

    def templates(self):
        return {}

    def repairable(self):
        has = self.body.has
        legs = has["hip_y_l"] or has["hip_y_r"]; knees = has["knee_l"] or has["knee_r"]
        out = []
        for c in CLASSES:
            if c in V0_CLASSES:
                if c in ("legs", "lateral") and not legs: continue
                out.append(c); continue
            if c in ("stiff", "limp") and not knees: continue
            if c in ("hold", "weak") and not legs: continue
            out.append(c)
        return out

    def with_target(self, target):
        c = GaitCase.__new__(GaitCase)
        c.__dict__.update(self.__dict__)
        c.target = dict(target); c.names = list(target)
        c.scale = scales(target)
        c._cache = {}; c.evals = 0
        return c

    def tangents(self, st: GaitState):
        base = self.residual(st).ravel()
        signed = {}
        for cls in [c for c in CLASSES if c in V0_CLASSES or c in self.repairable()]:
            live = is_on(st, cls)
            vs = []
            if live:
                for p in CLASSES[cls]:
                    lo, hi = RANGES[p]; cur = getattr(st, p); h = EPS[p]
                    nxt = cur + h if cur + h <= hi else cur - h
                    if abs(nxt - cur) < 1e-12: continue
                    dd = (self.residual(replace(st, **{p: nxt})).ravel() - base) / (nxt - cur)
                    if float(dd @ dd) > 0: vs.append(dd)
            else:
                on = replace(st, **ON[cls]); r_on = self.residual(on).ravel()
                dd = r_on - base
                if float(dd @ dd) > 0: vs.append(dd)
                for p in CLASSES[cls]:
                    lo, hi = RANGES[p]; cur = getattr(on, p); h = EPS[p]
                    nxt = cur + h if cur + h <= hi else cur - h
                    if abs(nxt - cur) < 1e-12: continue
                    dd = self.residual(replace(on, **{p: nxt})).ravel() - r_on
                    if float(dd @ dd) > 0: vs.append(dd)
            if vs:
                signed[cls] = vs
        return signed


def _sweep(case, cur, pname, grid):
    lo, hi = RANGES[pname]
    vals = np.linspace(lo, hi, grid)
    errs = [case.error(replace(cur, **{pname: float(v)})) for v in vals]
    i = int(np.argmin(errs)); cur = replace(cur, **{pname: float(vals[i])})
    step = (hi - lo) / (grid - 1)
    fine = np.linspace(max(lo, vals[i] - step), min(hi, vals[i] + step), grid)
    errs2 = [case.error(replace(cur, **{pname: float(v)})) for v in fine]
    return replace(cur, **{pname: float(fine[int(np.argmin(errs2))])})


def fit_class(case, st: GaitState, cls, grid=7, rounds=2):
    cur = turn_on(st, cls)
    for _ in range(rounds):
        for p in CLASSES[cls]:
            cur = _sweep(case, cur, p, grid)
    return cur, case.error(cur)


def repair_gain(case, st: GaitState, cls):
    e0, c0 = case.error(st), st.cost()
    new, e1 = fit_class(case, st, cls)
    dc = max(new.cost() - c0, 1)
    return dict(cls=cls, state=new, e0=e0, e1=e1, gain=(e0 - e1) / dc, drop=e0 - e1, dcost=dc)


def fit_base(case, seed=0, maxiter=40, popsize=10):
    names = BASE_PARAMS
    bounds = [RANGES[p] for p in names]
    def f(x):
        return case.error(replace(GaitState(), **{n: float(v) for n, v in zip(names, x)}))
    r = differential_evolution(f, bounds, seed=seed, maxiter=maxiter, popsize=popsize, tol=1e-6, polish=False)
    st = replace(GaitState(), **{n: float(v) for n, v in zip(names, r.x)})
    return st, float(r.fun)


def load_v0(path=V0_PATH):
    import json
    v = json.load(open(path))["state"]
    return replace(GaitState(), **{k: v[k] for k in BASE_PARAMS if k in v})


def local_floor(case, st: GaitState, maxfev=4000):
    from scipy.optimize import minimize
    names = list(dict.fromkeys(BASE_PARAMS + [p for c in case.repairable() for p in CLASSES[c]]))
    lo = np.array([RANGES[p][0] for p in names]); hi = np.array([RANGES[p][1] for p in names])
    x0 = np.clip([getattr(st, p) for p in names], lo, hi)
    best = [case.error(st), st]
    def f(x):
        s2 = replace(st, **{n: float(v) for n, v in zip(names, np.clip(x, lo, hi))})
        e = case.error(s2)
        if e < best[0]:
            best[0], best[1] = e, s2
        return e
    minimize(f, x0, method="Powell", bounds=list(zip(lo, hi)), options=dict(maxfev=maxfev, xtol=1e-3, ftol=1e-6))
    return best[1], float(best[0])
