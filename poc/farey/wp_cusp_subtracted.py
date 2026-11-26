"""Moduli average of Z_B(-m) at L = 0 with the cusp handled exactly:
   int_M Z = int_{l >= l1} (2D Gauss, smooth) + int_0^{l1} P_m(l) dl  (cusp model; twist window width l, ratio checked),
 where P_m(l) = l (Z(-m) - 2 zeta(-m) l^m) from the strip-norm asymptotics (matches cell sums to 4-5 digits for l <= 0.1)."""
import math, sys, numpy as np, mpmath as mp
sys.path.insert(0, '.'); sys.argv = ["x", "check"]
src = open("wp_zeta_neg.py").read().split("print(\"\\nmodular")[0].replace('sys.path.insert(0, __file__.rsplit("/", 1)[0])', '')
exec(src)
import wp_average as W
exec(open("cusp_model.py").read().split("data = {")[0])
mu, C, tau_interval, lmax = W.domain(0.0)
def integrate_from(l1, f, nl=48, nt=20):
    xl, wl = np.polynomial.legendre.leggauss(nl); xt, wt = np.polynomial.legendre.leggauss(nt)
    vol = 0.0; I = 0.0
    for x, w in zip(xl, wl):
        l = l1 + (lmax - l1) * (x + 1) / 2; dl = (lmax - l1) * w / 2
        iv = tau_interval(l)
        if iv is None: continue
        t0, t1 = iv
        for y, v in zip(xt, wt):
            tau = t0 + (t1 - t0) * (y + 1) / 2; dt = (t1 - t0) * v / 2
            a = 2 * math.cosh(l / 2); b = C(l) * math.cosh(tau / 2)
            vol += 2 * dl * dt; I += 2 * dl * dt * f(a, b)
    return vol, I
l1 = 0.05
print("twist-window check at small l: width / l =", [round((lambda iv: 2 * (iv[1] - iv[0]))(tau_interval(l)) / l, 6) for l in (0.001, 0.01, 0.05)])
for m in (0, 2, 4):
    vol_hi, I_hi = integrate_from(l1, lambda a, b, m=m: ZB_neg(a, b, 0.0, m)[0])
    zm = float(mp.zeta(-m)) if m else -0.5
    cusp = float(mp.quad(lambda l: P(m, l) + 2 * zm * l ** (m + 1) * (1 if m else 1), [mp.mpf(0), mp.mpf("1e-8"), mp.mpf("1e-4"), mp.mpf("0.01"), mp.mpf(l1)]))
    vol_lo = l1 ** 2 / 2   # int_0^{l1} l dl  (window width l)
    vol = vol_hi + vol_lo; I = I_hi + cusp
    print("m = %d: Vol = %.6f (pred %.6f);  smooth part %.6f + cusp part %.6f = %.6f;  average %.6f" % (m, vol, math.pi ** 2 / 6, I_hi, cusp, I, I / vol), flush=True)
