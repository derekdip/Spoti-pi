"""Exact Taylor expansion of the two-state critical surface along a direction, by Newton's method in
the ring of truncated power series over Q.

The two-state system is made polynomial with the Lagrange auxiliary T = z(1 + R_e T)(1 + R_o T), which
is symmetric in (R_e, R_o), so one T serves both kernels:
    Delta = 1 - z(R_e + R_o) - 2 z R_e R_o T,
    Phi_0(R_e, R_o) = z (1 + R_o T) / Delta,      Phi_0(R_o, R_e) = z (1 + R_e T) / Delta.
Unknowns (z, R_e, R_o, T) as power series in t along (x, y) = (e^{a t}, e^{b t}); equations
    P1 = R_e (Delta - z(1 + R_o T)) - x Delta = 0
    P2 = R_o (Delta - z(1 + R_e T)) - y Delta = 0
    P3 = T - z (1 + R_e T)(1 + R_o T) = 0
    P4 = det d(P1, P2, P3) / d(R_e, R_o, T) = 0          (the singular point of the branch)
started at the exact critical point (1/8, 3/2, 3/2, 2/9) at t = 0.  Then
    Lambda(a t, b t) = -log( z(t) / (1/8) ),   kappa_r(a c1 + b c2) / k -> r! [t^r] Lambda.
Directions run: (1,-1) transverse, (1,0) marginal, (1,1) diagonal (must reproduce the scalar curve).
"""
from fractions import Fraction as Fr
from math import factorial
import json, sys, time

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12     # series order in t
VARS = ("z", "Re", "Ro", "T", "x", "y")

# ---- multivariate polynomials: dict {exponent tuple: Fraction}
def padd(p, q):
    out = dict(p)
    for m, c in q.items():
        out[m] = out.get(m, 0) + c
        if out[m] == 0: del out[m]
    return out
def pscale(p, c): return {m: c * v for m, v in p.items()} if c else {}
def pmul(p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + b for a, b in zip(m1, m2))
            out[m] = out.get(m, 0) + c1 * c2
    return {m: c for m, c in out.items() if c != 0}
def pvar(name):
    e = [0] * 6; e[VARS.index(name)] = 1; return {tuple(e): Fr(1)}
def pconst(c): return {(0,) * 6: Fr(c)} if c else {}
def pdiff(p, name):
    i = VARS.index(name); out = {}
    for m, c in p.items():
        if m[i] == 0: continue
        mm = list(m); mm[i] -= 1
        out[tuple(mm)] = out.get(tuple(mm), 0) + c * m[i]
    return out
z, Re, Ro, T, x, y = (pvar(v) for v in VARS)
one = pconst(1)
Delta = padd(padd(one, pscale(pmul(z, padd(Re, Ro)), -1)), pscale(pmul(pmul(pmul(z, Re), Ro), T), -2))
P1 = padd(pmul(Re, padd(Delta, pscale(pmul(z, padd(one, pmul(Ro, T))), -1))), pscale(pmul(x, Delta), -1))
P2 = padd(pmul(Ro, padd(Delta, pscale(pmul(z, padd(one, pmul(Re, T))), -1))), pscale(pmul(y, Delta), -1))
P3 = padd(T, pscale(pmul(z, pmul(padd(one, pmul(Re, T)), padd(one, pmul(Ro, T)))), -1))
Jrows = [[pdiff(P, v) for v in ("Re", "Ro", "T")] for P in (P1, P2, P3)]
def det3(A):
    a, b, c = A[0]; d, e, f = A[1]; g, h, i = A[2]
    t1 = pmul(a, padd(pmul(e, i), pscale(pmul(f, h), -1)))
    t2 = pmul(b, padd(pmul(d, i), pscale(pmul(f, g), -1)))
    t3 = pmul(c, padd(pmul(d, h), pscale(pmul(e, g), -1)))
    return padd(padd(t1, pscale(t2, -1)), t3)
P4 = det3(Jrows)
EQS = [P1, P2, P3, P4]
UNK = ("z", "Re", "Ro", "T")
JAC = [[pdiff(P, u) for u in UNK] for P in EQS]

# ---- truncated power series in t
def sz(): return [Fr(0)] * (N + 1)
def smul(a, b):
    out = sz()
    for i, u in enumerate(a):
        if u == 0: continue
        for j in range(N + 1 - i):
            if b[j]: out[i + j] += u * b[j]
    return out
def sadd(a, b): return [u + v for u, v in zip(a, b)]
def sscale(a, c): return [u * c for u in a]
def sinv(a):
    out = sz(); out[0] = 1 / a[0]
    for n in range(1, N + 1): out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
    return out
def sconst(c): o = sz(); o[0] = Fr(c); return o
def sexp(c):                         # e^{c t}
    return [Fr(c) ** n / factorial(n) for n in range(N + 1)]
def slog1p(w):                       # log(1 + w), w[0] = 0
    out = sz(); term = sconst(1)
    for n in range(1, N + 1):
        term = smul(term, w); out = sadd(out, sscale(term, Fr((-1) ** (n + 1), n)))
    return out

