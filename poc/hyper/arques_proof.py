"""The parity mobile IS the Arques parametrisation: symbolic verification of the dictionary.

Claim (derived by hand from the two-state equations, see docs): with p = 1 - 1/(1 + R_e T),
r = 1 - 1/(1 + R_o T), q = z / Delta, the two-state solution is rational in (p, q, r):
    z   = q (1 - p - r)                      Delta = 1 - p - r
    R_e = p (1 - r) / z                      R_o   = r (1 - p) / z
    T   = q (1 - p - r) / ((1 - p)(1 - r))
    x   = p (1 - q - r) / z                  y     = r (1 - p - q) / z
so that X = z x = p(1-q-r), U = z = q(1-p-r), Y = z y = r(1-p-q): the Arques parametrisation.
Checks:
 1. P1, P2, P3 of critical_surface.py vanish identically after this substitution (rational identities).
 2. With Htilde = p q r (1 - p - q - r):  (d/dX + d/dY) Htilde = q (p + r), equivalently
    grad Htilde . adj(J) (e_X + e_Y) = q (p + r) det J  as polynomials, where J = d(X,U,Y)/d(p,q,r).
    Since R_e + R_o - x - y = q (p + r) / z, this is the identity (d/dx + d/dy) H = G + G^T for the
    parametrised series, which with H(x, 0) = 0 proves Htilde is the hypermap series.
 3. Fold structure: every component of grad Htilde . adj(J) is divisible by det J = (1-p-q-r)^2 - 4pqr,
    so Htilde is stationary along the kernel of J on the whole fold: no square-root term, the leading
    singular exponent is 3/2, and the coefficient count is k^{-5/2}.
 4. At the symmetric point the 3/2 coefficient is nonzero: U(z) = M - M^2 = 1/4 - e^2 + 2 e^3 + ...
"""
from fractions import Fraction as Fr
import json, sys
sys.argv = [sys.argv[0], "4"]
import critical_surface as cs

def var(i):
    e = [0] * 6; e[i] = 1; return {tuple(e): Fr(1)}
p, q, r = var(0), var(1), var(2)
one = cs.pconst(1)
def lin(*terms):
    out = one
    for tm in terms: out = cs.padd(out, cs.pscale(tm, -1))
    return out
mul, add, sc = cs.pmul, cs.padd, cs.pscale
zN = mul(q, lin(p, r))
subst = {                                           # name -> (numerator, denominator) in Q[p,q,r]
    "z":  (zN, one),
    "Re": (mul(p, lin(r)), zN),
    "Ro": (mul(r, lin(p)), zN),
    "T":  (zN, mul(lin(p), lin(r))),
    "x":  (mul(p, lin(q, r)), zN),
    "y":  (mul(r, lin(p, q)), zN),
}
def ppow(P, e):
    out = one
    for _ in range(e): out = mul(out, P)
    return out
def rational_eval(P):
    """numerator of P(subst) over the common denominator prod den_v^{E_v}; returns numerator polynomial"""
    E = {v: max((m[i] for m in P), default=0) for i, v in enumerate(cs.VARS)}
    total = {}
    for m, c in P.items():
        term = cs.pconst(c)
        for i, v in enumerate(cs.VARS):
            num, den = subst[v]
            term = mul(term, ppow(num, m[i]))
            term = mul(term, ppow(den, E[v] - m[i]))
        total = add(total, term)
    return total
ok1 = all(rational_eval(P) == {} for P in (cs.P1, cs.P2, cs.P3))
print("1. two-state equations P1, P2, P3 vanish identically under the dictionary:", ok1)

