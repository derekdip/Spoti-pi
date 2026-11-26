"""Lattice-point error of the stable-norm ball B (modular torus) at larger R: iterative enumeration, N only."""
import math, sys, numpy as np
RMAX = float(sys.argv[1])
def L(t): return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)
l3 = L(3); out = [l3, l3, l3]
stack = [(3, 3, 3, l3, l3), (3, 3, 3, l3, l3), (3, 3, 3, l3, l3)]   # (tu, tw, td): three root cones
while stack:
    tu, tw, td, lu, lw = stack.pop()
    tm = tu * tw - td; lm = L(tm)
    if lm > RMAX: continue
    out.append(lm)
    stack.append((tu, tm, tw, lu, lm)); stack.append((tm, tw, tu, lm, lw))
Ns = np.sort(np.array(out)); del out
area = 0.8918031660
mult = np.sort(np.concatenate([Ns[:np.searchsorted(Ns, RMAX / k, side='right')] * k for k in range(1, int(RMAX / l3) + 1)]))
print("primitive classes mod sign with N <= %g: %d; lattice points/2: %d" % (RMAX, len(Ns), len(mult)))
count = lambda R: 2 * np.searchsorted(mult, R, side="right")
def count_disk(R):
    r = R * math.sqrt(area / math.pi); x = np.arange(-int(r), int(r) + 1)
    return int(np.sum(2 * np.floor(np.sqrt(np.maximum(r * r - x * x, 0))) + 1)) - 1
for seed in (5, 6):
    rng = np.random.default_rng(seed)
    print("seed %d:  window   rms E_B    rms E_disk   mean E_B" % seed)
    rb = []; rd = []; W = [w for w in (100, 200, 400, 800, 1600, 3200) if 2 * w <= RMAX]
    for w in W:
        Rs = rng.uniform(w, 2 * w, 3000)
        eb = count(Rs) - area * Rs ** 2
        ed = np.array([count_disk(R) for R in Rs[:600]]) - area * Rs[:600] ** 2
        rb.append(np.sqrt(np.mean(eb ** 2))); rd.append(np.sqrt(np.mean(ed ** 2)))
        print("        %5d   %8.2f   %8.2f   %8.2f" % (w, rb[-1], rd[-1], eb.mean()))
    print("   local exponents B:   ", " ".join("%.2f" % (math.log(rb[i + 1] / rb[i]) / math.log(2)) for i in range(len(W) - 1)))
    print("   local exponents disk:", " ".join("%.2f" % (math.log(rd[i + 1] / rd[i]) / math.log(2)) for i in range(len(W) - 1)))
# structure: does E_B correlate with the phase of R modulo the systole N0 = 2 log(phi^2)?
rng = np.random.default_rng(9); w = 2000 if RMAX >= 4000 else 800
Rs = rng.uniform(w, 2 * w, 20000); eb = (count(Rs) - area * Rs ** 2) / Rs ** 0.5
for name, per in (("systole N0", l3), ("N(2e0+e1)", L(6)), ("random 1.7", 1.7)):
    ph = 2 * np.pi * Rs / per
    c1 = abs(np.mean(eb * np.exp(1j * ph))); c2 = abs(np.mean(eb * np.exp(2j * ph)))
    print("E_B/R^(1/2) Fourier coefficient at period %-11s: |c1| = %.3f, |c2| = %.3f  (rms of E_B/R^(1/2) = %.3f)" % (name, c1, c2, np.sqrt(np.mean(eb ** 2))))
