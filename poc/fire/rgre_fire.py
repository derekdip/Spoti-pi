"""RGRE on fire: cases, the class vocabulary, automatic repairs, and the consumer-space residual.

The residual lives in the consumers' joint space, not the field's. Each consumer's error is
normalised by its own target scale and by its own width, so the four contribute equally and the
norm the selector sees is the objective being minimised. That is the consumer triple made
concrete: what counts as a defect is defined by what reads the field.

Class structure and parameter ranges were written from physical reasoning before any residual was
computed. Nothing here is chosen per scene.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from . import teacher as TT
from .tokens import FireState, as_record

# ---------------------------------------------------------------- vocabulary
CLASSES = {
    "amp":       ["amp"],
    "height":    ["height"],
    "width":     ["width", "spread"],
    "soot":      ["soot_amp", "soot_height"],
    "flicker":   ["flicker_amp", "flicker_hz", "flicker_lag"],
    "tilt":      ["tilt", "tilt_gust"],
    "rise":      ["rise_speed"],
    "deflect":   ["deflect"],
    "secondary": ["sec_amp", "sec_delay", "sec_speed", "sec_dur"],
    "floor":     ["floor"],
}
SUPPORT_CLASSES = ("deflect", "secondary")
# Nothing here is unrepairable. `floor`, a uniform excess temperature, is a legal parameter and a
# physically wrong model of a flame, so it is kept as a distractor rather than an abstention
# trigger: the interesting question is whether the procedure spends a step on it, which requires
# letting it try. Out-of-vocabulary behaviour is tested with scenes instead, not with a class.
UNREPAIRABLE = ()

RANGES = {
    "amp":         (300.0, 1400.0),
    "height":      (0.4, 4.0),
    "width":       (0.02, 0.20),
    "spread":      (0.0, 0.12),
    "soot_amp":    (0.0, 14.0),
    "soot_height": (0.2, 3.0),
    "flicker_amp": (0.0, 0.6),
    "flicker_hz":  (0.5, 8.0),
    "flicker_lag": (0.0, 1.2),
    "tilt":        (-0.5, 0.5),
    "tilt_gust":   (0.0, 0.4),
    "rise_speed":  (0.3, 6.0),
    "deflect":     (-0.4, 0.4),
    "sec_amp":     (0.0, 1000.0),
    "sec_delay":   (0.0, 3.0),
    "sec_speed":   (0.0, 3.0),
    "sec_dur":     (0.1, 3.0),
    "floor":       (0.0, 120.0),
}
# a small step away from zero, for the tangent direction of a switched-off expansion
EPS = {k: 0.04 * (hi - lo) for k, (lo, hi) in RANGES.items()}

# A class whose term is gated by two parameters at once (flicker needs both an amplitude and a
# frequency) has an identically zero derivative at the origin and could never be diagnosed. So an
# off class is probed by a secant from off to a canonical on-state, plus one secant per parameter
# about that state. These are mid-range guesses declared in advance, not fits.
ON = {
    "soot":      {"soot_amp": 3.0, "soot_height": 1.0},
    "flicker":   {"flicker_amp": 0.15, "flicker_hz": 3.0, "flicker_lag": 0.2},
    "tilt":      {"tilt": 0.10, "tilt_gust": 0.10},
    "rise":      {"rise_speed": 1.5},
    "deflect":   {"deflect": 0.12},
    "secondary": {"sec_amp": 300.0, "sec_delay": 0.5, "sec_speed": 0.5, "sec_dur": 1.0},
    "floor":     {"floor": 30.0},
}

V0_PARAMS = ("amp", "height", "width", "spread")


# ---------------------------------------------------------------- a case
class FireCase:
    """One scene: the teacher's consumer outputs, and everything needed to score a cheap state."""

    def __init__(self, name, scene, stride=4, probe_n=(6, 4)):
        self.name = name
        self.p, self.burners, self.patches, self.obstacles = scene
        rec = TT.run(self.p, self.burners, self.patches, self.obstacles)
        keep = np.arange(0, len(rec.times), stride)
        self.times = rec.times[keep]
        self.F = len(keep)
        W = self.p.nx * self.p.dx
        H = self.p.ny * self.p.dx
        self.probes = np.array([[x, y]
                                for x in np.linspace(0.12 * W, 0.88 * W, probe_n[0])
                                for y in np.linspace(0.08 * H, 0.55 * H, probe_n[1])])
        sub = TT.FireRecord(rec.p, self.times, rec.T[keep], rec.soot[keep], rec.fuel[keep], rec.solid, rec.meta)
        self.target, self.scale, self.names = {}, {}, []
        for cname, g in (("visual", lambda r: TT.g_visual(r)),
                         ("heat",   lambda r: TT.g_heat(r, self.probes)),
                         ("ignition", lambda r: TT.g_ignition(r, self.patches)),
                         ("ai",     lambda r: TT.g_ai(r))):
            if cname == "ignition" and not self.patches:
                continue
            t = np.asarray(g(sub), float).reshape(self.F, -1)
            s = float(np.sqrt((t ** 2).mean()))
            if s <= 1e-9:
                continue
            self.target[cname] = t
            self.scale[cname] = s
            self.names.append(cname)
        self._cache = {}
        self.evals = 0

    # ---- the cheap side
    def _consumers(self, st: FireState):
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

    def residual(self, st: FireState):
        """(F, Ntot): each consumer block normalised by its scale and its width."""
        pred = self._consumers(st)
        parts = []
        for cname in self.names:
            n = self.target[cname].shape[1]
            w = self.scale[cname] * np.sqrt(n)
            parts.append((self.target[cname] - pred[cname]) / w)
        return np.concatenate(parts, axis=1)

    def error(self, st: FireState):
        r = self.residual(st)
        return float(np.sqrt((r ** 2).sum() / (self.F * len(self.names))))

    def per_consumer(self, st: FireState):
        pred = self._consumers(st)
        return {c: float(np.sqrt(((self.target[c] - pred[c]) ** 2).mean()) / self.scale[c])
                for c in self.names}

    def blocks(self):
        """(start, stop) column range of each consumer in the concatenated residual."""
        out, i = {}, 0
        for c in self.names:
            n = self.target[c].shape[1]
            out[c] = (i, i + n)
            i += n
        return out, i

    # ---- geometry for diagnosis
    def tangents(self, st: FireState):
        """Finite-difference direction of each parameter, grouped by class."""
        base = self.residual(st).ravel()
        signed = {}
        for cls, params in CLASSES.items():
            live = any(getattr(st, q) != 0.0 for q in params) or cls == "width"
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
        """Support masks over the concatenated columns, for the two classes that own a place."""
        blocks, ntot = self.blocks()
        out = {}
        W, H = self.p.nx * self.p.dx, self.p.ny * self.p.dx
        def cell_centres(cname):
            if cname == "visual":
                k = 4
            elif cname == "ai":
                k = 16
            else:
                return None
            ny, nx = self.p.ny // k, self.p.nx // k
            xs = (np.arange(nx) + 0.5) * k * self.p.dx
            ys = (np.arange(ny) + 0.5) * k * self.p.dx
            X, Y = np.meshgrid(xs, ys)
            return X.ravel(), Y.ravel()
        if self.obstacles:
            m = np.zeros(ntot)
            for cname in self.names:
                a, b = blocks[cname]
                cc = cell_centres(cname)
                if cc is not None:
                    X, Y = cc
                    for o in self.obstacles:
                        m[a:b] += ((np.abs(X - o.x) <= o.half_w + 0.28) &
                                   (np.abs(Y - o.y) <= o.half_h + 0.34)).astype(float)
                elif cname == "heat":
                    for o in self.obstacles:
                        m[a:b] += ((np.abs(self.probes[:, 0] - o.x) <= o.half_w + 0.28) &
                                   (np.abs(self.probes[:, 1] - o.y) <= o.half_h + 0.34)).astype(float)
            out["deflect"] = (m > 0).astype(float)
        if self.patches:
            m = np.zeros(ntot)
            for cname in self.names:
                a, b = blocks[cname]
                if cname == "ignition":
                    m[a:b] = 1.0
                    continue
                cc = cell_centres(cname)
                if cc is not None:
                    X, Y = cc
                    for q in self.patches:
                        m[a:b] += (np.hypot(X - q.x, Y - q.y) <= q.radius + 0.22).astype(float)
                elif cname == "heat":
                    for q in self.patches:
                        m[a:b] += (np.hypot(self.probes[:, 0] - q.x,
                                            self.probes[:, 1] - q.y) <= q.radius + 0.22).astype(float)
            out["secondary"] = (m > 0).astype(float)
        return out


