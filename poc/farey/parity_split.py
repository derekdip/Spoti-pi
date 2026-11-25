"""(i) The gap law as a conic invariant: fixing the trace c of m, the cubic is the conic
Y^2 + Z^2 - c YZ + kx Y + ky Z + (c^2 + km c + s) = 0, and e^g = -4 det M3 / (c^2 - 4)^2 (M3 its 3x3 matrix).
(ii) Does the Hines-type sum split by Z/2-homology class, as Hu-Tan-Zhang's McShane identity does (1402.3904 Thm 1.3)?
Six sums S[class][p or q] = sum over m in the class of p g or q g; PSLQ against natural constants of the root cell.
"""
import heapq, sys
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from general import kap, fan_K, F, sphere_C
mp.mp.dps = 90


def run(name, C, s, X, Y, n_cells=4000):
    X, Y = mp.mpf(X), mp.mpf(Y)
    B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(B * B - 4 * c0)
    Zs, W = (-B - d) / 2, (-B + d) / 2                    # traces of e0 - e1 and e0 + e1
    e0, e1 = (1, 0), (0, 1); tr = {e0: X, e1: Y, (1, -1): Zs}
    S = {cl: [mp.mpf(0), mp.mpf(0)] for cl in ((1, 0), (0, 1), (1, 1))}; worst = 0
    h = [(-1.0, 0, e0, e1, (1, -1))]; n = 0
    while h and n < n_cells:
        _, _, L, R, opp = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); c = tr[L] * tr[R] - kap(m, C) - tr[opp]; tr[m] = c; n += 1
        km, kx, ky = kap(m, C), kap(L, C), kap(R, C)
        g = mp.log((c * c + km * c + s) / (c * c - 4) + (kx**2 + ky**2 + kx * ky * c) / (c * c - 4)**2)
        if n <= 200:
          M3 = mp.matrix([[1, -c / 2, kx / 2], [-c / 2, 1, ky / 2], [kx / 2, ky / 2, c * c + km * c + s]])
          worst = max(worst, abs(g - mp.log(-4 * mp.det(M3) / (c * c - 4)**2)))
        cl = (m[0] % 2, m[1] % 2); S[cl][0] += m[0] * g; S[cl][1] += m[1] * g
        for (a, b, o) in ((L, m, R), (m, R, L)):
            heapq.heappush(h, (-float((a[0] + a[1] + b[0] + b[1]) / (tr[a] * tr[b])**2), n, a, b, o))
    K0 = fan_K(Y, W, X, kap((0, 1), C), kap((1, 1), C)); K1 = fan_K(X, W, Y, kap((1, 0), C), kap((1, 1), C))
    # fans around e0 + e1 toward e0 and toward e1 (both ends of the bi-infinite fan through e0 and e1)
    KW0 = fan_K(X, W * X - kap((2, 1), C) - Y, W, kap((1, 0), C), kap((0, 1), C))
    KW1 = fan_K(Y, W * Y - kap((1, 2), C) - X, W, kap((0, 1), C), kap((1, 0), C))
    names = ["1", "F(e0)", "F(e1)", "F(e0+e1)", "F(e0-e1)", "log K0", "log K1", "log KW0", "log KW1", "log(X^2-4)", "log(Y^2-4)", "log(W^2-4)", "log 2"]
    basis = [mp.mpf(1), F(X), F(Y), F(W), F(Zs), mp.log(K0), mp.log(K1), mp.log(KW0), mp.log(KW1), mp.log(X * X - 4), mp.log(Y * Y - 4), mp.log(W * W - 4), mp.log(2)]
    print(f"{name}: conic-invariant form vs gap law, worst {mp.nstr(worst, 3)}; vector Hines check: "
          f"{mp.nstr(sum(v[0] for v in S.values()) - F(Y) + mp.log(K0), 3)}, {mp.nstr(sum(v[1] for v in S.values()) - F(X) + mp.log(K1), 3)}")
    mp.mp.dps = 60
    for cl, (sp, sq) in S.items():
        for lab, v in (("p g", sp), ("q g", sq)):
            rel = mp.pslq([v] + basis, maxcoeff=200, maxsteps=400000)
            txt = "no relation (coefficients <= 200)" if not rel or rel[0] == 0 else " ".join(f"{-r:+d}/{rel[0]} {nm}" for r, nm in zip(rel[1:], names) if r)
            print(f"   class {cl}, sum {lab} = {mp.nstr(v, 20)}: {txt}")
    # any linear relation among the six class sums and the basis together?
    vec = [v for cl in S for v in S[cl]]
    rel = mp.pslq(vec + basis, maxcoeff=100, maxsteps=1000000)
    labs = [f"S{cl}{w}" for cl in S for w in ("p", "q")] + names
    print("   joint relation:", "none (coefficients <= 100)" if not rel else " ".join(f"{r:+d} {nm}" for r, nm in zip(rel, labs) if r))
    mp.mp.dps = 90


