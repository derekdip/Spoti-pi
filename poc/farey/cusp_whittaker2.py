"""Exact-up-to-deficiency twist-Fourier expansion of Z_B on cusped tori, Fenchel-Nielsen (l, tau).
The stable norm on the line q = 1 is the piecewise-linear interpolation L(x) of the exact fan lengths
f_k = l(k alpha + beta) = 2 acosh(coth(l/2) cosh((tau + k l)/2)), up to corner deficiencies of size about e^{-2W}.
By homogeneity N(p, q) = q L(p/q), and Poisson summation over p coprime to q plus Ramanujan sums give
  Z(s) = 2 zeta(s) l^-s + 2 zeta(s-1) h(0) + 2 sum_{m != 0} sigma_{1-s}(|m|) h(m),   h(m) = int_R L(x)^-s e^{-2 pi i m x} dx.
h(m): 24-point Gauss-Legendre per unit segment for |k| <= K, analytic incomplete-gamma tails beyond."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cusp_whittaker import sink, traces, sigma
gx, gw = np.polynomial.legendre.leggauss(24); gx = (gx + 1) / 2; gw = gw / 2
def fan(l, tau, k): return 2 * np.arccosh(np.cosh((tau + k * l) / 2) / np.tanh(l / 2))
def hvec(s, l, tau, M, K=None):
    if K is None: K = int(40 / l) + 5
    ks = np.arange(-K, K); a = fan(l, tau, ks); b = fan(l, tau, ks + 1) - a
    X = ks[:, None] + gx[None, :]; Lx = a[:, None] + b[:, None] * gx[None, :]
    base = Lx ** (-s) * gw[None, :]
    out = []
    for m in range(-M, M + 1):
        h = complex(np.sum(base * np.exp(-2j * math.pi * m * X)))
        # tails: x > K: L = fK + l (x - K) (exactly linear up to e^{-K l}); x < -K: L = f_{-K} + l (-K - x)
        for sgn, x0, f0 in ((1, K, fan(l, tau, K)), (-1, -K, fan(l, tau, -K))):
            # int_0^inf (f0 + l u)^-s e^{-2 pi i m (x0 + sgn u)} du
            sm = mp.mpc(s)
            if m == 0: t = mp.mpf(f0) ** (1 - sm) / (mp.mpf(l) * (sm - 1))
            else:
                p = 2j * mp.pi * m * sgn / l            # e^{-2 pi i m sgn u} = e^{-p (v - f0)}, v = f0 + l u
                t = mp.exp(p * f0) / l * p ** (sm - 1) * mp.gammainc(1 - sm, p * f0)
            h += complex(mp.exp(-2j * mp.pi * m * x0) * t)
        out.append(h)
    return np.array(out)
def model(s, l, tau, M=6):
    H = hvec(s, l, tau, M); sm = mp.mpc(s)
    v = 2 * mp.zeta(sm) * mp.mpf(l) ** (-sm) + 2 * mp.zeta(sm - 1) * H[M]
    for m in range(1, M + 1): v += 2 * sigma(1 - sm, m) * (H[M + m] + H[M - m])
    return complex(v), np.abs(H[M:])
if __name__ == "__main__":
    for k in (1, 4, 10):
        rho = complex(mp.zetazero(k)); print("rho_%d (gamma = %.3f)" % (k, rho.imag))
        for l in (0.3, 0.6, 1.0, 1.4, 1.8):
            for tf in (0.0, 0.25, 0.5):
                tau = tf * l; zm, Hm = model(rho, l, tau)
                zt = ZB(rho, *sink(traces(l, tau)), th=math.pi / 3)[0]
                print("   l = %.1f tau/l = %.2f: true %+.6f%+.6fj  model %+.6f%+.6fj  rel.err %.1e" % (l, tf, zt.real, zt.imag, zm.real, zm.imag, abs(zt - zm) / abs(zt)), flush=True)
            print("      |h(m)| m = 0..6: " + " ".join("%.1e" % v for v in Hm))
