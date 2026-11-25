"""A Mirzakhani-type recursion for the corner polynomials F_{g,n}, checked symbolically.

F^S_{g}(Ls) = sum over pairs {i,j} of 'active' labels S of T_ij[V_g(x, L_rest)],
T_ij[V] = int_0^inf x^2 f(x; L_i, L_j) V(x, ...) dx,  f = (1/2) log P  (pants return orthogeodesic),
computed as sum_k c_k 2^{2k+2} [K_{2k+1}((Li+Lj)/2) + K_{2k+1}((Li-Lj)/2)].  F of a pair of pants is 0.

Recursion (distinguished boundary L1; S' = S - {1}):
  d/dL1 (L1 F^S_{g}(L)) =  M_{L1}[F^{S'}]                                     (Mirzakhani's operator with F in place of V:
                               connected term F_{g-1}(x, y, ...), disconnected F V + V F, B-terms F^{S'-k}_g(x, L without 1,k))
                        +  sum_{i<j in S'} T_ij[ I_1 ]                          (interaction: pants with beta_1 whose cuff is
                               the {i,j}-curve: I_1(x) = (1/2) int y [H(y, L1+x) + H(y, L1-x)] V_g(y, L_rest - 1) dy,
                               or I_1 = 1 when V_g(x, L_rest) is a pair of pants)
                        +  [1 in S] sum_{j in S'} d/dL1 (L1 T_1j[V_g(x, L_rest)]).
Both sides are computed independently (left: from the definition of F; right: from smaller F's and volumes).
"""
import sys, itertools
import sympy as sp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from higher_volumes import V as Vcached, Fk, coeffs_in, P
from moment_polys import K_sphere

xs = sp.symbols("xx yy")


def stable(g, n): return 2 * g - 2 + n > 0 and not (g == 0 and n < 3)


def Vof(g, syms):
    n = len(syms)
    if not stable(g, n): return None
    if (g, n) == (0, 3): return sp.Integer(1)
    return Vcached(g, n).subs(dict(zip(sp.symbols(f"L1:{n + 1}"), syms)), simultaneous=True)


def T(a, b, expr, var):
    """int_0^inf var^2 f(var; a, b) expr dvar, expr a polynomial even in var"""
    out = 0
    for k, c in coeffs_in(var, sp.expand(expr)).items():
        out += c * 2**(2 * k + 2) * (K_sphere(2 * k + 1, (a + b) / 2) + K_sphere(2 * k + 1, (a - b) / 2))
    return sp.expand(out)


def Fdef(g, syms, active):
    """definition: sum over pairs of active labels of T_ij[V_g(x, rest)]; zero for a pair of pants."""
    n = len(syms)
    if (g, n) == (0, 3): return sp.Integer(0)
    tot = 0; x = sp.Dummy("x")
    for a, b in itertools.combinations([s for s in syms if s in active], 2):
        rest = [s for s in syms if s not in (a, b)]
        Vr = Vof(g, [x] + rest)
        if Vr is None: continue
        tot += T(a, b, Vr, x)
    return sp.expand(tot)


def kernel2(expr_xy, x, y, t):
    """(1/2) int int x y H(x + y, t) expr dx dy for expr polynomial in x^2, y^2"""
    out = 0
    for (a, b), c in sp.Poly(sp.expand(expr_xy), x, y).terms():
        out += sp.Rational(1, 2) * c * sp.factorial(a + 1) * sp.factorial(b + 1) / sp.factorial(a + b + 3) * Fk((a + b + 2) // 2, t)
    return out


def kernel1(expr_x, x, t1, t2):
    """(1/2) int x [H(x, t1 + t2) + H(x, t1 - t2)] expr dx"""
    out = 0
    for k, c in coeffs_in(x, sp.expand(expr_x)).items():
        out += sp.Rational(1, 2) * c * (Fk(k, t1 + t2) + Fk(k, t1 - t2))
    return out


def rhs(g, syms, active):
    L1, others = syms[0], list(syms[1:]); S1 = set(active) - {L1}; x, y = sp.Dummy("x"), sp.Dummy("y"); tot = 0
    # Mirzakhani operator on F (pairs among S1 only; new boundaries x, y inactive)
    if g >= 1 and stable(g - 1, len(others) + 2):
        tot += kernel2(Fdef(g - 1, [x, y] + others, S1), x, y, L1)
    for g1 in range(g + 1):
        g2 = g - g1
        for r in range(len(others) + 1):
            for I in itertools.combinations(others, r):
                J = [o for o in others if o not in I]
                if not (stable(g1, len(I) + 1) and stable(g2, len(J) + 1)): continue
                F1 = Fdef(g1, [x] + list(I), S1); F2 = Fdef(g2, [y] + J, S1)
                V1 = Vof(g1, [x] + list(I)); V2 = Vof(g2, [y] + J)
                tot += kernel2(sp.expand(F1 * V2 + V1 * F2), x, y, L1)
    for k in others:
        rest = [o for o in others if o != k]
        if stable(g, len(rest) + 1):
            tot += kernel1(Fdef(g, [x] + rest, S1 - {k}), x, L1, k)
    # interaction: pairs among S1, the pants containing beta_1 has the {i,j}-curve as a cuff
    for a, b in itertools.combinations([s for s in others if s in S1], 2):
        rest = [s for s in syms if s not in (a, b)]                  # includes L1
        if not stable(g, len(rest) + 1): continue
        if (g, len(rest) + 1) == (0, 3):
            I1 = sp.Integer(1)                                       # d/dL1 (L1 V_{0,3}) = 1
        else:
            rest2 = [s for s in rest if s != L1]
            I1 = kernel1(Vof(g, [y] + rest2), y, L1, x) if stable(g, len(rest2) + 1) else 0
            # the B-term of V_g(x, rest) pairing L1 with x: (1/2) int y [H(y, L1 + x) + H(y, L1 - x)] V_g(y, rest - L1) dy
        tot += T(a, b, sp.expand(I1), x)
    # pairs containing 1
    if L1 in active:
        for j in [s for s in others if s in S1]:
            rest = [s for s in others if s != j]
            Vr = Vof(g, [x] + rest)
            if Vr is None: continue
            tot += sp.diff(L1 * T(L1, j, Vr, x), L1)
    return sp.expand(tot)


if __name__ == "__main__":
    for (g, n) in ((0, 4), (0, 5), (0, 6), (1, 2), (1, 3), (0, 7), (2, 2)):
        L = list(sp.symbols(f"L1:{n + 1}"))
        lhs = sp.expand(sp.diff(L[0] * Fdef(g, L, set(L)), L[0]))
        r = rhs(g, L, set(L))
        print(f"(g, n) = ({g},{n}): d/dL1 (L1 F) - [M(F) + interaction + pairs with 1] = {sp.simplify(lhs - r)}", flush=True)
