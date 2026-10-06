"""Exact raw moments, to order J, of X = c1 - c2 and of c1 over rooted planar hypermaps with k darts.

Same Frobenius content-product machinery as moments.py, but the jets live in the divided-power basis
a^r / r!, so that x = N e^{a} is the jet [1, 1, 1, ...] and y = N e^{-a} is [1, -1, 1, ...], both integer.
The coefficient of a^r / r! in the genus-0 transitive part, divided by (k-1)!, is then exactly
sum_{rooted maps} (c1 - c2)^r (mode X) or sum c1^r (mode c1). Cumulants follow by the usual recursion.

Modes:  X   : x = N e^{a},  y = N e^{-a}, u = N
        c1  : x = N e^{a},  y = N,        u = N
"""
from math import comb, factorial
from fractions import Fraction as Fr
import json, os, sys, time
from moments import partitions, hook_dim, contents

J = 8
BIN = [[comb(r, m) for m in range(r + 1)] for r in range(J + 1)]
ZJ = [0] * (J + 1)

def jmul(p, q):
    return [sum(BIN[r][m] * p[m] * q[r - m] for m in range(r + 1)) for r in range(J + 1)]
def jadd(p, q): return [a + b for a, b in zip(p, q)]
def jscale(p, c): return [a * c for a in p]

def pmul(P, Q, D):
    out = [ZJ[:] for _ in range(D + 1)]
    for i, p in enumerate(P):
        if p == ZJ: continue
        for j, q in enumerate(Q):
            if i + j > D: break
            if q == ZJ: continue
            out[i + j] = jadd(out[i + j], jmul(p, q))
    return out

def content_product(lam, D, EX, EY):
    P = [[1] + [0] * J] + [ZJ[:] for _ in range(D)]
    for c in contents(lam):
        fx = [[c] + [0] * J, EX]
        fy = [[c] + [0] * J, EY]
        fu = [[c] + [0] * J, [1] + [0] * J]
        P = pmul(pmul(pmul(P, fx, D), fy, D), fu, D)
    return P

def all_triples(k, D, EX, EY):
    acc = [ZJ[:] for _ in range(D + 1)]
    for lam in partitions(k):
        d2 = hook_dim(lam) ** 2
        Pl = content_product(lam, D, EX, EY)
        for i in range(D + 1):
            acc[i] = jadd(acc[i], jscale(Pl[i], d2))
    kf = factorial(k)
    return [[c // kf for c in jet] for jet in acc]

def raw_sums(K, mode):
    EX = [1] * (J + 1)
    EY = [(-1) ** r for r in range(J + 1)] if mode == "X" else [1] + [0] * J
    D = K + 2
    P = {k: all_triples(k, D, EX, EY) for k in range(1, K + 1)}
    T = {}
    for k in range(1, K + 1):
        Tk = [j[:] for j in P[k]]
        for j in range(1, k):
            prod = pmul(T[j], P[k - j], D)
            c = comb(k - 1, j - 1)
            Tk = [jadd(Tk[i], jscale(prod[i], -c)) for i in range(D + 1)]
        T[k] = Tk
    out = {}
    for k in range(1, K + 1):
        top = T[k][k + 2]; km = factorial(k - 1)
        assert all(v % km == 0 for v in top)
        out[k] = [v // km for v in top]          # S_r = sum over rooted maps of (statistic)^r, r = 0..J
    return out

def cumulants(S):
    """raw sums S_0..S_J over N = S_0 maps -> cumulants kappa_1..kappa_J (Fractions)"""
    N = S[0]; m = [Fr(s, N) for s in S]
    kap = [None] * (J + 1)
    for n in range(1, J + 1):
        kap[n] = m[n] - sum(comb(n - 1, j - 1) * kap[j] * m[n - j] for j in range(1, n))
    return kap

if __name__ == "__main__":
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    mode = sys.argv[2] if len(sys.argv) > 2 else "X"
    t0 = time.time()
    S = raw_sums(K, mode)
    rows = []
    for k in range(1, K + 1):
        kap = cumulants(S[k])
        rows.append(dict(k=k, N=S[k][0], sums=S[k], kappa=[str(x) for x in kap[1:]]))
    print(f"[{time.time()-t0:.1f}s] mode {mode}, K={K}, J={J}")
    for r in rows:
        print(f"  k={r['k']:2d} N={r['N']}  kappa_1..{J} = " + ", ".join(f"{float(Fr(x)):.6g}" for x in r["kappa"]))
    out = os.path.join(os.path.dirname(__file__), "..", "results", f"hyper_cumulants_{mode}.json")
    json.dump(rows, open(out, "w"))
    print("wrote", os.path.normpath(out))
