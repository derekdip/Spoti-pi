"""Large deviations and local limit from the critical surface, tested against exact coefficients.

rho(x, y): the fold of the Arques parametrisation under (X, U, Y) = (zx, z, zy), by Newton in floats.
Lambda(t) = log(1/(8 rho(e^t1, e^t2))).  Rate function I(u) = sup_t (t.u - Lambda(t)), the supremum
found by Newton on grad Lambda(t) = u.  Prediction (local limit with lattice span 1):
    Pr(C_k = m) = exp(-k I(u)) / (2 pi k sqrt(det Sigma(u))) . (1 + O(1/k)),   u = m/k,
so  -(1/k) log Pr - (log k)/k - I(u) = O(1/k).  Tested at off-centre lattice points with the exact
Lagrange-Good coefficients (coefficients.py).  Also: the Hessian of Lambda is positive definite on a
grid over the compact tilt box |t_i| <= 1.2 (numerical evidence for (13109), not a proof).
"""
from math import exp, log, sqrt, pi
import json, sys
import numpy as np
from coefficients import coefficient, N_of

def fold(x, y, v0):
    v = v0.copy()
    for _ in range(100):
        z, p, q, r = v
        F = np.array([z * x - p * (1 - q - r), z - q * (1 - p - r), z * y - r * (1 - p - q),
                      (1 - p - q - r) ** 2 - 4 * p * q * r])
        J = np.array([[x, -(1 - q - r), p, p],
                      [1, q, -(1 - p - r), q],
                      [y, r, r, -(1 - p - q)],
                      [0, -2 * (1 - p - q - r) - 4 * q * r, -2 * (1 - p - q - r) - 4 * p * r, -2 * (1 - p - q - r) - 4 * p * q]])
        step = np.linalg.solve(J, -F); v = v + step
        if np.abs(step).max() < 1e-15: break
    return v
V0 = np.array([0.125, 0.25, 0.25, 0.25])
_cache = {}
def Lam(t1, t2):
    v = fold(exp(t1), exp(t2), V0)
    return log(1 / (8 * v[0]))
def grad(t, h=1e-5):
    return np.array([(Lam(t[0] + h, t[1]) - Lam(t[0] - h, t[1])) / (2 * h),
                     (Lam(t[0], t[1] + h) - Lam(t[0], t[1] - h)) / (2 * h)])
def hess(t, h=1e-3):
    H = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            e_i = np.eye(2)[i] * h; e_j = np.eye(2)[j] * h
            H[i, j] = (Lam(*(t + e_i + e_j)) - Lam(*(t + e_i - e_j)) - Lam(*(t - e_i + e_j)) + Lam(*(t - e_i - e_j))) / (4 * h * h)
    return H
def tilt_for(u):
    t = np.zeros(2)
    for _ in range(50):
        g = grad(t) - np.array(u)
        if np.abs(g).max() < 1e-11: break
        t = t - np.linalg.solve(hess(t), g)
    return t
def rate(u):
    t = tilt_for(u); return float(t @ np.array(u) - Lam(*t)), t

if __name__ == "__main__":
    H0 = hess(np.zeros(2))
    print("Hessian at t = 0:", H0.round(7).tolist(), " exact (5/81)[[2,-1],[-1,2]] =", [[10/81, -5/81], [-5/81, 10/81]])
    # positive definiteness on a grid
    lam_min = 1e9; arg = None
    for a in np.linspace(-1.2, 1.2, 13):
        for b in np.linspace(-1.2, 1.2, 13):
            ev = np.linalg.eigvalsh(hess(np.array([a, b])))
            if ev[0] < lam_min: lam_min, arg = ev[0], (a, b)
    print(f"min eigenvalue of Hess Lambda over the grid |t_i| <= 1.2: {lam_min:.6f} at t = {arg}  (positive: {lam_min > 0})")
    # rate function against exact coefficients
    ks = [int(a) for a in sys.argv[1:]] or [121, 241]
    targets = [(0.40, 0.30), (0.25, 0.25), (0.45, 0.45), (0.20, 0.50), (0.50, 0.25)]
    print("LDP test:  -(1/k) log Pr(C_k = m) - (log k)/k  against  I(m/k)   (difference should be O(1/k))")
    out = []
    for (u1, u2) in targets:
        row = {"u": (u1, u2), "k": {}}
        for k in ks:
            c1, c2 = round(k * u1), round(k * u2); c3 = k + 2 - c1 - c2
            A = coefficient(c1, c3, c2); N = N_of(k)
            logPr = log(A) - log(N)
            uk = (c1 / k, c2 / k)
            I, t = rate(uk)
            lhs = -logPr / k - log(k) / k
            row["k"][k] = {"c": (c1, c2, c3), "I": I, "lhs": lhs, "diff": lhs - I}
            print(f"   u=({u1:.2f},{u2:.2f}) k={k:3d} c=({c1},{c2},{c3})  I(u)={I:.6f}  lhs={lhs:.6f}  diff={lhs-I:+.6f}  k*diff={k*(lhs-I):+.4f}  t=({t[0]:+.3f},{t[1]:+.3f})")
        out.append(row)
    json.dump({"hessian0": H0.tolist(), "grid_min_eig": lam_min, "grid_argmin": arg, "ldp": out},
              open("../results/hyper_ldp_check.json", "w"), indent=1, default=str)
