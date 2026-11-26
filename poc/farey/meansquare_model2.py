"""Mean-square model with coherent grouping: geodesics of equal length share frequencies k/l, so amplitudes are summed
per (l, k) before squaring:  M(X) = sum_{l} sum_{k <= lam X l} |sum_{gamma: l_gamma = l} amp_gamma(k)|^2 / 2."""
import math, numpy as np
from collections import defaultdict
exec(open("poc/farey/stable_voronoi_series.py").read().split("# lattice side")[0].replace("'TMAX = 60.0'", "'TMAX = 34.0'"))
groups = defaultdict(list)
for a1, a2, l in zip(ap, am, Ls): groups[round(l, 9)].append((a1, a2))
print("geodesics: %d, distinct lengths: %d, multiplicities: %s" % (len(Ls), len(groups), sorted(set(len(v) for v in groups.values()))))
measured = {100: 9.62, 200: 12.51, 400: 18.38, 800: 32.91, 1600: 55.29, 3200: 83.30}
def M(X, lam, detail=False):
    tot = 0.0; per = []
    for l, faces in groups.items():
        K = int(lam * X * l) + 1; k = np.arange(1, K + 1, dtype=float)
        amp = sum((1 / np.tan(math.pi * k * a1) - 1 / np.tan(math.pi * k * a2)) / (math.pi * k) for a1, a2 in faces)
        c = 0.5 * np.sum(amp * amp); tot += c
        if detail: per.append((c, l, len(faces)))
    return (tot, per) if detail else tot
for lam in (0.25, 0.5, 1.0, 2.0):
    print("lam = %.2f: " % lam + "  ".join("w=%d: meas %.1f model %.1f" % (w, r, math.sqrt(M(1.5 * w, lam))) for w, r in measured.items()))
tot, per = M(3600, 1.0, True); per.sort(reverse=True)
print("X = 3600: rms %.1f; top lengths: %s" % (math.sqrt(tot), "  ".join("l=%.3f(x%d) %.0f%%" % (p[1], p[2], 100 * p[0] / tot) for p in per[:5])))
