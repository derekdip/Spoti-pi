"""Exact Farey-cell lattice count for a general cusped once-punctured torus, rooted at its Bowditch sink (x, y, z):
traces of e0, e1, e0+e1 with xy - z >= z, xz - y >= y, yz - x >= x. Root hexagon on rays e0, e0+e1, e1 (+-), cones
(e0, e0+e1), (e0+e1, e1), (e1, -e0) with mediant traces xz - y, zy - x, yx - z."""
import math, numpy as np
from mpmath import mp, mpf, acosh as macosh
mp.dps = 40
def sink(x, y):
    z = (x * y - math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y), 0))) / 2      # smaller root
    t = [x, y, z]
    for _ in range(1000):
        changed = False
        for i in range(3):
            j, k = [m for m in range(3) if m != i]
            other = t[j] * t[k] - t[i]
            if other < t[i] - 1e-12: t[i] = other; changed = True
        if not changed: break
    return sorted(t)[0], sorted(t)[1], sorted(t)[2]
class Torus:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = mpf(x), mpf(y), mpf(z)
        L = lambda tr: 2 * macosh(tr / 2)
        self.a, self.b, self.c = float(L(self.x)), float(L(self.y)), float(L(self.z))
        self.L = L
        self.area = self._area()
    def roots(self):
        x, y, z = self.x, self.y, self.z
        return [(x, z, y), (z, y, x), (y, x, z)]
    def cells(self, R, ETA=1e-3, NMAX=None):
        out = []; st = list(self.roots()); L = self.L
        while st:
            tu, tw, td = st.pop(); tm = tu * tw - td
            a, b, c = L(tu), L(tw), L(tm); dl = a + b - c
            if NMAX is not None:
                if float(a + b) > NMAX: continue
            elif float(dl) * R * R < ETA and float(a + b) > 2 * math.log(R) + 6: continue
            out.append((float(a), float(b), float(dl))); st += [(tu, tm, tw), (tm, tw, tu)]
        return out
    def _area(self):
        a, b, c = self.a, self.b, self.c
        A = 1 / (a * c) + 1 / (c * b) + 1 / (b * a)
        for lu, lw, dl in self.cells(1.0, NMAX=70): A += dl / (lu * lw * (lu + lw - dl))
        return A
def T(p, q, R):
    if R < p + q: return 0
    beta = np.arange(1, int((R - p) / q) + 1); return int(np.sum(np.floor((R - beta * q) / p)))
def S_cell(R, lu, lw, dl):
    tot = 0; bmax = int(R / (lu + lw - dl)) + 1
    b = np.arange(1, bmax + 1, dtype=float)
    lo = np.maximum(np.floor((R - b * lw) / lu), b - 1); hi = np.floor((R - b * (lw - dl)) / lu); tot += int(np.sum(np.maximum(hi - lo, 0)))
    a = np.arange(1, bmax + 1, dtype=float)
    lo = np.maximum(np.floor((R - a * lu) / lw), a); hi = np.floor((R - a * (lu - dl)) / lw); tot += int(np.sum(np.maximum(hi - lo, 0)))
    return tot
def E(X, R):
    a, b, c = X.a, X.b, X.c
    root = 2 * (int(R // a) + int(R // b) + int(R // c) + T(a, c, R) + T(c, b, R) + T(b, a, R))
    return root + 2 * sum(S_cell(R, *cl) for cl in X.cells(R)) - X.area * R * R
if __name__ == "__main__":
    import sys
    rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    for trial in range(3):
        x = 2.05 + 3 * rng.random(); b = 2 * math.sqrt(x * x / (x * x - 4)) * math.cosh(rng.random() * 2)  # FN-type second trace
        s = sink(x, b); X = Torus(*s)
        # direct enumeration from the sink: all primitive classes are the sink's 3 curves plus all descendants
        lens = [X.a, X.b, X.c]; st = list(X.roots())
        while st:
            tu, tw, td = st.pop(); tm = tu * tw - td; lm = float(X.L(tm))
            if lm > 400: continue
            lens.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
        Ns = np.sort(np.array(lens))
        mult = np.sort(np.concatenate([Ns[:np.searchsorted(Ns, 400 / k, side='right')] * k for k in range(1, int(400 / Ns[0]) + 1)]))
        print("surface: sink traces (%.4f, %.4f, %.4f), lengths (%.4f, %.4f, %.4f), Area(B) = %.8f" % (s + (X.a, X.b, X.c, X.area)))
        for R in sorted(rng.uniform(50, 390, 4)):
            d = 2 * np.searchsorted(mult, R, side="right") - X.area * R * R
            print("   R = %7.2f: direct E = %10.4f   cells E = %10.4f" % (R, d, E(X, R)))
