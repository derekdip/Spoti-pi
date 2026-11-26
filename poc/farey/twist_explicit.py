"""Compare the twist-averaged Riesz count with the explicit formula of its arithmetic core.
Core: (g^2/a) sum_{q<=X} (phi(q)/q)(X-q)^2, X = R/g, g = log(9/5) (gap law of alpha), whose zero terms are
    Z(R) = (g^2/a) sum_rho 2 zeta(rho-1) X^(rho+1) / ((rho-1) rho (rho+1) zeta'(rho)).
Tests: (1) the core itself vs its explicit formula (exact arithmetic check);
(2) the hyperbolic twist average: fit  F = cubic + beta * Z(R) (+ free cos/sin at g1 for comparison)."""
import math, numpy as np, mpmath as mp
mp.mp.dps = 20
a = 2 * math.log((3 + math.sqrt(5)) / 2); g = math.log(9 / 5)
zs = [mp.zetazero(k) for k in range(1, 101)]
co = [2 * mp.zeta(r - 1) / ((r - 1) * r * (r + 1) * mp.zeta(r, derivative=1)) for r in zs]
print("first zero coefficient |2 zeta(rho-1)/((rho-1)rho(rho+1)zeta'(rho))| = %.4e" % abs(co[0]))
def Z(R, nz=100):
    X = mp.mpf(R) / g
    return float((g * g / a) * sum(2 * (c * X ** (r + 1)).real for c, r in zip(co[:nz], zs[:nz])))
# (1) core check
N = 4000; phi = np.arange(N + 1)
for p in range(2, N + 1):
    if phi[p] == p: phi[p::p] -= phi[p::p] // p
def core(R):
    X = R / g; q = np.arange(1, int(X) + 1)
    return (g * g / a) * np.sum(phi[q] / q * (X - q) ** 2)
def core_pred(R):
    X = R / g
    return (g * g / a) * (2 * X ** 3 / math.pi ** 2 - X / 3) + Z(R)
print("\n(1) arithmetic core vs explicit formula (100 zeros):")
for R in (30.0, 60.0, 100.0, 150.0, 400.0, 1000.0):
    c = core(R); pr = core_pred(R); sm = (g * g / a) * (2 * (R / g) ** 3 / math.pi ** 2 - (R / g) / 3)
    print("   R = %6.0f: core - smooth = % .6f   zero sum = % .6f   difference % .2e   (R^1.5 = %.0f)" % (R, c - sm, Z(R), c - pr, R ** 1.5))
# (2) hyperbolic twist average
Rs, F = np.load("poc/farey/twist_average.npy"); m = Rs >= 20; Rs, F = Rs[m], F[m]
Zr = np.array([Z(R) for R in Rs])
Cr = np.array([core(R) for R in Rs])
def lsq(cols, y):
    X = np.array(cols).T; sc = np.abs(X).max(0); c, *_ = np.linalg.lstsq(X / sc, y, rcond=None); return y - (X / sc) @ c, c / sc
base = [Rs ** j for j in range(4)]
r0, _ = lsq(base, F)
r1, c1 = lsq(base + [Zr], F)
lg = np.log(Rs); g1 = float(zs[0].imag)
r2, c2 = lsq(base + [Rs ** 1.5 * np.cos(g1 * lg), Rs ** 1.5 * np.sin(g1 * lg)], F)
print("\n(2) hyperbolic twist average F(R), R in [20, 150]:")
print("   residual rms: cubic %.4f | cubic + beta Z(R) %.4f with beta = %.4f | cubic + free g1 term %.4f" % (r0.std(), r1.std(), c1[-1], r2.std()))
# phase/amplitude of the g1 component: free fit vs prediction
A_fit = complex(c2[-2], -c2[-1])
X1 = complex(2 * co[0] * (g * g / a) * g ** (-(zs[0] + 1)))   # R^(rho+1) coefficient: X^(rho+1) = R^(rho+1) g^-(rho+1)
A_pred = X1 * complex(1, 0)
print("   g1 component, as R^1.5 (A cos(g1 log R) + B sin): fit amplitude %.3e phase %.3f; predicted %.3e phase %.3f" % (
    abs(A_fit), math.atan2(A_fit.imag, A_fit.real), abs(A_pred), math.atan2(A_pred.imag, A_pred.real)))
# how much of F - (smooth) is the arithmetic core: compare F with the core directly
r3, c3 = lsq(base + [Cr], F)
print("   F = cubic + kappa * core: kappa = %.6f, residual rms %.4f" % (c3[-1], r3.std()))

# growth of the non-core residual, and the r-dependence of the tips (min over tau of l_{r,q})
for lo, hi in ((20, 50), (50, 90), (90, 150)):
    mm = (Rs >= lo) & (Rs < hi)
    print("   residual (cubic fit) rms on [%3d,%3d): %.3f   /R^1.5: %.2e   /R: %.2e   core zero-sum rms there: %.3f" % (
        lo, hi, r0[mm].std(), (r0[mm] / Rs[mm] ** 1.5).std(), (r0[mm] / Rs[mm]).std(), Zr[mm].std()))

