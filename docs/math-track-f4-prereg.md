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
speed, drifts with the steady wind and the gust, grows laterally, holds
its peak while its fuel burns and then cools exponentially. Under a
shelf it drifts sideways as it approaches, is held under the shelf as a
flattened pancake spending its denied climb on sideways travel, and
resumes climbing once it clears an edge. The field is the **maximum**
over live parcels, because temperature is intensive and two parcels
overlapping are the same gas; an optional hot disc at the burner and a
parcel-carried soot are combined the same way. A bed lights on the same
delay law as before and emits parcels on its own envelope. No state, no
stepping: a frame is still evaluated on its own from the causes.

The claim under test is structural. Flicker, detachment at switch-off
and splitting around a shelf are not tokens here; they are what a train
of discrete parcels does. So two scenes that were out of vocabulary for
the column grammar by construction, `shutoff` and `split`, are predicted
to be in vocabulary now. That prediction is recorded below as P1.

V0 is the train alone (nine parameters). Expansions, off at zero:
`jitter`, `wind`, `deflect` (with its reach), `base`, `soot`, `bed`,
`attract`, `profile` (the parcel's profile exponent, Gaussian by
default), and `floor`, the same deliberate wrong atom as before.
Classes, ranges and on-states are in `poc/fire/rgre_puffs.py`. V0
defaults were set from four numbers measured on `plume`, which no
experiment scores (`poc/fire_puff_probe.py`,
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

The pilot ran three rounds, each of which changed something, and the
grammar and protocol above are what the third round left:

1. **Round one** summed parcel temperatures. Slow parcels near the source
   piled into thousands of kelvin, the fitter shrank the train until it
   was invisible, and both scenes fitted a hot disc. Temperature is
   intensive; the combination is now a maximum.
2. **Round two** (maximum combination, three Powell starts, standard and
   look objectives) still parked every start in a disc-plus-invisible-
   train optimum. Hand-built hot trains beat the fitted states, so the
   optimiser was leaving value on the table; a train-only-then-all fit
   on `windy` found 0.339 with glow correlation 0.93; seeded differential
   evolution on `obstacle` found 0.41 on the look objective where the best
   local start found 0.53. Pictures showed parcels flying through the
   shelf or pushed to its far edge while the teacher's column ends at the
   shelf. Three changes followed: shelf blocking, the profile exponent,
   and the DE-plus-two-stage floor protocol.
3. **Round three** is the grammar and protocol frozen here:

| scene | objective | fit (de, two-stage) | standard error | column best-known | per consumer (vis, heat, ai) | burn wrong | passable wrong | glow corr | parcels |
|---|---|---|---|---|---|---|---|---|---|
| windy | standard | 0.329 (0.332, 0.329) | **0.329** | 0.385 | 0.474, 0.135, 0.286 | 0.6% | 0.4% | 0.90 | 6 |
| windy | look | 0.255 (0.255, 0.257) | 0.354 | 0.385 | 0.515, 0.184, 0.279 | 0.9% | 0.5% | **0.92** | 7 |
| obstacle | standard | 0.432 (0.432, 0.471) | **0.432** | 0.460 | 0.655, 0.137, 0.335 | 1.5% | 1.1% | 0.78 | 14 |
| obstacle | look | 0.370 (0.370, 0.390) | 0.489 | 0.460 | 0.741, 0.144, 0.384 | 2.7% | 3.2% | **0.80** | 12 |

The standard fit beats the column grammar on both seen scenes, by 15 and
6 percent, and on every consumer. The look fit raises the glow
correlation by 0.02 on each scene at a cost in linear error, and on
`obstacle` its state misses 59 percent of hazard cells: the tone-mapped
objective buys glow with hazard. The two optimisers agree within 1
percent on three of four fits and DE wins the fourth by 9 percent. Glow
correlation reached 0.92 on the simplest scene and 0.80 on the shelf
scene; the 0.90 proposed in `docs/fire-decisions.md` is therefore not
reachable as a median over scenes that are harder than `windy`, and the
bar below is set at what the shelf scene reached. F3's absolute floor of
0.35 is reached on `windy` and not on `obstacle`, so no absolute floor
bar is frozen; the floor bar is relative to the column grammar, which is
the question this experiment exists to answer.

The pilot's fitted states are not used anywhere in the unseen run. Its
starts are the DE Latin hypercube at seed 0 and the two-stage fit from
V0, on every scene.

## Procedure (frozen)

Unchanged from F3 except for the representation and one added fitting
objective: same teacher, same frame stride, same probes, same four
consumers, same consumer-space residual normalised per consumer by scale
and width, same `diagnose` and `select_projection` from
`poc/rgre/core.py`, same one percent accept floor and spent-repair
blacklist, no stopping rule, no borrowed threshold (`NO_GATE = 1.01`).

- **Standard floor.** `rgre_puffs.floor_fit` on the four standard
  consumers: the minimum of two candidates, both reported. Seeded
  differential evolution (seed 0, population 12 per parameter, 30
  generations, Latin hypercube start) followed by a Powell polish; and
  Powell from a two-stage start, which first fits the train with the
  hot disc, the soot and the floor held off and then hands everything
  over. Inert parameters are pruned per scene as before (no bed without
  patches, no deflect without a shelf, no attract with one burner).
  This is the number comparable with every earlier floor, and it is
  "no worse than", as the whole fire arc established.
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

Column reference values are the best-known floors from the fire arc and
the decision rates of the f6 Powell states (`poc/results/column_reference.json`):
best-known floors ignition 0.580, delayed_ignition 0.626, full 0.590,
twin 0.503, shelf_bed 0.615, split 0.411, shutoff 0.551.

- **F4-B1, glow.** Median glow correlation over the second half of the
  run, at the look-fit state, over the seven unseen scenes `>= 0.80`.
  For `shutoff`, where nothing glows in the second half, the full-run
  correlation is used instead. The count of scenes at or above 0.90 is
  reported.
- **F4-B2, floor against the column.** The standard-fit error is below
  the column grammar's best-known floor on at least 6 of the 7 unseen
  scenes.
- **F4-B3, decisions.** At the standard-fit state, median burn
  disagreement `<= 5%` and median passable disagreement `<= 5%` over the
  seven unseen scenes; median missed-alight `<= 25%` over the three
  scorable bed scenes (`ignition`, `delayed_ignition`, `full`;
  `shelf_bed`'s bed never lights in the teacher and is vacuous).
- **F4-B4, cost.** Parcels per source at the standard-fit state `<= 24`
  on every unseen scene.
- **F4-B5, search.** Median greedy error reduction `>= 0.80` of the
  standard floor's reduction, F3-B2 verbatim.


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
