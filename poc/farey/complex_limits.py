"""Complex (quasi-Fuchsian) continuation of the stable-norm invariants and their limits.

With complex traces the complex length N = arccosh(t/2) = (l + i twist)/2 replaces N. The dual area A* = sum g N and the
polygon formula Area(B) = (1/2) sum cross(v_i, v_{i+1}) / (N_i N_{i+1}) (v_i in angular order) are then holomorphic in
the traces wherever the tree sums converge; so is the Mahler product M = Area(B) A*.
Tests: (1) complex flat limit mu -> 4: A* ~ pi delta/4 with complex delta (mu - 2 = 2 cos(delta/2)), M -> pi^2;
(2) complex tropical limit: g(e0) -> 2 l2 etc. with complex theta lengths, A* -> 4 sum l_i l_j, M -> hexagon formula.
"""
import cmath, heapq, math, sys
import numpy as np


def N(t): return cmath.acosh(t / 2)
def g(t, mu): return cmath.log(1 + (4 - mu) / (t * t - 4))


def curves(a, b, mu, tol=1e-13, cap=400_000):
    disc = (a * b)**2 - 4 * (a * a + b * b - mu); r = cmath.sqrt(disc)
    c1, c2 = (a * b - r) / 2, (a * b + r) / 2; c, w = (c1, c2) if abs(c1) <= abs(c2) else (c2, c1)
    tr = {(1, 0): a, (0, 1): b, (0, -1): b, (1, -1): c, (1, 1): w}; out = {(1, 0): a, (0, 1): b}
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        h = [(-1.0, 0, e0, e1, opp)]; n = 0
        while h and len(out) < cap:
            _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); t = tr[L] * tr[R] - tr[o]; tr[m] = t; out[m] = t; n += 1
            if abs(g(t, mu) * N(t)) > tol:
                for (x, y, oo) in ((L, m, R), (m, R, L)):
                    tt = tr[x] * tr[y]; heapq.heappush(h, (-abs(g(tt, mu) * N(tt)), n, x, y, oo))
    return out


def invariants(a, b, mu):
    cv = curves(a, b, mu)
    As = sum(g(t, mu) * N(t) for t in cv.values())
    pts = sorted(((math.atan2(s * v[1], s * v[0]), s * v[0], s * v[1], N(t)) for v, t in cv.items() for s in (1, -1)))
    AB = 0.5 * sum((p[1] * q[2] - q[1] * p[2]) / (p[3] * q[3]) for p, q in zip(pts, pts[1:] + pts[:1]))
    return AB, As, AB * As, len(cv)


def hexagon(l1, l2, l3):
    s13, s23, s12 = 1 / (l1 + l3), 1 / (l2 + l3), 1 / (l1 + l2)
    V = [(s13, 0), (s12, s12), (0, s23), (-s13, 0), (-s12, -s12), (0, -s23)]
    AB = 0.5 * sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(V, V[1:] + V[:1])); AZ = 4 * (l1 * l2 + l1 * l3 + l2 * l3)
    return AB, AZ, AB * AZ


