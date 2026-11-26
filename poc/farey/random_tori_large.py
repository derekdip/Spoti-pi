"""Lattice error E_B on random cusped tori up to R = 2e6 (exact cell algorithm), with the largest partial quotient of
the cell rotation numbers in range. Metric theorem prediction: polylog growth for almost every surface."""
import math, numpy as np, sys, time
sys.path.insert(0, "poc/farey")
from cell_count_general import sink, Torus, E
def amax(xv, B):
    xv -= math.floor(xv); q0, q1 = 1, 0; m = 0
    for _ in range(80):
        if xv < 1e-14 or q0 > B: break
        xv = 1 / xv; a = math.floor(xv); xv -= a; m = max(m, a); q0, q1 = a * q0 + q1, q0
    return m
rng = np.random.default_rng(7)
for trial in range(4):
    x = 2.05 + 3 * rng.random(); b = 2 * math.sqrt(x * x / (x * x - 4)) * math.cosh(rng.random() * 2)
    s = sink(x, b); X = Torus(*s)
    print("\nsurface %d: sink traces (%.4f, %.4f, %.4f), Area %.6f" % ((trial,) + s + (X.area,)), flush=True)
    for w, n in ((1e3, 80), (1e4, 60), (1e5, 40), (1e6, 24)):
        t0 = time.time(); Rs = rng.uniform(w, 2 * w, n); v = np.array([E(X, R) for R in Rs])
        cs = X.cells(2 * w); am = 0
        for lu, lw, dl in cs:
            lm = lu + lw - dl
            for xv, l in ((lw / lu, lw), ((lm - lu) / lu, lw), (lu / lw, lu), ((lm - lw) / lw, lu)): am = max(am, amax(xv, 2 * w / l))
        print("   w = %8.0f: rms %7.2f  max %7.2f  mean %+6.2f  (%d cells, largest quotient in range %d, %.0f s)" % (w, v.std(), np.abs(v).max(), v.mean(), len(cs), am, time.time() - t0), flush=True)
