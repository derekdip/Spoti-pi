"""Static geometry between a set of stalks and the banked causes.

Precomputed once: distances/directions to each event, and the nearest point
on the path polyline (perpendicular distance, side, pass time, tangent).
Per-frame work is then only time envelopes.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .causes import Events, PathToken, PlayerPath


@dataclass
class Geometry:
    pos: np.ndarray  # (N, 2)
    # events
    ev_t0: np.ndarray  # (E,)
    ev_dir: np.ndarray  # (E, 2)
    ev_d: np.ndarray  # (N, E)
    ev_out: np.ndarray  # (N, E, 2)
    # path
    path_dperp: np.ndarray  # (N,)
    path_tpass: np.ndarray  # (N,)
    path_nout: np.ndarray  # (N, 2) unit normal pointing away from the path
    path_tan: np.ndarray  # (N, 2) unit tangent at nearest point
    # live cause
    player: PlayerPath

    @property
    def n(self) -> int:
        return int(self.pos.shape[0])

    @property
    def n_events(self) -> int:
        return int(self.ev_t0.shape[0])


def build_geometry(pos: np.ndarray, events: Events, path: PathToken, player: PlayerPath) -> Geometry:
    dvec = pos[:, None, :] - events.p[None, :, :]
    d = np.linalg.norm(dvec, axis=-1)
    out = dvec / np.maximum(d, 1e-6)[..., None]

    # nearest point on the polyline
    a = path.points[:-1]  # (M-1, 2)
    bseg = path.points[1:]
    seg = bseg - a
    seg_len2 = np.maximum((seg * seg).sum(-1), 1e-12)
    rel = pos[:, None, :] - a[None, :, :]  # (N, M-1, 2)
    u = np.clip((rel * seg[None]).sum(-1) / seg_len2[None], 0.0, 1.0)  # (N, M-1)
    proj = a[None] + u[..., None] * seg[None]
    dist = np.linalg.norm(pos[:, None, :] - proj, axis=-1)
    j = np.argmin(dist, axis=1)
    rows = np.arange(pos.shape[0])
    dperp = dist[rows, j]
    uj = u[rows, j]
    tpass = path.times[:-1][j] + uj * (path.times[1:][j] - path.times[:-1][j])
    tan = seg[j] / np.sqrt(seg_len2[j])[:, None]
    away = pos - proj[rows, j]
    left = np.stack([-tan[:, 1], tan[:, 0]], axis=-1)
    side = np.sign((away * left).sum(-1))
    side[side == 0] = 1.0
    nout = left * side[:, None]
    return Geometry(pos, events.t0, events.dir, d, out, dperp, tpass, nout, tan, player)
