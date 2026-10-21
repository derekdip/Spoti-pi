"""The hand: executes a stroke plan as timed pen motion with a persona (docs/doodle-bots.md).

A stroke is a polyline. The hand resamples it along its length, slows at corners, starts with a small
hook, overshoots the end, adds tremor (smoothed noise) and drift (a slow wobble across the stroke),
and lifts the pen between strokes with a travel time and a think pause. The same plan executed by two
personas is two different drawings; the same persona executing the same plan twice is two different
drawings too, which is half of "never repeats".
"""
from __future__ import annotations
import numpy as np

PERSONAS = {
    "neat":  dict(speed=260.0, tremor=0.5, drift=0.8, overshoot=2.0, hook=1.0, think=0.6),
    "quick": dict(speed=430.0, tremor=1.4, drift=2.2, overshoot=7.0, hook=3.0, think=0.25),
    "shaky": dict(speed=170.0, tremor=2.6, drift=3.0, overshoot=3.0, hook=2.0, think=0.9),
    "lazy":  dict(speed=210.0, tremor=1.0, drift=1.6, overshoot=4.0, hook=1.5, think=1.5),
    "bold":  dict(speed=340.0, tremor=0.9, drift=1.2, overshoot=9.0, hook=2.0, think=0.4),
}
TRAVEL = 900.0      # px/s, pen-up travel between strokes


def resample(stroke, step=2.0):
    """Points spaced `step` along the polyline (a single point becomes a short dot)."""
    s = np.asarray(stroke, float)
    if len(s) < 2:
        return np.stack([s[0], s[0] + [step, 0]], 0)
    seg = np.linalg.norm(np.diff(s, axis=0), axis=1); L = seg.sum()
    if L < 1e-6:
        return np.stack([s[0], s[0] + [step, 0]], 0)
    cum = np.concatenate([[0.0], np.cumsum(seg)]); n = max(2, int(L / step) + 1)
    u = np.linspace(0, L, n)
    return np.stack([np.interp(u, cum, s[:, 0]), np.interp(u, cum, s[:, 1])], 1)


def _smooth(x, w):
    if w <= 1 or len(x) < w:
        return x
    k = np.ones(w) / w
    return np.stack([np.convolve(x[:, i], k, mode="same") for i in range(x.shape[1])], 1)


def execute_stroke(stroke, persona, rng, t0=0.0):
    """One stroke as (times, points): absolute times in seconds and canvas points, pen down throughout."""
    p = persona; pts = resample(stroke, 2.0)
    d = pts[-1] - pts[-2]; d = d / max(np.linalg.norm(d), 1e-9)
    d0 = pts[1] - pts[0]; d0 = d0 / max(np.linalg.norm(d0), 1e-9)
    # a hook at the start: the pen lands a little off and slides in
    ang = rng.uniform(-np.pi, np.pi); hook = p["hook"] * rng.uniform(0.3, 1.0)
    pts = np.concatenate([[pts[0] + hook * np.array([np.cos(ang), np.sin(ang)])], pts], 0)
    # overshoot at the end
    over = p["overshoot"] * rng.uniform(0.2, 1.0); k = max(1, int(over / 2.0))
    pts = np.concatenate([pts, pts[-1] + d * np.linspace(2.0, over, k)[:, None]], 0) if over > 2.0 else pts
    n = len(pts)
    # tremor and drift
    noise = _smooth(rng.normal(0.0, p["tremor"], (n, 2)), 5)
    tang = np.gradient(pts, axis=0); tang /= np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-9)
    normal = np.stack([-tang[:, 1], tang[:, 0]], 1)
    s = np.linspace(0, 1, n); drift = p["drift"] * rng.uniform(0.4, 1.0) * np.sin(2 * np.pi * rng.uniform(0.5, 1.5) * s + rng.uniform(0, 2 * np.pi))
    pts = pts + noise + drift[:, None] * normal
    # timing: slower at corners and at the start
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    v = np.diff(pts, axis=0); v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
    turn = np.zeros(len(seg)); turn[1:] = np.arccos(np.clip((v[1:] * v[:-1]).sum(1), -1, 1))
    speed = p["speed"] * (0.3 + 0.7 * np.exp(-3.0 * turn)) * rng.uniform(0.85, 1.15)
    ramp = np.minimum(1.0, 0.3 + np.arange(len(seg)) / 6.0)
    dt = seg / (speed * ramp)
    t = t0 + np.concatenate([[0.0], np.cumsum(dt)])
    return t, pts


def execute(strokes, persona, rng, t0=0.0):
    """A plan as a list of (times, points) with pen-up travel and a think pause between strokes."""
    out, t = [], t0
    for i, s in enumerate(strokes):
        if i:
            t += np.linalg.norm(np.asarray(s[0], float) - out[-1][1][-1]) / TRAVEL + persona["think"] * rng.uniform(0.4, 1.6)
        ts, pts = execute_stroke(s, persona, rng, t); out.append((ts, pts)); t = ts[-1]
    return out
