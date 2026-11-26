"""Hyperbolic Fourier-Whittaker model of Z_B near the cusp of moduli.
Fenchel-Nielsen (l, tau) on cusped tori: traces x = 2cosh(l/2), y = 2coth(l/2)cosh(tau/2), z = 2coth(l/2)cosh((tau+l)/2).
Homogeneous model: N(p, q) = q n(p/q + tau/l), n(x) = W + 2 log cosh(x l/2), W = 2 log(2 coth(l/2)). Summing over p
coprime to q with Ramanujan sums c_q(m), and using sum_q c_q(m) q^-s = sigma_{1-s}(m)/zeta(s):
  Z_model(s) = 2 zeta(s) l^-s + 2 zeta(s-1) g(0) + 4 sum_{m>=1} sigma_{1-s}(m) g(m) cos(2 pi m tau / l),
  g(m) = int_R n(x)^-s e^{-2 pi i m x} dx   (continued in s).
This is the analogue of E*(z,s) = ... + 4 sqrt(y) sum n^{s-1/2} sigma_{1-2s}(n) K_{s-1/2}(2 pi n y) cos(2 pi n x)."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
mp.mp.dps = 25
def sink(t):
    t = list(t)
    while True:
        for i in range(3):
            j, k = [m for m in range(3) if m != i]; o = t[j] * t[k] - t[i]
            if o < t[i] - 1e-13: t[i] = o; break
        else: return tuple(sorted(t))
def traces(l, tau):
    ct = 1 / math.tanh(l / 2); return 2 * math.cosh(l / 2), 2 * ct * math.cosh(tau / 2), 2 * ct * math.cosh((tau + l) / 2)
def ghat(s, l, m):
    W = 2 * mp.log(2 / mp.tanh(l / 2)); A = W - 2 * mp.log(2)
    g = lambda u: (W + 2 * mp.log(mp.cosh(u))) ** (-s) - (A + 2 * u) ** (-s)
    if m == 0:
        I = mp.quad(g, [0, 1, 3, 8, 20, 40]) + A ** (1 - s) / (2 * (s - 1))
        return 2 / l * I
    k = 4 * mp.pi * m / l
    pts = [0] + [mp.pi * j / k for j in range(1, int(40 * k / mp.pi) + 1, max(1, int(k / mp.pi)))] + [40]
    I1 = mp.quad(lambda u: g(u) * mp.cos(k * u), sorted(set(pts)))
    def J(sg):  # int_0^inf (A+2u)^-s e^{i sg k u} du = (1/2) e^{-i sg k A/2} int_A^inf v^-s e^{i sg (k/2) v} dv
        p = -1j * sg * k / 2
        return 0.5 * mp.exp(-1j * sg * k * A / 2) * p ** (s - 1) * mp.gammainc(1 - s, p * A)
    return 2 / l * (I1 + (J(1) + J(-1)) / 2)
def sigma(s, m): return mp.fsum(mp.mpf(d) ** s for d in range(1, m + 1) if m % d == 0)
def model(s, l, taus, M):
    G = [ghat(s, l, m) for m in range(M + 1)]
    out = []
    for tau in taus:
        v = 2 * mp.zeta(s) * mp.mpf(l) ** (-s) + 2 * mp.zeta(s - 1) * G[0]
        v += 4 * mp.fsum(sigma(1 - s, m) * G[m] * mp.cos(2 * mp.pi * m * tau / l) for m in range(1, M + 1))
        out.append(complex(v))
    return np.array(out), [abs(complex(g)) for g in G]
if __name__ == "__main__":
    for k in (1, 4):
        rho = mp.zetazero(k)
        print("rho_%d (gamma = %.3f)" % (k, float(rho.imag)))
        for l in (0.3, 0.6, 1.0, 1.4):
            taus = [0.0, 0.25 * l, 0.5 * l]
            Zm, G = model(rho, l, taus, 8)
            for tau, zm in zip(taus, Zm):
                x, y, z = traces(l, tau); X = sink((x, y, z)); zt = ZB(complex(rho), *X, th=math.pi / 3)[0]
                print("   l = %.2f tau/l = %.2f: true %+.5f%+.5fj  model %+.5f%+.5fj  rel.err %.2e" % (l, tau / l, zt.real, zt.imag, zm.real, zm.imag, abs(zt - zm) / abs(zt)))
            print("      |g(m)|, m = 0..8: " + " ".join("%.1e" % g for g in G))
