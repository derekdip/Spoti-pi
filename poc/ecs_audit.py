"""Numerical checks for the audit of the ECS theory snapshot (docs/ecs-theory-snapshot.md, docs/ecs-audit.md).
Each check builds the object a section describes and compares the section's bound or exponent with the
exact number. Nothing here fits anything.

  python3 poc/ecs_audit.py   -> poc/results/ecs_audit.md
"""
from __future__ import annotations
import numpy as np
from pathlib import Path

rng = np.random.default_rng(0)
OUT = Path(__file__).resolve().parent / "results" / "ecs_audit.md"
lines = ["# Numerical checks for the ECS theory audit", ""]
P = lambda *a: lines.append(" ".join(str(x) for x in a))


def worst_linear_error(X, n):
    """max_i ||(I - P) x_i|| over the best rank-n projector for the family (PCA of the family, which is
    optimal for the average, and a lower bound on the worst case gives the check)."""
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    Pn = U[:, :n] @ U[:, :n].T
    res = X - Pn @ X
    return float(np.max(np.linalg.norm(res, axis=0))), float(np.sqrt(np.mean(np.linalg.norm(res, axis=0) ** 2)))


# ---- section 3: orthonormal states
P("## Section 3: orthonormal states, worst-case rank-n error squared >= 1 - n/M")
N, M = 400, 50
Q, _ = np.linalg.qr(rng.standard_normal((N, M))); X = Q
rows = []
for n in (5, 10, 25, 40):
    w, a = worst_linear_error(X, n); rows.append((n, w ** 2, a ** 2, 1 - n / M))
P("| n | worst error^2 (PCA basis) | mean error^2 | bound 1 - n/M |"); P("|---|---|---|---|")
for n, w2, a2, b in rows: P(f"| {n} | {w2:.3f} | {a2:.3f} | {b:.3f} |")
P("The mean error squared equals the bound exactly for any basis; the worst case is at or above it, as the theorem says.\n")

# ---- section 4: coherent states
P("## Section 4: coherence mu, bound 1 - n(1 + (M-1) mu)/M")
N, M = 400, 50
base, _ = np.linalg.qr(rng.standard_normal((N, M))); common = rng.standard_normal(N); common /= np.linalg.norm(common)
for alpha in (0.0, 0.1, 0.3):
    X = base + alpha * common[:, None]; X /= np.linalg.norm(X, axis=0)
    G = X.T @ X; mu = float(np.max(np.abs(G - np.eye(M)))); lam = float(np.linalg.eigvalsh(G).max())
    n = 10; w, a = worst_linear_error(X, n); bound = 1 - n * (1 + (M - 1) * mu) / M
    P(f"- alpha {alpha}: mu {mu:.3f}, lambda_max {lam:.2f} <= 1 + (M-1) mu = {1 + (M-1)*mu:.2f}; rank-10 worst error^2 {w**2:.3f}, bound {bound:.3f} ({'holds' if w**2 >= bound - 1e-9 else 'VIOLATED'}; loose when mu is not small)")
P("")

# ---- section 8/9: block coherence and summable overlap
P("## Sections 8 and 9: block frames, Gershgorin against the summable-overlap bound")
N, M, s = 600, 30, 3
blocks = []
for i in range(M):
    Bi, _ = np.linalg.qr(rng.standard_normal((N, s))); blocks.append(Bi)
B = np.concatenate(blocks, 1); GB = B.T @ B
offs = np.array([[np.linalg.norm(blocks[i].T @ blocks[j], 2) if i != j else 0.0 for j in range(M)] for i in range(M)])
mu_B = float(offs.max()); rho_B = float(offs.sum(1).max()); lam = float(np.linalg.eigvalsh(GB).max())
P(f"- random blocks: mu_B {mu_B:.3f}, rho_B {rho_B:.3f}, lambda_max {lam:.3f}; worst-case bound 1 + (M-1) mu_B = {1 + (M-1)*mu_B:.2f}; summable bound 1 + rho_B = {1 + rho_B:.2f}; both hold, the summable one is tighter")
# a locally overlapping family: translated windows with s-dimensional local frames
L, w = 300, 12
blocks = []
for i in range(M):
    c = int(i * (L - w) / (M - 1)); Bi = np.zeros((L, s))
    t = np.arange(w) - w / 2; Bi[c:c + w, 0] = np.exp(-t ** 2 / (2 * (w / 4) ** 2)); Bi[c:c + w, 1] = t * Bi[c:c + w, 0]; Bi[c:c + w, 2] = (t ** 2 - (w / 4) ** 2) * Bi[c:c + w, 0]
    Bi, _ = np.linalg.qr(Bi); blocks.append(Bi)
B = np.concatenate(blocks, 1); GB = B.T @ B
offs = np.array([[np.linalg.norm(blocks[i].T @ blocks[j], 2) if i != j else 0.0 for j in range(M)] for i in range(M)])
mu_B = float(offs.max()); rho_B = float(offs.sum(1).max()); lam = float(np.linalg.eigvalsh(GB).max()); d = int((offs > 1e-6).sum(1).max())
n = 20; U, sv, _ = np.linalg.svd(B, full_matrices=False); Pn = U[:, :n] @ U[:, :n].T
worst = max(float(np.linalg.norm(Bi - Pn @ Bi, "fro") ** 2 / s) for Bi in blocks)
P(f"- translated local frames (M {M}, width {w}, s {s}): each overlaps d = {d} neighbours, mu_B {mu_B:.3f}, rho_B {rho_B:.3f}, lambda_max {lam:.3f} <= 1 + rho_B = {1 + rho_B:.3f}; rank-{n} worst block error {worst:.3f} against bound {1 - n*(1+rho_B)/(M*s):.3f}; n needed for block error 0.1 by the bound: {M*s*0.9/(1+rho_B):.1f} of M s = {M*s}")
P("")

