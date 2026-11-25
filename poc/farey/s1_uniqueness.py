"""Why the dual area (s = 1) is the unique moment with int = c V^2 (the input of the product law).

(1) Locality: unfolding writes int sum g N^s as a sum over pants-pairs (A, B) of K_s((A+B)/2) + K_s((A-B)/2), a polynomial
    of degree s+3 (s odd). (2) Degree: c V^2 has degree 4, so s = 1. (3) At s = 1, torus: degree 4 with a double root at the
    flat point forces c (y^2 + pi^2)^2; sphere: sum_{i<j} [(Li+Lj)^4 + (Li-Lj)^4] is a multiple of (sum L^2)^2 iff n = 4.
    For s >= 3 a function of sum L^2 needs triple products L_i^2 L_j^2 L_k^2, which pants (two other boundaries) cannot make.
(4) Bridge to Mirzakhani's recursion: d/dL g(x; L) = (1/2) sinh(L/2)/(cosh x + cosh(L/2)) = (1/2)(1 - H(L, 2x)),
    H(x, y) = 1/(1 + e^{(x+y)/2}) + 1/(1 + e^{(x-y)/2}); and int_0^inf x^2/(cosh x + cosh a) dx = a (a^2 + pi^2)/(3 sinh a),
    so d/dL int A* = L (L^2 + 4 pi^2)/96 = (L/2) V11  -> int A* = 6 V11^2 (fundamental-domain normalisation).
"""
import sympy as sp, mpmath as mp, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from moment_polys import I_sphere, P

if __name__ == "__main__":
    # (3) the n = 4 coincidence
    for n in (3, 4, 5, 6):
        L = sp.symbols(f"L1:{n + 1}"); lhs = sp.expand(sum((L[i] + L[j])**4 + (L[i] - L[j])**4 for i in range(n) for j in range(i + 1, n)))
        S2 = sp.expand(sum(x**2 for x in L)**2); c = sp.Poly(lhs, *L).coeff_monomial(L[0]**4) / sp.Poly(S2, *L).coeff_monomial(L[0]**4)
        print(f"n = {n}: sum_(i<j) [(Li+Lj)^4 + (Li-Lj)^4] - {c} (sum L^2)^2 = {sp.factor(sp.expand(lhs - c * S2))}")
    # (3') triple products absent at s = 3 on the sphere, but needed by any function of sum L^2 of that degree
    e, L = I_sphere(3); top = sp.Poly(e, *L, P)
    print(f"sphere s = 3: coefficient of L1^2 L2^2 L3^2 in int = {top.coeff_monomial(L[0]**2 * L[1]**2 * L[2]**2)};  in (sum L^2)^3 it is 6")
    # (4) kernel identity and the derivative of int A*
    mp.mp.dps = 30
    H = lambda x, y: 1 / (1 + mp.exp((x + y) / 2)) + 1 / (1 + mp.exp((x - y) / 2))
    worst = max(abs(mp.sinh(Lv / 2) / (mp.cosh(x) + mp.cosh(Lv / 2)) - (1 - H(Lv, 2 * x))) for Lv in (0.3, 1.7, 4.0) for x in (0.2, 1.1, 3.0))
    print(f"(1/2) sinh(L/2)/(cosh x + cosh(L/2)) = (1/2)(1 - H(L, 2x)): worst error {mp.nstr(worst, 3)}")
    for a in (0.5, 2.0, 5.0):
        num = mp.quad(lambda x: x**2 / (mp.cosh(x) + mp.cosh(a)), [0, 5, 30, 100])
        print(f"int x^2/(cosh x + cosh a), a = {a}: {mp.nstr(num, 18)}  vs a(a^2 + pi^2)/(3 sinh a) = {mp.nstr(a * (a * a + mp.pi**2) / (3 * mp.sinh(a)), 18)}")
    for Lv in (0.0, 2.0, 5.0):
        num = mp.quad(lambda x: x**2 / 4 * mp.sinh(Lv / 2) / (mp.cosh(x) + mp.cosh(Lv / 2)), [0, 5, 30, 100])
        V11 = (Lv**2 + 4 * mp.pi**2) / 48
        print(f"d/dL int A* at L = {Lv}: {mp.nstr(num, 15)}  vs (L/2) V11 = {mp.nstr(Lv / 2 * V11, 15)}")
