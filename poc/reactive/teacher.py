"""Expensive reference ("teacher") vegetation simulation.

N stalks on a regular grid. Each stalk's tip displacement b_i (2D, in the
ground plane) follows a damped spring with

  * a stiffening (saturating) restoring force toward a plastic rest offset h_i,
  * lattice neighbour coupling (this is what makes disturbances propagate),
  * penalty contact between the stalk TIP and a moving cylindrical player,
  * drag along the player's velocity while the base is under the player,
  * plastic "crush": h_i drifts toward b_i while |b_i| exceeds a threshold,
    and recovers slowly afterwards (hysteresis -> persistent trail).

This is deliberately NOT what we want to run on Quest. It is the thing we
record offline and then try to approximate with cheap closed-form primitives.
The nonlinear terms (contact, stiffening, crush) are what make the test
meaningful: a purely linear coupled-spring lattice is exactly a superposition
of Green's functions and would be trivially representable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .causes import PlayerPath


@dataclass
class TeacherParams:
    nx: int = 40
    ny: int = 40
    extent: float = 10.0  # field is [0, extent]^2 metres
    k: float = 40.0  # stalk stiffness (1/s^2, unit mass)
    zeta: float = 0.25  # damping ratio
    k_n: float = 25.0  # neighbour coupling
    b_max: float = 0.5  # stiffening scale
    contact_radius: float = 0.35
    k_contact: float = 400.0
    k_drag: float = 6.0
    crush_threshold: float = 0.30
    crush_rate: float = 4.0  # 1/s plastic flow while over threshold
    crush_recovery: float = 20.0  # s
    fps: float = 60.0
    substeps: int = 4
    duration: float = 10.0

    @property
    def c(self) -> float:
        return 2.0 * self.zeta * np.sqrt(self.k)

    @property
    def dt(self) -> float:
        return 1.0 / (self.fps * self.substeps)


@dataclass
class TeacherRecord:
    """What we record: the expensive state x(t) and the causes u(t)."""

    params: TeacherParams
    pos: np.ndarray  # (N, 2) stalk base positions
    times: np.ndarray  # (F,)
    bend: np.ndarray  # (F, N, 2) tip displacement
    lean: np.ndarray  # (F, N, 2) plastic offset h (diagnostic only)
    player: np.ndarray  # (F, 2) player position per frame
    wall_time: float = 0.0
    flops_per_stalk_frame: float = field(default=0.0)


def stalk_grid(p: TeacherParams) -> np.ndarray:
    xs = (np.arange(p.nx) + 0.5) * (p.extent / p.nx)
    ys = (np.arange(p.ny) + 0.5) * (p.extent / p.ny)
    gx, gy = np.meshgrid(xs, ys, indexing="xy")
    return np.stack([gx.ravel(), gy.ravel()], axis=-1)


def _laplacian(b2d: np.ndarray) -> np.ndarray:
    lap = np.zeros_like(b2d)
    lap[1:, :] += b2d[:-1, :] - b2d[1:, :]
    lap[:-1, :] += b2d[1:, :] - b2d[:-1, :]
    lap[:, 1:] += b2d[:, :-1] - b2d[:, 1:]
    lap[:, :-1] += b2d[:, 1:] - b2d[:, :-1]
    return lap


def run_teacher(path: PlayerPath, p: TeacherParams | None = None) -> TeacherRecord:
    import time as _time

    p = p or TeacherParams()
    pos = stalk_grid(p)
    n = pos.shape[0]
    b = np.zeros((n, 2))
    v = np.zeros((n, 2))
    h = np.zeros((n, 2))
    dt = p.dt
    n_frames = int(round(p.duration * p.fps)) + 1
    times = np.arange(n_frames) / p.fps
    bend = np.zeros((n_frames, n, 2))
    lean = np.zeros((n_frames, n, 2))
    player = path.position(times)
    R = p.contact_radius
    t = 0.0
    t_start = _time.perf_counter()
    for f in range(n_frames):
        bend[f] = b
        lean[f] = h
        if f == n_frames - 1:
            break
        for _ in range(p.substeps):
            P = path.position(t)
            V = path.velocity(t)
            # restoring force toward plastic rest offset, stiffening with amplitude
            rel = b - h
            mag2 = (rel * rel).sum(-1, keepdims=True)
            stiff = p.k * (1.0 + mag2 / (p.b_max * p.b_max))
            acc = -stiff * rel - p.c * v
            # neighbour coupling
            acc += p.k_n * _laplacian(b.reshape(p.ny, p.nx, 2)).reshape(n, 2)
            # tip contact with the player cylinder
            tip = pos + b
            dv = tip - P
            d = np.linalg.norm(dv, axis=1, keepdims=True)
            out = dv / np.maximum(d, 1e-6)
            gap = np.maximum(0.0, R - d)
            acc += p.k_contact * gap * out
            # drag along player velocity while the base is under the player
            db = np.linalg.norm(pos - P, axis=1, keepdims=True)
            w = np.clip(1.0 - db / R, 0.0, 1.0)
            acc += p.k_drag * w * V
            # integrate (semi-implicit Euler)
            v = v + dt * acc
            b = b + dt * v
            # plastic crush with slow recovery
            over = (np.linalg.norm(b, axis=1, keepdims=True) > p.crush_threshold)
            h = h + dt * p.crush_rate * over * (b - h)
            h = h * (1.0 - dt / p.crush_recovery)
            t += dt
    wall = _time.perf_counter() - t_start
    # rough op count per stalk per substep: spring 12, laplacian 16, contact 22,
    # drag 10, integrate 8, crush 12 -> ~80, times substeps per frame.
    flops = 80.0 * p.substeps
    return TeacherRecord(p, pos, times, bend, lean, player, wall, flops)
