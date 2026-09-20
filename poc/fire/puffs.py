"""A second cheap fire grammar: sources emit puffs that rise, drift, grow and cool on their own.

The anchored-column grammar in `tokens.py` failed for one reason, found three times over: every
source was a single shape fixed to its cause. A plume is not that. It is a train of hot parcels
leaving the source, each one carried up by its own buoyancy, sideways by the wind, around a shelf
by the shelf, and cooling as it goes. Nothing about that needs state: a parcel emitted at time
t_k has a position and a temperature at time t that are closed-form functions of (t - t_k), so a
frame is still evaluated on its own, from the causes, with no stepping. Flicker, detachment at
switch-off and splitting around a shelf are not separate tokens here; they are what a train of
discrete parcels does.

Parameters, on-states and ranges were set from physical reasoning and from four numbers measured
on the unscored `plume` scene (`poc/fire_puff_probe.py`): rise speed, puffing frequency, tongue
height and width growth. None was fitted to a scored scene before the pilot, which is declared in
`docs/math-track-f4-prereg.md`.
"""
from __future__ import annotations

from dataclasses import dataclass, fields as dc_fields

import numpy as np

from .teacher import FireParams, FireRecord, T_AMBIENT, _grid

GUST_HZ = 0.7          # the teacher's crosswind gust frequency, a known property of the cause
MAX_LIVE = 40          # hard cap on parcels per source per frame; the cost bar is lower


@dataclass(frozen=True)
class PuffState:
    """V0 is the puff train alone. Every other field is an expansion, off at zero."""
    # --- V0: the train
    amp: float = 600.0          # K of excess temperature at a parcel's peak; parcels overlap
    rate: float = 6.0           # Hz, parcels emitted per second by a source
    v_rise: float = 2.2         # m/s, the speed a parcel settles to (teacher front: 2.25 m/s by 1.2 m)
    accel: float = 2.5          # 1/s, how fast it gets there from rest (teacher: 0.75 m/s at 0.45 m)
    burn: float = 0.3           # s a parcel holds its peak (fuel still burning)
    cool: float = 1.0           # s e-folding time once it stops burning (teacher: -0.76 over 1.07 s)
    width: float = 0.06         # m lateral sigma at birth (teacher: 0.06 at 0.2 m)
    grow: float = 0.04          # m per second of lateral growth (teacher: 0.094 at 1.2 m)
    aspect: float = 2.5         # vertical sigma over lateral sigma: parcels stretch in the shear
    # --- expansions
    jitter: float = 0.0         # m of hashed lateral offset per parcel: asymmetry and flicker
    wind: float = 0.0           # m/s steady lateral drift
    gust: float = 0.0           # m/s amplitude of drift oscillating at GUST_HZ
    deflect: float = 0.0        # m of sideways drift per metre climbed under a shelf's influence
    reach: float = 0.0          # m below the shelf at which that influence starts
    sharp: float = 0.0          # parcel profile exponent; 0 means the Gaussian default of 2
    base_amp: float = 0.0       # K excess held in the burner disc while it is on
    soot_amp: float = 0.0       # soot a parcel carries at birth
    soot_tau: float = 0.0       # s e-folding of that soot
    bed_amp: float = 0.0        # K excess of a bed fire's parcels at its plateau
    bed_delay: float = 0.0      # s before the nearest bed lights
    bed_speed: float = 0.0      # s per metre of extra delay with distance from the flame
    bed_dur: float = 0.0        # s the bed holds its plateau before the fuel runs out
    bed_fall: float = 0.0       # s the bed takes to die once it has
    attract: float = 0.0        # m/s of lateral drift toward another live source (entrainment)
    floor: float = 0.0          # K of uniform excess: the deliberate wrong atom

    def enabled(self):
        base = ["amp", "rate", "v_rise", "accel", "burn", "cool", "width", "grow", "aspect"]
        return base + [f.name for f in dc_fields(self)
                       if f.name not in base and getattr(self, f.name) != 0.0]

    def cost(self):
        return len(self.enabled())

    def life(self):
        """Age past which a parcel is too cold to matter: its hold plus three cooling times (5%)."""
        return min(self.burn + 3.0 * max(self.cool, 1e-3), 4.0)

    def live_count(self):
        """Parcels per source per frame at steady state: the runtime cost of this state."""
        return int(np.ceil(self.life() * self.rate))


# ---------------------------------------------------------------- one parcel
def _hash(k, salt=0):
    """Deterministic per-parcel number in [0, 1): stateless jitter."""
    h = (np.asarray(k, dtype=np.int64) * 2654435761 + salt * 97 + 12345) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 1274126177) & 0xFFFFFFFF
    return ((h >> 8) & 0xFFFFFF) / float(1 << 24)


