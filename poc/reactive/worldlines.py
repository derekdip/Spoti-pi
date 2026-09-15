"""Frozen trajectory family for Math Track B2 (causal path complexity).

Every worldline is built from an analytic speed v(t) and heading theta(t):
    p(t) = p0 + integral v (cos theta, sin theta) dt
so the acceleration is analytic:
    p'' = v' (cos theta, sin theta) + v theta' (-sin theta, cos theta).
Position comes from a fine numerical integral of the analytic velocity.

Common rules (frozen): duration 10 s, sampled at 200 Hz, walking ends by
8.5 s, every start/stop uses a 0.5 s smoothstep ramp, every turn uses a
smoothstep of fixed width. Nothing here is tuned after C_G is computed.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .causes import PlayerPath

T_TOTAL = 10.0
HZ = 200.0
RAMP = 0.5


def _smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _dsmooth(x):
    inside = (x > 0) & (x < 1)
    return np.where(inside, 6 * x * (1 - x), 0.0)


def ramp_speed(t, t_on, t_off, v):
    """Speed v between t_on and t_off with smoothstep ramps of width RAMP at both ends."""
    up = _smooth((t - t_on) / RAMP)
    down = 1 - _smooth((t - (t_off - RAMP)) / RAMP)
    s = v * up * down
    ds = v * (_dsmooth((t - t_on) / RAMP) / RAMP * down - up * _dsmooth((t - (t_off - RAMP)) / RAMP) / RAMP)
    return s, ds


def turns_heading(t, theta0, turns, width):
    """Heading = theta0 + sum of smoothstep turns (t_k, dtheta_k) of the given width."""
    th = np.full_like(t, theta0)
    dth = np.zeros_like(t)
    for tk, d in turns:
        th = th + d * _smooth((t - tk) / width)
        dth = dth + d * _dsmooth((t - tk) / width) / width
    return th, dth


@dataclass
class Worldline:
    name: str
    times: np.ndarray
    points: np.ndarray
    accel: np.ndarray  # analytic p''(t), (M, 2)
    speed: np.ndarray
    heading_rate: np.ndarray  # analytic theta'(t)
    t_walk: float

    def as_path(self) -> PlayerPath:
        return PlayerPath(self.times, self.points, self.t_walk)


def _build(name, p0, t, v, dv, th, dth, t_walk) -> Worldline:
    vel = v[:, None] * np.stack([np.cos(th), np.sin(th)], -1)
    acc = dv[:, None] * np.stack([np.cos(th), np.sin(th)], -1) + (v * dth)[:, None] * np.stack([-np.sin(th), np.cos(th)], -1)
    dt = t[1] - t[0]
    pos = np.array(p0)[None, :] + np.concatenate([[[0.0, 0.0]], np.cumsum(0.5 * (vel[1:] + vel[:-1]) * dt, axis=0)])
    return Worldline(name, t, pos, acc, v, dth, t_walk)


def family() -> list[Worldline]:
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    out = []

    # 1. constant-speed straight: 8 m in 8 s
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    th, dth = turns_heading(t, 0.0, [], 0.3)
    out.append(_build("straight", (1.0, 5.0), t, v, dv, th, dth, 8.0))

    # 2. smooth S-curve: heading swings +-0.9 rad sinusoidally, one full period over the walk
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    ph = np.clip(t / 8.0, 0, 1)
    th = 0.9 * np.sin(2 * np.pi * ph)
    dth = np.where(t < 8.0, 0.9 * 2 * np.pi / 8.0 * np.cos(2 * np.pi * ph), 0.0)
    out.append(_build("s_curve", (1.0, 4.0), t, v, dv, th, dth, 8.0))

    # 3. repeated stop/start: four 2 m dashes of 1.3 s with 0.6 s pauses, straight line
    v = np.zeros_like(t)
    dv = np.zeros_like(t)
    for k in range(4):
        t_on = k * 1.9
        s, ds = ramp_speed(t, t_on, t_on + 1.3, 2.0 / (1.3 - RAMP))
        v += s
        dv += ds
    th, dth = turns_heading(t, 0.0, [], 0.3)
    out.append(_build("stop_start", (1.0, 5.0), t, v, dv, th, dth, 4 * 1.9 - 0.6))

    # 4. smooth slalom: heading swings +-1.0 rad, three periods over the walk
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    ph = np.clip(t / 8.0, 0, 1)
    th = 1.0 * np.sin(2 * np.pi * 3 * ph)
    dth = np.where(t < 8.0, 1.0 * 2 * np.pi * 3 / 8.0 * np.cos(2 * np.pi * 3 * ph), 0.0)
    out.append(_build("slalom", (1.0, 5.0), t, v, dv, th, dth, 8.0))

    # 5. sharp zigzag: six alternating +-1.4 rad turns of 0.15 s width at constant speed
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    turns = [(1.0 + k * 1.15, (1.4 if k % 2 == 0 else -1.4) * (1 if k > 0 else 0.5)) for k in range(6)]
    th, dth = turns_heading(t, 0.0, turns, 0.15)
    out.append(_build("zigzag", (1.0, 4.5), t, v, dv, th, dth, 8.0))

    # 6. wandering with stops and a reversal: heading = slow sinusoids, speed with two pauses,
    #    a pi turn (reversal) during the second pause
    v = np.zeros_like(t)
    dv = np.zeros_like(t)
    for t_on, t_off, vk in ((0.0, 3.0, 1.3), (3.6, 5.6, 1.1), (6.3, 8.5, 1.4)):
        s, ds = ramp_speed(t, t_on, t_off, vk)
        v += s
        dv += ds
    th = 0.35 * np.sin(2 * np.pi * t / 4.0) + 0.25 * np.sin(2 * np.pi * t / 1.7 + 1.0)
    dth = 0.35 * 2 * np.pi / 4.0 * np.cos(2 * np.pi * t / 4.0) + 0.25 * 2 * np.pi / 1.7 * np.cos(2 * np.pi * t / 1.7 + 1.0)
    th2, dth2 = turns_heading(t, 0.0, [(5.7, np.pi)], 0.5)
    out.append(_build("wandering", (1.5, 6.5), t, v, dv, th + th2, dth + dth2, 8.5))

    # 7. two-speed straight: slow then fast, no turning (acceleration without curvature)
    v1, dv1 = ramp_speed(t, 0.0, 4.5, 0.6)
    v2, dv2 = ramp_speed(t, 4.5, 8.0, 1.6)
    th, dth = turns_heading(t, 0.0, [], 0.3)
    out.append(_build("two_speed", (1.0, 5.0), t, v1 + v2, dv1 + dv2, th, dth, 8.0))

    # 8. constant-speed circle of radius 2.5 m (curvature without speed change)
    v, dv = ramp_speed(t, 0.0, 8.0, 1.6)
    r = 2.5
    dth = v / r
    th = np.concatenate([[0.0], np.cumsum(0.5 * (dth[1:] + dth[:-1]) * (t[1] - t[0]))])
    out.append(_build("circle", (5.0, 2.5), t, v, dv, th, dth, 8.0))
    return out
