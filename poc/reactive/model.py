"""A cheap model = additive composition of primitives + optional saturation."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .geometry import Geometry
from .primitives import GRAMMAR, Param, Primitive, Saturate


@dataclass
class Term:
    prim: Primitive
    params: dict[str, float]


@dataclass
class CheapModel:
    terms: list[Term] = field(default_factory=list)
    saturate: dict[str, float] | None = None

    # ---- parameter vector plumbing (unconstrained z <-> bounded x) ----
    def param_specs(self) -> list[tuple[int, Param]]:
        specs = []
        for i, t in enumerate(self.terms):
            for p in t.prim.params:
                specs.append((i, p))
        if self.saturate is not None:
            for p in Saturate.params:
                specs.append((-1, p))
        return specs

    def get_vector(self) -> np.ndarray:
        z = []
        for i, p in self.param_specs():
            x = self.saturate[p.name] if i < 0 else self.terms[i].params[p.name]
            z.append(_to_z(x, p))
        return np.array(z)

    def set_vector(self, z: np.ndarray) -> None:
        for (i, p), zi in zip(self.param_specs(), z):
            x = _from_z(zi, p)
            if i < 0:
                self.saturate[p.name] = x
            else:
                self.terms[i].params[p.name] = x

    # ---- evaluation ----
    def evaluate(self, g: Geometry, times: np.ndarray) -> tuple[np.ndarray, float]:
        """Return (bend (F,N,2), cost in ops per stalk per frame)."""
        b = np.zeros((len(times), g.n, 2))
        cost = 0.0
        for t in self.terms:
            bt, live = t.prim.evaluate(g, times, t.params)
            b += bt
            cost += t.prim.cost * live
        if self.saturate is not None:
            b = Saturate().apply(b, self.saturate)
            cost += Saturate.cost
        return b, cost

    def copy(self) -> "CheapModel":
        return CheapModel(
            [Term(t.prim, dict(t.params)) for t in self.terms],
            None if self.saturate is None else dict(self.saturate),
        )

    def describe(self) -> str:
        lines = []
        for t in self.terms:
            ps = ", ".join(f"{k}={v:.3g}" for k, v in t.params.items())
            lines.append(f"  {t.prim.name}({ps})")
        if self.saturate is not None:
            lines.append(f"  saturate(b_max={self.saturate['b_max']:.3g})")
        return "\n".join(lines) if lines else "  (empty)"

    @property
    def names(self) -> list[str]:
        n = [t.prim.name for t in self.terms]
        if self.saturate is not None:
            n.append("saturate")
        return n


def make_term(name: str) -> Term:
    cls = GRAMMAR[name]
    return Term(cls(), {p.name: p.init for p in cls.params})


def _to_z(x: float, p: Param) -> float:
    u = np.clip((x - p.lo) / (p.hi - p.lo), 1e-4, 1 - 1e-4)
    return float(np.log(u / (1 - u)))


def _from_z(z: float, p: Param) -> float:
    u = 1.0 / (1.0 + np.exp(-z))
    return float(p.lo + (p.hi - p.lo) * u)