def _kinematics(st: PuffState, a, t_k, t, x0, y0, k, others, obstacles):
    """Position and the two sigmas of parcels of ages `a` (array), emitted at `t_k`, now at `t`."""
    y = y0 + st.v_rise * (a - (1.0 - np.exp(-st.accel * a)) / st.accel)
    x = np.full_like(a, x0)
    if st.jitter != 0.0:
        x = x + st.jitter * (2.0 * _hash(k) - 1.0)
    if st.wind != 0.0:
        x = x + st.wind * a
    if st.gust != 0.0:
        w = 2.0 * np.pi * GUST_HZ
        x = x + (st.gust / w) * (np.cos(w * t_k) - np.cos(w * t))
    if st.attract != 0.0 and others:
        for ox in others:
            x = x + st.attract * a * np.sign(ox - x0)
    sig = st.width + st.grow * a
    sy = st.aspect * sig
    if st.deflect != 0.0 and obstacles:
        reach = max(st.reach, 0.05)
        for o in obstacles:
            bottom = o.y - o.half_h
            start = bottom - reach
            under = np.abs(x - o.x) <= o.half_w + sig
            hit = (y > start) & under
            if not hit.any():
                continue
            side = np.sign(x - o.x)
            side = np.where(side == 0.0, 1.0, side)
            # approaching: drift sideways at `deflect` per metre climbed once inside the reach
            climb = np.clip(y - start, 0.0, reach)
            x_new = x + side * st.deflect * climb
            # blocked: the climb the shelf denies is spent moving sideways under it, and whatever
            # is left once the parcel clears the edge is climb again
            denied = np.maximum(y - bottom, 0.0)
            to_edge = np.maximum((o.half_w + 2.0 * sig) - np.abs(x_new - o.x), 0.0)
            slide = np.minimum(denied, to_edge)
            x_new = x_new + side * slide
            # a parcel under the shelf is a pancake, not a blob: its vertical extent is capped by
            # the gap left below the shelf, so its tail never heats the space above a shelf it
            # has not cleared
            y_new = np.where(denied > 0.0, bottom - 0.75 * sig + (denied - slide), y)
            not_cleared = hit & (np.abs(x_new - o.x) <= o.half_w + 2.0 * sig)
            flat = np.clip(bottom - y_new, 0.25 * sig, sy)
            x = np.where(hit, x_new, x)
            y = np.where(hit, y_new, y)
            sy = np.where(not_cleared, flat, sy)
    return x, y, sig, sy


def _emit(st: PuffState, t, t_on, t_off, x0, y0, others, obstacles, k_salt):
    """Parcels alive at time t from a source on over [t_on, t_off]: (x, y, sigma, age, index)."""
    life = st.life()
    if t <= t_on:
        return None
    k_hi = int(np.floor((min(t, t_off) - t_on) * st.rate))
    k_lo = int(np.ceil((t - life - t_on) * st.rate))
    k_lo = max(k_lo, 0)
    if k_hi < k_lo:
        return None
    k = np.arange(k_lo, k_hi + 1)
    if len(k) > MAX_LIVE:
        k = k[-MAX_LIVE:]
    t_k = t_on + k / st.rate
    a = t - t_k
    x, y, sig, sy = _kinematics(st, a, t_k, t, x0, y0, k + k_salt, others, obstacles)
    return x, y, sig, sy, a, k


def _envelope(st: PuffState, a):
    return np.where(a <= st.burn, 1.0, np.exp(-(a - st.burn) / max(st.cool, 1e-3)))


def _splat(field, xs, ys, x, y, sx, sy, amp, q=2.0):
    """Combine separable Gaussian blobs into a (ny, nx) field by maximum, each on its own slice.

    Temperature is intensive: two parcels overlapping are the same hot gas, not twice as hot. A sum
    would pile the slow parcels near the source into thousands of kelvin, which the first pilot
    did, and the fitter then shrank the train until it was invisible. The maximum makes `amp` the
    flame temperature and overlap only a matter of continuity.
    """
    dx = xs[1] - xs[0]
    nx, ny = len(xs), len(ys)
    for xi, yi, sxi, syi, ai in zip(x, y, sx, sy, amp):
        if ai <= 0.0:
            continue
        i0 = max(int((xi - 3.5 * sxi) / dx), 0); i1 = min(int((xi + 3.5 * sxi) / dx) + 2, nx)
        j0 = max(int((yi - 3.5 * syi) / dx), 0); j1 = min(int((yi + 3.5 * syi) / dx) + 2, ny)
        if i1 <= i0 or j1 <= j0:
            continue
        gx = np.exp(-0.5 * np.abs((xs[i0:i1] - xi) / sxi) ** q)
        gy = np.exp(-0.5 * np.abs((ys[j0:j1] - yi) / syi) ** q)
        np.maximum(field[j0:j1, i0:i1], ai * gy[:, None] * gx[None, :], out=field[j0:j1, i0:i1])


