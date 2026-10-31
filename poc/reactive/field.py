"""Level-1 coarse field: bake the model onto a grid, then sample bilinearly.

This is the O(m * cells) + O(N) evaluation path. It makes per-stalk cost
independent of the number of live tokens, at the price of blurring any
feature narrower than a cell.
"""
from __future__ import annotations

import numpy as np

from .causes import Events, PathToken, PlayerPath
from .geometry import build_geometry
from .model import CheapModel


def bake_and_sample(model: CheapModel, pos: np.ndarray, times: np.ndarray, grid: int, extent: float,
                    events: Events, path: PathToken, player: PlayerPath) -> tuple[np.ndarray, float]:
    cell = extent / grid
    cx = (np.arange(grid) + 0.5) * cell
    gx, gy = np.meshgrid(cx, cx, indexing="xy")
    centres = np.stack([gx.ravel(), gy.ravel()], axis=-1)
    g = build_geometry(centres, events, path, player)
    fb, cost_per_cell = model.evaluate(g, times)  # (F, G*G, 2)
    fb = fb.reshape(len(times), grid, grid, 2)
    # bilinear sample at stalk positions
    u = pos[:, 0] / cell - 0.5
    v = pos[:, 1] / cell - 0.5
    i0 = np.clip(np.floor(u).astype(int), 0, grid - 2)
    j0 = np.clip(np.floor(v).astype(int), 0, grid - 2)
    fu = np.clip(u - i0, 0, 1)[None, :, None]
    fv = np.clip(v - j0, 0, 1)[None, :, None]
    s = (fb[:, j0, i0] * (1 - fu) * (1 - fv) + fb[:, j0, i0 + 1] * fu * (1 - fv)
         + fb[:, j0 + 1, i0] * (1 - fu) * fv + fb[:, j0 + 1, i0 + 1] * fu * fv)
    # cost per stalk per frame: bake amortised over stalks + bilinear sample
    cost = cost_per_cell * grid * grid / pos.shape[0] + 12.0
    return s, cost
