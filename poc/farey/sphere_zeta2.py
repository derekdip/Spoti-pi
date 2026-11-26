"""Stable-norm zeta of a non-symmetric cusped four-holed sphere (boundary traces 2,2,2,2; base traces X = 7, Y = 9).
Root triangle (e0, e1, e0-e1) with Z = smaller Fricke root; cones (e0,e1) opp e0-e1, (e1, e1-e0) opp e0, (e1-e0, -e0) opp e1.
Root term: 2 [ sum_cones zeta_2(s; a+b | a, b) + zeta(s) (l_X^-s + l_Y^-s + l_Z^-s) ], Barnes zeta by Bernoulli series + quadrature.
Tests: toric formula Z_B(0) = -1 + (1/3) sum_slopes g/l (sphere gap law with linear Fricke terms) vs Barnes cell sum;
Z_B(3) cells vs direct (with tail estimate); Z_B(rho_1) != 0."""
import mpmath as mp, math, sys
exec(open("poc/farey/certify_rho1.py").read().split("NC = 22")[0].replace("mp.mp.dps = 30", "mp.mp.dps = 40"))
sys.path.insert(0, "poc/farey")
from sphere import setup, kappa, base, gap_formula
C = setup(*map(mp.mpf, (2, 2, 2, 2))); X, Y = mp.mpf(7), mp.mpf(9); Zs, Zl = base(C, X, Y)
print("cusped sphere: X = 7, Y = 9, Z(e0-e1) = %s, Z(e0+e1) = %s" % (mp.nstr(Zs, 10), mp.nstr(Zl, 10)))
Lg = lambda t: 2 * mp.acosh(t / 2)
tr = {(1, 0): X, (0, 1): Y, (1, -1): Zs, (-1, 1): Zs, (-1, 0): X}
cones = [((1, 0), (0, 1), (1, -1)), ((0, 1), (-1, 1), (1, 0)), ((-1, 1), (-1, 0), (0, 1))]
cells = []; st = [(u, w, tr[u], tr[w], tr[d]) for u, w, d in cones]
while st:
    u, w, tu, tw, td = st.pop(); m = (u[0] + w[0], u[1] + w[1]); tm = tu * tw - kappa(m, C) - td
    a, b, c = Lg(tu), Lg(tw), Lg(tm)
    if max(a, b) > 50: continue
    cells.append((a, b, c, tm, m, (u, w))); st += [(u, m, tu, tm, tw), (m, w, tm, tw, tu)]
print("cells: %d; min defect %s (must be > 0: corners genuine)" % (len(cells), mp.nstr(min(a + b - c for a, b, c, *_ in cells), 3)))
lX, lY, lZ = Lg(X), Lg(Y), Lg(Zs)
cone_l = [(lX, lY), (lY, lZ), (lZ, lX)]
def barnes(s, a, b):
    Cg = ser_g(a, b); I1 = sum(Cg.get(k, 0) * T0 ** (s + k) / (s + k) for k in range(-2, KSER))
    g = lambda t: 1 / ((mp.exp(a * t) - 1) * (mp.exp(b * t) - 1))
    I2 = mp.quad(lambda t: t ** (s - 1) * g(t), [T0, 0.25, 1, 4, 16, mp.inf])
    return (I1 + I2) / mp.gamma(s)
def Zcell(s, NC=22):
    root = 2 * (sum(barnes(s, a, b) for a, b in cone_l) + mp.zeta(s) * (lX ** -s + lY ** -s + lZ ** -s))
    return root + 2 * mp.fsum(Delta(s, a, b, c)[0] for a, b, c, *_ in cells if max(a, b) <= NC)
# Z_B(0): Barnes cell sum vs toric formula
TB0 = lambda a, b: (a * a - 3 * a * b + b * b) / (12 * a * b)
z2_0 = lambda a, b: (a * a + 3 * a * b + b * b) / (12 * a * b)
cell0 = 2 * (sum(z2_0(a, b) for a, b in cone_l) - mp.mpf(3) / 2) + 2 * mp.fsum(TB0(a, c) + TB0(c, b) - TB0(a, b) for a, b, c, *_ in cells)
def g_of(v, t, uw=None):
    km = kappa(v, C); others = [k for k in ((1, 0), (0, 1), (1, 1)) if k != (v[0] % 2, v[1] % 2)]
    kx, ky = [ {(1,0): C["p"], (0,1): C["q"], (1,1): C["r"]}[o] for o in others]
    return gap_formula(t, km, kx, ky, C["s"])
tor = -1 + (mp.mpf(1) / 3) * (g_of((1, 0), X) / lX + g_of((0, 1), Y) / lY + g_of((1, -1), Zs) / lZ + mp.fsum(g_of(m, t) / c for a, b, c, t, m, uw in cells))
print("Z_B(0): Barnes cell sum %s   toric formula -1 + (1/3) sum g/l %s   difference %s" % (mp.nstr(cell0, 14), mp.nstr(tor, 14), mp.nstr(cell0 - tor, 3)))
print("Z_B(3): cell decomposition %s" % mp.nstr(Zcell(mp.mpf(3)), 12))
D3 = lX ** -3 + lY ** -3 + lZ ** -3 + mp.fsum(c ** -3 for a, b, c, *_ in cells if c <= 50)
print("        direct over slopes with l <= 50: %s (+ tail ~ %s)" % (mp.nstr(2 * mp.zeta(3) * D3, 12), mp.nstr(2 * mp.zeta(3) * 2 * (3 / mp.pi ** 2) * (mp.mpf(1)) / 50 * 0, 3)))
r1 = mp.zetazero(1); z = Zcell(r1)
print("Z_B(rho_1) = %s  |Z_B(rho_1)| = %s" % (mp.nstr(z, 10), mp.nstr(abs(z), 6)))
