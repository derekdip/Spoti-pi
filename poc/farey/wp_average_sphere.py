"""Weil-Petersson average of the dual area over the moduli space of four-holed spheres (boundary lengths L1..L4).

Gap law factorisation (verified to 6e-13 on 2000 random cases): for a curve of length x separating {1,2} | {3,4},
    e^g = P(x; L1, L2) P(x; L3, L4),  P(x; A, B) = (cosh(x/2) + cosh((A+B)/2)) (cosh(x/2) + cosh((A-B)/2)) / sinh^2(x/2)
(one factor per pair of pants bounded by the curve). Mirzakhani unfolding, one class (pairing) at a time, V_{0,3} = 1:
    int over M_{0,4}(L) of A* = sum over pairings, pairs (A,B): 4 [K((A+B)/2) + K((A-B)/2)],  K(y) = y^4/12 + pi^2 y^2/6 + pi^4/24
                              = (sum L_i^2 + 4 pi^2)^2 / 8;   Vol = V_{0,4}(L) = (sum L_i^2 + 4 pi^2)/2;   average = V_{0,4}/2.
Independent check: integrate over a fundamental domain in Fenchel-Nielsen coordinates, one chart per pairing.
Chart for the class (1,0) curve alpha (separating {1,2}|{3,4}), X = 2 cosh(x/2): the transverse traces on the conic are
    Y(tau) = u_e + 2 sqrt(G) cosh(tau),  tr(alpha +- beta) = u_o + 2 sqrt(G) cosh(tau +- x/2),   G = e^{g_alpha},
u the period-2 particular solution of the fan; tau -> tau + x is the Dehn twist about alpha (two fan steps).
Domain: |tau| <= x/2 and alpha shorter than Y and both tr(alpha +- beta).
"""
import math, heapq, sys
import numpy as np


def setup(L):
    al, be, ga, de = [2 * math.cosh(l / 2) for l in L]
    return (al * be + ga * de, be * ga + al * de, al * ga + be * de), al * al + be * be + ga * ga + de * de + al * be * ga * de - 4


def kap(v, C): return {(1, 0): C[0], (0, 1): C[1], (1, 1): C[2]}[(v[0] % 2, v[1] % 2)]


def gap(c, km, kx, ky, s): return math.log((c * c + km * c + s) / (c * c - 4) + (kx * kx + ky * ky + kx * ky * c) / (c * c - 4)**2)


def chart(x, tau, C, s):
    """traces (X, Y, Z-, Z+) for alpha = e0 of length x, twist tau: Y = tr e1, Z- = tr(e0 - e1), Z+ = tr(e0 + e1)"""
    X = 2 * math.cosh(x / 2); p, q, r = C
    G = math.exp(gap(X, p, q, r, s))
    ue = (X * r + 2 * q) / (X * X - 4); uo = (X * q + 2 * r) / (X * X - 4)
    R = 2 * math.sqrt(G)
    return X, ue + R * math.cosh(tau), uo + R * math.cosh(tau - x / 2), uo + R * math.cosh(tau + x / 2), (ue, uo, R)


def Astar(X, Y, Zm, C, s, tol=1e-12, cap=200000):
    """dual area: all curves mod sign (e0, e1 and the interiors of the cones (e0, e1), (e0, -e1))"""
    tr = {(1, 0): X, (0, 1): Y, (0, -1): Y, (1, -1): Zm, (1, 1): X * Y - C[2] - Zm}
    def term(v, t):
        own = (v[0] % 2, v[1] % 2); km = kap(v, C); kx, ky = [kap(w, C) for w in ((1, 0), (0, 1), (1, 1)) if w != own]
        return gap(t, km, kx, ky, s) * math.acosh(t / 2)
    A = term((1, 0), X) + term((0, 1), Y); n = 0
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        h = [(-1.0, 0, e0, e1, opp)]
        while h and n < cap:
            _, _, Lv, Rv, o = heapq.heappop(h); m = (Lv[0] + Rv[0], Lv[1] + Rv[1]); t = tr[Lv] * tr[Rv] - kap(m, C) - tr[o]; tr[m] = t; n += 1
            tm = term(m, t); A += tm
            if tm > tol:
                for (a, b, oo) in ((Lv, m, Rv), (m, Rv, Lv)):
                    tt = tr[a] * tr[b]; heapq.heappush(h, (-tt**-2 * math.log(tt), n, a, b, oo))
    return A


def residual_check(L):
    C, s = setup(L); worst = 0
    for x in (0.4, 1.3, 2.7):
        for tau in (-1.0, 0.0, 0.3, 2.2):
            X, Y, Zm, Zp, _ = chart(x, tau, C, s)
            for Z in (Zm, Zp):
                worst = max(worst, abs(X * X + Y * Y + Z * Z - X * Y * Z + C[0] * X + C[1] * Y + C[2] * Z + s) / (X * Y * Z))
            worst = max(worst, abs(Zm + Zp - (X * Y - C[2])) / (X * Y))
    return worst


def integrate(L, nx=40, nt=16):
    tot_vol = tot_I = 0.0
    for perm in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):      # pairings {12|34}, {13|24}, {14|23} as the class of alpha
        Lp = [L[i] for i in perm]; C, s = setup(Lp)
        def interval(x):
            X, _, _, _, (ue, uo, R) = chart(x, 0.0, C, s)
            v = math.acosh(max(1.0, (X - ue) / R)); w = math.acosh(max(1.0, (X - uo) / R))
            lo, hi = v, x / 2 - w
            return (lo, hi) if hi > lo else None
        xs = np.linspace(1e-4, 30, 30000); ok = [interval(x) is not None for x in xs]
        xmax = xs[max(i for i, o in enumerate(ok) if o)]
        gx, wx = np.polynomial.legendre.leggauss(nx); gt, wt = np.polynomial.legendre.leggauss(nt)
        for u, wu in zip(gx, wx):
            sv = (u + 1) / 2; x = xmax * sv * sv; dx = xmax * 2 * sv * wu / 2
            iv = interval(x)
            if iv is None: continue
            for y, wy in zip(gt, wt):
                tau = iv[0] + (iv[1] - iv[0]) * (y + 1) / 2; dt = (iv[1] - iv[0]) * wy / 2
                X, Y, Zm, Zp, _ = chart(x, tau, C, s)
                tot_vol += 2 * dx * dt; tot_I += 2 * dx * dt * Astar(X, Y, Zm, C, s)
    return tot_vol, tot_I


if __name__ == "__main__":
    for L in ((0, 0, 0, 0), (1.0, 2.0, 0.5, 1.5), (3.0, 0.0, 2.0, 4.0)):
        print(f"L = {L}: Fricke residual of the chart {residual_check(L):.1e}", flush=True)
        S = sum(l * l for l in L) + 4 * math.pi**2
        vol, I = integrate(L)
        print(f"   Vol = {vol:.6f} (predicted V04 = {S / 2:.6f});  int A* = {I:.6f} (predicted {S * S / 8:.6f});  average = {I / vol:.6f} (predicted {S / 4:.6f})", flush=True)
