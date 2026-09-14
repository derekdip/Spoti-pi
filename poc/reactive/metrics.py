"""Error metrics: visual (state RMS), late/persistence, and a gameplay query."""
from __future__ import annotations

import numpy as np


def rel_rmse(pred: np.ndarray, ref: np.ndarray) -> float:
    num = np.sqrt(np.mean((pred - ref) ** 2))
    den = np.sqrt(np.mean(ref ** 2))
    return float(num / max(den, 1e-12))


def smooth_time(b: np.ndarray, window: int) -> np.ndarray:
    """Moving average over frames (axis 0); a crude stand-in for what a viewer perceives."""
    if window <= 1:
        return b
    k = np.ones(window) / window
    out = np.empty_like(b)
    flat = b.reshape(b.shape[0], -1)
    res = np.apply_along_axis(lambda x: np.convolve(x, k, mode="same"), 0, flat)
    out[...] = res.reshape(b.shape)
    return out


def rel_rmse_smoothed(pred: np.ndarray, ref: np.ndarray, window: int) -> float:
    return rel_rmse(smooth_time(pred, window), smooth_time(ref, window))


def coarse_field(bend: np.ndarray, pos: np.ndarray, grid: int, extent: float) -> np.ndarray:
    """Mean |bend| per cell over the given frames: what an AI would query."""
    mag = np.linalg.norm(bend, axis=-1).mean(0)  # (N,)
    ix = np.clip((pos[:, 0] / extent * grid).astype(int), 0, grid - 1)
    iy = np.clip((pos[:, 1] / extent * grid).astype(int), 0, grid - 1)
    acc = np.zeros((grid, grid))
    cnt = np.zeros((grid, grid))
    np.add.at(acc, (iy, ix), mag)
    np.add.at(cnt, (iy, ix), 1.0)
    return acc / np.maximum(cnt, 1.0)


def trail_iou(pred: np.ndarray, ref: np.ndarray, pos: np.ndarray, grid: int, extent: float, frac: float = 0.25) -> float:
    """Gameplay capability: can a coarse consumer find the trail where the teacher left it?"""
    fr = coarse_field(ref, pos, grid, extent)
    fp = coarse_field(pred, pos, grid, extent)
    thr = frac * fr.max()
    a = fr > thr
    b = fp > thr
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / max(union, 1))
