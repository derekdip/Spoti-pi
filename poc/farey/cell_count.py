"""Exact Farey-cell decomposition of the lattice count of the stable-norm ball (modular torus):
   A(R) = A_root(R) + 2 sum_cells S_cell(R),
   S_cell(R) = #{(a,b) >= 1 : a l_u + b l_w - delta min(a,b) <= R < a l_u + b l_w}  (points gained when m is inserted).
Cells are kept if delta R^2 >= ETA (expected contribution of the rest is about R^2 * area tail); validated against direct
counts, then used to compute E_B(R) = A(R) - Area R^2 far beyond direct enumeration."""
import math, numpy as np, sys
from mpmath import mp, mpf, acosh as macosh, log as mlog
mp.dps = 40
def Lm(t): return 2 * macosh(mpf(t) / 2)
area = 0.891803166008
l3 = float(Lm(3))
def cells_for(R, ETA):
    out = []; st = [(3, 3, 3), (3, 3, 3), (3, 3, 3)]
    while st:
        tu, tw, td = st.pop(); tm = tu * tw - td
        a, b, c = Lm(tu), Lm(tw), Lm(tm); dl = a + b - c
        if float(dl) * R * R < ETA and float(a + b) > 2 * math.log(R) + 6: continue
        out.append((float(a), float(b), float(dl)))
        st += [(tu, tm, tw), (tm, tw, tu)]
    return out
def T(p, q, R):    # #{alpha, beta >= 1 : alpha p + beta q <= R}
    if R < p + q: return 0
    beta = np.arange(1, int((R - p) / q) + 1); return int(np.sum(np.floor((R - beta * q) / p)))
def A_root(R):
    rays = 3 * int(R // l3)
    return 2 * (rays + 3 * T(l3, l3, R))
def S_cell(R, lu, lw, dl):
    tot = 0
    # a >= b: a in ((R - b lw)/lu, (R - b (lw - dl))/lu],  a >= b
    bmax = int(R / (lu + lw - dl)) + 1
    b = np.arange(1, bmax + 1, dtype=float)
    lo = np.maximum(np.floor((R - b * lw) / lu), b - 1); hi = np.floor((R - b * (lw - dl)) / lu)
    tot += int(np.sum(np.maximum(hi - lo, 0)))
    # a < b: b in ((R - a lu)/lw, (R - a (lu - dl))/lw],  b > a
    amax = int(R / (lu + lw - dl)) + 1
    a = np.arange(1, amax + 1, dtype=float)
    lo = np.maximum(np.floor((R - a * lu) / lw), a); hi = np.floor((R - a * (lu - dl)) / lw)
    tot += int(np.sum(np.maximum(hi - lo, 0)))
    return tot
def E_cells(R, ETA=1e-3):
    cs = cells_for(R, ETA)
    return A_root(R) + 2 * sum(S_cell(R, *c) for c in cs) - area * R * R, len(cs)
if __name__ == "__main__":
    # validation against direct enumeration
    def Lf(tr): return 2 * math.acosh(tr / 2) if tr < 10**300 else 2 * math.log(tr)
    out = [Lf(3)] * 3; st = [(3, 3, 3)] * 3
    while st:
        tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lf(tm)
        if lm > 1200: continue
        out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
    Ns = np.sort(np.array(out))
    mult = np.sort(np.concatenate([Ns[:np.searchsorted(Ns, 1200 / k, side='right')] * k for k in range(1, int(1200 / l3) + 1)]))
    rng = np.random.default_rng(4)
    print("validation (direct lattice count vs cell decomposition):")
    for R in sorted(rng.uniform(50, 1100, 8)):
        d = 2 * np.searchsorted(mult, R, side="right") - area * R * R
        e, nc = E_cells(R)
        print("   R = %8.3f: direct E = %9.4f   cells E = %9.4f   (%d cells)" % (R, d, e, nc))
