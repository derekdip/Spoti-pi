"""RGRE over the puff grammar: vocabulary, ranges, on-states, the case, and the fitters.

Same consumer-space residual as `rgre_fire.py`, same diagnosis and selection from `poc/rgre/core`.
Only the representation and its class structure differ. Class structure, ranges and on-states
were written before any scored scene was fitted; the pilot that touched two seen scenes is
declared in the F4 preregistration.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from . import teacher as TT
from .rgre_fire import FireCase
from .puffs import PuffState, as_record

# ---------------------------------------------------------------- vocabulary
V0_CLASSES = ("amp", "rate", "rise", "cool", "width")
CLASSES = {
    "amp":     ["amp"],
    "rate":    ["rate"],
    "rise":    ["v_rise", "accel"],
    "cool":    ["burn", "cool"],
    "width":   ["width", "grow", "aspect"],
    # expansions
    "jitter":  ["jitter"],
    "wind":    ["wind", "gust"],
    "deflect": ["deflect", "reach"],
    "base":    ["base_amp"],
    "soot":    ["soot_amp", "soot_tau"],
    "bed":     ["bed_amp", "bed_delay", "bed_speed", "bed_dur", "bed_fall"],
    "attract": ["attract"],
    "profile": ["sharp"],
    "floor":   ["floor"],
}
SUPPORT_CLASSES = ("deflect", "bed")
UNREPAIRABLE = ()

RANGES = {
    "amp":       (300.0, 1400.0),
    "rate":      (0.5, 10.0),
    "v_rise":    (0.3, 4.0),
    "accel":     (0.5, 30.0),
    "burn":      (0.0, 1.5),
    "cool":      (0.05, 2.0),
    "width":     (0.02, 0.20),
    "grow":      (0.0, 0.30),
    "aspect":    (0.3, 5.0),
    "jitter":    (0.0, 0.15),
    "wind":      (-1.0, 1.0),
    "gust":      (0.0, 1.5),
    "deflect":   (0.0, 1.5),
    "reach":     (0.05, 1.0),
    "sharp":     (1.0, 6.0),
    "base_amp":  (0.0, 1200.0),
    "soot_amp":  (0.0, 14.0),
    "soot_tau":  (0.2, 4.0),
    "bed_amp":   (0.0, 1200.0),
    "bed_delay": (0.0, 3.0),
    "bed_speed": (0.0, 3.0),
    "bed_dur":   (0.1, 3.0),
    "bed_fall":  (0.05, 2.0),
    "attract":   (-0.3, 0.3),
    "floor":     (0.0, 120.0),
}
EPS = {k: 0.04 * (hi - lo) for k, (lo, hi) in RANGES.items()}

ON = {
    "jitter":  {"jitter": 0.03},
    "wind":    {"wind": 0.2, "gust": 0.3},
    "deflect": {"deflect": 0.5, "reach": 0.4},
    "base":    {"base_amp": 600.0},
    "soot":    {"soot_amp": 3.0, "soot_tau": 2.0},
    "bed":     {"bed_amp": 500.0, "bed_delay": 0.5, "bed_speed": 0.5, "bed_dur": 1.2, "bed_fall": 0.5},
    "attract": {"attract": 0.05},
    "profile": {"sharp": 3.0},
    "floor":   {"floor": 30.0},
}


# ---------------------------------------------------------------- the case
class PuffCase(FireCase):
    """The same teacher, targets and residual; the cheap side is the puff grammar."""

    def _consumers(self, st: PuffState):
        key = tuple(getattr(st, f) for f in st.__dataclass_fields__)
        if key in self._cache:
            return self._cache[key]
        rec = as_record(st, self.p, self.times, self.burners, self.patches, self.obstacles)
        out = {}
        for cname in self.names:
            if cname == "visual":
                v = TT.g_visual(rec)
            elif cname == "heat":
                v = TT.g_heat(rec, self.probes)
            elif cname == "ignition":
                v = TT.g_ignition(rec, self.patches)
            else:
                v = TT.g_ai(rec)
            out[cname] = np.asarray(v, float).reshape(self.F, -1)
        self.evals += 1
        if len(self._cache) > 400:
            self._cache.clear()
        self._cache[key] = out
        return out

    def tangents(self, st: PuffState):
        base = self.residual(st).ravel()
        signed = {}
        for cls, params in CLASSES.items():
            live = cls in V0_CLASSES or any(getattr(st, q) != 0.0 for q in params)
            vs = []
            if live:
                for pname in params:
                    lo, hi = RANGES[pname]
                    cur = getattr(st, pname)
                    h = EPS[pname]
                    nxt = cur + h if cur + h <= hi else cur - h
                    if abs(nxt - cur) < 1e-12:
                        continue
                    d = (self.residual(replace(st, **{pname: nxt})).ravel() - base) / (nxt - cur)
                    if float(d @ d) > 0:
                        vs.append(d)
            else:
                on = replace(st, **ON[cls])
                r_on = self.residual(on).ravel()
                d = r_on - base
                if float(d @ d) > 0:
                    vs.append(d)
                for pname in params:
                    lo, hi = RANGES[pname]
                    cur = getattr(on, pname)
                    h = EPS[pname]
                    nxt = cur + h if cur + h <= hi else cur - h
                    if abs(nxt - cur) < 1e-12:
                        continue
                    dd = self.residual(replace(on, **{pname: nxt})).ravel() - r_on
                    if float(dd @ dd) > 0:
                        vs.append(dd)
            if vs:
                signed[cls] = vs
        return signed

    def templates(self):
        t = super().templates()
        return {k: v for k, v in t.items() if k in SUPPORT_CLASSES}


# ---------------------------------------------------------------- repairs
def _sweep(case, cur, pname, grid):
    lo, hi = RANGES[pname]
    vals = np.linspace(lo, hi, grid)
    errs = [case.error(replace(cur, **{pname: float(v)})) for v in vals]
    i = int(np.argmin(errs))
    cur = replace(cur, **{pname: float(vals[i])})
    step = (hi - lo) / (grid - 1)
    fine = np.linspace(max(lo, vals[i] - step), min(hi, vals[i] + step), grid)
    errs2 = [case.error(replace(cur, **{pname: float(v)})) for v in fine]
    return replace(cur, **{pname: float(fine[int(np.argmin(errs2))])})


def fit_class(case, st: PuffState, cls, grid=7):
    """Coordinate descent over the class's parameters, from the on-state if the class is off."""
    cur = st
    if cls in ON and all(getattr(st, q) == 0.0 for q in CLASSES[cls]):
        cur = replace(st, **ON[cls])
    for pname in CLASSES[cls]:
        cur = _sweep(case, cur, pname, grid)
    return cur, case.error(cur)


