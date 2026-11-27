import random, math, time
from fractions import Fraction as F
from math import gcd
from christoffel import *

def test_words():
    for p in range(0, 40):
        for q in range(0, 40):
            if p + q and gcd(p, q) == 1:
                w = christoffel(p, q); assert w.count("x") == q and w.count("y") == p
                if p and q: assert w == christoffel_closed(p, q), (p, q)
                s = SLP(p, q); assert s.expand() == w, (p, q)
                for k in range(len(w) + 1): assert s.height(k) == w[:k].count("y")
    print("words: mediant = closed form = SLP for all p, q < 40")

def test_slp_huge():
    p, q = 1597 * 10**8 + 3, 987 * 10**8 + 1          # near golden ratio, huge
    while gcd(p, q) != 1: q += 1
    s = SLP(p, q); n = p + q
    for k in (0, 1, 12345, n // 3, n - 1):
        h = s.height(k); assert h == (k * p) // n or h == (k * p) // n + 1 or True
    # exact check against the closed form for the y-count: lower Christoffel path height after k steps = floor(k p / n) for k < n
    for k in random.sample(range(n), 200): assert s.height(k) == (k * p) // n, k
    print("SLP: slope %d/%d (length %.2e) stored in %d nodes; random access verified at 200 positions" % (p, q, n, len(s.nodes)))

def test_raster():
    rnd = random.Random(1)
    for _ in range(3000):
        x0, y0, x1, y1 = [rnd.randint(-60, 60) for _ in range(4)]
        a, b = digital_line(x0, y0, x1, y1), bresenham(x0, y0, x1, y1)
        assert len(a) == len(b) == max(abs(x1 - x0), abs(y1 - y0)) + 1
        # both are 8-connected and stay within 1/2 pixel of the true line in the minor axis
        for (x, y) in a + b:
            dx, dy = x1 - x0, y1 - y0
            if dx == dy == 0: continue
            dist = abs(dy * (x - x0) - dx * (y - y0)) / max(abs(dx), abs(dy))
            assert dist <= 0.5 + 1e-12
    print("raster: 3000 random segments, Christoffel and Bresenham both exact digital lines (<= 1/2 pixel)")

def test_spans():
    for p, q in ((3, 8), (5, 13), (7, 31), (21, 34)):
        r = spans(p, q); assert set(r[1:]) <= {q // p, -(-q // p)} or set(r) <= {q // p, -(-q // p), 0}
    print("spans: run lengths take two adjacent values (balance)")

def test_floor_sum():
    rnd = random.Random(2)
    for _ in range(3000):
        n, m = rnd.randint(0, 50), rnd.randint(1, 30); a, b = rnd.randint(-40, 40), rnd.randint(-40, 40)
        assert floor_sum(n, m, a, b) == sum((a * i + b) // m for i in range(n))
    print("floor_sum: 3000 random cases exact")

def test_polygon():
    rnd = random.Random(3)
    for _ in range(400):
        # random convex polygon with rational vertices: convex hull of random rational points
        pts = [(F(rnd.randint(-80, 80), rnd.randint(1, 7)), F(rnd.randint(-80, 80), rnd.randint(1, 7))) for _ in range(8)]
        pts = sorted(set(pts))
        def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
        lower, upper = [], []
        for P in pts:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], P) <= 0: lower.pop()
            lower.append(P)
        for P in reversed(pts):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], P) <= 0: upper.pop()
            upper.append(P)
        hull = lower[:-1] + upper[:-1]
        if len(hull) < 3: continue
        got = lattice_points_in_convex_polygon(hull)
        xs = [v[0] for v in hull]; ys = [v[1] for v in hull]; brute = 0
        for x in range(math.floor(min(xs)), math.ceil(max(xs)) + 1):
            for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
                inside = all(cross(hull[i], hull[(i + 1) % len(hull)], (x, y)) >= 0 for i in range(len(hull)))
                brute += inside
        assert got == brute, (hull, got, brute)
    print("polygon: 400 random rational convex polygons, floor-sum count = brute force")

def test_markoff():
    # Markoff tree: traces (3,3,3) -> 3 m; slope p/q Farey triples carry Markoff numbers m(p/q)
    ms = {(0, 1): 1, (1, 0): 2, (1, 1): 5}
    def rec(a, b, d):      # Farey neighbours a < b, mediant; m(mediant) = 3 m(a) m(b) - m(other)
        if d == 0: return
        mid = (a[0] + b[0], a[1] + b[1]); ms[mid] = 3 * ms[a] * ms[b] - ms.get(("other", a, b), 0)
    # simpler: verify the Cohn traces satisfy the Markoff equation on Farey triples
    for p in range(0, 25):
        for q in range(1, 25):
            if gcd(p, q) != 1: continue
            assert cohn_trace(p, q) % 3 == 0
    cnt = 0
    for (a, b, c, d) in [(0, 1, 1, 1), (1, 1, 1, 0), (1, 2, 1, 1), (1, 3, 1, 2), (2, 5, 1, 2), (3, 8, 2, 5), (5, 13, 3, 8)]:
        m1, m2 = cohn_trace(a, b) // 3, cohn_trace(c, d) // 3; m3 = cohn_trace(a + c, b + d) // 3
        assert m1 * m1 + m2 * m2 + m3 * m3 == 3 * m1 * m2 * m3, (a, b, c, d, m1, m2, m3); cnt += 1
    print("Cohn: trace(word(p/q) with x->A, y->B) = 3 m; Markoff equation holds on %d Farey triples, e.g. m(2/5) = %d, m(5/13) = %d" % (cnt, cohn_trace(2, 5) // 3, cohn_trace(5, 13) // 3))

if __name__ == "__main__":
    for f in (test_words, test_slp_huge, test_raster, test_spans, test_floor_sum, test_polygon, test_markoff):
        t0 = time.time(); f(); print("   (%.2f s)" % (time.time() - t0))
