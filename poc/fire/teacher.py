"""Expensive offline fire teacher: 2D buoyant reacting flow with fuel, soot and obstacles.

Deliberately not designed around any cheap representation. It is a standard stable-fluids solver
(semi-Lagrangian advection, Jacobi pressure projection, vorticity confinement) carrying
temperature, fuel and soot, with Arrhenius-free threshold combustion and a solid mask.

Fields are stored as (ny, nx) with axis 0 running upward. SI units, temperature in kelvin.

Consumers (defined here, not in the representation) follow the game's needs rather than the
solver's state: what the player sees, what burns them, what catches fire, and where the AI must
not walk.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import map_coordinates

T_AMBIENT = 293.0


@dataclass
class FireParams:
    nx: int = 96
    ny: int = 160
    size_x: float = 1.5           # m; dx = size_x / nx, square cells
    fps: int = 60
    substeps: int = 4
    duration: float = 4.0
    ignite_T: float = 573.0       # K, ~300 C
    burn_rate: float = 14.0       # 1/s, fuel consumed per second above ignition
    heat_release: float = 247.0   # K per unit fuel burned; heat_release * burn_rate is set against
                                  # cooling + radiate so a fed flame sits near 1200 K
    soot_yield: float = 0.6       # soot per unit fuel burned
    cooling: float = 2.4          # 1/s Newtonian cooling toward ambient
    radiate: float = 1.6          # extra cooling proportional to (T - amb)^2 / 1e3
    buoyancy: float = 1.4         # m/s^2, times (T - amb) / amb; below the 2-D inviscid value,
                                  # which overshoots because a 2-D plume cannot entrain cool air the way a 3-D one does
    conduct: float = 0.0016       # m^2/s thermal diffusivity; lets a flame hold on a fuel bed
    vort_eps: float = 0.32        # vorticity confinement strength
    drag: float = 0.08            # 1/s velocity damping
    soot_decay: float = 0.35      # 1/s
    jacobi: int = 50
    sponge: int = 12              # damping cells at the top edge
    wind: float = 0.0             # m/s steady crosswind
    gust_amp: float = 0.0         # m/s amplitude of a crosswind gust
    gust_hz: float = 0.7          # its frequency; a property of the cause, not of any model
    base_noise: float = 0.0       # m/s of optional seeded turbulence in the reacting zone; the
                                  # unforced column already flickers, so this is off by default
    seed: int = 0

    @property
    def dx(self) -> float:
        return self.size_x / self.nx

    @property
    def dt(self) -> float:
        return 1.0 / (self.fps * self.substeps)


@dataclass
class Burner:
    """A gas jet: holds a fuel concentration inside a disc, with a brief igniter at switch-on.

    Holding a level rather than adding a rate matters: the buoyant flow sweeps injected fuel out of
    the disc within a step or two, so a rate-based source never reaches a reacting concentration.
    """
    x: float
    y: float
    radius: float = 0.09
    level: float = 1.0            # fuel concentration maintained inside the disc while on
    t_on: float = 0.0
    t_off: float = 1e9
    pilot_T: float = 1200.0       # K, the igniter
    pilot_for: float = 1e9        # s, how long the igniter is held after t_on (a continuous pilot by default)


@dataclass
class FuelPatch:
    """A finite fuel bed that can be ignited by the flow and then burns out."""
    x: float
    y: float
    radius: float = 0.07
    amount: float = 1.4


@dataclass
class Obstacle:
    x: float
    y: float
    half_w: float
    half_h: float


@dataclass
class FireRecord:
    p: FireParams
    times: np.ndarray             # (F,)
    T: np.ndarray                 # (F, ny, nx) float32, kelvin
    soot: np.ndarray              # (F, ny, nx) float32
    fuel: np.ndarray              # (F, ny, nx) float32
    solid: np.ndarray             # (ny, nx) bool
    meta: dict = field(default_factory=dict)

    @property
    def extent(self):
        return (0.0, self.p.nx * self.p.dx, 0.0, self.p.ny * self.p.dx)


def _grid(p: FireParams):
    xs = (np.arange(p.nx) + 0.5) * p.dx
    ys = (np.arange(p.ny) + 0.5) * p.dx
    return np.meshgrid(xs, ys)  # X, Y both (ny, nx)


def _disc(X, Y, x0, y0, r):
    return ((X - x0) ** 2 + (Y - y0) ** 2) <= r * r


def _advect(f, u, v, dt, dx):
    ny, nx = f.shape
    J, I = np.meshgrid(np.arange(nx, dtype=float), np.arange(ny, dtype=float))
    yi = I - dt * v / dx
    xi = J - dt * u / dx
    np.clip(yi, 0, ny - 1, out=yi)
    np.clip(xi, 0, nx - 1, out=xi)
    return map_coordinates(f, [yi, xi], order=1, mode="nearest")


def _divergence(u, v, dx):
    du = np.gradient(u, dx, axis=1)
    dv = np.gradient(v, dx, axis=0)
    return du + dv


def _project(u, v, dx, solid, iters):
    div = _divergence(u, v, dx)
    div = np.where(solid, 0.0, div)
    p = np.zeros_like(div)
    rhs = div * dx * dx
    for _ in range(iters):
        q = np.pad(p, 1, mode="edge")
        p_new = 0.25 * (q[:-2, 1:-1] + q[2:, 1:-1] + q[1:-1, :-2] + q[1:-1, 2:] - rhs)
        p = np.where(solid, 0.0, p_new)
    gx = np.gradient(p, dx, axis=1)
    gy = np.gradient(p, dx, axis=0)
    u = u - gx
    v = v - gy
    u = np.where(solid, 0.0, u)
    v = np.where(solid, 0.0, v)
    return u, v, p


def _vorticity_confinement(u, v, dx, eps):
    w = np.gradient(v, dx, axis=1) - np.gradient(u, dx, axis=0)
    aw = np.abs(w)
    gx = np.gradient(aw, dx, axis=1)
    gy = np.gradient(aw, dx, axis=0)
    n = np.sqrt(gx * gx + gy * gy) + 1e-12
    nx_, ny_ = gx / n, gy / n
    fx = eps * dx * (ny_ * w)
    fy = -eps * dx * (nx_ * w)
    return fx, fy


def run(p: FireParams, burners=(), patches=(), obstacles=(), record_stride: int = 1) -> FireRecord:
    """Integrate the teacher and record temperature, soot and fuel at `fps / record_stride`."""
    rng = np.random.default_rng(p.seed)
    X, Y = _grid(p)
    solid = np.zeros((p.ny, p.nx), dtype=bool)
    for o in obstacles:
        solid |= (np.abs(X - o.x) <= o.half_w) & (np.abs(Y - o.y) <= o.half_h)
    u = np.zeros((p.ny, p.nx))
    v = np.zeros((p.ny, p.nx))
    T = np.full((p.ny, p.nx), T_AMBIENT)
    fuel = np.zeros((p.ny, p.nx))
    soot = np.zeros((p.ny, p.nx))
    for q in patches:
        fuel += q.amount * _disc(X, Y, q.x, q.y, q.radius)
    burner_masks = [_disc(X, Y, b.x, b.y, b.radius) for b in burners]
    # a little seeded noise so the plume is not perfectly symmetric
    T += rng.normal(0.0, 0.6, T.shape)

    sponge = np.ones((p.ny, p.nx))
    if p.sponge:
        ramp = np.linspace(0.0, 1.0, p.sponge)[::-1]
        sponge[-p.sponge:, :] *= ramp[:, None]

    n_frames = int(round(p.duration * p.fps)) // record_stride + 1
    times = np.arange(n_frames) * record_stride / p.fps
    Ts = np.zeros((n_frames, p.ny, p.nx), dtype=np.float32)
    Ss = np.zeros((n_frames, p.ny, p.nx), dtype=np.float32)
    Fs = np.zeros((n_frames, p.ny, p.nx), dtype=np.float32)
    total_steps = int(round(p.duration * p.fps)) * p.substeps
    t = 0.0
    frame = 0
    for step in range(total_steps + 1):
        if step % (p.substeps * record_stride) == 0 and frame < n_frames:
            Ts[frame] = T
            Ss[frame] = soot
            Fs[frame] = fuel
            frame += 1
        if step == total_steps:
            break
        dt = p.dt
        # sources
        for b, m in zip(burners, burner_masks):
            if b.t_on <= t <= b.t_off:
                fuel[m] = np.maximum(fuel[m], b.level)
                if t <= b.t_on + b.pilot_for:
                    T[m] = np.maximum(T[m], b.pilot_T)
        # combustion
        hot = (T > p.ignite_T) & (fuel > 0.0)
        burn = np.where(hot, np.minimum(fuel, p.burn_rate * fuel * dt), 0.0)
        fuel -= burn
        T += p.heat_release * burn
        soot += p.soot_yield * burn
        # cooling and conduction
        dT = T - T_AMBIENT
        T -= dt * (p.cooling * dT + p.radiate * dT * dT / 1e3)
        if p.conduct:
            q = np.pad(T, 1, mode="edge")
            lap = (q[:-2, 1:-1] + q[2:, 1:-1] + q[1:-1, :-2] + q[1:-1, 2:] - 4 * T) / (p.dx * p.dx)
            T = T + dt * p.conduct * lap
        soot *= np.exp(-p.soot_decay * dt)
        # forces
        v += dt * p.buoyancy * (T - T_AMBIENT) / T_AMBIENT
        if p.vort_eps:
            fx, fy = _vorticity_confinement(u, v, p.dx, p.vort_eps)
            u += dt * fx
            v += dt * fy
        if p.base_noise:
            react = (T > p.ignite_T)
            if react.any():
                amp = p.base_noise * np.sqrt(dt)
                u = u + amp * rng.normal(0.0, 1.0, u.shape) * react
                v = v + amp * rng.normal(0.0, 1.0, v.shape) * react
        if p.wind or p.gust_amp:
            u += dt * 4.0 * (p.wind + p.gust_amp * np.sin(2 * np.pi * p.gust_hz * t) - u)
        u *= np.exp(-p.drag * dt)
        v *= np.exp(-p.drag * dt)
        u = np.where(solid, 0.0, u) * sponge
        v = np.where(solid, 0.0, v) * sponge
        # advection
        u, v = _advect(u, u, v, dt, p.dx), _advect(v, u, v, dt, p.dx)
        u, v, _ = _project(u, v, p.dx, solid, p.jacobi)
        T = _advect(T, u, v, dt, p.dx)
        fuel = _advect(fuel, u, v, dt, p.dx)
        soot = _advect(soot, u, v, dt, p.dx)
        T = np.where(solid, T_AMBIENT, T)
        fuel = np.where(solid, 0.0, fuel)
        soot = np.where(solid, 0.0, soot)
        T = T_AMBIENT + (T - T_AMBIENT) * sponge
        t += dt
    return FireRecord(p, times, Ts, Ss, Fs, solid,
                      {"burners": len(burners), "patches": len(patches), "obstacles": len(obstacles)})


# ---------------------------------------------------------------- consumers
VIS_T0 = 700.0       # K, below this the gas does not glow enough to see
VIS_T1 = 1500.0      # K, saturated emission
HAZARD_T = 400.0     # K, the AI treats anything hotter as impassable


def coarsen(fields: np.ndarray, k: int) -> np.ndarray:
    """Block-average the trailing two axes by k, the resolution a game texture would carry."""
    f, ny, nx = fields.shape
    ny2, nx2 = ny // k, nx // k
    return fields[:, :ny2 * k, :nx2 * k].reshape(f, ny2, k, nx2, k).mean((2, 4))


def emission(T: np.ndarray) -> np.ndarray:
    return np.clip((T - VIS_T0) / (VIS_T1 - VIS_T0), 0.0, 1.0)


def g_visual(rec: FireRecord, k: int = 4) -> np.ndarray:
    """What the player sees: coarse glow, soot-obscured. (F, ny/k, nx/k)."""
    em = emission(rec.T) * np.exp(-0.5 * rec.soot)
    return coarsen(em, k)


def g_heat(rec: FireRecord, probes: np.ndarray) -> np.ndarray:
    """Temperature at probe points in metres, (F, P): what burns a hand."""
    dx = rec.p.dx
    yi = probes[:, 1] / dx - 0.5
    xi = probes[:, 0] / dx - 0.5
    return np.stack([map_coordinates(rec.T[f], [yi, xi], order=1, mode="nearest") for f in range(rec.T.shape[0])])


def g_ignition(rec: FireRecord, patches, hold: float = 0.05) -> np.ndarray:
    """Per fuel patch, whether it is alight at each frame, (F, P)."""
    X, Y = _grid(rec.p)
    out = np.zeros((rec.T.shape[0], len(patches)))
    for i, q in enumerate(patches):
        m = _disc(X, Y, q.x, q.y, q.radius)
        out[:, i] = ((rec.T[:, m] > rec.p.ignite_T) & (rec.fuel[:, m] > 1e-3)).mean(1)
    return out


def g_ai(rec: FireRecord, k: int = 16) -> np.ndarray:
    """Coarse hazard occupancy, (F, ny/k, nx/k)."""
    return coarsen((rec.T > HAZARD_T).astype(float), k)


CONSUMERS = {"visual": g_visual, "heat": g_heat, "ignition": g_ignition, "ai": g_ai}
