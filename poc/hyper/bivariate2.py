"""Full bivariate polynomials H_k(x, y) = sum over rooted planar hypermaps with k darts of x^c1 y^c2,
from the character formula with x = a N, y = b N, u = N, for k <= K (default 10).

The polynomial in (N, a, b) is truncated at N-degree k+2; the coefficient of N^{k+2} in the transitive
part, divided by (k-1)!, is H_k with a-degree c1 and b-degree c2.  Output: hyper_bivariate2.json with
H[k][c1][c2].
"""
from math import comb, factorial
import json, os, sys, time
import numpy as np
from moments import partitions, hook_dim, contents

def mul3(P, Q, D, A):
    """P, Q: object arrays (D+1, A+1, A+1); product truncated at N-degree D (a, b degrees never exceed A)."""
    out = np.zeros((D + 1, A + 1, A + 1), dtype=object); out[:] = 0
    for n in range(D + 1):
        for i in range(A + 1):
            for j in range(A + 1):
                c = P[n, i, j]
                if c == 0: continue
                nn, ii, jj = D + 1 - n, A + 1 - i, A + 1 - j
                out[n:, i:, j:] += c * Q[:nn, :ii, :jj]
    return out

def content_product(lam, D, A):
    P = np.zeros((D + 1, A + 1, A + 1), dtype=object); P[:] = 0; P[0, 0, 0] = 1
    for c in contents(lam):
        # (a N + c): shift N-degree and a-degree by one, plus c times
        Px = np.zeros_like(P); Px[:] = 0
        Px[1:, 1:, :] += P[:-1, :-1, :]; Px += c * P
        # (b N + c)
        Py = np.zeros_like(Px); Py[:] = 0
        Py[1:, :, 1:] += Px[:-1, :, :-1]; Py += c * Px
        # (N + c)
        Pu = np.zeros_like(Py); Pu[:] = 0
        Pu[1:, :, :] += Py[:-1, :, :]; Pu += c * Py
        P = Pu
    return P

def all_triples(k, D, A):
    acc = np.zeros((D + 1, A + 1, A + 1), dtype=object); acc[:] = 0
    for lam in partitions(k):
        acc += hook_dim(lam) ** 2 * content_product(lam, D, A)
    kf = factorial(k)
    return np.vectorize(lambda v: v // kf, otypes=[object])(acc)

if __name__ == "__main__":
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    t0 = time.time()
    D, A = K + 2, K
    P = {k: all_triples(k, D, A) for k in range(1, K + 1)}
    T = {}
    for k in range(1, K + 1):
        Tk = P[k].copy()
        for j in range(1, k):
            Tk -= comb(k - 1, j - 1) * mul3(T[j], P[k - j], D, A)
        T[k] = Tk
    H = {}
    for k in range(1, K + 1):
        km = factorial(k - 1)
        top = T[k][k + 2]
        assert all(int(v) % km == 0 for v in top.flatten())
        H[k] = [[int(top[i, j]) // km for j in range(k + 1)] for i in range(k + 1)]
        tot = sum(map(sum, H[k]))
        print(f"  k={k:2d} total {tot}  H_k(1,1) check; degrees c1,c2 in 1..{k}")
    print(f"[{time.time()-t0:.1f}s]")
    json.dump({str(k): H[k] for k in H}, open(os.path.join(os.path.dirname(__file__), "..", "results", "hyper_bivariate2.json"), "w"))
    print("wrote hyper_bivariate2.json")
