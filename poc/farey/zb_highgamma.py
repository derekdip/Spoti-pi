"""Z_B(rho_k) at large gamma on the modular torus with the vectorised evaluator: ray theta = pi/2 - 7 ln10/gamma
(about 7 digits lost), dense Gauss-Legendre panels (length <= 1.5) out to r = R(theta) so that e^{-l_min r cos theta}
< 1e-18. Validated against the 20 mpmath values (zeros_angle_0p785.npy), then extended."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); import zb_moduli as zm
def setpanels(th, lmin):
    rmax = 45 / (lmin * math.cos(th)) + 5
    edges = [zm.T0, 0.25, 1.0] + list(np.arange(2.0, rmax, 1.5)) + [rmax]
    g = np.polynomial.legendre.leggauss(32)
    zm.NODES = np.concatenate([(b - a) / 2 * g[0] + (a + b) / 2 for a, b in zip(edges[:-1], edges[1:])])
    zm.WTS = np.concatenate([(b - a) / 2 * g[1] for a, b in zip(edges[:-1], edges[1:])])
def ZBk(k, tr=(3.0, 3.0, 3.0)):
    rho = complex(mp.zetazero(k)); g = rho.imag
    th = max(math.pi / 3, math.pi / 2 - 7 * math.log(10) / g)
    setpanels(th, 2 * math.acosh(min(tr) / 2))
    return rho, zm.ZB(rho, *tr, th=th, smax=40)[0]
if __name__ == "__main__":
    ref = np.load("poc/farey/zeros_angle_0p785.npy")
    for k in (1, 5, 10, 15, 20):
        rho, z = ZBk(k); print("k = %2d: fast %+.8f%+.8fj   mpmath %+.8f%+.8fj   |diff| %.1e" % (k, z.real, z.imag, ref[k - 1, 2].real, ref[k - 1, 2].imag, abs(z - ref[k - 1, 2])), flush=True)
    rows = []
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    for k in range(1, K + 1):
        rho, z = ZBk(k); zp = complex(mp.zeta(rho, derivative=1)); rows.append((rho.imag, abs(z), abs(zp), abs(z / (2 * rho * zp))))
    r = np.array(rows); np.save("poc/farey/zb_highgamma.npy", r); g = r[:, 0]
    for lo, hi in ((0, 50), (50, 100), (100, 150), (150, 200), (200, 250), (250, 300)):
        m = (g >= lo) & (g < hi)
        if m.sum() > 2: print("gamma in [%3d,%3d): <|Z_B|^2>/gamma = %.3f   <|Z_B|^2> = %.1f   (%d zeros)" % (lo, hi, np.mean(r[m, 1] ** 2 / g[m]), np.mean(r[m, 1] ** 2), m.sum()))
    S = np.cumsum(2 * r[:, 3] ** 2)
    for T in (50, 100, 150, 200, 250):
        i = np.searchsorted(g, T) - 1
        if 0 <= i < len(g): print("  2 sum_{gamma<%d} |c|^2 = %.4f" % (T, S[i]))
