"""Hyperbolic (modular torus) amplitude growth vs the flat law: |Z_B(rho_k)|, k = 1..60 (k <= 20 from
zeros_angle_0p785.npy, k = 21..60 parsed from zeros_hi_*.log; all theta = pi/4 with dps 30 + (pi/4) gamma/ln10 + 10)."""
import re, glob, numpy as np, mpmath as mp
ref = np.load("poc/farey/zeros_angle_0p785.npy")
rows = [(r[0].imag, abs(r[2]), abs(r[1])) for r in ref]
for fn in sorted(glob.glob("poc/farey/zeros_hi_*.log")):
    for line in open(fn):
        m = re.match(r"k = +(\d+): gamma = +([\d.]+).*Z_B\(rho\) = \(([-\d.e+]+) ([+-]) ([\d.e+-]+)j\)\s+\|c_k\| = ([\d.]+)", line)
        if m:
            zr, sg, zi = float(m.group(3)), m.group(4), float(m.group(5)); zi = zi if sg == "+" else -zi
            rows.append((float(m.group(2)), abs(complex(zr, zi)), float(m.group(6))))
r = np.array(sorted(rows)); r = r[:34]; g = r[:, 0]   # k <= 34: the 40-term Bernoulli series is unreliable beyond gamma ~ 105
print("modular torus: %d zeros, gamma up to %.1f" % (len(r), g[-1]))
for lo, hi in ((0, 40), (40, 70), (70, 105)):
    m = (g >= lo) & (g < hi)
    print("  gamma in [%3d,%3d): <|Z_B|^2> = %7.1f   <|Z_B|^2>/gamma = %.3f   (%d zeros)" % (lo, hi, np.mean(r[m, 1] ** 2), np.mean(r[m, 1] ** 2 / g[m]), m.sum()))
c = np.polyfit(np.log(g), np.log(r[:, 1] ** 2), 1); print("  log-log fit |Z_B|^2 ~ gamma^%.2f" % c[0])
S = np.cumsum(2 * r[:, 2] ** 2)
for T in (40, 70, 103):
    i = np.searchsorted(g, T) - 1; print("  2 sum_{gamma<%d} |c|^2 = %.4f" % (T, S[i]))
fl = np.load("poc/farey/flat_amplitudes.npy"); gf = fl[:, 0]
for T in (40, 70, 103):
    i = np.searchsorted(gf, T) - 1; print("  flat hexagonal for comparison: 2 sum_{gamma<%d} |c|^2 = %.4f" % (T, np.cumsum(2 * fl[:, 4] ** 2)[i]))
