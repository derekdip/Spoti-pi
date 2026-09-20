# Measured: what the bend arithmetic costs on a mobile GPU

`docs/quest-notes.md` section 4 said to measure before optimising the math
further, and listed profiling as step 2 of "where this should go next". This
is that measurement. Harness: `poc/web/bendbench.html`. Raw output:
`poc/results/bendbench-run2.json`.

## Method

Five modes draw the identical field from the identical instance buffers in
one instanced call, so only the per-vertex arithmetic differs. A zero-valued
uniform keeps both instance attributes live in every program, so the no-bend
baseline cannot quietly skip a vertex fetch the other modes pay for. Kernels
are ported from `unity/ReactiveKernels.hlsl` with the fitted constants in the
notes.

Timing does not use frame deltas, which quantise to whole vsync periods.
Each sample draws several frames and forces the GPU to finish with a
one-pixel `readPixels`; the clock's own quantum is probed at start-up and the
frames per block chosen from it. The stall is identical in every mode and
cancels out of the deltas. A warm-up runs at the measured load before
anything counts, and the baseline is measured twice, opening and closing, so
drift is visible and the two are averaged.

Device: an iPhone on iOS 18.7, reporting only "Apple GPU", through the Claude
app's web view. Render target 1024x640. Timer quantum 1 ms, 13 frames per
block, so nominal resolution 0.077 ms.

**The real noise floor is the baseline spread, not the timer.** The two
baselines differ by 0.38, 0.69 and 0.46 ms across the three presets, so
anything under about 0.7 ms is not a reading. That is the bar used below,
and it is roughly ten times the timer resolution.

## What it costs

Calibration raised the stalk count until the no-bend baseline needed about
10 ms, and overshot to 12 to 13 ms. Every preset therefore sits at a similar
frame cost but reaches it with different geometry.

| preset | stalks | verts/blade | M verts | M tris | baseline ms | drift |
|---|---|---|---|---|---|---|
| balanced, 4 segments, thin opaque | 575,079 | 10 | 5.75 | 4.60 | 13.04 | +3.0% |
| fill-bound, 2 segments, wide alpha-tested | 563,804 | 6 | 3.38 | 2.26 | 12.35 | -5.5% |
| vertex-bound, 10 segments, thin opaque | 399,362 | 22 | 8.79 | 7.99 | 13.46 | +3.5% |

| preset | mode | ms | vs baseline | resolved? |
|---|---|---|---|---|
| balanced | wake | 13.15 | +0.12, +1% | no |
| balanced | wake+presence | 13.77 | +0.73, +6% | marginal |
| balanced | **six terms** | 17.85 | **+4.81, +37%** | yes |
| balanced | bend texture | 13.31 | +0.27, +2% | no |
| fill-bound | wake | 13.08 | +0.73, +6% | marginal |
| fill-bound | wake+presence | 13.46 | +1.12, +9% | yes |
| fill-bound | **six terms** | 16.85 | **+4.50, +36%** | yes |
| fill-bound | bend texture | 11.31 | -1.04, -8% | yes |
| vertex-bound | wake | 13.38 | -0.08, -1% | no |
| vertex-bound | wake+presence | 13.54 | +0.08, +1% | no |
| vertex-bound | **six terms** | 14.38 | **+0.92, +7%** | yes |
| vertex-bound | bend texture | 13.31 | -0.15, -1% | no |

An earlier run at 420,000 stalks on the balanced preset, before the timer
fix, gave +2.67 ms or +27%. Same direction, same order, 30% apart on the
per-stalk figure; that run could only resolve 0.33 ms.

## Three findings

**At shipping density the question is moot.** The notes' cornfield is 15,000
stalks. Scaling the six-term cost down:

| preset | ms per 1000 stalks | at 15,000 stalks | share of a 13.9 ms budget |
|---|---|---|---|
| balanced | 0.0084 | 0.125 ms | 0.90% |
| fill-bound | 0.0080 | 0.120 ms | 0.86% |
| vertex-bound | 0.0023 | 0.035 ms | 0.25% |

Under one percent of a 72 Hz frame, agreeing across three load shapes. The
whole scene at that density extrapolates to about 0.36 ms. Section 4's claim
that the bend ALU is a small slice of fill or vertex cost holds, and the
reason is simply that a realistic field is 40 times smaller than what it
takes to load this GPU.

**The bend texture costs nothing, anywhere.** It is inside the noise floor
on two presets and measurably faster than the no-bend baseline on the third.
Against the six-term per-vertex path it saves 4.5 ms at the measured loads.
Section 2 of the notes recommended evaluating per instance rather than per
vertex on cost-model grounds; this is the first hardware evidence for it,
and it is the switch to throw if density ever rises.

**Op counts do not predict cost.** The same arithmetic, in the same compiled
program, costs eight times more per vertex-shader invocation in one preset
than another:

| preset | invocations | six-term cost | per million invocations |
|---|---|---|---|
| balanced | 5.75M | +4.81 ms | 0.836 ms |
| fill-bound | 3.38M | +4.50 ms | 1.330 ms |
| vertex-bound | 8.79M | +0.92 ms | 0.105 ms |

The vertex-bound preset runs the most invocations and pays the least. Six
numbers are not enough to identify the mechanism on a tile-based deferred
renderer, and no explanation is offered here. What matters for this project
is the consequence: the compositional search in `poc/reactive/search.py`
scores candidates with rough op counts, and op counts mispredict measured
cost by up to 8x depending on surrounding geometry. Any future use of that
cost term should either be calibrated against measurements at the intended
geometry or treated as a tie-breaker rather than a budget.

## What this does not measure

A phone is not a Quest 2. Both are tile-based mobile GPUs and the Quest
browser runs the same code, but the driver, the resolution, the stereo path
and the thermal envelope all differ, and a Unity build is not a WebGL2 one.
The stalk counts here are 25 to 40 times a realistic planting over a fixed
24 m field, so overdraw is far past anything a real scene produces. Nothing
here was run on a headset.

## Consequence for the ship list

The notes' section 1 says to ship two terms, wake and presence, on a
per-stalk error argument. Nothing in this measurement contradicts that, and
at 15,000 stalks it would not matter either way. The `pow` in the
generalised Gaussian and the two `exp` plus `sin` and `cos` in the spring
envelope are the obvious cuts if the six-term path is ever needed at
density; the notes already permit fixing `q = 1`, which removes both `pow`
calls. That optimisation is now known to be worth about 4.8 ms at 575,000
stalks and about 0.1 ms at 15,000, which is to say: not worth doing until
something else forces the density up.
