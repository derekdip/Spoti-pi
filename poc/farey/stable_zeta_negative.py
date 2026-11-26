"""Z_B(-m) for the stable norm of the modular torus from Barnes double zeta values, as Farey-cell sums.
Polygon norm with unimodular fan: Z_N(s) = sum_cones zeta_2(s; w1+w2 | w1, w2) + zeta(s) sum_rays N^-s, and
zeta_2(-m; w1+w2 | w1, w2) = m!/(m+2)! B_{2,m+2},  sum_n B_{2,n} t^n/n! = t^2 / ((1-e^{-w1 t})(1-e^{-w2 t})).
Per cone: T_m(a,b) = zeta_2(-m) + zeta(-m)(a^m + b^m)/2  (each ray shared by two cones).
Z_B(-m) = T-sum of the root hexagon + sum over Farey cells of [T_m(a,c) + T_m(c,b) - T_m(a,b)], c = N(mediant).
Independent check: Theta(eps) - 1 = 2 Area/eps^2 + sum_n Z(-n)(-eps)^n/n!."""
import sympy as sp, mpmath as mp, math, numpy as np
mp.mp.dps = 40
t, w1, w2 = sp.symbols('t w1 w2', positive=True)
gen = sp.series(t ** 2 / ((1 - sp.exp(-w1 * t)) * (1 - sp.exp(-w2 * t))), t, 0, 9).removeO()
MS = range(0, 6)
Tfun = {}
for m in MS:
    B = sp.factorial(m + 2) * sp.expand(gen).coeff(t, m + 2)
    z2 = sp.simplify(sp.factorial(m) / sp.factorial(m + 2) * B)
    T = sp.simplify(z2 + sp.zeta(-m) * (w1 ** m + w2 ** m) / 2) if m > 0 else sp.simplify(z2 + sp.Rational(-1, 2) * sp.Rational(1, 2) * 2)
    Tfun[m] = sp.lambdify((w1, w2), T, "mpmath")
    print("m = %d: zeta_2(-m; w1+w2|w1,w2) = %s ;  per-cone T_m = %s" % (m, sp.factor(z2), sp.factor(T)))
L = lambda tr: 2 * mp.acosh(mp.mpf(tr) / 2)
l3 = L(3)
def cellsum(m, NMAX=45):
    tot = 6 * Tfun[m](l3, l3)              # root hexagon e0, e0+e1, e1, -e0, ... all of length l3
    stack = [(3, 3, 3), (3, 3, 3), (3, 3, 3)]  # three cones (half plane); the other three by symmetry
    acc = mp.mpf(0)
    while stack:
        tu, tw, td = stack.pop(); tm = tu * tw - td
        a, b, c = L(tu), L(tw), L(tm)
        if c > NMAX: continue
        acc += Tfun[m](a, c) + Tfun[m](c, b) - Tfun[m](a, b)
        stack += [(tu, tm, tw), (tm, tw, tu)]
    return tot + 2 * acc
res = {m: cellsum(m) for m in MS}
for m in MS:
    print("Z_B(-%d) from Farey-cell Barnes sum: %s   (cutoff N <= 35: %s)" % (m, mp.nstr(res[m], 15), mp.nstr(cellsum(m, 35), 15)))
# theta check: reuse the primitive lengths
RMAX = 2500.0
def Lf(tr): return 2 * math.acosh(tr / 2) if tr < 10**300 else 2 * math.log(tr)
out = [Lf(3)] * 3; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lf(tm)
    if lm > RMAX: continue
    out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
Ns = np.sort(np.array(out)); area = 0.891803166008
e = np.array([0.4, 0.3, 0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025])
th = np.array([2 * np.sum(1 / np.expm1(x * Ns[x * Ns < 700])) - 2 * area / x ** 2 for x in e])
X = np.array([e ** n for n in range(6)]).T
c = np.linalg.lstsq(X, th, rcond=None)[0]
print("\ntheta fit  Theta - 1 - 2Area/eps^2 = sum_n Z(-n) (-eps)^n / n!  (eps in [0.025, 0.4], degree 5):")
for n in range(4):
    print("   n = %d: Z_B(-%d) from theta = %.6f   Farey-cell Barnes = %s" % (n, n, c[n] * math.factorial(n) * (-1) ** n, mp.nstr(res[n], 8)))
print("   Z_B(0) toric formula -1 + (1/3) sum g/l = -0.653652 (previous section)")
