"""Closed-form search for the dual-area constant of the modular torus,
    A* = Area(B*) = sum over simple closed geodesics gamma of g_gamma N_gamma,
    g = log(t^2/(t^2 - 4)) = 2 log coth(l/2),  N = arccosh(t/2) = l/2,  t = 3 x Markov number,
(Doan-Li-Nguyen Thm 1.3 in the norm l/2), and of companion sums, by PSLQ. Also the four-punctured sphere at (7, 7, 7).
Sums over all curves mod sign: e0, e1, and the interiors of the cones (e0, e1) and (e0, -e1), best first until terms < 1e-125.
"""
import heapq, sys
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from general import kap, sphere_C
mp.mp.dps = 140
F = lambda t: mp.acosh(t / 2)


def all_curves(C, s, X, Y, tol=mp.mpf(10)**-125):
    X, Y = mp.mpf(X), mp.mpf(Y); B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(max(B * B - 4 * c0, 0))   # clamp: a double root (e.g. the square torus) can round slightly negative
    Zs = (-B - d) / 2; W = X * Y - kap((1, 1), C) - Zs
    tr = {(1, 0): X, (0, 1): Y, (0, -1): Y, (1, -1): Zs, (1, 1): W}; out = {(1, 0): X, (0, 1): Y}
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        h = [(-1.0, 0, e0, e1, opp)]; n = 0
        while h:
            _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); tr[m] = tr[L] * tr[R] - kap(m, C) - tr[o]; out[m] = tr[m]; n += 1
            if mp.log(tr[m]) / tr[m]**2 > tol:
                for (a, b, oo) in ((L, m, R), (m, R, L)):
                    heapq.heappush(h, (-float(1 / (tr[a] * tr[b])**2), n, a, b, oo))
    return out


def gap(v, c, C, s):
    cls = {(1, 0): C[0], (0, 1): C[1], (1, 1): C[2]}; own = (v[0] % 2, v[1] % 2); km = cls[own]; kx, ky = [cls[k] for k in cls if k != own]
    return mp.log((c * c + km * c + s) / (c * c - 4) + (kx * kx + ky * ky + kx * ky * c) / (c * c - 4)**2)


if __name__ == "__main__":
    z = (0, 0, 0); cv = all_curves(z, 0, 3, 3)
    A = sum(gap(v, c, z, 0) * F(c) for v, c in cv.items())
    sums = {"A* = sum g N": A,
            "sum g": sum(gap(v, c, z, 0) for v, c in cv.items()),
            "sum g N^2": sum(gap(v, c, z, 0) * F(c)**2 for v, c in cv.items()),
            "sum N h (h McShane atom)": sum(F(c) * (1 - mp.sqrt(1 - 4 / c**2)) / 2 for v, c in cv.items()),
            "sum N / c^2": sum(F(c) / c**2 for v, c in cv.items()),
            "sum Li2(4/c^2)": sum(mp.polylog(2, 4 / c**2) for v, c in cv.items())}
    print(f"modular torus: {len(cv)} curves summed (terms down to 1e-125)")
    Cs, ss = sphere_C(2, 2, 2, 2); cs = all_curves(tuple(map(mp.mpf, Cs)), mp.mpf(ss), 7, 7)
    As = sum(gap(v, c, tuple(map(mp.mpf, Cs)), mp.mpf(ss)) * F(c) for v, c in cs.items())
    print(f"four-punctured sphere: A* = {mp.nstr(As, 40)};  A*/A*(torus) = {mp.nstr(As / A, 40)}")
    lam = (3 + mp.sqrt(5)) / 2; L = mp.log(lam); s5 = mp.sqrt(5)
    names = ["1", "pi^2", "zeta3", "logl", "logl^2", "logl^3", "s5", "s5 logl", "s5 logl^2", "pi^2 logl", "log2", "log3", "log5",
             "Li2(1/l^2)", "Li3(1/l^2)", "Li2(1/l)", "Catalan", "pi", "pi^2 s5"]
    basis = [mp.mpf(1), mp.pi**2, mp.zeta(3), L, L**2, L**3, s5, s5 * L, s5 * L**2, mp.pi**2 * L, mp.log(2), mp.log(3), mp.log(5),
             mp.polylog(2, 1 / lam**2), mp.polylog(3, 1 / lam**2), mp.polylog(2, 1 / lam), mp.catalan, mp.pi, mp.pi**2 * s5]
    mp.mp.dps = 115
    for k, v in sums.items():
        rel = mp.pslq([v] + basis, maxcoeff=10**4, maxsteps=10**6)
        txt = "no relation (|coeff| <= 1e4)" if not rel or rel[0] == 0 else " ".join(f"{-r:+d}/{rel[0]}*{nm}" for r, nm in zip(rel[1:], names) if r)
        print(f"  {k:<26} = {mp.nstr(v, 32)}   {txt}")
    # control: Hines product, all curves: prod coth^{2h} -- here the unweighted analogue sum g with heights is not computed;
    # control instead: the known value F(3) = log lam must be found if inserted
    rel = mp.pslq([F(3)] + basis, maxcoeff=10**4, maxsteps=10**6); print("  control F(3) =", " ".join(f"{-r:+d}/{rel[0]}*{nm}" for r, nm in zip(rel[1:], names) if r))


