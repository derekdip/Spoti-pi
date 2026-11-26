"""Size of A^{s/2} Z_A(s) - Z_flat(s) inside the critical strip (real s), hexagonal cone torus (z exact).
Prediction: local exponent min(1, (s+1)/2) (first-order term vs staircase term), log at s = 1.
Also prints the ratio to the first-order formula (A/12) s zeta(s) E(z, s/2+1)."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
exec(open("poc/farey/flat_first_order.py").read().split("pts = {")[0])
z = mp.mpc(0.5, math.sqrt(3) / 2)
trf = lambda kap: (lambda t: (t, t, t))(max(r.real for r in np.roots([1, -3, 0, kap]) if abs(r.imag) < 1e-9))
for s in [float(a) for a in sys.argv[1].split(",")]:
    zf = float(Zflat(s, z)); fo = float(s * mp.zeta(s) * E(s / 2 + 1, z) / 12)
    prev = None; line = []
    for A in (0.4, 0.2, 0.1, 0.05, 0.025):
        th = 2 * math.pi - A; kap = 2 - 2 * math.cos(th / 2)
        zA = ZB(complex(s), *trf(kap), th=0.0, smax=44, rho=False)[0].real * A ** (s / 2)
        d = zA - zf
        loc = "" if prev is None else " exp %.3f" % (math.log(abs(prev / d)) / math.log(2))
        line.append("A=%.3f: diff/A %.4f (vs first-order %.4f)%s" % (A, d / A, fo, loc)); prev = d
    print("s = %.2f (predicted exponent %.3f), Z_flat = %.6f:\n   " % (s, min(1, (s + 1) / 2), zf) + "\n   ".join(line), flush=True)