# ---------------------------------------------------------------- repairs
def fit_class(case: FireCase, st: FireState, cls, grid=7):
    """Coordinate descent over the class's parameters: coarse sweep, then a refine around it.

    A class gated by more than one parameter (soot needs an amplitude and a height, flicker an
    amplitude and a frequency, secondary an amplitude and a duration) is unreachable from the
    all-zero state: the first parameter swept changes nothing or makes things worse, zero wins, and
    every later parameter is gated off. So an entirely-off class starts from the same canonical
    on-state its tangent direction uses. F2 found this the hard way.
    """
    cur = st
    if all(getattr(st, q) == 0.0 for q in CLASSES[cls]) and cls in ON:
        cur = replace(st, **ON[cls])
    for pname in CLASSES[cls]:
        lo, hi = RANGES[pname]
        vals = np.linspace(lo, hi, grid)
        errs = [case.error(replace(cur, **{pname: float(v)})) for v in vals]
        i = int(np.argmin(errs))
        cur = replace(cur, **{pname: float(vals[i])})
        step = (hi - lo) / (grid - 1)
        fine = np.linspace(max(lo, vals[i] - step), min(hi, vals[i] + step), grid)
        errs2 = [case.error(replace(cur, **{pname: float(v)})) for v in fine]
        cur = replace(cur, **{pname: float(fine[int(np.argmin(errs2))])})
    return cur, case.error(cur)


