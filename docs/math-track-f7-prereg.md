# F7: the hybrid selector as the fire workflow's default, and the F4 comparison re-run. Preregistration (frozen before any scored scene is run)

F6 folded the dictionary check into the fire workflow: fit the six
classes whose linearisation gap is over 0.25, rank the rest by
projection, take the best fitted drop. It captured the oracle's own
repair on the median step at half the oracle's cost and beat the arc's
selector on fourteen scenes of fifteen. Where it still lost, the
oracle's class was a small-gap class every time, ranked by the
projection below `deflect`; F1's support templates, which the fire
cross-check found put the mechanism ahead of the value, were the
suspect. F7 makes that one change and re-runs the comparison the arc
uses to judge the cheap fire: F4's seven scenes, F4's ten-step budget,
F4's scoring of the terminal state.

## The change

The small-gap classes are ranked by the signed tangents alone. The
templates are dropped from the diagnosis (`core.diagnose` called with
no templates and no support classes, both unchanged functions). Nothing
else moves: the same classification of classes, the same class fit,
the same spent rule, the same objective. A second variant that fits
the top two projected small-gap classes instead of one is run beside
it and reported, not barred.

## What it is compared with

All on the same seven scenes (`ignition`, `delayed_ignition`, `full`,
`twin`, `shelf_bed`, `split`, `shutoff`), from the same default state:

- F4's projection greedy, ten steps, the arc's own workflow
  (`poc/results/f4.json`, `greedy.e_final`);
- F4's global floor, differential evolution over all 22 parameters
  (`fits.standard`), and its look fit;
- the column grammar's best known floor (`poc/results/column_reference.json`);
- F6's hybrid with templates, eight steps (`poc/results/f6.json`).

Per-step value is measured against the full oracle table computed at
every step of every path, as in F6. The terminal state is scored with
`poc/fire_decisions.decisions`, exactly as F4 scored its fitted states,
so the glow correlation and the decision rates compare directly.
`poc/f7_experiment.py`, scorer `poc/f7_score.py`, both committed with
this document.

## The declared pilot

`windy`, not one of the seven, two steps
(`poc/results/f7_pilot.*`): both variants took `rise` then `jitter`,
the oracle's own picks, at value 1.00, from 0.962 to 0.591 in two
steps, six repairs a step of eleven; 48 seconds.

## Bars (frozen)

- **K1, value.** Median per-step value `>= 0.90` over all steps with
  positive oracle gain, and mean value above F6's hybrid on the same
  seven scenes (F6's mean over its fifteen was 0.75).
- **K2, the terminal state moves.** Terminal error after ten steps
  below F4's projection greedy on `>= 6` of the seven scenes.
- **K3, the greedy reaches the floor.** Median terminal reduction
  `>= 0.95` of F4's differential-evolution floor's median reduction.
  F4's projection greedy reached 0.83.
- **K4, the look.** Glow correlation (F4's `late_correlation`) at the
  hybrid's terminal state above the correlation at F4's floor state on
  `>= 4` of the seven scenes.

Reported: the two-class variant on every line; terminal error against
the column grammar's best known floor, scene by scene; the decision
rates and parcel counts at the hybrid terminal against F4's floor
state; the share of lost steps whose oracle was a small-gap class,
against F6's 43 of 120.

## Predictions

K1 holds: the lost steps in F6 were the templates' doing on the scenes
looked at, and this removes them. K2 holds: F6's hybrid already beat
the arc's selector on all seven of these scenes at eight steps. K3 is
open and is the point: a greedy search with one class fitted per step
against a 22-parameter global optimiser. K4 is open: F4 found the
glow correlation at the floor state was 0.64 in median and that the
look was not what the fitting objective optimises; a better search on
the same objective may or may not move it.

## Outcome (frozen, exclusive)

- **A**: K2 and K3 hold. The hybrid greedy is the workflow: it reaches
  the global floor at a fraction of its cost and the puff fire's
  terminal state is the vocabulary's floor.
- **B**: K2 holds, K3 fails. The search moves the terminal state and
  does not reach the floor; the remaining gap is the greedy's.
- **C**: K3 holds, K2 fails.
- **D**: neither.

K1 and K4 are reported under every letter. If K4 holds the look moved
with the search; if it fails, F4's finding stands that the look is a
matter of the objective, not of the search.

No rescue, no second run on the scored scenes, no change to the
classification, the rules or the budget after this commit. Results go
in `docs/math-track-f7-results.md`; nothing above is edited after the
run.
