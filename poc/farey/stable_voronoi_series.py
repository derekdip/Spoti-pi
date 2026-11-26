"""Voronoi series for the lattice error of the stable-norm ball (modular torus), Gaussian-smoothed in R:
   E_sigma(R) = sum_{gamma simple} sum_{k>=1} [cot(pi k a+) - cot(pi k a-)]/(pi k) cos(2 pi k R/l) exp(-2 pi^2 sigma^2 k^2/l^2) + C
 a^+- = <J n^+-, xi0>/l with <v, xi0> = 1.  Compared with the smoothed lattice count minus Area (R^2 + sigma^2)."""
import math, numpy as np, sys
from scipy.special import ndtr
exec(open("poc/farey/stable_voronoi.py").read().split('K = lambda a')[0].replace('TMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0', 'TMAX = 130.0'))
def egcd(a, b):
    if b == 0: return (1, 0) if a >= 0 else (-1, 0)
    x, y = egcd(b, a % b); return (y, x - (a // b) * y)
half = corners[: len(corners) // 2]
ap, am, Ls = [], [], []
for v, N, G, npl, nm in half:
    p, q = int(v[0]), int(v[1]); x, y = egcd(p, q); assert p * x + q * y == 1
    xi0 = np.array([x, y], float)
    ap.append((J(npl) @ xi0) / N); am.append((J(nm) @ xi0) / N); Ls.append(N)
ap, am, Ls = np.array(ap), np.array(am), np.array(Ls)
print("geodesics (mod sign) with l <= %g: %d;  check a- - a+ = G/l: max err %.1e" % (TMAX, len(Ls), np.max(np.abs((am - ap) - np.array([c[2] for c in half]) / Ls))))
# lattice side: all x = k v, N(x) = k l
Rs = np.linspace(20, 100, 161); area = 0.891803166008
lens = np.concatenate([Ls * k for k in range(1, 200)]); lens = lens[lens < 125]
def lattice_smooth(R, s): return 2 * np.sum(ndtr((R - lens) / s)) - area * (R * R + s * s)
def series(R, s, KMAX=400):
    k = np.arange(1, KMAX + 1)[:, None]
    amp = (1 / np.tan(math.pi * k * ap) - 1 / np.tan(math.pi * k * am)) / (math.pi * k)
    damp = np.exp(-2 * math.pi ** 2 * s * s * k * k / Ls ** 2)
    return np.sum(amp * damp * np.cos(2 * math.pi * k * R / Ls))
for s in (0.5, 0.3):
    lat = np.array([lattice_smooth(R, s) for R in Rs]); ser = np.array([series(R, s) for R in Rs])
    C = np.mean(lat - ser)
    print("sigma = %.2f: rms lattice error %.4f; rms(series) %.4f; fitted constant C = %.4f; rms(lattice - series - C) %.2e; corr %.6f" % (
        s, lat.std(), ser.std(), C, (lat - ser - C).std(), np.corrcoef(lat, ser)[0, 1]))
# which geodesics carry the error: share of the series variance from l <= 10, 10..20, > 20 at sigma = 0.3
k = np.arange(1, 401)[:, None]
amp = (1 / np.tan(math.pi * k * ap) - 1 / np.tan(math.pi * k * am)) / (math.pi * k) * np.exp(-2 * math.pi ** 2 * 0.09 * k * k / Ls ** 2)
var = 0.5 * np.sum(amp ** 2, 0)
for lo, hi in ((0, 10), (10, 20), (20, 40), (40, 60), (60, 130)):
    mm = (Ls > lo) & (Ls <= hi); print("   l in (%2d, %2d]: %4d geodesics carry %.1f%% of the series variance" % (lo, hi, mm.sum(), 100 * var[mm].sum() / var.sum()))
print("   C vs -1 - (the Gibbs constant): the lattice count excludes x = 0")

# (a) the constant: C = -1 - S0, S0 = sum_gamma sum_k (cot pi k a+ - cot pi k a-)/(pi k)  (undamped, partial sums in k)
for KM in (1000, 4000, 16000):
    k = np.arange(1, KM + 1)[:, None]
    S0 = np.sum((1 / np.tan(math.pi * k * ap) - 1 / np.tan(math.pi * k * am)) / (math.pi * k))
    print("(a) K <= %5d: -1 - S0 = %.4f   (fitted C = -0.6537)" % (KM, -1 - S0))
# (b) zero amplitudes: Z_B(rho) from a smoothed lattice sum, and the predicted coefficient Z_B(rho)/(2 rho (rho+1) zeta'(rho))
import mpmath as mp
from scipy.special import gamma as G_
allN = np.concatenate([Ls * k for k in range(1, 400)]); allN = allN[allN < 128]
def ZB(s, X):
    w = np.exp(-(allN / X) ** 4)
    main = 2 * area * X ** (2 - s) * complex(mp.gamma((2 - s) / 4)) / 4
    return 2 * np.sum(allN ** (-s) * w) - main
r1 = complex(mp.zetazero(1)); zp1 = complex(mp.zeta(mp.mpc(r1.real, r1.imag), derivative=1))
for X in (30.0, 45.0, 60.0):
    z = ZB(r1, X); c = z / (2 * r1 * (r1 + 1) * zp1)
    print("(b) X = %4.0f: Z_B(rho_1) = %.5f %+.5fi;  |coefficient of R^(1+rho_1)| (mod sign) = %.4e   (fitted from P data: 1.88e-02)" % (X, z.real, z.imag, abs(c) / 1))
