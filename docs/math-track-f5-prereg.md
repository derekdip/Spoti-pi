# F5: does a quasi-static sway law make the cheap fire follow a gust? Preregistration (frozen before any fresh scene is run)

F4 returned outcome D and named one specific cause for the visual half
of it: on every scene with a gust the fit slowed its parcels to a crawl
and filled the swept envelope instead of following the flame. F5 fixes
that, and in diagnosing it found that F4's glow bar cannot measure what
it was asked to measure.

## The diagnosis, on a pilot scene declared seen

Every F4 scene with a gust also has a bed or a shelf, so none can be
used to diagnose the gust without spending a scored scene. `gusty`, a
gusted plume with nothing else, was added for this and is **seen**: it
is excluded from every bar below, and it is the scene the bars are set
against.

**The teacher's plume sways almost in phase at every height.**
`poc/fire_gust_probe.py`, output `poc/results/gust_probe.log`: the
0.7 Hz component of the lateral centroid has a phase slope of
0.07 rad/m from 0.15 m to 1.5 m, and an amplitude growing 1.8x over
that range. The root moves too, 24 cm of range at 0.12 m. The gust is a
body force on the whole velocity field, so the air column shifts
together and the plume is quasi-static.

**The old law carried each parcel's birth phase upward**, giving a
phase slope of `w / v_rise`, about 2 rad/m at a realistic rise speed:
thirty times too much. Neighbouring heights then sway in opposite
directions and superposing them cancels the sway, so filling the swept
envelope with slow, long-lived parcels was genuinely the better fit.
Every F4 gusted fit did exactly that, choosing `v_rise` 0.37 to
0.56 m/s against a measured front speed of 2.25.

**The new law** (`poc/fire/puffs.py::_kinematics`): a parcel sits on the
instantaneous streamline, offset by the current lateral air speed times
the time it has been climbing, so every height shares one phase and the
amplitude grows with height. Two parameters follow from the
measurement, `gust_lag` and `sway_base`. For a steady wind the two laws
agree, which is why `windy` was never affected.

**Achievability, on the pilot** (`de_fit`, 16 active parameters):

| | fit error | sway tracked | phase error | glow correlation | parcels |
|---|---|---|---|---|---|
| new law | **0.518** | **87%** | 31 deg | 0.71 | 18 |
| same, gust forced off | 0.579 | 2% | — | **0.79** | 31 |

Tracking the sway improves the error by 10 percent and makes the glow
correlation worse.

## Why the glow correlation is not the motion bar

That result is a property of the measure, and it is demonstrable with
no model in it. `poc/fire_measure_check.py`, output
`poc/results/measure_check.log`, scores competitors built from the
teacher's own output:

| competitor | correlation |
|---|---|
| the teacher's own time-average: a perfect static blob | 0.852 |
| the teacher itself, delayed 0.07 s (17 deg of gust) | 0.965 |
| the teacher itself, delayed 0.13 s (34 deg) | 0.899 |
| the teacher itself, delayed 0.20 s (50 deg) | **0.836** |
| the teacher itself, delayed 0.27 s (67 deg) | 0.783 |
| the teacher itself, delayed half a gust period | 0.651 |

A **perfect** model of the fire, more than about 45 degrees out of
phase, scores below a model that never moves at all. Three scenes give
the same numbers to within 0.01, so this is the measure and the cause,
not the scene.

Two consequences, both of which change what F5 can claim. The
correlation is a **shape** measure whose ceiling for a static model is
0.85, so a bar of 0.80 on it can be met with no motion whatever: F4's
B1 was never a motion test, and F4's failure of it at 0.64 was a
statement about shape. And 45 degrees is not an arbitrary tolerance
but the measured point where motion stops paying, so it is the
tolerance used below.

## Procedure (frozen)

Unchanged from F4 except as stated: same teacher, frame stride, probes,
four consumers, consumer-space residual, `diagnose` and
`select_projection`, one percent accept floor, spent-repair blacklist,
no stopping rule, `NO_GATE = 1.01`.

- **Floor fit.** `rgre_puffs.floor_fit` wrapped in `BudgetCase`, which
  multiplies the error by `1 + 0.02` per parcel over a budget of 16 per
  source. F4's floor bought accuracy with parcels because nothing in
  the objective said a parcel costs anything. Every reported error is
  the **unpenalised** error; the penalty acts only inside the fit.
  Candidates are seeded differential evolution (seed 0, population 12,
  22 generations) with a Powell polish, and Powell from the two-stage
  start; the minimum is kept and both are reported.