if __name__ == "__main__":
    z = (0, 0, 0)
    run("modular torus (3, 3)", z, 0, 3, 3)
    run("punctured torus (2.6, 4.1)", z, 0, mp.mpf("2.6"), mp.mpf("4.1"))
    C, s = sphere_C(*map(mp.mpf, ("2.5", "2.2", "3.0", "2.1"))); run("four-holed sphere (2.5, 2.2, 3.0, 2.1), (9, 11)", C, s, 9, 11)


def residual_search():
    """With the vector Hines relations removed (drop class (1,1) sums and log K0, log K1), is there any other relation
    among the class sums and the root-cell constants?"""
    import general
    for name, C, s, X, Y in (("punctured torus (2.6, 4.1)", (0, 0, 0), 0, mp.mpf("2.6"), mp.mpf("4.1")),
                             ("four-holed sphere", *sphere_C(*map(mp.mpf, ("2.5", "2.2", "3.0", "2.1"))), mp.mpf(9), mp.mpf(11))):
        mp.mp.dps = 90
        B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(B * B - 4 * c0); Zs, W = (-B - d) / 2, (-B + d) / 2
        e0, e1 = (1, 0), (0, 1); tr = {e0: X, e1: Y, (1, -1): Zs}; S = {(1, 0): [0, 0], (0, 1): [0, 0]}
        h = [(-1.0, 0, e0, e1, (1, -1))]; n = 0
        while h and n < 4000:
            _, _, L, R, opp = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); c = tr[L] * tr[R] - kap(m, C) - tr[opp]; tr[m] = c; n += 1
            km, kx, ky = kap(m, C), kap(L, C), kap(R, C)
            g = mp.log((c * c + km * c + s) / (c * c - 4) + (kx**2 + ky**2 + kx * ky * c) / (c * c - 4)**2)
            cl = (m[0] % 2, m[1] % 2)
            if cl in S: S[cl][0] += m[0] * g; S[cl][1] += m[1] * g
            for (a, b, o) in ((L, m, R), (m, R, L)):
                heapq.heappush(h, (-float((a[0] + a[1] + b[0] + b[1]) / (tr[a] * tr[b])**2), n, a, b, o))
        KW0 = fan_K(X, W * X - kap((2, 1), C) - Y, W, kap((1, 0), C), kap((0, 1), C)); KW1 = fan_K(Y, W * Y - kap((1, 2), C) - X, W, kap((0, 1), C), kap((1, 0), C))
        names = ["S(1,0)p", "S(1,0)q", "S(0,1)p", "S(0,1)q", "1", "F(e0)", "F(e1)", "F(e0+e1)", "F(e0-e1)", "log KW0", "log KW1", "log(X^2-4)", "log(Y^2-4)", "log(W^2-4)", "log 2"]
        vals = S[(1, 0)] + S[(0, 1)] + [mp.mpf(1), F(X), F(Y), F(W), F(Zs), mp.log(KW0), mp.log(KW1), mp.log(X * X - 4), mp.log(Y * Y - 4), mp.log(W * W - 4), mp.log(2)]
        mp.mp.dps = 60
        rel = mp.pslq(vals, maxcoeff=100, maxsteps=2000000)
        print(f"residual search, {name}:", "no relation (coefficients <= 100)" if not rel else " ".join(f"{r:+d} {nm}" for r, nm in zip(rel, names) if r))


if __name__ == "__main__":
    residual_search()
