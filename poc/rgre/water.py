"""RGRE-1 water domain: chirp-token representations of splashes against the spectral water teacher.

Representation state: shared chirp parameters theta, a gain, an onset shift dt, and (for two causes) a pair
coefficient c1. Classes: floor (the base fit's own misfit, known from calibration, unrepairable), coordinate,
unary, tail, interaction. Repairs per docs/math-track-rgre1-prereg.md.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from reactive.metrics import rel_rmse
from w1_experiment import CENTRE, NL, region
from water.teacher import SpectralWater, WaterParams, _record, run_splash, run_wake
from water.tokens import KERNELS

chirp = KERNELS["chirp"][0]
CLASSES = ("floor", "coordinate", "unary", "tail", "interaction")
REPAIRS = [("shift", "coordinate"), ("gain", "unary"), ("shape", "unary"), ("pair", "interaction"), ("lam", "tail"), ("m", "tail")]
REPAIR_SETS = {c: [r for r, cc in REPAIRS if cc == c] for c in CLASSES}
COSTS = {"shift": 1.0, "gain": 1.0, "shape": 3.0, "pair": 1.0, "lam": 1.0, "m": 1.0}
SHIFT_GRID = np.linspace(-0.15, 0.05, 41)
PAIR_GRID = np.linspace(-0.4, 0.4, 41)
LAM_GRID = np.array([0.25, 0.35, 0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0])
M_GRID = np.array([-1.0, -0.7, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.7, 1.0])
UNARY = ("g_eff", "v_max", "k_cut")
FPS = 60


@dataclass(frozen=True)
class WState:
    theta: tuple  # sorted (key, value) pairs
    gain: float = 1.0
    dt: float = 0.0
    c1: float = 0.0

    def th(self):
        return dict(self.theta)


def mk_state(theta: dict, **kw):
    return WState(tuple(sorted(theta.items())), **kw)


class Grid:
    def __init__(self, p: WaterParams, centre):
        self.p = p
        xs = np.arange(p.n) * p.dx
        X, Y = np.meshgrid(xs, xs, indexing="ij")
        self.times_all = np.arange(int(p.duration * p.fps) + 1) / p.fps
        self.ok = self.times_all >= 0.15
        r = np.sqrt((X - centre[0]) ** 2 + (Y - centre[1]) ** 2)
        self.sub = (r < 1.6) & (np.arange(p.n)[:, None] % 3 == 0) & (np.arange(p.n)[None, :] % 3 == 0)
        self.ev = r < 2.0
        self.fit_pts, self.eval_pts = np.stack([X[self.sub], Y[self.sub]], -1), np.stack([X[self.ev], Y[self.ev]], -1)
        self.fit_frames = np.flatnonzero(self.ok)[::2]
        self.t_fit, self.t_eval = self.times_all[self.fit_frames], self.times_all[self.ok]


def base_params(**kw):
    return WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **kw)


def token_field(state: WState, centres, pts, times, theta_base=None, dt_override=None):
    th = state.th()
    dt = state.dt if dt_override is None else dt_override
    out = np.zeros((len(times), pts.shape[0]))
    for c in centres:
        r = np.linalg.norm(pts - np.asarray(c)[None, :], axis=1)[None, :]
        out += state.gain * np.stack([chirp(r, np.array([[t - dt]]), th)[0] for t in times])
    if len(centres) == 2 and state.c1 != 0.0:
        mid = 0.5 * (np.asarray(centres[0]) + np.asarray(centres[1]))
        r = np.linalg.norm(pts - mid[None, :], axis=1)[None, :]
        tb = theta_base or th
        out += state.c1 * state.gain ** 2 * np.stack([chirp(r, np.array([[t]]), tb)[0] for t in times])
    return out


class WaterCase:
    def __init__(self, name, classes, eta, centres, grid: Grid, state0: WState, theta0: dict, floor_full=None):
        self.name, self.classes, self.centres, self.g, self.theta0 = name, tuple(classes), [tuple(c) for c in centres], grid, theta0
        self.tgt = eta[grid.ok][:, grid.ev]
        self.ref_fit = eta[grid.fit_frames][:, grid.sub]
        self.state0 = state0
        self.floor_full = floor_full
        self._cache: dict = {}

    def field(self, s: WState, where="eval"):
        if where == "eval":
            return token_field(s, self.centres, self.g.eval_pts, self.g.t_eval, self.theta0)
        return token_field(s, self.centres, self.g.fit_pts, self.g.t_fit, self.theta0)

    def evaluate(self, s: WState):
        if s not in self._cache:
            pred = self.field(s)
            self._cache[s] = (rel_rmse(pred, self.tgt), pred)
        return self._cache[s]

    def E(self, s):
        return self.evaluate(s)[0]

    def E_fit(self, s):
        return rel_rmse(self.field(s, "fit"), self.ref_fit)

    def residual(self, s):
        E, pred = self.evaluate(s)
        return self.tgt - pred, pred

    def floor_field(self, s: WState):
        """The base fit's own misfit at A = 1, translated to each cause and scaled by the gain."""
        if self.floor_full is None:
            return None
        out = np.zeros_like(self.tgt)
        n = self.g.p.n
        for c in self.centres:
            di, dj = int(round((c[0] - CENTRE[0]) / self.g.p.dx)), int(round((c[1] - CENTRE[1]) / self.g.p.dx))
            f = np.roll(np.roll(self.floor_full, di, axis=1), dj, axis=2) if (di or dj) else self.floor_full
            out += s.gain * f[:, self.g.ev]
        return out

    def diagnostics(self, s: WState, pred):
        h = 1.0 / 240.0
        d_t = (self.field(replace(s, dt=s.dt - h)) - self.field(replace(s, dt=s.dt + h))) / (2 * h)
        signed = {"coordinate": [d_t], "unary": [pred / max(s.gain, 1e-9)], "tail": []}
        th = s.th()
        for k in UNARY + ("lam", "m"):
            v = th[k]
            hp = 1e-2 * abs(v) if v != 0 else 1e-3
            tp, tm = dict(th), dict(th)
            tp[k], tm[k] = v + hp, v - hp
            d = (self.field(replace(s, theta=tuple(sorted(tp.items())))) - self.field(replace(s, theta=tuple(sorted(tm.items()))))) / (2 * hp)
            (signed["unary"] if k in UNARY else signed["tail"]).append(d)
        fl = self.floor_field(s)
        if fl is not None:
            signed["floor"] = [fl]
        templates = {}
        if len(self.centres) == 2:
            f1 = token_field(replace(s, c1=0.0), [self.centres[0]], self.g.eval_pts, self.g.t_eval)
            f2 = token_field(replace(s, c1=0.0), [self.centres[1]], self.g.eval_pts, self.g.t_eval)
            templates["interaction"] = (np.abs(f1) * np.abs(f2)).sum(0)
        return signed, templates

    def apply(self, s: WState, name):
        if name == "shift":
            cands = [replace(s, dt=s.dt + d) for d in SHIFT_GRID]
        elif name == "lam":
            cands = [mk_state({**s.th(), "lam": s.th()["lam"] * m}, gain=s.gain, dt=s.dt, c1=s.c1) for m in LAM_GRID]
        elif name == "m":
            cands = [mk_state({**s.th(), "m": s.th()["m"] + d}, gain=s.gain, dt=s.dt, c1=s.c1) for d in M_GRID]
        elif name == "pair":
            if len(self.centres) != 2:
                return s, COSTS[name], self.E(s)
            cands = [replace(s, c1=s.c1 + c) for c in PAIR_GRID]
        elif name == "gain":
            p = self.field(s, "fit")
            g = float((p * self.ref_fit).sum() / max((p * p).sum(), 1e-30))
            s2 = replace(s, gain=s.gain * g)
            return s2, COSTS[name], self.E(s2)
        elif name == "shape":
            th = s.th()

            def loss(z):
                t2 = dict(th)
                for k, zk in zip(UNARY, z):
                    t2[k] = th[k] * np.exp(zk)
                return self.E_fit(mk_state(t2, gain=s.gain, dt=s.dt, c1=s.c1))
            res = minimize(loss, np.zeros(3), method="Powell", options={"maxfev": 150, "xtol": 1e-2, "ftol": 1e-4})
            t2 = dict(th)
            for k, zk in zip(UNARY, res.x):
                t2[k] = th[k] * np.exp(zk)
            s2 = mk_state(t2, gain=s.gain, dt=s.dt, c1=s.c1)
            return s2, COSTS[name], self.E(s2)
        else:
            raise ValueError(name)
        s2 = min(cands, key=self.E_fit)
        return s2, COSTS[name], self.E(s2)


