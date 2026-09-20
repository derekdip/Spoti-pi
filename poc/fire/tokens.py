"""The cheap fire representation: a stateless closed-form field driven by the scene's causes.

Deliberately underpowered at V0. A burner is a buoyant column of excess temperature: Gaussian
across, exponential decay with height, a width that grows linearly. That is the whole of it. No
flicker, no wind, no soot, no obstacle, no rise time, and a fuel patch does nothing at all.

Everything past V0 is an expansion that the residual has to ask for. The structure of each
expansion was written from physical reasoning before any residual was computed: a plume puffs, a
crosswind leans it, soot obscures it, heat takes time to climb, a solid deflects it, and an
ignited bed becomes a second source at a delay that grows with its distance from the flame.

Like the corn and water grammars this is a pure function of (causes, parameters, time). No state,
no stepping, so any frame can be evaluated on its own.
"""
from __future__ import annotations

from dataclasses import dataclass, replace, fields as dc_fields

import numpy as np

from .teacher import FireParams, FireRecord, T_AMBIENT, _grid

GUST_HZ = 0.7          # the teacher's crosswind gust frequency, a known property of the cause


@dataclass(frozen=True)
class FireState:
    """V0 is the first four numbers. Every other field is an expansion, off at zero."""
    # --- V0 column
    amp: float = 900.0          # K of excess temperature at the source
    height: float = 1.6         # m, e-folding height of the excess
    width: float = 0.06         # m, Gaussian half-width at the source
    spread: float = 0.02        # width growth per metre climbed
    # --- expansions
    soot_amp: float = 0.0       # peak soot concentration at the source
    soot_height: float = 0.0    # m, its e-folding height
    flicker_amp: float = 0.0    # fractional amplitude of the puffing oscillation
    flicker_hz: float = 0.0     # Hz
    flicker_lag: float = 0.0    # s per metre: a puff travels up
    tilt: float = 0.0           # m of lean per metre climbed, from a steady wind
    tilt_gust: float = 0.0      # the same, oscillating at the gust frequency
    rise_speed: float = 0.0     # m/s the column establishes upward; 0 means instantly
    deflect: float = 0.0        # m of lateral push per metre of obstacle proximity
    sec_amp: float = 0.0        # excess temperature of an ignited fuel bed
    sec_delay: float = 0.0      # s before the nearest bed lights
    sec_speed: float = 0.0      # s per metre of extra delay with distance from the flame
    sec_dur: float = 0.0        # s the bed burns for
    floor: float = 0.0          # K of uniform excess: the deliberate wrong atom

    def enabled(self):
        """Names of the parameters currently doing anything, which is what a repair costs."""
        base = ["amp", "height", "width", "spread"]
        return base + [f.name for f in dc_fields(self)
                       if f.name not in base and getattr(self, f.name) != 0.0]

    def cost(self):
        return len(self.enabled())


# ---------------------------------------------------------------- the field
def _column(X, Y, T_, x0, y0, on, amp, height, width, spread, st, obstacles):
    """One source's excess-temperature field over (F, ny, nx). `on` is (F,) in [0, 1]."""
    dy = Y - y0
    up = np.maximum(dy, 0.0)
    # vertical: exponential above the source, a short tail below it
    prof = np.where(dy >= 0.0, np.exp(-up / max(height, 1e-3)),
                    np.exp(dy / max(0.12, 1e-3)))
    w = width + spread * up
    # lateral centre, per frame: steady lean, gust lean, obstacle deflection
    xc = x0 + st.tilt * up
    if st.tilt_gust != 0.0:
        lag = up / st.rise_speed if st.rise_speed > 0 else np.zeros_like(up)
        phase = 2.0 * np.pi * GUST_HZ * (T_[:, None, None] - lag[None])
        xc = xc[None] + st.tilt_gust * up[None] * np.sin(phase)
    else:
        xc = np.broadcast_to(xc, (len(T_),) + X.shape)
    if st.deflect != 0.0 and obstacles:
        push = np.zeros_like(X)
        for o in obstacles:
            reach = o.half_h + 0.25
            near = np.clip(1.0 - np.abs(Y - o.y) / reach, 0.0, 1.0)
            side = np.sign(x0 - o.x) if abs(x0 - o.x) > 1e-6 else 1.0
            inside = (np.abs(X - o.x) <= o.half_w + 0.10)
            push += st.deflect * near * side * inside
        xc = xc + push[None]
    lat = np.exp(-0.5 * ((X[None] - xc) / np.maximum(w, 1e-3)[None]) ** 2)
    f = amp * prof[None] * lat
    # temporal: rise time up the column, then flicker
    gate = on[:, None, None]
    if st.rise_speed > 0.0:
        pass  # the caller already folded the rise delay into `on`
    if st.flicker_amp != 0.0 and st.flicker_hz > 0.0:
        ph = 2.0 * np.pi * st.flicker_hz * (T_[:, None, None] - st.flicker_lag * up[None])
        gate = gate * (1.0 + st.flicker_amp * np.sin(ph))
    return f * gate