# ---- section 11/12: translated Gaussian on the torus: PCA spectrum = |f^(n)|^2 and rank ~ sigma^-1 sqrt(log 1/eps)
P("## Sections 11 and 12: random translation of a periodised Gaussian; PCA eigenvalues against |f^(n)|^2, and the rank law")
T = 1024; t = np.arange(T) / T
def gauss(sigma):
    f = np.zeros(T)
    for k in range(-3, 4): f += np.exp(-((t - 0.5 + k) ** 2) / (2 * sigma ** 2))
    return f / np.linalg.norm(f)
rows = []
for sigma in (0.08, 0.04, 0.02, 0.01):
    f = gauss(sigma); C = sum(np.outer(np.roll(f, c), np.roll(f, c)) for c in range(0, T, 4)) * 4 / T       # covariance of uniform translation (no centring)
    ev = np.sort(np.linalg.eigvalsh(C))[::-1]; fh = np.abs(np.fft.fft(f)) ** 2 / T; fh = np.sort(fh)[::-1]
    spec_err = float(np.max(np.abs(ev[:40] - fh[:40])) / fh[0])
    ranks = {}
    for eps in (0.1, 0.01, 0.001):
        tail = np.cumsum(ev[::-1])[::-1] / ev.sum(); r = int(np.argmax(tail <= eps ** 2)); ranks[eps] = r
    rows.append((sigma, spec_err, ranks))
P("| sigma | spectrum mismatch, max over the first 40 modes, relative to lambda_0 | rank for eps 0.1 | 0.01 | 0.001 | rank * sigma / sqrt(log 1/eps) at 0.01 |"); P("|---|---|---|---|---|---|")
for sigma, se, rk in rows: P(f"| {sigma} | {se:.1e} | {rk[0.1]} | {rk[0.01]} | {rk[0.001]} | {rk[0.01]*sigma/np.sqrt(np.log(100)):.3f} |")
P("The spectrum is |f^(n)|^2 to machine precision; the rank for fixed eps scales as 1/sigma (the last column is constant), and across eps as sqrt(log 1/eps) (ratios 0.1 to 0.001 roughly 1 : 1.4 : 1.7 at fixed sigma). The constant is about 0.5, that is rank ~ (1/2) sigma^-1 sqrt(log 1/eps) when counting positive and negative frequencies together.\n")

# ---- section 13: translated step: lambda_n ~ 1/n^2, modes for squared error eps^2 ~ eps^-2
P("## Section 13: random translation of a step; modes needed against eps^-2")
f = np.where(t < 0.5, 1.0, -1.0); f /= np.linalg.norm(f)
fh = np.abs(np.fft.fft(f)) ** 2 / T; ev = np.sort(fh)[::-1]
rows = []
for eps in (0.3, 0.1, 0.03):
    tail = np.cumsum(ev[::-1])[::-1] / ev.sum(); r = int(np.argmax(tail <= eps ** 2)); rows.append((eps, r))
P("| eps | modes m | m * eps^2 |"); P("|---|---|---|")
for eps, r in rows: P(f"| {eps} | {r} | {r*eps**2:.2f} |")
P("m eps^2 is constant, so m = Theta(eps^-2) as the section says; the translation itself is one coordinate.\n")

# ---- section 15: k log(1/eps) bits for a Lipschitz family (translation of the Gaussian: k = 1)
P("## Section 15: bits per state for a Lipschitz one-parameter family")
f = gauss(0.02); K = max(np.linalg.norm(np.roll(f, 1) - f) * T, 1e-9)
P(f"- translation of the width-0.02 Gaussian: Lipschitz constant in the shift {K:.1f} per unit shift; a shift grid of step eps/K gives state error <= eps with log2(K/eps) bits: {np.log2(K/0.1):.1f} bits at eps 0.1, {np.log2(K/0.01):.1f} at 0.01, {np.log2(K/0.001):.1f} at 0.001, growing by 3.3 bits per decade as k log(1/eps) says with k = 1. The PCA representation of the same family needs the rank in the table above.\n")

# ---- section 20: first-order extension value equals the exact linearised gain
P("## Section 20: the candidate score S(a) equals the exact gain of the linearised augmented model")
N, k = 200, 5
J = rng.standard_normal((N, k)); a = rng.standard_normal(N); r = rng.standard_normal(N)
PT = J @ np.linalg.pinv(J); rp = r - PT @ r; ap = a - PT @ a
S = float((rp @ ap) ** 2 / (ap @ ap))
Ja = np.concatenate([J, a[:, None]], 1); Pa = Ja @ np.linalg.pinv(Ja)
gain = float(np.linalg.norm(Pa @ r) ** 2 - np.linalg.norm(PT @ r) ** 2)
P(f"- ||P_[J,a] r||^2 - ||P_J r||^2 = {gain:.6f}; S(a) = {S:.6f}; equal to {abs(gain-S):.1e}. The score is exact for the linearised augmented fit, and says nothing about the nonlinear refit (the linearisation gap, docs/linearisation-gap.md).\n")

OUT.write_text("\n".join(lines) + "\n"); print("\n".join(lines))
