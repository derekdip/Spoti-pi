"""The relative-parity mobile system and what it determines.

Two-state system (the note's (17), kernel corrected):
    R_e = x / (1 - Phi_0(R_e, R_o)),   R_o = y / (1 - Phi_0(R_o, R_e)),
    Phi_0(X, Y) = sum_i z^i K_i(X, Y) = (1 + z(X - Y) - Delta) / (2 X Delta),
    Delta = sqrt(1 - 2z(X + Y) + z^2 (X - Y)^2),
where the root's class carries weight x, its relative-parity class n_0 weight x and the other class n_1
weight y.  G(x, y) = R_e - x counts mobiles with a marked corner by (n_0, n_1).

Claim tested exactly (polynomial identity, k <= K):
    (d/dx + d/dy) H_k(x, y) = [z^k] ( G(x, y) + G(y, x) )                                   (*)
where H_k(x, y) = sum_{rooted hypermaps} x^c1 y^c2.  Pointing at a vertex and NOT weighting it makes
the global min-label parity irrelevant: the two orientations of the root edge contribute
x^{n_0} y^{n_1} + x^{n_1} y^{n_0} whichever class holds the minimum.  The weighted version
    x d/dx H + y d/dy H  ?=  x G(x, y) + y G(y, x)
is also tested and fails, which is the note's minimum-parity obstruction made concrete.

Then the critical surface rho(x, y) of the two-state system is found numerically (Newton) and the
Hessian of Lambda(t1, t2) = log(rho(1,1) / rho(e^t1, e^t2)) at 0 is compared with the exact
covariance rates: 10/81 on the diagonal, -5/81 off it, hence 10/27 in the transverse direction.
"""
from fractions import Fraction as Fr
from math import comb, sqrt, log, exp
import json, sys
import numpy as np

H = {int(k): v for k, v in json.load(open("../results/hyper_bivariate2.json")).items()}
K = max(H)

def two_state_series(x, y, K):
    """Fraction series in z (to order K) of R_e, R_o at numeric x, y."""
    def mul(a, b):
        out = [Fr(0)] * (K + 1)
        for i, u in enumerate(a):
            if u == 0: continue
            for j in range(K + 1 - i):
                if b[j]: out[i + j] += u * b[j]
        return out
    def inv(a):
        out = [Fr(0)] * (K + 1); out[0] = 1 / a[0]
        for n in range(1, K + 1): out[n] = -sum(a[i] * out[n - i] for i in range(1, n + 1)) / a[0]
        return out
    def Phi(X, Y):
        # sum_i z^i sum_{a+b=i-1} C(i-1,a) C(i,b) X^a Y^b, truncated at z^K
        Xp = [[Fr(1)] + [Fr(0)] * K]; Yp = [[Fr(1)] + [Fr(0)] * K]
        for _ in range(K): Xp.append(mul(Xp[-1], X)); Yp.append(mul(Yp[-1], Y))
        out = [Fr(0)] * (K + 1)
        for i in range(1, K + 1):
            acc = [Fr(0)] * (K + 1)
            for a in range(i):
                b = i - 1 - a
                term = mul(Xp[a], Yp[b]); c = comb(i - 1, a) * comb(i, b)
                acc = [p + c * q for p, q in zip(acc, term)]
            for n in range(K + 1 - i): out[n + i] += acc[n]
        return out
    Re = [Fr(x)] + [Fr(0)] * K; Ro = [Fr(y)] + [Fr(0)] * K
    for _ in range(K + 1):
        one = [Fr(1)] + [Fr(0)] * K
        Re_new = [Fr(x) * v for v in inv([p - q for p, q in zip(one, Phi(Re, Ro))])]
        Ro_new = [Fr(y) * v for v in inv([p - q for p, q in zip(one, Phi(Ro, Re))])]
        Re, Ro = Re_new, Ro_new
    return Re, Ro

def dH(k, x, y):        # (d/dx + d/dy) H_k at (x, y), and the weighted x d/dx + y d/dy
    s = Fr(0); sw = Fr(0)
    for c1 in range(1, k + 1):
        for c2 in range(1, k + 1):
            h = H[k][c1][c2]
            if h == 0: continue
            s += h * (c1 * Fr(x) ** (c1 - 1) * Fr(y) ** c2 + c2 * Fr(x) ** c1 * Fr(y) ** (c2 - 1))
            sw += h * (c1 + c2) * Fr(x) ** c1 * Fr(y) ** c2
    return s, sw

