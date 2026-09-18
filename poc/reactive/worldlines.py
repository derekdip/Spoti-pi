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


def corner_probe() -> Worldline:
    """B3 calibration probe: constant speed, one 90 degree turn of 0.15 s, 4 m in and 4 m out."""
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    th, dth = turns_heading(t, 0.0, [(4.0, np.pi / 2)], 0.15)
    return _build("corner_probe", (1.0, 2.0), t, v, dv, th, dth, 8.0)


def tangential_probe() -> Worldline:
    """B4 tangential probe: straight line, speed 0.6 -> 1.6 -> 0.6 -> 1.2 -> 0.6 with 0.8 s smooth
    transitions, never below 0.6 m/s while walking, no turning. Start/stop ramps as everywhere."""
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    base, dbase = ramp_speed(t, 0.0, 8.0, 0.6)
    v, dv = base.copy(), dbase.copy()
    for t_on, t_off, extra in ((1.0, 2.8, 1.0), (4.0, 5.8, 0.6)):
        # smooth bump of height `extra` between t_on and t_off (0.8 s smoothstep edges), only while walking
        up = _smooth((t - t_on) / 0.8)
        down = 1 - _smooth((t - (t_off - 0.8)) / 0.8)
        gate = (t < 7.5)
        v = v + extra * up * down * gate
        dv = dv + extra * (_dsmooth((t - t_on) / 0.8) / 0.8 * down - up * _dsmooth((t - (t_off - 0.8)) / 0.8) / 0.8) * gate
    th, dth = turns_heading(t, 0.0, [], 0.3)
    return _build("tangential_probe", (1.0, 5.0), t, v, dv, th, dth, 8.0)


def embedded_corner(length_m: float, with_corner: bool) -> Worldline:
    """Transfer-invariance probe: straight walk of total length `length_m` at the corner probe's speed,
    with (or without) the same 90 degree, 0.15 s corner at the midpoint. Duration scales with length."""
    v0 = 8.0 / (8.0 - RAMP)  # the corner probe's cruising speed
    t_walk = length_m / v0 + RAMP  # so that the distance covered is length_m
    t_total = t_walk + 2.0
    t = np.arange(int(t_total * HZ) + 1) / HZ
    v, dv = ramp_speed(t, 0.0, t_walk, v0)
    turns = [(t_walk / 2, np.pi / 2)] if with_corner else []
    th, dth = turns_heading(t, 0.0, turns, 0.15)
    name = f"corner_L{int(length_m)}" if with_corner else f"straight_L{int(length_m)}"
    w = _build(name, (0.0, 0.0), t, v, dv, th, dth, t_walk)
    return w


# ---------------------------------------------------------------------------
# B5 (smooth / singular / event decomposition) probes and fresh trajectories.
# Written before the B5 preregistration was frozen; none of these was run
# before the freeze (the design pilot used only zigzag, stop_start, corner_L8).
# ---------------------------------------------------------------------------


def corner_tau(tau: float, length_m: float = 8.0, theta: float = np.pi / 2) -> Worldline:
    """B5-H4 probe: `embedded_corner`'s walk with the corner's smoothstep width `tau` instead of 0.15 s."""
    v0 = 8.0 / (8.0 - RAMP)
    t_walk = length_m / v0 + RAMP
    t_total = t_walk + 2.0
    t = np.arange(int(t_total * HZ) + 1) / HZ
    v, dv = ramp_speed(t, 0.0, t_walk, v0)
    th, dth = turns_heading(t, 0.0, [(t_walk / 2, theta)], tau)
    return _build(f"corner_tau{tau:g}", (0.0, 0.0), t, v, dv, th, dth, t_walk)


def dwell_probe(dwell: float) -> Worldline:
    """B5-H5 probe: straight line, 3 m dash at 1.2 m/s, a stop of duration `dwell`, 3 m dash.
    `dwell = 0` is the momentary stop where the two ramps meet at zero speed; entrance and exit are
    identical for every dwell."""
    t_dash = 3.0 / 1.2 + RAMP
    t_walk = 2 * t_dash + dwell
    t_total = t_walk + 2.0
    t = np.arange(int(t_total * HZ) + 1) / HZ
    v1, dv1 = ramp_speed(t, 0.0, t_dash, 1.2)
    v2, dv2 = ramp_speed(t, t_dash + dwell, t_walk, 1.2)
    th, dth = turns_heading(t, 0.0, [], 0.3)
    return _build(f"dwell{dwell:g}", (0.0, 0.0), t, v1 + v2, dv1 + dv2, th, dth, t_walk)


def fresh_family() -> list[Worldline]:
    """B5 fresh trajectories (never used in B2 to B4): mixed defect classes and one negative control."""
    t = np.arange(int(T_TOTAL * HZ) + 1) / HZ
    out = []
    # three corners of different angles, 0.2 s each, 2 m legs at 1 m/s
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    th, dth = turns_heading(t, 0.0, [(2.0, np.pi / 3), (4.0, -110 * np.pi / 180), (6.0, 150 * np.pi / 180)], 0.2)
    out.append(_build("three_corners", (0.0, 0.0), t, v, dv, th, dth, 8.0))
    # corner, 1 s stop, corner
    v1, dv1 = ramp_speed(t, 0.0, 3.3, 1.0)
    v2, dv2 = ramp_speed(t, 4.3, 7.6, 1.0)
    th, dth = turns_heading(t, 0.0, [(1.5, np.pi / 2), (6.0, -120 * np.pi / 180)], 0.15)
    out.append(_build("corner_stop_corner", (0.0, 0.0), t, v1 + v2, dv1 + dv2, th, dth, 7.6))
    # a smooth bend (half sine period over the first 4 s) followed by a 100 degree corner
    v, dv = ramp_speed(t, 0.0, 8.0, 8.0 / (8.0 - RAMP))
    ph = np.clip(t / 8.0, 0, 1)
    th_s = np.where(t < 4.0, 0.6 * np.sin(2 * np.pi * ph), 0.0)
    dth_s = np.where(t < 4.0, 0.6 * 2 * np.pi / 8.0 * np.cos(2 * np.pi * ph), 0.0)
    th_c, dth_c = turns_heading(t, 0.0, [(5.5, 100 * np.pi / 180)], 0.2)
    out.append(_build("bend_then_corner", (0.0, 0.0), t, v, dv, th_s + th_c, dth_s + dth_c, 8.0))
    # a reversal: 180 degrees in 0.3 s at constant speed
    v, dv = ramp_speed(t, 0.0, 8.0, 1.0)
    th, dth = turns_heading(t, 0.0, [(4.0, np.pi)], 0.3)
    out.append(_build("reversal", (0.0, 0.0), t, v, dv, th, dth, 8.0))
    # negative control: tight smooth slalom, heading +-0.8 rad, four periods, peak |theta'| = 2.51 rad/s < 3
    v, dv = ramp_speed(t, 0.0, 8.0, 1.0)
    ph = np.clip(t / 8.0, 0, 1)
    th = 0.8 * np.sin(2 * np.pi * 4 * ph)
    dth = np.where(t < 8.0, 0.8 * 2 * np.pi * 4 / 8.0 * np.cos(2 * np.pi * 4 * ph), 0.0)
    out.append(_build("tight_slalom", (0.0, 0.0), t, v, dv, th, dth, 8.0))
    return out
