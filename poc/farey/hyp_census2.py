"""Hyperbolic blind-surface census v2 and adaptive boundary winding.
Z is evaluated at the sink-normalised surface, so it is continuous across the mirror edges and Newton is unclamped.
A zero is counted if it lies in the closed mirror triangle (v in [0, 1]) after dedupe; zeros found outside are reflected
copies and are mapped back. Boundary winding: adaptive refinement until every phase step < 0.3 rad."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cusp_whittaker import sink
def surf_raw(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    d = (x * y) ** 2 - 4 * (x * x + y * y)
    if d < 0: y = lo; d = 0.0
    return x, y, (x * y - math.sqrt(d)) / 2
def Zf(rho, x, v, smax=36): return ZB(rho, *sink(surf_raw(x, v)), th=math.pi / 3, smax=smax)[0]
mode = sys.argv[1]; ks = [int(a) for a in sys.argv[2].split(",")]
for k in ks:
    rho = complex(mp.zetazero(k))
    if mode == "wind":
        XMIN = 2.03
        xa = np.concatenate([np.linspace(3.0, 2.2, 400), np.linspace(2.2, XMIN, 120)[1:]])
        pts = [(x, 1.0) for x in xa] + [(XMIN, v) for v in np.linspace(1, 0, 80)[1:]] + [(x, 0.0) for x in xa[::-1][1:]]
        Z = [Zf(rho, *p) for p in pts]
        for it in range(8):
            newp, newZ, changed = [pts[0]], [Z[0]], False
            for i in range(1, len(pts)):
                if abs(np.angle(Z[i] / Z[i - 1])) > 0.3:
                    mpnt = ((pts[i][0] + pts[i - 1][0]) / 2, (pts[i][1] + pts[i - 1][1]) / 2); newp.append(mpnt); newZ.append(Zf(rho, *mpnt)); changed = True
                newp.append(pts[i]); newZ.append(Z[i])
            pts, Z = newp, newZ
            if not changed: break
        Z = np.array(Z); st = np.angle(Z[1:] / Z[:-1])
        print("k = %d gamma = %.3f: boundary winding %.4f (points %d, max step %.3f, min |Z| %.4f)" % (k, rho.imag, st.sum() / (2 * math.pi), len(Z), np.abs(st).max(), np.abs(Z).min()), flush=True)
    else:
        xs = np.linspace(3.0, 2.08, 70); vs = np.linspace(-0.04, 1.04, 56)
        G = np.array([[Zf(rho, x, v) for v in vs] for x in xs])
        starts = []
        for i in range(len(xs) - 1):
            for j in range(len(vs) - 1):
                lp = [G[i, j], G[i + 1, j], G[i + 1, j + 1], G[i, j + 1], G[i, j]]
                if abs(sum(np.angle(lp[q + 1] / lp[q]) for q in range(4))) > math.pi: starts.append(((xs[i] + xs[i + 1]) / 2, (vs[j] + vs[j + 1]) / 2))
        F = lambda p: (lambda w: [w.real, w.imag])(Zf(rho, p[0], p[1], smax=40))
        found = []
        for p0 in starts:
            sol, info, ier, msg = fsolve(F, list(p0), xtol=1e-12, full_output=True); x, v = sol
            if ier != 1 or np.hypot(*F(sol)) > 1e-7 or not (2.0 < x <= 3.0): continue
            tr = sink(surf_raw(x, v))
            if not any(max(abs(a - b) for a, b in zip(tr, t2)) < 1e-6 for t2 in found): found.append(tr)
        print("k = %d gamma = %.3f: %d winding cells, %d distinct blind surfaces" % (k, rho.imag, len(starts), len(found)), flush=True)
        for t in sorted(found): print("     traces (%.7f, %.7f, %.7f)" % t)
