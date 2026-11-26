"""Does the twist-averaged Riesz count carry the Riemann zeros?  Fit
    F(R) = cubic(R) + R^(3/2) sum_k [A_k cos(g_k log R) + B_k sin(g_k log R)]
with g_k the zeta zeros, against the same fit with fake frequencies, and against the single-surface count."""
import math, numpy as np, mpmath as mp, sys
sys.setrecursionlimit(100000)
Rs, F = np.load("poc/farey/twist_average.npy")
m = Rs >= 20; Rs, F = Rs[m], F[m]
gam = [float(mp.zetazero(k).imag) for k in range(1, 7)]
def fit(Rv, Fv, freqs, deg=3):
    cols = [Rv ** j for j in range(deg + 1)]
    for g in freqs:
        cols += [Rv ** 1.5 * np.cos(g * np.log(Rv)), Rv ** 1.5 * np.sin(g * np.log(Rv))]
    X = np.array(cols).T; sc = np.abs(X).max(0); c, *_ = np.linalg.lstsq(X / sc, Fv, rcond=None)
    res = Fv - (X / sc) @ c; c = c / sc
    return res, c
def report(name, Rv, Fv):
    r0, _ = fit(Rv, Fv, [])
    print("\n%s: rms residual after cubic only: %.4f;  residual/R^1.5 rms %.2e" % (name, r0.std(), (r0 / Rv ** 1.5).std()))
    for lab, fr in (("zeta zeros g1..g3", gam[:3]), ("zeta zeros g1..g6", gam), ("fake  x0.83", [g * 0.83 for g in gam[:3]]),
                    ("fake  x1.21", [g * 1.21 for g in gam[:3]]), ("fake  10,17,23", [10.0, 17.0, 23.0])):
        r, c = fit(Rv, Fv, fr)
        amps = [math.hypot(c[4 + 2 * i], c[5 + 2 * i]) for i in range(len(fr))]
        print("   + %-20s rms residual %.4f (%.1f%% of cubic-only); amplitudes %s" % (lab, r.std(), 100 * r.std() / r0.std(), " ".join("%.2e" % x for x in amps)))
    # scan a single frequency
    gs = np.linspace(5, 40, 701); red = []
    for g in gs:
        r, _ = fit(Rv, Fv, [g]); red.append(r.std())
    red = np.array(red); order = np.argsort(red)
    peaks = []
    for i in order:
        if all(abs(gs[i] - p) > 1.5 for p in peaks): peaks.append(gs[i])
        if len(peaks) == 4: break
    print("   single-frequency scan: best frequencies %s  (zeta zeros %s)" % (" ".join("%.2f" % p for p in peaks), " ".join("%.2f" % g for g in gam[:4])))
report("twist-averaged count <sum (R - l)_+>_tau", Rs, F)

# single surface: the modular torus itself, Riesz count sum_gamma (R - l)_+ over simple geodesics
def Lt(t): return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)
RMAX = Rs.max(); l3 = Lt(3); out = [l3, l3, l3]; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lt(tm)
    if lm > RMAX: continue
    out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
ls = np.sort(out); cs = np.concatenate([[0], np.cumsum(ls)]); n = np.searchsorted(ls, Rs)
report("single modular torus sum (R - l)_+", Rs, n * Rs - cs[n])
