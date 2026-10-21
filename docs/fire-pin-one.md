# Which measured constants are really the token's parameters, and a correction to how they were judged

Pinning seven measured constants at once made the fire worse on every
scene (`docs/fire-physics-first.md`), while pinning one of them had
produced the best-looking state in the arc
(`docs/fire-height-control.md`). This resolves that by pinning each
alone. It also corrects an error in how every correlation in the last
two documents was framed.

Script: `poc/fire_pin_one.py`, prediction recorded in its docstring and
committed before the run. Output: `poc/results/pin_one.log`, `.json`,
`pin_combined.log`, `static_reference.log`. Scene: `plume`, the
reference scene, never scored in any experiment. Free baseline
reproduces the height control exactly: error 0.4753, visual 0.705,
correlation 0.75, 14 parcels.

## Each constant, pinned alone

| pinned | value | total error | visual | correlation |
|---|---|---|---|---|
| `accel` | 0.661 /s | **-8.8%** | -9.4% | **0.86** |
| `width` | 0.055 m | **-5.0%** | -6.8% | 0.85 |
| `v_rise` | 2.25 m/s | +13.8% | -6.1% | 0.84 |
| `v_rise` | 3.47 m/s | +1.5% | -5.1% | 0.83 |
| `soot_amp` | 10.09 | +15.0% | +8.7% | 0.83 |
| `amp` | 906.5 K | +1.6% | -4.2% | 0.82 |
| `cool` | 0.775 s | +1.6% | -0.8% | **0.67** |
| `grow` | 0.140 m/s | **+49.6%** | +25.9% | **0.45** |

Six of eight improve the correlation on their own, so the recorded
prediction (fewer than half) **fails**, in the direction that says the
identifications are individually sound and the seven-at-once result was
an interaction. `v_rise` at 2.25 replicates the height control exactly,
0.75 to 0.84.

**Two of them improve the total error as well**, by 8.8 and 5.0 percent.
Differential evolution with 22 generations, a Powell polish and a
two-stage start did not find those states; fixing one parameter from a
measurement did. That is an optimiser failure, not only an objective
preference, and it is the first direct evidence in the arc that the
floors are still being under-measured.

**The two failures are the two named in advance.** The physics-first
write-up predicted that `cool` and `grow` were misidentified, because
both were measured as ensemble properties of the plume rather than
per-parcel ones: `cool` from the decay of the centreline peak, which is
a superposition of parcels passing a point, and `grow` from the lateral
spread of the time-mean field, which contains the scatter of parcel
positions as well as each parcel's own growth. Both fail here, `grow`
catastrophically, and `grow` alone is destructive enough to account for
much of the seven-at-once collapse. The third quantity that write-up
suspected, `v_rise`, is fine at both measured values.

## Combining them is not additive

| on `plume` | total error | visual | correlation | parcels |
|---|---|---|---|---|
| free fit | 0.4753 | 0.705 | 0.75 | 14 |
| `amp`, `v_rise`, `accel`, `width` | +0.4% | +0.1% | **0.70** | 15 |
| those four plus `soot_amp` | +0.6% | +2.3% | **0.88** | 13 |

The four that each help most cheaply are, together, **worse than any of
them alone**, and adding a fifth moves the correlation from 0.70 to
0.88. Whatever the interaction is, it is strong and it is not
predictable from the single-parameter results, so a combination has to
be measured rather than assembled.

## The correction: the static-blob reference is scene-dependent

`docs/fire-physics-first.md`, `docs/fire-height-control.md` and this
session's summaries all compared correlations against "a static blob
reaches 0.85". That number came from `poc/fire_measure_check.py`, which
was run on three scenes, **all of them gusted**. It does not
generalise, and treating it as a constant was wrong.

| scene | gust | static-blob reference | best model state in the arc |
|---|---|---|---|
| plume | none | **0.997** | 0.88 |
| twin | none | **0.989** | 0.86 |
| strong_gust | 2.6 m/s | 0.796 | **0.80** |
| bed_chain | 2.0 m/s | 0.827 | 0.81 |
| gusty | 1.6 m/s | 0.852 | 0.82 |
| gust_shelf | 1.8 m/s | 0.853 | 0.80 |
| ignition | 1.6 m/s | 0.852 | 0.73 |
| full | 1.6 m/s | 0.860 | 0.76 |

The reference is 0.99 where the teacher barely moves and 0.80 to 0.86
where it sways, because a time-average is a nearly perfect predictor of
a steady flame. So the claims made earlier in this session need
correcting in both directions:

- **On the steady scenes the model is far worse than trivial.** The 0.88
  on `plume` celebrated above is well below the 0.997 a motionless model
  reaches there. Saying it "beat the static ceiling" was wrong.
- **On the gusted scenes the model is close to the reference, and on one
  it is past it.** `strong_gust` at 0.80 against 0.796 is the only state
  anywhere in this arc that beats a static blob on its own scene, and it
  is a state F5 already produced.

F5's B2 also has to be re-read. It was set at 0.70 and passed at 0.800
over five gusted fresh scenes, whose references run 0.796 to 0.853; so
it passed a model that is at or just below trivial on four of the five
and past it on one. That is a fairer description than either "passed"
or the "worse than a static blob" gloss put on it at the time.

## What this settles, and what it does not

**Settled.** The objective and the optimiser, not the grammar, limit
appearance on the scenes tested. Six of eight measured constants
improve the look when pinned, two of them improve the fitting error as
well, and the grammar reaches 0.88 on `plume` where free fitting
reaches 0.75. The grammar had those states available throughout.

**Not settled.** Whether any of this closes the gap on the scenes that
matter. The gains here are on `plume`, the simplest scene in the set,
and the static reference shows that scene is nearly trivial to predict.
The honest next test is the five-constant recipe on the gusted scenes,
scored against each scene's own reference rather than a borrowed
constant.

**A standing correction to the method.** Every reference quantity in
this arc should be measured per scene before it is used as a bar. The
0.85 that four documents leaned on was measured on three scenes that
shared a property the others do not.
