"""Per-cell discrepancies with the root hexagon grouped with its three rational cells (l_u = l_w = l3).
For each other cell: rms of D over [w, 2w], and the largest partial quotient of alpha = l_w/l_u, alpha' = (l_m - l_u)/l_u
among convergents with denominator q <= R/l (the ones active at scale R)."""
import math, numpy as np, sys
sys.path.insert(0, "poc/farey")
from cell_count import cells_for, S_cell, A_root, area, l3
def cfq(x, qmax):
    a0 = math.floor(x); x -= a0; qs = [1, 0]; best = 0; trail = []
    for _ in range(60):
        if x < 1e-13: break
        x = 1 / x; a = math.floor(x); x -= a
        q = a * qs[0] + qs[1]
        if qs[0] > qmax: break
        best = max(best, a); trail.append(a); qs = [q, qs[0]]
    return best, trail[:12]
rng = np.random.default_rng(5)
for w in (3e3, 3e4):
    Rs = rng.uniform(w, 2 * w, 60); cs = cells_for(2 * w, 1e-3)
    Dg = np.zeros(len(Rs)); D = np.zeros((len(cs), len(Rs))); isroot = np.array([abs(c[0] - l3) < 1e-9 and abs(c[1] - l3) < 1e-9 for c in cs])
    for j, R in enumerate(Rs):
        for i, (lu, lw, dl) in enumerate(cs):
            lm = lu + lw - dl; D[i, j] = 2 * (S_cell(R, lu, lw, dl) - R * R * dl / (2 * lu * lw * lm))
        Dg[j] = A_root(R) - area * R * R + D[isroot, j].sum() + sum(R * R * cs[i][2] / (cs[i][0] * cs[i][1] * (cs[i][0] + cs[i][1] - cs[i][2])) for i in range(len(cs)) if not isroot[i])
    # Dg = root hexagon + its 3 rational cells, with the non-root cells' area restored so that E = Dg + sum non-root D
    E = Dg + D[~isroot].sum(0)
    print("\nw = %.0f: rms E %.1f; rms(root hexagon + 3 rational cells) %.1f; non-root cells %d" % (w, E.std(), Dg.std(), (~isroot).sum()))
    r = D.std(1); r[isroot] = -1; o = np.argsort(-r)
    big = []
    for i in o[:10]:
        lu, lw, dl = cs[i]; lm = lu + lw - dl; R = 2 * w
        b1, t1 = cfq(lw / lu, R / lw); b2, t2 = cfq((lm - lu) / lu, R / lw)
        print("   l_u=%7.3f l_w=%7.3f delta=%.1e rms %6.1f | max quotient in range: alpha %4d %s, alpha' %4d %s" % (lu, lw, dl, r[i], b1, t1, b2, t2))
    for thr in (50, 100, 200):
        sel = [i for i in range(len(cs)) if not isroot[i] and max(cfq(cs[i][1] / cs[i][0], 2 * w / cs[i][1])[0], cfq((cs[i][1] - cs[i][2]) / cs[i][0], 2 * w / cs[i][1])[0]) >= thr]
        rest = [i for i in range(len(cs)) if not isroot[i] and i not in sel]
        print("   cells with a quotient >= %3d in range: %3d; rms of their sum %.1f; rms of all other cells + root %.1f" % (thr, len(sel), D[sel].sum(0).std() if sel else 0, (Dg + D[rest].sum(0)).std()))
