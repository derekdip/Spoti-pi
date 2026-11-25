"""The higher-complexity pants-corner polynomials F_{g,n} as the next moment of Mirzakhani's recursion.

(1) Kernel identity: with f(x; A, B) = (1/2) log P(x; A, B) (P = cosh^2(d/2), the pants' return orthogeodesic),
        (1/4) [H(x, A+B) + H(x, A-B)] = 1/2 - (1/2) coth(x/2) - d/dx f(x; A, B),
    H Mirzakhani's kernel. Hence her B-term (1/2) int x [H(x, L1+Lj) + H(x, L1-Lj)] V(x) dx
        = 2 int f(x; L1, Lj) d/dx(x V) dx + int x (1 - coth(x/2)) V dx      (integration by parts).
    So the volume recursion is the s = -1 moment of the pants factor (weight d/dx(x .)), and
        F_{g,n} = sum_{i<j} int x^2 f(x; L_i, L_j) V_{g,n-1}(x, L_rest) dx
    is the s = +1 moment.
(2) Table of F_{g,n} and the cusped averages <F> = F(0)/V(0).
"""
import sys, itertools, time
import sympy as sp, mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from higher_volumes import V, pants_corner_sum, Fk, coeffs_in, P


def kernel_check():
    mp.mp.dps = 40
    H = lambda x, y: 1 / (1 + mp.exp((x + y) / 2)) + 1 / (1 + mp.exp((x - y) / 2))
    f = lambda x, A, B: (mp.log(mp.cosh(x / 2) + mp.cosh((A + B) / 2)) + mp.log(mp.cosh(x / 2) + mp.cosh((A - B) / 2))) / 2 - mp.log(mp.sinh(x / 2))
    worst = 0
    for (x, A, B) in ((0.3, 0.7, 1.9), (2.5, 3.1, 0.4), (6.0, 1.2, 5.5), (11.0, 0.0, 0.0)):
        lhs = (H(x, A + B) + H(x, A - B)) / 4; rhs = mp.mpf(1) / 2 - mp.coth(x / 2) / 2 - mp.diff(lambda t: f(t, A, B), x)
        worst = max(worst, abs(lhs - rhs))
    print(f"(1) kernel identity, worst error {mp.nstr(worst, 3)}")
    # B-term both ways for V(x) = V_{1,1}(x) = (x^2 + 4 pi^2)/48 (the B-term of the (1,2) recursion), at L1 = 1.3, L2 = 0.6
    L1, L2 = mp.mpf("1.3"), mp.mpf("0.6"); Vx = lambda x: (x * x + 4 * mp.pi**2) / 48; dxV = lambda x: Vx(x) + x * x / 24
    B1 = mp.quad(lambda x: x * (H(x, L1 + L2) + H(x, L1 - L2)) * Vx(x) / 2, [0, 5, 30, 120])
    B2 = mp.quad(lambda x: 2 * f(x, L1, L2) * dxV(x) + x * (1 - mp.coth(x / 2)) * Vx(x), [0, 5, 30, 120])
    print(f"    B-term of the (1,2) recursion at (L1, L2) = (1.3, 0.6): via H {mp.nstr(B1, 20)};  via the pants factor {mp.nstr(B2, 20)}")


def table(cases, budget=1500):
    t0 = time.time()
    for (g, n) in cases:
        if time.time() - t0 > budget: print("   (time budget reached)"); break
        Fsum, L = pants_corner_sum(g, n); Vg = sp.expand(V(g, n))
        F0 = Fsum.subs({l: 0 for l in L}); V0 = Vg.subs({l: 0 for l in L}); r = sp.cancel(sp.expand(F0) / (sp.expand(V0) * P**2))
        npairs = n * (n - 1) // 2
        q, rem = sp.div(sp.Poly(Fsum, *L, P), sp.Poly(Vg, *L, P))
        # quotient degree-2 part: F = V Q + R with Q of degree 2 (division in lex order); report Q's symmetric part
        print(f"({g},{n}): V(0) = {sp.factor(V0)};  <F>(cusped) = F(0)/V(0) = {r} pi^2  (= {sp.cancel(r / npairs)} = {float(r / npairs):.5f} pi^2 per boundary pair, {npairs} pairs)", flush=True)


if __name__ == "__main__":
    kernel_check()
    table([(0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (3, 2), (4, 2)], budget=2400)
