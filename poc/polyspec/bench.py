"""Speed and accuracy. Polygon: a heptagon with rational vertices (denominator 7) filling ~60% of an N x N raster.
  brute  : lattice mask built once, then each coefficient as w^T M z (O(N^2) per coefficient)
  FFT    : numpy fft2 of the mask (all N^2 coefficients at once), cost per coefficient = total / N^2
  monoid : polygon_dft, O(edges log N) per coefficient, no raster
Accuracy at large N: float result vs the same algorithm in mpmath at 60 digits, error relative to the area."""
import math, time, random, cmath, numpy as np
from fractions import Fraction as Fr
import mpmath as mp
import polyspec
from polyspec import polygon_dft
def heptagon(N):
    c = N / 2; r = 0.45 * N
    return [(Fr(round(7 * (c + r * math.cos(2 * math.pi * j / 7 + 0.3))), 7), Fr(round(7 * (c + r * math.sin(2 * math.pi * j / 7 + 0.3))), 7)) for j in range(7)]
def mask(V, N):
    y, x = np.mgrid[0:N, 0:N]; M = np.ones((N, N), bool)
    for i in range(len(V)):
        (x1, y1), (x2, y2) = V[i], V[(i + 1) % len(V)]
        # exact integer test: 49 * cross >= 0 with numerators over 7
        X1, Y1, X2, Y2 = (int(v * 7) for v in (x1, y1, x2, y2))
        M &= (X2 - X1) * (7 * y - Y1) - (Y2 - Y1) * (7 * x - X1) >= 0
    return M
# huge rasters: only the monoid method is possible; accuracy vs 60-digit mpmath run of the same algorithm
mp.mp.dps = 60
def run_mp(V, kx, ky, N):
    saved = (cmath.exp, math.pi)
    class C:   # minimal shim: polygon_dft uses cmath.exp and math.pi
        pass
    polyspec.cmath = type("m", (), {"exp": staticmethod(lambda z: mp.exp(mp.mpc(z.real, z.imag) if isinstance(z, complex) else z))})
    polyspec.math = type("m", (), {"pi": mp.pi, "ceil": math.ceil, "floor": math.floor, "gcd": math.gcd})
    try: return polygon_dft(V, kx, ky, N)
    finally: polyspec.cmath = cmath; polyspec.math = math
def main():
    rng = random.Random(1)
    print("%7s %10s | %12s %12s %12s | %s" % ("N", "points", "brute/coef", "FFT/coef", "monoid/coef", "max |monoid - brute| / area"))
    for N in (256, 1024, 4096, 8192):
        V = heptagon(N); M = mask(V, N); area = int(M.sum())
        ks = [(rng.randrange(N), rng.randrange(N)) for _ in range(20)]
        t0 = time.perf_counter(); Mf = M.astype(np.float64)
        bf = []
        for kx, ky in ks:
            wx = np.exp(-2j * np.pi * kx * np.arange(N) / N); zy = np.exp(-2j * np.pi * ky * np.arange(N) / N)
            bf.append(zy @ Mf @ wx)                       # rows are y, columns are x
        tb = (time.perf_counter() - t0) / len(ks)
        t0 = time.perf_counter(); F = np.fft.fft2(Mf); tf = (time.perf_counter() - t0) / (N * N)
        t0 = time.perf_counter(); mo = [polygon_dft(V, kx, ky, N) for kx, ky in ks]; tm = (time.perf_counter() - t0) / len(ks)
        err = max(abs(a - b) for a, b in zip(mo, bf)) / area
        errF = max(abs(F[ky, kx] - b) for (kx, ky), b in zip(ks, bf)) / area
        print("%7d %10d | %9.1f us %9.4f us %9.1f us | %.1e   (FFT vs brute %.1e)" % (N, area, tb * 1e6, tf * 1e6, tm * 1e6, err, errF), flush=True)
    print("\nhuge rasters (no raster stored):")
    for e in (5, 6, 7, 9, 12, 15):
        N = 10 ** e; V = heptagon(N); area = 0.5 * abs(sum(float(V[i][0] * V[(i+1) % 7][1] - V[(i+1) % 7][0] * V[i][1]) for i in range(7)))
        ks = [(rng.randrange(1, 50), rng.randrange(1, 50)) for _ in range(4)] + [(rng.randrange(N), rng.randrange(N)) for _ in range(4)]
        t0 = time.perf_counter(); fl = [polygon_dft(V, kx, ky, N) for kx, ky in ks]; tm = (time.perf_counter() - t0) / len(ks)
        ex = [run_mp(V, kx, ky, N) for kx, ky in ks]
        err = max(abs(complex(a) - complex(b)) for a, b in zip(fl, ex)) / area
        mag = max(abs(complex(b)) for b in ex[:4]) / area
        print("  N = 1e%-2d  ~%.1e lattice points  %7.1f us/coef  float64 error / area %.1e   (|F|/area at low k ~ %.1e)" % (e, area, tm * 1e6, err, mag), flush=True)
if __name__ == "__main__": main()
