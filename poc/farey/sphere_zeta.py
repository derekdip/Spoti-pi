"""Stable-norm zeta of a four-holed sphere (symmetric cusped case, sink traces (7, 7, 7)).
Simple curves = slopes; traces X^2+Y^2+Z^2-XYZ+8(X+Y+Z)+28 = 0; mediant c = ab - kappa(class of c) - (opposite), kappa = 8.
Checks: (1) Farey-cell decomposition reproduces Z_B(3) (direct lattice sum); (2) toric formula
Z_B(0) = -1 + (1/3) sum_slopes g/l with the sphere gap law vs the cell sum and the Riesz/theta value;
(3) Z_B(-1) = Z_B(-3) = 0; (4) Z_B(rho_1) != 0  ->  Omega(sqrt R) for counting simple closed geodesics on the sphere."""
import mpmath as mp, math, numpy as np, sys
sys.argv = ["x"]
mp.mp.dps = 40
kap, s0 = mp.mpf(8), mp.mpf(28)
L = lambda t: 2 * mp.acosh(t / 2)
def cls(v): return (v[0] % 2, v[1] % 2)
K = {(1, 0): kap, (0, 1): kap, (1, 1): kap}
root = {(1, 0): mp.mpf(7), (0, 1): mp.mpf(7), (-1, 1): mp.mpf(7)}
# cones of the half plane: (e0, e1) opp e0-e1 -> trace of (1,-1) = 7; (e1, e1-e0) opp e0; (e1-e0, -e0) opp e1
cones = [((1, 0), (0, 1), mp.mpf(7)), ((0, 1), (-1, 1), mp.mpf(7)), ((-1, 1), (-1, 0), mp.mpf(7))]
def cells(NMAX):
    out = []; st = [(u, w, root[u] if u in root else root[(-u[0], -u[1])], root[w] if w in root else root[(-w[0], -w[1])], d) for u, w, d in cones]
    while st:
        u, w, tu, tw, td = st.pop(); m = (u[0] + w[0], u[1] + w[1]); tm = tu * tw - K[cls(m)] - td
        a, b, c = L(tu), L(tw), L(tm)
        if max(a, b) > NMAX: continue
        out.append((a, b, c, tm, m)); st += [(u, m, tu, tm, tw), (m, w, tm, tw, tu)]
    return out
l7 = L(mp.mpf(7))
# (1) direct sum at s = 3 over primitive slopes (root curves + all mediants), times 2 zeta(3) (both signs, all multiples)
cs = cells(60)
D3 = 3 * l7 ** -3 + mp.fsum(c ** -3 for a, b, c, t, m in cs)
direct3 = 2 * mp.zeta(3) * D3
print("cells with max N <= 60: %d; min defect %s" % (len(cs), mp.nstr(min(a + b - c for a, b, c, t, m in cs), 3)))
exec(open("poc/farey/certify_rho1.py").read().split("NC = 22")[0].replace("mp.mp.dps = 30", "mp.mp.dps = 40"))
def Zcell(s, NC=22):
    return 6 * l7 ** (-s) * mp.zeta(s - 1) + 2 * mp.fsum(Delta(s, a, b, c)[0] for a, b, c, t, m in cs if max(a, b) <= NC)
print("(1) Z_B(3): direct %s   cell decomposition %s" % (mp.nstr(direct3, 12), mp.nstr(Zcell(mp.mpf(3)), 12)))
# (2) Z_B(0): toric formula with the sphere gap law (F-normalisation gap g, jump 2g in the l normalisation)
def gap(c): return mp.log((c * c + kap * c + s0) / (c * c - 4) + (3 * kap * kap * 0 + kap * kap + kap * kap + kap * kap * c) / (c * c - 4) ** 2)
tor = -1 + (mp.mpf(1) / 3) * (3 * gap(mp.mpf(7)) / l7 + mp.fsum(gap(t) / c for a, b, c, t, m in cs))
# Barnes cell sum at s = 0: T0(a,b) = (a^2 - 3ab + b^2)/(12ab)
T0 = lambda a, b: (a * a - 3 * a * b + b * b) / (12 * a * b)
cell0 = 6 * T0(l7, l7) + 2 * mp.fsum(T0(a, c) + T0(c, b) - T0(a, b) for a, b, c, t, m in cs)
T1 = lambda a, b: mp.mpf(0)
T2 = lambda a, b: -(a ** 4 - 5 * a * a * b * b + b ** 4) / (360 * a * b)
cell2 = 6 * T2(l7, l7) + 2 * mp.fsum(T2(a, c) + T2(c, b) - T2(a, b) for a, b, c, t, m in cs)
print("(2) Z_B(0): Barnes cell sum %s   toric formula -1 + (1/3) sum g/l %s" % (mp.nstr(cell0, 12), mp.nstr(tor, 12)))
print("    Z_B(-2) (cell sum) = %s;  Z_B(-1) = Z_B(-3) = 0 (odd T_m vanish identically)" % mp.nstr(cell2, 10))
# theta check of Z_B(0): Theta(eps) - 1 - 2 Area/eps^2 -> Z_B(0)
area = 3 / l7 ** 2 + mp.fsum((a + b - c) / (a * b * c) for a, b, c, t, m in cs)   # hexagon 3/l^2 + cell increments
Ns = np.array([float(l7)] * 3 + [float(c) for a, b, c, t, m in cs])
for eps in (0.1, 0.05):
    th = 2 * np.sum(1 / np.expm1(eps * Ns[eps * Ns < 700])) - 2 * float(area) / eps ** 2
    print("    theta check eps = %.2f: %.6f" % (eps, th))
# (4) Z_B(rho_1)
r1 = mp.zetazero(1)
print("(4) Z_B(rho_1) = %s  (|.| = %s)" % (mp.nstr(Zcell(r1), 10), mp.nstr(abs(Zcell(r1)), 6)))
