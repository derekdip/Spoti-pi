"""Flat analogue of zero-blind surfaces. For a flat unit-area torus with modulus z, the lattice zeta is
2 zeta(s) E(z, s/2), and the sharp primitive count carries rho with amplitude prop. to E*(z, rho/2), where
E* = xi(2s) E(z, s) = xi(2s) y^s + xi(2-2s) y^{1-s} + 4 sqrt(y) sum_n n^{s-1/2} sigma_{1-2s}(n) K_{s-1/2}(2 pi n y) cos(2 pi n x).
At s = rho/2, xi(2s) = 0. Blind flat tori are zeros of E*(., rho/2) on the half fundamental domain
0 <= x <= 1/2, |z| >= 1 (the PGL2(Z) quotient, matching the mirror triangle used for hyperbolic tori)."""
import mpmath as mp, numpy as np, math, sys
from scipy.optimize import fsolve
mp.mp.dps = 20
xi = lambda w: mp.pi ** (-w / 2) * mp.gamma(w / 2) * mp.zeta(w)
NT = 40
def coefs(s):
    sig = [mp.fsum(mp.mpf(d) ** (1 - 2 * s) for d in range(1, n + 1) if n % d == 0) for n in range(1, NT + 1)]
    return [mp.mpf(n) ** (s - 0.5) * sig[n - 1] for n in range(1, NT + 1)]
def Estar(s, x, y, cf, c2):
    tot = c2 * mp.mpf(y) ** (1 - s)
    for n in range(1, NT + 1):
        u = 2 * mp.pi * n * y
        if u > 60 + abs(s.imag): break
        tot += 4 * mp.sqrt(y) * cf[n - 1] * mp.besselk(s - 0.5, u) * mp.cos(2 * mp.pi * n * x)
    return complex(tot)
res = []
for k in range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 9):
    rho = mp.zetazero(k); s = rho / 2; cf = coefs(s); c2 = xi(2 - 2 * s)
    # grid: x in [0, 1/2], y from the arc to YMAX; constant term dominates above (no zeros)
    YMAX = 2.5 + float(rho.imag) / 12
    nx, ny = 45, 90
    xs = np.linspace(0, 0.5, nx); us = np.linspace(0, 1, ny)
    Y = lambda x, u: math.sqrt(1 - x * x) + u * (YMAX - math.sqrt(1 - x * x))
    # separable evaluation: precompute K for each (x-column's y) is not separable since y depends on x; just loop
    F = np.array([[Estar(s, x, Y(x, u), cf, c2) for u in us] for x in xs])
    cand = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            loop = [F[i, j], F[i + 1, j], F[i + 1, j + 1], F[i, j + 1], F[i, j]]
            w = sum(np.angle(loop[q + 1] / loop[q]) for q in range(4)) / (2 * math.pi)
            if abs(w) > 0.5: cand.append(((xs[i] + xs[i + 1]) / 2, (us[j] + us[j + 1]) / 2))
    found = []
    G = lambda p: (lambda v: [v.real, v.imag])(Estar(s, p[0], p[1], cf, c2))
    for xc, uc in cand:
        sol = fsolve(G, [xc, Y(xc, uc)], xtol=1e-12)
        if np.hypot(*G(sol)) < 1e-9 and 0 < sol[0] < 0.5 and sol[0] ** 2 + sol[1] ** 2 > 1 and not any(np.hypot(sol[0] - a, sol[1] - b) < 1e-6 for a, b in found):
            found.append(tuple(sol))
    g = float(rho.imag); res.append((k, g, len(cand), len(found)))
    print("k = %d gamma = %7.3f: %d winding cells, %d confirmed blind flat tori; |E*| range on grid [%.3g, %.3g]; random-wave estimate gamma^2/96 = %.1f" % (
        k, g, len(cand), len(found), np.abs(F).min(), np.abs(F).max(), g * g / 96), flush=True)
    for a, b in sorted(found): print("      z = %.6f + %.6f i" % (a, b))
