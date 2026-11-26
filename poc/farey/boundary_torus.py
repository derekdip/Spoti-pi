"""Riemann zeros in the simple-geodesic count of a one-holed torus with geodesic boundary (the building block of every
surface of genus >= 2). Fricke: x^2 + y^2 + z^2 - xyz = 2 - 2 cosh(Lb/2). Exact count of interior simple geodesics
up to 3000, spectral projection of E_P/sqrt R onto R^{i gamma_k}, against c_k = Z_B(rho_k)/(2 rho_k zeta'(rho_k))."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cell_count_general import Torus
LMAX = 3000.0
def sink(t):
    t = list(t)
    while True:
        for i in range(3):
            j, k = [m for m in range(3) if m != i]; o = t[j] * t[k] - t[i]
            if o < t[i] - 1e-13: t[i] = o; break
        else: return tuple(sorted(t))
def lengths(x, y, z):
    def L(lt): return 2 * math.acosh(math.exp(lt) / 2) if lt < 30 else 2 * lt - 2 * math.exp(-2 * lt)
    lx, ly, lz = math.log(x), math.log(y), math.log(z)
    out = [L(lx), L(ly), L(lz)]; st = [(lx, lz, ly), (lz, ly, lx), (ly, lx, lz)]
    while st:
        lu, lw, ld = st.pop(); lm = lu + lw + math.log1p(-math.exp(ld - lu - lw)); l = L(lm)
        if l > LMAX: continue
        out.append(l); st += [(lu, lm, lw), (lm, lw, lu)]
    return np.sort(np.array(out))
GAM = [float(mp.zetazero(k).imag) for k in range(1, 9)]
for Lb, x, y in ((2.0, 2.9, 3.3), (6.0, 4.0, 5.0)):
    kap = 2 - 2 * math.cosh(Lb / 2)
    z = (x * y + math.sqrt((x * y) ** 2 - 4 * (x * x + y * y - kap))) / 2
    tr = sink((x, y, z)); X = Torus(*tr)
    print("boundary length %.1f: sink traces (%.6f, %.6f, %.6f), Fricke residual %.1e, Area(B) = %.6f" % (Lb, *tr, tr[0]**2+tr[1]**2+tr[2]**2-tr[0]*tr[1]*tr[2]-kap, X.area))
    Ns = lengths(*tr); Rs = np.exp(np.linspace(math.log(50), math.log(LMAX * 0.999), 20000)); t = np.log(Rs)
    f = (np.searchsorted(Ns, Rs, side="right") - 3 / math.pi ** 2 * X.area * Rs ** 2) / np.sqrt(Rs)
    w = 0.5 - 0.5 * np.cos(2 * math.pi * (t - t[0]) / (t[-1] - t[0]))
    print("   %d simple geodesics up to %g; rms E_P/sqrt R = %.3f" % (len(Ns), LMAX, f.std()))
    for k, g in enumerate(GAM, 1):
        rho = complex(mp.zetazero(k)); zb = ZB(rho, *tr, th=math.pi / 3)[0]; c = zb / (2 * rho * complex(mp.zeta(rho, derivative=1)))
        proj = np.sum(f * w * np.exp(-1j * g * t)) / np.sum(w)
        print("   gamma_%d = %6.3f: measured %.4f  predicted |c_k| %.4f   phase measured %+.3f predicted %+.3f" % (k, g, abs(proj), abs(c), np.angle(proj), np.angle(c)))
