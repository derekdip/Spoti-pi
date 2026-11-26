"""First-order term of the flat limit, Re s > 2:
   A^{s/2} Z_A(s) = Z_flat(s) + (A/12) s zeta(s) E(z, s/2 + 1) + o(A).
Checked at real s = 3, 4 at the hexagonal and square cone tori (z exact by symmetry)."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
mp.mp.dps = 25
xi = lambda w: mp.pi ** (-w / 2) * mp.gamma(w / 2) * mp.zeta(w)
def Estar(w, z, NT=40):
    x, y = mp.re(z), mp.im(z); tot = xi(2 * w) * y ** w + xi(2 * w - 1) * y ** (1 - w)
    for n in range(1, NT + 1):
        sig = mp.fsum(mp.mpf(d) ** (1 - 2 * w) for d in range(1, n + 1) if n % d == 0)
        tot += 4 * mp.sqrt(y) * mp.mpf(n) ** (w - 0.5) * sig * mp.besselk(w - 0.5, 2 * mp.pi * n * y) * mp.cos(2 * mp.pi * n * x)
    return tot
E = lambda w, z: Estar(w, z) / xi(2 * w)
Zflat = lambda s, z: 2 * mp.zeta(s) * E(s / 2, z)
pts = {"hexagonal": (mp.mpc(0.5, math.sqrt(3) / 2), lambda kap: (lambda t: (t, t, t))(max(r.real for r in np.roots([1, -3, 0, kap]) if abs(r.imag) < 1e-9))),
       "square": (mp.mpc(0, 1), lambda kap: (lambda x: (x, x, x * x / 2))(math.sqrt(4 + 2 * math.sqrt(4 - kap))))}
for s in (4.0,):
    for name, (z, trf) in pts.items():
        zf = Zflat(s, z); pred = s * mp.zeta(s) * E(s / 2 + 1, z) / 12
        print("s = %.0f %-9s: Z_flat = %.8f, predicted first-order coefficient (s/12) zeta(s) E(z, s/2+1) = %.6f" % (s, name, float(zf), float(pred)))
        for A in (0.4, 0.2, 0.1, 0.05):
            th = 2 * math.pi - A; kap = 2 - 2 * math.cos(th / 2)
            zA = ZB(complex(s), *trf(kap), th=0.0, smax=44, rho=False)[0].real * A ** (s / 2)
            print("     A = %.3f: (A^{s/2} Z_A - Z_flat)/A = %.6f   ratio to prediction %.4f" % (A, (zA - float(zf)) / A, (zA - float(zf)) / A / float(pred)), flush=True)
# s = rho_1: first-order coefficient (s/12) zeta(s) E(z, s/2+1) = 0, so (A^{rho/2} Z_A - Z_flat)/A -> 0
rho = mp.zetazero(1)
for name, (z, trf) in pts.items():
    zf = complex(2 * mp.pi ** (rho / 2) * Estar(rho / 2, z) / mp.gamma(rho / 2))
    print("s = rho_1 %-9s: Z_flat = %s; predicted first-order coefficient 0" % (name, zf))
    for A in (0.4, 0.2, 0.1, 0.05):
        th = 2 * math.pi - A; kap = 2 - 2 * math.cos(th / 2)
        zA = ZB(complex(rho), *trf(kap), th=math.pi / 3, smax=44)[0] * complex(mp.mpf(A) ** (rho / 2))
        print("     A = %.3f: |A^{rho/2} Z_A - Z_flat|/A = %.4f   /A^2 = %.4f" % (A, abs(zA - zf) / A, abs(zA - zf) / A ** 2), flush=True)
