"""Three limits of the stable-norm ball of one-holed / cone / cusped tori, x^2 + y^2 + z^2 - xyz = mu.

Flat limit mu -> 4 (cone angle 2 pi - delta, delta = hyperbolic area, mu - 2 = 2 cos(delta/2)):
    predictions: Mahler volume -> pi^2 (ellipse); A* = sum g N ~ pi delta / 4 and Area(B) ~ 4 pi / delta, the dual-area
    identity reducing to int_0^inf r^2/sinh^2 r dr = pi^2/6.
Tropical limit mu -> -infinity (long boundary): N(p, q) -> l1|p| + l2|q| + l3|p - q| (theta-graph lengths, from
    log a = l1 + l3, log b = l2 + l3, log c = l1 + l2 with c the trace of e0 - e1); B -> hexagon, B* -> zonotope;
    gap law g(e0) = log((a^2 - mu)/(a^2 - 4)) -> 2 l2, etc.; Mahler -> the hexagon's value (9 when l1 = l2 = l3).
Pinching a -> 2: Mahler -> 8 (parallelogram).
Double precision; curves best first until g N < 1e-13.
"""
import heapq, math, sys
import numpy as np


def curves(a, b, mu, tol=1e-13, cap=3_000_000):
    """All simple curves mod sign: e0, e1, interiors of cones (e0, e1) and (e0, -e1). Torus mediant rule c = xy - z."""
    disc = (a * b)**2 - 4 * (a * a + b * b - mu); c = (a * b - math.sqrt(max(disc, 0))) / 2; w = a * b - c
    tr = {(1, 0): a, (0, 1): b, (0, -1): b, (1, -1): c, (1, 1): w}; out = {(1, 0): a, (0, 1): b}
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        h = [(-1.0, 0, e0, e1, opp)]; n = 0
        while h and len(out) < cap:
            _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); t = tr[L] * tr[R] - tr[o]; tr[m] = t; out[m] = t; n += 1
            if gN(t, mu) > tol:
                for (x, y, oo) in ((L, m, R), (m, R, L)):
                    heapq.heappush(h, (-gN(tr[x] * tr[y], mu), n, x, y, oo))
    return out, c


def N(t): return math.acosh(t / 2)
def g(t, mu): return math.log1p((4 - mu) / (t * t - 4))
def gN(t, mu): return g(t, mu) * N(t) if t > 2 else 1.0


def invariants(a, b, mu):
    cv, c = curves(a, b, mu)
    As = sum(g(t, mu) * N(t) for t in cv.values())
    pts = sorted(((math.atan2(s * v[1], s * v[0]), s * v[0] / N(t), s * v[1] / N(t)) for v, t in cv.items() for s in (1, -1)))
    AB = 0.5 * sum(p[1] * q[2] - q[1] * p[2] for p, q in zip(pts, pts[1:] + pts[:1]))
    return AB, As, AB * As, len(cv), c


def hexagon_mahler(l1, l2, l3):
    """B = {l1|x| + l2|y| + l3|x - y| <= 1} (third basic curve e0 - e1), B* = zonotope sum l_i [-u_i, u_i]."""
    s13, s23, s12 = 1 / (l1 + l3), 1 / (l2 + l3), 1 / (l1 + l2)
    V = [(s13, 0), (s12, s12), (0, s23), (-s13, 0), (-s12, -s12), (0, -s23)]   # on y=0, x=y, x=0 (N(1,1) = l1 + l2)
    AB = 0.5 * sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(V, V[1:] + V[:1])); AZ = 4 * (l1 * l2 + l1 * l3 + l2 * l3)
    return AB, AZ, AB * AZ


