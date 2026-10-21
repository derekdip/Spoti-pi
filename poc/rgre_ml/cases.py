"""Cases: a teacher function, a student missing part of it, and the consumers that read it.

A case is what RGRE-1 called a case: one teacher, one student with a known defect, and the
question "which module should be added next". Ground truth is the module the teacher has and the
student does not. The consumers are the ML analogue of the fire's: the raw prediction, a binary
decision at a threshold, and a coarse regional average, each normalised by its own scale so the
residual RGRE sees is in decision space rather than in the field.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import least_squares

from .dictionary import MODULES, CLASSES, D, Student, evaluate_module, oov_term, OOV_KINDS

N_SAMPLES = 512
GRID = 6            # coarse consumer: GRID x GRID cells over (x0, x1)
NOISE = 0.02        # observation noise on the teacher, relative to its rms


def sample_inputs(rng, n=N_SAMPLES):
    return rng.uniform(-1.0, 1.0, size=(n, D))


def random_theta(rng, name, scale=1.0):
    """A random on-state for a module: draw within bounds, ensure gated amplitude is not tiny."""
    m = MODULES[name]
    lo, hi = np.array(m.lo), np.array(m.hi)
    th = rng.uniform(lo, hi) * scale
    if m.gated:
        a = rng.uniform(0.6, 1.8) * (1 if rng.random() < 0.5 else -1)
        th[0] = a
    else:
        th = rng.normal(0, 0.8, size=len(th))
    return np.clip(th, lo, hi)


@dataclass
class Case:
    name: str
    kind: str                       # "isolated", "two", "oov", "control"
    X: np.ndarray
    y: np.ndarray                   # teacher output
    student0: Student
    missing: tuple                  # ground-truth modules the student lacks
    oov: str | None
    thresh: float

    # ---- consumers
    def consumers(self, pred):
        c_value = pred
        c_decide = (pred > self.thresh).astype(float)
        c_coarse = coarse(self.X, pred)
        return {"value": c_value, "decide": c_decide, "coarse": c_coarse}

    def targets(self):
        if not hasattr(self, "_t"):
            self._t = self.consumers(self.y)
            self._scale = {k: float(np.sqrt((v ** 2).mean())) or 1.0 for k, v in self._t.items()}
        return self._t, self._scale

    def residual(self, s: Student):
        """(1, Ntot): every consumer normalised by its scale and its width, as the fire did."""
        t, sc = self.targets()
        p = self.consumers(s.predict(self.X))
        parts = [(t[k] - p[k]) / (sc[k] * np.sqrt(len(t[k]))) for k in t]
        return np.concatenate(parts)[None, :]

    def error(self, s: Student):
        r = self.residual(s)
        return float(np.sqrt((r ** 2).sum() / 3))

    def per_consumer(self, s: Student):
        t, sc = self.targets()
        p = self.consumers(s.predict(self.X))
        return {k: float(np.sqrt(((t[k] - p[k]) ** 2).mean()) / sc[k]) for k in t}

    def blocks(self):
        t, _ = self.targets()
        out, i = {}, 0
        for k in t:
            out[k] = (i, i + len(t[k])); i += len(t[k])
        return out, i


def coarse(X, v):
    """Mean of v over a GRID x GRID partition of (x0, x1)."""
    ix = np.clip(((X[:, 0] + 1) / 2 * GRID).astype(int), 0, GRID - 1)
    iy = np.clip(((X[:, 1] + 1) / 2 * GRID).astype(int), 0, GRID - 1)
    cell = iy * GRID + ix
    out = np.zeros(GRID * GRID); cnt = np.zeros(GRID * GRID)
    np.add.at(out, cell, v); np.add.at(cnt, cell, 1)
    return out / np.maximum(cnt, 1)


# ---------------------------------------------------------------- tangents and repairs
EPS = {c: 0.04 * (np.array(MODULES[c].hi) - np.array(MODULES[c].lo)) for c in CLASSES}


def tangents(case: Case, s: Student):
    """Finite-difference direction of each parameter, grouped by class; off gated classes probed
    by a secant from their on-state, exactly as the fire's tangents() does."""
    base = case.residual(s).ravel()
    signed = {}
    for c in CLASSES:
        m = MODULES[c]
        cur = np.array(s.theta.get(c, np.zeros(len(m.params))), float)
        live = np.any(cur != 0.0) or not m.gated
        vs = []
        if live:
            for i in range(len(m.params)):
                h = EPS[c][i]
                nxt = cur.copy(); nxt[i] = cur[i] + h if cur[i] + h <= m.hi[i] else cur[i] - h
                d = (case.residual(s.with_module(c, nxt)).ravel() - base) / (nxt[i] - cur[i])
                if d @ d > 0: vs.append(d)
        else:
            on = np.array(m.on, float)
            r_on = case.residual(s.with_module(c, on)).ravel()
            d = r_on - base
            if d @ d > 0: vs.append(d)
            for i in range(len(m.params)):
                h = EPS[c][i]
                nxt = on.copy(); nxt[i] = on[i] + h if on[i] + h <= m.hi[i] else on[i] - h
                dd = case.residual(s.with_module(c, nxt)).ravel() - r_on
                if dd @ dd > 0: vs.append(dd)
        if vs:
            signed[c] = vs
    return signed