# ---------------------------------------------------------------- teachers
def eta_linear_single(A=1.0, sigma=0.03, depth=0.4, nu=1e-4, gamma0=0.25, delay_frames=0, centre=CENTRE):
    p = base_params(depth=depth, nu=nu, gamma0=gamma0)
    eta = run_splash(p, centre[0], centre[1], v0=A, sigma=sigma).eta.astype(float)
    if delay_frames:
        out = np.zeros_like(eta)
        out[delay_frames:] = eta[:-delay_frames]
        eta = out
    return eta, p


def eta_nonlinear_single(A):
    p = base_params(**NL)
    return run_splash(p, CENTRE[0], CENTRE[1], v0=A, sigma=0.03).eta.astype(float), p


def eta_nonlinear_pair(A, D):
    p = base_params(**NL)
    sim = SpectralWater(p)
    sim.add_impulse(CENTRE[0] - D / 2, CENTRE[1], A, 0.03)
    sim.add_impulse(CENTRE[0] + D / 2, CENTRE[1], A, 0.03)
    return _record(sim, p, None).eta.astype(float), p


def eta_hidden(A2, offset):
    p = base_params()
    sim = SpectralWater(p)
    sim.add_impulse(CENTRE[0], CENTRE[1], 1.0, 0.03)
    sim.add_impulse(CENTRE[0] + offset[0], CENTRE[1] + offset[1], A2, 0.03)
    return _record(sim, p, None).eta.astype(float), p


