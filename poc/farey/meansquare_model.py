"""Mean-square model of the lattice error of B from the Voronoi series:
   M(X; lam) = sum_gamma sum_{k <= lam X l_gamma} (cot pi k a+ - cot pi k a-)^2 / (2 pi^2 k^2),
compared with the measured rms of E_B over windows [w, 2w] (ball_lattice_big.log). Face data from closed forms."""
import math, numpy as np, sys
exec(open("poc/farey/stable_voronoi_series.py").read().split("# lattice side")[0].replace("'TMAX = 60.0'", "'TMAX = 34.0'"))
print("geodesics used: %d (l <= 34)" % len(Ls))
measured = {100: 9.62, 200: 12.51, 400: 18.38, 800: 32.91, 1600: 55.29, 3200: 83.30}
def M(X, lam, LM=34.0):
    tot = 0.0
    for a1, a2, l in zip(ap, am, Ls):
        if l > LM: continue
        K = int(lam * X * l) + 1
        k = np.arange(1, K + 1, dtype=float)
        d = (1 / np.tan(math.pi * k * a1) - 1 / np.tan(math.pi * k * a2)) / (math.pi * k)
        tot += 0.5 * np.sum(d * d)
    return tot
for lam in (0.5, 1.0, 2.0):
    row = []
    for w, rms in measured.items():
        X = 1.5 * w
        row.append((w, rms, math.sqrt(M(X, lam))))
    print("lam = %.1f: " % lam + "  ".join("w=%d: meas %.1f model %.1f" % r for r in row))
# which geodesics carry M at X = 2400, lam = 1: share by length, and the largest single contributions
X = 2400.0; contrib = []
for a1, a2, l in zip(ap, am, Ls):
    K = int(X * l) + 1; k = np.arange(1, K + 1, dtype=float)
    d = (1 / np.tan(math.pi * k * a1) - 1 / np.tan(math.pi * k * a2)) / (math.pi * k)
    contrib.append((0.5 * np.sum(d * d), l, a1, int(k[np.argmax(np.abs(d))])))
contrib.sort(reverse=True); tot = sum(c[0] for c in contrib)
print("\nX = 2400, lam = 1: total M = %.1f (rms %.1f)" % (tot, math.sqrt(tot)))
for c in contrib[:6]:
    print("   l = %6.3f  a+ = %.10f  share %.1f%%  peak at k = %d" % (c[1], c[2] % 1, 100 * c[0] / tot, c[3]))
for lo, hi in ((0, 5), (5, 10), (10, 20), (20, 34)):
    s = sum(c[0] for c in contrib if lo < c[1] <= hi); print("   l in (%2d, %2d]: %.1f%%" % (lo, hi, 100 * s / tot))
