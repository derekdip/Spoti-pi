"""The locomotion case for RGRE: a teacher trajectory, the consumers the game reads, the residual in
consumer space, and the class machinery (tangents, class fits, the hybrid selector) in the form the
fire used. The teacher is a qpos trajectory from poc/gait/teacher.py; the student is the grammar.

Consumers, each normalised by its own scale and width as the fire's were:
  contact   fraction of frames each contact part (feet, thighs, hands, pelvis) touches the floor,
            in six half-second bins: footsteps, haptics, decals
  root      forward speed; torso height and pitch in six bins; head height: pathing and what is seen
  reach     the hands' farthest forward and highest points relative to the torso: can it grab
  pose      every present joint's angle at twelve instants: the silhouette
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import numpy as np
import mujoco
from scipy.optimize import differential_evolution
from .grammar import GaitState, CLASSES, V0_CLASSES, RANGES, ON, EPS, Body, trajectory, is_on, turn_on, WINDOW, FPS
from . import biped

RESULTS = Path(__file__).resolve().parents[2] / "poc" / "results"
CONTACT_EPS = 0.015     # m: a part this close to the floor is in contact
BINS = 6
POSE_SAMPLES = 12


def teacher_qpos(morph, seed=0):
    q = np.load(RESULTS / f"gait_teacher_{morph}_s{seed}_qpos.npy")
    lo, hi = int(WINDOW[0] * FPS), int(WINDOW[1] * FPS)
    return q[lo:hi]


PHASE_BINS = 16


def cycles(ref, fps=FPS, lo=0.3, hi=2.5):
    """Cycle boundaries from a reference joint angle: upward crossings of its mean after smoothing.
    Returns a list of (start, end) frame indices; the whole window if no full cycle is found."""
    k = max(1, int(0.1 * fps))
    sm = np.convolve(ref - ref.mean(), np.ones(k) / k, mode="same")
    up = np.where((sm[:-1] < 0) & (sm[1:] >= 0))[0] + 1
    out = [(a, b) for a, b in zip(up[:-1], up[1:]) if lo * fps <= b - a <= hi * fps]
    return out if out else [(0, len(ref))]


def phase_mean(series, cyc, nb=PHASE_BINS):
    """(nb, ...) mean of a series over its cycles, each resampled to nb phase bins."""
    acc = np.zeros((nb,) + series.shape[1:]); n = 0
    for a, b in cyc:
        seg = series[a:b]
        idx = np.linspace(0, len(seg) - 1, nb).round().astype(int)
        acc += seg[idx]; n += 1
    return acc / max(n, 1)


def bouts(c):
    """Number of contact bouts and their mean length (frames) in a boolean series."""
    d = np.diff(np.concatenate([[0], c.astype(int), [0]]))
    starts = np.where(d == 1)[0]; ends = np.where(d == -1)[0]
    n = len(starts)
    return n, (float((ends - starts).mean()) if n else 0.0)


def consumers(body: Body, qpos):
    """The consumer blocks from a qpos trajectory (T, nq).

    Pilot fixes, in order: poses compared at absolute instants let a static crouch beat a walk with
    its phase slightly off, so periodic quantities are compared per phase bin of the body's own
    cycle; then two teacher runs of the same body differed more than the fitted grammar did from
    either, because two or three irregular cycles average into a smeared waveform, so the blocks
    that carry the gait's size are statistics that do not depend on timing: per-joint mean, spread
    and range, and per-part stance fraction, bout count and bout length. Speed, height and pitch
    are blocks of their own so that each is scaled by itself."""
    m, d = body.m, body.d
    T = len(qpos)
    torso = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso"); head = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "head")
    hands = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, f"hand_{s}") for s in ("l", "r")]
    gids = [body.gid[g] for g in body.contact_geoms]
    contact = np.zeros((T, len(gids))); tz = np.zeros(T); hz = np.zeros(T); reach = np.zeros((T, 4))
    for k in range(T):
        d.qpos[:] = qpos[k]; mujoco.mj_kinematics(m, d)
        contact[k] = body.lowest(gids) <= CONTACT_EPS
        tz[k] = d.xpos[torso][2]; hz[k] = d.xpos[head][2]
        for i, h in enumerate(hands):
            reach[k, 2 * i] = d.xpos[h][0] - d.xpos[torso][0]; reach[k, 2 * i + 1] = d.xpos[h][2]
    edges = np.linspace(0, T, BINS + 1).astype(int)
    binned = lambda v: np.array([v[a:b].mean(0) for a, b in zip(edges[:-1], edges[1:])])
    pitch = qpos[:, 2]
    speed = (qpos[-1, 0] - qpos[0, 0]) / ((T - 1) / FPS)
    ref_name = next(n for n in ("hip_l", "hip_r", "shoulder_l") if n in body.jadr)
    cyc = cycles(qpos[:, body.jadr[ref_name]])
    durations = np.array([(b - a) / FPS for a, b in cyc])
    joints = qpos[:, 3:]
    stance = []
    for j in range(contact.shape[1]):
        n, L = bouts(contact[:, j] > 0.5)
        stance += [contact[:, j].mean(), n / (T / FPS), L / FPS]
    out = {
        "contact_t": binned(contact).ravel(),
        "stance": np.array(stance),
        "joint_stats": np.concatenate([joints.mean(0), joints.std(0), joints.min(0), joints.max(0)]),
        "speed": np.array([speed]),
        "height": np.concatenate([binned(tz), [hz.mean()]]),
        "pitch": np.array([pitch.mean(), pitch.std()]),      # two teacher seeds disagree on pitch in time by 1.5 scales: statistics only
        "rhythm": np.array([1.0 / durations.mean(), durations.std() / durations.mean()]),
        "reach": np.array([reach[:, 0].max(), reach[:, 1].max(), reach[:, 2].max(), reach[:, 3].max()]),
        "pose_phase": phase_mean(joints, cyc).ravel(),
    }
    return out


class GaitCase:
    """One teacher trajectory and everything needed to score a grammar state against it."""

    def __init__(self, morph, seed=0):
        self.name = f"{morph}_s{seed}"; self.morph = morph; self.seed = seed
        self.body = Body(morph)
        self.q_teacher = teacher_qpos(morph, seed)
        self.target = consumers(self.body, self.q_teacher)
        self.names = list(self.target)
        self.scale = {k: float(np.sqrt((v ** 2).mean())) or 1.0 for k, v in self.target.items()}
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
        """(1, Ntot): every consumer block normalised by its scale and its width."""
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

    # ---- which classes can do anything on this body
    def repairable(self):
        has = self.body.has
        out = []
        for c in CLASSES:
            if c in V0_CLASSES: continue
            if c.endswith("_l") and not has["hip_l"]: continue
            if c.endswith("_r") and not has["hip_r"]: continue
            if c.startswith("stiff") or c.startswith("short"):
                if not has[f"knee_{c[-1]}"]: continue
            if c == "hop" and not (has["hip_l"] or has["hip_r"]): continue
            out.append(c)
        return out

    # ---- tangents: the direction each parameter moves the residual, before any fit
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
                    d = (self.residual(replace(st, **{p: nxt})).ravel() - base) / (nxt - cur)
                    if float(d @ d) > 0: vs.append(d)
            else:
                on = replace(st, **ON[cls]); r_on = self.residual(on).ravel()
                d = r_on - base
                if float(d @ d) > 0: vs.append(d)
                for p in CLASSES[cls]:
                    lo, hi = RANGES[p]; cur = getattr(on, p); h = EPS[p]
                    nxt = cur + h if cur + h <= hi else cur - h
                    if abs(nxt - cur) < 1e-12: continue
                    dd = self.residual(replace(on, **{p: nxt})).ravel() - r_on
                    if float(dd @ dd) > 0: vs.append(dd)
            if vs:
                signed[cls] = vs
        return signed


# ---------------------------------------------------------------- class fits, as the fire's
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
    """Coordinate descent over the class's parameters from the on-state, two rounds."""
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
    """V0: the walk base fitted to the intact teacher by differential evolution over the gait class."""
    names = CLASSES["gait"]
    bounds = [RANGES[p] for p in names]
    def f(x):
        return case.error(replace(GaitState(), **{n: float(v) for n, v in zip(names, x)}))
    r = differential_evolution(f, bounds, seed=seed, maxiter=maxiter, popsize=popsize, tol=1e-6, polish=False)
    st = replace(GaitState(), **{n: float(v) for n, v in zip(names, r.x)})
    return st, float(r.fun)


def joint_fit(case, st: GaitState, seed=0, maxiter=30, popsize=8):
    """The floor: every repairable parameter of every class free at once, from the given state."""
    names = list(CLASSES["gait"]) + [p for c in case.repairable() for p in CLASSES[c]]
    bounds = [RANGES[p] for p in names]
    x0 = np.array([getattr(st, p) for p in names])
    def f(x):
        return case.error(replace(st, **{n: float(v) for n, v in zip(names, x)}))
    r = differential_evolution(f, bounds, seed=seed, maxiter=maxiter, popsize=popsize, tol=1e-6, polish=False, x0=np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds]))
    return replace(st, **{n: float(v) for n, v in zip(names, r.x)}), float(r.fun)
