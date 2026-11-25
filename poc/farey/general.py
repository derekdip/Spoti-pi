"""Generalising the gap law and the Hines identity to any Vieta tree X^2+Y^2+Z^2-XYZ+pX+qY+rZ+s = 0
(one-holed torus: p = q = r = 0, s = -mu; four-holed sphere: Fricke coefficients), real or complex.

(1) Energy principle. Along a fan t_k (curves L + k m, k in Z) the trace of m is fixed, so t_{k+1} + t_{k-1} = c t_k - kappa_k
is linear; after removing its period-2 particular solution u_k, I = w_k^2 + w_{k+1}^2 - c w_k w_{k+1} (w = t - u) is
conserved and equals -(c^2 - 4) K K' for w_k = K lam^k + K' lam^-k. The gap is g = log K + log K' = log(-I/(c^2 - 4)).
(2) Vector Hines. N(x, y) the stable norm on the cone (e0, e1); its gradient jumps by g_m (-q, p) at each rational m = (p, q).
Summing: sum p g = F(e1) - log K0, sum q g = F(e0) - log K1 (their sum is the Hines-type identity).
"""
import heapq
import mpmath as mp
mp.mp.dps = 80
F = lambda t: mp.acosh(t / 2)


def kap(v, C):
    return {(1, 0): C[0], (0, 1): C[1], (1, 1): C[2]}[(v[0] % 2, v[1] % 2)]


def fan_K(t0, t1, c, ke, ko):
    lam = c / 2 + mp.sqrt(c * c / 4 - 1)
    u, v = mp.lu_solve(mp.matrix([[2, -c], [-c, 2]]), mp.matrix([-ke, -ko]))
    return ((t1 - v) - (t0 - u) / lam) / (lam - 1 / lam)


def gap_energy(tl, tr_, c, kl, km, kr):
    """g from the conserved energy of the bi-infinite fan through (L = t_0, R = t_{-1}) around m (trace c)."""
    # fan t_k = trace of L + k m; t_{-1} = trace of L - m = R side (R = m - L up to sign); kappa_k alternates kr (k odd) / kl (k even)
    u = mp.lu_solve(mp.matrix([[2, -c], [-c, 2]]), mp.matrix([-kl, -kr]))   # particular solution: u_even (class of L), u_odd (class of R)
    ue, uo = u[0], u[1]
    w0, w1 = tl - ue, (c * tl - kr - tr_) - uo   # t_1 = trace of L + m (class of L + m = class of R)
    # note: kappa of L+m equals kappa of R (same parity), and recurrence t_{k+1} = c t_k - kappa_{k+1} - t_{k-1}
    I = w0 * w0 + w1 * w1 - c * w0 * w1
    return mp.log(-I / (c * c - 4))


def run(name, C, s, X, Y, n_cells=3000):
    X, Y = mp.mpmathify(X), mp.mpmathify(Y)
    B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(B * B - 4 * c0)
    Zs = min([(-B - d) / 2, (-B + d) / 2], key=lambda z: mp.re(z))
    e0, e1 = (1, 0), (0, 1); tr = {e0: X, e1: Y, (1, -1): Zs}
    Sp = Sq = mp.mpf(0); worst = 0; h = [(-1.0, 0, e0, e1, (1, -1))]; n = 0
    while h and n < n_cells:
        _, _, L, R, opp = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); c = tr[L] * tr[R] - kap(m, C) - tr[opp]; tr[m] = c; n += 1
        km, kl, kr = kap(m, C), kap(L, C), kap(R, C)
        g = mp.log((c * c + km * c + s) / (c * c - 4) + (kl**2 + kr**2 + kl * kr * c) / (c * c - 4)**2)
        if n <= 40: worst = max(worst, abs(g - gap_energy(tr[L], tr[R], c, kl, km, kr)))
        Sp += m[0] * g; Sq += m[1] * g
        for (a, b, o) in ((L, m, R), (m, R, L)):
            heapq.heappush(h, (-float(abs((a[0] + a[1] + b[0] + b[1]) / (tr[a] * tr[b])**2)), n, a, b, o))
    XY = X * Y - kap((1, 1), C) - Zs
    K0 = fan_K(Y, XY, X, kap((0, 1), C), kap((1, 1), C)); K1 = fan_K(X, XY, Y, kap((1, 0), C), kap((1, 1), C))
    print(f"{name}: gap law vs energy principle, worst {mp.nstr(worst, 3)}")
    dp, dq = Sp - F(Y) + mp.log(K0), Sq - F(X) + mp.log(K1)
    print(f"   sum p g = {mp.nstr(Sp, 18)}   F(e1) - log K0 = {mp.nstr(F(Y) - mp.log(K0), 18)}   signed diff {mp.nstr(dp, 3)}")
    print(f"   sum q g = {mp.nstr(Sq, 18)}   F(e0) - log K1 = {mp.nstr(F(X) - mp.log(K1), 18)}   signed diff {mp.nstr(dq, 3)}")


def sphere_C(al, be, ga, de):
    return (al * be + ga * de, be * ga + al * de, al * ga + be * de), al**2 + be**2 + ga**2 + de**2 + al * be * ga * de - 4


if __name__ == "__main__":
    z = (0, 0, 0)
    run("modular torus (3, 3)", z, 0, 3, 3)
    run("asymmetric punctured torus (2.6, 4.1)", z, 0, 2.6, 4.1)
    run("one-holed torus mu = -7, (3.4, 5.2)", z, 7, 3.4, 5.2)
    run("torus with cone point mu = 1.5, (2.9, 3.6)", z, -1.5, 2.9, 3.6)
    C, s = sphere_C(*map(mp.mpf, ("2.5", "2.2", "3.0", "2.1"))); run("four-holed sphere (2.5, 2.2, 3.0, 2.1), (9, 11)", C, s, 9, 11)
    run("quasi-Fuchsian punctured torus (3 + 0.4i, 3.2 - 0.3i)", z, 0, mp.mpc(3, 0.4), mp.mpc(3.2, -0.3))
    run("arbitrary real cubic (p, q, r, s) = (1.3, -0.7, 2.9, 5.1), (8, 10)", tuple(map(mp.mpf, ("1.3", "-0.7", "2.9"))), mp.mpf("5.1"), 8, 10)
    run("arbitrary complex cubic, (8 + 0.6i, 9 - 0.4i)", (mp.mpc(1, .5), mp.mpc(-2, .3), mp.mpf(4)), mp.mpc(-3, 1), mp.mpc(8, .6), mp.mpc(9, -.4))
    C, s = sphere_C(*map(mp.mpf, ("2.5", "2.2", "3.0", "2.1"))); run("complex four-holed sphere (9 + i, 11 - 0.5i)", C, s, mp.mpc(9, 1), mp.mpc(11, -0.5))