def repair_gain(case: FireCase, st: FireState, cls):
    """Error reduction per unit added cost for turning this class on and fitting it."""
    e0, c0 = case.error(st), st.cost()
    new, e1 = fit_class(case, st, cls)
    dc = max(new.cost() - c0, 1)
    return dict(cls=cls, state=new, e0=e0, e1=e1, gain=(e0 - e1) / dc, drop=e0 - e1, dcost=dc)


def joint_fit(case: FireCase, st: FireState, passes=2, grid=7):
    """Every parameter of every class at once, no greed and no selection: the vocabulary's floor.

    Off classes start from their canonical on-state for the same reason fit_class does.
    """
    cur = st
    for cls in CLASSES:
        if all(getattr(cur, q) == 0.0 for q in CLASSES[cls]) and cls in ON:
            cur = replace(cur, **ON[cls])
    order = [q for params in CLASSES.values() for q in params]
    for _ in range(passes):
        for pname in order:
            lo, hi = RANGES[pname]
            vals = np.linspace(lo, hi, grid)
            errs = [case.error(replace(cur, **{pname: float(v)})) for v in vals]
            i = int(np.argmin(errs))
            cur = replace(cur, **{pname: float(vals[i])})
            step = (hi - lo) / (grid - 1)
            fine = np.linspace(max(lo, vals[i] - step), min(hi, vals[i] + step), grid)
            errs2 = [case.error(replace(cur, **{pname: float(v)})) for v in fine]
            cur = replace(cur, **{pname: float(fine[int(np.argmin(errs2))])})
    return cur, case.error(cur)
