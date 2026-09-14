# Proof of concept

`run_experiment.py` does the whole loop:

1. **Teacher.** `reactive/teacher.py` runs 1600 stalks (576 with `--quick`)
   for 10 s at 60 fps with 4 substeps. Each stalk is a damped spring with
   stiffening, coupled to its four neighbours, with penalty contact between
   its tip and a 0.35 m cylinder that walks an S-curve for 6 s and then
   stands still, drag along the walker's velocity, and plastic crush with
   slow recovery. It records `bend(t)` for every stalk.
2. **Causes.** `reactive/causes.py` turns the walk into what a runtime would
   bank: one event every 0.5 m of travel, a 20 Hz polyline of the path with
   pass times, and the live player position.
3. **Grammar.** `reactive/primitives.py` holds the cheap kernels. Every one is
   a pure function of static geometry, time and a handful of parameters, so
   there is no per-stalk state, no integration, and no drift.
4. **Search.** `reactive/search.py` does greedy forward selection over the
   grammar, fitting parameters with Powell on a subset of frames and stalks.
   The objective is relative RMS error overall, plus the same on the
   persistence phase, plus a cost term from rough op counts.
5. **Report.** Full-resolution errors, the greedy path, single-primitive
   baselines, and the extra error from baking the model to a coarse field at
   16, 32 and 64 cells across.

The tests in `tests/` check the closed-form spring response against RK4,
causality of the ring wave and wake, and that dead tokens change nothing.
