# F7 results: outcome B. Without templates the hybrid takes the oracle's repair on the median step and beats the arc's workflow on six scenes of seven, and the greedy still reaches only 0.73 of the global floor: with the puff grammar the search is part of the limit

Preregistration: `docs/math-track-f7-prereg.md`, frozen at commit
`c2dd7dc`, unchanged. Raw output: `poc/results/f7.json`, `f7.log`,
`f7_report.md` (the frozen scorer's output, `poc/f7_score.py`). Seven
scenes, ten steps, two variants, the full oracle table at every step,
742 seconds on three workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 value | median `>= 0.90`, mean above F6's hybrid | median **1.000**, mean **0.844** vs 0.758 | pass |
| K2 the terminal state moves | below F4's projection greedy on `>= 6` of 7 | **6 of 7** | pass |
| K3 the greedy reaches the floor | median reduction `>= 0.95` of F4's differential-evolution floor | **0.725** (F4's greedy 0.600) | **fail** |
| K4 the look | glow correlation above F4's floor state on `>= 4` of 7 | 3 of 7 | **fail, as F4 predicted** |

K2 holds and K3 fails, so the letter is **B**: the search moves the
terminal state and does not reach the floor, and the remaining gap is
the greedy's. This time the frozen text fits the numbers.

## What each bar means

**Dropping the templates removes a third of the lost steps and not the
rest (K1).** Lost steps fell from 19 of 56 in F6 to 18 of 68 here, and
on every one the oracle's class was still a small-gap class, `width`
on most: the projection ranks `jitter` and `cool` above `width` at the
later states, templates or not. The two-class variant, which fits the
top two projected small-gap classes, lifts the mean value to 0.927 at
seven repairs a step instead of six, and loses only 5 steps of 68. So
the projection's ranking among the small-gap classes is unreliable at
the second place as well as the first, and the cheap remedy is to fit
two of them.

**The terminal state moves (K2).** Six scenes of seven end below F4's
ten-step projection greedy, by 0.004 (`shutoff`) to 0.114 (`split`).
The one loss is `full`, 0.591 against 0.525: the hybrid took `cool`,
`jitter` and `soot` on steps three to six while the oracle wanted
`deflect`, the class the fire cross-check found the templates put
first; without them the projection ranked it fourth. The two-class
variant ends `full` at 0.529 and every other scene at or below the
one-class variant.

**The greedy does not reach the floor (K3).** Median terminal
reduction is 0.297 for the hybrid, 0.346 for the two-class variant
(reported), 0.410 for F4's differential-evolution fit of all 22
parameters at once. F3 found the column grammar's greedy reaching 96
percent of its joint fit and concluded the search was not the limit.
That conclusion does not carry to the puff grammar: a path of one
class fitted at a time by coordinate descent, however well chosen,
ends 0.11 of the V0 error above what the joint optimiser finds, and
the better selector closed a third of the gap F4's greedy had left.
The remaining gap is the greedy's own, and the joint fit costs twenty
times the compute.

**The look does not move with the search (K4).** Glow correlation at
the hybrid terminal is above F4's floor state on `twin`, `shelf_bed`
and `split` and below it on the three bed-ignition scenes; `shutoff`
is undefined for both, the fire being out over the late window the
statistic reads. F4's finding stands: the look is a matter of the
objective, not of the search, and F4's look fit, which optimised the
tone-mapped glow directly, is the only state that moved it.

## Reported

Against the column grammar's best known floor the hybrid ends below on
two scenes of seven (`twin`, `split`); F4's differential-evolution
floor was below on five. Decision rates at the hybrid terminal are
within a few points of F4's floor state either way: heat-decision
disagreement 0.1 to 21 percent against 0.2 to 16, hazard-grid
disagreement 1 to 16 against 1 to 13; `delayed_ignition` misses no
bed ignition where the floor state missed 11 percent, and `ignition`
misses 17 where the floor missed 6. Parcel counts at the hybrid
terminal run from 15 to 33, above the floor state's on four scenes,
because the greedy has no cost in its objective and the budget penalty
F4 froze was applied to the floor fit only.

## What F7 establishes, and what changes in the tooling

1. The hybrid selector without templates is the fire workflow's
   default from here, with two projected small-gap classes fitted per
   step: `rgre_puffs.hybrid_pick`. That choice of two over one is made
   on this run's reported variant, not on a bar, and is recorded as
   such: it costs one repair a step and recovers most of the remaining
   lost steps.
2. With the puff grammar the search is part of the limit. F3's
   "vocabulary, not search" was a fact about the column grammar. The
   puff grammar's greedy path ends 0.11 above its joint floor, and the
   next question about the cheap fire is whether a joint polish from
   the greedy terminal recovers that at a fraction of the
   differential-evolution cost, which is a search question, not a
   grammar one.
3. The look stays where F4 left it: a property of the objective.

No rescue, no second run on the scored scenes. Nothing above is edited
after the run.
