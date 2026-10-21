"""Exact genus-0 transitive triple statistics via the content-product (Frobenius) formula.

sum_{s1 s2 s3 = 1 in S_k} x^{c1} y^{c2} u^{c3} = (1/k!) sum_{lambda |- k} (dim lambda)^2 prod_{boxes} (x+c)(y+c)(u+c)

Transitive (connected) triples come from the logarithm of the exponential series; genus 0 is the top
degree k+2 in N after x = N(1+a), y = N(1+b), u = N. Everything is a jet of order 2 in (a, b), so each
coefficient is an integer polynomial in N of degree <= k+2, truncated there.

Outputs, per k, divided by (k-1)! so that they are sums over rooted planar hypermaps with k darts:
  N_k  = number of rooted planar hypermaps
  L_k  = sum c1                       (the note's cycle-pointed series M)
  s2_k = sum c1^2,  s11_k = sum c1 c2
  Q_k  = sum (c1-c2)^2 / 2            (the note's Q = V/2)
  D_k  = sum (c1+c2)^2 / 2            (the vertex second moment used in the proof)
"""
from math import comb, factorial
import json, os, sys, time

def partitions(n, m=None):
    if m is None: m = n
    if n == 0: yield []; return
    for first in range(min(n, m), 0, -1):
        for rest in partitions(n - first, first):
            yield [first] + rest

def hook_dim(lam):
    n = sum(lam); conj = [sum(1 for r in lam if r > j) for j in range(lam[0])]
    h = 1
    for i, r in enumerate(lam):
        for j in range(r):
            h *= (r - j - 1) + (conj[j] - i - 1) + 1
    return factorial(n) // h

def contents(lam):
    return [j - i for i, r in enumerate(lam) for j in range(r)]

# jets: [1, a, b, a^2, ab, b^2]
def jmul(p, q):
    return [p[0]*q[0],
            p[0]*q[1] + p[1]*q[0],
            p[0]*q[2] + p[2]*q[0],
            p[0]*q[3] + p[1]*q[1] + p[3]*q[0],
            p[0]*q[4] + p[1]*q[2] + p[2]*q[1] + p[4]*q[0],
            p[0]*q[5] + p[2]*q[2] + p[5]*q[0]]
def jadd(p, q): return [x + y for x, y in zip(p, q)]
def jscale(p, c): return [x * c for x in p]
Z6 = [0]*6

def pmul(P, Q, D):
    """polynomials in N (lists of jets), truncated at degree D"""
    out = [Z6[:] for _ in range(D + 1)]
    for i, p in enumerate(P):
        if p == Z6: continue
        for j, q in enumerate(Q):
            if i + j > D: break
            if q == Z6: continue
            out[i + j] = jadd(out[i + j], jmul(p, q))
    return out

def content_product(lam, D):
    P = [[1,0,0,0,0,0]] + [Z6[:] for _ in range(D)]
    for c in contents(lam):
        fx = [[c,0,0,0,0,0], [1,1,0,0,0,0]]   # x + c = N(1+a) + c
        fy = [[c,0,0,0,0,0], [1,0,1,0,0,0]]   # y + c = N(1+b) + c
        fu = [[c,0,0,0,0,0], [1,0,0,0,0,0]]   # u + c = N + c
        P = pmul(pmul(pmul(P, fx, D), fy, D), fu, D)
    return P

def all_triples(k, D):
    acc = [Z6[:] for _ in range(D + 1)]
    for lam in partitions(k):
        d2 = hook_dim(lam) ** 2
        Pl = content_product(lam, D)
        for i in range(D + 1):
            acc[i] = jadd(acc[i], jscale(Pl[i], d2))
    kf = factorial(k)
    return [[c // kf for c in jet] for jet in acc]

def main(K):
    D = K + 2
    t0 = time.time()
    P = {k: all_triples(k, D) for k in range(1, K + 1)}
    T = {}
    for k in range(1, K + 1):
        Tk = [j[:] for j in P[k]]
        for j in range(1, k):
            prod = pmul(T[j], P[k - j], D)
            c = comb(k - 1, j - 1)
            Tk = [jadd(Tk[i], jscale(prod[i], -c)) for i in range(D + 1)]
        T[k] = Tk
    rows = []
    for k in range(1, K + 1):
        top = T[k][k + 2]                        # genus-0 transitive, jets in (a,b)
        n0, s1, s2, q1, q12, q2 = top
        S1sq = 2 * q1 + s1; S2sq = 2 * q2 + s2
        km = factorial(k - 1)
        for v in (n0, s1, s2, S1sq, q12, S2sq): assert v % km == 0
        N = n0 // km; L = s1 // km
        assert s2 // km == L, "colour symmetry"
        V2 = S1sq - 2 * q12 + S2sq                # sum (c1-c2)^2
        W2 = S1sq + 2 * q12 + S2sq                # sum (c1+c2)^2
        assert V2 % (2 * km) == 0 and W2 % (2 * km) == 0
        rows.append(dict(k=k, N=N, L=L, s2=S1sq // km, s11=q12 // km,
                         Q=V2 // (2 * km), D=W2 // (2 * km)))
    print(f"[{time.time()-t0:.1f}s] per k: N (rooted count), L = sum c1, s2 = sum c1^2, s11 = sum c1 c2, "
          f"Q = sum (c1-c2)^2 / 2, D = sum (c1+c2)^2 / 2")
    for r in rows: print("  ", r)
    return rows

if __name__ == "__main__":
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    rows = main(K)
    L = [0] + [r["L"] for r in rows]
    cat = [comb(2*k, k) // (k + 1) for k in range(K + 1)]
    print("L_k = 2^(k-1) Cat_k:", all(L[k] == 2**(k-1) * cat[k] for k in range(1, K+1)))
    print("(k+2) N_k = 3 L_k   :", all((r["k"] + 2) * r["N"] == 3 * r["L"] for r in rows))
    out = os.path.join(os.path.dirname(__file__), "..", "results", "hyper_moments.json")
    with open(out, "w") as f: json.dump(rows, f, indent=1)
    print("wrote", os.path.normpath(out))