if __name__ == "__main__":
    Kz = min(K, int(sys.argv[1]) if len(sys.argv) > 1 else K)
    # (*) as a polynomial identity: both sides have degree <= Kz-1 in x and in y; agreement on a
    # Kz x Kz grid of distinct abscissae proves it for every k <= Kz at once
    grid = [Fr(p, 1) for p in range(1, Kz + 1)]
    ok_star, ok_weighted = True, True
    fails = 0
    for x in grid:
        for y in grid:
            Re, Ro = two_state_series(x, y, Kz)
            Re2, Ro2 = two_state_series(y, x, Kz)
            for k in range(1, Kz + 1):
                lhs, lhs_w = dH(k, x, y)
                rhs = Re[k] + Re2[k]                 # [z^k] (G(x,y) + G(y,x)), the -x, -y are order 0
                rhs_w = x * Re[k] + y * Re2[k]
                ok_star &= (lhs == rhs)
                if lhs_w != rhs_w: fails += 1
    print(f"(*) (d/dx + d/dy) H_k = [z^k](G(x,y) + G(y,x)) as polynomials, k <= {Kz}, on a {Kz}x{Kz} grid:", ok_star)
    print(f"weighted version x H_x + y H_y = x G(x,y) + y G(y,x): fails at {fails} of {Kz**3} (k, x, y) points; "
          "the pointed vertex's own weight is where the minimum-label parity enters")

    # ---- numeric critical surface of the two-state system
    def Phi0(z, X, Y):
        D = sqrt(1 - 2 * z * (X + Y) + z * z * (X - Y) ** 2)
        return (1 + z * (X - Y) - D) / (2 * X * D)
    def F(v, x, y):
        z, Re, Ro = v
        return np.array([x / (1 - Phi0(z, Re, Ro)) - Re, y / (1 - Phi0(z, Ro, Re)) - Ro])
    def system(v, x, y):
        z, Re, Ro = v
        h = 1e-7
        J = np.zeros((2, 2))
        for j in range(2):
            vp = v.copy(); vp[1 + j] += h; vm = v.copy(); vm[1 + j] -= h
            J[:, j] = (F(vp, x, y) - F(vm, x, y)) / (2 * h)
        f = F(v, x, y)
        return np.array([f[0], f[1], np.linalg.det(J)])
    def rho(x, y, v0):
        v = v0.copy()
        for _ in range(60):
            g = system(v, x, y)
            Jn = np.zeros((3, 3)); h = 1e-6
            for j in range(3):
                vp = v.copy(); vp[j] += h; vm = v.copy(); vm[j] -= h
                Jn[:, j] = (system(vp, x, y) - system(vm, x, y)) / (2 * h)
            step = np.linalg.solve(Jn, -g)
            v = v + step
            if np.abs(step).max() < 1e-14: break
        return v
    v11 = rho(1.0, 1.0, np.array([0.125, 1.5, 1.5]))
    print(f"critical point at (x,y)=(1,1): z = {v11[0]:.12f} (1/8), R_e = R_o = {v11[1]:.12f} (3/2)")
    def Lam(t1, t2):
        v = rho(exp(t1), exp(t2), v11)
        return log(v11[0] / v[0])
    def hess(dirn, h):
        f = lambda t: Lam(dirn[0] * t, dirn[1] * t)
        return (-f(2*h) + 16*f(h) - 30*f(0) + 16*f(-h) - f(-2*h)) / (12 * h * h)
    def grad(dirn, h):
        f = lambda t: Lam(dirn[0] * t, dirn[1] * t)
        return (-f(2*h) + 8*f(h) - 8*f(-h) + f(-2*h)) / (12 * h)
    res = {}
    for name, d, exact in (("diagonal (1,1): Var(c1+c2)/k", (1, 1), 10/81), ("transverse (1,-1): Var(c1-c2)/k", (1, -1), 10/27),
                           ("axis (1,0): Var(c1)/k", (1, 0), 10/81)):
        h1, h2 = hess(d, 0.02), hess(d, 0.01)
        val = (16 * h2 - h1) / 15
        res[name] = val
        print(f"Lambda'' in direction {name}: {val:.7f}   exact rate {exact:.7f}   diff {val-exact:+.1e}")
    g = grad((1, 0), 0.01)
    print(f"Lambda' in direction (1,0): {g:.7f}   exact mean rate 1/3 = {1/3:.7f}")
    json.dump({"identity_star_k_max": Kz, "identity_star": ok_star, "weighted_fails": fails,
               "hessian": res, "gradient_axis": g}, open("../results/hyper_parity_mobile.json", "w"), indent=1)
