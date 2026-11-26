"""Hyperbolic blind-surface census by argument-principle bisection: grid -> winding cells -> recursive 2x2 subdivision
keeping cells with nonzero winding (boundary sampled densely) down to size 1e-5, then Newton polish. Robust where
Newton from coarse starts fails. Chart (x, v), sink-normalised so Z is continuous across mirror edges; zeros counted
once per distinct sink triple."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cusp_whittaker import sink
def surf_raw(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    d = (x * y) ** 2 - 4 * (x * x + y * y)
    if d < 0: y = lo; d = 0.0
    return x, y, (x * y - math.sqrt(d)) / 2
k = int(sys.argv[1]); rho = complex(mp.zetazero(k))
cache = {}
def Z(x, v):
    key = (round(x, 12), round(v, 12))
    if key not in cache: cache[key] = ZB(rho, *sink(surf_raw(x, v)), th=math.pi / 3, smax=36)[0]
    return cache[key]
def wind(x0, x1, v0, v1, m=6):
    pts = [(x0 + (x1 - x0) * i / m, v0) for i in range(m)] + [(x1, v0 + (v1 - v0) * i / m) for i in range(m)] + \
          [(x1 - (x1 - x0) * i / m, v1) for i in range(m)] + [(x0, v1 - (v1 - v0) * i / m) for i in range(m)] + [(x0, v0)]
    vals = [Z(*p) for p in pts]; st = [np.angle(vals[i + 1] / vals[i]) for i in range(len(vals) - 1)]
    if max(abs(a) for a in st) > 1.5: return None          # under-resolved boundary -> refine
    return round(sum(st) / (2 * math.pi))
def locate(x0, x1, v0, v1, depth=0):
    w = wind(x0, x1, v0, v1)
    if w is None and depth < 14:
        xm, vm = (x0 + x1) / 2, (v0 + v1) / 2
        return sum((locate(*c, depth + 1) for c in ((x0, xm, v0, vm), (xm, x1, v0, vm), (x0, xm, vm, v1), (xm, x1, vm, v1))), [])
    if not w: return []
    if max(x1 - x0, v1 - v0) < 2e-5 or depth >= 14: return [((x0 + x1) / 2, (v0 + v1) / 2)]
    xm, vm = (x0 + x1) / 2, (v0 + v1) / 2
    return sum((locate(*c, depth + 1) for c in ((x0, xm, v0, vm), (xm, x1, v0, vm), (x0, xm, vm, v1), (xm, x1, vm, v1))), [])
xs = np.linspace(3.0, 2.08, 47); vs = np.linspace(-0.04, 1.04, 37)
found = []
for i in range(len(xs) - 1):
    for j in range(len(vs) - 1):
        for p in locate(xs[i + 1], xs[i], vs[j], vs[j + 1]):
            sol = fsolve(lambda q: (lambda w: [w.real, w.imag])(ZB(rho, *sink(surf_raw(q[0], q[1])), th=math.pi / 3, smax=40)[0]), list(p), xtol=1e-13)
            res = abs(ZB(rho, *sink(surf_raw(*sol)), th=math.pi / 3, smax=40)[0])
            tr = sink(surf_raw(*sol))
            if res < 1e-7 and not any(max(abs(a - b) for a, b in zip(tr, t2)) < 1e-6 for t2 in found): found.append(tr)
print("k = %d gamma = %.3f: %d distinct blind surfaces (bisection)" % (k, rho.imag, len(found)), flush=True)
for t in sorted(found): print("     traces (%.7f, %.7f, %.7f)" % t)
