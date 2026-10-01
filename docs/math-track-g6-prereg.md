# G6: the grammar without the hop class, ranges untouched. Preregistration (frozen before any scored case is run)

G5 (`docs/math-track-g5-results.md`) removed the hop class and widened
two base ranges, and the widening coarsened the fitter's grid sweeps
on every legs and torso refit, so the run could not say what removing
the class costs. G6 is G5 with the ranges exactly as G4's: `knee_off`
(0, 1.5), `bob_amp` (0, 0.1). The record supports that: G4's one
terminal state with hop on has a base twin at `knee_off` 1.40, `freq`
1.91, `bob_amp` 0.014, inside those ranges.

## What is the same and what is not

Everything is G4's except that hop is not a class: the grammar's
five remaining impairment classes, the base and its ranges, V0, the
consumers, the fourteen fitting teachers with two held-out runs each,
the two rules, the candidate order, six steps. `poc/g6_experiment.py`
is G5's script with the output paths; `poc/g6_score.py` is committed
with this document. The exclusivity table is not rerun: with the
ranges restored, every pair of the remaining classes is G2's table
(`poc/results/gait_dictionary_check.json`) with the hop rows removed,
since no other class's fit depends on hop's presence.

The fits are deterministic grid sweeps and the tests are
deterministic, so on every case where G4's path never applied hop the
G6 path must be G4's to the digit: the only change in the candidate
table is that hop is absent, and on those cases hop was either never
the first admissible candidate or was rejected before another
candidate was taken (the right stump, where the guard rejected it at
step zero and legs followed). One case applied hop: the left one-leg
body, at step zero. That case alone is the test of the class.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g6_pilot.*`): vault then torso, fitting 0.356289 and
held-out mean 0.342442, G4's pilot to six decimals. Excluded from
every bar.

## Bars (frozen)

Thirteen scored cases as G5: three design bodies with a designed
class, two mirrors, nine damaged bodies, four controls.

- **K6, reproduction.** All twelve scored cases other than the left
  one-leg body reproduce G4's repair list and G4's terminal fitting
  error to `1e-6`.
- **K5, the class's cost.** The left one-leg body's terminal fitting
  error is not above G4's (0.461) by more than one percent of its V0
  error (0.571).
- **K1, identity**, as G5: first `>= 2` of 3, within two 3 of 3,
  mirrors 2 of 2.
- **K2, K3, K4** as G5: within tolerance `>= 7` of 9; `<= 4`
  impairment repairs on the controls; mean held-out below V0 on `>= 7`
  of 9.

Reported: the left one-leg body's steps in full (drops, rejections),
the right stump's path, rejections by reason.

## Predictions

K6 holds, 12 of 12; if it fails, something other than hop and the
ranges differs between G4 and G6, and that is the finding. K1, K2,
K3, K4 hold as in G4 with the one-leg bodies moved out of the identity
count (3 of 3, 3 of 3, 2 of 2). K5 is the open one, and the
prediction is that it **fails**: in G5 the left one-leg body took legs
and torso and then had rhythm, vault and arms rejected by the held-out
test, and reaching the twin of G4's hop state needs `knee_off` and
`freq` to move together, which no single base class does. Hop's value
on that body was as a coordinated move, not as a direction.

## Outcome (frozen, exclusive)

Determined by K6 and K5.

- **A**: both hold. Hop was a duplicate in every sense; the grammar
  has five impairment classes and the one-leg gait is a base state
  the greedy path reaches.
- **B**: K6 holds, K5 fails. G5's damage was the grid, and hop was a
  coordinated move of base parameters the greedy base does not find:
  no direction, but search value. The predicted letter.
- **C**: K5 holds, K6 fails.
- **D**: neither.

K1 to K4 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
grammar, the rules or the budget after this commit. Results go in
`docs/math-track-g6-results.md`; nothing above is edited after the
run.
