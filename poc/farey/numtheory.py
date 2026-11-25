"""The conic gap law on Diophantine Markoff-type equations, in exact integer arithmetic.

(A) Ghosh-Sarnak surfaces x^2 + y^2 + z^2 - xyz = k (k integer). The gap at a solution-tree node of value c is
    e^g = (c^2 - k)/(c^2 - 4)   (rational),
and the vector Hines identity becomes an infinite product of rationals over the integer orbit (cone e0, e1; root
values X, Y, W = XY - Z with Z the opposite value):
    prod_m ((c_m^2 - k)/(c_m^2 - 4))^{p_m} = lam(Y) sqrt(X^2 - 4) / (W - Y / lam(X)),   lam(t) = (t + sqrt(t^2 - 4))/2,
and the same with p <-> q, X <-> Y. For k > 4 there is no hyperbolic torus behind the equation (commutator trace
k - 2 > 2). Checked: gap law vs brute-force integer fans, positivity of the defects F(a) + F(b) - F(c), the product.
(B) Rosenberger equations a x^2 + b y^2 + c z^2 = d xyz: the rescaling T_i = d x_i sqrt(a_i)/sqrt(abc) maps them onto
the Markoff equation, so a node of variable i with value v has e^g = d^2 v^2 / (d^2 v^2 - 4 a_j a_k).
"""
import heapq, itertools
import mpmath as mp
mp.mp.dps = 80
F = lambda t: mp.acosh(mp.mpf(t) / 2)
lam = lambda t: (mp.mpf(t) + mp.sqrt(mp.mpf(t)**2 - 4)) / 2


def roots(k, lim=60):
    """One root (X, Y, Z) per k with 3 <= X <= Y, Z the smaller Vieta root, and the tree growing (W = XY - Z > Y)."""
    best = None
    for X in range(3, lim):
        for Y in range(X, lim):
            # Z^2 - XY Z + X^2 + Y^2 - k = 0
            D = (X * Y)**2 - 4 * (X * X + Y * Y - k)
            if D < 0: continue
            r = mp.isqrt(D) if hasattr(mp, "isqrt") else int(D**0.5)
            r = int(D**0.5)
            while r * r > D: r -= 1
            while (r + 1)**2 <= D: r += 1
            if r * r != D or (X * Y - r) % 2: continue
            Z = (X * Y - r) // 2; W = X * Y - Z
            if W > Y and (best is None or X + Y < best[0] + best[1]): best = (X, Y, Z)
    return best


def tree_check(k, X, Y, Z, n_cells=3000):
    tr = {(1, 0): X, (0, 1): Y, (1, -1): Z}; Sp = Sq = mp.mpf(0); negD = 0; worst = mp.mpf(0); n = 0
    h = [(-1.0, 0, (1, 0), (0, 1), (1, -1))]
    while h and n < n_cells:
        _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); c = tr[L] * tr[R] - tr[o]; tr[m] = c; n += 1   # exact ints
        g = mp.log(mp.mpf(c * c - k) / (c * c - 4)); Sp += m[0] * g; Sq += m[1] * g
        with mp.workdps(2 * len(str(c)) + 40):   # D ~ 1/c^2 relative to F ~ log c: precision must grow with the trace
            negD += F(tr[L]) + F(tr[R]) - F(c) <= 0
        if n <= 25:   # brute force: the bi-infinite integer fan around m through L (t_0 = L, t_-1 = R), 60 steps each way
            fwd = [tr[L], c * tr[L] - tr[R]]; bwd = [tr[L], tr[R]]
            for _ in range(60): fwd.append(c * fwd[-1] - fwd[-2]); bwd.append(c * bwd[-1] - bwd[-2])
            brute = mp.log(fwd[61]) + mp.log(bwd[61]) - 2 * 61 * mp.log(lam(c))
            worst = max(worst, abs(brute - g))
        for (a, b, oo) in ((L, m, R), (m, R, L)):
            heapq.heappush(h, (-float(mp.mpf(a[0] + a[1] + b[0] + b[1]) / (mp.mpf(tr[a]) * tr[b])**2), n, a, b, oo))
    W = X * Y - Z
    Pp = lam(Y) * mp.sqrt(X * X - 4) / (W - Y / lam(X)); Pq = lam(X) * mp.sqrt(Y * Y - 4) / (W - X / lam(Y))
    return n, negD, worst, mp.exp(Sp), Pp, mp.exp(Sq), Pq


