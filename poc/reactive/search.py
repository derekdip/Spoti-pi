"""Greedy compositional search: a small stand-in for the ECS search.

Forward selection over the grammar: try adding each primitive (parameters
optimised with Powell in a bounded, unconstrained reparameterisation),
keep the addition that most reduces J, repeat until nothing helps.

J = E_all + w_late * E_late + lambda_cost * cost / 100
where E_* are relative RMS errors on a fit subset (frames x stalks).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from .geometry import Geometry
from .metrics import rel_rmse
from .model import CheapModel, make_term
from .primitives import GRAMMAR


@dataclass
class Objective:
    geom: Geometry
    times: np.ndarray
    ref: np.ndarray  # (F, N, 2)
    late_mask: np.ndarray  # (F,) bool
    w_late: float = 0.5
    lambda_cost: float = 0.01

    def __call__(self, model: CheapModel) -> tuple[float, dict]:
        pred, cost = model.evaluate(self.geom, self.times)
        e_all = rel_rmse(pred, self.ref)
        e_late = rel_rmse(pred[self.late_mask], self.ref[self.late_mask])
        j = e_all + self.w_late * e_late + self.lambda_cost * cost / 100.0
        return j, {"E_all": e_all, "E_late": e_late, "cost": cost}


def optimise(model: CheapModel, obj: Objective, maxfev: int = 600, mask: np.ndarray | None = None) -> float:
    """Powell over the (masked) unconstrained parameter vector. Returns final J."""
    z_full = model.get_vector()
    if z_full.size == 0:
        return obj(model)[0]
    idx = np.arange(z_full.size) if mask is None else np.flatnonzero(mask)
    if idx.size == 0:
        return obj(model)[0]

    def f(z):
        zz = z_full.copy()
        zz[idx] = z
        model.set_vector(zz)
        return obj(model)[0]

    res = minimize(f, z_full[idx], method="Powell", options={"maxfev": maxfev, "xtol": 1e-3, "ftol": 1e-5})
    z_full[idx] = res.x
    model.set_vector(z_full)
    return float(res.fun)


def optimise_new_then_all(model: CheapModel, obj: Objective, n_new: int, maxfev_new: int = 600,
                          maxfev_all: int = 300) -> float:
    """Fit only the last `n_new` parameters first, then briefly polish everything jointly."""
    n = model.get_vector().size
    mask = np.zeros(n, dtype=bool)
    mask[n - n_new:] = True
    optimise(model, obj, maxfev_new, mask)
    return optimise(model, obj, maxfev_all)


def greedy_search(obj: Objective, candidates: list[str] | None = None, max_terms: int = 6,
                  allow_saturate: bool = True, log=print) -> tuple[CheapModel, list[dict]]:
    candidates = candidates or list(GRAMMAR)
    model = CheapModel()
    best_j, _ = obj(model)
    history = [{"terms": [], "J": best_j, **obj(model)[1]}]
    log(f"start: J={best_j:.4f}")
    while len(model.terms) < max_terms:
        trials = []
        for name in candidates:
            if name in model.names:
                continue
            trial = model.copy()
            trial.terms.append(make_term(name))
            j = optimise_new_then_all(trial, obj, len(trial.terms[-1].prim.params))
            trials.append((j, name, trial))
            log(f"  try +{name:15s} J={j:.4f}")
        if allow_saturate and model.saturate is None and model.terms:
            trial = model.copy()
            trial.saturate = {"b_max": 0.6}
            j = optimise_new_then_all(trial, obj, 1)
            trials.append((j, "saturate", trial))
            log(f"  try +{'saturate':15s} J={j:.4f}")
        if not trials:
            break
        j, name, trial = min(trials, key=lambda x: x[0])
        if j >= best_j - 1e-4:
            log("no candidate improves J; stopping")
            break
        model, best_j = trial, j
        _, parts = obj(model)
        history.append({"terms": list(model.names), "J": best_j, **parts})
        log(f"accept +{name}: J={best_j:.4f} E_all={parts['E_all']:.3f} E_late={parts['E_late']:.3f} cost={parts['cost']:.0f}")
    return model, history
