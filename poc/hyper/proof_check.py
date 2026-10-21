"""Exact series verification of every identity in the proof of  Q = M^2 / (1 + M).

All arithmetic is in Fractions over the integers, truncated at t^K; nothing is floating point.
Steps (see docs/planar-triples-transverse.md):
  1. M = t (1 + 2M)^2  and  M_k = 2^{k-1} Cat_k.
  2. Mobile equation  R_s = s / (1 - Phi(R_s)),  Phi(u) = sum_{i>=1} C(2i-1, i) t^i u^{i-1}:
        R_1 = 1 + M                            (first moment: pointed maps)
        d/ds R_s |_{s=1} = 1 / ((1 - 2M)(1 + M))   (second moment)
  3. D = M + R' - 1  equals the data's  sum (c1+c2)^2 / 2 (k-1)!.
  4. Q = 3 D - 2 (t M' + 2 M)  equals the data's Q and equals M^2 / (1 + M).
  5. The note's consequences: Q = w (M + Q), the recurrence (20), E = 4 w (M + E).
  6. Limit  Var(c1 - c2) / (k + 2) -> 10/27  for a uniform rooted planar hypermap.
"""
from fractions import Fraction as Fr
from math import comb
import json, os, sys

def run(K):
    Z = [Fr(0)] * (K + 1)
    def mul(a, b):
        out = Z[:]
        for i, x in enumerate(a):
            if x == 0: continue
            for j in range(K + 1 - i):
                if b[j]: out[i + j] += x * b[j]
        return out
    def add(a, b): return [x + y for x, y in zip(a, b)]
    def scale(a, c): return [x * c for x in a]
    def inv(a):
        assert a[0] != 0
        out = Z[:]; out[0] = 1 / a[0]
        for n in range(1, K + 1):
            out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
        return out
    def const(c): out = Z[:]; out[0] = Fr(c); return out
    one = const(1); t = Z[:]; t[1] = Fr(1)
    def deriv_t(a): return [Fr(0)] + [a[n] * n for n in range(1, K + 1)] if False else [n * a[n] for n in range(K + 1)]  # t d/dt

    # 1. M = t (1 + 2 M)^2
    M = Z[:]
    for _ in range(K + 1):
        M = mul(t, mul(add(one, scale(M, 2)), add(one, scale(M, 2))))
    cat = [comb(2 * k, k) // (k + 1) for k in range(K + 1)]
    ok1 = all(M[k] == 2 ** (k - 1) * cat[k] for k in range(1, K + 1)) and M[0] == 0
    print("1. M = t(1+2M)^2 has coefficients 2^(k-1) Cat_k:", ok1)

    # 2. the mobile equation, solved by iteration in the t-adic topology
    bino = [0] + [comb(2 * i - 1, i) for i in range(1, K + 1)]
    def Phi(u):      # sum C(2i-1,i) t^i u^{i-1}
        out = Z[:]; tp = one; up = one
        for i in range(1, K + 1):
            tp = mul(tp, t)
            if i > 1: up = mul(up, u)
            out = add(out, scale(mul(tp, up), bino[i]))
        return out
    def dPhi(u):     # d/du Phi
        out = Z[:]; tp = one; up = one
        for i in range(1, K + 1):
            tp = mul(tp, t)
            if i > 2: up = mul(up, u)
            if i >= 2: out = add(out, scale(mul(tp, up), bino[i] * (i - 1)))
        return out
    R = one
    for _ in range(K + 1):
        R = inv(add(one, scale(Phi(R), -1)))
    ok2a = R == add(one, M)
    print("2a. R_1 = 1/(1 - Phi(R_1)) equals 1 + M:", ok2a)
    Rp = inv(add(one, scale(add(Phi(R), mul(R, dPhi(R))), -1)))   # d/ds R_s at s = 1
    closed = inv(mul(add(one, scale(M, -2)), add(one, M)))
    ok2b = Rp == closed
    print("2b. d/ds R_s at s=1 equals 1/((1-2M)(1+M)):", ok2b)

    # 3. D from the data
    rows = json.load(open(os.path.join(os.path.dirname(__file__), "..", "results", "hyper_moments.json")))
    data = {r["k"]: r for r in rows}
    kmax = min(K, max(data))
    D = add(add(M, Rp), const(-1))
    ok3 = all(D[k] == data[k]["D"] for k in range(1, kmax + 1))
    print(f"3. D = M + R' - 1 equals sum (c1+c2)^2 / 2(k-1)! from the character data, k <= {kmax}:", ok3)

    # 4. Q
    tMp = deriv_t(M)
    ok4a = tMp == mul(mul(M, add(one, scale(M, 2))), inv(add(one, scale(M, -2))))
    Q = add(scale(D, 3), scale(add(tMp, scale(M, 2)), -2))
    Qclosed = mul(mul(M, M), inv(add(one, M)))
    ok4b = Q == Qclosed
    ok4c = all(Q[k] == data[k]["Q"] for k in range(1, kmax + 1))
    Nser = [Fr(0)] + [Fr(3 * M[k], k + 2) for k in range(1, K + 1)]
    ok4d = all(Nser[k] == data[k]["N"] for k in range(1, kmax + 1))
    print("4a. t M' = M(1+2M)/(1-2M):", ok4a)
    print("4b. Q = 3D - 2(tM' + 2M) equals M^2/(1+M) as series to order", K, ":", ok4b)
    print(f"4c. ... and equals the data's Q_k for k <= {kmax}:", ok4c, "   4d. N_k = 3 L_k/(k+2):", ok4d)

    # 5. the note's consequences
    w = mul(t, add(one, scale(M, 2)))
    ok5a = Q == mul(w, add(M, Q))
    rec = all(Q[k] == M[k-1] + Q[k-1] + 2 * sum(M[i] * (M[k-1-i] + Q[k-1-i]) for i in range(1, k-1))
              for k in range(2, K + 1))
    E = add(tMp, scale(M, -1))
    ok5c = E == scale(mul(w, add(M, E)), 4)
    print("5. Q = w(M+Q):", ok5a, "  recurrence (20) for k <=", K, ":", rec, "  E = 4w(M+E):", ok5c)

    # 6. variance of c1 - c2 under the uniform rooted hypermap
    print("6. Var(c1-c2) = 2 Q_k / N_k against (10/27)(k+2), 10/27 = %.6f; Var(c1) = (D_k+Q_k)/(2N_k) - ((k+2)/3)^2" % (10/27))
    for k in sorted(set([2, 4, 8, 16, 32, 64, K])):
        if k > K: continue
        var = 2 * Q[k] / Nser[k]
        varc1 = (D[k] + Q[k]) / (2 * Nser[k]) - Fr(k + 2, 3) ** 2
        print(f"   k={k:3d}  Var(c1-c2) = {float(var):12.6f}   /(k+2) = {float(var/(k+2)):.6f}"
              f"   Var(c1) = {float(varc1):12.6f}   /(k+2) = {float(varc1/(k+2)):.6f}")
    allok = ok1 and ok2a and ok2b and ok3 and ok4a and ok4b and ok4c and ok4d and ok5a and rec and ok5c
    print("ALL CHECKS PASS:", allok)
    return allok

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 64)