def peval(p, env):
    """evaluate polynomial on series; env: name -> series; powers cached"""
    cache = {}
    def power(name, e):
        if e == 0: return sconst(1)
        if (name, e) not in cache:
            cache[(name, e)] = smul(power(name, e - 1), env[name]) if e > 1 else env[name]
        return cache[(name, e)]
    out = sz()
    for m, c in p.items():
        term = sconst(c)
        for name, e in zip(VARS, m):
            if e: term = smul(term, power(name, e))
        out = sadd(out, term)
    return out

def solve_series(A, b):
    """Gaussian elimination over Q[[t]] for A delta = b (4x4 of series)"""
    n = len(b); A = [row[:] for row in A]; b = b[:]
    for i in range(n):
        piv = next(r for r in range(i, n) if A[r][i][0] != 0)
        A[i], A[piv] = A[piv], A[i]; b[i], b[piv] = b[piv], b[i]
        inv = sinv(A[i][i])
        A[i] = [smul(v, inv) for v in A[i]]; b[i] = smul(b[i], inv)
        for r in range(n):
            if r != i and any(A[r][i]):
                f = A[r][i]
                A[r] = [sadd(v, sscale(smul(f, w), -1)) for v, w in zip(A[r], A[i])]
                b[r] = sadd(b[r], sscale(smul(f, b[i]), -1))
    return b

def surface(a, b):
    env = {"z": sconst(Fr(1, 8)), "Re": sconst(Fr(3, 2)), "Ro": sconst(Fr(3, 2)), "T": sconst(Fr(2, 9)),
           "x": sexp(a), "y": sexp(b)}
    for it in range(20):
        F = [peval(P, env) for P in EQS]
        if all(all(c == 0 for c in f) for f in F): break
        J = [[peval(d, env) for d in row] for row in JAC]
        delta = solve_series(J, [sscale(f, -1) for f in F])
        for u, d in zip(UNK, delta): env[u] = sadd(env[u], d)
    F = [peval(P, env) for P in EQS]
    assert all(all(c == 0 for c in f) for f in F), "Newton did not converge"
    zs = env["z"]
    Lam = sscale(slog1p(sscale(sadd(zs, sconst(Fr(-1, 8))), 8)), -1)     # -log(z / (1/8))
    return Lam, env

if __name__ == "__main__":
    t0 = time.time()
    res = {}
    for name, (a, b) in (("transverse (1,-1)", (1, -1)), ("marginal (1,0)", (1, 0)), ("diagonal (1,1)", (1, 1))):
        Lam, env = surface(a, b)
        rates = {r: factorial(r) * Lam[r] for r in range(1, N + 1)}
        res[name] = {str(r): str(v) for r, v in rates.items()}
        print(f"{name}: rates r! [t^r] Lambda")
        for r in range(1, N + 1):
            v = rates[r]
            print(f"   r={r:2d}: {str(v):>32s}  = {float(v):+.10f}")
        print(f"   z(t) = {[str(c) for c in env['z'][:5]]} ...")
    print(f"[{time.time()-t0:.1f}s]")
    tr = {int(r): Fr(v) for r, v in res["transverse (1,-1)"].items()}
    mg = {int(r): Fr(v) for r, v in res["marginal (1,0)"].items()}
    dg = {int(r): Fr(v) for r, v in res["diagonal (1,1)"].items()}
    checks = {
        "transverse odd rates vanish": all(tr[r] == 0 for r in range(1, N + 1, 2)),
        "transverse r=2 is 10/27": tr[2] == Fr(10, 27),
        "transverse r=4 is -94/729 = 9 kappa_4(c1)": tr[4] == Fr(-94, 729) and tr[4] == 9 * mg[4],
        "marginal r=1..5 are 1/3, 10/81, 14/729, -94/6561, -4690/531441":
            [mg[r] for r in range(1, 6)] == [Fr(1, 3), Fr(10, 81), Fr(14, 729), Fr(-94, 6561), Fr(-4690, 531441)],
        "marginal r=2 equals 3 * transverse ... i.e. transverse r=2 = 3 marginal r=2": tr[2] == 3 * mg[2],
        "diagonal reproduces the scalar curve (r=1..8)": [dg[r] for r in range(1, 9)] == [Fr(2, 3), Fr(10, 81), Fr(-14, 729), Fr(-94, 6561), Fr(4690, 531441), Fr(29170, 4782969), Fr(-369166, 43046721), Fr(-5647498, 1162261467)],
        "transverse r=6 equals candidate 4150/19683": tr[6] == Fr(4150, 19683),
    }
    alpha = -tr[6]; beta = Fr(729, 4) * (mg[6] + alpha / 27)
    checks["beta = (729/4)(kappa_6(c1) + alpha/27) equals candidate -2045/6561"] = beta == Fr(-2045, 6561)
    # degree 8: K8(a) = a8 e2^4 + b8 e2 e3^2 ; kappa_8(X) = a8 ; kappa_8(c1) = a8/81 - 4 b8/2187
    a8 = tr[8]; b8 = Fr(2187, 4) * (a8 / 81 - mg[8])
    for k, v in checks.items(): print(("ok   " if v else "FAIL "), k)
    print(f"degree-6 tensor: alpha = {alpha}, beta = {beta}")
    print(f"degree-8 tensor: a8 = {a8}, b8 = {b8}")
    json.dump({"order": N, "rates": res, "checks": checks, "alpha": str(alpha), "beta": str(beta), "a8": str(a8), "b8": str(b8)},
              open("../results/hyper_critical_surface.json", "w"), indent=1)
