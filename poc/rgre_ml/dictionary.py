"""A structured student model: a dictionary of candidate modules, each a class with parameters.

This is the ML setting RGRE is honest about. Its selection rule projects the residual onto the
tangent directions of candidate modules, which only means something when a module has a direction
before it is fitted: basis functions, feature transforms, symbolic terms, fixed-feature experts.
For a randomly initialised neural block the tangent is arbitrary, so RGRE would reduce to "try
each one", which is the oracle. So the student here is a generalised additive model over a
dictionary, the setting where "structured matching pursuit in decision space with abstention" is
a claim rather than a rename.

Every module: a name, its parameters, a canonical on-state for gated ones (an amplitude of zero
gates the rest, exactly the fire's soot/flicker/secondary problem), a cost equal to its parameter
count, and a closed-form evaluation. Nothing here is fitted to any case.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

D = 4  # input dimension


@dataclass(frozen=True)
class Module:
    name: str
    params: tuple                  # parameter names
    lo: tuple                      # bounds
    hi: tuple
    on: tuple                      # canonical on-state (all-zero means the module is off)
    gated: bool                    # True if a zero amplitude makes every other parameter inert

    @property
    def cost(self):
        return len(self.params)


def _lin(name, i):
    return Module(name, (f"w{i}",), (-3.0,), (3.0,), (0.0,), False)


MODULES = {
    "linear": Module("linear", tuple(f"w{i}" for i in range(D)), (-3.0,) * D, (3.0,) * D, (0.0,) * D, False),
    "quad":   Module("quad",   tuple(f"b{i}" for i in range(D)), (-3.0,) * D, (3.0,) * D, (0.0,) * D, False),
    "pair":   Module("pair",   tuple(f"c{i}{j}" for i in range(D) for j in range(i + 1, D)),
                     (-3.0,) * 6, (3.0,) * 6, (0.0,) * 6, False),
    "cubic":  Module("cubic",  tuple(f"d{i}" for i in range(D)), (-2.0,) * D, (2.0,) * D, (0.0,) * D, False),
    "sin1":   Module("sin1",   ("A", "w", "phi"), (-3.0, 0.5, -3.2), (3.0, 6.0, 3.2), (0.6, 2.0, 0.0), True),
    "sin2":   Module("sin2",   ("A", "w", "phi"), (-3.0, 0.5, -3.2), (3.0, 6.0, 3.2), (0.6, 2.0, 0.0), True),
    "bump":   Module("bump",   ("A", "m0", "m1", "m2", "m3", "s"),
                     (-4.0, -1.0, -1.0, -1.0, -1.0, 0.15), (4.0, 1.0, 1.0, 1.0, 1.0, 1.0),
                     (1.0, 0.0, 0.0, 0.0, 0.0, 0.4), True),
    "step1":  Module("step1",  ("A", "k", "t"), (-3.0, 1.0, -1.0), (3.0, 12.0, 1.0), (0.8, 5.0, 0.0), True),
    "abs2":   Module("abs2",   ("A", "t"), (-3.0, -1.0), (3.0, 1.0), (0.8, 0.0), True),
    "exp3":   Module("exp3",   ("A", "beta"), (-2.0, -2.5), (2.0, 2.5), (0.4, 1.0), True),
}
CLASSES = tuple(MODULES)


def evaluate_module(name, theta, X):
    """One module's contribution at inputs X (n, D). theta is its parameter vector."""
    m = MODULES[name]
    th = np.asarray(theta, float)
    if name == "linear":
        return X @ th
    if name == "quad":
        return (X ** 2) @ th
    if name == "pair":
        cols = [X[:, i] * X[:, j] for i in range(D) for j in range(i + 1, D)]
        return np.stack(cols, 1) @ th
    if name == "cubic":
        return (X ** 3) @ th
    if name == "sin1":
        A, w, phi = th; return A * np.sin(w * X[:, 0] + phi)
    if name == "sin2":
        A, w, phi = th; return A * np.sin(w * X[:, 1] + phi)
    if name == "bump":
        A, s = th[0], max(th[5], 1e-3); mu = th[1:5]
        return A * np.exp(-((X - mu) ** 2).sum(1) / (2 * s * s))
    if name == "step1":
        A, k, t = th; return A / (1.0 + np.exp(-k * (X[:, 0] - t)))
    if name == "abs2":
        A, t = th; return A * np.abs(X[:, 1] - t)
    if name == "exp3":
        A, beta = th; return A * (np.exp(beta * X[:, 2]) - 1.0)
    raise KeyError(name)


@dataclass
class Student:
    """A GAM over the dictionary. `theta[name]` absent means the module is off."""
    theta: dict = field(default_factory=dict)

    def copy(self):
        return Student({k: np.array(v, float) for k, v in self.theta.items()})

    def active(self):
        return [c for c in CLASSES if c in self.theta and np.any(np.asarray(self.theta[c]) != 0.0)]

    def cost(self):
        return sum(MODULES[c].cost for c in self.active())

    def predict(self, X):
        y = np.zeros(len(X))
        for c, th in self.theta.items():
            if np.any(np.asarray(th) != 0.0):
                y += evaluate_module(c, th, X)
        return y

    def with_module(self, name, theta):
        s = self.copy(); s.theta[name] = np.array(theta, float); return s


# ---------------------------------------------------------------- out-of-vocabulary terms
def oov_term(kind, X, amp):
    """Structure the dictionary cannot express. These exist to test abstention."""
    if kind == "prodfreq":
        return amp * np.sin(3.0 * X[:, 0] * X[:, 1])
    if kind == "xor":
        return amp * np.tanh(3.0 * X[:, 0]) * np.tanh(3.0 * X[:, 1])
    if kind == "spiral":
        r = np.hypot(X[:, 0], X[:, 1]); a = np.arctan2(X[:, 1], X[:, 0])
        return amp * np.sin(2.0 * a + 4.0 * r)
    if kind == "ridge":
        return amp * np.exp(-8.0 * (X[:, 0] - X[:, 2]) ** 2)
    raise KeyError(kind)


OOV_KINDS = ("prodfreq", "xor", "spiral", "ridge")
