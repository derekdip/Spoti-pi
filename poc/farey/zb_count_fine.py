"""Finer zero census of Z_B(rho_k) on the mirror triangle (hyperbolic cusped tori): 64 x 48 grid with x down to 2.03,
Newton from every winding cell and from every local minimum of |Z| below 0.3, dedupe."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
def surf(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    z = (x * y - math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y), 0))) / 2
    return x, y, z
k = int(sys.argv[1]); rho = complex(mp.zetazero(k))
xs = np.concatenate([np.linspace(3.0, 2.15, 60), np.linspace(2.14, 2.03, 10)]); vs = np.linspace(0, 1, 50)
Z = np.array([[ZB(rho, *surf(x, v), th=math.pi / 3, smax=36)[0] for v in vs] for x in xs])
starts = []
for i in range(len(xs) - 1):
    for j in range(len(vs) - 1):
        lp = [Z[i, j], Z[i + 1, j], Z[i + 1, j + 1], Z[i, j + 1], Z[i, j]]
        if abs(sum(np.angle(lp[q + 1] / lp[q]) for q in range(4))) > math.pi: starts.append(((xs[i] + xs[i + 1]) / 2, (vs[j] + vs[j + 1]) / 2))
A = np.abs(Z)
for i in range(1, len(xs) - 1):
    for j in range(1, len(vs) - 1):
        if A[i, j] < 0.3 and A[i, j] == A[i - 1:i + 2, j - 1:j + 2].min(): starts.append((xs[i], vs[j]))
F = lambda p: (lambda w: [w.real, w.imag])(ZB(rho, *surf(min(max(p[0], 2.01), 3.0), min(max(p[1], 0.0), 1.0)), th=math.pi / 3, smax=40)[0])
found = []
for p0 in starts:
    sol = fsolve(F, list(p0), xtol=1e-12); x, v = sol
    if np.hypot(*F(sol)) < 1e-7 and 2.01 < x <= 3 and 0 <= v <= 1 and not any(abs(x - a) < 1e-6 and abs(v - b) < 1e-6 for a, b in found):
        found.append((x, v))
print("k = %d gamma = %.3f: %d starts, %d confirmed zeros (hyperbolic, mirror triangle)" % (k, rho.imag, len(starts), len(found)), flush=True)
for x, v in sorted(found): print("     traces (%.7f, %.7f, %.7f)" % surf(x, v))
