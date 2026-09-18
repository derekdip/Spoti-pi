"""The Arques comparison made explicit.

A. The Jacobian determinant of X = p(1-q-r), U = q(1-p-r), Y = r(1-p-q) is (1-p-q-r)^2 - 4pqr.
B. The critical surface of that parametrisation under (X, U, Y) = (z x, z, z y), expanded exactly along
   (x, y) = (e^{at}, e^{bt}) by Newton in Q[[t]], is compared with the two-state mobile surface
   (critical_surface.py) to order 12 in three directions.
C. On the mobile solution, with Delta = 1 - z(R_e + R_o) - 2 z R_e R_o T, the note's (13040), (13038)
      x + y = 1 + 1/z - 3/(2 Delta) - Delta^3/(2 z^2),
      (x - y)^2 = (Delta - z)^3 (z - Delta^3) / (Delta^3 z^3)
   are tested as series identities, and the bridge Delta = 1 - p - r, q = z / Delta is tested.
D. The trivariate series Htilde(X, U, Y) = sum_maps X^c1 U^c3 Y^c2 (exact to total degree 14 from
   hyper_bivariate2.json) is searched for a rational expression P/D in the Arques parameters by a
   Pade-type null-space computation.
"""
from fractions import Fraction as Fr
from math import factorial
import json, sys, time
sys.argv = [sys.argv[0], "12"]
import critical_surface as cs
N = cs.N

# ---- A. symbolic determinant (reuse the polynomial tools of critical_surface with variables renamed)
PV = ("p", "q", "r", "_", "_", "_")
def var(i):
    e = [0] * 6; e[i] = 1; return {tuple(e): Fr(1)}
p, q, r = var(0), var(1), var(2)
one = cs.pconst(1)
def lin(*terms):  # 1 - sum(terms)
    out = one
    for tm in terms: out = cs.padd(out, cs.pscale(tm, -1))
    return out
X = cs.pmul(p, lin(q, r)); U = cs.pmul(q, lin(p, r)); Y = cs.pmul(r, lin(p, q))
J = [[cs.pdiff(f, v) for v in ("z", "Re", "Ro")] for f in (X, U, Y)]   # variable slots 0,1,2 are p,q,r
detJ = cs.det3(J)
theta = lin(p, q, r)
claim = cs.padd(cs.pmul(theta, theta), cs.pscale(cs.pmul(cs.pmul(p, q), r), -4))
print("A. det J = (1-p-q-r)^2 - 4pqr:", cs.padd(detJ, cs.pscale(claim, -1)) == {})

# ---- B. Arques critical surface along a direction, exact series
# unknowns (z, p, q, r) -> reuse slots ("z","Re","Ro","T") of the series machinery: p=Re, q=Ro, r=T
zv, pv, qv, rv, xv, yv = (cs.pvar(v) for v in cs.VARS)
E1 = cs.padd(cs.pmul(zv, xv), cs.pscale(cs.pmul(pv, lin(qv, rv)), -1))        # z x - p(1-q-r)
E2 = cs.padd(zv, cs.pscale(cs.pmul(qv, lin(pv, rv)), -1))                     # z   - q(1-p-r)
E3 = cs.padd(cs.pmul(zv, yv), cs.pscale(cs.pmul(rv, lin(pv, qv)), -1))        # z y - r(1-p-q)
th = lin(pv, qv, rv)
E4 = cs.padd(cs.pmul(th, th), cs.pscale(cs.pmul(cs.pmul(pv, qv), rv), -4))    # fold
AEQS = [E1, E2, E3, E4]
AJAC = [[cs.pdiff(P, u) for u in cs.UNK] for P in AEQS]
def arques_surface(a, b):
    env = {"z": cs.sconst(Fr(1, 8)), "Re": cs.sconst(Fr(1, 4)), "Ro": cs.sconst(Fr(1, 4)), "T": cs.sconst(Fr(1, 4)),
           "x": cs.sexp(a), "y": cs.sexp(b)}
    for it in range(20):
        F = [cs.peval(P, env) for P in AEQS]
        if all(all(c == 0 for c in f) for f in F): break
        Jm = [[cs.peval(d, env) for d in row] for row in AJAC]
        delta = cs.solve_series(Jm, [cs.sscale(f, -1) for f in F])
        for u, d in zip(cs.UNK, delta): env[u] = cs.sadd(env[u], d)
    F = [cs.peval(P, env) for P in AEQS]
    assert all(all(c == 0 for c in f) for f in F)
    return env
