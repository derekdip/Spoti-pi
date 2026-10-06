"""Exact checks of the algebraic claims in the second note ("Exact variance, mobile structure, and the
Gaussian frontier"), sections 2, 5, 7, 8, 9, 10, 14 and 17.  Fractions throughout; nothing floating.
"""
from fractions import Fraction as Fr
from math import comb, factorial
import json, os, sys

K = 40                                    # series order in z
def Z(): return [Fr(0)] * (K + 1)
def mul(a, b):
    out = Z()
    for i, x in enumerate(a):
        if x == 0: continue
        for j in range(K + 1 - i):
            if b[j]: out[i + j] += x * b[j]
    return out
def add(a, b): return [x + y for x, y in zip(a, b)]
def sub(a, b): return [x - y for x, y in zip(a, b)]
def scale(a, c): return [x * c for x in a]
def const(c): o = Z(); o[0] = Fr(c); return o
def inv(a):
    out = Z(); out[0] = 1 / a[0]
    for n in range(1, K + 1): out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
    return out
def sqrt1p(w):                            # sqrt(1 + w) for w with w[0] = 0
    out = const(1); c = Fr(1)
    term = const(1)
    for n in range(1, K + 1):
        c = c * (Fr(1, 2) - n + 1) / n
        term = mul(term, w)
        out = add(out, scale(term, c))
    return out
def log1p(w):
    out = Z(); term = const(1)
    for n in range(1, K + 1):
        term = mul(term, w); out = add(out, scale(term, Fr((-1) ** (n + 1), n)))
    return out
def tderiv(a): return [n * a[n] for n in range(K + 1)]
one = const(1); t = Z(); t[1] = Fr(1)

M = Z()
for _ in range(K + 1): M = mul(t, mul(add(one, scale(M, 2)), add(one, scale(M, 2))))
w = mul(t, add(one, scale(M, 2)))
data = {r["k"]: r for r in json.load(open("../results/hyper_moments.json"))}
kd = max(data)
Q = mul(mul(M, M), inv(add(one, M)))
report = []
def check(name, ok): report.append((name, ok)); print(("ok   " if ok else "FAIL ") + name)

# --- section 2: U = M - M^2, D_z U = M(1+2M), z D_z U = w M, Q = z D_z U + w Q
U = sub(M, mul(M, M))
check("S2  U = M - M^2 has coefficients N_k", all(U[k] == data[k]["N"] for k in range(1, kd + 1)))
DU = tderiv(U)
check("S2  D_z U = M (1 + 2M)", DU == mul(M, add(one, scale(M, 2))))
check("S2  z D_z U = w M", mul(t, DU) == mul(w, M))
check("S2  Q = z D_z U + w Q", Q == add(mul(t, DU), mul(w, Q)))

# --- section 5: Lagrange formula (4); A, B closed forms; A = 2 M B
def lagrange_Q(k):                       # (1/k) [u^{k-2}] (2+u)/(1+u)^2 (1+2u)^{2k}
    n = k - 2
    if n < 0: return 0
    s = Fr(0)
    for j in range(n + 1):               # [u^j] (2+u)/(1+u)^2 = 2 (-1)^j (j+1) + (-1)^(j-1) j
        c = 2 * (-1) ** j * (j + 1) + ((-1) ** (j - 1) * j if j >= 1 else 0)
        s += c * comb(2 * k, n - j) * 2 ** (n - j)
    return s / k
check("S5  Lagrange formula (4) for Q_k", all(lagrange_Q(k) == data[k]["Q"] for k in range(1, kd + 1)))
den = inv(mul(sub(one, scale(M, 2)), add(one, M)))
A = scale(mul(mul(M, M), den), 2); B = mul(M, den)
check("S5  A = 2M^2/((1-2M)(1+M)) equals sum c1(c1-1)", all(A[k] == data[k]["s2"] - data[k]["L"] for k in range(1, kd + 1)))
check("S5  B = M/((1-2M)(1+M)) equals sum c1 c2", all(B[k] == data[k]["s11"] for k in range(1, kd + 1)))
check("S5  A = 2 M B", A == scale(mul(M, B), 2))