if __name__ == "__main__":
    print("(A) x^2 + y^2 + z^2 - xyz = k, integer orbits")
    for k in (-20, -5, -1, 0, 1, 2, 3, 4, 5, 8, 13, 20, 52, 100):
        r = roots(k)
        if r is None: print(f"  k = {k}: no growing integer root with 3 <= X <= Y < 60"); continue
        X, Y, Z = r; n, negD, worst, eSp, Pp, eSq, Pq = tree_check(k, X, Y, Z)
        alg = mp.identify(Pp, ["sqrt(%d)" % (X * X - 4), "sqrt(%d)" % (Y * Y - 4)]) if True else ""
        print(f"  k = {k:>4}: root ({X}, {Y}; opposite {Z}), W = {X * Y - Z}; {n} nodes; non-positive defects {negD}; gap law vs integer fans {mp.nstr(worst, 3)}")
        print(f"          prod^p = {mp.nstr(eSp, 22)}  closed form {mp.nstr(Pp, 22)}  rel. diff {mp.nstr(abs(eSp / Pp - 1), 3)};  prod^q rel. diff {mp.nstr(abs(eSq / Pq - 1), 3)}")
    print("\n(B) Rosenberger equations a x^2 + b y^2 + c z^2 = d xyz (a <= b <= c <= 6, d <= 12, solutions < 30)")
    from fractions import Fraction as Fr
    tori = {}
    for (a, b, c, d) in itertools.product(range(1, 7), range(1, 7), range(1, 7), range(1, 13)):
        if not (a <= b <= c): continue
        sols = [(x, y, z) for x in range(1, 30) for y in range(1, 30) for z in range(1, 30) if a * x * x + b * y * y + c * z * z == d * x * y * z]
        if not sols: continue
        x, y, z = min(sols, key=sum)
        # reduce the torus to its minimal triple of squared traces T_i^2 = d^2 v_i^2 a_i/(abc) by descending Vieta moves
        T2 = [Fr(d * d * v * v * ai, a * b * c) for v, ai in zip((x, y, z), (a, b, c))]
        T = [mp.sqrt(mp.mpf(t.numerator) / t.denominator) for t in T2]
        while True:
            T.sort(); new = T[0] * T[1] - T[2]
            if new >= T[2] - mp.mpf(10)**-40: break
            T[2] = new
        key = tuple(mp.nstr(t * t, 12) for t in sorted(T)); tori.setdefault(key, []).append((a, b, c, d))
    for key, eqs in sorted(tori.items(), key=lambda kv: float(kv[0][0])):
        print(f"  minimal squared traces ({', '.join(key)}): {len(eqs)} equations, e.g. {eqs[:4]}")
    print("\n(B') raw-integer product identity: node of variable i (= parity class) with value v has e^g = d^2 v^2/(d^2 v^2 - 4 a_j a_k)")
    for (a, b, c, d), root in (((1, 1, 1, 3), (1, 1, 1)), ((1, 1, 2, 4), (1, 1, 1)), ((1, 2, 3, 6), (1, 1, 1)), ((1, 1, 5, 5), (1, 2, 1))):
        co = (a, b, c); var = {(1, 0): 0, (0, 1): 1, (1, 1): 2}
        x0, y0, z0 = root; kk = mp.mpf(d) / mp.sqrt(a * b * c); Tn = lambda i, v: kk * mp.sqrt(co[i]) * v
        val = {(1, 0): x0, (0, 1): y0}
        # opposite e0 - e1 (class (1,1), variable z): the smaller Vieta root of the z-equation
        zz = [z0, (d * x0 * y0) // c - z0]; val[(1, -1)] = min(zz); W0 = max(zz)
        if Tn(2, W0) < max(Tn(0, x0), Tn(1, y0)): print(f"  ({a},{b},{c},{d}): root not in the growing cone, skipped"); continue
        h = [(-1.0, 0, (1, 0), (0, 1), (1, -1))]; Sp = mp.mpf(0); n = 0
        cls = lambda v: var[(v[0] % 2, v[1] % 2)]
        while h and n < 3000:
            _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); i = cls(m); j, k2 = cls(L), cls(R)
            assert d * val[L] * val[R] % co[i] == 0
            v = d * val[L] * val[R] // co[i] - val[o]; val[m] = v; n += 1
            Sp += m[0] * mp.log(mp.mpf(d * d * v * v) / (d * d * v * v - 4 * co[j] * co[k2]))
            for (aa, bb, oo) in ((L, m, R), (m, R, L)):
                heapq.heappush(h, (-float(mp.mpf(aa[0] + aa[1] + bb[0] + bb[1]) / (Tn(cls(aa), val[aa]) * Tn(cls(bb), val[bb]))**2), n, aa, bb, oo))
        X, Y, W = Tn(0, x0), Tn(1, y0), Tn(2, W0)
        P = lam(Y) * mp.sqrt(X * X - 4) / (W - Y / lam(X))
        print(f"  ({a},{b},{c},{d}) root {root}: prod over 3000 integer nodes = {mp.nstr(mp.exp(Sp), 20)}; closed form {mp.nstr(P, 20)} = {mp.identify(P, ['sqrt(2)', 'sqrt(3)', 'sqrt(5)', 'sqrt(6)'])}; rel. diff {mp.nstr(abs(mp.exp(Sp) / P - 1), 3)}")
