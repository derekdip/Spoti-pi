"""Which Farey cells carry E_B at large R? Per-cell discrepancy D = 2 (S_cell - R^2 delta/(2 l_u l_w l_m)), rms over
R in [w, 2w]; rank cells, and report their two rotation numbers alpha = l_w/l_u, alpha' = (l_m - l_u)/l_u with their
continued fractions."""
import math, numpy as np, sys
sys.path.insert(0, "poc/farey")
from cell_count import cells_for, S_cell, A_root, area, l3
def cf(x, n=10):
    out = []
    for _ in range(n):
        a = math.floor(x); out.append(a); x -= a
        if x < 1e-12: break
        x = 1 / x
    return out
rng = np.random.default_rng(5)
for w in (3e3, 3e4):
    Rs = rng.uniform(w, 2 * w, 60)
    cs = cells_for(2 * w, 1e-3)
    D = np.zeros((len(cs), len(Rs))); root = np.zeros(len(Rs))
    for j, R in enumerate(Rs):
        root[j] = A_root(R) - area * R * R
        for i, (lu, lw, dl) in enumerate(cs):
            lm = lu + lw - dl
            D[i, j] = 2 * (S_cell(R, lu, lw, dl) - R * R * dl / (2 * lu * lw * lm))
    E = root + D.sum(0)
    print("\nw = %.0f: rms E %.1f; rms root part %.1f; cells %d" % (w, E.std(), root.std(), len(cs)))
    r = D.std(1); o = np.argsort(-r)
    for i in o[:8]:
        lu, lw, dl = cs[i]; lm = lu + lw - dl
        print("   cell l_u=%7.3f l_w=%7.3f delta=%.2e: rms %6.1f | alpha=l_w/l_u cf %s | alpha'=(l_m-l_u)/l_u cf %s" % (
            lu, lw, dl, r[i], cf(lw / lu), cf((lm - lu) / lu)))
    # share of variance from the top cells, coherent
    for top in (1, 3, 6, 12):
        sel = o[:top]; print("   top %2d cells + root: rms %.1f" % (top, (root + D[sel].sum(0)).std()))
