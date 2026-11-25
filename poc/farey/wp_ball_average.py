"""Weil-Petersson average of the stable-norm ball area, and the product of the two averages.

Prediction: in complexity one, #{simple gamma : l_gamma <= R} ~ (3/(4 pi^2)) Area(B) R^2 (primitive vectors mod sign in
the ball of radius R/2 in N = l/2 units), and Mirzakhani's unfolding gives int over moduli of #{l <= R} = R^2/2 per
mapping-class orbit (V_{0,3} = 1), independent of the boundary. Hence
    one-holed tori:     int Area(B) = 2 pi^2/3,  <Area(B)> = 16 pi^2/(L^2 + 4 pi^2)        (cusped: 4)
    four-holed spheres: int Area(B) = 2 pi^2 (3 orbits), <Area(B)> = 4 pi^2/(sum L^2 + 4 pi^2)  (cusped: 1)
and with <A*> from before:  <Area(B)> <A*> = pi^2  identically.
Check: integrate Area(B) (polygon through the corners +-v/N(v)) over the same fundamental domains as wp_average*.py.
"""
import math, sys, heapq
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import wp_average as WT, wp_average_sphere as WS
from limits import curves as torus_curves


def area_from(vecs_N):
    pts = sorted(((math.atan2(s * v[1], s * v[0]), s * v[0] / n, s * v[1] / n) for v, n in vecs_N for s in (1, -1)))
    return 0.5 * sum(p[1] * q[2] - q[1] * p[2] for p, q in zip(pts, pts[1:] + pts[:1]))


def torus_area(a, b, mu):
    cv, _ = torus_curves(a, b, mu, tol=1e-13)
    return area_from([(v, math.acosh(t / 2)) for v, t in cv.items()])


def sphere_area(X, Y, Zm, C, s, cap=200000, tol=1e-13):
    tr = {(1, 0): X, (0, 1): Y, (0, -1): Y, (1, -1): Zm, (1, 1): X * Y - C[2] - Zm}; out = {(1, 0): X, (0, 1): Y}; n = 0
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        h = [(-1.0, 0, e0, e1, opp)]
        while h and n < cap:
            _, _, Lv, Rv, o = heapq.heappop(h); m = (Lv[0] + Rv[0], Lv[1] + Rv[1]); t = tr[Lv] * tr[Rv] - WS.kap(m, C) - tr[o]; tr[m] = t; out[m] = t; n += 1
            if math.log(t) / t**2 > tol:
                for (a, b, oo) in ((Lv, m, Rv), (m, Rv, Lv)):
                    tt = tr[a] * tr[b]; heapq.heappush(h, (-math.log(tt) / tt**2, n, a, b, oo))
    return area_from([(v, math.acosh(t / 2)) for v, t in out.items()])


def torus_run(L, nl=48, nt=20):
    mu, C, tau_interval, lmax = WT.domain(L)
    xl, wl = np.polynomial.legendre.leggauss(nl); xt, wt = np.polynomial.legendre.leggauss(nt); vol = I = 0.0
    for x, w in zip(xl, wl):
        s = (x + 1) / 2; l = lmax * s * s; dl = lmax * 2 * s * w / 2; iv = tau_interval(l)
        if iv is None: continue
        for y, v in zip(xt, wt):
            tau = iv[0] + (iv[1] - iv[0]) * (y + 1) / 2; dt = (iv[1] - iv[0]) * v / 2
            vol += 2 * dl * dt; I += 2 * dl * dt * torus_area(2 * math.cosh(l / 2), C(l) * math.cosh(tau / 2), mu)
    return vol, I


def sphere_run(L, nx=40, nt=16):
    vol = I = 0.0
    for perm in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        Lp = [L[i] for i in perm]; C, s = WS.setup(Lp)
        def interval(x):
            X, _, _, _, (ue, uo, R) = WS.chart(x, 0.0, C, s)
            v = math.acosh(max(1.0, (X - ue) / R)); w = math.acosh(max(1.0, (X - uo) / R)); return (v, x / 2 - w) if x / 2 - w > v else None
        xs = np.linspace(1e-4, 30, 30000); xmax = xs[max(i for i, x in enumerate(xs) if interval(x) is not None)]
        gx, wx = np.polynomial.legendre.leggauss(nx); gt, wt = np.polynomial.legendre.leggauss(nt)
        for u, wu in zip(gx, wx):
            sv = (u + 1) / 2; x = xmax * sv * sv; dx = xmax * 2 * sv * wu / 2; iv = interval(x)
            if iv is None: continue
            for y, wy in zip(gt, wt):
                tau = iv[0] + (iv[1] - iv[0]) * (y + 1) / 2; dt = (iv[1] - iv[0]) * wy / 2
                X, Y, Zm, Zp, _ = WS.chart(x, tau, C, s)
                vol += 2 * dx * dt; I += 2 * dx * dt * sphere_area(X, Y, Zm, C, s)
    return vol, I


if __name__ == "__main__":
    pi2 = math.pi**2
    for L in (0.0, 2.0):
        vol, I = torus_run(L); S = L * L + 4 * pi2
        print(f"torus L = {L}: int Area(B) = {I:.6f} (predicted 2 pi^2/3 = {2 * pi2 / 3:.6f});  <Area(B)> = {I / vol:.6f} (predicted {16 * pi2 / S:.6f});  "
              f"<Area(B)> x (L^2 + 4 pi^2)/16 = {I / vol * S / 16:.6f} (predicted pi^2 = {pi2:.6f})", flush=True)
    for L in ((0, 0, 0, 0), (1.0, 2.0, 0.5, 1.5)):
        vol, I = sphere_run(L); S = sum(l * l for l in L) + 4 * pi2
        print(f"sphere L = {L}: int Area(B) = {I:.6f} (predicted 2 pi^2 = {2 * pi2:.6f});  <Area(B)> = {I / vol:.6f} (predicted {4 * pi2 / S:.6f});  "
              f"<Area(B)> x <A*> = {I / vol * S / 4:.6f} (predicted pi^2)", flush=True)
