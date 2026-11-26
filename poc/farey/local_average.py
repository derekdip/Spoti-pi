"""Local 2D average over the cusped one-holed tori near the modular torus: uniform in twist, Gaussian bump in a = l(alpha).
Computes Pbar(R) = < sum_{simple gamma} (R - l_gamma)_+ > on a fine R grid, for bump widths sigma_a in SIGMAS."""
import math, sys, numpy as np
RMAX = 150.0; H = 0.004
Rg = np.arange(0.0, RMAX + 1e-9, 0.02)
def twist_avg(a):
    lam = math.exp(a / 2); K = 1 / math.tanh(a / 2)
    def tr(r, q, taus):
        y = 2 * K * np.cosh(taus / 2); z = 2 * K * np.cosh((taus + a) / 2)
        p = (z - y / lam) / (lam - 1 / lam); s = y - p; b10 = p * s - 1
        m00 = np.ones_like(taus); m01 = np.zeros_like(taus); m10 = np.zeros_like(taus); m11 = np.ones_like(taus)
        for i in range(1, q + 1):
            m00, m01, m10, m11 = m00 * p + m01 * b10, m00 + m01 * s, m10 * p + m11 * b10, m10 + m11 * s
            k = (i * r) // q - ((i - 1) * r) // q
            if k:
                f = lam ** k; m00, m01, m10, m11 = m00 * f, m01 / f, m10 * f, m11 / f
        return np.abs(m00 + m11)
    F = np.maximum(Rg - a, 0.0)
    for q in range(1, 1000):
        hit = False
        for r in range(q):
            if math.gcd(r, q) != 1: continue
            c = -(r / q) * a - a / 2; T = RMAX / q + 6
            taus = np.arange(c - T, c + T, H)
            l = 2 * np.arccosh(np.maximum(tr(r, q, taus), 2.0) / 2)
            if l.min() > RMAX: continue
            hit = True
            ls = np.sort(l[l < RMAX]); cs = np.concatenate([[0], np.cumsum(ls)]); n = np.searchsorted(ls, Rg)
            F += (n * Rg - cs[n]) * H / a
        if not hit: break
    return F
a0 = 2 * math.log((3 + math.sqrt(5)) / 2)
SIGMAS = [float(x) for x in sys.argv[1:]] or [0.0, 0.03, 0.06]
xg, wg = np.polynomial.hermite_e.hermegauss(14); wg = wg / wg.sum()
out = {"R": Rg}
for sg in SIGMAS:
    if sg == 0:
        P = twist_avg(a0)
    else:
        P = sum(w * twist_avg(a0 + sg * x) for x, w in zip(xg, wg))
    out["s%.3f" % sg] = P
    print("sigma_a = %.3f done; Pbar(150) = %.4f" % (sg, P[-1]), flush=True)
np.savez("poc/farey/local_average.npz", **out)
