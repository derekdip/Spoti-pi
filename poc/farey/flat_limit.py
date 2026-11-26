"""Flat limit of the stable-norm zeta: for cone tori x^2+y^2+z^2-xyz = kappa, area A = 2 pi - theta, check
A^{rho/2} Z_{B,kappa}(rho) -> Z_flat(rho; z) = 2 pi^{rho/2} E*(z, rho/2)/Gamma(rho/2) as kappa -> 4,
at the hexagonal (x = y = z) and square (x = y, z = x^2/2) points."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
exec(open("poc/farey/flat_blind.py").read().split("res = []")[0])
for k in (1, 2):
    rho = mp.zetazero(k); s = rho / 2; cf = coefs(s); c2 = xi(2 - 2 * s)
    for name, zf, trf in (("hexagonal", mp.mpc(0.5, math.sqrt(3) / 2), lambda kap: (lambda t: (t, t, t))(max(r.real for r in np.roots([1, -3, 0, kap]) if abs(r.imag) < 1e-9))),
                          ("square", mp.mpc(0, 1), lambda kap: (lambda x: (x, x, x * x / 2))(math.sqrt(4 + 2 * math.sqrt(4 - kap))))):
        flat = 2 * mp.pi ** (rho / 2) * Estar(s, float(zf.real), float(zf.imag), cf, c2) / mp.gamma(rho / 2)
        print("rho_%d %s: flat value %s" % (k, name, mp.nstr(flat, 8)))
        for kap in (3.0, 3.6, 3.9, 3.96, 3.99):
            th = 2 * math.acos(1 - kap / 2); A = 2 * math.pi - th; t = trf(kap)
            z = ZB(complex(rho), *t, th=math.pi / 3, smax=40)[0] * complex(mp.mpf(A) ** (rho / 2))
            print("   kappa %.2f (area %.3f): A^{rho/2} Z = %+.5f%+.5fj   |diff|/|flat| = %.3e" % (kap, A, z.real, z.imag, abs(z - complex(flat)) / abs(complex(flat))), flush=True)