def fit_module(case: Case, s: Student, c: str):
    """Fit one module's parameters to the consumer residual, everything else fixed.

    Starts from the on-state when the module is off, for the reason F2 found the hard way: a gated
    module started at zero has a zero gradient in every other parameter.
    """
    m = MODULES[c]
    cur = np.array(s.theta.get(c, np.zeros(len(m.params))), float)
    if m.gated and not np.any(cur != 0.0):
        cur = np.array(m.on, float)
    lo, hi = np.array(m.lo), np.array(m.hi)
    x0 = np.clip(cur, lo + 1e-6, hi - 1e-6)

    def res(th):
        return case.residual(s.with_module(c, th)).ravel()

    r = least_squares(res, x0, bounds=(lo, hi), max_nfev=60 * len(x0), xtol=1e-6, ftol=1e-6)
    new = s.with_module(c, r.x)
    return new, case.error(new)


# ---------------------------------------------------------------- building cases
def make_teacher(rng, present, oov=None, oov_amp=1.0):
    theta = {c: random_theta(rng, c) for c in present}
    def f(X):
        y = np.zeros(len(X))
        for c, th in theta.items():
            y += evaluate_module(c, th, X)
        if oov is not None:
            y += oov_term(oov, X, oov_amp)
        return y
    return theta, f


def build_cases(seed, n_iso=18, n_two=8, n_oov=8, n_ctrl=4, n_mixed=0, log=print):
    """Fresh cases from one seed. Nothing about them is looked at before the freeze."""
    rng = np.random.default_rng(seed)
    cases = []
    others = [c for c in CLASSES if c != "linear"]

    def finish(name, kind, present, hidden, oov=None, oov_amp=1.0):
        X = sample_inputs(rng)
        theta, f = make_teacher(rng, present, oov, oov_amp)
        y = f(X); y = y + NOISE * float(np.sqrt((y ** 2).mean()) or 1) * rng.normal(size=len(y))
        # the student has every module the teacher has except the hidden ones, at the teacher's values
        s0 = Student({c: theta[c] for c in present if c not in hidden})
        thresh = float(np.median(y))
        return Case(name, kind, X, y, s0, tuple(hidden), oov, thresh)

    # isolated: student has linear + one or two known modules; one module missing
    for k in range(n_iso):
        missing = rng.choice(others)
        known = [c for c in rng.choice([c for c in others if c != missing], size=rng.integers(1, 3), replace=False)]
        cases.append(finish(f"iso_{missing}_{k}", "isolated", ["linear"] + known + [missing], [missing]))
    # two missing: the mixture analogue
    for k in range(n_two):
        miss = list(rng.choice(others, size=2, replace=False))
        known = [c for c in rng.choice([c for c in others if c not in miss], size=1, replace=False)]
        cases.append(finish(f"two_{miss[0]}_{miss[1]}_{k}", "two", ["linear"] + known + miss, miss))
    # out of vocabulary: student has everything the teacher has; the residual is a term no module makes
    for k in range(n_oov):
        kind = OOV_KINDS[k % len(OOV_KINDS)]
        known = [c for c in rng.choice(others, size=2, replace=False)]
        cases.append(finish(f"oov_{kind}_{k}", "oov", ["linear"] + known, [], oov=kind, oov_amp=float(rng.uniform(0.8, 1.6))))
    # control: nothing missing, only noise; RGRE should find nothing worth doing
    for k in range(n_ctrl):
        known = [c for c in rng.choice(others, size=2, replace=False)]
        cases.append(finish(f"ctrl_{k}", "control", ["linear"] + known, []))
    # mixed: one module missing AND one term the dictionary cannot make. This is the case the
    # deferral claim needs: growth can fix the first and cannot touch the second, so a deferral
    # rule that ranks by "unexplainable" should send the teacher the second and not the first.
    for k in range(n_mixed):
        missing = rng.choice(others)
        kind = OOV_KINDS[k % len(OOV_KINDS)]
        known = [c for c in rng.choice([c for c in others if c != missing], size=1, replace=False)]
        cases.append(finish(f"mixed_{missing}_{kind}_{k}", "mixed", ["linear"] + known + [missing], [missing],
                            oov=kind, oov_amp=float(rng.uniform(0.8, 1.6))))
    log(f"built {len(cases)} cases from seed {seed}: {n_iso} isolated, {n_two} two-missing, {n_oov} oov, {n_ctrl} control, {n_mixed} mixed")
    return cases