def eta_moving():
    p = base_params()
    return run_wake(p, (CENTRE[0] - 0.25, CENTRE[1]), (1.25, 0.0), 0.4, p0=0.08, sigma=0.05).eta.astype(float), p


def fit_single(theta0, eta, grid, A, with_shift=True):
    """W4's direct fit of a single splash: least-squares gain, and the onset shift on a grid if asked."""
    ref = eta[grid.fit_frames][:, grid.sub]

    def profiled(dt):
        K = token_field(mk_state(theta0, gain=1.0, dt=dt), [CENTRE], grid.fit_pts, grid.t_fit)
        g = float((K * ref).sum() / max((K * K).sum(), 1e-30))
        return rel_rmse(g * K, ref), g
    if not with_shift:
        return 0.0, profiled(0.0)[1]
    best = min(np.arange(-0.2, 0.021, 0.004), key=lambda d: profiled(d)[0])
    return float(best), profiled(best)[1]


def floor_field_full(theta0, grid):
    eta, _ = eta_linear_single(1.0)
    xs = np.arange(grid.p.n) * grid.p.dx
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel()], -1)
    tok = token_field(mk_state(theta0), [CENTRE], pts, grid.t_eval).reshape(len(grid.t_eval), grid.p.n, grid.p.n)
    return (eta[grid.ok] - tok).astype(np.float32)