t0 = time.time()
okB = True
for name, (a, b) in (("transverse (1,-1)", (1, -1)), ("marginal (1,0)", (1, 0)), ("diagonal (1,1)", (1, 1))):
    envA = arques_surface(a, b)
    LamM, envM = cs.surface(a, b)
    same = envA["z"] == envM["z"]
    okB &= same
    print(f"B. {name}: Arques fold z(t) == two-state mobile z(t) to order {N}: {same}")
    if name == "transverse (1,-1)":
        envA_tr, envM_tr = envA, envM
print(f"   [{time.time()-t0:.1f}s]")

# ---- C. the (Delta, z) formulas on the mobile solution, and the bridge
def check_C(envA, envM, label):
    z, Re, Ro, T = (envM[k] for k in ("z", "Re", "Ro", "T"))
    x, y = envM["x"], envM["y"]
    Delta = cs.sadd(cs.sadd(cs.sconst(1), cs.sscale(cs.smul(z, cs.sadd(Re, Ro)), -1)),
                    cs.sscale(cs.smul(cs.smul(cs.smul(z, Re), Ro), T), -2))
    inv = cs.sinv
    lhs1 = cs.sadd(x, y)
    rhs1 = cs.sadd(cs.sadd(cs.sadd(cs.sconst(1), inv(z)), cs.sscale(inv(Delta), Fr(-3, 2))),
                   cs.sscale(cs.smul(cs.smul(cs.smul(Delta, Delta), Delta), inv(cs.smul(z, z))), Fr(-1, 2)))
    d = cs.sadd(x, cs.sscale(y, -1)); lhs2 = cs.smul(d, d)
    Dz = cs.sadd(Delta, cs.sscale(z, -1)); D3 = cs.smul(cs.smul(Delta, Delta), Delta)
    num = cs.smul(cs.smul(cs.smul(Dz, Dz), Dz), cs.sadd(z, cs.sscale(D3, -1)))
    den = cs.smul(D3, cs.smul(cs.smul(z, z), z))
    rhs2 = cs.smul(num, inv(den))
    ok1, ok2 = lhs1 == rhs1, lhs2 == rhs2
    # bridge: Delta = 1 - p - r, q = z / Delta with (p, q, r) = Arques (Re, Ro, T) slots
    pA, qA, rA = envA["Re"], envA["Ro"], envA["T"]
    ok3 = Delta == cs.sadd(cs.sconst(1), cs.sscale(cs.sadd(pA, rA), -1))
    ok4 = qA == cs.smul(z, inv(Delta))
    print(f"C. {label}: (13040) x+y formula {ok1}; (13038) (x-y)^2 formula {ok2}; Delta = 1-p-r {ok3}; q = z/Delta {ok4}")
    return ok1 and ok2 and ok3 and ok4
okC = check_C(envA_tr, envM_tr, "transverse")
envA_m = arques_surface(1, 0); _, envM_m = cs.surface(1, 0)
okC &= check_C(envA_m, envM_m, "marginal  ")

# ---- D. reconstruct Htilde as a rational function of (p, q, r)
DEG = 14
H = {int(k): v for k, v in json.load(open("../results/hyper_bivariate2.json")).items()}
def tz(): return {}
def tadd(a, b):
    out = dict(a)
    for m, c in b.items():
        out[m] = out.get(m, 0) + c
        if out[m] == 0: del out[m]
    return out
def tmul(a, b):
    out = {}
    for (a1, a2, a3), c1 in a.items():
        for (b1, b2, b3), c2 in b.items():
            if a1 + a2 + a3 + b1 + b2 + b3 > DEG: continue
            m = (a1 + b1, a2 + b2, a3 + b3)
            out[m] = out.get(m, 0) + c1 * c2
    return {m: c for m, c in out.items() if c != 0}
def tscale(a, c): return {m: c * v for m, v in a.items()}
Ht = {}
for k in range(1, 13):
    for c1 in range(1, k + 1):
        for c2 in range(1, k + 1):
            h = H[k][c1][c2]
            if h: Ht[(c1, k + 2 - c1 - c2, c2)] = Fr(h)          # X^c1 U^c3 Y^c2
