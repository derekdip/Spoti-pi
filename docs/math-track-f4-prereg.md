# F4: can a puff-train grammar express the teacher's fire? Preregistration (frozen before any unseen scene is run)

Three frozen experiments and one unfrozen arc established that the fire
representation, not the search, was the limit: greedy selection by
residual projection reaches 96 percent of a joint fit, and the joint fit
of a single anchored column, with three source shapes and two profile
exponents added, still leaves 0.58 relative error against 0.003 of seed
noise. The decision-level scoring (`docs/fire-decisions.md`) then showed
where that error lives: burn and passable decisions are 1 to 4 percent
wrong on the two simplest scenes, but the glow correlates 0.76 with the
teacher's against a corn precedent of 0.98, and a picture of the two
(`poc/results/fire_compare.png`) shows a short dim block against a tall
tapering tongue. The cheap fire is a fair hazard and it is not fire to
look at.

F4 tests the rebuild that every one of those documents ended by naming:
a grammar whose sources are not anchored shapes.

## The grammar

`poc/fire/puffs.py`. A source emits parcels at a rate; a parcel emitted
at `t_k` has, at time `t`, a position, a size and a temperature that are
closed-form functions of its age `t - t_k`: it accelerates to a rise
speed, drifts with the steady wind and the gust, is pushed toward the
nearer edge of a shelf it would hit, grows laterally, holds its peak
while its fuel burns and then cools exponentially. The field is the sum
over live parcels, plus an optional hot disc at the burner and a
parcel-carried soot. A bed lights on the same delay law as before and
emits parcels on its own envelope. No state, no stepping: a frame is
still evaluated on its own from the causes.

The claim under test is structural. Flicker, detachment at switch-off
and splitting around a shelf are not tokens here; they are what a train
of discrete parcels does. So two scenes that were out of vocabulary for
the column grammar by construction, `shutoff` and `split`, are predicted
to be in vocabulary now. That prediction is recorded below as P1.

V0 is the train alone (nine parameters). Expansions, off at zero:
`jitter`, `wind`, `deflect`, `base`, `soot`, `bed`, `attract`, and
`floor`, the same deliberate wrong atom as before. Classes, ranges and
on-states are in `poc/fire/rgre_puffs.py` and were written before any
scored scene was fitted. V0 defaults were set from four numbers measured
on `plume`, which no experiment scores (`poc/fire_puff_probe.py`,
`poc/results/puff_probe.log`): the start-up front reaches 2.25 m/s by
1.2 m, the mean centreline excess falls by a factor 0.47 over the 1.07 s
it takes to climb from 0.3 to 1.8 m, the lateral sigma grows from 0.060
to 0.094 m over a metre, and the unforced column barely flickers.

## The declared pilot, on two seen scenes

Before anything was frozen the grammar was fitted to `windy` and
`obstacle`, the two scenes the decision analysis found best served by
the old grammar, by `poc/fire_puff_pilot.py`. Those two scenes are
**seen** and are excluded from every bar below. The pilot exists for the
reason F3 gave: to know whether a bar is reachable before freezing it.
Its numbers are in `poc/results/puff_pilot.log` and are repeated here
so that what the bars were set against is on record.

PILOT_PLACEHOLDER

## Procedure (frozen)

Unchanged from F3 except for the representation and one added fitting
objective: same teacher, same frame stride, same probes, same four
consumers, same consumer-space residual normalised per consumer by scale
and width, same `diagnose` and `select_projection` from
`poc/rgre/core.py`, same one percent accept floor and spent-repair
blacklist, no stopping rule, no borrowed threshold (`NO_GATE = 1.01`).

- **Standard floor.** `rgre_puffs.floor_fit` on the four standard
  consumers: Powell from three starts (all classes on at their
  on-states, V0, box midpoint), 40 evaluations per active parameter
  each, minimum kept, the three values reported. Inert parameters are
  pruned per scene as before (no bed without patches, no deflect
  without a shelf, no attract with one burner). This is the number
  comparable with every earlier floor, and it is "no worse than", as
  the whole fire arc established.
- **Look floor.** The same fit with the visual consumer tone-mapped,
  `glow ** (1/2.2)`, before comparison (`rgre_puffs.LookCase`). The
  pilot found that under a linear glow the sooted base holds nearly
  all of the visual energy and the tongue costs almost nothing to
  omit, so a linear fit produces a hot disc. A player sees glow through
  a display transfer, and this objective says so. Heat, ignition and
  hazard are untouched in it.
- **Scoring.** Both fitted states are scored on the untouched standard
  case: linear four-consumer error, per-consumer error, decision rates
  (`poc/fire_decisions.py`), glow correlation over the second half of
  the run on the linear coarse glow, motion ratio, parcels per source.
  No bar is scored on the tone-mapped objective itself.
- **Greedy.** From V0 on the standard case, up to 10 steps, one repair
  evaluated per nomination, the same rule and constants F3 ran.

Runner: `poc/f4_experiment.py`. Output: `poc/results/f4.json`,
`f4_run.log`.

## Unseen scenes

`ignition`, `delayed_ignition`, `full`, `twin`, `shelf_bed`, `split`,
`shutoff`: seven scenes, none of which the puff grammar has been run on
before this experiment. Five were scored for the column grammar; two
were its out-of-vocabulary cases and are scored here.

## Bars (frozen)

BARS_PLACEHOLDER

## Predictions, recorded before the run

- **P1.** `split` and `shutoff`, out of vocabulary for the column
  grammar by construction, reach floors below the column grammar's
  best-known 0.411 and 0.551 respectively.
- **P2.** Greedy selects `deflect` on at least two of the three shelf
  scenes (`full`, `shelf_bed`, `split`), `bed` on at least two of the
  four bed scenes, and `attract` on `twin`.
- **P3.** `twin` is the hardest unseen scene for the glow: two plumes
  lean into each other by entrainment, which `attract` models as a
  constant drift and the teacher does not.

## Outcome (frozen, exclusive)

Determined by B1 (glow) and B2 (floor) alone; the other bars are
reported and do not move the letter.

- **A**: B1 and B2 hold. The puff grammar is fire to look at and within
  the numeric floor F3 asked for.
- **B**: B1 holds, B2 fails. It looks like fire and the hot region's
  extent is still numerically off for some consumer; the per-consumer
  table names which.
- **C**: B1 fails, B2 holds. Numerically adequate and not fire to look
  at: the correlation and the RMS disagree, and the picture decides
  which to believe.
- **D**: both fail. The puff train is not enough either.

No rescue, no second run on these scenes. Results go in
`docs/math-track-f4-results.md`; nothing above is edited after the run.