# --- section 7: singular expansions in eps = sqrt(1 - 8z) and the 1/k expansion of Q_k / L_k
E = 12                                    # order in eps
def eser(coeffs): return coeffs + [Fr(0)] * (E + 1 - len(coeffs))
def emul(a, b):
    out = [Fr(0)] * (E + 1)
    for i in range(E + 1):
        for j in range(E + 1 - i): out[i + j] += a[i] * b[j]
    return out
def einv(a):
    out = [Fr(0)] * (E + 1); out[0] = 1 / a[0]
    for n in range(1, E + 1): out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
    return out
eps = eser([Fr(0), Fr(1)])
Me = emul(eser([Fr(1), Fr(-1)]), einv(eser([Fr(2), Fr(2)])))           # (1 - eps) / (2 (1 + eps))
check("S7  M = (1-eps)/(2(1+eps)) solves M = z(1+2M)^2 with z = (1-eps^2)/8",
      Me == emul(eser([Fr(1, 8), Fr(0), Fr(-1, 8)]), emul(add_e := [x + y for x, y in zip(eser([Fr(1)]), [2 * m for m in Me])], add_e)))
Qe = emul(emul(Me, Me), einv([x + y for x, y in zip(eser([Fr(1)]), Me)]))
Qe_note = emul(emul(eser([Fr(1), Fr(-1)]), eser([Fr(1), Fr(-1)])), einv(emul(eser([Fr(2), Fr(2)]), eser([Fr(3), Fr(1)]))))
check("S7  Q = (1-eps)^2 / (2(1+eps)(3+eps))", Qe == Qe_note)
check("S7  Q = 1/6 - 5/9 eps + 23/27 eps^2 - 77/81 eps^3 + ...", Qe[:4] == [Fr(1, 6), Fr(-5, 9), Fr(23, 27), Fr(-77, 81)])
# [z^k] eps^j = 8^k (-1)^k binom(j/2, k); even j vanish for large k; ratio to j = 1 is a rational function of k
def ratio_series(j, order):              # binom(j/2,k)/binom(1/2,k) as a series in kappa = 1/k
    out = [Fr(0)] * (order + 1); out[0] = Fr(1)
    for i in range(1, (j - 1) // 2 + 1):
        a = Fr(1, 2) + i                  # factor a / (a - k) = -(a/k) / (1 - a/k)
        f = [Fr(0)] * (order + 1)
        for n in range(1, order + 1): f[n] = -a ** n
        new = [Fr(0)] * (order + 1)
        for p in range(order + 1):
            for q in range(order + 1 - p): new[p + q] += out[p] * f[q]
        out = new
    return out
ORD = 5
def kappa_expansion(series):
    tot = [Fr(0)] * (ORD + 1)
    for j in range(1, E + 1, 2):
        r = ratio_series(j, ORD)
        for n in range(ORD + 1): tot[n] += series[j] * r[n]
    return tot
num = kappa_expansion(Qe); denom = kappa_expansion(Me)
# ratio of two series in kappa
def kinv(a):
    out = [Fr(0)] * (ORD + 1); out[0] = 1 / a[0]
    for n in range(1, ORD + 1): out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
    return out
def kmul(a, b):
    out = [Fr(0)] * (ORD + 1)
    for i in range(ORD + 1):
        for j in range(ORD + 1 - i): out[i + j] += a[i] * b[j]
    return out
QL = kmul(num, kinv(denom))              # Q_k / L_k = sum QL[n] k^{-n}
print("     Q_k/L_k = " + " + ".join(f"({c}) k^-{n}" for n, c in enumerate(QL)))
check("S7  (6): Q_k/L_k = 5/9 - 16/(27k) + O(k^-2)", QL[0] == Fr(5, 9) and QL[1] == Fr(-16, 27))
# Var(c1-c2) = (2(k+2)/3) Q_k/L_k = (2/3) k QL + (4/3) QL : coefficient of k^0 is (2/3) QL[1] + (4/3) QL[0]
var_const = Fr(2, 3) * QL[1] + Fr(4, 3) * QL[0]
var_k1 = Fr(2, 3) * QL[2] + Fr(4, 3) * QL[1]
print(f"     Var(c1-c2) = 10/27 k + {var_const} + ({var_k1})/k + ...;  note's (7) claims constant 4/81")
check("S7  (7) constant term is 28/81, not 4/81", var_const == Fr(28, 81))
ok7 = True
for k in range(12, kd + 1):
    exact = Fr(2 * data[k]["Q"], data[k]["N"])
    pred = Fr(10, 27) * k + var_const + var_k1 / k + (Fr(2, 3) * QL[3] + Fr(4, 3) * QL[2]) / k ** 2
    ok7 &= abs(exact - pred) * k ** 3 < 30
print(f"     residual of the k^-2 truncation times k^3 at k={kd}: {float(abs(Fr(2*data[kd]['Q'], data[kd]['N']) - (Fr(10,27)*kd + var_const + var_k1/kd + (Fr(2,3)*QL[3] + Fr(4,3)*QL[2])/kd**2))*kd**3):.3f}")
check("S7  1/k expansion of Var(c1-c2) matches the exact data to O(k^-3)", ok7)

# --- section 8: the critical curve
for qv in [Fr(1, 2), Fr(1, 3), Fr(2, 5), Fr(3, 4)]:
    z = qv ** 3; u = (1 - qv ** 2) / (4 * qv ** 3)
    # F(z,u) = u - ((1-4zu)^{-1/2} - 1)/2 ; 1 - 4 z u = q^2 exactly
    F = u - (1 / qv - 1) / 2
    Fu = 1 - z / qv ** 3
    s_claim = (1 - qv) ** 2 * (1 + 2 * qv) / (4 * qv ** 3)
    check(f"S8  critical curve at q={qv}: F_u = 0 and F = (1-q)^2(1+2q)/(4q^3)", Fu == 0 and F == s_claim)
check("S8  s = 1 gives q = 1/2, rho = 1/8, u = 3/2", (1 - Fr(1, 2)) ** 2 * 2 / (4 * Fr(1, 8)) == 1 and Fr(1, 2) ** 3 == Fr(1, 8) and (1 - Fr(1, 4)) / (4 * Fr(1, 8)) == Fr(3, 2))

# --- section 9-10: Lambda(t) = -3 log(2q(t)), e^t = (1-q)^2 (1+2q) / (4 q^3), by exact series reversion
T = 10
def tser(c): return c + [Fr(0)] * (T + 1 - len(c))
def tmul(a, b):
    out = [Fr(0)] * (T + 1)
    for i in range(T + 1):
        for j in range(T + 1 - i): out[i + j] += a[i] * b[j]
    return out
def tlog1p(wv):
    out = [Fr(0)] * (T + 1); term = tser([Fr(1)])
    for n in range(1, T + 1):
        term = tmul(term, wv); out = [x + y for x, y in zip(out, [Fr((-1) ** (n + 1), n) * c for c in term])]
    return out
d = tser([Fr(0), Fr(1)])                  # delta, with 2q = 1 + delta
# t(delta) = 2 log(1 - d) + log(1 + d/2) - 3 log(1 + d)
tt = [2 * a + b - 3 * c for a, b, c in zip(tlog1p([-x for x in d]), tlog1p([x / 2 for x in d]), tlog1p(d))]
# revert: delta as a series in t
dl = [Fr(0)] * (T + 1)
for _ in range(T + 2):
    # delta = (t - sum_{n>=2} tt[n] delta^n) / tt[1]
    acc = tser([Fr(0), Fr(1)])
    pw = tser([Fr(1)])
    for n in range(2, T + 1):
        pw = tmul(pw, dl) if n > 2 else tmul(dl, dl)
        acc = [x - tt[n] * y for x, y in zip(acc, pw)]
    dl = [x / tt[1] for x in acc]
Lam = [-3 * x for x in tlog1p(dl)]
print("     Lambda(t) coefficients:", [str(c) for c in Lam[1:9]])
check("S9  (10): Lambda = 2/3 t + 5/81 t^2 - 7/2187 t^3 - 47/78732 t^4 + 469/6377292 t^5 + ...",
      Lam[1:6] == [Fr(2, 3), Fr(5, 81), Fr(-7, 2187), Fr(-47, 78732), Fr(469, 6377292)])
kap_pred = {r: (-1) ** r * Lam[r] * factorial(r) for r in range(1, 9)}      # kappa_r(c_i) ~ (-1)^r Lambda^(r)(0) k
print("     predicted kappa_r(c_i)/k:", {r: str(v) for r, v in kap_pred.items()})
check("S10 kappa_3, kappa_4, kappa_5 constants are 14/729, -94/6561, -4690/531441",
      kap_pred[3] == Fr(14, 729) and kap_pred[4] == Fr(-94, 6561) and kap_pred[5] == Fr(-4690, 531441))
json.dump({str(r): str(v) for r, v in kap_pred.items()}, open("../results/hyper_lambda_constants.json", "w"))

# --- section 14: the parity kernel K_i and the closed form of Phi_0
def Kser(X, Y):                           # sum_i z^i K_i(X, Y)
    out = Z()
    for i in range(1, K + 1):
        out[i] = sum(comb(i - 1, a) * comb(i, i - 1 - a) * X ** a * Y ** (i - 1 - a) for a in range(i))
    return out
R = add(one, M)
Phi_scalar = Z()
for i in range(1, K + 1):
    Ri = const(1)
    for _ in range(i - 1): Ri = mul(Ri, R)
    Phi_scalar = add(Phi_scalar, scale([c if n == i else 0 for n, c in enumerate(Ri[:K + 1])] if False else [Ri[n - i] if n >= i else Fr(0) for n in range(K + 1)], comb(2 * i - 1, i)))
X0, Y0 = Fr(3, 7), Fr(5, 11)
lhs = Kser(X0, Y0)
Delta = sqrt1p(add(scale(t, -2 * (X0 + Y0)), scale(mul(t, t), (X0 - Y0) ** 2)))
rhs_fixed = mul(sub(add(one, scale(t, X0 - Y0)), Delta), inv(scale(Delta, 2 * X0)))
rhs_note = scale(sub(sub(one, scale(t, X0 - Y0)), Delta), 1 / (2 * X0))
check("S14 K_i(R,R) = C(2i-1,i-1) R^(i-1): sum_i z^i K_i(R,R) = Phi(R)", all(
    sum(comb(i - 1, a) * comb(i, i - 1 - a) for a in range(i)) == comb(2 * i - 1, i) for i in range(1, 30)))
check("S14 note's (16) closed form", lhs == rhs_note)
check("S14 corrected closed form Phi_0 = (1 + z(X-Y) - Delta) / (2 X Delta)", lhs == rhs_fixed)

# --- section 17: Psi(R), lambda_-, and R / (1 - lambda_-) = 1 / (1 - w)
# (d_X - d_Y) K_i at X = Y = R  =  sum (a - b) C(i-1,a) C(i,b) R^(i-2)
Psi = Z()
for i in range(2, K + 1):
    coef = sum((a - (i - 1 - a)) * comb(i - 1, a) * comb(i, i - 1 - a) for a in range(i))
    Ri = const(1)
    for _ in range(i - 2): Ri = mul(Ri, R)
    Psi = add(Psi, scale([Ri[n - i] if n >= i else Fr(0) for n in range(K + 1)], -coef))
Psi_closed = mul(mul(M, M), inv(mul(add(one, scale(M, 2)), mul(add(one, M), add(one, M)))))
check("S17 (19): Psi(R) = M^2 / ((1+2M)(1+M)^2)", Psi == Psi_closed)
lam_minus = scale(mul(mul(R, R), Psi), -1)
check("S17 lambda_- = -M^2/(1+2M)", lam_minus == scale(mul(mul(M, M), inv(add(one, scale(M, 2)))), -1))
check("S17 (20): R/(1 - lambda_-) = 1/(1 - w)", mul(R, inv(sub(one, lam_minus))) == inv(sub(one, w)))

print("\nALL:", all(ok for _, ok in report), f"({sum(ok for _, ok in report)}/{len(report)})")
json.dump([{"check": n, "ok": ok} for n, ok in report], open("../results/hyper_note2_check.json", "w"), indent=1)