if __name__ == "__main__":
    pi2 = math.pi**2
    print("FLAT LIMIT: symmetric cone tori (a, a, a), mu = 3a^2 - a^3 -> 4 as a -> 2")
    for a in (2.6, 2.3, 2.1, 2.05, 2.02, 2.01):
        mu = 3 * a * a - a**3; delta = 2 * math.acos((mu - 2) / 2)
        AB, As, M, n, _ = invariants(a, a, mu)
        print(f"  a = {a}: mu = {mu:.5f}, area delta = {delta:.5f}; {n} curves; Mahler = {M:.6f} = {M / pi2:.6f} pi^2;  "
              f"A* / (pi delta/4) = {As / (math.pi * delta / 4):.5f};  Area(B) / (4 pi/delta) = {AB / (4 * math.pi / delta):.5f}")
    print("FLAT LIMIT, non-symmetric shape: (a, b) with c from mu; fixed ratio of log-traces, mu -> 4")
    for eps in (0.3, 0.15, 0.08, 0.04):
        a, b = 2 * math.cosh(eps), 2 * math.cosh(1.3 * eps); cosang = 0.3   # flat lattice: |e0| = 2 eps, |e1| = 2.6 eps, angle via c
        c = 2 * math.cosh(eps * math.sqrt(1 + 1.69 - 2 * 1.3 * cosang))     # |e0 - e1| flat
        mu = a * a + b * b + c * c - a * b * c; delta = 2 * math.acos(max(-1, min(1, (mu - 2) / 2)))
        if not (c < a * b - c): continue
        AB, As, M, n, _ = invariants(a, b, mu)
        print(f"  eps = {eps}: mu = {mu:.5f}; {n} curves; Mahler = {M:.6f} = {M / pi2:.6f} pi^2;  A* / (pi delta/4) = {As / (math.pi * delta / 4):.5f}")
    print("TROPICAL LIMIT: long boundary, mu -> -infinity")
    for a in (6.0, 20.0, 100.0, 1000.0, 1e5):
        mu = 3 * a * a - a**3; AB, As, M, n, c = invariants(a, a, mu)
        l = math.log(a) / 2; Ah, Az, Mh = hexagon_mahler(l, l, l)
        print(f"  symmetric (a, a, a), a = {a:g}: mu = {mu:.3g}; {n} curves; Mahler = {M:.6f} (regular hexagon {Mh:.6f});  "
              f"Area(B) x l^2 = {AB * l * l:.5f} (hexagon {Ah * l * l:.5f}); A*/l^2 = {As / l**2:.5f} (zonotope {Az / l**2:.5f});  "
              f"g(e0)/(2 l) = {g(a, mu) / (2 * l):.5f}")
    for (la, lb, lc) in ((1.0, 1.5, 2.2), (1.0, 3.0, 3.5)):
        for scale in (5.0, 20.0, 60.0):
            a, b, c = math.exp(scale * la), math.exp(scale * lb), math.exp(scale * lc)   # log-traces of e0, e1, e0 - e1
            if not (c >= b and c <= a * b / 2): continue
            mu = a * a + b * b + c * c - a * b * c
            l1, l2, l3 = (math.log(a) + math.log(c) - math.log(b)) / 2, (math.log(b) + math.log(c) - math.log(a)) / 2, (math.log(a) + math.log(b) - math.log(c)) / 2
            AB, As, M, n, _ = invariants(a, b, mu); Ah, Az, Mh = hexagon_mahler(l1, l2, l3)
            print(f"  log-trace ratios ({la}, {lb}, {lc}) x {scale:g}: theta lengths ({l1:.3g}, {l2:.3g}, {l3:.3g}); Mahler = {M:.6f}, hexagon {Mh:.6f};  "
                  f"g(e0)/(2 l2) = {g(a, mu) / (2 * l2):.5f}, g(e1)/(2 l1) = {g(b, mu) / (2 * l1):.5f}")
    print("hexagon Mahler volume over theta-graph shapes (l1, l2, l3) with l1 + l2 + l3 = 1:")
    vals = [(hexagon_mahler(x, y, 1 - x - y)[2], x, y) for x in np.linspace(0.01, 0.98, 98) for y in np.linspace(0.01, 0.98, 98) if x + y < 0.99]
    print(f"  max {max(vals)[0]:.6f} at {max(vals)[1:]}, min {min(vals)[0]:.6f} at ({min(vals)[1]:.2f}, {min(vals)[2]:.2f})")
    print("PINCHING: a -> 2 at fixed mu = 0 (cusped), b mid-range")
    for a in (2.01, 2.003, 2.001, 2.0003):
        lo, hi = max(a, 2 * a / math.sqrt(a * a - 4)), a / math.sqrt(a - 2); AB, As, M, n, _ = invariants(a, (lo + hi) / 2, 0.0)
        la = 2 * math.acosh(a / 2); print(f"  a = {a}: l(alpha) = {la:.4f}; {n} curves; Mahler = {M:.5f}; (M - 8) x log(1/l) = {(M - 8) * math.log(1 / la):.4f}")
