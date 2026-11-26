"""Z_B(0) for the stable-norm ball of the modular torus, two independent ways.
 (i)  theta:  Theta(eps) - 1 - 2 Area/eps^2  as eps -> 0, Theta(eps) - 1 = 2 sum_prim 1/(e^{eps l} - 1);
 (ii) Riesz:  sum_{v != 0} (R - N(v))_+ = (Area/3) R^3 + Z_B(0) R + Z_B(-1)/2 ... i.e. the linear coefficient (residue of A^(s) at s=1).
Quadratic forms give -1; the square max(|x|,|y|) gives 8 zeta(-1) = -2/3."""
import math, numpy as np
RMAX = 4000.0
def L(t): return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)
l3 = L(3); out = [l3, l3, l3]; st = [(3, 3, 3, ), (3, 3, 3), (3, 3, 3)]
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = L(tm)
    if lm > RMAX: continue
    out.append(lm); st.append((tu, tm, tw)); st.append((tm, tw, tu))
Ns = np.sort(np.array(out)); del out
area = 0.8918031660
print("primitive classes mod sign with l <= %g: %d" % (RMAX, len(Ns)))
print("(i) Theta(eps) - 1 - 2 Area/eps^2:")
vals = []
for eps in (0.5, 0.2, 0.1, 0.05, 0.03, 0.02, 0.015):
    x = eps * Ns; x = x[x < 700]
    th = 2 * np.sum(1 / np.expm1(x)) - 2 * area / eps ** 2
    vals.append((eps, th)); print("    eps = %.3f: %.6f" % (eps, th))
e = np.array([v[0] for v in vals]); t = np.array([v[1] for v in vals])
for model, cols in (("Z + a eps", [np.ones_like(e), e]), ("Z + a eps^(1/2) + b eps", [np.ones_like(e), np.sqrt(e), e])):
    k = e <= 0.1; X = np.array(cols).T[k]; c = np.linalg.lstsq(X, t[k], rcond=None)[0]
    print("    fit %-26s on eps <= 0.1: Z_B(0) = %.5f" % (model, c[0]))
# (ii) Riesz: A(R) = 2 sum_k sum_prim (R - k l)_+ ; fit cubic on R in [100, 1500]
mult = np.sort(np.concatenate([Ns[:np.searchsorted(Ns, 1600 / k, side='right')] * k for k in range(1, int(1600 / l3) + 1)]))
cs = np.concatenate([[0], np.cumsum(mult)])
Rs = np.linspace(100, 1500, 3000); n = np.searchsorted(mult, Rs); A = 2 * (n * Rs - cs[n])
for fixed in (False, True):
    if fixed:   # impose the known R^3 and R^2 coefficients: Area/3 and 0
        y = A - area / 3 * Rs ** 3; X = np.array([Rs, np.ones_like(Rs)]).T
        c = np.linalg.lstsq(X, y, rcond=None)[0]; print("(ii) Riesz, R^3 = Area/3 and R^2 = 0 imposed: linear coefficient = %.5f, const %.4f" % (c[0], c[1]))
    else:
        X = np.array([Rs ** 3, Rs ** 2, Rs, np.ones_like(Rs)]).T; c = np.linalg.lstsq(X, A, rcond=None)[0]
        print("(ii) Riesz, free cubic: R^3 %.8f (Area/3 = %.8f), R^2 %.2e, linear %.5f" % (c[0], area / 3, c[1], c[2]))