# 2. the derivative identity
X = mul(p, lin(q, r)); U = mul(q, lin(p, r)); Y = mul(r, lin(p, q))
Ht = mul(mul(mul(p, q), r), lin(p, q, r))
J = [[cs.pdiff(f, v) for v in ("z", "Re", "Ro")] for f in (X, U, Y)]       # slots 0,1,2 = p,q,r
def cof(i, j):
    rows = [rr for rr in range(3) if rr != i]; cols = [cc for cc in range(3) if cc != j]
    a, b = J[rows[0]][cols[0]], J[rows[0]][cols[1]]; c, d = J[rows[1]][cols[0]], J[rows[1]][cols[1]]
    return sc(add(mul(a, d), sc(mul(b, c), -1)), (-1) ** (i + j))
adj = [[cof(j, i) for j in range(3)] for i in range(3)]                     # adj = cofactor transpose
detJ = cs.det3(J)
grad = [cs.pdiff(Ht, v) for v in ("z", "Re", "Ro")]
w = [add(add(mul(grad[0], adj[0][j]), mul(grad[1], adj[1][j])), mul(grad[2], adj[2][j])) for j in range(3)]  # w_j = dHt/d(X,U,Y)_j * detJ
lhs = add(w[0], w[2])
rhs = mul(mul(q, add(p, r)), detJ)
ok2 = add(lhs, sc(rhs, -1)) == {}
print("2. (d/dX + d/dY) Htilde = q (p + r), i.e. grad.adj(J)(e_X + e_Y) = q(p+r) det J:", ok2)
# and, by symmetry, the full pointed series
tot = add(add(w[0], w[1]), w[2])
e2 = add(add(mul(p, q), mul(q, r)), mul(r, p))
ok2b = add(tot, sc(mul(e2, detJ), -1)) == {}
print("   (d/dX + d/dU + d/dY) Htilde = pq + qr + rp:", ok2b)

# 3. divisibility of each w_j by detJ (monic quadratic in q): reduce and check the remainder
def reduce_mod_det(P):
    P = dict(P)
    # detJ = q^2 + (lower in q); write detJ = q^2 + L, so q^2 == -L
    L = {m: c for m, c in detJ.items() if m[1] < 2}
    assert detJ.get((0, 2, 0, 0, 0, 0)) == 1 and all(m[1] <= 2 for m in detJ)
    while True:
        high = [m for m in P if m[1] >= 2]
        if not high: break
        m = max(high, key=lambda mm: mm[1]); c = P.pop(m)
        mm = list(m); mm[1] -= 2
        P = add(P, sc(mul({tuple(mm): Fr(1)}, L), -c))
    return P
ok3 = all(reduce_mod_det(wj) == {} for wj in w)
print("3. every component of grad Htilde . adj(J) is divisible by det J (no square-root term on the fold):", ok3)
# and the same for the pointed series e2? (not needed) ; check that grad Htilde itself is NOT divisible (sanity)
print("   sanity: grad Htilde itself is not divisible by det J:", not all(reduce_mod_det(g) == {} for g in grad))

# 4. singular expansion of U(z) = M - M^2 at the symmetric point
E = 8
def emul(a, b):
    out = [Fr(0)] * (E + 1)
    for i in range(E + 1):
        for j in range(E + 1 - i): out[i + j] += a[i] * b[j]
    return out
def einv(a):
    out = [Fr(0)] * (E + 1); out[0] = 1 / a[0]
    for n in range(1, E + 1): out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
    return out
Me = emul([Fr(1), Fr(-1)] + [Fr(0)] * (E - 1), einv([Fr(2), Fr(2)] + [Fr(0)] * (E - 1)))
Ue = [a - b for a, b in zip(Me, emul(Me, Me))]
print("4. U = M - M^2 in eps = sqrt(1-8z):", [str(c) for c in Ue[:5]], " -> no eps^1 term, eps^3 coefficient", Ue[3])
ok4 = Ue[1] == 0 and Ue[3] != 0
print("ALL:", ok1 and ok2 and ok2b and ok3 and ok4)
json.dump({"dictionary": ok1, "derivative_identity": ok2, "pointed_is_e2": ok2b, "fold_stationary": ok3,
           "U_expansion": [str(c) for c in Ue[:6]]}, open("../results/hyper_arques_proof.json", "w"), indent=1)
