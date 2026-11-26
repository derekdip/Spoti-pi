"""Find near-coincident frequencies k/l among resonant Voronoi terms: for the largest single-frequency amplitudes,
list the other terms within df of the same frequency and the summed amplitude."""
import math, numpy as np
from collections import defaultdict
exec(open("poc/farey/stable_voronoi_series.py").read().split("# lattice side")[0].replace("'TMAX = 60.0'", "'TMAX = 40.0'"))
terms = []   # (freq, amp, l, k)
for a1, a2, l in zip(ap, am, Ls):
    k = np.arange(1, int(12 * l) + 1, dtype=float)
    amp = (1 / np.tan(math.pi * k * a1) - 1 / np.tan(math.pi * k * a2)) / (math.pi * k)
    big = np.abs(amp) > 0.5
    for kk, A in zip(k[big], amp[big]): terms.append((kk / l, A, l, int(kk)))
terms.sort()
f = np.array([t[0] for t in terms]); A = np.array([t[1] for t in terms])
print("terms with |amp| > 0.5 and frequency <= 12: %d" % len(terms))
order = np.argsort(-np.abs(A))
seen = set()
for i in order[:12]:
    if i in seen: continue
    near = np.where(np.abs(f - f[i]) < 2e-3)[0]
    seen.update(near.tolist())
    print("freq %.9f: %d terms within 2e-3, amplitudes %s ; sum %.4f ; spread of freqs %.2e" % (
        f[i], len(near), " ".join("%+.2f(l=%.3f,k=%d)" % (A[j], terms[j][2], terms[j][3]) for j in near[:8]), A[near].sum(), f[near].max() - f[near].min()))
