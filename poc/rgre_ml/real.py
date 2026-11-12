"""RGRE-ML-2: the real-data case. Six tabular regression datasets, a per-feature dictionary, one consumer.

The student is an intercept plus a linear term plus any modules grown from a dictionary defined
per feature and per pair of features: a square, a cube, a sinusoid, a sigmoid step, an absolute
value and an exponential of each feature, and a product and a two-dimensional Gaussian bump of
each pair. Every module has bounds, a cost equal to its parameter count and, for gated modules,
a canonical on-state, as the synthetic dictionary did. Features are z-scored on the training
split and divided by three so that three standard deviations map to one, the range the module
bounds were written for; the target is z-scored on the training split so errors are in units of
its standard deviation on every dataset.

One consumer, the prediction. RGRE-ML-1 and the fire cross-check settled the diagnosis-space
question, so the residual here is the field residual throughout.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

DATA = Path(__file__).resolve().parent / "data"
DATASETS = ("diabetes", "mpg", "concrete", "winered", "abalone", "california")
TEST_FRAC = 0.3
XSCALE = 3.0


# ---------------------------------------------------------------- data
def load(name):
    with open(DATA / f"{name}.csv") as f:
        rows = list(csv.reader(f))
    A = np.array(rows[1:], float)
    return A[:, :-1], A[:, -1], rows[0][:-1]


def split(name, seed):
    """A seeded 70/30 split, standardised on the training part only."""
    X, y, feats = load(name)
    rng = np.random.default_rng(1000 * seed + 17)
    idx = rng.permutation(len(X))
    n_te = int(round(TEST_FRAC * len(X)))
    te, tr = idx[:n_te], idx[n_te:]
    mu, sd = X[tr].mean(0), X[tr].std(0)
    sd[sd == 0] = 1.0
    ym, ys = y[tr].mean(), y[tr].std()
    Xs = (X - mu) / sd / XSCALE
    yz = (y - ym) / ys
    return Xs[tr], yz[tr], Xs[te], yz[te], feats


# ---------------------------------------------------------------- dictionary
@dataclass(frozen=True)
class RModule:
    name: str
    kind: str
    feats: tuple
    params: tuple
    lo: tuple
    hi: tuple
    on: tuple
    gated: bool

    @property
    def cost(self):
        return len(self.params)


def build_dictionary(d):
    mods = {}
    for j in range(d):
        mods[f"quad_{j}"] = RModule(f"quad_{j}", "quad", (j,), ("b",), (-3.0,), (3.0,), (0.0,), False)
        mods[f"cubic_{j}"] = RModule(f"cubic_{j}", "cubic", (j,), ("d",), (-2.0,), (2.0,), (0.0,), False)
        mods[f"sin_{j}"] = RModule(f"sin_{j}", "sin", (j,), ("A", "w", "phi"), (-3.0, 0.5, -3.2), (3.0, 6.0, 3.2), (0.6, 2.0, 0.0), True)
        mods[f"step_{j}"] = RModule(f"step_{j}", "step", (j,), ("A", "k", "t"), (-3.0, 1.0, -1.0), (3.0, 12.0, 1.0), (0.8, 5.0, 0.0), True)
        mods[f"abs_{j}"] = RModule(f"abs_{j}", "abs", (j,), ("A", "t"), (-3.0, -1.0), (3.0, 1.0), (0.8, 0.0), True)
        mods[f"exp_{j}"] = RModule(f"exp_{j}", "exp", (j,), ("A", "beta"), (-2.0, -2.5), (2.0, 2.5), (0.4, 1.0), True)
    for j in range(d):
        for k in range(j + 1, d):
            mods[f"pair_{j}_{k}"] = RModule(f"pair_{j}_{k}", "pair", (j, k), ("c",), (-3.0,), (3.0,), (0.0,), False)
            mods[f"bump_{j}_{k}"] = RModule(f"bump_{j}_{k}", "bump", (j, k), ("A", "mj", "mk", "s"),
                                            (-4.0, -1.0, -1.0, 0.15), (4.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 0.4), True)
    return mods


def evaluate(m: RModule, th, X):
    th = np.asarray(th, float)
    x = X[:, m.feats[0]]
    if m.kind == "quad":
        return th[0] * x * x
    if m.kind == "cubic":
        return th[0] * x * x * x
    if m.kind == "pair":
        return th[0] * x * X[:, m.feats[1]]
    if m.kind == "sin":
        return th[0] * np.sin(th[1] * x + th[2])
    if m.kind == "step":
        return th[0] / (1.0 + np.exp(-th[1] * (x - th[2])))
    if m.kind == "abs":
        return th[0] * np.abs(x - th[1])
    if m.kind == "exp":
        return th[0] * (np.exp(np.clip(th[1] * x, -20, 20)) - 1.0)
    if m.kind == "bump":
        xk = X[:, m.feats[1]]
        s = max(float(th[3]), 1e-3)
        return th[0] * np.exp(-((x - th[1]) ** 2 + (xk - th[2]) ** 2) / (2 * s * s))
    raise KeyError(m.kind)


def anchors(m: RModule):
    """Fixed on-states for the anchored-tangent variant: the canonical one plus shifts of the shape
    parameter a projection cannot see from a single point (frequency, threshold, rate, centre)."""
    on = np.array(m.on, float)
    out = [on]
    if m.kind == "sin":
        for w in (1.0, 4.0):
            a = on.copy(); a[1] = w; out.append(a)
    elif m.kind == "step":
        for t in (-0.5, 0.5):
            a = on.copy(); a[2] = t; out.append(a)
    elif m.kind == "abs":
        for t in (-0.5, 0.5):
            a = on.copy(); a[1] = t; out.append(a)
    elif m.kind == "exp":
        a = on.copy(); a[1] = -1.5; out.append(a)
    elif m.kind == "bump":
        for mj, mk in ((-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)):
            a = on.copy(); a[1] = mj; a[2] = mk; out.append(a)
    return out


def basis(m: RModule, X):
    """The direction of a one-parameter linear module: its contribution at unit coefficient."""
    return evaluate(m, (1.0,), X)


@dataclass
class RStudent:
    b0: float
    w: np.ndarray
    theta: dict = field(default_factory=dict)      # module name -> parameter vector
    order: list = field(default_factory=list)      # modules in the order they were added

    def copy(self):
        return RStudent(self.b0, self.w.copy(), {k: v.copy() for k, v in self.theta.items()}, list(self.order))

    def predict(self, X, mods):
        y = self.b0 + X @ self.w
        for name, th in self.theta.items():
            y = y + evaluate(mods[name], th, X)
        return y

    def with_module(self, name, th):
        s = self.copy()
        if name not in s.theta:
            s.order.append(name)
        s.theta[name] = np.asarray(th, float).copy()
        return s

    def cost(self, mods):
        return sum(mods[n].cost for n in self.theta)


# ---------------------------------------------------------------- the case
class RCase:
    def __init__(self, name, seed):
        self.name, self.seed = name, seed
        self.Xtr, self.ytr, self.Xte, self.yte, self.feats = split(name, seed)
        self.n, self.d = self.Xtr.shape
        self.mods = build_dictionary(self.d)
        self.eps = {k: 0.04 * (np.array(m.hi) - np.array(m.lo)) for k, m in self.mods.items()}

    # ---- students and errors
    def student0(self, y=None):
        y = self.ytr if y is None else y
        A = np.column_stack([np.ones(self.n), self.Xtr])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        return RStudent(float(coef[0]), coef[1:].copy())

    def predict(self, s, X):
        return s.predict(X, self.mods)

    def error(self, s, y=None):
        y = self.ytr if y is None else y
        return float(np.sqrt(np.mean((y - self.predict(s, self.Xtr)) ** 2)))

    def test_error(self, s, yte=None):
        yte = self.yte if yte is None else yte
        return float(np.sqrt(np.mean((yte - self.predict(s, self.Xte)) ** 2)))

    def residual(self, s, y=None):
        """(1, n) training residual scaled so that its squared norm is the mean squared error."""
        y = self.ytr if y is None else y
        return ((y - self.predict(s, self.Xtr)) / np.sqrt(self.n))[None, :]

    def candidates(self, s):
        return [k for k in self.mods if k not in s.theta]

    # ---- tangents: the direction each candidate parameter moves the residual, before any fit
    def tangents(self, s, anchored=False):
        """One canonical on-state per gated module, as RGRE-ML-1 froze it. With `anchored`, the
        declared variant: secants at several fixed on-states per gated module, so a module whose
        shape must be fitted has more than one direction to be recognised by."""
        X = self.Xtr
        signed = {}
        for k in self.candidates(s):
            m = self.mods[k]
            vs = []
            if not m.gated:
                vs.append(-basis(m, X) / np.sqrt(self.n))
            else:
                for on in (anchors(m) if anchored else [np.array(m.on, float)]):
                    c_on = evaluate(m, on, X)
                    vs.append(-c_on / np.sqrt(self.n))
                    for i in range(len(m.params)):
                        h = self.eps[k][i]
                        nxt = on.copy()
                        nxt[i] = on[i] + h if on[i] + h <= m.hi[i] else on[i] - h
                        vs.append(-(evaluate(m, nxt, X) - c_on) / np.sqrt(self.n))
            vs = [v for v in vs if float(v @ v) > 0]
            if vs:
                signed[k] = vs
        return signed

    # ---- one repair: fit one module to the residual, everything else fixed
    def fit_module(self, s, k, y=None):
        y = self.ytr if y is None else y
        m = self.mods[k]
        r0 = y - self.predict(s, self.Xtr)
        lo, hi = np.array(m.lo), np.array(m.hi)
        if not m.gated:
            f = basis(m, self.Xtr)
            ff = float(f @ f)
            th = np.array([float(r0 @ f) / ff if ff > 0 else 0.0])
            th = np.clip(th, lo, hi)
        else:
            x0 = np.clip(np.array(m.on, float), lo + 1e-6, hi - 1e-6)
            res = least_squares(lambda t: r0 - evaluate(m, t, self.Xtr), x0, bounds=(lo, hi),
                                max_nfev=60 * len(x0), xtol=1e-6, ftol=1e-6)
            th = res.x
        new = s.with_module(k, th)
        return new, self.error(new, y)

    def oracle_table(self, s, y=None):
        """Every candidate fitted once from the current state: raw training-error drop, and the
        held-out error of each fitted state (context, never used to pick)."""
        y = self.ytr if y is None else y
        e0 = self.error(s, y)
        out = {}
        for k in self.candidates(s):
            new, e1 = self.fit_module(s, k, y)
            out[k] = dict(state=new, e1=e1, drop=e0 - e1, test=self.test_error(new))
        return e0, out


# ---------------------------------------------------------------- regions and a reference model
def kmeans(X, K, seed, iters=30):
    """Plain k-means with k-means++ seeding; returns centroids."""
    rng = np.random.default_rng(seed)
    n = len(X)
    C = [X[rng.integers(n)]]
    for _ in range(1, K):
        d2 = np.min(((X[:, None, :] - np.array(C)[None, :, :]) ** 2).sum(2), axis=1)
        p = d2 / d2.sum() if d2.sum() > 0 else np.full(n, 1.0 / n)
        C.append(X[rng.choice(n, p=p)])
    C = np.array(C)
    for _ in range(iters):
        lab = assign(X, C)
        for k in range(K):
            if np.any(lab == k):
                C[k] = X[lab == k].mean(0)
    return C


def assign(X, C):
    return np.argmin(((X[:, None, :] - C[None, :, :]) ** 2).sum(2), axis=1)


def knn_predict(Xtr, ytr, Xte, k=10):
    out = np.empty(len(Xte))
    for i in range(0, len(Xte), 256):
        blk = Xte[i:i + 256]
        d2 = ((blk[:, None, :] - Xtr[None, :, :]) ** 2).sum(2)
        nn = np.argpartition(d2, k, axis=1)[:, :k]
        out[i:i + 256] = ytr[nn].mean(1)
    return out
