"""Scan Z_B(rho_1) over the moduli space of cusped once-punctured tori. Fundamental domain (sink ordering x <= y <= z,
z the smaller Markoff root of x^2 + y^2 + z^2 = xyz): 2 < x <= 3, max(x, sqrt(4 + 16/(x^2-4))) <= y <= x/sqrt(x-2).
Corners: hexagonal (3,3,3), square (2v2, 2v2, 4), cusp x -> 2. Look for zeros via winding numbers of grid cells."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
K = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rho = complex(mp.zetazero(K)); th = math.pi / 3
def surf(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    z = (x * y - math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y), 0))) / 2
    return x, y, z
xs = 2 + 1 / np.linspace(1, 14, 40) ** 1.0 * 1.0         # x from 3 down to 2.07
vs = np.linspace(0, 1, 30)
Z = np.zeros((len(xs), len(vs)), complex)
for i, x in enumerate(xs):
    for j, v in enumerate(vs): Z[i, j] = ZB(rho, *surf(x, v), th=th, smax=40)[0]
    print("x = %.4f: |Z| min %.3f max %.3f" % (x, abs(Z[i]).min(), abs(Z[i]).max()), flush=True)
np.save("poc/farey/zb_scan_k%d.npy" % K, np.array([xs, vs, Z], dtype=object), allow_pickle=True)
ph = np.angle(Z); wind = []
for i in range(len(xs) - 1):
    for j in range(len(vs) - 1):
        loop = [Z[i, j], Z[i + 1, j], Z[i + 1, j + 1], Z[i, j + 1], Z[i, j]]
        w = sum(np.angle(loop[k + 1] / loop[k]) for k in range(4)) / (2 * math.pi)
        if abs(w) > 0.5: wind.append((i, j, round(w), xs[i], vs[j]))
print("grid cells with nonzero winding:", wind)
i, j = np.unravel_index(np.argmin(abs(Z)), Z.shape); print("min |Z| = %.4f at x = %.4f v = %.3f -> traces %s" % (abs(Z[i, j]), xs[i], vs[j], surf(xs[i], vs[j])))
