"""Gap law and a Hines-type identity for the four-holed sphere (Fricke relation with linear terms).

Traces of simple closed curves (made positive), X^2 + Y^2 + Z^2 - XYZ + p X + q Y + r Z + s = 0, where for boundary
traces (al, be, ga, de): p = al be + ga de, q = be ga + al de, r = al ga + be de, s = al^2 + be^2 + ga^2 + de^2 + al be ga de - 4
(cusps: p = q = r = 8, s = 28). A curve of slope (P, Q) carries the coefficient of its parity class:
(1, 0) -> p, (0, 1) -> q, (1, 1) -> r. Vieta: the mediant of a cell is c = a b - kappa(class of c) - (opposite vertex).

Derived symbolically before this check (fan recurrence t_{k+1} + t_{k-1} = c t_k - kappa, with its period-2 particular
solution, and the Fricke relation): the slope gap at a curve m of trace c and coefficient k_m, the other two classes
k_x, k_y,
    g_m = log[ (c^2 + k_m c + s)/(c^2 - 4) + (k_x^2 + k_y^2 + k_x k_y c)/(c^2 - 4)^2 ],
and, from the end fans, the Hines-type identity sum_w M_w g_w = F(e0) + F(e1) - log K0 - log K1 over the rationals of
(0, 1), M_w the height p + q on the slice, F = arccosh(t/2), K0 and K1 the leading coefficients of the end fans.
"""
import heapq
import mpmath as mp
mp.mp.dps = 120
F = lambda t: mp.acosh(t / 2)


def setup(al, be, ga, de):
    p, q, r = al * be + ga * de, be * ga + al * de, al * ga + be * de; s = al**2 + be**2 + ga**2 + de**2 + al * be * ga * de - 4
    return dict(p=p, q=q, r=r, s=s)


def kappa(v, C):
    cls = (v[0] % 2, v[1] % 2)
    return {(1, 0): C["p"], (0, 1): C["q"], (1, 1): C["r"]}[cls]


def base(C, X, Y):
    """Z with X^2+Y^2+Z^2-XYZ+pX+qY+rZ+s = 0, the smaller root (so that (X, Y, Z) is the triple of e0, e1, e0 - e1)."""
    B = -(X * Y) + C["r"]; c0 = X * X + Y * Y + C["p"] * X + C["q"] * Y + C["s"]; d = B * B - 4 * c0
    return (-B - mp.sqrt(d)) / 2, (-B + mp.sqrt(d)) / 2


def fan_K(t0, t1, c, k_even, k_odd):
    """Leading coefficient K of a fan t_k = K lam^k + ... with t_{k+1} + t_{k-1} = c t_k - kappa_{k+1}, kappa alternating."""
    lam = c / 2 + mp.sqrt(c * c / 4 - 1)
    u, v = mp.matrix([[2, -c], [-c, 2]]) ** -1 * mp.matrix([-k_even, -k_odd])   # 2u - c v = -k_even (k odd), 2v - c u = -k_odd (k even)
    return ((t1 - v) - (t0 - u) / lam) / (lam - 1 / lam)


def gap_formula(c, km, kx, ky, s):
    return mp.log((c * c + km * c + s) / (c * c - 4) + (kx * kx + ky * ky + kx * ky * c) / (c * c - 4)**2)


def check(al, be, ga, de, X, Y):
    C = setup(*map(mp.mpf, (al, be, ga, de))); X, Y = mp.mpf(X), mp.mpf(Y); Zs, Zl = base(C, X, Y)
    e0, e1 = (1, 0), (0, 1); tr = {e0: X, e1: Y, (1, -1): Zs}
    print(f"boundary traces ({al}, {be}, {ga}, {de}): p, q, r = {mp.nstr(C['p'], 6)}, {mp.nstr(C['q'], 6)}, {mp.nstr(C['r'], 6)}, s = {mp.nstr(C['s'], 6)}; base triple X = {X}, Y = {Y}, Z(e0 - e1) = {mp.nstr(Zs, 8)}, Z(e0 + e1) = {mp.nstr(Zl, 8)}")
    # tree on the cone (e0, e1), best first by 1/(ab)^2 * M until terms are tiny; record traces and defects
    def child(L, R, opp):
        m = (L[0] + R[0], L[1] + R[1]); return m, tr[L] * tr[R] - kappa(m, C) - tr[opp]
    h = [(-1.0, e0, e1, (1, -1))]; S_Mg = mp.mpf(0); nonconvex = 0; worst_gap = mp.mpf(0); n = 0
    while h and n < 4000:
        _, L, R, opp = heapq.heappop(h); m, cm = child(L, R, opp); tr[m] = cm; n += 1
        D = F(tr[L]) + F(tr[R]) - F(cm); nonconvex += D <= 0
        km = kappa(m, C); others = [C[k] for k in ("p", "q", "r") if C[k] != km] if len({C['p'], C['q'], C['r']}) == 3 else None
        # the other two classes: those of L and R (classes of a Farey triangle are all different)
        kx, ky = kappa(L, C), kappa(R, C)
        g = gap_formula(cm, km, kx, ky, C["s"]); S_Mg += (sum(m)) * g
        if n <= 30:   # gap by brute force along the fans k m + L and k m - L
            t = [tr[L], cm * tr[L] - kappa((L[0] + m[0], L[1] + m[1]), C) - tr[R]]; sgn = [tr[L], tr[R]]
            for k in range(1, 70):
                nxt_v = (L[0] + (k + 1) * m[0], L[1] + (k + 1) * m[1]); t.append(cm * t[-1] - kappa(nxt_v, C) - t[-2])
                nxt_w = (-L[0] + (k + 1) * m[0], -L[1] + (k + 1) * m[1]); sgn.append(cm * sgn[-1] - kappa(nxt_w, C) - sgn[-2])
            brute = F(t[69]) + F(sgn[69]) - 2 * 69 * F(cm); worst_gap = max(worst_gap, abs(brute - g))
        for (a, b, o) in ((L, m, R), (m, R, L)):
            heapq.heappush(h, (-float((a[0] + a[1] + b[0] + b[1]) / (tr[a] * tr[b])**2), a, b, o))
    print(f"   cells {n}; non-positive defects {nonconvex}; gap law vs brute-force fans, worst error {mp.nstr(worst_gap, 3)}")
    # Hines-type: sum M g = F(e0) + F(e1) - log K0 - log K1; K0: fan k e0 + e1 (classes alternate (0,1), (1,1)); K1: fan e0 + k e1
    K0 = fan_K(Y, X * Y - kappa((1, 1), C) - Zs, X, kappa((0, 1), C) if True else 0, kappa((1, 1), C))
    K1 = fan_K(X, X * Y - kappa((1, 1), C) - Zs, Y, kappa((1, 0), C), kappa((1, 1), C))
    rhs = F(X) + F(Y) - mp.log(K0) - mp.log(K1)
    print(f"   Hines-type: sum M g = {mp.nstr(S_Mg, 25)}; F(e0) + F(e1) - log K0 - log K1 = {mp.nstr(rhs, 25)}; difference {mp.nstr(S_Mg - rhs, 3)}")


if __name__ == "__main__":
    check(2, 2, 2, 2, 7, 7)                 # cusped, symmetric
    check(2.5, 2.2, 3.0, 2.1, 9, 11)        # four different boundary lengths
    check(3.0, 2.0, 2.0, 4.0, 12, 10)       # two cusps and two boundaries
