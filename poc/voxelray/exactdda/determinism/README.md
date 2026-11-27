# Determinism across builds (`run.sh`, `determinism.c`, `determinism.log`)

Same source, 11 builds on this x86-64 machine: gcc -O0, -O2, -O3 -march=native (FMA contraction on and off),
-ffast-math, -mfpmath=387 (x87), clang -O2, clang -O3 -march=native -ffast-math, and gcc/clang with -ffast-math -mrecip
(approximate reciprocals, as GPUs use). There are 20 000 integer-generated rays (every 8th tie-heavy), 2000 steps each,
and the path of each ray is hashed.

| method | rays whose path depends on the build |
|---|---|
| exactdda (`EDDA_WALK`) | **0** |
| Amanatides-Woo float32 (accumulated tMax) | 3096 (15.5%), all from the `-mrecip` builds |
| Amanatides-Woo float64 | 0 |
| recompute variant float32, t = (plane - o) * (1/d) | 547 (x87: 259, -mrecip: 388) |
| recompute variant float64 | 0 |

**Reading.**
- The basic float loop uses only divide, add and compare, which are correctly rounded IEEE operations, so on one
  architecture it is reproducible across ordinary compilers and flags, fast-math included. Our first run, without
  `-mrecip`, showed exactly that.
- float32 stops being reproducible under approximate reciprocals (`-mrecip`, and GPU `rcp`) or x87 extended precision.
  Those are the situations that matter for CPU/GPU agreement and for cross-platform lockstep.
- float64 survived every build tested here.
- Architectures other than x86-64 (ARM, GPUs) were not tested in this container.
- Exact integer traversal is identical in every case, by construction.
