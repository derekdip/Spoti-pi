"""Odd moments of the corner measure, averaged over moduli: closed forms and their factorisation.

One-holed torus, boundary L, y = L/2. Corner measure mu_X = sum_gamma g_gamma delta_{N_gamma} (N = l/2). Unfolding:
    I_s(y) = int over M_{1,1}(L) of sum_gamma g N^s = int_0^inf (l^{s+1}/2^s) log((cosh l + cosh y)/(cosh l - 1)) dl.
Decomposition (log cosh / log sinh series): for s odd the two log(1 + e^-u) pieces combine into an integral over the whole
line, giving
    I_s = [ y^{s+3}/((s+2)(s+3)) + sum_{j even} C(s+1, j) y^{s+1-j} 2 j! eta(j+2) + 2 (s+1)! zeta(s+3) ] / 2^s,
a polynomial in y and pi^2. (s = 1: the dual area.) Four-holed sphere: per pants factor the same with l -> x, y -> (A+-B)/2.
"""
import sympy as sp

y, P = sp.symbols("y pi", positive=True)
zeta_even = lambda n: sp.Rational(abs(sp.bernoulli(n)) * 2**(n - 1), sp.factorial(n)) * P**n      # zeta(n), n even
eta_even = lambda n: (1 - sp.Rational(1, 2**(n - 1))) * zeta_even(n)


def I_torus(s):
    assert s % 2 == 1
    tot = y**(s + 3) / ((s + 2) * (s + 3))
    for j in range(0, s + 2, 2):
        tot += sp.binomial(s + 1, j) * y**(s + 1 - j) * 2 * sp.factorial(j) * eta_even(j + 2)
    tot += 2 * sp.factorial(s + 1) * zeta_even(s + 3)
    return sp.expand(tot / 2**s)


if __name__ == "__main__":
    import mpmath as mp
    for s in (1, 3, 5, 7, 9):
        e = I_torus(s); f = sp.factor(e)
        print(f"s = {s}: I_s(y) = {f}")
        # numerical check of the integral at y = 0.7
        yy = mp.mpf("0.7")
        num = mp.quad(lambda l: l**(s + 1) / 2**s * mp.log((mp.cosh(l) + mp.cosh(yy)) / (2 * mp.sinh(l / 2)**2)), [0, 1, 5, 20, 80])
        print(f"        check at y = 0.7: quadrature {mp.nstr(num, 15)}  formula {mp.nstr(sp.N(e.subs({y: sp.Rational(7, 10), P: sp.pi}), 20), 15)}")


def K_sphere(s, yy):
    """K_s(y) = int_0^inf u^{s+1} log((cosh u + cosh y)/sinh u) du, s odd (one pants factor, u = x/2)."""
    tot = yy**(s + 3) / ((s + 2) * (s + 3))
    for j in range(0, s + 2, 2):
        tot += sp.binomial(s + 1, j) * yy**(s + 1 - j) * 2 * sp.factorial(j) * eta_even(j + 2)
    tot += sp.factorial(s + 1) * (zeta_even(s + 3) - eta_even(s + 3))
    return tot


def I_sphere(s):
    """int over M_{0,4}(L) of sum g N^s: sum over pairings, pairs (A,B): 4 [K((A+B)/2) + K((A-B)/2)] (from x = 2u, N = x/2 = u)."""
    L = sp.symbols("L1:5", positive=True); tot = 0
    for (i, j, k, l) in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        for (A, B) in ((L[i], L[j]), (L[k], L[l])):
            tot += 4 * (K_sphere(s, (A + B) / 2) + K_sphere(s, (A - B) / 2))
    return sp.expand(tot), L


def sphere_report():
    import mpmath as mp
    for s in (1, 3, 5):
        e, L = I_sphere(s); S = sum(x**2 for x in L) + 4 * P**2
        q, r = sp.div(sp.Poly(e, *L, P), sp.Poly(S**2, *L, P))
        print(f"sphere s = {s}: remainder of I_s / (sum L^2 + 4 pi^2)^2 is {'0' if r.is_zero else r.as_expr()};  quotient {sp.factor(q.as_expr())}")
        # numerical check at L = (0.3, 0.8, 0.5, 1.1): direct integral over x of x g(x) (x/2)^s summed over the 3 pairings
        Lv = [mp.mpf(v) for v in ("0.3", "0.8", "0.5", "1.1")]
        def Pf(x, A, Bb): h = mp.cosh(x / 2); return (h + mp.cosh((A + Bb) / 2)) * (h + mp.cosh((A - Bb) / 2)) / mp.sinh(x / 2)**2
        num = 0
        for (i, j, k, l) in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
            num += mp.quad(lambda x: x * (x / 2)**s * mp.log(Pf(x, Lv[i], Lv[j]) * Pf(x, Lv[k], Lv[l])), [0, 1, 5, 20, 120])
        val = sp.N(e.subs({**{L[t]: sp.Rational(str(Lv[t])) for t in range(4)}, P: sp.pi}), 20)
        print(f"        check at L = (0.3, 0.8, 0.5, 1.1): quadrature {mp.nstr(num, 14)}  formula {mp.nstr(val, 14)}")


if __name__ == "__main__":
    sphere_report()


def sphere_divisibility():
    """Divisibility of the sphere odd moments by S = sum L^2 + 4 pi^2 once, and vanishing order at the pillowcase
    (all L_i = i pi, four cone angles pi: the flat point)."""
    t = sp.symbols("t")
    for s in (1, 3, 5, 7):
        e, L = I_sphere(s); S = sum(x**2 for x in L) + 4 * P**2
        r1 = sp.div(sp.Poly(e, *L, P), sp.Poly(S, *L, P))[1]
        # along the ray L_i = i pi (1 - t), vanishing order in t at t = 0
        ray = sp.expand(e.subs({x: sp.I * P * (1 - t) for x in L}))
        order = next(k for k in range(12) if sp.simplify(ray.diff(t, k).subs(t, 0)) != 0)
        print(f"sphere s = {s}: divisible by S once: {r1.is_zero};  vanishing order at the pillowcase along L_i = i pi (1 - t): {order}")


if __name__ == "__main__":
    sphere_divisibility()
