"""Numerical check of the proof of the vector Hines identity (docs/farey-markoff-checks.md, 'A proof').

For a Farey interval (L, R): D_L^R = log K(L; R), the log leading coefficient of the fan k L + R; N(v) = F(tr v);
beta(L, R) = N(R) - D_L^R. Finite identity, exact at every depth n (by induction, from two exact fan facts):
    sum_{m, depth < n} p_m g_m + sum_{(L, R) at depth n} [L_p beta(L, R) + R_p beta(R, L)] = N(e1) - D_{e0}^{e1},
and the same for q with N(e0) - D_{e1}^{e0}. Torus (no linear terms): beta = log[(b + sqrt(b^2 - 4)) / (b + sqrt(b^2 - 4G))],
b = tr R, G = e^{g_L} = (a^2 - k)/(a^2 - 4), a = tr L; so |beta| = O(1/(a b)^2) and the remainder is a tail of sum |m|/c_m^2.
Checked: (1) the two fan facts, (2) the finite identity at depths 1..12, (3) the closed form of beta, (4) the remainder decay.
"""
import sys
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from general import kap, fan_K, sphere_C
mp.mp.dps = 220
F = lambda t: mp.acosh(t / 2)


def check(name, C, s, X, Y, depth=12):
    X, Y = mp.mpf(X), mp.mpf(Y); Bq = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(Bq * Bq - 4 * c0)
    tr = {(1, 0): X, (0, 1): Y, (1, -1): (-Bq - d) / 2}
    add = lambda u, v: (u[0] + v[0], u[1] + v[1])
    Dfan = lambda L, R: mp.log(fan_K(tr[R], tr[add(L, R)], tr[L], kap(R, C), kap(add(L, R), C)))   # fan k L + R
    beta = lambda L, R: F(tr[R]) - Dfan(L, R)
    tr[(1, 1)] = X * Y - kap((1, 1), C) - tr[(1, -1)]
    rhs = (F(Y) - Dfan((1, 0), (0, 1)), F(X) - Dfan((0, 1), (1, 0)))
    level = [((1, 0), (0, 1), (1, -1))]; S = [mp.mpf(0), mp.mpf(0)]; worst_fact = mp.mpf(0); worst_beta = mp.mpf(0); torus = C == (0, 0, 0)
    print(f"{name}")
    for n in range(1, depth + 1):
        nxt = []
        for (L, R, o) in level:
            m = add(L, R); c = tr[m]
            g = mp.log((c * c + kap(m, C) * c + s) / (c * c - 4) + (kap(L, C)**2 + kap(R, C)**2 + kap(L, C) * kap(R, C) * c) / (c * c - 4)**2)
            S[0] += m[0] * g; S[1] += m[1] * g
            nxt += [(L, m, R), (m, R, L)]
        level = nxt
        for (L, R, o) in level:   # fans need the trace of L + R
            m = add(L, R); tr[m] = tr[L] * tr[R] - kap(m, C) - tr[o]
        rem = [sum(L[i] * beta(L, R) + R[i] * beta(R, L) for (L, R, o) in level) for i in (0, 1)]
        if n <= 4:   # fact 1: D_L^{L+R} = D_L^R + N(L); fact 2: g_m = D_m^L + D_m^R - N(m)  (m = L + R, fans around m)
            for (L, R, o) in level[:8]:
                m = add(L, R)
                if add(L, m) not in tr: tr[add(L, m)] = tr[L] * tr[m] - kap(add(L, m), C) - tr[R]
                if add(m, R) not in tr: tr[add(m, R)] = tr[m] * tr[R] - kap(add(m, R), C) - tr[L]
                if add(add(L, m), L) not in tr: tr[add(add(L, m), L)] = tr[L] * tr[add(L, m)] - kap(add(add(L, m), L), C) - tr[m]
                f1 = Dfan(L, m) - Dfan(L, R) - F(tr[L])
                c = tr[m]; g = mp.log((c * c + kap(m, C) * c + s) / (c * c - 4) + (kap(L, C)**2 + kap(R, C)**2 + kap(L, C) * kap(R, C) * c) / (c * c - 4)**2)
                f2 = g - (Dfan(m, L) + Dfan(m, R) - F(c))
                worst_fact = max(worst_fact, abs(f1), abs(f2))
        if torus:
            for (L, R, o) in level[:64]:
                a, b = tr[L], tr[R]; G = (a * a + s) / (a * a - 4)
                worst_beta = max(worst_beta, abs(beta(L, R) - mp.log((b + mp.sqrt(b * b - 4)) / (b + mp.sqrt(b * b - 4 * G)))))
        e = [S[i] + rem[i] - rhs[i] for i in (0, 1)]
        if n in (1, 2, 3, 4, 6, 8, 10, 12):
            print(f"   depth {n:>2}: finite identity error (p, q) = ({mp.nstr(e[0], 2)}, {mp.nstr(e[1], 2)}); remainder (p, q) = ({mp.nstr(rem[0], 3)}, {mp.nstr(rem[1], 3)})")
    print(f"   fan facts 1 and 2, worst error {mp.nstr(worst_fact, 3)}" + (f"; closed form of beta, worst error {mp.nstr(worst_beta, 3)}" if torus else ""))


if __name__ == "__main__":
    z = (0, 0, 0)
    check("punctured torus (2.6, 4.1), k = 0", z, 0, mp.mpf("2.6"), mp.mpf("4.1"))
    check("one-holed torus k = -20, (3, 5)", z, 20, 3, 5)
    check("Ghosh-Sarnak k = 5, root (3, 4)", z, -5, 3, 4)
    check("pair of pants: boundary traces (-3, -3, -3) -> (3, 3, -3), k = 54 (Goldman t = 52 > 18)", z, -54, 3, 3)
    C, s = sphere_C(*map(mp.mpf, ("2.5", "2.2", "3.0", "2.1"))); check("four-holed sphere (2.5, 2.2, 3.0, 2.1), (9, 11)", C, s, 9, 11)
