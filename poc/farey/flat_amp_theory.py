"""Mean-square prediction <|Z_flat(rho)|^2>/gamma -> (1/2pi) sum_m r(m)^2 m^{-3/2} (functional equation + mean value
theorem), hexagonal unimodular lattice; compared with the 300 computed zeros. Also the exact FE check at rho_1."""
import math, numpy as np, mpmath as mp
from collections import Counter
c = 2 / math.sqrt(3)                      # unimodular hexagonal: |a + b w|^2 = c (a^2 + ab + b^2)
R = 1500; cnt = Counter()
for a in range(-R, R + 1):
    bs = np.arange(-R, R + 1); q = a * a + a * bs + bs * bs
    for v in q[(q > 0) & (q <= R * R // 2)]: cnt[int(v)] += 1
Q = R * R // 2
S = sum(r * r * (c * m) ** -1.5 for m, r in cnt.items() if m <= Q)
tail = 0  # r^2 ~ (log m) on average; tail beyond Q ~ C log Q / sqrt(Q)
print("sum_m r(m)^2 m^{-3/2} (norms up to %d) = %.4f   ->  predicted <|Z|^2>/gamma = %.4f" % (Q, S, S / (2 * math.pi)))
r = np.load("poc/farey/flat_amplitudes.npy"); g = r[:, 0]
for lo in (0, 100, 200, 300, 400):
    m = (g >= lo) & (g < lo + 150)
    if m.sum(): print("  observed <|Z|^2>/gamma, gamma in [%d, %d): %.3f (%d zeros)" % (lo, lo + 150, np.mean(r[m, 1] ** 2 / g[m]), m.sum()))
print("  observed overall: %.3f" % np.mean(r[:, 1] ** 2 / g))

# Landau-corrected mean over zeros: <x^{i gamma}>_zeros ~ -Lambda(x) x^{-1/2}/log(T/2pi) for prime powers x
from sympy import factorint
def Lam(n):
    f = factorint(n); return math.log(list(f)[0]) if len(f) == 1 else 0.0
cross = 0.0
norms = sorted(m for m in cnt if m <= 200000)
pk = [q for q in range(2, 450) if Lam(q) > 0]
for n in norms:
    rn = cnt[n]
    for q in pk:
        m = n * q * q
        if m > Q: break
        if m in cnt: cross += rn * cnt[m] * (c * c * n * m) ** -0.75 * Lam(q) * q ** -0.5
print("Landau cross sum C = %.4f" % cross)
for lo in (0, 100, 200, 300, 400):
    m = (g >= lo) & (g < lo + 150)
    if m.sum():
        T = np.mean(g[m]); L = math.log(T / (2 * math.pi))
        pred = (S - 2 * cross / L) / (2 * math.pi)
        print("  gamma ~ %5.0f: Landau-corrected prediction %.3f   observed %.3f" % (T, pred, np.mean(r[m, 1] ** 2 / g[m])))
