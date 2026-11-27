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
