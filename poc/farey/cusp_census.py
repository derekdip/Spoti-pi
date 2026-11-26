"""Census of blind surfaces in the cusp region l <= LMAX of moduli (where the twist-Fourier expansion is accurate),
for large gamma, using cusp_whittaker2.model (64-point GL). Domain: l in [0.12, LMAX], tau/l in [0, 1/2] (mirror quotient).
Records: number of zeros, smallest systole, and the m = 1 stationary-phase threshold l_1 solving gamma l M(W) = 2 pi."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import brentq
sys.path.insert(0, "poc/farey"); import cusp_whittaker2 as cw
gx, gw = np.polynomial.legendre.leggauss(64); cw.gx = (gx + 1) / 2; cw.gw = gw / 2
LMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
def Mfun(W):
    u = np.linspace(0.01, 12, 4000); return np.max(np.tanh(u) / (W + 2 * np.log(np.cosh(u))))
def thresh(g, m=1):
    F = lambda l: g * l * Mfun(2 * math.log(2 / math.tanh(l / 2))) - 2 * math.pi * m
    try: return brentq(F, 0.01, 3.0)
    except ValueError: return float("nan")
for k in [int(a) for a in sys.argv[1].split(",")]:
    rho = complex(mp.zetazero(k)); g = rho.imag
    Mh = int(g * LMAX * 0.3 / (2 * math.pi)) + 6
    ls = np.exp(np.linspace(math.log(0.12), math.log(LMAX), 70)); fs = np.linspace(0, 0.5, 36)
    Z = np.array([[cw.model(rho, l, f * l, M=Mh)[0] for f in fs] for l in ls])
    zs = []
    for i in range(len(ls) - 1):
        for j in range(len(fs) - 1):
            lp = [Z[i, j], Z[i + 1, j], Z[i + 1, j + 1], Z[i, j + 1], Z[i, j]]
            w = sum(np.angle(lp[q + 1] / lp[q]) for q in range(4))
            if abs(w) > math.pi: zs.append((math.sqrt(ls[i] * ls[i + 1]), (fs[j] + fs[j + 1]) / 2, int(np.sign(w))))
    lmin = min((z[0] for z in zs), default=float("nan"))
    print("k = %3d gamma = %7.2f: %3d zeros with l <= %.2f (signed %+d); smallest systole %.3f; m=1 threshold %.3f, m=2 %.3f; harmonics %d; zeros/gamma^2 = %.4f" % (
        k, g, len(zs), LMAX, sum(z[2] for z in zs), lmin, thresh(g), thresh(g, 2), Mh, len(zs) / g ** 2), flush=True)
