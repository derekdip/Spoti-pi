"""The degree-six test and the marginal cumulant constants, from the exact order-8 data.

Reads hyper_cumulants_X.json (X = c1 - c2) and hyper_cumulants_c1.json.  Exact relations forced by
S_3 symmetry and c1 + c2 + c3 = k + 2 are checked at every k:
    odd cumulants of X vanish;  kappa_2(X) = 3 kappa_2(c1);  kappa_4(X) = 9 kappa_4(c1);
    kappa_1(c1) = (k+2)/3;  kappa_2(c1) = 2 Q_k / (3 N_k).
Growth: each cumulant is fitted exactly on its last m values to a k + b + c/k + ... and the linear
coefficient is compared with the constant predicted by the critical curve (hyper_lambda_constants.json)
for the marginal cumulants, and reported as new for kappa_6(X) and kappa_8(X), which the marginals do
not determine.  kappa_6(X) = O(k) is the note's degree-six test.
"""
from fractions import Fraction as Fr
import json, sys

X = {r["k"]: r for r in json.load(open("../results/hyper_cumulants_X.json"))}
C = {r["k"]: r for r in json.load(open("../results/hyper_cumulants_c1.json"))}
mom = {r["k"]: r for r in json.load(open("../results/hyper_moments.json"))}
pred = {int(r): Fr(v) for r, v in json.load(open("../results/hyper_lambda_constants.json")).items()}
K = min(max(X), max(C)); J = len(X[1]["kappa"])
kX = {k: [None] + [Fr(v) for v in X[k]["kappa"]] for k in X}
kC = {k: [None] + [Fr(v) for v in C[k]["kappa"]] for k in C}

ok = True
for k in range(1, K + 1):
    ok &= all(kX[k][r] == 0 for r in range(1, J + 1, 2))
    ok &= kX[k][2] == 3 * kC[k][2] and kX[k][4] == 9 * kC[k][4]
    ok &= kC[k][1] == Fr(k + 2, 3)
    if k in mom: ok &= kC[k][2] == Fr(2 * mom[k]["Q"], 3 * mom[k]["N"])
print(f"exact relations (odd kappa(X) = 0, kappa2(X) = 3 kappa2(c1), kappa4(X) = 9 kappa4(c1), "
      f"kappa1(c1) = (k+2)/3, kappa2(c1) = 2Q/(3N)) at every k <= {K}:", ok)

def fit_linear(seq, m):
    """exact solve of kappa(k) = a k + b + c/k + ... (m unknowns) on the last m points; returns a"""
    ks = list(range(K - m + 1, K + 1))
    A = [[Fr(k), Fr(1)] + [Fr(1, k ** p) for p in range(1, m - 1)] for k in ks]
    b = [seq[k] for k in ks]
    n = m
    for i in range(n):                      # Gaussian elimination
        piv = next(r for r in range(i, n) if A[r][i] != 0)
        A[i], A[piv] = A[piv], A[i]; b[i], b[piv] = b[piv], b[i]
        for r in range(n):
            if r != i and A[r][i] != 0:
                f = A[r][i] / A[i][i]
                A[r] = [x - f * y for x, y in zip(A[r], A[i])]; b[r] -= f * b[i]
    return b[0] / A[0][0]

print("\nmarginal cumulants of c1: fitted linear coefficient (last 4/5/6 points) against the critical-curve prediction")
print(" r | fit m=4 | fit m=5 | fit m=6 | predicted (-1)^r Lambda^(r)(0) | value")
for r in range(2, J + 1):
    fits = [fit_linear({k: kC[k][r] for k in kC}, m) for m in (4, 5, 6)]
    print(f" {r} | " + " | ".join(f"{float(f):+.7f}" for f in fits) + f" | {pred[r]} | {float(pred[r]):+.7f}")

print("\ncumulants of X = c1 - c2: growth")
print(" r | kappa_r(X) at K | /K | /K^2 | /K^3 | fit m=4 | fit m=5 | fit m=6 | forced by marginals?")
for r in range(2, J + 1, 2):
    v = kX[K][r]
    fits = [fit_linear({k: kX[k][r] for k in kX}, m) for m in (4, 5, 6)]
    forced = {2: "yes: 3 kappa_2(c1)", 4: "yes: 9 kappa_4(c1)", 6: "no (e2^3, e3^2)", 8: "no (e2^4, e2 e3^2)"}[r]
    print(f" {r} | {float(v):+.6f} | {float(v/K):+.6f} | {float(v/K**2):+.6f} | {float(v/K**3):+.6f} | "
          + " | ".join(f"{float(f):+.7f}" for f in fits) + f" | {forced}")

print("\nkappa_6(X) at every k, and first differences (a linear law gives a constant difference):")
print("  k: " + " ".join(f"{k}" for k in range(2, K + 1)))
print("  kappa_6(X): " + " ".join(f"{float(kX[k][6]):.4f}" for k in range(2, K + 1)))
print("  diff      : " + " ".join(f"{float(kX[k][6] - kX[k-1][6]):+.4f}" for k in range(3, K + 1)))

# decomposition of the degree-6 invariant cumulant tensor: K6(a) = alpha e2(a)^3 + beta e3(a)^2
a6 = fit_linear({k: kX[k][6] for k in kX}, 6); alpha = -a6
beta = Fr(729, 4) * (pred[6] + alpha / 27)
print(f"\ndegree-6 tensor: alpha = -lim kappa_6(X)/k ~ {float(alpha):+.7f},  beta = (729/4)(kappa_6(c1)/k + alpha/27) ~ {float(beta):+.7f}")
for n in range(6, 16):
    v = a6 * 3 ** n
    if abs(v - round(v)) < 0.02: print(f"  kappa_6(X)/k * 3^{n} = {float(v):.4f}  (near integer {round(v)}: candidate {round(v)}/3^{n})"); break
else:
    print("  no small 3-power rational found for kappa_6(X)/k within 0.02")

# Gaussian-limit predictions for the raw moments
print("\nraw moments of X against the Gaussian limits 3 sigma^4 and 15 sigma^6, sigma^2 = 10k/27 + 28/81:")
for k in (8, 16, 24, K):
    if k > K: continue
    N = X[k]["N"]; S = X[k]["sums"]
    s2 = Fr(10, 27) * k + Fr(28, 81)
    m4, m6 = Fr(S[4], N), Fr(S[6], N)
    print(f"  k={k:2d}  E[X^4]/(3 sigma^4) = {float(m4 / (3 * s2**2)):.5f}   E[X^6]/(15 sigma^6) = {float(m6 / (15 * s2**3)):.5f}")
json.dump({"K": K, "alpha": str(alpha), "beta": str(beta), "a6_fit": str(a6)}, open("../results/hyper_degree6.json", "w"))
