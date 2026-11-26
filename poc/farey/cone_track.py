"""Track the blind surface of rho_k along the cone-angle deformation x^2+y^2+z^2-xyz = kappa (kappa = 2 - 2cos(theta/2)):
kappa = 0 cusped hyperbolic, kappa -> 4 rescaled flat. Unknowns: sink lengths (a, b); c from the Fricke relation (smaller
root). Report scale-invariant shape (b/a, c/a); the flat blind torus z_flat has shape (|z|, |z-1|)."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cusp_whittaker import sink
k = int(sys.argv[1]); x0 = [float(v) for v in sys.argv[2].split(",")]; zflat = complex(sys.argv[3])
rho = complex(mp.zetazero(k))
def tr3(a, b, kap):
    x, y = 2 * math.cosh(a / 2), 2 * math.cosh(b / 2); d = (x * y) ** 2 - 4 * (x * x + y * y - kap)
    return x, y, (x * y - math.sqrt(max(d, 0))) / 2
def Z(p, kap):
    t = sink(tr3(p[0], p[1], kap)); return ZB(rho, *t, th=math.pi / 3, smax=40)[0]
a0, b0 = 2 * math.acosh(x0[0] / 2), 2 * math.acosh(x0[1] / 2); p = [a0, b0]
print("flat target shape (|z|, |z-1|) = (%.4f, %.4f)" % (abs(zflat), abs(zflat - 1)))
prev_area = 2 * math.pi
for kap in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.3, 3.6, 3.8, 3.9, 3.95, 3.98]:
    th = 2 * math.acos(1 - kap / 2); area = 2 * math.pi - th; sc = math.sqrt(area / prev_area) if kap > 1.4 else 1.0; prev_area = area
    p = [p[0] * sc, p[1] * sc]
    sol, info, ier, msg = fsolve(lambda q: (lambda w: [w.real, w.imag])(Z(q, kap)), p, xtol=1e-12, full_output=True)
    p = list(sol); res = abs(Z(p, kap)); t = sink(tr3(p[0], p[1], kap))
    a, b, c = sorted(2 * math.acosh(v / 2) for v in t)
    print("kappa %.2f (cone angle %6.2f deg, area %.3f): |Z| %.1e  lengths (%.4f, %.4f, %.4f)  shape (%.4f, %.4f)" % (
        kap, math.degrees(th), area, res, a, b, c, b / a, c / a), flush=True)
