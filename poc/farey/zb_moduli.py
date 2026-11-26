"""Z_B(s) at a nontrivial zeta zero for a general cusped once-punctured torus, vectorised in double precision.
Rooted at the Bowditch sink (x, y, z) (lengths a, b, c):
  Z_B(s) = 2 zeta(s)(a^-s + b^-s + c^-s) + 2[zeta_2(s; a, c) + zeta_2(s; c, b) + zeta_2(s; b, a)] + 2 sum_cells Delta(s),
zeta_2(s; p, q) = sum_{alpha, beta >= 1} (alpha p + beta q)^-s, Delta from D(t) = e^{ct}(e^{dt} - 1)/prod(e^{xt} - 1).
At s = rho the ray term vanishes. Each piece is (1/Gamma(s)) int_0^inf t^{s-1} f(t) dt, computed on the ray arg t = THETA:
Laurent series (Bernoulli) on |t| < T0, Gauss-Legendre beyond. Cells truncated at u + w > SMAX (tail ~ S^6 e^-S)."""
import numpy as np, mpmath as mp, math
KS = 34; T0 = 0.05
BNf = np.array([float(mp.bernoulli(n)) for n in range(KS + 2)]); BNf[1] = -0.5
FACT = np.array([math.factorial(n) for n in range(KS + 2)], dtype=float)
def hser(p):                      # coefficients of t^m, m = -1..KS-1 for 1/(e^{pt}-1); p: array
    n = np.arange(KS + 1); return BNf[n] * np.power.outer(p, n - 1.0) / FACT[n]     # index i <-> t^{i-1}
def gser(p, q):                   # t^k, k = -2..KS-2 -> index k+2
    A, B = hser(p), hser(q); out = np.zeros((len(p), KS + 1))
    for i in range(KS + 1): out[:, i:] += A[:, [i]] * B[:, :KS + 1 - i]
    return out
_gl = np.polynomial.legendre.leggauss(64)
PANELS = [T0, 0.25, 1, 3, 8, 20, 50, 120, 300]
NODES = np.concatenate([(b - a) / 2 * _gl[0] + (a + b) / 2 for a, b in zip(PANELS[:-1], PANELS[1:])])
WTS = np.concatenate([(b - a) / 2 * _gl[1] for a, b in zip(PANELS[:-1], PANELS[1:])])
def mellin(s, coef, ftab, th):    # coef: (n, KS+1) Laurent coefs t^{k}, k=-2..; ftab: f on ray nodes (n, nodes)
    e = np.exp(1j * th); z0 = T0 * e; k = np.arange(-2, KS - 1)
    ser = (coef * (z0 ** (s + k) / (s + k))).sum(1)
    tt = NODES * e
    quad = (ftab * (tt ** (s - 1) * e * WTS)).sum(1)
    return ser + quad
def em(x, t): return np.exp(-np.multiply.outer(x, t))
def tree(x, y, z, smax):
    mp.mp.dps = 60
    L = lambda tr: 2 * mp.acosh(tr / 2)
    cells = []; st = [(mp.mpf(x), mp.mpf(z), mp.mpf(y)), (mp.mpf(z), mp.mpf(y), mp.mpf(x)), (mp.mpf(y), mp.mpf(x), mp.mpf(z))]
    while st:
        tu, tw, td = st.pop(); a, b = L(tu), L(tw)
        if a + b > smax: continue
        tm = tu * tw - td; c = L(tm); cells.append((float(a), float(b), float(c), float(a + b - c)))
        st += [(tu, tm, tw), (tm, tw, tu)]
    mp.mp.dps = 15
    return np.array(cells)
def ZB(s, x, y, z, th=math.pi / 4, smax=44.0, rho=True):
    L = lambda tr: 2 * math.acosh(tr / 2)
    a, b, c = L(x), L(y), L(z)
    tt = NODES * np.exp(1j * th)
    P = np.array([a, c, b]); Q = np.array([c, b, a])
    gc = gser(P, Q); gf = em(P, tt) * em(Q, tt) / ((1 - em(P, tt)) * (1 - em(Q, tt)))
    tot = 2 * mellin(s, gc, gf, th).sum()
    cl = tree(x, y, z, smax)
    for blk in range(0, len(cl), 4000):
        u, w, m, d = cl[blk:blk + 4000].T
        coef = gser(u, m) + gser(m, w) - gser(u, w); hm = hser(m); coef[:, 1:] += hm[:, :KS]      # h index i(t^{i-1}) -> k = i-1 -> col i+1
        f = em(m, tt) * (-np.expm1(-np.multiply.outer(d, tt))) / ((1 - em(u, tt)) * (1 - em(w, tt)) * (1 - em(m, tt)))
        tot += 2 * mellin(s, coef, f, th).sum()
    ray = 0 if rho else 2 * complex(mp.zeta(s)) * (a ** -s + b ** -s + c ** -s)
    return tot / complex(mp.gamma(s)) + ray, len(cl)
if __name__ == "__main__":
    import time
    r = complex(mp.zetazero(1))
    for th in (math.pi / 4, math.pi / 3):
        for smax in (30, 38, 44):
            t0 = time.time(); v, n = ZB(r, 3.0, 3.0, 3.0, th, smax); print("theta %.3f smax %d: Z_B(rho1) = %.10f%+.10fj  cells %d  (%.1f s)" % (th, smax, v.real, v.imag, n, time.time() - t0))
    print("certified value: 0.645754390276+5.96283154319j")
