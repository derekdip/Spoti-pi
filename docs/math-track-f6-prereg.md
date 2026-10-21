# F6: the two ML-track changes folded into the fire workflow. Preregistration (frozen before any scored scene is run)

RGRE-ML-3 replaced the procedure's stopping constant with a permutation
test on its own statistic, and the linearisation-gap document turned
"a candidate must have a direction before it is fitted" into a number
that can be measured per class before a run. Both were established on
real tabular data. This experiment brings them back to the domain the
procedure was built for, the cheap fire, and asks whether they change
what the fire workflow does. Same teacher, same puff grammar, same
classes, ranges and objective as F4 and F5, same selector
(`poc/rgre/core.py`, unchanged), same class fit (`rgre_puffs.fit_class`).

## The two changes

**The dictionary check.** `poc/results/fire_lin_gap.json` measured, on
the nine design scenes at step zero, the share of each class's fitted
repair that lies outside its tangent span. The classification it gives
is frozen here as a property of the grammar: `amp`, `cool`, `wind`,
`rate`, `bed` and `rise` have gaps of 0.48 to 0.98 and are fitted to
be ranked; `width`, `deflect`, `profile`, `base` and `attract` have
gaps of 0.00 to 0.13 and are ranked by projection; `jitter`, `soot`
and `floor` are inert at step zero, their gap is unmeasured, and they
are ranked by projection. The **hybrid** rule at each step fits every
live large-gap class, fits the projection's top small-gap class, and
takes the best drop. It needs at most seven repairs per step against
the arc's one and the oracle's twelve to fourteen.

**The stop with no constant.** At each step the statistic `q_top`, the
largest share of residual energy any one class's tangents explain, is
recomputed on the residual shuffled within each consumer block, 49
times; the rule declines a step when any of the first M shuffles
reaches the observed value, M = 19 scored and M = 49 reported, as in
RGRE-ML-3.

## Protocol

Fifteen scenes: the nine design scenes (`windy`, `obstacle`, `twin`,
`split`, `shutoff`, `ignition`, `delayed_ignition`, `full`,
`shelf_bed`) on which the gap table was measured, and six transfer
scenes from F5 (`gusty`, `gust_shelf`, `fast_gust`, `strong_gust`,
`gust_twin`, `bed_chain`) on which nothing was measured. Three
selection rules grow the grammar from the default state on every scene,
each along its own path, eight steps, no stopping rule; the arc's
spent rule (a repair worth under one percent is not applied and its
class is blacklisted) is kept so that a path cannot stall on one class.
At every step of every path the full oracle table is computed, so value
captured is measured against the same table for all three rules and
the repairs each rule would need is counted rather than spent.
Held-out error is the same state scored against a second teacher run
of the scene with the seed advanced by one; the difference between the
two teacher runs is recorded per scene as the noise floor.
`poc/f6_experiment.py`, scorer `poc/f6_score.py`, both committed with
this document.

## The declared pilot

`plume`, the bare flame, two steps, excluded from every bar
(`poc/results/f6_pilot.*`). The arc's projection picked `wind` at step
zero, a repair the fit could not make pay, and `width` at step one for
0.55 of the oracle; the hybrid picked `rise` then `jitter`, the
oracle's own choices, at value 1.00, and ended at 0.610 against
projection's 0.649. `q_top` was 23 times its shuffled maximum at both
steps. Fifty-two seconds.

## Bars (frozen)

- **G1, value.** Over every step of every path with positive oracle
  gain, the hybrid's median value captured `>= 0.90` and above the
  projection rule's median.
- **G2, terminal.** Median terminal in-sample reduction after eight
  steps, hybrid `>=` projection, and `>= 0.95` of the oracle rule's
  median.
- **G3, the check transfers.** On the six transfer scenes, the
  step-zero gap of each classified class falls on the same side of
  0.25 as the design classification on `>= 80%` of scene-class pairs.
- **S1, the stop.** On the hybrid path, scored by held-out error at
  the chosen step: the null rule's mean regret is below the one percent
  rule's, and on scenes whose last three steps each gained under one
  percent held-out, the null rule stopped before the budget on at least
  half.

Reported: repairs needed per step by rule; per-scene terminal errors,
in-sample and held-out, with the noise floor; the null rule at M = 49;
the ratio of `q_top` to its shuffled maximum by step; the gap of the
oracle's class and of each rule's pick along the paths.

## Predictions

G1 holds: the six large-gap classes are the ones the projection could
not rank, and fitting them is what the check prescribes. G2 is open:
F3 found the arc's greedy path reaching 96 percent of the joint fit,
so the room for a better first step to change the terminal error is
small. G3 holds if the gap is a property of the grammar and fails if
it was a property of the nine scenes; the prediction is that it holds.
S1 fails: the fire residual is structured everywhere and reachable
almost nowhere, and a shuffle null tests structure, not reachability,
so the rule is expected never to stop within the budget. That result
would say the same thing RGRE-ML-3's auto mpg case said from the other
side, and it is worth having on record in the domain that motivated
the procedure.

## Outcome (frozen)

- **A**: G1 and G2 hold. The dictionary check improves the fire
  workflow end to end, at half the oracle's cost.
- **B**: G1 holds, G2 fails. The check fixes the picks and the terminal
  state was already at the vocabulary's floor, as F3 said.
- **C**: G1 fails. The classification does not carry along a path.

G3 and S1 are reported with pass or fail under every letter.

No rescue, no second run on the scored scenes, no change to the
classification, the rules or the budget after this commit. Results go
in `docs/math-track-f6-results.md`; nothing above is edited after the
run.
