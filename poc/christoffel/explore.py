"""Where Christoffel words could go: (a) exact pixel agreement with Bresenham, (b) compressed random access timing,
(c) Markoff-ranked slopes as sampling generators: star discrepancy of the 2D point sets {(i/N, frac(i alpha))} for
alpha from the Lagrange (Markoff) spectrum vs random slopes."""
import random, time, math
from christoffel import *
# (a)
rnd = random.Random(7); same = 0; tot = 0; diffs = []
for _ in range(5000):
    x0, y0, x1, y1 = [rnd.randint(-200, 200) for _ in range(4)]
    a, b = digital_line(x0, y0, x1, y1), bresenham(x0, y0, x1, y1); tot += 1
    if a == b: same += 1
    else: diffs.append((x0, y0, x1, y1))
print("(a) pixel-identical to Bresenham in %d / %d random segments" % (same, tot))
# (b)
p, q = 10**12 + 39, 618033988749
from math import gcd
while gcd(p, q) != 1: q += 1
t0 = time.time(); s = SLP(p, q); tb = time.time() - t0
ks = [rnd.randrange(p + q) for _ in range(20000)]
t0 = time.time(); hs = [s.height(k) for k in ks]; ta = time.time() - t0
assert all(h == (k * p) // (p + q) for h, k in zip(hs, ks))
print("(b) line of %.2e steps: SLP %d nodes built in %.1f ms; 20000 random height queries in %.1f ms (%.1f us each), all exact" % (p + q, len(s.nodes), 1e3 * tb, 1e3 * ta, 1e6 * ta / len(ks)))
# (c) star discrepancy (exact for 2D via sorting is O(N^2); use N = 610 and the standard grid-corner evaluation)
def star_disc(pts):
    xs = sorted(set([0.0] + [p[0] for p in pts] + [1.0])); n = len(pts); best = 0.0
    pts = sorted(pts)
    for i, x in enumerate(xs[1:], 1):
        ys = sorted(p[1] for p in pts if p[0] < x)          # points strictly left of x (open box)
        ysc = sorted(p[1] for p in pts if p[0] <= x)        # closed
        for k, y in enumerate(ysc):
            best = max(best, abs((k + 1) / n - x * y))
        for k, y in enumerate(ys + [1.0]):
            best = max(best, abs(k / n - x * y))
    return best
N = 610
phi = (1 + 5 ** .5) / 2
markoff_alphas = [("golden (1+sqrt5)/2, Lagrange sqrt5", phi), ("silver 1+sqrt2, Lagrange sqrt8", 1 + 2 ** .5),
                  ("(9+sqrt221)/10, Lagrange sqrt221/5", (9 + 221 ** .5) / 10), ("(23+sqrt1517)/26, Lagrange sqrt1517/13", (23 + 1517 ** .5) / 26)]
for name, a in markoff_alphas:
    pts = [(i / N, (i * a) % 1.0) for i in range(N)]
    print("(c) %-42s D* = %.5f   N D* = %.2f" % (name, star_disc(pts), N * star_disc(pts)))
rs = []
for j in range(8):
    a = random.Random(100 + j).random() * 3
    pts = [(i / N, (i * a) % 1.0) for i in range(N)]; rs.append(N * star_disc(pts))
print("(c) random slopes (8): N D* = %s" % ", ".join("%.1f" % v for v in rs))