def repair_gain(case, st: PuffState, cls):
    e0, c0 = case.error(st), st.cost()
    new, e1 = fit_class(case, st, cls)
    dc = max(new.cost() - c0, 1)
    return dict(cls=cls, state=new, e0=e0, e1=e1, gain=(e0 - e1) / dc, drop=e0 - e1, dcost=dc)


def active_params(case):
    """Parameters that can do anything on this scene; the rest are exact plateaus."""
    drop = set()
    if not case.patches:
        drop |= set(CLASSES["bed"])
    if not case.obstacles:
        drop |= set(CLASSES["deflect"])
    if len(case.burners) < 2:
        drop |= set(CLASSES["attract"])
    return [q for params in CLASSES.values() for q in params if q not in drop]


def _vec_to_state(x, names, base: PuffState):
    return replace(base, **{n: float(np.clip(v, *RANGES[n])) for n, v in zip(names, x)})


def all_on(base: PuffState):
    on = base
    for cls in CLASSES:
        if cls in ON and all(getattr(on, q) == 0.0 for q in CLASSES[cls]):
            on = replace(on, **ON[cls])
    return on


TRAIN_ONLY_OFF = ("base_amp", "soot_amp", "soot_tau", "floor")


def two_stage_start(case, base: PuffState, names, maxfev_per_dim=40):
    """Fit the train with the hot disc, the soot and the floor held off, then hand everything over.

    The pilot found every single-stage start parked in a hot-disc optimum with an invisible train:
    a hot un-sooted tongue glows ten times brighter than the teacher's sooty one, so from any
    start the cheapest move is to cool the train until it vanishes. Fitting the train alone first
    forces it to carry the consumers, and the second stage then adds soot and the disc to a state
    that already has a tongue. On `windy` this found 0.339 where three single-stage starts found
    0.370 and the column grammar 0.385.
    """
    from scipy.optimize import minimize
    train = [n for n in names if n not in TRAIN_ONLY_OFF]
    lo = np.array([RANGES[n][0] for n in train]); hi = np.array([RANGES[n][1] for n in train])
    x0 = np.array([float(np.clip(getattr(base, n), *RANGES[n])) for n in train])
    r = minimize(lambda x: case.error(_vec_to_state(x, train, base)), x0, method="Powell",
                 bounds=list(zip(lo, hi)), options={"maxfev": maxfev_per_dim * len(train), "xtol": 1e-3, "ftol": 1e-4})
    st = _vec_to_state(r.x, train, base)
    st = replace(st, **ON["soot"], base_amp=ON["base"]["base_amp"])
    return np.array([float(np.clip(getattr(st, n), *RANGES[n])) for n in names])


