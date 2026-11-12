"""Cheap ripple tokens: stateless closed forms evaluated at surface points.

`ring`      the corrected wave packet from the vegetation grammar: a Gaussian
            ring travelling at one speed with a fixed wavelength.
`chirp`     a dispersive ring in the Cauchy-Poisson form: phase g t^2 / (4 r),
            so long waves run ahead and short waves trail, which is what deep
            water actually does. Amplitude envelope with a soft causal front and
            a viscous cutoff: the local wavenumber is g t^2 / (4 r^2), and waves
            shorter than 2 pi / k_cut are damped away (real ponds kill them).

A wake is the Huygens superposition of the splash token along the path.
"""
from __future__ import annotations

import numpy as np

R0 = 0.05  # geometric spreading scale (m)

RING_PARAMS = ["A", "lam", "v", "w", "kappa", "phi"]
RING_BOUNDS = [(1e-4, 0.05), (0.05, 10.0), (0.1, 3.0), (0.01, 0.5), (5.0, 200.0), (-np.pi, np.pi)]
RING_INIT = [0.005, 1.0, 0.5, 0.1, 60.0, 0.0]

CHIRP_PARAMS = ["A", "lam", "m", "n", "g_eff", "phi", "v_max", "k_cut"]
CHIRP_BOUNDS = [(1e-4, 0.1), (0.05, 10.0), (-1.0, 3.0), (0.0, 3.0), (2.0, 30.0), (-np.pi, np.pi), (0.2, 5.0), (20.0, 2000.0)]
CHIRP_INIT = [0.01, 1.0, 1.0, 1.5, 9.81, 0.0, 1.5, 300.0]

RING_COST = 26.0  # ops per point per live token (see unity/ReactiveKernels.hlsl)
CHIRP_COST = 40.0


def ring(r: np.ndarray, tau: np.ndarray, p: dict) -> np.ndarray:
    """r: (..., N) distances, tau: (..., 1) or broadcastable times since the event."""
    x = r - p["v"] * tau
    env = np.exp(-p["lam"] * tau) * np.exp(-x * x / (2 * p["w"] ** 2)) / np.sqrt(1.0 + r / R0)
    out = p["A"] * env * np.cos(p["kappa"] * x + p["phi"])
    return np.where(tau > 0, out, 0.0)


def chirp(r: np.ndarray, tau: np.ndarray, p: dict) -> np.ndarray:
    tau_p = np.maximum(tau, 1e-4)
    rr = np.maximum(r, 0.02)
    k_loc = p["g_eff"] * tau_p * tau_p / (4.0 * rr * rr)  # local wavenumber of the chirp
    env = (np.exp(-p["lam"] * tau_p) * (tau_p / 0.5) ** p["m"] / (1.0 + rr / R0) ** p["n"]
           * np.exp(-(rr / (p["v_max"] * tau_p + 0.02)) ** 4)
           * np.exp(-(k_loc / p["k_cut"]) ** 2))
    out = p["A"] * env * np.cos(p["g_eff"] * tau_p * tau_p / (4.0 * rr) + p["phi"])
    return np.where(tau > 0, out, 0.0)


KERNELS = {"ring": (ring, RING_PARAMS, RING_BOUNDS, RING_INIT, RING_COST),
           "chirp": (chirp, CHIRP_PARAMS, CHIRP_BOUNDS, CHIRP_INIT, CHIRP_COST)}


def evaluate_events(kind: str, p: dict, pts: np.ndarray, times: np.ndarray,
                    ev_pos: np.ndarray, ev_t: np.ndarray, ev_amp: np.ndarray,
                    live_eps: float = 1e-3) -> tuple[np.ndarray, float]:
    """Superpose one token per event. Returns (height (F, N), mean live tokens per point).

    A token counts as live at a point when its envelope there exceeds live_eps of its peak.
    """
    fn = KERNELS[kind][0]
    d = np.linalg.norm(pts[:, None, :] - ev_pos[None, :, :], axis=-1)  # (N, E)
    out = np.zeros((len(times), pts.shape[0]))
    live = 0.0
    for f, t in enumerate(times):
        tau = (t - ev_t)[None, :]  # (1, E)
        h = fn(d, tau, p) * ev_amp[None, :]
        out[f] = h.sum(1)
        live += (np.abs(h) > live_eps * np.abs(ev_amp).max() * p["A"]).sum(1).mean()
    return out, live / len(times)
