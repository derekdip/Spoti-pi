# exactdda.h: exact, deterministic voxel ray traversal

A single-header C99 library (also compiles as C++) that walks a ray through a 3D voxel grid using integer arithmetic
only. The path never drifts and is identical on every platform, compiler and float mode. It is also faster than the
usual floating-point Amanatides-Woo DDA. Any step can be reached directly, in O(log k), so one long ray can be split
across threads exactly.

```c
#include "exactdda.h"

edda_ray r;
double o[3] = {3.25, 10.5, 7.75}, d[3] = {1.0, 0.9, 1.1};
edda_init_f(&r, o, d, 16, 15);          /* origin to 1/65536 voxel, direction to 15-bit integers */

EDDA_WALK(&r, 1000, x, y, z, {          /* fast loop: body runs for each new voxel (x, y, z) */
    if (solid(x, y, z)) break;
});

int64_t tn, td; edda_t_exit(&r, &tn, &td);   /* exact exit parameter of the current voxel, t = tn/td */
edda_seek(&r, 1000000);                      /* jump to the state after 10^6 steps, exactly, in O(log) */
```

## API

| Call | Purpose |
|---|---|
| `edda_init(r, o_num, S, d)` | Origin `o_num/S` (integers), integer direction `d` (abs(d) < 2^31, not all zero) |
| `edda_init_f(r, o, d, frac_bits, dir_bits)` | Deterministic quantisation of a float ray: origin to 2^-frac_bits, direction to dir_bits-bit integers |
| `EDDA_WALK(r, maxsteps, x, y, z, { body })` | Fast loop with the state in registers. `break` works; the state is written back to `r` |
| `edda_step(r)` | One 6-connected step; returns the axis moved. Ties (edges, corners) step x, then y, then z |
| `edda_step26(r)` | One 26-connected step (tied axes together); returns a bit mask |
| `edda_seek(r, k)`, `edda_voxel_at(r, k, out)` | Exact state or voxel after k steps from the start, O(log k). Needs `__int128` (GCC/Clang) |
| `edda_t_exit(r, &tn, &td)` | Exact exit parameter of the current voxel |
| `edda_max_steps(r)` | Steps per axis for which the arithmetic is guaranteed exact |

**Conventions.**
- At parameter t the ray is in the voxel containing P(t + 0). Per axis the index is floor(x) for d >= 0 and ceil(x) - 1
  for d < 0, so a ray starting on a plane is already in the voxel it is heading into.
- `EDDA_WALK` and `edda_step` produce identical paths, and all calls compose: walk, then seek, then step, and so on.

**Exactness.** Per axis, the crossings are t_j = (j S - F)/(abs(d) S). The next crossing is chosen by exact
cross-multiplication:
- 64-bit while provably safe (`safe64`, typically about 10^15 steps);
- 128-bit beyond that, where available.

Without `__int128`, use `edda_max_steps` and do not call `edda_seek`.

## Verified (`make test`, `tests/`)

1. `edda_step` matches an independent brute-force event sort (all crossings as exact fractions, sorted by
   (time, axis)) on 3000 random rays, including ties through edges and corners and axis-parallel rays.
2. `edda_seek` and `edda_voxel_at` match stepping (1500 rays x 20 positions). Independent chunks join exactly.
3. `edda_step26` is 26-connected and visits a subsequence of the 6-connected path.
4. On rays of 10^9 steps, seek(K) equals seek(K - 1000) followed by 1000 steps, and exit times are monotone.
5. `edda_init_f` is deterministic.
6. `EDDA_WALK` matches `edda_step` on 2000 rays, including the forced 128-bit branch and early `break`.
7. Path hashes from `edda_step` and from `EDDA_WALK` both match the earlier validated kernel (`../dda.c`) on all 69 632
   benchmark rays.
8. No warnings with `-std=c99 -Wall -Wextra -pedantic` (gcc, clang). The C++11 build compiles (`make cxx`).

## Speed (`tests/bench_vs_dda.c`, `bench.log`)

69 632 rays x 4096 steps, gcc -O3 -march=native, this container's CPU:

| | ns per ray-step, 1 thread | 4 threads |
|---|---|---|
| `EDDA_WALK` | **2.28** | **0.72** |
| `edda_step` in a loop | 9.03 | 2.29 |
| float32 Amanatides-Woo (`../dda.c`) | 5.79 | 1.59 |
| float64 Amanatides-Woo (`../dda.c`) | 5.59 | 1.44 |

**Why it is fast.** Each step's choice depends on the previous one, so step latency sets the speed. An integer add and
compare costs about 1 cycle in that chain; a float add costs 3-4.

**Why `edda_step` is slower.** A call that updates `r->v[b]` through memory pays a store-to-load round trip on every
step. Use `EDDA_WALK` in hot loops.

**Why exactness matters** (`../README.md`).
- float32 Amanatides-Woo takes a wrong path on 99.4% of these rays within 4096 steps.
- float64 resolves edge and corner ties inconsistently, on 94% of the tie-heavy rays here, and drifts on rays of
  10^5-10^6 steps.

## Limits

- The inputs are fixed-point. Float rays must be quantised first (`edda_init_f`), which perturbs the direction by at most
  one part in 2^dir_bits, deterministically.
- `edda_seek` needs `__int128`, so not MSVC as written.
- Only CPU has been measured. On GPUs 64-bit integer multiplies are emulated. A GPU port would use the common-denominator
  form (adds and compares only, `../dda.c` `exact_tmax`) with tighter bounds.
