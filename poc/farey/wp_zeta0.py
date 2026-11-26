"""Direct Weil-Petersson check of <Z_B(0)> = 0, i.e. <(1/3) sum_gamma g_gamma / l_gamma> = 1, over M_{1,1}(L).
Same Fenchel-Nielsen fundamental domain and quadrature as wp_average.py (which reproduced Vol = (L^2 + 4 pi^2)/24).
Here g = gap law (log((t^2 - mu)/(t^2 - 4))), l = 2 N(t) (limits.N is the l/2 normalisation)."""
import math, sys, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import wp_average as W
from limits import curves, g as gap, N as Nf
def F(a, b, mu):
    cv, _ = curves(a, b, mu, tol=1e-13)
    return sum(gap(t, mu) / (2 * Nf(t)) for t in cv.values()) / 3.0
W.Astar = F
for L in (0.0, 2.0, 5.0):
    for nl, nt in ((48, 20), (72, 28)):
        vol, I, lmax = W.integrate(L, nl, nt)
        print("L = %.1f (nodes %d x %d): Vol = %.6f (predicted %.6f);  int (1 + Z_B(0)) = %.6f;  average = %.5f  (predicted 1, i.e. <Z_B(0)> = 0)"
              % (L, nl, nt, vol, (L * L + 4 * math.pi ** 2) / 24, I, I / vol), flush=True)
