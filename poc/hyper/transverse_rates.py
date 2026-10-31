"""Cumulant rates of X = c1 - c2 from the two-state critical surface, numerically.

Lambda(t, -t) = log(rho(1,1)/rho(e^t, e^-t)) is even and analytic; its Taylor coefficients c_2r give
kappa_2r(X)/k -> (2r)! c_2r if the joint quasi-powers hold.  Fitted by least squares on even powers
from Newton-converged values of rho.  Compared with the exact rate 10/27 (r=1), the forced rate
9 * (-94/6561) = -94/729 (r=2), and reported for r = 3, 4 where the marginals say nothing.
"""
from math import sqrt, log, exp, factorial
import json
import numpy as np

def Phi0(z, X, Y):
    D = sqrt(1 - 2 * z * (X + Y) + z * z * (X - Y) ** 2)
    return (1 + z * (X - Y) - D) / (2 * X * D)
def F(v, x, y):
    z, Re, Ro = v
    return np.array([x / (1 - Phi0(z, Re, Ro)) - Re, y / (1 - Phi0(z, Ro, Re)) - Ro])
def system(v, x, y):
    h = 1e-7; J = np.zeros((2, 2))
    for j in range(2):
        vp = v.copy(); vp[1 + j] += h; vm = v.copy(); vm[1 + j] -= h
        J[:, j] = (F(vp, x, y) - F(vm, x, y)) / (2 * h)
    f = F(v, x, y)
    return np.array([f[0], f[1], np.linalg.det(J)])
def crit(x, y, v0):
    v = v0.copy()
    for _ in range(80):
        g = system(v, x, y); Jn = np.zeros((3, 3)); h = 1e-6
        for j in range(3):
            vp = v.copy(); vp[j] += h; vm = v.copy(); vm[j] -= h
            Jn[:, j] = (system(vp, x, y) - system(vm, x, y)) / (2 * h)
        step = np.linalg.solve(Jn, -g); v = v + step
        if np.abs(step).max() < 1e-15: break
    return v

v11 = crit(1.0, 1.0, np.array([0.125, 1.5, 1.5]))
z11 = v11[0]
ts = np.linspace(-0.3, 0.3, 121)
vals = []
v = v11.copy()
for t in ts[ts >= 0]:
    v = crit(exp(t), exp(-t), v); vals.append((t, log(z11 / v[0])))
lam = {t: L for t, L in vals}
tt = np.array([t for t, _ in vals] + [-t for t, _ in vals if t > 0])
LL = np.array([L for _, L in vals] + [L for t, L in vals if t > 0])
out = {}
for deg in (12, 14, 16):
    A = np.stack([tt ** (2 * r) for r in range(1, deg // 2 + 1)], axis=1)
    coef, *_ = np.linalg.lstsq(A, LL, rcond=None)
    out[deg] = {2 * r: factorial(2 * r) * coef[r - 1] for r in range(1, 5)}
print("kappa_2r(X)/k from the critical surface (fit degree 12 / 14 / 16):")
exact = {2: 10 / 27, 4: -94 / 729}
for r in (2, 4, 6, 8):
    line = f"  r={r}: " + "  ".join(f"{out[d][r]:+.9f}" for d in (12, 14, 16))
    if r in exact: line += f"   exact {exact[r]:+.9f}"
    print(line)
json.dump({str(r): out[16][r] for r in (2, 4, 6, 8)}, open("../results/hyper_transverse_rates.json", "w"), indent=1)
