"""Simple-geodesic count on the modular torus at large R: P(R) = #{gamma simple, l <= R} (mod sign)
 = (1/2) sum_d mu(d) A(R/d), A = full lattice count (both signs, x != 0). A(t) for t < T0 by direct enumeration,
for t >= T0 by the exact Farey-cell decomposition. Error P - (3/pi^2) Area R^2, compared with sqrt(R) and with the
first-zero prediction |Z_B(rho_1)| / (|rho_1| |zeta'(rho_1)|) = 0.535 (amplitude of the R^(1/2) cos term)."""
import math, numpy as np, sys, time
sys.path.insert(0, "poc/farey")
from cell_count import E_cells, area, l3
import mpmath as mp
T0 = 3000.0
def Lf(tr): return 2 * math.acosh(tr / 2) if tr < 10**300 else 2 * math.log(tr)
out = [Lf(3)] * 3; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lf(tm)
    if lm > T0: continue
    out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
Ns = np.sort(np.array(out)); del out
mult = np.sort(np.concatenate([Ns[:np.searchsorted(Ns, T0 / k, side='right')] * k for k in range(1, int(T0 / l3) + 1)]))
print("direct table: %d primitive (mod sign) up to %g, %d lattice points (one sign)" % (len(Ns), T0, len(mult)), flush=True)
DMAX = int(2.1e6 / l3) + 2
mu = np.ones(DMAX + 1, dtype=np.int8); mu[0] = 0; isp = np.ones(DMAX + 1, bool); isp[:2] = False
for p in range(2, DMAX + 1):
    if isp[p]:
        isp[2 * p::p] = False; mu[p::p] *= -1; mu[p * p::p * p] = 0
def A(t):
    return 2 * np.searchsorted(mult, t, side="right") if t < T0 else E_cells(t)[0] + area * t * t
def P(R):
    d = np.arange(1, int(R / l3) + 1); small = R / d < T0
    tot = np.sum(mu[d[small]] * 2 * np.searchsorted(mult, R / d[small], side="right"))
    for dd in d[~small]:
        if mu[dd]: tot += mu[dd] * A(R / dd)
    return tot / 2
# check against direct primitive count for R < T0
for R in (500.0, 1500.0, 2900.0):
    print("check R = %g: Moebius %.1f, direct %d" % (R, P(R), np.searchsorted(Ns, R, side="right")), flush=True)
r1 = mp.zetazero(1); pred = 6.0 / (abs(r1) * abs(mp.zeta(r1, derivative=1)))
print("first-zero amplitude prediction: %.4f (with |Z_B(rho_1)| = 6.0)" % pred)
rng = np.random.default_rng(21)
for w, n in ((1e4, 40), (1e5, 24), (1e6, 12)):
    t0 = time.time(); Rs = rng.uniform(w, 2 * w, n)
    e = np.array([P(R) - 3 / math.pi ** 2 * area * R * R for R in Rs])
    print("w = %8.0f: rms(P error) %8.1f  rms(error/sqrt R) %.3f  max|error|/sqrt R %.3f  mean error/sqrt R %+.3f  (%.0f s)" % (
        w, e.std(), (e / np.sqrt(Rs)).std(), np.abs(e / np.sqrt(Rs)).max(), np.mean(e / np.sqrt(Rs)), time.time() - t0), flush=True)
