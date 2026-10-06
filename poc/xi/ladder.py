"""Exact rational check of the alternating spectral ladder constants C_n.

After hazard scaling the xi Hankel kernel becomes k(s) = Phi(x0 + s/H)/Phi(x0) with
  log k(s) = -s - sum_{r>=2} eps^{r-1} s^r / r!      (theta / Gumbel jets)
and the operator matrix in the monic-Laguerre basis p_n (weight e^{-2u}) is
  A_mn = int_0^inf e^{-2s} G(s,eps) R_mn(s) ds,  R_mn(s) = int_0^s p_m(u) p_n(s-u) du,
  G = exp(log k + s),  int_0^inf e^{-2s} s^j ds = j!/2^{j+1}.
Every coefficient is rational, so with rational eps the whole matrix and its LDL pivots are exact.
"""
from fractions import Fraction as F
from math import factorial

# ---------------- polynomials as coefficient lists (index = degree), Fraction entries
def padd(a, b):
    n = max(len(a), len(b)); return [(a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0)) for i in range(n)]
def pmul(a, b):
    if not a or not b: return []
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out
def pscale(a, c): return [x * c for x in a]

# ---------------- monic Laguerre for weight e^{-2u}: a_n=(2n+1)/2, b_n=n^2/4
def laguerre(N):
    ps = [[F(1)]]
    if N > 1: ps.append([F(-1, 2), F(1)])
    for n in range(1, N - 1):
        a, b = F(2 * n + 1, 2), F(n * n, 4)
        ps.append(padd(pmul([F(0), F(1)], ps[n]), padd(pscale(ps[n], -a), pscale(ps[n - 1], -b))))
    return ps[:N]

def norm2(n):  # ||p_n||^2 = (n!)^2 / 2^(2n+1)
    return F(factorial(n) ** 2, 2 ** (2 * n + 1))

# ---------------- R_mn(s) = int_0^s p_m(u) p_n(s-u) du
def conv_poly(pm, pn):
    out = []
    for i, a in enumerate(pm):
        if not a: continue
        for j, b in enumerate(pn):
            if not b: continue
            c = a * b * F(factorial(i) * factorial(j), factorial(i + j + 1))
            k = i + j + 1
            while len(out) <= k: out.append(F(0))
            out[k] += c
    return out

# ---------------- eps-series for G(s,eps) = exp(P), P = -sum_{r>=2} c_r eps^{r-1} s^r
def jets(kind, M):
    """P as a list over eps powers 0..M of polynomials in s."""
    P = [[] for _ in range(M + 1)]
    for r in range(2, M + 2):
        if kind == "theta":   c = F(1, factorial(r))          # exp(-(e^{eps s}-1)/eps)
        elif kind == "talpha": c = F(1, r)                     # (1 - delta s)^{1/delta}
        elif kind == "quad":  c = F(1, 2) if r == 2 else F(0)  # quadratic jet only
        else: raise ValueError(kind)
        if c and r - 1 <= M:
            term = [F(0)] * r + [-c]
            P[r - 1] = padd(P[r - 1], term)
    return P

def sexp(P, M):
    """exp of an eps-series with zero constant term, truncated at eps^M."""
    G = [[] for _ in range(M + 1)]; G[0] = [F(1)]
    term = [[] for _ in range(M + 1)]; term[0] = [F(1)]
    for j in range(1, M + 1):
        new = [[] for _ in range(M + 1)]
        for e1 in range(M + 1):
            if not term[e1]: continue
            for e2 in range(1, M + 1 - e1):
                if not P[e2]: continue
                new[e1 + e2] = padd(new[e1 + e2], pmul(term[e1], P[e2]))
        term = [pscale(x, F(1, j)) if x else [] for x in new]
        if not any(term): break
        G = [padd(G[i], term[i]) for i in range(M + 1)]
    return G

def integrate(poly):  # int_0^inf e^{-2s} poly(s) ds
    return sum(c * F(factorial(j), 2 ** (j + 1)) for j, c in enumerate(poly) if c)

def build(N, kind, eps, M):
    ps = laguerre(N)
    G = sexp(jets(kind, M), M)
    Gs = []  # G with eps substituted
    for e, poly in enumerate(G):
        if poly: Gs = padd(Gs, pscale(poly, eps ** e))
    A = [[F(0)] * N for _ in range(N)]
    for m in range(N):
        for n in range(m, N):
            val = integrate(pmul(Gs, conv_poly(ps[m], ps[n])))
            A[m][n] = A[n][m] = val
    # symmetric normalisation: 1/(||p_m|| ||p_n||) = 2 * 2^(m+n) / (m! n!), rational
    At = [[A[m][n] * F(2 * 2 ** (m + n), factorial(m) * factorial(n)) for n in range(N)] for m in range(N)]
    return At

def ldl_pivots(M):
    n = len(M); A = [row[:] for row in M]; d = []
    for k in range(n):
        d.append(A[k][k])
        if A[k][k] == 0: break
        for i in range(k + 1, n):
            f = A[i][k] / A[k][k]
            for j in range(k + 1, n):
                A[i][j] -= f * A[k][j]
    return d

if __name__ == "__main__":
    N, M = 7, 9
    conj = [F(factorial(n), 2 ** (2 * n + 1)) for n in range(N)]
    print("conjecture C_n = n!/2^(2n+1):", [str(c) for c in conj], "\n")
    for kind in ("theta", "talpha", "quad"):
        print(f"=== {kind} ===")
        for eps in (F(1, 100), F(1, 1000), F(1, 10000)):
            d = ldl_pivots(build(N, kind, eps, M))
            Cs = [float(d[n] / ((-1) ** n * eps ** n)) for n in range(len(d))]
            print(f"  eps=1/{int(1/eps):<6d} C_n ~ " + "  ".join(f"{c:.6f}" for c in Cs))
        print("  conjecture       " + "  ".join(f"{float(c):.6f}" for c in conj))
        print()
