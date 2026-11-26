"""Intersection-theoretic form of the corner polynomials.

Mirzakhani: V_{g,n}(L) = int exp(2 pi^2 kappa_1 + sum L_i^2 psi_i / 2) over Mbar_{g,n}; the pi -> 0 part is the pure psi
(Kontsevich) volume V^top. Each pair term of F_{g,n} is an integral over the boundary divisor D_ij = Mbar_{0,3} x Mbar_{g,n-1}
with a node insertion G(L_i +- L_j; psi_node). Claim (top degree, pi -> 0, where the Bernoulli smoothing S = 2 pi D/sin 2 pi D
becomes the identity and G(0) ~ pi^{2k+4} vanishes):
    F^top_{g,n}(L) = sum_{i<j} sum_{+-} (1/4) int_0^{X} (X - s) s^2 V^top_{g,n-1}(s, L_rest) ds,   X = L_i +- L_j,
a tropical (metric ribbon graph) pants gluing: the cut curve has length s <= L_i +- L_j, weight (X - s) s^2 / 4.
In psi-class terms: [x^{2k}] V^top_{g,n-1} = <tau_k tau_rest>/(2^k k!), so the node insertion is
    (X^4/4) int_0^1 (1 - u) u^2 exp(u^2 X^2 psi/2) du.
"""
import sys, itertools
import sympy as sp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from higher_volumes import V, P, pants_corner_sum


def top(expr):
    return sp.expand(expr.subs(P, 0))


if __name__ == "__main__":
    s = sp.symbols("s")
    for (g, n) in ((0, 4), (0, 5), (0, 6), (1, 2), (1, 3), (2, 2), (0, 7)):
        L = sp.symbols(f"L1:{n + 1}")
        Ftop = top(pants_corner_sum(g, n)[0])
        Vm = sp.expand(V(g, n - 1)); names = sp.symbols(f"L1:{n}"); rhs = 0
        for i, j in itertools.combinations(range(n), 2):
            rest = [L[k] for k in range(n) if k not in (i, j)]
            Vs = top(Vm.subs(dict(zip(names, (s,) + tuple(rest))), simultaneous=True))
            for X in (L[i] + L[j], L[i] - L[j]):
                rhs += sp.Rational(1, 4) * sp.integrate((X - s) * s**2 * Vs, (s, 0, X))
        print(f"({g},{n}): F^top - tropical pants gluing = {sp.simplify(sp.expand(Ftop - rhs))}", flush=True)
