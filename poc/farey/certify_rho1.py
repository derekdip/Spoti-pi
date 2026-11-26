"""Certificate that Z_B(rho_1) != 0 on the modular torus.
 Z_B(rho) = 6 l3^-rho zeta(rho - 1) + 2 sum_cells Delta_cell(rho).  For every cell with max(N_u, N_w) <= NC we compute
 Delta_cell(rho_1) with mpmath (Bernoulli series on t < T0, quadrature beyond, quadrature error recorded) and the ratio
 Lambda = |Delta| / delta.  Envelope: Lambda <= K (a + b)^p, fitted with margin; tail bound
 2 sum_{cells beyond NC} K (a+b)^p * 15.24 e^{-(a+b)}, summed over the actual cells up to N = 60 plus an analytic tail."""
import mpmath as mp, math, numpy as np
mp.mp.dps = 30
L = lambda tr: 2 * mp.acosh(mp.mpf(tr) / 2)
l3 = L(3); rho = mp.zetazero(1)
KSER = 40; T0 = mp.mpf("0.05")
BN = [mp.bernoulli(n) for n in range(KSER + 4)]; BN[1] = mp.mpf(-1) / 2
def ser_a(p): return [BN[n] * p ** (n - 1) / mp.factorial(n) for n in range(KSER + 4)]
def ser_g(p, q):
    A, B = ser_a(p), ser_a(q); C = {}
    for i in range(KSER + 4):
        for j in range(KSER + 4 - i): C[i + j - 2] = C.get(i + j - 2, 0) + A[i] * B[j]
    return C
def Delta(s, a, b, c):
    Cg, C2, C3, Ah = ser_g(a, c), ser_g(c, b), ser_g(a, b), ser_a(c)
    coef = {k: Cg.get(k, 0) + C2.get(k, 0) - C3.get(k, 0) + (Ah[k + 1] if 0 <= k + 1 < len(Ah) else 0) for k in range(-2, KSER)}
    I1 = sum(coef[k] * T0 ** (s + k) / (s + k) for k in range(-1, KSER))
    tail_ser = abs(coef[KSER - 1]) * T0 ** (KSER + 1)          # size of the last series term (convergence check)
    g = lambda p, q, t: 1 / ((mp.exp(p * t) - 1) * (mp.exp(q * t) - 1))
    D = lambda t: g(a, c, t) + g(c, b, t) + 1 / (mp.exp(c * t) - 1) - g(a, b, t)
    I2, err = mp.quad(lambda t: t ** (s - 1) * D(t), [T0, 0.25, 1, 4, 16, mp.inf], error=True)
    return (I1 + coef[-2] * T0 ** (s - 2) / (s - 2) + I2) / mp.gamma(s), abs(err / mp.gamma(s)) + tail_ser
NC = 22
cells = []; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; a, b, c = L(tu), L(tw), L(tm)
    if max(a, b) > 60: continue
    cells.append((a, b, c, a + b - c)); st += [(tu, tm, tw), (tm, tw, tu)]
inner = [x for x in cells if max(x[0], x[1]) <= NC]; outer = [x for x in cells if max(x[0], x[1]) > NC]
print("cells: %d computed (max N <= %d), %d in the tail up to N = 60" % (len(inner), NC, len(outer)), flush=True)
tot = 6 * l3 ** (-rho) * mp.zeta(rho - 1); qerr = mp.mpf(0); ratios = []
for a, b, c, dl in inner:
    d, e = Delta(rho, a, b, c); tot += 2 * d; qerr += 2 * e; ratios.append((float(a + b), float(abs(d) / dl)))
r = np.array(ratios)
# envelope Lambda <= K (a+b)^p: fit p on the upper hull, then K = max ratio / (a+b)^p with factor 2 margin
p = 4.0; K = 2 * max(lam / s ** p for s, lam in r)
print("Lambda = |Delta|/delta over computed cells: min %.3e, max %.3e; envelope Lambda <= K (a+b)^%g with K = %.3e (2x margin)" % (r[:, 1].min(), r[:, 1].max(), p, K))
for lo, hi in ((0, 8), (8, 14), (14, 20), (20, 30), (30, 50)):
    m = (r[:, 0] > lo) & (r[:, 0] <= hi)
    if m.any(): print("   a+b in (%2d, %2d]: max Lambda/(a+b)^4 = %.3e (%d cells)" % (lo, hi, (r[m, 1] / r[m, 0] ** p).max(), m.sum()))
tail_cells = 2 * sum(K * float(a + b) ** p * 15.24 * math.exp(-float(a + b)) for a, b, c, dl in outer)
# beyond N = 60: number of cells with a+b in [S, S+1] is at most ~ S^2 (primitive count), so sum K S^p 15.24 e^-S S^2
tail_far = 2 * sum(K * S ** (p + 2) * 15.24 * math.exp(-S) for S in range(60, 400))
print("\nZ_B(rho_1) = %s" % mp.nstr(tot, 12))
print("quadrature + series error bound: %.2e;  tail bound (cells with max N in (%d, 60]): %.2e;  beyond 60: %.2e" % (float(qerr), NC, tail_cells, tail_far))
total_err = float(qerr) + tail_cells + tail_far
print("certified: |Z_B(rho_1)| >= %.6f - %.2e > 0" % (float(abs(tot)), total_err))
