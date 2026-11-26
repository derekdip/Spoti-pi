"""Z_B(rho_k), k <= K, on the modular torus via the Farey-cell sum with Delta_cell computed on the rotated ray
arg t = pi/2 - eta (eta = 1/(1 + gamma)): no cancellation amplified by 1/Gamma(rho)."""
import mpmath as mp, math, sys, time, numpy as np
mp.mp.dps = 30
KSER = 40; T0 = mp.mpf("0.05")
BN = [mp.bernoulli(n) for n in range(KSER + 4)]; BN[1] = mp.mpf(-1) / 2
def ser_a(p): return [BN[n] * p ** (n - 1) / mp.factorial(n) for n in range(KSER + 4)]
def ser_g(p, q):
    A, B = ser_a(p), ser_a(q); C = {}
    for i in range(KSER + 4):
        for j in range(KSER + 4 - i): C[i + j - 2] = C.get(i + j - 2, 0) + A[i] * B[j]
    return C
L = lambda tr: 2 * mp.acosh(mp.mpf(tr) / 2)
def Delta_rot(s, a, b, c, th):
    Cg, C2, C3, Ah = ser_g(a, c), ser_g(c, b), ser_g(a, b), ser_a(c)
    coef = {k: Cg.get(k, 0) + C2.get(k, 0) - C3.get(k, 0) + (Ah[k + 1] if 0 <= k + 1 < len(Ah) else 0) for k in range(-2, KSER)}
    z0 = T0 * mp.expj(th)
    I1 = sum(coef[k] * z0 ** (s + k) / (s + k) for k in range(-2, KSER))
    dl = a + b - c; e = mp.expj(th)
    D = lambda t: mp.exp(c * t) * mp.expm1(dl * t) / (mp.expm1(a * t) * mp.expm1(b * t) * mp.expm1(c * t))
    f = lambda r: (r * e) ** (s - 1) * D(r * e) * e
    I2 = mp.quad(f, [T0, 0.25, 1, 3, 8, 20, mp.inf])
    return (I1 + I2) / mp.gamma(s)
cells = []; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td
    if max(L(tu), L(tw)) > 22: continue
    cells.append((L(tu), L(tw), L(tm))); st += [(tu, tm, tw), (tm, tw, tu)]
K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
l3 = L(3); out = []
for k in range(1, K + 1):
    t0 = time.time(); r = mp.zetazero(k); g = float(r.imag); th = mp.pi / 2 - 1 / (1 + g)
    Z = 6 * l3 ** (-r) * mp.zeta(r - 1) + 2 * mp.fsum(Delta_rot(r, a, b, c, th) for a, b, c in cells)
    cf = Z / (2 * r * mp.zeta(r, derivative=1)); out.append((complex(r), complex(cf), complex(Z)))
    print("k = %2d: gamma = %8.4f  Z_B(rho) = %s  |c_k| = %.4f  (%.0f s)" % (k, g, mp.nstr(Z, 9), abs(cf), time.time() - t0), flush=True)
np.save("poc/farey/zeros_rotated.npy", np.array([[o[0], o[1], o[2]] for o in out]))
