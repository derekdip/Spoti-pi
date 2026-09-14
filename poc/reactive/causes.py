"""Causes (the u(t) side): the player path and the events emitted from it.

Everything the cheap model is allowed to know about the world comes from
here. Nothing in this file knows about grass.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PlayerPath:
    """Dense sampled player trajectory (what the game already has)."""

    times: np.ndarray  # (M,)
    points: np.ndarray  # (M, 2)
    t_walk: float = 0.0  # time at which the player stops moving

    def position(self, t: np.ndarray) -> np.ndarray:
        t = np.asarray(t, dtype=float)
        x = np.interp(t, self.times, self.points[:, 0])
        y = np.interp(t, self.times, self.points[:, 1])
        return np.stack([x, y], axis=-1)

    def velocity(self, t: np.ndarray, h: float = 1e-3) -> np.ndarray:
        return (self.position(t + h) - self.position(t - h)) / (2 * h)

    @property
    def t_end(self) -> float:
        return float(self.times[-1])


def s_curve_walk(t_walk: float = 6.0, t_total: float = 10.0, hz: float = 200.0) -> PlayerPath:
    """Walk an S-curve across a 10 m field for t_walk seconds, then stand still."""
    n = int(t_total * hz) + 1
    times = np.linspace(0.0, t_total, n)
    s = np.clip(times / t_walk, 0.0, 1.0)
    # ease in/out so the walk starts and stops smoothly
    s = s * s * (3 - 2 * s)
    x = 1.0 + 7.5 * s
    y = 5.0 + 1.3 * np.sin(2 * np.pi * s * 0.9)
    return PlayerPath(times, np.stack([x, y], axis=-1), t_walk)


@dataclass
class Events:
    """Level-0 tokens: tiny transient causes emitted along the path."""

    p: np.ndarray  # (E, 2) position
    t0: np.ndarray  # (E,) emission time
    dir: np.ndarray  # (E, 2) unit travel direction at emission

    def __len__(self) -> int:
        return int(self.p.shape[0])


def emit_stride_events(path: PlayerPath, stride: float = 0.5) -> Events:
    """Emit a 'footstep' event every `stride` metres of travel."""
    pts = path.points
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    marks = np.arange(0.0, arc[-1], stride)
    idx = np.searchsorted(arc, marks)
    idx = np.clip(idx, 1, len(pts) - 1)
    p = pts[idx]
    t0 = path.times[idx]
    d = pts[idx] - pts[idx - 1]
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    return Events(p, t0, d)


@dataclass
class PathToken:
    """The banked path: a coarse polyline with pass times (a snow-track style token)."""

    points: np.ndarray  # (M, 2)
    times: np.ndarray  # (M,)


def bank_path(path: PlayerPath, hz: float = 20.0) -> PathToken:
    """Resample the dense path into the coarse polyline the runtime would keep."""
    n = int(path.t_end * hz) + 1
    times = np.linspace(0.0, path.t_end, n)
    return PathToken(path.position(times), times)
