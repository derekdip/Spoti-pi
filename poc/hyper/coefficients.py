"""Exact joint coefficients A_k(c1, c2, c3) of rooted planar hypermaps from Htilde = pqr(1-p-q-r).

Lagrange-Good inversion for p = X/(1-q-r), q = U/(1-p-r), r = Y/(1-p-q):
    [X^a U^b Y^c] F(p,q,r) = [p^a q^b r^c] F . (1-q-r)^{-a} (1-p-r)^{-b} (1-p-q)^{-c} . det M,
    det M = det(delta_ij - (w_j/phi_i) d_j phi_i) = det J / ((1-q-r)(1-p-r)(1-p-q)),
    det J = (1-p-q-r)^2 - 4pqr.
With F = pqr (1-p-q-r):
    A(a, b, c) = [p^{a-1} q^{b-1} r^{c-1}]  Q(p,q,r) (1-q-r)^{-(a+1)} (1-p-r)^{-(b+1)} (1-p-q)^{-(c+1)},
    Q = (1-p-q-r) ((1-p-q-r)^2 - 4pqr),
where a = c1 (vertices, X), b = c3 (U), c = c2 (Y), a + b + c = k + 2.  A finite triple sum of
multinomials for each of the 20 monomials of Q; exact integers.

Uses: verify against the full joint data k <= 12; check the support is the whole triangle; factor
large entries (a product formula would show only small primes); compute central coefficients for
large k and test k Pr(c1 = c2 = (k+2)/3) -> 27 sqrt(3) / (10 pi) = 1/(2 pi sqrt(det Sigma)).
"""
from fractions import Fraction as Fr
from math import comb, factorial, sqrt, pi, log
import json, sys, time

# ---- Q as a dict of monomials
def padd(P, Qd):
    out = dict(P)
    for m, c in Qd.items():
        out[m] = out.get(m, 0) + c
        if out[m] == 0: del out[m]
    return out
def pmul(P, Qd):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Qd.items():
            m = (m1[0] + m2[0], m1[1] + m2[1], m1[2] + m2[2]); out[m] = out.get(m, 0) + c1 * c2
    return {m: c for m, c in out.items() if c}
one = {(0, 0, 0): 1}; p = {(1, 0, 0): 1}; q = {(0, 1, 0): 1}; r = {(0, 0, 1): 1}
theta = padd(one, {(1, 0, 0): -1, (0, 1, 0): -1, (0, 0, 1): -1})
detJ = padd(pmul(theta, theta), {(1, 1, 1): -4})
Qpoly = pmul(theta, detJ)

FACT = [1]
def fact(n):
    while len(FACT) <= n: FACT.append(FACT[-1] * len(FACT))
    return FACT[n]
def multinom(n, i, j):        # [q^i r^j] (1 - q - r)^{-(n+1)} = (n+i+j)! / (n! i! j!)
    return fact(n + i + j) // (fact(n) * fact(i) * fact(j))

def coefficient(a, b, c):
    """A(a, b, c) with a = c1, b = c3, c = c2; returns 0 outside the support"""
    if min(a, b, c) < 1: return 0
    total = 0
    for (al, be, ga), coef in Qpoly.items():
        A, B, C = a - 1 - al, b - 1 - be, c - 1 - ga     # remaining degrees in p, q, r
        if min(A, B, C) < 0: continue
        s = 0
        # factor1 (1-q-r)^{-(a+1)} gives q^{i1} r^{j1}; factor2 (1-p-r)^{-(b+1)} gives p^{i2} r^{j2};
        # factor3 (1-p-q)^{-(c+1)} gives p^{i3} q^{j3};  i2+i3 = A, i1+j3 = B, j1+j2 = C
        for i2 in range(A + 1):
            i3 = A - i2
            for i1 in range(B + 1):
                j3 = B - i1
                f3 = multinom(c, i3, j3)
                for j1 in range(C + 1):
                    j2 = C - j1
                    s += multinom(a, i1, j1) * multinom(b, i2, j2) * f3
        total += coef * s
    return total

def N_of(k): return 3 * 2 ** (k - 1) * comb(2 * k, k) // (k + 1) // (k + 2)

if __name__ == "__main__":
    H = {int(k): v for k, v in json.load(open("../results/hyper_bivariate2.json")).items()}
    K = max(H)
    t0 = time.time()
    ok = True; support_ok = True
    for k in range(1, K + 1):
        for c1 in range(1, k + 1):
            for c2 in range(1, k + 1):
                c3 = k + 2 - c1 - c2
                val = coefficient(c1, c3, c2) if c3 >= 1 else 0
                ok &= (val == H[k][c1][c2])
                if c3 >= 1 and H[k][c1][c2] <= 0: support_ok = False
    print(f"Lagrange-Good coefficient formula equals the character data for every (k, c1, c2), k <= {K}: {ok}  [{time.time()-t0:.1f}s]")
    print(f"support is the whole triangle c1, c2, c3 >= 1 (lattice span 1): {support_ok}")
    # factorisation of a few entries
    def factor(n):
        f = []; d = 2
        while d * d <= n:
            while n % d == 0: f.append(d); n //= d
            d += 1
        if n > 1: f.append(n)
        return f
    print("prime factorisations of some joint counts at k = 12 (c1, c2, c3):")
    for (c1, c2) in ((4, 4), (3, 5), (5, 5), (2, 6), (6, 2), (7, 3)):
        v = H[12][c1][c2]; print(f"   ({c1},{c2},{14-c1-c2}): {v} = {factor(v)}")
    # central coefficients for large k
    print("local limit test: k Pr(c1 = c2 = m), m = (k+2)/3, against 27 sqrt3/(10 pi) = %.6f" % (27 * sqrt(3) / (10 * pi)))
    rows = []
    for k in [int(a) for a in sys.argv[1:]] or [31, 61, 91, 121, 151]:
        assert k % 3 == 1
        m = (k + 2) // 3
        t1 = time.time()
        A = coefficient(m, m, m); N = N_of(k)
        val = k * A / N
        rows.append((k, val))
        print(f"   k={k:4d}  k Pr = {val:.6f}   ratio to limit {val / (27*sqrt(3)/(10*pi)):.5f}  [{time.time()-t1:.1f}s]")
    if len(rows) >= 2:
        (k1, v1), (k2, v2) = rows[-2], rows[-1]
        rich = (k2 * v2 - k1 * v1) / (k2 - k1)
        print(f"   Richardson (1/k) extrapolation from the last two: {rich:.6f}   ratio {rich / (27*sqrt(3)/(10*pi)):.5f}")
    json.dump({"formula_matches_data": ok, "support_full": support_ok, "central": rows}, open("../results/hyper_coefficients.json", "w"), indent=1)
