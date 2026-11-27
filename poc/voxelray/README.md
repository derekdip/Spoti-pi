# Exact voxel ray traversal with O(log) random access

The 3D analogue of Christoffel digital lines (`poc/christoffel`). Ray P(t) = O + t D, rational origin O = o/S, integer
direction D. Per axis, the plane crossings are the arithmetic progression t_j = (j - f)/|d|, and the number of crossings
up to time t is floor(|d| t + f). That is a 3D floor-sum count; its projection to each coordinate plane is a 2D digital
line. All arithmetic is integer.

| Piece | Result |
|---|---|
| `Ray.traverse` (exact DDA; tie policy `face`: 6-connected, tied axes stepped in x, y, z order; `all`: 26-connected) | Identical to an independent brute-force event sort on 600 random rays, including corner ties and axis-parallel rays |
| `Ray.voxel_at(k)` (voxel after k steps by binary search on the merged progressions) | Equal to sequential on 300 rays x 25 positions; step 200 000 in 1.1-2.2 ms |
| `Ray.traverse_chunk(k0, n)` (independent chunk start, for parallel traversal) | Chunks join exactly into the sequential path |
| `batch.py`: fixed-point int64 kernel (S = 2^16, abs(d) < 2^15, < 2^20 steps, every product < 2^51), numpy lockstep | Equal to the exact reference; 91 ns per ray-step against 75 ns for float32 Amanatides-Woo |

**Floating point fails** (`test_voxelray.log`, `stress_float.log`, `batch.log`):
- **float32 Amanatides-Woo:** 90.6% of 4096 random rays visit a wrong voxel within 2000 steps (median first error at step
  1230). Long rays go wrong after about 1100-2000 steps.
- **float64:** rays through lattice edges and corners, with directions (2,3,6), (3,4,12) and (5,5,7) from an integer start,
  differ after 8-15 steps, because tie order depends on the rounding of 1/d. Long generic rays fail after 3e5-1.7e6 steps.
- **Exact traversal:** never drifts, and is deterministic, which matters for lockstep simulation, watertight voxelisation
  and agreement between CPU and GPU.

**Limits.**
- The O(log) random access uses Python Fractions here. A kernel would use the same integer comparisons.
- The int64 bounds assume fixed-point inputs. Larger ranges need 128-bit products.
- Some float64 tie "errors" are a different valid tie choice. The problem is that float resolves ties inconsistently.

## C kernel benchmark (`dda.c`, `run_dda.py`; CPU only, since there is no GPU in this environment)

Setup: 65 536 generic rays (|d| < 2^10, origins up to 2^10 voxels) plus 4096 tie-heavy rays (integer starts, |d| <= 12),
4096 steps each, gcc -O3 -march=native, OpenMP.

| method | ns/ray-step, with per-step path hash (1 / 4 threads) | without (`dda_nohash.c`) (1 / 4) |
|---|---|---|
| exact, cross-multiplication (num_a ad_b < num_b ad_a) | 7.46 / 2.14 | **3.50 / 0.94** |
| exact, integer tMax (common denominator L = abs(dx dy dz); T += S L/ad, adds and compares only) | **6.93 / 1.68** | 4.54 / 1.30 |
| float32 Amanatides-Woo | 10.54 / 2.83 | 5.79 / 1.59 |
| float64 Amanatides-Woo | 10.51 / 2.74 | 5.59 / 1.44 |

**Correctness.**
- Both exact C kernels match the Python exact reference (same path hash) on 100 sampled rays, 60 generic and 40
  tie-heavy, and agree with each other on all 69 632 rays.
- float32 gets the path wrong on 99.4% of generic rays within 4096 steps.
- float64 is right on generic rays at this length, but differs on 94.1% of the tie-heavy rays. Those are inconsistent tie
  resolutions, not misses.

**Correction (see `exactdda/README.md`).** The float baseline here updates `tmax[b]` through memory. Against a register-resident float loop, exact is about 1.2-1.4x slower on pure stepping, so it is not faster. The original claim was: on CPU, exact traversal is not a cost, 1.3-1.6x faster than float Amanatides-Woo. Integer add and
compare have 1-cycle latency in the loop's dependency chain, against 3-4 cycles for a float add. That rounding never
happens is the side benefit.

**GPU caveat (not measured).** GPUs emulate int64 multiply, so the integer tMax variant, with only adds and compares, is
the natural GPU form. A 32-bit version needs tighter bounds, roughly (steps x S x L/ad) < 2^31, i.e. fewer sub-voxel bits.
