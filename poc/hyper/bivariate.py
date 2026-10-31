"""Full distribution of c1 over rooted planar hypermaps with k darts, from the character formula,
against Tutte's slicings formula.

With x = a N, y = N, u = N the a-degree of a monomial is c1 itself, so no jet is needed: coefficients
are integer polynomials in (N, a), truncated at N-degree k+2 and a-degree k.  The genus-0 transitive
part is the coefficient of N^{k+2}; its a-polynomial, divided by (k-1)!, is  sum_c H(k, c) a^c  where
H(k, c) is the number of rooted planar hypermaps with k darts and c vertices.

Tutte (A census of slicings, 1962), dualised to bipartite maps and read through the S_3 symmetry of
hypermaps: the number of rooted planar bipartite maps with e edges and f faces is
    T(e, f) = 2 e! / ((e - f + 2)! f!) * [t^e] beta(t)^f,   beta(t) = sum_{i>=1} C(2i-1, i) t^i.
The two tables must agree, and their second moments must agree with hyper_moments.json.
"""
from math import comb, factorial
from fractions import Fraction
import json, os, sys, time
from moments import partitions, hook_dim, contents

def pmul(P, Q, D, A):
    out = [[0]*(A+1) for _ in range(D+1)]
    for i, p in enumerate(P):
        for j, q in enumerate(Q):
            if i + j > D: break
            o = out[i+j]
            for da, pa in enumerate(p):
                if pa == 0: continue
                for db, qb in enumerate(q):
                    if da + db > A: break
                    if qb: o[da+db] += pa * qb
    return out

def content_product(lam, D, A):
    P = [[1] + [0]*A] + [[0]*(A+1) for _ in range(D)]
    for c in contents(lam):
        fx = [[c] + [0]*A, [0, 1] + [0]*(A-1)]    # x + c = a N + c
        fu = [[c] + [0]*A, [1] + [0]*A]           # y + c = u + c = N + c
        P = pmul(pmul(pmul(P, fx, D, A), fu, D, A), fu, D, A)
    return P

def all_triples(k, D, A):
    acc = [[0]*(A+1) for _ in range(D+1)]
    for lam in partitions(k):
        d2 = hook_dim(lam) ** 2
        Pl = content_product(lam, D, A)
        for i in range(D+1):
            for j in range(A+1): acc[i][j] += d2 * Pl[i][j]
    kf = factorial(k)
    return [[c // kf for c in row] for row in acc]

def character_table(K):
    D, A = K + 2, K
    P = {k: all_triples(k, D, A) for k in range(1, K+1)}
    T = {}
    for k in range(1, K+1):
        Tk = [row[:] for row in P[k]]
        for j in range(1, k):
            prod = pmul(T[j], P[k-j], D, A)
            c = comb(k-1, j-1)
            for i in range(D+1):
                for m in range(A+1): Tk[i][m] -= c * prod[i][m]
        T[k] = Tk
    H = {}
    for k in range(1, K+1):
        km = factorial(k-1)
        row = T[k][k+2]
        assert all(v % km == 0 for v in row)
        H[k] = [v // km for v in row]           # index = c1
    return H

def tutte_table(K):
    beta = [0] + [comb(2*i-1, i) for i in range(1, K+1)]
    powers = [[1] + [0]*K]
    for f in range(1, K+1):
        prev = powers[-1]; nxt = [0]*(K+1)
        for i, p in enumerate(prev):
            if p == 0: continue
            for j in range(1, K+1-i): nxt[i+j] += p * beta[j]
        powers.append(nxt)
    T = {}
    for e in range(1, K+1):
        row = [0]*(e+1)
        for f in range(1, e+1):
            v = Fraction(2 * factorial(e), factorial(e-f+2) * factorial(f)) * powers[f][e]
            assert v.denominator == 1
            row[f] = int(v)
        T[e] = row
    return T

if __name__ == "__main__":
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    t0 = time.time()
    H = character_table(K)
    T = tutte_table(K)
    print(f"[{time.time()-t0:.1f}s] rooted planar hypermaps with k darts and c vertices")
    ok = True
    for k in range(1, K+1):
        hrow = H[k][:k+1]; trow = T[k] + [0]*(k+1-len(T[k]))
        same = hrow == trow
        ok &= same
        print(f"  k={k:2d} total={sum(hrow):>12d} by c1: {hrow[1:]}  tutte agrees: {same}")
    print("character table == Tutte slicings table for all k <=", K, ":", ok)
    mom = {r["k"]: r for r in json.load(open(os.path.join(os.path.dirname(__file__), "..", "results", "hyper_moments.json")))}
    okm = True
    for k in range(1, min(K, max(mom))+1):
        s1 = sum(c * H[k][c] for c in range(k+1)); s2 = sum(c*c*H[k][c] for c in range(k+1))
        okm &= (s1 == mom[k]["L"] and s2 == mom[k]["s2"] and sum(H[k]) == mom[k]["N"])
    print("first and second moments of c1 agree with hyper_moments.json:", okm)
    out = os.path.join(os.path.dirname(__file__), "..", "results", "hyper_bivariate.json")
    json.dump({"character": {k: H[k][:k+1] for k in H}, "tutte": T, "agree": ok and okm}, open(out, "w"), indent=0)
    print("wrote", os.path.normpath(out))