def ball_area(cv):
    """Area of B = {N <= 1}: polygon through the corners +-v/N(v) of all curves, in angular order (missing corners cost
    triangles of size ~ g |side|^2, below the summation tolerance)."""
    pts = []
    for v, c in cv.items():
        n = F(c)
        for sgn in (1, -1): pts.append((mp.atan2(sgn * v[1], sgn * v[0]), sgn * v[0] / n, sgn * v[1] / n))
    pts.sort(key=lambda p: p[0])
    return sum(p[1] * q[2] - q[1] * p[2] for p, q in zip(pts, pts[1:] + pts[:1])) / 2


def second_pass():
    mp.mp.dps = 140
    z = (0, 0, 0); cv = all_curves(z, 0, 3, 3)
    mcs = sum((1 - mp.sqrt(1 - 4 / c**2)) / 2 for c in cv.values())
    A = sum(mp.log(c * c / (c * c - 4)) * F(c) for c in cv.values()); AB = ball_area(cv)
    cv2 = all_curves(z, 0, 3, 3, tol=mp.mpf(10)**-95); AB2 = ball_area(cv2)
    print(f"control, McShane over the same curves: sum h = {mp.nstr(mcs, 50)} (should be 1/2; error {mp.nstr(mcs - mp.mpf(1) / 2, 3)})")
    print(f"Area(B) = {mp.nstr(AB, 45)}  (tolerance 1e-125 vs 1e-95: difference {mp.nstr(AB - AB2, 3)})")
    print(f"Area(B) x A* = {mp.nstr(AB * A, 40)};  A*/Area(B) = {mp.nstr(A / AB, 40)};  Area(B) x A* / pi^2 = {mp.nstr(AB * A / mp.pi**2, 30)}")
    lam = (3 + mp.sqrt(5)) / 2; L = mp.log(lam); s5 = mp.sqrt(5)
    names = ["1", "pi^2", "zeta3", "logl", "logl^2", "s5", "s5 logl", "log2", "log3", "log5", "1/logl", "1/logl^2", "s5/logl", "pi", "Li2(1/l^2)"]
    basis = [mp.mpf(1), mp.pi**2, mp.zeta(3), L, L**2, s5, s5 * L, mp.log(2), mp.log(3), mp.log(5), 1 / L, 1 / L**2, s5 / L, mp.pi, mp.polylog(2, 1 / lam**2)]
    mp.mp.dps = 85
    for k, v in (("Area(B)", AB), ("Area(B) A*", AB * A), ("A*/Area(B)", A / AB), ("1/Area(B)", 1 / AB)):
        rel = mp.pslq([v] + basis, maxcoeff=10**4, maxsteps=10**6)
        print(f"  {k:<12} = {mp.nstr(v, 30)}  ", "no relation (|coeff| <= 1e4)" if not rel or rel[0] == 0 else " ".join(f"{-r:+d}/{rel[0]}*{nm}" for r, nm in zip(rel[1:], names) if r))
    rel = mp.pslq([mcs] + basis, maxcoeff=10**4, maxsteps=10**6)
    print("  control McShane sum found as:", " ".join(f"{-r:+d}/{rel[0]}*{nm}" for r, nm in zip(rel[1:], names) if r))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "ball":
    second_pass()
