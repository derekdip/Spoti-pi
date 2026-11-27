# polyspec: exact DFT coefficients of a rasterised polygon in O(edges log N)

`polygon_dft(verts, kx, ky, N)` returns sum over the integer points of a closed convex polygon (rational vertices) of
e^{-2 pi i (kx x + ky y)/N}. This is the spectrum of the polygon *as rasterised by point sampling*, aliasing
included, and it never builds the raster.

**How.** Split the polygon into integer columns. The column sums are geometric series, so everything reduces to
sum_t w^t z^{floor((a t + b)/c)} along each edge. That is a product over the edge's Christoffel word in a
3-component monoid (U = (1, z, 0), R = (w, 1, 1), (al, be, ga)(al', be', ga') = (al al', be be', ga + al be ga')).
The universal Euclidean algorithm (the recursion behind `floor_sum`) evaluates it in O(log) monoid products. The
ky = 0 row needs sum w^t floor(...), which uses a 4-component monoid.

| file | what |
|---|---|
| `polyspec.py` | `ueuclid`, `G_exp`, `G_lin`, `polygon_dft` |
| `test_polyspec.py` | word construction (2000 cases), weighted floor sums vs direct (2000), polygon DFT vs brute-force lattice enumeration (840 coefficients on 60 random rational convex polygons, max error 9e-11): all pass |
| `bench.py` -> `bench.log`, `precision.py` -> `precision.log` | speed vs brute force and FFT; float64 accuracy at huge N |

## Results (pure Python for the monoid; numpy for brute force and FFT)

| N | lattice points | brute force / coef | FFT / coef (amortised over all N^2) | monoid / coef |
|---|---|---|---|---|
| 256 | 3.6e4 | 0.20 ms | 0.05 us | 0.29 ms |
| 1024 | 5.8e5 | 1.9 ms | 0.03 us | 0.18 ms |
| 4096 | 9.3e6 | 76 ms | 0.05 us | 0.21 ms |
| 8192 | 3.7e7 | 323 ms | 0.05 us | 0.22 ms |
| 1e9 | 5.5e17 | impossible | impossible | 0.47 ms |
| 1e15 | 5.5e29 | impossible | impossible | 0.78 ms |

The float64 relative error per coefficient grows roughly like N times machine epsilon:

| N | relative error |
|---|---|
| 1e3 | 1e-13 |
| 1e6 | 1e-9 |
| 1e9 | 1e-7 to 1e-6 |
| 1e12 | 1e-4 |

The cause is w = e^{-2 pi i k/N} near 1 and the division by (z - 1). For N beyond about 1e9, use higher precision:
the same code runs unchanged on mpmath.

## Verdict (honest)

- **If you want the whole spectrum of a raster that fits in memory, use the FFT.** It is about 4000x cheaper per
  coefficient.
- **The monoid wins for a few coefficients:** it is faster than brute force from N of about 1000, and 1500x faster at
  N = 8192, with cost independent of N. It also wins for rasters too large to exist, such as an exact aliasing
  spectrum of a polygon at 1e9 x 1e9 resolution or the Fourier analysis of a CAD outline at nanometre pitch.
- **It is exact up to rounding,** so it can certify rasteriser coverage and aliasing.
- It is niche. Plausible users are exact aliasing analysis of vector shapes (this is the 2D-shape version of the
  moire model), structure factors of polygonal 2D crystal grains, lattice-point exponential sums in number theory,
  and test oracles for rasterisers.
- The convention includes boundary points (a closed polygon). A top-left fill rule needs the half-open variant, which
  is a one-line change per edge.
