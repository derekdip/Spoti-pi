"""Signed count of zero-blind hyperbolic tori = winding of Z_B(rho_k) around the boundary of the mirror triangle:
hexagonal corner x = 3 -> along the mirror edge v = 1 (y = z) to the cusp cut x = XMIN -> twist segment v: 1 -> 0 ->
along the mirror edge v = 0 (y = x, then z = xy/2) back to x = 3. No zeros beyond the cut: |Z| is large and
twist-independent there (Theorem 11 regime; checked by the minimum of |Z| on the cut)."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from zb_scan import surf
XMIN = 2.03
for k in [int(a) for a in sys.argv[1].split(",")]:
    rho = complex(mp.zetazero(k))
    xa = np.concatenate([np.linspace(3.0, 2.2, 700), np.linspace(2.2, XMIN, 300)[1:]])
    path = [(x, 1.0) for x in xa] + [(XMIN, v) for v in np.linspace(1, 0, 200)[1:]] + [(x, 0.0) for x in xa[::-1][1:]]
    Z = np.array([ZB(rho, *surf(x, v), th=math.pi / 3, smax=36)[0] for x, v in path])
    steps = np.angle(Z[1:] / Z[:-1])
    print("k = %d gamma = %.3f: boundary winding %.4f  (max phase step %.2f rad, min |Z| on path %.3f, on cusp cut %.3f)" % (
        k, rho.imag, steps.sum() / (2 * math.pi), np.abs(steps).max(), np.abs(Z).min(), np.abs(Z[999:1198]).min()), flush=True)
