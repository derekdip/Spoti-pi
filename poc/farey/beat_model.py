"""Beat-packet model of the lattice error: cluster Voronoi terms with near-equal frequency (gap < GAP), and model
   mean_{R in [w,2w]} E_B(R)^2  ~  sum_clusters mean_R |sum_j A_j e^{2 pi i f_j R}|^2 / 2,
with all terms of geodesics l <= 40 and frequencies <= F. Compared with measured rms (ball_lattice_big.log)."""
import math, numpy as np
exec(open("poc/farey/stable_voronoi_series.py").read().split("# lattice side")[0].replace("'TMAX = 60.0'", "'TMAX = 40.0'"))
measured = {100: 9.62, 200: 12.51, 400: 18.38, 800: 32.91, 1600: 55.29, 3200: 83.30}
def terms(F):
    fs, As = [], []
    for a1, a2, l in zip(ap, am, Ls):
        k = np.arange(1, int(F * l) + 1, dtype=float)
        fs.append(k / l); As.append((1 / np.tan(math.pi * k * a1) - 1 / np.tan(math.pi * k * a2)) / (math.pi * k))
    f = np.concatenate(fs); A = np.concatenate(As); o = np.argsort(f); return f[o], A[o]
def model(f, A, w, gap):
    cut = np.where(np.diff(f) > gap)[0] + 1
    Rs = np.linspace(w, 2 * w, 64)
    tot = 0.0
    for idx in np.split(np.arange(len(f)), cut):
        if len(idx) == 1: tot += 0.5 * A[idx[0]] ** 2; continue
        P = np.exp(2j * math.pi * np.outer(Rs, f[idx])) @ A[idx]
        tot += 0.5 * np.mean(np.abs(P) ** 2)
    return math.sqrt(tot)
for F in (3.0, 6.0):
    f, A = terms(F)
    for gap in (1e-3, 1e-4):
        print("F = %.0f, gap = %.0e (%d terms): " % (F, gap, len(f)) + "  ".join("w=%d: meas %.1f model %.1f" % (w, r, model(f, A, w, gap)) for w, r in measured.items()), flush=True)

# convergence in F, and the packets that carry the growth
for F in (9.0, 12.0):
    f, A = terms(F)
    print("F = %.0f, gap = 1e-03 (%d terms): " % (F, len(f)) + "  ".join("w=%d: meas %.1f model %.1f" % (w, r, model(f, A, w, 1e-3)) for w, r in measured.items()), flush=True)
f, A = terms(6.0); cut = np.where(np.diff(f) > 1e-3)[0] + 1
rows = []
for idx in np.split(np.arange(len(f)), cut):
    if len(idx) < 2: continue
    vals = []
    for w in (100, 3200):
        Rs = np.linspace(w, 2 * w, 64); P = np.exp(2j * math.pi * np.outer(Rs, f[idx])) @ A[idx]; vals.append(0.5 * np.mean(np.abs(P) ** 2))
    rows.append((vals[1] - vals[0], f[idx].mean(), len(idx), np.abs(A[idx]).max(), A[idx].sum(), f[idx].max() - f[idx].min(), vals))
rows.sort(reverse=True)
print("packets with the largest growth of mean square from w=100 to w=3200 (F = 6):")
for r in rows[:8]:
    print("   freq %.6f: %3d terms, max |A| %.1f, net sum %+.3f, freq spread %.2e, mean square %.1f -> %.1f" % (r[1], r[2], r[3], r[4], r[5], r[6][0], r[6][1]))
