"""RGRE-1 corn domain: path-compression representations of a walker's wake, the wake+presence consumer.

Teacher F = the reference consumer field of the dense 200 Hz path with the reference kernel (plus, for
unknown cases, a field the representation knows nothing about). Representation = a spacetime polyline
(vertices chosen by a DP from the dense samples) with pass times, a global time offset, and the kernel's
persistence / width / amplitude multipliers. Classes and repairs per docs/math-track-rgre1-prereg.md.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

import b2_experiment as b2
import b3_experiment as b3
import b4_experiment as b4
import b5_experiment as b5
from reactive.causes import PathToken
from reactive.worldlines import HZ, RAMP, T_TOTAL, Worldline, _build, ramp_speed, turns_heading

TOL_BASE = 0.03
M_PAR = 0.0231
DTHETA = 0.08
VERTEX_COST = 3.0
PARAM_COST = 1.0
CLASSES = ("coordinate", "stop", "corner", "smooth", "tail", "unary")
REPAIRS = [("shift", "coordinate"), ("events", "stop"), ("corner_tighten", "corner"), ("tangent_alloc", "corner"),
           ("smooth_adaptive", "smooth"), ("smooth_uniform", "smooth"), ("decay", "tail"), ("width", "unary"), ("amp", "unary")]
REPAIR_SETS = {c: [r for r, cc in REPAIRS if cc == c] for c in CLASSES}
SHIFT_GRID = np.linspace(-0.2, 0.2, 21)
MULT_GRID = np.array([0.25, 0.35, 0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0])
WIDTH_GRID = np.array([0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.4, 1.7, 2.0])
FPS = b2.FPS


@dataclass(frozen=True)
class State:
    tol_scale: float = 1.0
    corner_scale: float = 1.0
    adaptive: bool = False
    tangent: bool = False
    interior_events: bool = True
    edge_events: bool = True
    tau0: float = 0.0
    lam_mult: float = 1.0
    w_mult: float = 1.0
    B_mult: float = 1.0


def dp(points, times, weights, tol, forced, tangents=None, moving=None, dtheta=None):
    """Spacetime DP with per-sample weights and an optional chord-direction criterion."""
    keep = np.zeros(len(points), dtype=bool)
    keep[0] = keep[-1] = True
    if forced is not None and len(forced):
        keep[np.asarray(forced, int)] = True
    anchors = np.flatnonzero(keep)
    stack = [(anchors[k], anchors[k + 1]) for k in range(len(anchors) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        u = (times[a + 1:b] - times[a]) / max(times[b] - times[a], 1e-12)
        phat = points[a] + u[:, None] * (points[b] - points[a])
        v = weights[a + 1:b] * np.linalg.norm(points[a + 1:b] - phat, axis=1) / tol
        if tangents is not None:
            chord = points[b] - points[a]
            L = np.linalg.norm(chord)
            if L > 1e-9:
                cosang = np.clip((tangents[a + 1:b] * (chord / L)[None, :]).sum(1), -1.0, 1.0)
                ang = np.where(moving[a + 1:b], np.arccos(cosang) / dtheta, 0.0)
                v = np.maximum(v, ang)
        i = int(np.argmax(v))
        if v[i] > 1.0:
            keep[a + 1 + i] = True
            stack.append((a, a + 1 + i))
            stack.append((a + 1 + i, b))
    return np.flatnonzero(keep)


def stop_intervals_all(w):
    """Every zero-speed interval of at least 0.2 s except the launch sample: interior and terminal stops."""
    still = w.speed <= b2.STOP_SPEED
    edges = np.flatnonzero(still[1:] != still[:-1]) + 1
    bounds = np.concatenate([[0], edges, [len(still)]])
    out = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        if still[a]:
            ta, tb = w.times[a], w.times[min(b, len(w.times) - 1)]
            if tb - ta >= 0.2 and ta >= 0.3:
                out.append((int(a), int(b)))
    return out


class CornCase:
    def __init__(self, name, w: Worldline, model0, classes, state0: State, extra_field=None, hidden: Worldline | None = None):
        self.name, self.w, self.model0, self.classes, self.state0 = name, w, model0, tuple(classes), state0
        self.pos = b4.strip_grid(w)
        self.times = np.arange(int(w.times[-1] * FPS) + 1) / FPS
        self.cons = b2.Consumer(model0, self.pos, self.times)
        self.ref, g = self.cons.field(w, PathToken(w.points, w.times))
        if hidden is not None:
            self.ref = self.ref + b2.Consumer(model0, self.pos, self.times).field(hidden, PathToken(hidden.points, hidden.times))[0]
        if extra_field is not None:
            self.ref = self.ref + extra_field(self.pos, self.times)
        self.scored = (g.path_dperp < b2.LOCAL_R) & b4.unambiguous(self.pos, w)
        self.norm = float(np.linalg.norm(self.ref[:, self.scored]))
        idx = np.clip(np.searchsorted(w.times, g.path_tpass), 0, len(w.times) - 1)
        foot = w.points[idx]
        self.mask_C = np.zeros(len(self.pos), bool)
        for i0, i1, _ in b3.corners(w):
            self.mask_C |= np.linalg.norm(foot[:, None, :] - w.points[i0:i1][None], axis=-1).min(1) <= b5.DELTA_M
        self.mask_T = np.zeros(len(self.pos), bool)
        for a, b in stop_intervals_all(w):
            self.mask_T |= np.linalg.norm(foot[:, None, :] - w.points[a:b][None], axis=-1).min(1) <= b5.DELTA_M
        a_par, a_perp = b3.frenet(w)
        dens = (M_PAR * a_par ** 2 + a_perp ** 2) ** 0.25
        self.dens_stalk = dens[idx]
        self.tangents = b5.dense_tangents(w)
        self.moving = w.speed > b2.STOP_SPEED
        ev = b2.event_vertices(w.speed)
        self.interior_events = np.array([i for i in ev if 0.3 < w.times[i] < w.t_walk - 0.3], int)
        self.edge_events = np.array([i for i in ev if not (0.3 < w.times[i] < w.t_walk - 0.3)], int)
        self.corner_samples = b5.corner_neigh(w)
        sm = self.moving & ~self.corner_samples
        self.smooth_w = np.where(sm, 1.0 + dens / max(dens[sm].mean(), 1e-9), 1.0) if sm.any() else np.ones(len(w.times))
        self._cache: dict = {}

    # ---- representation ----
    def model(self, s: State):
        m = self.model0.copy()
        for t in m.terms:
            if t.prim.name == "wake":
                t.params["lam"] *= s.lam_mult
                t.params["w"] *= s.w_mult
                t.params["B"] *= s.B_mult
        return m

    def vertices(self, s: State):
        w = self.w
        parts = ([self.edge_events] if s.edge_events else []) + ([self.interior_events] if s.interior_events else [])
        forced = np.concatenate(parts) if parts else np.zeros(0, int)
        weights = np.ones(len(w.times))
        if s.corner_scale < 1.0:
            weights[self.corner_samples] = 1.0 / s.corner_scale
        if s.adaptive:
            weights = weights * self.smooth_w
        tol = TOL_BASE * s.tol_scale
        if s.tangent:
            return dp(w.points, w.times, weights, tol, forced, self.tangents, self.moving, DTHETA)
        return dp(w.points, w.times, weights, tol, forced)

    def field(self, s: State, model=None):
        idx = self.vertices(s)
        cons = b2.Consumer(model or self.model(s), self.pos, self.times)
        pred, _ = cons.field(self.w, PathToken(self.w.points[idx], self.w.times[idx] + s.tau0))
        return pred, idx

    def error(self, pred):
        return float(np.linalg.norm((pred - self.ref)[:, self.scored]) / self.norm)

    def evaluate(self, s: State):
        key = s
        if key not in self._cache:
            pred, idx = self.field(s)
            self._cache[key] = (self.error(pred), int(len(idx)), pred)
        return self._cache[key]

    def E(self, s: State):
        return self.evaluate(s)[0]

    # ---- diagnostics (representation and kinematics only) ----
    def flat(self, arr):
        return arr[:, self.scored, :].transpose(0, 2, 1).reshape(-1, int(self.scored.sum()))

    def residual(self, s: State):
        E, n, pred = self.evaluate(s)
        return self.flat(self.ref - pred), pred

    def diagnostics(self, s: State, pred):
        h = 0.01
        d_tau = (self.field(replace(s, tau0=s.tau0 + h))[0] - self.field(replace(s, tau0=s.tau0 - h))[0]) / (2 * h)

        def dparam(attr):
            v = getattr(s, attr)
            hp = 0.05 * v
            return (self.field(replace(s, **{attr: v + hp}))[0] - self.field(replace(s, **{attr: v - hp}))[0]) / (2 * hp)
        signed = {"coordinate": [self.flat(d_tau)], "tail": [self.flat(dparam("lam_mult"))], "unary": [self.flat(dparam("w_mult")), self.flat(dparam("B_mult"))]}
        Ehat = (pred ** 2).sum((0, 2))
        sc = self.scored
        C, T = self.mask_C & sc, self.mask_T & sc
        Sm = sc & ~C & ~T
        templates = {"corner": (Ehat * C)[sc], "stop": (Ehat * T)[sc], "smooth": (Ehat * self.dens_stalk * Sm)[sc]}
        return signed, templates

    # ---- repairs ----
    def apply(self, s: State, name):
        E0, n0, pred0 = self.evaluate(s)
        if name == "shift":
            cands = [replace(s, tau0=s.tau0 + d) for d in SHIFT_GRID]
            s2 = min(cands, key=self.E)
            return s2, PARAM_COST, self.E(s2)
        if name == "decay":
            cands = [replace(s, lam_mult=s.lam_mult * m) for m in MULT_GRID]
            s2 = min(cands, key=self.E)
            return s2, PARAM_COST, self.E(s2)
        if name == "width":
            cands = [replace(s, w_mult=s.w_mult * m) for m in WIDTH_GRID]
            s2 = min(cands, key=self.E)
            return s2, PARAM_COST, self.E(s2)
        if name == "amp":
            p, r = pred0[:, self.scored], self.ref[:, self.scored]
            g = float((p * r).sum() / max((p * p).sum(), 1e-30))
            s2 = replace(s, B_mult=s.B_mult * g)
            return s2, PARAM_COST, self.E(s2)
        if name == "events":
            s2 = replace(s, interior_events=True, edge_events=True)
        elif name == "corner_tighten":
            s2 = replace(s, corner_scale=s.corner_scale * 0.5)
        elif name == "tangent_alloc":
            s2 = replace(s, tangent=True)
        elif name == "smooth_adaptive":
            s2 = replace(s, adaptive=True)
        elif name == "smooth_uniform":
            s2 = replace(s, tol_scale=s.tol_scale * 0.5)
        else:
            raise ValueError(name)
        E2, n2, _ = self.evaluate(s2)
        return s2, max(VERTEX_COST * (n2 - n0), PARAM_COST), E2


# ---------------------------------------------------------------- fresh trajectory generators (seeded)
def _heading(rng, t, n=3, amp=(0.25, 0.7), freq=(0.08, 0.3)):
    th = np.zeros_like(t)
    dth = np.zeros_like(t)
    for _ in range(n):
        a, f, ph = rng.uniform(*amp), rng.uniform(*freq), rng.uniform(0, 2 * np.pi)
        th += a * np.sin(2 * np.pi * f * t + ph)
        dth += a * 2 * np.pi * f * np.cos(2 * np.pi * f * t + ph)
    return th, dth


def gentle_path(rng, name, amp=(0.05, 0.2)):
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    v0 = rng.uniform(0.9, 1.3)
    v, dv = ramp_speed(t, 0.0, 8.0, v0)
    th, dth = _heading(rng, t, amp=amp)
    dth = np.where(t < 8.0, dth, 0.0)
    return _build(name, (0.0, 0.0), t, v, dv, th, dth, 8.0)


def smooth_path(rng, name):
    for _ in range(50):
        t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
        v0 = rng.uniform(0.8, 1.4)
        v, dv = ramp_speed(t, 0.0, 8.0, v0)
        th, dth = _heading(rng, t, amp=(0.25, 0.7))
        dth = np.where(t < 8.0, dth, 0.0)
        if np.abs(dth).max() < 2.8 and np.abs(dth).max() > 0.8:
            return _build(name, (0.0, 0.0), t, v, dv, th, dth, 8.0)
    raise RuntimeError("no smooth path")


def corner_path(rng, name, n_corners=None, with_stop=False):
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    v0 = rng.uniform(0.9, 1.3)
    if with_stop:
        d1 = rng.uniform(2.5, 3.5)
        dwell = rng.uniform(0.5, 1.2)
        v1, dv1 = ramp_speed(t, 0.0, d1, v0)
        v2, dv2 = ramp_speed(t, d1 + dwell, 8.0, v0)
        v, dv = v1 + v2, dv1 + dv2
        t_walk = 8.0
        windows = [(0.8, d1 - 0.7), (d1 + dwell + 0.7, 7.3)]
    else:
        v, dv = ramp_speed(t, 0.0, 8.0, v0)
        t_walk = 8.0
        windows = [(1.0, 7.0)]
    n_c = n_corners if n_corners is not None else int(rng.integers(2, 5))
    turns = []
    for k in range(n_c):
        lo, hi = windows[k % len(windows)]
        for _ in range(100):
            tk = rng.uniform(lo, hi)
            if all(abs(tk - tj) >= 1.1 for tj, _ in turns):
                break
        ang = np.deg2rad(rng.uniform(50, 160)) * (1 if rng.random() < 0.5 else -1)
        turns.append((tk, ang))
    tau = rng.uniform(0.1, 0.3)
    th0, dth0 = _heading(rng, t, amp=(0.03, 0.12))
    th, dth = turns_heading(t, 0.0, turns, tau)
    dth = np.where(t < t_walk, dth + dth0, 0.0)
    return _build(name, (0.0, 0.0), t, v, dv, th + th0, dth, t_walk)


def stop_path(rng, name, n_stops=None):
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    v0 = rng.uniform(0.9, 1.3)
    n_s = n_stops if n_stops is not None else int(rng.integers(1, 3))
    v = np.zeros_like(t)
    dv = np.zeros_like(t)
    t_on = 0.0
    for k in range(n_s + 1):
        d = rng.uniform(1.4, 2.2)
        if t_on + d > 8.4:
            d = 8.4 - t_on
        s, ds = ramp_speed(t, t_on, t_on + d, v0)
        v += s
        dv += ds
        t_off = t_on + d
        t_on = t_off + (rng.uniform(0.4, 1.5) if k < n_s else 0.0)
    th, dth = _heading(rng, t, amp=(0.03, 0.12))
    dth = np.where(t < t_off, dth, 0.0)
    return _build(name, (0.0, 0.0), t, v, dv, th, dth, float(t_off))


def gust_field(rng):
    a = 0.15
    sigma = 1.5
    phi = rng.uniform(0, 2 * np.pi)
    c0 = np.array([rng.uniform(-1, 1), rng.uniform(-1, 1)])
    u = np.array([np.cos(phi + 1.2), np.sin(phi + 1.2)]) * 1.5
    d = np.array([np.cos(phi), np.sin(phi)])

    def f(pos, times):
        out = np.zeros((len(times), len(pos), 2))
        for i, t in enumerate(times):
            c = c0 + u * t
            env = np.exp(-((pos - c[None, :]) ** 2).sum(1) / (2 * sigma * sigma))
            out[i] = a * env[:, None] * d[None, :]
        return out
    return f


def hidden_walker(rng, w: Worldline):
    off = np.array([0.0, rng.uniform(0.9, 1.3) * (1 if rng.random() < 0.5 else -1)])
    return Worldline(w.name + "_hidden", w.times, w.points + off[None, :], w.accel, w.speed, w.heading_rate, w.t_walk)


def fresh_cases(model0, seed):
    rng = np.random.default_rng(seed)
    cases = []
    for k in range(6):
        cases.append(CornCase(f"smooth_{k}", smooth_path(rng, f"smooth_{k}"), model0, ("smooth",), State()))
    for k in range(6):
        cases.append(CornCase(f"corner_{k}", corner_path(rng, f"corner_{k}"), model0, ("corner",), State()))
    for k in range(6):
        cases.append(CornCase(f"stop_{k}", stop_path(rng, f"stop_{k}"), model0, ("stop",), State(interior_events=False, edge_events=False)))
    for k in range(6):
        tau = rng.uniform(0.05, 0.15) * (1 if rng.random() < 0.5 else -1)
        cases.append(CornCase(f"coordinate_{k}", gentle_path(rng, f"coordinate_{k}"), model0, ("coordinate",), State(tau0=tau)))
    for k in range(6):
        m = rng.uniform(0.3, 0.6) if k % 2 == 0 else rng.uniform(1.6, 3.0)
        cases.append(CornCase(f"tail_{k}", gentle_path(rng, f"tail_{k}"), model0, ("tail",), State(lam_mult=m)))
    for k in range(6):
        m = rng.uniform(0.5, 0.75) if k % 2 == 0 else rng.uniform(1.3, 1.8)
        cases.append(CornCase(f"unary_{k}", gentle_path(rng, f"unary_{k}"), model0, ("unary",), State(w_mult=m)))
    mixtures = []
    for k in range(2):
        mixtures.append(CornCase(f"mix_corner_stop_{k}", corner_path(rng, f"mix_corner_stop_{k}", with_stop=True), model0, ("corner", "stop"), State(interior_events=False, edge_events=False)))
    for k in range(2):
        tau = rng.uniform(0.06, 0.14) * (1 if rng.random() < 0.5 else -1)
        mixtures.append(CornCase(f"mix_coordinate_corner_{k}", corner_path(rng, f"mix_coordinate_corner_{k}"), model0, ("coordinate", "corner"), State(tau0=tau)))
    mixtures.append(CornCase("mix_tail_smooth_0", smooth_path(rng, "mix_tail_smooth_0"), model0, ("tail", "smooth"), State(lam_mult=rng.uniform(1.8, 2.8))))
    mixtures.append(CornCase("mix_unary_stop_0", stop_path(rng, "mix_unary_stop_0"), model0, ("unary", "stop"), State(interior_events=False, edge_events=False, w_mult=rng.uniform(0.5, 0.7))))
    unknown = []
    for k in range(2):
        unknown.append(CornCase(f"unknown_wind_{k}", gentle_path(rng, f"unknown_wind_{k}"), model0, ("unknown",), State(), extra_field=gust_field(rng)))
    wh = gentle_path(rng, "unknown_hidden_0")
    unknown.append(CornCase("unknown_hidden_0", wh, model0, ("unknown",), State(), hidden=hidden_walker(rng, wh)))
    return cases, mixtures, unknown


def old_cases(model0):
    """Calibration set for the abstention threshold: B5's fresh family under the base representation."""
    from reactive.worldlines import fresh_family
    out = []
    for w in fresh_family():
        cls = ("corner",) if w.name in ("three_corners", "reversal") else ("corner", "stop") if w.name == "corner_stop_corner" else ("smooth", "corner") if w.name == "bend_then_corner" else ("smooth",)
        out.append(CornCase("old_" + w.name, w, model0, cls, State()))
    return out
