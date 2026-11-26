"""Refine the zero of Z_B(rho_1) on moduli space found by zb_scan.py; validate the general-surface formula at real s
against the direct sum 2 zeta(s) sum_{simple} l^-s; stability in smax and ray angle."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
rho = complex(mp.zetazero(1))
def surf(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    z = (x * y - math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y), 0))) / 2
    return x, y, z
F = lambda p: (lambda w: [w.real, w.imag])(ZB(rho, *surf(*p), th=math.pi / 3, smax=40)[0])
sol = fsolve(F, [2.68, 0.36], xtol=1e-13); x, y, z = surf(*sol)
print("root: x = %.12f v = %.12f -> traces (%.12f, %.12f, %.12f), Markoff check %.2e" % (sol[0], sol[1], x, y, z, x*x+y*y+z*z-x*y*z))
L = lambda t: 2 * math.acosh(t / 2); print("sink lengths (%.10f, %.10f, %.10f)" % (L(x), L(y), L(z)))
for th in (math.pi / 4, math.pi / 3, 0.4 * math.pi):
    for smax in (36, 44, 50):
        v, n = ZB(rho, x, y, z, th=th, smax=smax); print("  theta %.3f smax %2d: Z_B(rho_1) = %+.3e %+.3ej  (%d cells)" % (th, smax, v.real, v.imag, n))
# Jacobian: transversality (nonzero determinant = isolated, nondegenerate zero)
h = 1e-6; J = np.array([[(F([sol[0] + h * (k == 0), sol[1] + h * (k == 1)])[i] - F([sol[0] - h * (k == 0), sol[1] - h * (k == 1)])[i]) / (2 * h) for k in range(2)] for i in range(2)])
print("Jacobian d(Re,Im)/d(x,v) =\n", J, "\n det = %.4f (sign = local degree)" % np.linalg.det(J))
# validation at real s: direct sum over simple geodesics
mp.mp.dps = 40; lens = [L(x), L(y), L(z)]; st = [(mp.mpf(x), mp.mpf(z), mp.mpf(y)), (mp.mpf(z), mp.mpf(y), mp.mpf(x)), (mp.mpf(y), mp.mpf(x), mp.mpf(z))]
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = float(2 * mp.acosh(tm / 2))
    if lm > 60: continue
    lens.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
lens = np.array(lens); mp.mp.dps = 15
for s in (2.6, 3.0, 4.0):
    direct = 2 * float(mp.zeta(s)) * np.sum(lens ** -s)
    v, n = ZB(complex(s), x, y, z, th=0.0, smax=44, rho=False)
    print("s = %.1f: direct sum %.10f   cell formula %.10f%+.1ej" % (s, direct, v.real, v.imag))
np.save("poc/farey/zb_root.npy", np.array([x, y, z]))