if __name__ == "__main__":
    pi2 = math.pi**2; f = lambda z: f"{z.real:+.6f}{z.imag:+.6f}i"
    print("(1) COMPLEX FLAT LIMIT: symmetric (a, a, a), a = 2 + r e^{i phi}, r -> 0")
    for phi in (0.0, 0.4, 0.8, 1.2):
        for r in (0.3, 0.1, 0.03, 0.01):
            a = 2 + r * cmath.exp(1j * phi); mu = 3 * a * a - a**3; delta = 2 * cmath.acos((mu - 2) / 2)
            AB, As, M, n = invariants(a, a, mu)
            print(f"  phi = {phi}, r = {r}: mu = {f(mu)}, delta = {f(delta)}; {n} curves;  M/pi^2 = {f(M / pi2)};  A*/(pi delta/4) = {f(As / (math.pi * delta / 4))}")
    print("(2) COMPLEX TROPICAL LIMIT: (a, a, a), a = R e^{i phi}, R -> infinity; theta lengths l = log(a)/2 (complex)")
    for phi in (0.3, 0.8):
        for R in (20.0, 300.0, 1e4):
            a = R * cmath.exp(1j * phi); mu = 3 * a * a - a**3; AB, As, M, n = invariants(a, a, mu)
            l = cmath.log(a) / 2; Ah, Az, Mh = hexagon(l, l, l)
            print(f"  phi = {phi}, R = {R:g}: {n} curves; g(e0)/(2l) = {f(g(a, mu) / (2 * l))};  A*/(12 l^2) = {f(As / Az)};  M = {f(M)} (hexagon {f(Mh)})")
    print("    asymmetric complex shape: log traces (1 + 0.3i, 1.5 - 0.2i, 2.2 + 0.1i) x scale")
    for scale in (5.0, 15.0, 40.0):
        la, lb, lc = scale * (1 + 0.3j), scale * (1.5 - 0.2j), scale * (2.2 + 0.1j)
        a, b, c = cmath.exp(la), cmath.exp(lb), cmath.exp(lc); mu = a * a + b * b + c * c - a * b * c
        l1, l2, l3 = (la + lc - lb) / 2, (lb + lc - la) / 2, (la + lb - lc) / 2
        AB, As, M, n = invariants(a, b, mu); Ah, Az, Mh = hexagon(l1, l2, l3)
        print(f"  scale {scale:g}: {n} curves; g(e0)/(2 l2) = {f(g(a, mu) / (2 * l2))}, g(e1)/(2 l1) = {f(g(b, mu) / (2 * l1))};  A*/zonotope = {f(As / Az)};  M = {f(M)}, hexagon {f(Mh)}")


def tree_plan(a, b, mu, tol=1e-13, cap=400_000):
    """The curve set and its creation order (m, L, R, o), from the target point."""
    disc = (a * b)**2 - 4 * (a * a + b * b - mu); r = cmath.sqrt(disc); c1, c2 = (a * b - r) / 2, (a * b + r) / 2
    c, w = (c1, c2) if abs(c1) <= abs(c2) else (c2, c1)
    tr = {(1, 0): a, (0, 1): b, (0, -1): b, (1, -1): c, (1, 1): w}; plan = []
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        h = [(-1.0, 0, e0, e1, opp)]; n = 0
        while h and len(plan) < cap:
            _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); t = tr[L] * tr[R] - tr[o]; tr[m] = t; plan.append((m, L, R, o)); n += 1
            if abs(g(t, mu) * N(t)) > tol:
                for (x, y, oo) in ((L, m, R), (m, R, L)):
                    tt = tr[x] * tr[y]; heapq.heappush(h, (-abs(g(tt, mu) * N(tt)), n, x, y, oo))
    return plan


