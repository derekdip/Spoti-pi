"""Does the product-law structure extend beyond complexity one?

Pants-corner sum on S_{g,n} (n >= 2 boundaries): for each pair {i, j}, sum over the curves gamma that cut off a pair of
pants containing boundaries i, j of (l_gamma/2) log P(l_gamma; L_i, L_j) (P = cosh^2(d/2), d the pants' return
orthogeodesic). For S_{0,4} this is exactly the dual area. Mirzakhani unfolding (cut surface S_{0,3} + S_{g,n-1}):
    F_{g,n}(L) = sum_{i<j} int_0^inf (x^2/2) log P(x; L_i, L_j) V_{g,n-1}(x, L_rest) dx,
and int_0^inf x^{2k+2} (1/2) log P(x; A, B) dx = 2^{2k+2} [K_{2k+1}((A+B)/2) + K_{2k+1}((A-B)/2)]   (moment_polys.K_sphere).
Volumes V_{g,n} from Mirzakhani's recursion (Mulase-Safnuk form) with the kernel moments
    F_{2k+1}(t) = int_0^inf x^{2k+1} H(x, t) dx = (2k+1)! sum_{i=0}^{k+1} zeta(2i) (2^{2i+1} - 4) t^{2k+2-2i}/(2k+2-2i)!,  zeta(0) = -1/2.
"""
import sympy as sp, itertools, functools, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from moment_polys import K_sphere, P

PI = P
def zeta_even(n):
    if n == 0: return sp.Rational(-1, 2)
    return sp.Rational(abs(sp.bernoulli(n)) * 2**(n - 1), sp.factorial(n)) * PI**n


def Fk(k, t):   # int x^{2k+1} H(x, t) dx
    return sp.factorial(2 * k + 1) * sum(zeta_even(2 * i) * (2**(2 * i + 1) - 4) * t**(2 * k + 2 - 2 * i) / sp.factorial(2 * k + 2 - 2 * i) for i in range(k + 2))


def coeffs_in(var, poly):
    """poly in var^2: {k: coefficient of var^{2k}}"""
    p = sp.Poly(sp.expand(poly), var); out = {}
    for (d,), c in p.terms():
        assert d % 2 == 0; out[d // 2] = c
    return out


@functools.lru_cache(None)
def V(g, n):
    """V_{g,n}(L1..Ln) as an expression in symbols L1..Ln and pi."""
    L = sp.symbols(f"L1:{n + 1}")
    if (g, n) == (0, 3): return sp.Integer(1)
    if (g, n) == (1, 1): return (L[0]**2 + 4 * PI**2) / 48
    x, y = sp.symbols("x y"); L1 = L[0]; rhs = 0
    def sub(expr, names, vals): return expr.subs(dict(zip(names, vals)), simultaneous=True)
    # connected A: V_{g-1, n+1}(x, y, L2..Ln)
    if g >= 1:
        Vc = V(g - 1, n + 1); names = sp.symbols(f"L1:{n + 2}")
        Vc = sub(Vc, names, (x, y) + tuple(L[1:]))
        for (a, b), c in sp.Poly(sp.expand(Vc), x, y).terms():
            rhs += sp.Rational(1, 2) * c * sp.factorial(a + 1) * sp.factorial(b + 1) / sp.factorial(a + b + 3) * Fk((a + b + 2) // 2, L1)
    # disconnected A: V_{g1, |I|+1}(x, L_I) V_{g2, |J|+1}(y, L_J), I + J = {2..n}
    others = list(range(1, n))
    for g1 in range(0, g + 1):
        g2 = g - g1
        for r in range(0, len(others) + 1):
            for I in itertools.combinations(others, r):
                J = [j for j in others if j not in I]
                if (g1, len(I) + 1) in ((0, 1), (0, 2)) or (g2, len(J) + 1) in ((0, 1), (0, 2)): continue
                V1 = sub(V(g1, len(I) + 1), sp.symbols(f"L1:{len(I) + 2}"), (x,) + tuple(L[i] for i in I))
                V2 = sub(V(g2, len(J) + 1), sp.symbols(f"L1:{len(J) + 2}"), (y,) + tuple(L[j] for j in J))
                prod = sp.expand(V1 * V2)
                for (a, b), c in sp.Poly(prod, x, y).terms():
                    rhs += sp.Rational(1, 2) * c * sp.factorial(a + 1) * sp.factorial(b + 1) / sp.factorial(a + b + 3) * Fk((a + b + 2) // 2, L1)
    # B: sum_j int x [H(x, L1 + Lj) + H(x, L1 - Lj)] V_{g, n-1}(x, L without 1, j) dx
    for j in range(1, n):
        if (g, n - 1) in ((0, 2), (0, 1)): continue
        rest = [L[i] for i in range(1, n) if i != j]
        Vb = sub(V(g, n - 1), sp.symbols(f"L1:{n}"), (x,) + tuple(rest))
        for k, c in coeffs_in(x, Vb).items():
            rhs += sp.Rational(1, 2) * c * (Fk(k, L1 + L[j]) + Fk(k, L1 - L[j]))
    # d/dL1 (L1 V) = rhs  ->  V = (1/L1) int_0^L1 rhs
    t = sp.symbols("t"); integ = sp.integrate(sp.expand(rhs.subs(L1, t)), (t, 0, L1))
    return sp.factor(sp.expand(sp.cancel(integ / L1)))


def pants_corner_sum(g, n):
    L = sp.symbols(f"L1:{n + 1}"); x = sp.symbols("x"); tot = 0
    Vr = V(g, n - 1)
    for i, j in itertools.combinations(range(n), 2):
        rest = [L[k] for k in range(n) if k not in (i, j)]
        Vx = Vr.subs(dict(zip(sp.symbols(f"L1:{n}"), (x,) + tuple(rest))), simultaneous=True) if not (g == 0 and n - 1 == 3 and False) else Vr
        for k, c in coeffs_in(x, Vx).items():
            tot += c * 2**(2 * k + 2) * (K_sphere(2 * k + 1, (L[i] + L[j]) / 2) + K_sphere(2 * k + 1, (L[i] - L[j]) / 2))
    return sp.expand(tot), L


if __name__ == "__main__":
    known = {(0, 4): lambda L: (4 * PI**2 + sum(l**2 for l in L)) / 2,
             (1, 2): lambda L: (4 * PI**2 + L[0]**2 + L[1]**2) * (12 * PI**2 + L[0]**2 + L[1]**2) / 192,
             (0, 5): lambda L: sum(l**4 for l in L) / 8 + sum(L[i]**2 * L[j]**2 for i in range(5) for j in range(i + 1, 5)) / 2 + 3 * PI**2 * sum(l**2 for l in L) + 10 * PI**4}
    for (g, n), f in known.items():
        L = sp.symbols(f"L1:{n + 1}"); d = sp.expand(V(g, n) - f(L)); print(f"V_({g},{n}) from the recursion matches the known formula: {d == 0}", flush=True)
    for (g, n) in ((0, 4), (0, 5), (1, 2), (0, 6), (1, 3), (2, 2)):
        Fsum, L = pants_corner_sum(g, n); Vg = sp.expand(V(g, n))
        q, r = sp.div(sp.Poly(Fsum, *L, P), sp.Poly(Vg, *L, P))
        print(f"(g, n) = ({g},{n}): deg V = {sp.Poly(Vg, *L).total_degree()}, deg F = {sp.Poly(Fsum, *L).total_degree()};  F divisible by V: {r.is_zero}"
              + (f";  F / V = {sp.factor(q.as_expr())}" if r.is_zero else ""), flush=True)
