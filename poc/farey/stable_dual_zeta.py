"""Continuation of Z_B(s) = sum_{v != 0} N(v)^-s to -1 < Re s < 0 from the Voronoi series:
    Z_B(s) = -((2 pi)^s / pi) Gamma(1-s) cos(pi s/2) sum_gamma l^-s [C_{a+}(1-s) - C_{a-}(1-s)],  C_a(w) = sum_k cot(pi k a) k^-w.
Independent check: Z_B(s) = lim_{eps->0} [ sum_v N^-s e^{-eps N} - 2 Area Gamma(2-s) eps^(s-2) ]  (+ O(eps) terms, extrapolated).
Also Z_B(0) = C (the mean lattice error, -0.6537), compared with -1 (quadratic forms) and -2/3 (the square)."""
import math, numpy as np, mpmath as mp
exec(open("poc/farey/stable_voronoi_series.py").read().split("# lattice side")[0].replace("'TMAX = 60.0'", "'TMAX = 60.0'"))
area = 0.891803166008
allN = np.concatenate([Ls * k for k in range(1, 400)]); allN = allN[allN < 128]
def direct(s, eps):
    return 2 * np.sum(allN ** (-s) * np.exp(-eps * allN)) - 2 * area * complex(mp.gamma(2 - s)) * eps ** (s - 2)
def direct_extrap(s):
    e = np.array([0.5, 0.4, 0.3, 0.25]); v = np.array([direct(s, x) for x in e])
    # fit v = Z + a eps + b eps^2
    X = np.array([np.ones_like(e), e, e * e]).T
    return np.linalg.lstsq(X.astype(complex), v, rcond=None)[0][0], v
def dual(s, KMAX=20000, LMAX=130):
    k = np.arange(1, KMAX + 1)[:, None]; mm = Ls <= LMAX
    c = (1 / np.tan(math.pi * k * ap[mm]) - 1 / np.tan(math.pi * k * am[mm])) * k ** (s - 1.0)
    S = np.sum(Ls[mm] ** (-s) * np.sum(c, 0))
    return -(2 * math.pi) ** s / math.pi * complex(mp.gamma(1 - s)) * complex(mp.cos(math.pi * s / 2)) * S
for s in (-0.3, -0.6, complex(-0.4, 3.0), complex(-0.5, 8.0)):
    Zd, raw = direct_extrap(s)
    print("s = %-14s direct (eps -> 0): %.5f %+.5fi   [eps = .5..: %s]" % (s, Zd.real, Zd.imag, " ".join("%.4f" % x.real for x in raw)))
    for KM, LM in ((2000, 60), (20000, 60), (20000, 130)):
        Zv = dual(s, KM, LM); print("        dual series (k <= %5d, l <= %3d): %.5f %+.5fi" % (KM, LM, Zv.real, Zv.imag))
Z0, raw = direct_extrap(0.0)
print("\nZ_B(0) direct: %.5f   (mean lattice error C = -0.6537; quadratic forms give -1, the square 8 zeta(-1) = -2/3)" % Z0.real)

print("\nRiesz-weighted cotangent sums, weight (1 - k/K)^3, geodesics with l <= LM:")
def dual_riesz(s, K, LM, chunk=200000):
    mm = Ls <= LM; S = np.zeros(mm.sum(), complex)
    for k0 in range(1, K + 1, chunk):
        k = np.arange(k0, min(K, k0 + chunk - 1) + 1)[:, None].astype(float)
        w = (1 - k / K) ** 3
        S += np.sum(w * (1 / np.tan(math.pi * k * ap[mm]) - 1 / np.tan(math.pi * k * am[mm])) * k ** (s - 1.0), 0)
    S = np.sum(Ls[mm] ** (-s) * S)
    return -(2 * math.pi) ** s / math.pi * complex(mp.gamma(1 - s)) * complex(mp.cos(math.pi * s / 2)) * S
for s in (-0.3, -0.6, complex(-0.4, 3.0)):
    Zd, _ = direct_extrap(s)
    row = ["K=%d: %.4f%+.4fi" % (K, *(lambda z: (z.real, z.imag))(dual_riesz(s, K, 20))) for K in (10**4, 10**5, 10**6)]
    print("  s = %-12s direct %.4f%+.4fi | dual, l <= 20: %s | dual l <= 40, K=10^6: %.4f" % (s, Zd.real, Zd.imag, "  ".join(row), dual_riesz(s, 10**6, 40).real))