def continued_invariants(path, steps=400):
    """path(s), s in [0, 1]: (a, b, mu) with path(0) on the real (Fuchsian/cone) locus. N and g of every curve are
    continued along the path (nearest of +-N + 2 pi i k, and g + 2 pi i k), giving the holomorphic continuation."""
    a1, b1, mu1 = path(1.0); plan = tree_plan(a1, b1, mu1)
    vecs = [(1, 0), (0, 1)] + [p[0] for p in plan]
    prevN, prevg, prevc = None, None, None
    for k in range(steps + 1):
        a, b, mu = path(k / steps); disc = (a * b)**2 - 4 * (a * a + b * b - mu); r = cmath.sqrt(disc)
        roots = ((a * b - r) / 2, (a * b + r) / 2)
        if prevc is None: c = min(roots, key=lambda z: abs(z))
        else: c = min(roots, key=lambda z: abs(z - prevc))
        prevc = c; tr = {(1, 0): a, (0, 1): b, (0, -1): b, (1, -1): c, (1, 1): a * b - c}
        for (m, L, R, o) in plan: tr[m] = tr[L] * tr[R] - tr[o]
        T = np.array([tr[v] for v in vecs], dtype=complex)
        n0 = np.arccosh(T / 2); g0 = np.log(1 + (4 - mu) / (T * T - 4))
        if prevN is None: Ns, gs = n0, g0
        else:   # nearest branch: +-n0 + 2 pi i k, and g0 + 2 pi i k, to the previous step's values
            best = None
            for sg in (1, -1):
                k = np.round((prevN - sg * n0).imag / (2 * np.pi)); cand = sg * n0 + 2j * np.pi * k
                best = cand if best is None else np.where(np.abs(cand - prevN) < np.abs(best - prevN), cand, best)
            Ns = best; gs = g0 + 2j * np.pi * np.round((prevg - g0).imag / (2 * np.pi))
        prevN, prevg = Ns, gs
    As = complex(np.sum(gs * Ns)); Ns, gs = list(Ns), list(gs)
    pts = sorted(((math.atan2(s * v[1], s * v[0]), s * v[0], s * v[1], n) for v, n in zip(vecs, Ns) for s in (1, -1)))
    AB = 0.5 * sum((p[1] * q[2] - q[1] * p[2]) / (p[3] * q[3]) for p, q in zip(pts, pts[1:] + pts[:1]))
    return AB, As, AB * As, len(vecs), dict(zip(vecs, gs)), dict(zip(vecs, Ns))


def run_continued():
    pi2 = math.pi**2; f = lambda z: f"{z.real:+.6f}{z.imag:+.6f}i"
    print("(1') COMPLEX FLAT LIMIT with holomorphic continuation (path: rotate phi from 0)")
    for phi in (0.4, 0.8, 1.2):
        for r in (0.1, 0.03, 0.01):
            def path(s, phi=phi, r=r):
                a = 2 + r * cmath.exp(1j * phi * s); return a, a, 3 * a * a - a**3
            a, _, mu = path(1); delta = 2 * cmath.acos((mu - 2) / 2)
            AB, As, M, n, _, _ = continued_invariants(path, steps=120)
            print(f"  phi = {phi}, r = {r}: {n} curves; M/pi^2 = {f(M / pi2)};  A*/(pi delta/4) = {f(As / (math.pi * delta / 4))};  Area(B) delta/(4 pi) = {f(AB * delta / (4 * math.pi))}")
    print("(2') COMPLEX TROPICAL LIMIT with continuation (path: imaginary parts of the log-traces switched on)")
    for (la0, lb0, lc0) in (((1 + 0.3j), (1.5 - 0.2j), (2.2 + 0.1j)), ((1 + 0.8j), (1 + 0.8j), (1 + 0.8j))):
        for scale in (5.0, 15.0, 40.0):
            def path(s, la0=la0, lb0=lb0, lc0=lc0, scale=scale):
                la, lb, lc = [scale * (z.real + 1j * s * z.imag) for z in (la0, lb0, lc0)]
                a, b, c = cmath.exp(la), cmath.exp(lb), cmath.exp(lc); return a, b, a * a + b * b + c * c - a * b * c
            la, lb, lc = [scale * z for z in (la0, lb0, lc0)]
            l1, l2, l3 = (la + lc - lb) / 2, (lb + lc - la) / 2, (la + lb - lc) / 2
            AB, As, M, n, gs, Ns = continued_invariants(path, steps=200); Ah, Az, Mh = hexagon(l1, l2, l3)
            print(f"  shape {la0, lb0, lc0} x {scale:g}: {n} curves; g(e0)/(2 l2) = {f(gs[(1, 0)] / (2 * l2))}, g(e1)/(2 l1) = {f(gs[(0, 1)] / (2 * l1))};  "
                  f"A*/zonotope = {f(As / Az)};  M = {f(M)}, hexagon {f(Mh)}")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "continued":
    run_continued()
