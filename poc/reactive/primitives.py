"""The cheap runtime grammar: closed-form, stateless primitives.

Every primitive is a pure function of (static geometry, time, params).
There is no per-stalk state and no integration, so there is no rollout
drift by construction and reconstruction is deterministic across clients
and replays. That is the corrected form of the write-up's spring model
(the per-frame integrated spring is frame-rate dependent).

Cost numbers are rough op counts per stalk per (live token) per frame,
for the search's cost term only. Real Quest cost must be profiled.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geometry import Geometry

LIVE_EPS = 1e-3  # a token whose envelope is below this fraction of peak is dead


@dataclass
class Param:
    name: str
    lo: float
    hi: float
    init: float


def spring_response(tau: np.ndarray, lam: float, k: float, zeta: float) -> np.ndarray:
    """Closed-form tip response of x'' + c x' + k x = k e^{-lam tau}, x(0)=x'(0)=0.

    Underdamped only (0 < zeta < 1). Returned normalised so its peak is 1.
    """
    c = 2.0 * zeta * np.sqrt(k)
    w = np.sqrt(k) * np.sqrt(max(1.0 - zeta * zeta, 1e-9))
    a = lam - 0.5 * c
    P = k / (a * a + w * w)

    def raw(x):
        x = np.maximum(x, 0.0)
        return P * (np.exp(-lam * x) - np.exp(-0.5 * c * x) * (np.cos(w * x) - (a / w) * np.sin(w * x)))

    grid = np.linspace(0.0, 4.0 / min(lam, 0.5 * c) + 2.0 * np.pi / w, 400)
    peak = np.max(np.abs(raw(grid)))
    return np.where(tau >= 0.0, raw(tau) / max(peak, 1e-12), 0.0)


class Primitive:
    name: str = "base"
    params: list[Param] = []
    cost: float = 0.0  # ops per stalk per live token per frame
    per_event: bool = False

    def evaluate(self, g: Geometry, times: np.ndarray, p: dict) -> tuple[np.ndarray, float]:
        """Return (bend (F,N,2), mean live token count per frame)."""
        raise NotImplementedError


def gkern(d: np.ndarray, w: float, q: float) -> np.ndarray:
    """Generalised Gaussian: q=2 is Gaussian, q=1 exponential, large q a box of half-width w."""
    return np.exp(-0.5 * (np.abs(d) / w) ** q)


def _mix_dir(a: np.ndarray, b: np.ndarray, mix: float) -> np.ndarray:
    d = (1.0 - mix) * a + mix * b
    return d / np.maximum(np.linalg.norm(d, axis=-1, keepdims=True), 1e-9)


class Presence(Primitive):
    """Live cause: the player is here right now. Gaussian push, outward mixed with travel direction."""

    name = "presence"
    params = [Param("A", 0.01, 1.0, 0.3), Param("sigma", 0.05, 1.5, 0.35), Param("mix", 0.0, 1.0, 0.3), Param("q", 0.5, 4.0, 2.0)]
    cost = 22.0

    def evaluate(self, g, times, p):
        P = g.player.position(times)  # (F, 2)
        V = g.player.velocity(times)
        V = V / np.maximum(np.linalg.norm(V, axis=-1, keepdims=True), 1e-6)
        dvec = g.pos[None, :, :] - P[:, None, :]
        d = np.linalg.norm(dvec, axis=-1)
        out = dvec / np.maximum(d, 1e-6)[..., None]
        amp = p["A"] * gkern(d, p["sigma"], p["q"])
        return amp[..., None] * _mix_dir(out, V[:, None, :], p["mix"]), 1.0


class RadialImpulse(Primitive):
    """Per event: Gaussian in space, closed-form spring response in time."""

    name = "radial_impulse"
    params = [
        Param("A", 0.01, 1.0, 0.3),
        Param("sigma", 0.05, 1.5, 0.35),
        Param("lam", 0.1, 20.0, 2.0),
        Param("k", 5.0, 200.0, 40.0),
        Param("zeta", 0.05, 0.95, 0.3),
        Param("mix", 0.0, 1.0, 0.3),
        Param("q", 0.5, 4.0, 2.0),
    ]
    cost = 24.0
    per_event = True

    def evaluate(self, g, times, p):
        tau = times[:, None] - g.ev_t0[None, :]  # (F, E)
        env = spring_response(tau, p["lam"], p["k"], p["zeta"])
        live = np.abs(env) > LIVE_EPS
        env = np.where(live, env, 0.0)
        space = gkern(g.ev_d, p["sigma"], p["q"])  # (N, E)
        dirs = _mix_dir(g.ev_out, g.ev_dir[None, :, :], p["mix"])  # (N, E, 2)
        b = p["A"] * np.einsum("fe,ne,nec->fnc", env, space, dirs)
        return b, float(live.sum(1).mean())


class RingWave(Primitive):
    """Per event: an outward travelling, damped, geometrically spreading ring.

    Unlike the write-up's cos(k r - w t) this has a causal front (Gaussian
    ring at r = v tau) and 1/sqrt(1 + r/r0) spreading, so a splash does not
    ripple the whole field instantly.
    """

    name = "ring_wave"
    params = [
        Param("A", 0.005, 0.5, 0.05),
        Param("lam", 0.2, 20.0, 2.0),
        Param("v", 0.2, 5.0, 1.25),
        Param("w", 0.05, 1.0, 0.3),
        Param("kappa", 0.5, 30.0, 8.0),
    ]
    cost = 26.0
    per_event = True
    r0 = 0.5

    def evaluate(self, g, times, p):
        tau = times[:, None] - g.ev_t0[None, :]  # (F, E)
        env = np.where(tau >= 0, np.exp(-p["lam"] * np.maximum(tau, 0)), 0.0)
        live = env > LIVE_EPS
        env = np.where(live, env, 0.0)
        r = g.ev_d  # (N, E)
        x = r[None, :, :] - p["v"] * tau[:, None, :]  # (F, N, E)
        ring = np.exp(-x * x / (2 * p["w"] ** 2)) * np.cos(p["kappa"] * x)
        spread = 1.0 / np.sqrt(1.0 + r / self.r0)
        amp = p["A"] * env[:, None, :] * ring * spread[None]
        b = np.einsum("fne,nec->fnc", amp, g.ev_out)
        return b, float(live.sum(1).mean())


class Wake(Primitive):
    """Path token: Gaussian across the path, closed-form spring response in time since pass.

    One-sided (zero before the player arrives, `t_lead` seconds before the
    centre passes) and anchored to the polyline, so a turning player leaves
    the right wake. This is the path-anchored twin of RadialImpulse.
    """

    name = "wake"
    params = [
        Param("B", 0.01, 1.0, 0.3),
        Param("w", 0.05, 1.5, 0.35),
        Param("t_lead", 0.0, 0.6, 0.15),
        Param("lam", 0.1, 20.0, 3.0),
        Param("k", 5.0, 400.0, 60.0),
        Param("zeta", 0.05, 0.95, 0.3),
        Param("mix", 0.0, 1.0, 0.5),
        Param("q", 0.5, 4.0, 2.0),
    ]
    cost = 26.0

    def evaluate(self, g, times, p):
        tau = times[:, None] - (g.path_tpass[None, :] - p["t_lead"])  # (F, N)
        env = spring_response(tau, p["lam"], p["k"], p["zeta"])
        space = gkern(g.path_dperp, p["w"], p["q"])  # (N,)
        d = _mix_dir(g.path_nout, g.path_tan, p["mix"])  # (N, 2)
        b = p["B"] * (env * space[None, :])[..., None] * d[None]
        return b, 1.0


class Crush(Primitive):
    """Path token: persistent lean that rises after the pass and recovers slowly."""

    name = "crush"
    params = [
        Param("C", 0.01, 1.0, 0.2),
        Param("w", 0.05, 1.5, 0.25),
        Param("t_rise", 0.05, 5.0, 0.5),
        Param("t_rec", 1.0, 200.0, 20.0),
        Param("mix", 0.0, 1.0, 0.3),
        Param("q", 0.5, 4.0, 2.0),
    ]
    cost = 24.0

    def evaluate(self, g, times, p):
        dt = times[:, None] - g.path_tpass[None, :]
        dtp = np.maximum(dt, 0)
        env = np.where(dt >= 0, (1 - np.exp(-dtp / p["t_rise"])) * np.exp(-dtp / p["t_rec"]), 0.0)
        space = gkern(g.path_dperp, p["w"], p["q"])
        d = _mix_dir(g.path_nout, g.path_tan, p["mix"])
        b = p["C"] * (env * space[None, :])[..., None] * d[None]
        return b, 1.0


class Saturate(Primitive):
    """Unary post-op: soft clamp of bend magnitude (the one nonlinearity)."""

    name = "saturate"
    params = [Param("b_max", 0.1, 2.0, 0.6)]
    cost = 8.0

    def apply(self, b: np.ndarray, p: dict) -> np.ndarray:
        m = np.linalg.norm(b, axis=-1, keepdims=True)
        bm = p["b_max"]
        return b * (np.tanh(m / bm) * bm / np.maximum(m, 1e-9))


GRAMMAR: dict[str, type[Primitive]] = {
    c.name: c for c in (Presence, RadialImpulse, RingWave, Wake, Crush)
}
