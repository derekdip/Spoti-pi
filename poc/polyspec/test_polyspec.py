import random, math, cmath, itertools
from fractions import Fraction as Fr
from polyspec import ueuclid, emul, EONE, G_exp, G_lin, polygon_dft
rng = random.Random(7)
# 1. universal Euclid word vs explicit word
for _ in range(2000):
    p, q = rng.randint(0, 30), rng.randint(1, 30); r = rng.randint(0, q - 1); l = rng.randint(0, 40)
    word = []; prev = r // q
    for t in range(1, l + 1):
        cur = (p * t + r) // q; word += ["U"] * (cur - prev) + ["R"]; prev = cur
    cat = lambda X, Y: X + Y
    got = ueuclid(p, q, r, l, "U", "R", cat, "")
    assert got == "U" * (r // q) * 0 + "".join(word) or got == "".join(word), (p, q, r, l)
print("universal Euclid word: 2000 random cases OK")
# 2. G sums vs direct
for _ in range(2000):
    n = rng.randint(0, 60); a = rng.randint(-40, 40); b = rng.randint(-200, 200); c = rng.randint(1, 30)
    w = cmath.exp(2j * rng.random() * math.pi); z = cmath.exp(2j * rng.random() * math.pi)
    d1 = sum(w ** t * z ** ((a * t + b) // c) for t in range(n)); d2 = sum(w ** t * ((a * t + b) // c) for t in range(n))
    assert abs(G_exp(n, a, b, c, w, z) - d1) < 1e-9 * (1 + n * n), (n, a, b, c)
    assert abs(G_lin(n, a, b, c, w) - d2) < 1e-9 * (1 + n * n * 10), (n, a, b, c)
print("G_exp, G_lin vs direct sums: 2000 random cases OK")
# 3. polygon DFT vs brute force over lattice points
def inside(verts, x, y):
    n = len(verts)
    for i in range(n):
        (x1, y1), (x2, y2) = verts[i], verts[(i + 1) % n]
        if (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) < 0: return False
    return True
def rand_convex(R):
    pts = [(Fr(rng.randint(-R * 7, R * 7), 7), Fr(rng.randint(-R * 5, R * 5), rng.choice([1, 3, 5]))) for _ in range(12)]
    pts = sorted(set(pts))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
worst = 0; cases = 0
for trial in range(60):
    R = rng.choice([3, 8, 20]); V = rand_convex(R)
    if len(V) < 3: continue
    xs = [v[0] for v in V]; ys = [v[1] for v in V]
    L = [(x, y) for x in range(math.floor(min(xs)), math.ceil(max(xs)) + 1) for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1) if inside(V, x, y)]
    N = 64
    for kx, ky in [(0, 0), (1, 0), (0, 1), (5, 0), (0, 7), (3, 11), (63, 2), (17, 40)] + [(rng.randrange(N), rng.randrange(N)) for _ in range(6)]:
        bf = sum(cmath.exp(-2j * math.pi * (kx * x + ky * y) / N) for x, y in L)
        got = polygon_dft(V, kx, ky, N); worst = max(worst, abs(got - bf)); cases += 1
        assert abs(got - bf) < 1e-8 * (1 + len(L)), (V, kx, ky, got, bf)
print("polygon DFT vs brute force: %d cases on 60 random rational convex polygons OK, max abs error %.1e" % (cases, worst))
