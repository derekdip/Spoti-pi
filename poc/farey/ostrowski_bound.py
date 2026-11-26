"""Ostrowski-type bound for E_B from the Farey-cell decomposition, compared with the measured max |E_B|.
 Each relevant cell (delta R^2 >= ETA or a+b <= 2 log R + 6) contributes 2 * sum over its four rotation numbers
 (l_w/l_u, (l_m-l_u)/l_u, l_u/l_w, (l_m-l_w)/l_w) of (1/2) sum_{q_k <= R/l} (a_{k+1} + 1); plus the root group's
 rational O(1)-per-ray part (counted as 6 + 2 per root cell). Also reports the largest partial quotient in range."""
import math, numpy as np, sys
sys.path.insert(0, "poc/farey")
from cell_count import cells_for
def ost(x, B):
    x = x - math.floor(x); q0, q1 = 1, 0; tot = 0.0; amax = 0
    for _ in range(80):
        if x < 1e-14 or q0 > B: break
        x = 1 / x; a = math.floor(x); x -= a
        tot += 0.5 * (a + 1); amax = max(amax, a); q0, q1 = a * q0 + q1, q0
    return tot, amax
measured = {1e3: 99, 3e3: 211, 1e4: 482, 3e4: 841, 1e5: 598, 3e5: 839, 1e6: 758}
for R, mx in measured.items():
    R2 = 2 * R; cs = cells_for(R2, 1e-3); tot = 0.0; amax = 0; nrel = 0
    for lu, lw, dl in cs:
        lm = lu + lw - dl
        if abs(lu - lw) < 1e-12: tot += 2; continue          # root-type rational cells: bounded by the ray terms
        nrel += 1
        for x, l in ((lw / lu, lw), ((lm - lu) / lu, lw), (lu / lw, lu), ((lm - lw) / lw, lu)):
            o, a = ost(x, R2 / l); tot += 2 * o; amax = max(amax, a)
    print("window up to R = %8.0f: measured max|E_B| %4d | Ostrowski-type bound %9.0f | relevant cells %3d | largest quotient in range %d" % (R2, mx, tot + 6, nrel, amax))
