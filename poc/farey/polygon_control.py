"""Control: lattice error of fixed convex polygons, to calibrate what B's error means.
Polygons: (i) p8 = hull of v/N(v), N(v) <= 8 (36 corners, edges carry ratios of geodesic lengths);
(ii) p8 after a fixed generic area-preserving linear map; (iii) a random centrally symmetric 36-gon; (iv) a square rotated by
the golden angle (4 badly approximable edges). Column counting; rms over random R in [w, 2w]."""
import math, numpy as np, sys
sys.setrecursionlimit(10000)
def L(t): return 2 * math.acosh(t / 2)
pts = []
def cone(u, w, tu, tw, td, T):
    tm = tu * tw - td
    if L(tm) > T: return
    m = (u[0] + w[0], u[1] + w[1]); pts.append((m, L(tm)))
    cone(u, m, tu, tm, tw, T); cone(m, w, tm, tw, tu, T)
T = 8.0
pts += [((1, 0), L(3)), ((0, 1), L(3)), ((1, 1), L(3))]
cone((1, 0), (1, 1), 3, 3, 3, T); cone((1, 1), (0, 1), 3, 3, 3, T); cone((0, 1), (-1, 0), 3, 3, 3, T)
V = np.array([[p[0] / n, p[1] / n] for p, n in pts]); V = np.vstack([V, -V])
def sort_ccw(W): return W[np.argsort(np.arctan2(W[:, 1], W[:, 0]))]
def area(W): return 0.5 * np.sum(W[:, 0] * np.roll(W[:, 1], -1) - W[:, 1] * np.roll(W[:, 0], -1))
def make_counter(W):
    W = sort_ccw(W); A = area(W)
    ix = np.argmin(W[:, 0]); W = np.roll(W, -ix, axis=0); jx = np.argmax(W[:, 0])
    low = W[:jx + 1]; up = np.vstack([W[jx:], W[:1]])[::-1]
    def cnt(R):
        x = np.arange(math.ceil(R * W[:, 0].min()), math.floor(R * W[:, 0].max()) + 1)
        yl = np.interp(x / R, low[:, 0], low[:, 1]) * R; yu = np.interp(x / R, up[:, 0], up[:, 1]) * R
        return np.sum(np.floor(yu) - np.ceil(yl) + 1) - 1
    return cnt, A
rng = np.random.default_rng(0)
M = np.array([[1.0, 0.1234567], [0.0712345, 1.0]]); M /= math.sqrt(np.linalg.det(M))
th = np.sort(rng.uniform(0, np.pi, 18)); rr = rng.uniform(0.45, 0.55, 18)
Rnd = np.array([[r * math.cos(t), r * math.sin(t)] for r, t in zip(rr, th)]); Rnd = np.vstack([Rnd, -Rnd])
from scipy.spatial import ConvexHull
Rnd = Rnd[ConvexHull(Rnd).vertices]
g = math.pi * (3 - math.sqrt(5)); Sq = 0.5 * np.array([[math.cos(g + k * math.pi / 2), math.sin(g + k * math.pi / 2)] for k in range(4)])
shapes = {"p8 (B corners N<=8)": V, "p8 sheared": V @ M.T, "random 36-gon": Rnd, "golden square": Sq}
W_ = (50, 100, 200, 400, 800, 1600)
for name, W in shapes.items():
    cnt, A = make_counter(W)
    r = []
    for w in W_:
        Rs = rng.uniform(w, 2 * w, 1200); e = np.array([cnt(R) for R in Rs]) - A * Rs ** 2
        r.append(math.sqrt(np.mean(e ** 2)))
    print("%-22s corners %3d  rms: %s   local exps: %s" % (name, len(sort_ccw(W)), " ".join("%7.2f" % x for x in r),
          " ".join("%.2f" % (math.log(r[i + 1] / r[i], 2)) for i in range(len(r) - 1))))

# which property matters? (a) corners on lattice rays with generic radii; (b) true radii 1/N(v) but corners moved off the rays
print()
U = np.vstack([np.array([p for p, n in pts], float), -np.array([p for p, n in pts], float)])
Nn = np.concatenate([[n for p, n in pts]] * 2)
for trial in range(2):
    fac = np.exp(rng.normal(0, 0.004, len(pts))); fac = np.concatenate([fac, fac])
    Wa = U / (Nn * fac)[:, None]
    from scipy.spatial import ConvexHull
    Wa = Wa[ConvexHull(Wa).vertices]
    rot = 0.003 * (trial + 1); Rm = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]])
    for name, W in (("(a) lattice rays, radii x e^N(0,.004)", Wa), ("(b) true radii, rotated %.3f rad" % rot, V @ Rm.T)):
        cnt, A = make_counter(W); r = []
        for w in W_:
            Rs = rng.uniform(w, 2 * w, 1200); e = np.array([cnt(R) for R in Rs]) - A * Rs ** 2
            r.append(math.sqrt(np.mean(e ** 2)))
        print("%-40s corners %3d  rms: %s   local exps: %s" % (name, len(W), " ".join("%7.2f" % x for x in r),
              " ".join("%.2f" % (math.log(r[i + 1] / r[i], 2)) for i in range(len(r) - 1))))
