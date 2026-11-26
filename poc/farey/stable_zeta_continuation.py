"""Meromorphic continuation of Z_B via the Farey-cell decomposition.
 Z_B(s) = 6 l3^-s zeta(s-1) + 2 sum_cells Delta(s),
 Delta(s) = (1/Gamma(s)) int_0^inf t^{s-1} D(t) dt,  D = g(u,m) + g(m,w) + h(m) - g(u,w),
 g(p,q) = e^{-(Np+Nq)t}/((1-e^{-Np t})(1-e^{-Nq t})),  h(m) = e^{-Nm t}/(1-e^{-Nm t}).
 D(t) = d0 t^-2 + 0 t^-1 + O(1), d0 = 1/(Nu Nm) + 1/(Nm Nw) - 1/(Nu Nw); for Re s > 0:
 Delta(s) = (1/Gamma(s)) [ int_0^1 t^{s-1}(D - d0/t^2) dt + d0/(s-2) + int_1^inf t^{s-1} D dt ].
Checks: (1) delta e^{max(Nu,Nw)} bounded; (2) s = 3 vs direct sum; (3) s = rho_1 vs the smoothed-sum value 0.6457+5.9625i."""
import mpmath as mp, math, numpy as np
mp.mp.dps = 40
L = lambda tr: 2 * mp.acosh(mp.mpf(tr) / 2)
l3 = L(3)
cells = []
st = [(3, 3, 3)] * 3
NCUT = 24
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td
    a, b, c = L(tu), L(tw), L(tm)
    if max(a, b) > NCUT: continue
    cells.append((a, b, c)); st += [(tu, tm, tw), (tm, tw, tu)]
d = [(a + b - c) * mp.exp(max(a, b)) for a, b, c in cells]
print("cells with max(Nu, Nw) <= %d: %d;  delta * e^{max(Nu,Nw)}: min %s, max %s" % (NCUT, len(cells), mp.nstr(min(d), 5), mp.nstr(max(d), 5)))
d2 = [(a + b - c) * mp.exp(max(a, b) / 2) for a, b, c in cells]
print("   (for comparison delta * e^{max/2}: max %s)" % mp.nstr(max(d2), 5))
KSER = 40; T0 = mp.mpf("0.05")
BN = [mp.bernoulli(n) for n in range(KSER + 4)]; BN[1] = mp.mpf(-1) / 2   # 1/(e^x - 1) = sum B_n x^(n-1)/n!
def ser_a(p):   # coefficients of 1/(e^{pt}-1) in powers t^(n-1), n = 0..
    return [BN[n] * p ** (n - 1) / mp.factorial(n) for n in range(KSER + 4)]
def ser_g(p, q):  # 1/((e^{pt}-1)(e^{qt}-1)) = sum_k C_k t^k, k >= -2
    A, B = ser_a(p), ser_a(q); C = {}
    for i in range(KSER + 4):
        for j in range(KSER + 4 - i):
            C[i + j - 2] = C.get(i + j - 2, 0) + A[i] * B[j]
    return C
def Delta(s, a, b, c):
    Cg = ser_g(a, c); C2 = ser_g(c, b); C3 = ser_g(a, b); Ah = ser_a(c)
    coef = {k: Cg.get(k, 0) + C2.get(k, 0) - C3.get(k, 0) + (Ah[k + 1] if 0 <= k + 1 < len(Ah) else 0) for k in range(-2, KSER)}
    d0 = coef[-2]
    # small t: int_0^T0 t^{s-1} (D - d0/t^2) dt = sum_{k>=-1} coef_k T0^{s+k}/(s+k)  (coef_-1 should vanish)
    I1 = sum(coef[k] * T0 ** (s + k) / (s + k) for k in range(-1, KSER)) if abs(coef[-1]) < 1e-25 else None
    def g(p, q, t): return 1 / ((mp.exp(p * t) - 1) * (mp.exp(q * t) - 1))
    D = lambda t: g(a, c, t) + g(c, b, t) + 1 / (mp.exp(c * t) - 1) - g(a, b, t)
    I2 = mp.quad(lambda t: t ** (s - 1) * D(t), [T0, 0.25, 1, 4, 16, mp.inf])
    # d0 part on [T0, inf) was not subtracted: the d0 t^-2 term is in I2; on [0, T0] we used D - d0/t^2, so add int_0^T0 d0 t^{s-3} = d0 T0^{s-2}/(s-2)
    return (I1 + d0 * T0 ** (s - 2) / (s - 2) + I2) / mp.gamma(s), coef[-1]
def ZB(s, ncut=NCUT):
    return 6 * l3 ** (-s) * mp.zeta(s - 1) + 2 * mp.fsum(Delta(s, a, b, c)[0] for a, b, c in cells if max(a, b) <= ncut)
# direct sum at s = 3
def Lf(tr): return 2 * math.acosh(tr / 2) if tr < 10**300 else 2 * math.log(tr)
out = [Lf(3)] * 3; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lf(tm)
    if lm > 3000: continue
    out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
Ns = np.array(out); zeta3 = float(mp.zeta(3))
direct3 = 2 * zeta3 * np.sum(Ns ** -3.0)  # + tail beyond 3000 ~ 2 zeta(3) * (6 Area/pi^2... ) tiny
tail = 2 * zeta3 * (3 / math.pi ** 2) * 0.8918031660 * 2 / 3000   # sum_{l > X} l^-3 ~ int 2c l^-2
print("\n(2) s = 3: cell sum %s   direct %.12f (+ tail ~ %.1e)" % (mp.nstr(ZB(mp.mpf(3)), 13), direct3, tail))
r1 = mp.zetazero(1)
print('    max |coef_-1| over cells (pole at s=1 must cancel): %s' % mp.nstr(max(abs(Delta(mp.mpf(3), a, b, c)[1]) for a, b, c in cells), 3))
for nc in (12, 18, 24):
    z = ZB(r1, nc); print("(3) s = rho_1, cells up to %2d: Z_B = %s" % (nc, mp.nstr(z, 10)))
print("    smoothed lattice sum (earlier section): 0.64566 + 5.96253i")
for s in (mp.mpf("0.5"),):
    print("    s = %s: Z_B = %s" % (s, mp.nstr(ZB(s), 12)))