def _bed_envelope(st: PuffState, t, t_ign):
    tau = t - t_ign
    if tau <= 0.0:
        return 0.0
    rise = max(0.15 * st.bed_dur, 1e-3)
    up = 1.0 - np.exp(-tau / rise)
    down = np.exp(-max(tau - st.bed_dur, 0.0) / max(st.bed_fall, 1e-3))
    return float(up * down)


# ---------------------------------------------------------------- the field
def evaluate(st: PuffState, p: FireParams, times, burners, patches, obstacles):
    """Return (T, soot), each (F, ny, nx) float32: the whole output of the cheap model."""
    X, Y = _grid(p)
    xs, ys = X[0], Y[:, 0]
    F = len(times)
    exc = np.zeros((F, p.ny, p.nx))
    soot = np.zeros((F, p.ny, p.nx))
    burner_xy = [(b.x, b.y) for b in burners]
    q = st.sharp if st.sharp > 0.0 else 2.0
    for f, t in enumerate(times):
        for bi, b in enumerate(burners):
            others = [ox for oi, (ox, oy) in enumerate(burner_xy) if oi != bi and burners[oi].t_on <= t] \
                if st.attract != 0.0 else []
            em = _emit(st, t, b.t_on, b.t_off, b.x, b.y, others, obstacles, k_salt=1000 * bi)
            if em is not None:
                x, y, sig, sy, a, k = em
                _splat(exc[f], xs, ys, x, y, sig, sy, st.amp * _envelope(st, a), q)
                if st.soot_amp != 0.0 and st.soot_tau > 0.0:
                    _splat(soot[f], xs, ys, x, y, sig, sy, st.soot_amp * np.exp(-a / st.soot_tau), q)
            if st.base_amp != 0.0 and b.t_on <= t <= b.t_off:
                r4 = (((X - b.x) ** 2 + (Y - b.y) ** 2) / max(b.radius, 1e-3) ** 2) ** 2
                np.maximum(exc[f], st.base_amp * np.exp(-r4), out=exc[f])
        if st.bed_amp != 0.0 and patches:
            bx = burners[0].x if burners else p.nx * p.dx * 0.5
            by = burners[0].y if burners else 0.0
            for qi, q in enumerate(patches):
                d = float(np.hypot(q.x - bx, q.y - by))
                t_ign = st.bed_delay + st.bed_speed * d
                em = _emit(st, t, t_ign, 1e9, q.x, q.y, [], obstacles, k_salt=5000 + 1000 * qi)
                if em is None:
                    continue
                x, y, sig, sy, a, k = em
                env_k = np.array([_bed_envelope(st, t - ak, t_ign) for ak in a])   # bed level at emission
                _splat(exc[f], xs, ys, x, y, sig, sy, st.bed_amp * env_k * _envelope(st, a), q)
    if st.floor != 0.0:
        exc += st.floor
    solid = np.zeros((p.ny, p.nx), dtype=bool)
    for o in obstacles:
        solid |= (np.abs(X - o.x) <= o.half_w) & (np.abs(Y - o.y) <= o.half_h)
    exc = np.where(solid[None], 0.0, exc)
    return (T_AMBIENT + exc).astype(np.float32), np.maximum(soot, 0.0).astype(np.float32)


def as_record(st: PuffState, p, times, burners, patches, obstacles) -> FireRecord:
    """Wrap the cheap output so the teacher's own consumer functions read it unchanged."""
    Tf, soot = evaluate(st, p, times, burners, patches, obstacles)
    X, Y = _grid(p)
    solid = np.zeros((p.ny, p.nx), dtype=bool)
    for o in obstacles:
        solid |= (np.abs(X - o.x) <= o.half_w) & (np.abs(Y - o.y) <= o.half_h)
    fuel = np.zeros_like(Tf)
    times = np.asarray(times, float)
    if st.bed_amp != 0.0 and patches:
        bx = burners[0].x if burners else 0.0
        by = burners[0].y if burners else 0.0
        for q in patches:
            d = float(np.hypot(q.x - bx, q.y - by))
            t_ign = st.bed_delay + st.bed_speed * d
            tau = np.maximum(times - t_ign, 0.0)
            left = np.clip(1.0 - tau / max(st.bed_dur, 1e-3), 0.0, 1.0)
            left = np.where(times >= t_ign, left, 1.0)
            m = ((X - q.x) ** 2 + (Y - q.y) ** 2) <= q.radius ** 2
            fuel += (m[None] * q.amount) * left[:, None, None]
    else:
        for q in patches:
            m = ((X - q.x) ** 2 + (Y - q.y) ** 2) <= q.radius ** 2
            fuel += (m * q.amount)[None]
    return FireRecord(p, times, Tf, soot, fuel.astype(np.float32), solid, {"cheap": "puffs"})
