"""Remainder bound for the sphere (forced fans), completing the proof of the vector Hines identity there.

Fan around L through R: t_j = K lam^j + K' lam^-j + u_j, u the period-2 particular solution (u_0 = u_e at the R slot):
    u_e = (a kappa(L+R) + 2 kappa(R)) / (a^2 - 4),   a = tr L.
Energy: K K' = G = e^{g_L}; K + K' = b - u_e (b = tr R), K the larger root (c_m > tr(R - L)). Hence, exactly,
    beta(L, R) = N(R) - log K = log[ (b + sqrt(b^2 - 4)) / (bt + sqrt(bt^2 - 4G)) ],   bt = b - u_e,
and |beta| <= C/(a b) (u_e = O(1/a), G - 1 = O(1/a)); the depth-n remainder is <= C' sum_{m at depth n+1} |m|/c_m, a
tail of a convergent series. Checked: the closed form, sup |beta| a b over all intervals to depth 12, and its limit
kappa(L+R) (leading term beta ~ u_e / b ~ kappa(L+R)/(a b)).
"""
import sys
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from general import kap, fan_K, sphere_C
mp.mp.dps = 1300   # beta ~ 1/(ab) reaches 1e-1000 at depth 12: traces must be resolved to that absolute precision
F = lambda t: mp.acosh(t / 2)


def run(name, bnd, X, Y, depth=12):
    C, s = sphere_C(*map(mp.mpf, bnd)); X, Y = mp.mpf(X), mp.mpf(Y)
    B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; tr = {(1, 0): X, (0, 1): Y, (1, -1): (-B - mp.sqrt(B * B - 4 * c0)) / 2}
    add = lambda u, v: (u[0] + v[0], u[1] + v[1])
    tr[(1, 1)] = X * Y - kap((1, 1), C) - tr[(1, -1)]
    def gapL(L, R):   # gap at L: its two Farey-neighbour classes are those of R and L + R
        a = tr[L]; km, kx, ky = kap(L, C), kap(R, C), kap(add(L, R), C)
        return (a * a + km * a + s) / (a * a - 4) + (kx * kx + ky * ky + kx * ky * a) / (a * a - 4)**2
    level = [((1, 0), (0, 1), (1, -1))]; worst_cf = mp.mpf(0); rows = []; series = mp.mpf(0)
    for n in range(1, depth + 1):
        nxt = []
        for (L, R, o) in level:
            m = add(L, R); nxt += [(L, m, R), (m, R, L)]
        level = nxt; supb = mp.mpf(0); rem = mp.mpf(0); tail = mp.mpf(0); lim = []
        for (L, R, o) in level:
            m = add(L, R); tr[m] = tr[L] * tr[R] - kap(m, C) - tr[o]
        for (L, R, o) in level:
            m = add(L, R)
            for (P, Q) in ((L, R), (R, L)):
                a, b = tr[P], tr[Q]; G = gapL(P, Q); ue = (a * kap(add(P, Q), C) + 2 * kap(Q, C)) / (a * a - 4); bt = b - ue
                beta = F(b) - mp.log(fan_K(b, tr[m], a, kap(Q, C), kap(m, C)))
                cf = mp.log((b + mp.sqrt(b * b - 4)) / (bt + mp.sqrt(bt * bt - 4 * G)))
                worst_cf = max(worst_cf, abs(beta - cf)); supb = max(supb, abs(beta) * a * b); lim.append(beta * a * b / kap(m, C))
                rem += (P[0] + P[1]) * abs(beta)
            tail += (m[0] + m[1]) / tr[m]
        if n in (2, 4, 6, 8, 10, 12):
            rows.append((n, supb, rem, tail, min(lim), max(lim)))
    print(f"{name}: closed form of beta with forcing, worst error {mp.nstr(worst_cf, 3)}")
    for n, supb, rem, tail, lo, hi in rows:
        print(f"   depth {n:>2}: sup |beta| a b = {mp.nstr(supb, 5)};  sum |w| |beta| = {mp.nstr(rem, 4)} <= {mp.nstr(rem / tail, 3)} x sum_(m at depth n+1) |m|/c_m = {mp.nstr(tail, 4)};  beta a b / kappa(L+R) in [{mp.nstr(lo, 6)}, {mp.nstr(hi, 6)}]")


if __name__ == "__main__":
    run("four-holed sphere (2.5, 2.2, 3.0, 2.1), (9, 11)", ("2.5", "2.2", "3.0", "2.1"), 9, 11)
    run("four-punctured sphere (2, 2, 2, 2), (7, 7)", ("2", "2", "2", "2"), 7, 7)
    run("sphere with large boundaries (3, 5, 4, 6), (40, 50)", ("3", "5", "4", "6"), 40, 50)
