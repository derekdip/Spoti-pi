# Puddle slosh (confined shallow water)

**Effect.** Water in a trough, bucket or shallow puddle after an impact:
sloshes back and forth, settles in a few seconds.

**Status: not recommended as a token.** Two cheap closed forms were fitted
to real MPM data and neither predicts the future of the slosh. Use the
fitted period and decay to drive a seeded procedural slosh, or run a tiny
1-D shallow-water solver (64 cells is nothing on CPU). Details below so the
negative result is not repeated.

**Data.** DeepMind Learning-to-Simulate `WaterDrop` validation set: 2-D MPM
water drops landing in a 0.8-wide box, 1000 frames at 2.5 ms. Free
surface extracted per column from the top particles
(`poc/water/gns_data.py`). Window: from 0.375 s after the floor is 90% wet
to the end (about 2 s). Depth after landing 0.02 to 0.09 box units; slosh
amplitude is a third of the depth, so this is strongly nonlinear shallow
water (bores), not gentle modes.

**Noise floor.** The extracted surface carries about 0.38 of its RMS as
column-sampling noise (what a 5-frame x 3-column box filter removes), so
the best possible in-window error is roughly 0.4.

**Candidates and scores** (`poc/results/slosh.md`, `slosh_pulse.md`):

| model | in-window error (median) | held-out second half |
|---|---|---|
| K = 4 standing shallow-water modes, fitted speed and damping | 0.73 to 0.86 (first 8 trajectories) | about 1.0 |
| K = 8 standing modes | 0.68 to 0.82 (first 8 trajectories) | about 1.0 |
| bouncing pulse with wall reflections (method of images), 30 trajectories | 0.76 | 1.00 |

In-window, both explain about half of the coherent energy. Fitted on the
first half of the window and scored on the second, both are no better than
predicting a flat surface. The slosh's frequency and shape drift with
amplitude (nonlinear), so a fixed-frequency closed form loses phase within
one period.

**What is reusable.** The fitted wave speed (median 0.8 box units per
second) and decay (1 to 3 per second) are consistent across trajectories
and give the right look for a procedural slosh. The Huygens/image-source
idea is still right for the first reflection or two.

**Known limits.** The synthetic teacher for open ponds is exact but
linear; the real puddle data is real but a 2-D side view with a noisy
surface. A 3-D shallow-water or MPM teacher of a stepped-in puddle would
settle whether a footstep splash (not a falling drop) behaves better.