def _gate(times, t_on, t_off, y0, Y, rise_speed):
    """(F, ny, nx) or (F,) on/off, delayed by climb time when a rise speed is set."""
    if rise_speed and rise_speed > 0.0:
        lag = np.maximum(Y - y0, 0.0) / rise_speed
        g = ((times[:, None, None] >= t_on + lag[None]) &
             (times[:, None, None] <= t_off + lag[None])).astype(float)
        return g
    return ((times >= t_on) & (times <= t_off)).astype(float)


def evaluate(st: FireState, p: FireParams, times, burners, patches, obstacles):
    """Return (T, soot) each (F, ny, nx) float32, the cheap model's whole output."""
    X, Y = _grid(p)
    F = len(times)
    exc = np.zeros((F, p.ny, p.nx))
    soot = np.zeros((F, p.ny, p.nx))
    for b in burners:
        g = _gate(times, b.t_on, b.t_off, b.y, Y, st.rise_speed)
        if g.ndim == 1:
            col = _column(X, Y, times, b.x, b.y, g, st.amp, st.height, st.width, st.spread, st, obstacles)
        else:
            col = _column(X, Y, times, b.x, b.y, np.ones(F), st.amp, st.height, st.width, st.spread, st, obstacles) * g
        exc += col
        if st.soot_amp != 0.0:
            s = _column(X, Y, times, b.x, b.y, np.ones(F) if g.ndim > 1 else g,
                        st.soot_amp, max(st.soot_height, 1e-3), st.width, st.spread,
                        replace(st, flicker_amp=0.0), obstacles)
            soot += s * (g if g.ndim > 1 else 1.0)
    if st.sec_amp != 0.0 and patches:
        bx = burners[0].x if burners else p.nx * p.dx * 0.5
        by = burners[0].y if burners else 0.0
        for q in patches:
            d = float(np.hypot(q.x - bx, q.y - by))
            t_ign = st.sec_delay + st.sec_speed * d
            g = _gate(times, t_ign, t_ign + max(st.sec_dur, 1e-3), q.y, Y, 0.0)
            exc += _column(X, Y, times, q.x, q.y, g, st.sec_amp, max(st.height * 0.5, 1e-3),
                           q.radius, st.spread, replace(st, tilt_gust=0.0, deflect=0.0), obstacles)
    if st.floor != 0.0:
        exc += st.floor
    solid = np.zeros((p.ny, p.nx), dtype=bool)
    for o in obstacles:
        solid |= (np.abs(X - o.x) <= o.half_w) & (np.abs(Y - o.y) <= o.half_h)
    exc = np.where(solid[None], 0.0, exc)
    return (T_AMBIENT + exc).astype(np.float32), np.maximum(soot, 0.0).astype(np.float32)


def as_record(st: FireState, p, times, burners, patches, obstacles) -> FireRecord:
    """Wrap the cheap output so the teacher's own consumer functions read it unchanged."""
    Tf, soot = evaluate(st, p, times, burners, patches, obstacles)
    X, Y = _grid(p)
    solid = np.zeros((p.ny, p.nx), dtype=bool)
    for o in obstacles:
        solid |= (np.abs(X - o.x) <= o.half_w) & (np.abs(Y - o.y) <= o.half_h)
    fuel = np.zeros_like(Tf)
    if st.sec_amp != 0.0 and patches:
        bx = burners[0].x if burners else 0.0
        by = burners[0].y if burners else 0.0
        for q in patches:
            d = float(np.hypot(q.x - bx, q.y - by))
            t_ign = st.sec_delay + st.sec_speed * d
            m = ((X - q.x) ** 2 + (Y - q.y) ** 2) <= q.radius ** 2
            live = (times >= t_ign) & (times <= t_ign + max(st.sec_dur, 1e-3))
            fuel[np.ix_(np.where(live)[0], *[np.arange(s) for s in m.shape])] += m * q.amount
    else:
        for q in patches:
            m = ((X - q.x) ** 2 + (Y - q.y) ** 2) <= q.radius ** 2
            fuel += (m * q.amount)[None]
    return FireRecord(p, times, Tf, soot, fuel.astype(np.float32), solid, {"cheap": True})