Xs, Us, Ys = {(1, 0, 0): Fr(1)}, {(0, 1, 0): Fr(1)}, {(0, 0, 1): Fr(1)}
ps, qs, rs = dict(Xs), dict(Us), dict(Ys)
for _ in range(DEG + 1):                     # p = X + p(q + r), etc.
    ps, qs, rs = (tadd(Xs, tmul(ps, tadd(qs, rs))), tadd(Us, tmul(qs, tadd(ps, rs))), tadd(Ys, tmul(rs, tadd(ps, qs))))
# sanity: X == p (1 - q - r) as series
chk = tadd(Xs, tscale(tmul(ps, tadd({(0,0,0): Fr(1)}, tscale(tadd(qs, rs), -1))), -1))
print("D. inversion of the parametrisation to degree", DEG, ":", chk == {})
t0 = time.time()
def monomials(d):
    return [(i, j, l) for i in range(d + 1) for j in range(d + 1 - i) for l in range(d + 1 - i - j)]
pw = {}
def power(s, e, key):
    if (key, e) not in pw:
        pw[(key, e)] = {(0, 0, 0): Fr(1)} if e == 0 else tmul(power(s, e - 1, key), s)
    return pw[(key, e)]
def mono_series(i, j, l):
    return tmul(tmul(power(ps, i, "p"), power(qs, j, "q")), power(rs, l, "r"))
dP, dD = 6, 3
monP, monD = monomials(dP), monomials(dD)
cols = []                                   # unknown vector: [c_P (monP) ; c_D (monD)]; equation: P - Htilde * D = 0
for m in monP: cols.append(mono_series(*m))
for m in monD: cols.append(tscale(tmul(Ht, mono_series(*m)), -1))
rows = sorted({mm for col in cols for mm in col})
A = [[col.get(mm, Fr(0)) for col in cols] for mm in rows]
print(f"   Pade system: {len(rows)} equations, {len(cols)} unknowns (P deg <= {dP}, D deg <= {dD}) [{time.time()-t0:.1f}s]")
# null space by exact Gaussian elimination
ncol = len(cols); M = [row[:] for row in A]; pivcols = []; rrow = 0
for c in range(ncol):
    piv = next((i for i in range(rrow, len(M)) if M[i][c] != 0), None)
    if piv is None: continue
    M[rrow], M[piv] = M[piv], M[rrow]
    inv = 1 / M[rrow][c]; M[rrow] = [v * inv for v in M[rrow]]
    for i in range(len(M)):
        if i != rrow and M[i][c] != 0:
            f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rrow])]
    pivcols.append(c); rrow += 1
free = [c for c in range(ncol) if c not in pivcols]
print(f"   rank {rrow}, null space dimension {len(free)} [{time.time()-t0:.1f}s]")
sol = None
if free:
    fc = free[0]
    v = [Fr(0)] * ncol; v[fc] = Fr(1)
    for i, c in enumerate(pivcols): v[c] = -M[i][fc]
    Pc = {m: v[i] for i, m in enumerate(monP) if v[i] != 0}
    Dc = {m: v[len(monP) + i] for i, m in enumerate(monD) if v[len(monP) + i] != 0}
    scale = Dc.get((0, 0, 0), None) or next(iter(Dc.values()))
    Pc = {m: c / scale for m, c in Pc.items()}; Dc = {m: c / scale for m, c in Dc.items()}
    def show(poly):
        return " + ".join(f"({c}) p^{i} q^{j} r^{l}" for (i, j, l), c in sorted(poly.items()))
    print("   numerator   P =", show(Pc)); print("   denominator D =", show(Dc))
    sol = {"P": {str(m): str(c) for m, c in Pc.items()}, "D": {str(m): str(c) for m, c in Dc.items()}}
    # verify P - Htilde D = 0 to degree 14
    lhs = tz()
    for m, c in Pc.items(): lhs = tadd(lhs, tscale(mono_series(*m), c))
    for m, c in Dc.items(): lhs = tadd(lhs, tscale(tmul(Ht, mono_series(*m)), -c))
    print("   P = Htilde * D as series to total degree 14:", lhs == {})
json.dump({"A_det": True, "B_surfaces_agree": okB, "C_formulas_and_bridge": okC, "D_rational_form": sol},
          open("../results/hyper_arques_bridge.json", "w"), indent=1)
print("ALL:", okB and okC)
