"""Does the Voronoi series stay exact as the smoothing width sigma shrinks? Compare with the smoothed lattice error at
sigma = 0.3, 0.15, 0.08, 0.05, and track how the series depends on the geodesic cutoff (l <= LM)."""
import math, numpy as np
from scipy.special import ndtr
exec(open("poc/farey/stable_voronoi_series.py").read().split("# lattice side")[0].replace("'TMAX = 60.0'", "'TMAX = 130.0'"))
area = 0.891803166008
lens = np.concatenate([Ls * k for k in range(1, 200)]); lens = lens[lens < 125]
Rs = np.linspace(30, 90, 121)
def lat(R, s): return 2 * np.sum(ndtr((R - lens) / s)) - area * (R * R + s * s)
def ser(R, s, LM, KMAX=4000):
    mm = Ls <= LM; k = np.arange(1, KMAX + 1)[:, None]
    amp = (1 / np.tan(math.pi * k * ap[mm]) - 1 / np.tan(math.pi * k * am[mm])) / (math.pi * k)
    return np.sum(amp * np.exp(-2 * math.pi ** 2 * s * s * k * k / Ls[mm] ** 2) * np.cos(2 * math.pi * k * R / Ls[mm]))
for s in (0.3, 0.15, 0.08, 0.05):
    L0 = np.array([lat(R, s) for R in Rs])
    out = []
    for LM in (20, 40, 80, 130):
        S0 = np.array([ser(R, s, LM) for R in Rs]); C = np.mean(L0 - S0)
        out.append("l<=%d: mismatch %.2e (series rms %.2f)" % (LM, (L0 - S0 - C).std(), S0.std()))
    print("sigma = %.2f: lattice rms %.3f | %s" % (s, L0.std(), " | ".join(out)), flush=True)