def de_fit(case, base: PuffState, names, seed=0, popsize=12, maxiter=30, maxfev_per_dim=40):
    """Seeded differential evolution over the active parameters, then a Powell polish.

    Every local start the pilot tried (all-on, V0, midpoint, two-stage) sat in a different basin
    and none was reliable; on `obstacle` a global search from a Latin hypercube found 0.46 where
    the best local start found 0.52. Deterministic for a given seed, so a rerun reproduces it.
    """
    from scipy.optimize import differential_evolution, minimize
    lo = np.array([RANGES[n][0] for n in names]); hi = np.array([RANGES[n][1] for n in names])
    obj = lambda x: case.error(_vec_to_state(x, names, base))
    r = differential_evolution(obj, list(zip(lo, hi)), maxiter=maxiter, popsize=popsize, seed=seed,
                               tol=1e-6, polish=False, init="latinhypercube")
    r2 = minimize(obj, r.x, method="Powell", bounds=list(zip(lo, hi)),
                  options={"maxfev": maxfev_per_dim * len(names), "xtol": 1e-3, "ftol": 1e-4})
    x, e = (r2.x, float(r2.fun)) if r2.fun <= r.fun else (r.x, float(r.fun))
    return x, e, int(r.nfev + r2.nfev)


def floor_fit(case, base: PuffState, starts=None, maxfev_per_dim=40, verbose=False):
    """Best error the grammar reaches on this scene: a global search and a two-stage local one.

    Two candidates, the minimum kept and both reported: differential evolution with a Powell
    polish, and Powell from the two-stage start. Not monotone in anything; the fire arc showed no
    single optimiser is. The result is 'no worse than', and the spread is reported with it.
    """
    from scipy.optimize import minimize
    names = active_params(case)
    lo = np.array([RANGES[n][0] for n in names]); hi = np.array([RANGES[n][1] for n in names])

    def obj(x):
        return case.error(_vec_to_state(x, names, base))

    spread = {}
    x_de, e_de, n_de = de_fit(case, base, names, maxfev_per_dim=maxfev_per_dim)
    spread["de"] = e_de
    if verbose:
        print(f"      de: {e_de:.4f} in {n_de} evals", flush=True)
    x0 = np.clip(two_stage_start(case, base, names, maxfev_per_dim), lo, hi)
    e0 = obj(x0)
    r = minimize(obj, x0, method="Powell", bounds=list(zip(lo, hi)),
                 options={"maxfev": maxfev_per_dim * len(names), "xtol": 1e-3, "ftol": 1e-4})
    e_ts = min(float(r.fun), e0)
    x_ts = r.x if r.fun <= e0 else x0
    spread["two_stage"] = e_ts
    if verbose:
        print(f"      two-stage: {e0:.4f} -> {e_ts:.4f} in {r.nfev} evals", flush=True)
    best_x, best_e = (x_de, e_de) if e_de <= e_ts else (x_ts, e_ts)
    return _vec_to_state(best_x, names, base), float(best_e), names, spread
# ---------------------------------------------------------------- how much it moves, reported only
def motion_ratio(case, st, k=4):
    """Cheap over teacher temporal standard deviation of the coarse glow, median over the tenth of
    cells where the teacher moves most, second half of the run. Not fitted and not a bar: the
    frame-wise objective is minimised by the mean fire, so this says how much motion that cost."""
    F = case.F
    tgt = case.target["visual"][F // 2:].std(axis=0)
    pred = case._consumers(st)["visual"][F // 2:].std(axis=0)
    hot = tgt >= np.quantile(tgt, 0.9)
    return float(np.median(pred[hot] / np.maximum(tgt[hot], 1e-9)))


# ---------------------------------------------------------------- what the player actually sees
GAMMA = 1.0 / 2.2   # display transfer: the tongue at a tenth of the base's glow is a third as bright


class LookCase:
    """The same case with the visual consumer tone-mapped before it is compared.

    Under a linear glow the sooted base holds nearly all of the visual energy and the tongue, at a
    tenth of its value, costs almost nothing to leave out; the first pilot fitted exactly that.
    A player sees glow through a display gamma, so this consumer compares `glow ** (1/2.2)`.
    Heat, ignition and hazard are untouched. Every bar is still scored on the untouched case.
    """

    def __init__(self, case: PuffCase):
        self.inner = case
        self.__dict__.update({k: v for k, v in case.__dict__.items() if k not in ("target", "scale", "_cache")})
        self.target = dict(case.target)
        self.scale = dict(case.scale)
        t = case.target["visual"] ** GAMMA
        self.target["visual"] = t
        self.scale["visual"] = float(np.sqrt((t ** 2).mean()))
        self._cache = {}

    def _consumers(self, st):
        out = dict(self.inner._consumers(st))
        out["visual"] = out["visual"] ** GAMMA
        return out

    residual = FireCase.residual
    error = FireCase.error
    per_consumer = FireCase.per_consumer
    blocks = FireCase.blocks
    tangents = PuffCase.tangents
    templates = PuffCase.templates