def fresh_cases(theta0, grid, floor_full, log=print):
    cases, mixtures, unknown = [], [], []
    base = mk_state(theta0)
    for k, df in enumerate((3, 4, 5, 6, 7, 8)):
        eta, _ = eta_linear_single(1.0, delay_frames=df)
        cases.append(WaterCase(f"coordinate_{k}", ("coordinate",), eta, [CENTRE], grid, base, theta0, floor_full))
        log(f"  built coordinate_{k} (delay {df} frames)")
    for k, kw in enumerate(({"sigma": 0.02}, {"sigma": 0.025}, {"sigma": 0.04}, {"sigma": 0.05}, {"depth": 0.25}, {"depth": 0.7})):
        eta, _ = eta_linear_single(1.0, **kw)
        cases.append(WaterCase(f"unary_{k}", ("unary",), eta, [CENTRE], grid, base, theta0, floor_full))
        log(f"  built unary_{k} {kw}")
    for k, kw in enumerate(({"nu": 4e-4}, {"nu": 7e-4}, {"nu": 1e-3}, {"gamma0": 0.5}, {"gamma0": 0.75}, {"gamma0": 1.0})):
        eta, _ = eta_linear_single(1.0, **kw)
        cases.append(WaterCase(f"tail_{k}", ("tail",), eta, [CENTRE], grid, base, theta0, floor_full))
        log(f"  built tail_{k} {kw}")
    for k, (A, D) in enumerate(((5.0, 0.1875), (6.0, 0.28125), (8.0, 0.1875), (8.0, 0.28125), (6.0, 0.1875), (5.0, 0.28125))):
        single, _ = eta_nonlinear_single(A)
        dt, gain = fit_single(theta0, single, grid, A, with_shift=True)
        eta, _ = eta_nonlinear_pair(A, D)
        cen = [(CENTRE[0] - D / 2, CENTRE[1]), (CENTRE[0] + D / 2, CENTRE[1])]
        cases.append(WaterCase(f"interaction_{k}", ("interaction",), eta, cen, grid, mk_state(theta0, gain=gain, dt=dt), theta0, floor_full))
        log(f"  built interaction_{k} A={A} D={D} (single fit gain {gain:.2f} dt {dt*1e3:+.0f} ms)")
    for k, A in enumerate((3.5, 5.0, 7.0)):
        eta, _ = eta_nonlinear_single(A)
        mixtures.append(WaterCase(f"mix_coordinate_unary_{k}", ("coordinate", "unary"), eta, [CENTRE], grid, mk_state(theta0, gain=A), theta0, floor_full))
        log(f"  built mix_coordinate_unary_{k} A={A}")
    for k, (A, D) in enumerate(((6.0, 0.28125), (8.0, 0.1875))):
        single, _ = eta_nonlinear_single(A)
        _, gain = fit_single(theta0, single, grid, A, with_shift=False)
        eta, _ = eta_nonlinear_pair(A, D)
        cen = [(CENTRE[0] - D / 2, CENTRE[1]), (CENTRE[0] + D / 2, CENTRE[1])]
        mixtures.append(WaterCase(f"mix_interaction_coordinate_{k}", ("interaction", "coordinate"), eta, cen, grid, mk_state(theta0, gain=gain), theta0, floor_full))
        log(f"  built mix_interaction_coordinate_{k}")
    eta, _ = eta_linear_single(1.0, sigma=0.045, nu=1e-3)
    mixtures.append(WaterCase("mix_tail_unary_0", ("tail", "unary"), eta, [CENTRE], grid, base, theta0, floor_full))
    for k, off in enumerate(((1.4, 0.0), (0.0, -1.6))):
        eta, _ = eta_hidden(0.5, off)
        unknown.append(WaterCase(f"unknown_hidden_{k}", ("unknown",), eta, [CENTRE], grid, base, theta0, floor_full))
    eta, _ = eta_moving()
    unknown.append(WaterCase("unknown_moving_0", ("unknown",), eta, [CENTRE], grid, base, theta0, floor_full))
    log("  built unknowns")
    return cases, mixtures, unknown


def old_cases(theta0, grid, floor_full):
    out = []
    for A in (4.0, 6.0, 8.0):
        eta, _ = eta_nonlinear_single(A)
        out.append(WaterCase(f"old_A{A:g}", ("coordinate", "unary"), eta, [CENTRE], grid, mk_state(theta0, gain=A), theta0, floor_full))
    return out
