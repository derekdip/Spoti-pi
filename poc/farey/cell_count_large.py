"""E_B(R) for R up to 1e6 via the exact cell decomposition; rms over windows [w, 2w]; sensitivity to the cell cutoff."""
import math, numpy as np, sys, time
sys.path.insert(0, "poc/farey")
from cell_count import E_cells
rng = np.random.default_rng(11)
print("cutoff sensitivity at R ~ 2e4:")
for R in rng.uniform(1.5e4, 2.5e4, 3):
    print("   R = %.2f: ETA=1e-3 -> %.6f, ETA=1e-7 -> %.6f" % (R, E_cells(R, 1e-3)[0], E_cells(R, 1e-7)[0]), flush=True)
print("\nwindow [w, 2w]: rms E_B, max |E_B|, cells used")
for w, n in ((1e3, 200), (3e3, 200), (1e4, 200), (3e4, 160), (1e5, 120), (3e5, 80), (1e6, 60)):
    t0 = time.time(); Rs = rng.uniform(w, 2 * w, n); vals = []; nc = 0
    for R in Rs:
        e, nc = E_cells(R); vals.append(e)
    v = np.array(vals)
    print("   w = %8.0f: rms %8.2f   max %8.2f   mean %+7.2f   (%d cells, %.0f s)" % (w, v.std(), np.abs(v).max(), v.mean(), nc, time.time() - t0), flush=True)