- **Two objectives, cross-evaluated.** The standard four-consumer
  objective and the tone-mapped `LookCase`. Both fitted states are
  scored on the unpenalised standard error and **the better of the two
  is the scene's reported state**, which is the cross-evaluation F4's
  results said was missing.
- **Sway.** `f5_experiment.sway` fits the scene's own gust frequency,
  read from the cause, to the coarse-glow centroid over the second half
  of the run, for the teacher and the model by identical code. Reported
  as an amplitude ratio and a phase error in degrees.
- **Greedy.** From V0 on the budgeted case, 10 steps, on the fresh
  scenes only.

Runner: `poc/f5_experiment.py`. Output: `poc/results/f5.json`,
`f5_run.log`.

## Scenes

**Fresh, never fitted:** `gust_shelf` (gust plus a shelf, no bed),
`fast_gust` (the same gust at twice the frequency), `strong_gust`
(1.6 times the amplitude), `gust_twin` (two burners in a gust),
`bed_chain` (three beds in a line at increasing distance). All five
were validated against the teacher before this document was written
(`poc/fire_scene_check.py`, `poc/results/scene_check.log`); `bed_chain`
needed its third bed moved twice before it would light, which is the
check doing its job.

**Paired, declared seen:** `ignition`, `full` (gusted, from F4) and
`windy` (steady wind, the control for the claim that the two laws agree
without a gust). These were run in F4, so they are a before-and-after,
not a fresh test, and are reported separately from the fresh scenes.

**Transfer:** the state fitted on the pilot `gusty` is applied
**unchanged** to `fast_gust` and `strong_gust`, where only the cause
differs. Nothing is refitted. This is the test that the law is right as
a function of the cause rather than a curve fitted to one gust.

## Bars (frozen)

Scored at each scene's cross-evaluated best state, on the fresh scenes
only unless stated.

- **F5-B1, motion.** Median sway amplitude ratio over the four gusted
  fresh scenes within `[0.5, 1.5]`, and median phase error `<= 45`
  degrees. Pilot: 0.87 and 31 degrees.
- **F5-B2, shape.** Median glow correlation over the five fresh scenes
  `>= 0.70`. Pilot: 0.71. The static-average reference for each scene is
  reported beside it, so that no correlation is read as a motion result.
- **F5-B3, decisions.** Median burn disagreement `<= 5%`, median
  passable disagreement `<= 5%`, median missed alight `<= 25%` over the
  scenes where each applies. F4's B3 verbatim, so the two runs compare;
  F4 gave 11.5, 7.3 and 11 percent.
- **F5-B4, cost.** At most 20 parcels per source on every fresh scene.
  The objective's budget is 16 and its penalty is soft, so 20 is the
  budget plus the slack the pilot showed the penalty permits (18).
- **F5-B5, transfer.** The pilot's state, unchanged, keeps an amplitude
  ratio within `[0.5, 1.5]` and a phase error `<= 60` degrees on both
  `fast_gust` and `strong_gust`.
- **F5-B6, paired.** On the three paired scenes the unpenalised error is
  no worse than F4's by more than 10 percent, and the sway ratio
  improves on the two gusted ones.

## Predictions, recorded before the run

- **P1.** The fitted `v_rise` on gusted scenes rises above 1.0 m/s,
  against F4's 0.37 to 0.56, because filling the envelope is no longer
  the better fit.
- **P2.** `windy` is within 3 percent of F4's 0.329, since the two laws
  agree for a steady wind.
- **P3.** `fast_gust` is the hardest transfer: at twice the frequency
  the air has half the time to displace the plume, and the teacher's
  measured sway there is a quarter of `gusty`'s.
- **P4.** The glow correlation does not improve much even where the
  sway is tracked, because the measure rewards the average; the sway
  ratio and the error are where the fix should show.

## Outcome (frozen, exclusive)

Determined by B1 (motion) and B2 (shape); the others are reported and
do not move the letter.

- **A**: both hold. It moves like the teacher's fire and it is shaped
  like it.
- **B**: B1 holds, B2 fails. It moves right and is still the wrong
  shape; the residual names which consumer.
- **C**: B1 fails, B2 holds. Right shape, still not moving: the law is
  not the fix.
- **D**: neither.

No rescue, no second run on the fresh scenes. Results go in
`docs/math-track-f5-results.md`; nothing above is edited after the run.
