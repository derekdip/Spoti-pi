"""Robust continuation of a blind surface along kappa in [0, KMAX]: predictor (secant in kappa), Newton corrector,
accept only if |Z| < 1e-9 and the correction is small relative to the step; otherwise halve the step."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cusp_whittaker import sink
k = int(sys.argv[1]); x0 = [float(v) for v in sys.argv[2].split(",")]; zflat = complex(sys.argv[3]); KMAX = 3.985
rho = complex(mp.zetazero(k))
def tr3(a, b, kap):
    x, y = 2 * math.cosh(a / 2), 2 * math.cosh(b / 2); d = (x * y) ** 2 - 4 * (x * x + y * y - kap)
    return x, y, (x * y - math.sqrt(max(d, 0))) / 2
def F(q, kap):
    w = ZB(rho, *sink(tr3(math.exp(q[0]), math.exp(q[1]), kap)), th=math.pi / 3, smax=40)[0]; return [w.real, w.imag]
def shape(q, kap):
    a, b, c = sorted(2 * math.acosh(v / 2) for v in sink(tr3(math.exp(q[0]), math.exp(q[1]), kap))); return b / a, c / a
p = np.log(np.array([2 * math.acosh(x0[0] / 2), 2 * math.acosh(x0[1] / 2)])); kap = 0.0; h = 0.05; prev = None
print("flat target shape (%.4f, %.4f)" % (abs(zflat), abs(zflat - 1)))
print("kappa %.4f shape (%.4f, %.4f)" % ((kap,) + shape(p, kap)), flush=True)
nextprint = 0.25
while kap < KMAX - 1e-9:
    hk = min(h, KMAX - kap)
    pred = p + (p - prev[0]) / (kap - prev[1]) * hk if prev is not None else p.copy()
    sol = fsolve(lambda q: F(q, kap + hk), pred, xtol=1e-12)
    ok = np.hypot(*F(sol, kap + hk)) < 1e-9 and np.linalg.norm(sol - pred) < 0.004 + 0.3 * np.linalg.norm(pred - p)
    if ok:
        prev = (p, kap); p = sol; kap += hk; h = min(h * 1.4, 0.1 if kap < 3.0 else 0.025)
        if kap >= nextprint - 1e-9 or kap >= KMAX - 1e-9:
            A = 2 * math.pi - 2 * math.acos(1 - kap / 2)
            print("kappa %.4f area %.4f shape (%.4f, %.4f)" % ((kap, A) + shape(p, kap)), flush=True); nextprint = kap + 0.25 if kap < 3.5 else kap + 0.05
    else:
        h /= 2
        if h < 1e-4: print("lost the zero at kappa %.4f" % kap); break
