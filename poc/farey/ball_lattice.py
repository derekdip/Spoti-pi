"""Lattice-point error of the stable-norm ball B of the modular torus, against controls.

E_K(R) = #{v in Z^2 \\ 0 : v in R K} - Area(K) R^2, rms over windows [R, 2R], for
  B      : the stable-norm ball (gauge N, corners at every rational direction, corner jumps = gap law)
  disk   : Euclidean disk of the same area (circle problem: rms ~ R^(1/2))
  poly_T : the polygon hull of {v/N(v) : N(v) <= T} (finitely many corners: rms grows like log R)
Also the corner-resolution heuristic: at dilation R, B looks like the polygon hull of vertices with N(v) <= T(R);
the number of corners resolved at scale R is counted directly.
"""
import math, sys, numpy as np
sys.setrecursionlimit(100000)
RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 1000.0
prim, edges = [], []   # (p, q, N)
def L(t): return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)
def cone(u, w, tu, tw, td, lu, lw):
    tm = tu * tw - td
    lm = L(tm)
    if lm > RMAX:
        return
    m = (u[0] + w[0], u[1] + w[1]); prim.append((m[0], m[1], lm))
    cone(u, m, tu, tm, tw, lu, lm); cone(m, w, tm, tw, tu, lm, lw)
l3 = L(3)
prim += [(1, 0, l3), (0, 1, l3), (1, 1, l3)]
cone((1, 0), (1, 1), 3, 3, 3, l3, l3); cone((1, 1), (0, 1), 3, 3, 3, l3, l3); cone((0, 1), (-1, 0), 3, 3, 3, l3, l3)
P = np.array(prim, dtype=float)
ang = np.arctan2(P[:, 1], P[:, 0]); o = np.argsort(ang); P = P[o]
# B polygon area from consecutive directions (half plane, then double)
V = P[:, :2] / P[:, 2:3]
Vfull = np.vstack([V, -V])
def poly_area(W):
    a = np.arctan2(W[:, 1], W[:, 0]); W = W[np.argsort(a)]
    return 0.5 * np.sum(W[:, 0] * np.roll(W[:, 1], -1) - W[:, 1] * np.roll(W[:, 0], -1))
areaB = poly_area(Vfull)
print("primitive classes (mod sign) with N <= %g: %d; Area(B) = %.10f" % (RMAX, len(P), areaB))

# lengths of all lattice points in B-gauge: N(k v) = k N(v)
Ns = np.sort(P[:, 2])
mult = np.sort(np.concatenate([Ns[:np.searchsorted(Ns, RMAX / k, side='right')] * k for k in range(1, int(RMAX / l3) + 1)]))
mult = mult[mult <= RMAX]
def count_B(R): return 2 * np.searchsorted(mult, R, side="right")

# disk of equal area: count via rows
def count_disk(R):
    r = R * math.sqrt(areaB / math.pi); x = np.arange(-int(r), int(r) + 1)
    return int(np.sum(2 * np.floor(np.sqrt(np.maximum(r * r - x * x, 0))) + 1)) - 1

# polygon hull of vertices with N <= T: gauge = max over hull edges of the linear functional
def poly_gauge_counter(T):
    W = np.vstack([V[P[:, 2] <= T], -V[P[:, 2] <= T]])
    W = W[np.argsort(np.arctan2(W[:, 1], W[:, 0]))]
    W2 = np.roll(W, -1, axis=0)
    nrm = np.stack([W2[:, 1] - W[:, 1], W[:, 0] - W2[:, 0]], 1)     # outward normal (ccw order)
    c = np.sum(nrm * W, 1); F = nrm / c[:, None]                     # functional f with f = 1 on the edge
    area = poly_area(W)
    # upper and lower chains for column counting
    ix = np.argmin(W[:, 0]); W = np.roll(W, -ix, axis=0)       # start at leftmost vertex, ccw: lower chain first
    jx = np.argmax(W[:, 0])
    low = W[:jx + 1]; up = np.vstack([W[jx:], W[:1]])[::-1]
    def counter(R):
        x = np.arange(math.ceil(R * W[:, 0].min()), math.floor(R * W[:, 0].max()) + 1)
        yl = np.interp(x / R, low[:, 0], low[:, 1]) * R; yu = np.interp(x / R, up[:, 0], up[:, 1]) * R
        return int(np.sum(np.floor(yu + 1e-12) - np.ceil(yl - 1e-12) + 1)) - 1
    return counter, area, len(W)
print("extent check: max |v/N(v)| = %.3f" % np.max(np.abs(V)))

rng = np.random.default_rng(3)
def rms(counter, area, Rlo, n=1500):
    Rs = rng.uniform(Rlo, 2 * Rlo, n)
    e = np.array([counter(R) - area * R * R for R in Rs]); return math.sqrt(np.mean(e ** 2)), np.mean(e)
windows = [w for w in (25, 50, 100, 200, 400, 800, 1600) if 2 * w <= RMAX]
print("\nrms of E over [R, 2R]:")
print("   R      B         disk      poly(T=8)  poly(T=15)")
cp8, a8, n8 = poly_gauge_counter(8); cp15, a15, n15 = poly_gauge_counter(15)
res = {"B": [], "disk": [], "p8": [], "p15": []}
for R0 in windows:
    rb = rms(count_B, areaB, R0)[0]; rd = rms(count_disk, areaB, R0)[0]
    r8 = rms(cp8, a8, R0)[0]; r15 = rms(cp15, a15, R0)[0]
    for k, v in zip(res, (rb, rd, r8, r15)): res[k].append(v)
    print("  %4d  %8.3f  %8.3f  %8.3f  %8.3f" % (R0, rb, rd, r8, r15))
print("(polygons: %d and %d corners)" % (n8, n15))
for k in ("B", "disk"):
    print("fitted rms exponent %-5s: %.3f" % (k, np.polyfit(np.log(windows[1:]), np.log(res[k][1:]), 1)[0]))
for k in ("p8", "p15"):
    print("fitted rms exponent %-5s: %.3f" % (k, np.polyfit(np.log(windows[1:]), np.log(res[k][1:]), 1)[0]))

# corner resolution: corners of B whose 'sagitta' at dilation R exceeds one lattice spacing.
# For Farey neighbours (v, w) with mediant m, the boundary between v/N(v) and w/N(w) bulges past the chord by
# h = area of triangle(v/Nv, m/Nm, w/Nw) * 2 / |chord|; resolved at scale R if R h > 1/R-ish -> count R*h*R >= 1? use R h >= 1/|R chord|.
