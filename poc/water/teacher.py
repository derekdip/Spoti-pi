"""Exact teacher for small-amplitude water waves on a pond of finite depth.

Linear potential-flow theory: every Fourier mode of the surface height is an
independent damped oscillator with the dispersion relation
    omega^2 = g k tanh(k h)
driven by surface pressure. Time stepping uses the exact propagator of each
mode for piecewise-constant forcing, so the only approximations are the grid
and the assumption of small amplitude. No CFL, no numerical dispersion.

Damping gamma_k = gamma0 + nu k^2 stands in for viscosity and bottom drag.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

G = 9.81


@dataclass
class WaterParams:
    size: float = 6.0  # domain edge (m), periodic
    n: int = 256  # grid points per edge
    depth: float = 0.4  # m
    gamma0: float = 0.25  # 1/s bulk damping
    nu: float = 1.0e-4  # m^2/s viscous damping coefficient
    fps: float = 60.0
    substeps: int = 4
    duration: float = 5.0
    record_stride: int = 2  # record every k-th grid point

    @property
    def dx(self) -> float:
        return self.size / self.n

    @property
    def dt(self) -> float:
        return 1.0 / (self.fps * self.substeps)


@dataclass
class WaterRecord:
    params: WaterParams
    xs: np.ndarray  # (M,) recorded grid coordinates
    times: np.ndarray  # (F,)
    eta: np.ndarray  # (F, M, M) surface height, float32
    source: np.ndarray | None  # (F, 2) moving source position, if any


class SpectralWater:
    def __init__(self, p: WaterParams):
        self.p = p
        k1 = 2 * np.pi * np.fft.fftfreq(p.n, p.dx)
        self.kx = k1[:, None]
        self.ky = k1[None, :]
        k = np.sqrt(self.kx ** 2 + self.ky ** 2)
        self.k = k
        self.tanh_kh = np.tanh(k * p.depth)
        self.omega2 = G * k * self.tanh_kh
        self.gamma = p.gamma0 + p.nu * k ** 2
        assert np.all(self.gamma[k > 0] ** 2 < self.omega2[k > 0]), "overdamped modes: lower nu"
        self.omega_d = np.sqrt(np.maximum(self.omega2 - self.gamma ** 2, 1e-12))
        dt = p.dt
        e = np.exp(-self.gamma * dt)
        c, s = np.cos(self.omega_d * dt), np.sin(self.omega_d * dt)
        # propagator for x'' + 2 gamma x' + omega^2 x = 0 over dt
        self.a11 = e * (c + self.gamma / self.omega_d * s)
        self.a12 = e * s / self.omega_d
        self.a21 = -e * self.omega2 / self.omega_d * s
        self.a22 = e * (c - self.gamma / self.omega_d * s)
        self.inv_omega2 = np.where(k > 0, 1.0 / np.maximum(self.omega2, 1e-12), 0.0)
        xs = np.arange(p.n) * p.dx
        self.X, self.Y = np.meshgrid(xs, xs, indexing="ij")
        self.eta_hat = np.zeros((p.n, p.n), dtype=complex)
        self.vel_hat = np.zeros((p.n, p.n), dtype=complex)

    def add_impulse(self, x0: float, y0: float, v0: float, sigma: float) -> None:
        """Initial downward surface velocity: a stone, a foot, a drop."""
        r2 = (self.X - x0) ** 2 + (self.Y - y0) ** 2
        self.vel_hat += np.fft.fft2(-v0 * np.exp(-r2 / (2 * sigma * sigma)))

    def step(self, pressure: np.ndarray | None = None) -> None:
        """Advance one substep with surface pressure (m^2/s^2, i.e. p/rho) held constant."""
        if pressure is None:
            force = 0.0
        else:
            force = -self.k * self.tanh_kh * np.fft.fft2(pressure)
        eta_p = force * self.inv_omega2  # particular solution for constant forcing
        x = self.eta_hat - eta_p
        v = self.vel_hat
        self.eta_hat = self.a11 * x + self.a12 * v + eta_p
        self.vel_hat = self.a21 * x + self.a22 * v
        self.eta_hat[0, 0] = 0.0
        self.vel_hat[0, 0] = 0.0

    def eta(self) -> np.ndarray:
        return np.fft.ifft2(self.eta_hat).real


def run_splash(p: WaterParams, x0: float, y0: float, v0: float = 1.0, sigma: float = 0.03) -> WaterRecord:
    sim = SpectralWater(p)
    sim.add_impulse(x0, y0, v0, sigma)
    return _record(sim, p, None)


def run_wake(p: WaterParams, start: tuple[float, float], velocity: tuple[float, float], t_move: float,
             p0: float = 0.05, sigma: float = 0.05) -> WaterRecord:
    """A Gaussian pressure bump (a hand, a creature) dragged across the surface, then lifted."""
    sim = SpectralWater(p)

    def source_at(t: float):
        tt = min(t, t_move)
        return start[0] + velocity[0] * tt, start[1] + velocity[1] * tt

    def pressure_at(t: float):
        if t > t_move:
            return None
        sx, sy = source_at(t)
        r2 = (sim.X - sx) ** 2 + (sim.Y - sy) ** 2
        return p0 * np.exp(-r2 / (2 * sigma * sigma))

    return _record(sim, p, pressure_at, source_at)


def _record(sim: SpectralWater, p: WaterParams, pressure_at, source_at=None) -> WaterRecord:
    n_frames = int(round(p.duration * p.fps)) + 1
    times = np.arange(n_frames) / p.fps
    s = p.record_stride
    m = p.n // s
    eta = np.zeros((n_frames, m, m), dtype=np.float32)
    src = np.zeros((n_frames, 2)) if source_at else None
    t = 0.0
    for f in range(n_frames):
        eta[f] = sim.eta()[::s, ::s]
        if src is not None:
            src[f] = source_at(t)
        if f == n_frames - 1:
            break
        for _ in range(p.substeps):
            sim.step(None if pressure_at is None else pressure_at(t))
            t += p.dt
    xs = np.arange(m) * p.dx * s
    return WaterRecord(p, xs, times, eta, src)
