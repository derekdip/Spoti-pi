"""Identify the corner kernel with Mirzakhani's B-kernel.

S = 2 pi D / sin(2 pi D) (D = d/dX) is logistic smoothing (rho(u) = sech^2(u/4)/8) on polynomials; x/sin x = sum a_j x^{2j}.
Mirzakhani's B-term for a pair (1, j), as a function of t = L1 +- Lj: d/dt B[V](t) = (1/2) S[t V(t)]   (B[V](0) = 0),
since d/dt H(x, t) = rho(x - t) - rho(x + t).
Claim: the corner pair transform, as a function of X = Li +- Lj, is
    G[V](X) = (1/2) int_0^X B[x V](u) du + G[V](0),       i.e.  d^2/dX^2 G = (1/4) S[X^2 V(X)],
with T_ij[V] = G[V](Li + Lj) + G[V](Li - Lj). Check on monomials V = x^{2k}: G[x^{2k}](2y) must equal 2^{2k+2} K_{2k+1}(y).
"""
import sympy as sp, mpmath as mp, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from moment_polys import K_sphere, P

X, y, u = sp.symbols("X y u")


def S_op(poly, var, order=40):
    """2 pi D / sin(2 pi D) on a polynomial"""
    ser = sp.series(sp.Symbol("z") / sp.sin(sp.Symbol("z")), sp.Symbol("z"), 0, order).removeO()
    out = 0
    for j in range(0, order // 2):
        a = ser.coeff(sp.Symbol("z"), 2 * j)
        if a == 0: continue
        d = sp.diff(poly, var, 2 * j)
        if d == 0: break
        out += a * (2 * P)**(2 * j) * d
    return sp.expand(out)


def B_of(h):
    """Mirzakhani's B as a function of t: int_0^t (1/2) S[h](s) ds"""
    s = sp.Symbol("s"); return sp.integrate(sp.Rational(1, 2) * S_op(h.subs(X, s), s), (s, 0, X))


if __name__ == "__main__":
    # (a) Mirzakhani's B-kernel moments F_{2k+1}(t) = int x^{2k+1} H(x, t) dx satisfy d/dt F_{2k+1}(t) = S[t^{2k+1}] (odd extension):
    from higher_volumes import Fk
    for k in range(4):
        lhs = sp.diff(Fk(k, X), X); rhs = S_op(X**(2 * k + 1), X)
        print(f"(a) k = {k}: d/dt F_(2k+1)(t) - S[t^(2k+1)] = {sp.simplify(lhs - rhs)}")
    # (b) the claim on monomials
    for k in range(5):
        G = sp.Rational(1, 2) * sp.integrate(B_of(X**2 * X**(2 * k)).subs(X, u), (u, 0, X))   # B[x V]: smoothing of t (t V(t)) = t^2 V
        target = sp.expand(2**(2 * k + 2) * K_sphere(2 * k + 1, X / 2))
        const = sp.expand(target.subs(X, 0))
        print(f"(b) k = {k}: G[x^{2 * k}](X) + G(0) - 2^(2k+2) K_(2k+1)(X/2) = {sp.simplify(sp.expand(G + const - target))};  G(0) = {sp.factor(const)}")
    # (c) the constant G(0) = (1/2) int x^2 log coth(x/4) V dx: check for V = x^{2k}
    mp.mp.dps = 30
    for k in range(3):
        num = mp.quad(lambda x: x**2 * mp.log(mp.coth(x / 4)) * x**(2 * k) / 2, [0, 5, 40, 200])
        print(f"(c) k = {k}: (1/2) int x^(2k+2) log coth(x/4) dx = {mp.nstr(num, 20)};  G(0) = {mp.nstr(sp.N(sp.expand(2**(2 * k + 2) * K_sphere(2 * k + 1, 0)).subs(P, sp.pi), 25), 20)}")
