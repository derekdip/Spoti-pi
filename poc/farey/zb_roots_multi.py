"""Newton-refine every winding cell of zb_scan for k = 1..6; keep genuine zeros (|Z| < 1e-8 inside the domain), dedupe,
record degree sign (det of the Jacobian in (x, v))."""
import sys, math, numpy as np, mpmath as mp, re, ast
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
def surf(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    z = (x * y - math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y), 0))) / 2
    return x, y, z
xs = 2 + 1 / np.linspace(1, 14, 40); vs = np.linspace(0, 1, 30)
starts = {1: [(1, 10)]}
for line in open("poc/farey/zb_scan_multi.log"):
    m = re.match(r"k=(\d): grid cells with nonzero winding: (.*)", line)
    if m: starts[int(m.group(1))] = [(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+), -?\d+", m.group(2))]
for k in sorted(starts):
    rho = complex(mp.zetazero(k)); found = []
    F = lambda p: (lambda w: [w.real, w.imag])(ZB(rho, *surf(min(max(p[0], 2.02), 3.0), min(max(p[1], 0.0), 1.0)), th=math.pi / 3, smax=40)[0])
    for i, j in starts[k]:
        p0 = [(xs[i] + xs[i + 1]) / 2, (vs[j] + vs[j + 1]) / 2]
        sol, info, ier, msg = fsolve(F, p0, full_output=True, xtol=1e-12)
        x, v = sol; res = np.hypot(*F(sol))
        inside = 2.02 < x <= 3.0 and 0.0 <= v <= 1.0
        if res < 1e-7 and inside and not any(abs(x - a) < 1e-6 and abs(v - b) < 1e-6 for a, b, _ in found):
            h = 1e-6; J = np.array([[(F([x + h * (q == 0), v + h * (q == 1)])[r] - F([x - h * (q == 0), v - h * (q == 1)])[r]) / (2 * h) for q in range(2)] for r in range(2)])
            found.append((x, v, np.sign(np.linalg.det(J))))
    print("k = %d (gamma = %.3f): %d zero-blind surfaces" % (k, rho.imag, len(found)))
    for x, v, sg in sorted(found):
        t = surf(x, v); print("    traces (%.8f, %.8f, %.8f)  v = %.6f  degree %+d" % (t + (v, sg)))
