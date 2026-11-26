"""Analysis of the Chowla-Selberg survey: mean square of |Z_B| on the critical line and at zeros by band; growth exponent;
partial sums of 2 sum |c|^2 (hyperbolic modular torus) vs the flat log law."""
import numpy as np, glob
L = np.concatenate([np.load(f) for f in sorted(glob.glob("poc/farey/cs_line_*.npy"))]); L = L[np.argsort(L[:, 0])]
Zr = np.concatenate([np.load(f) for f in sorted(glob.glob("poc/farey/cs_zeros_*.npy"))]); Zr = Zr[np.argsort(Zr[:, 0])]
print("critical line: %d points, t in [%.0f, %.0f]" % (len(L), L[0, 0], L[-1, 0]))
for lo, hi in ((10, 50), (50, 100), (100, 200), (200, 400), (400, 800), (800, 1200), (1200, 1600), (1600, 2000)):
    m = (L[:, 0] >= lo) & (L[:, 0] < hi)
    if m.sum(): print("  t in [%4d,%4d): <|Z_B|^2> = %8.1f  rms %6.2f  max %7.2f  (%d pts)" % (lo, hi, np.mean(L[m, 1] ** 2), np.sqrt(np.mean(L[m, 1] ** 2)), L[m, 1].max(), m.sum()))
c = np.polyfit(np.log(L[:, 0]), np.log(L[:, 1] ** 2 + 1e-12), 1); print("  log-log fit of |Z_B|^2 vs t: exponent %.3f" % c[0])
print("zeros: %d, gamma up to %.1f" % (len(Zr), Zr[-1, 0]))
g = Zr[:, 0]
for lo, hi in ((0, 100), (100, 200), (200, 400), (400, 800), (800, 1500)):
    m = (g >= lo) & (g < hi)
    if m.sum(): print("  gamma in [%4d,%4d): <|Z_B(rho)|^2> = %8.1f   <1/|zeta'|^2> = %.4f  (%d zeros)" % (lo, hi, np.mean(Zr[m, 1] ** 2), np.mean(1 / Zr[m, 2] ** 2), m.sum()))
S = np.cumsum(2 * Zr[:, 3] ** 2)
for T in (50, 100, 200, 400, 800, 1400):
    i = np.searchsorted(g, T) - 1
    if 0 <= i < len(g): print("  2 sum_{gamma<%4d} |c|^2 = %.5f" % (T, S[i]))
