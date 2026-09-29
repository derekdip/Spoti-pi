# G6 results: outcome B. Without hop, twelve cases of twelve reproduce G4 to the digit, and the left one-leg body ends above G4's terminal: the class owned no direction and was worth a coordinated move the greedy base does not make

Preregistration: `docs/math-track-g6-prereg.md`, frozen at commit
`5c759a6`, unchanged. Raw output: `poc/results/g6.json`, `g6.log`,
`g6_report.md` (the frozen scorer's output, `poc/g6_score.py`), and
one picture per case (`poc/results/g6_*_checked.png`). Fourteen cases
run, thirteen scored (the declared pilot excluded), six steps, 412
seconds on three workers, scored against G4 on the same fitting
teachers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K6 reproduction | all 12 non-hop cases reproduce G4's repairs and terminal to `1e-6` | **12 of 12** | pass |
| K5 the class's cost | left one-leg terminal within one percent of V0 of G4's 0.461 | **0.477**, 2.8 percent of V0 above | **fail** |
| K1 identity kept | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | 3 of 3, 3 of 3, 2 of 2 | pass |
| K2 consumers | none beyond its tolerance on `>= 7` of 9 | 9 of 9 | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | 4 | pass |
| K4 growth generalises | mean held-out error below V0's on `>= 7` of 9 | 9 of 9 | pass |

K6 holds and K5 fails, so the letter is **B**, the predicted letter,
with K1 to K4 as predicted.

## What each bar means

**G5's damage was the grid, all of it (K6).** With the ranges put
back, every case whose G4 path never applied hop takes the same
repairs and reaches the same terminal error to six decimals, the
right stump included, where G4's guard had rejected hop at step zero
and legs followed. Everything G5 lost, the stiff class on both locked
knees and the guard firing five times, came from the seven-point
sweeps being laid over wider ranges, and nothing from the absence of
the class.

**Hop was worth 0.016 on one body, as a move (K5).** The left one-leg
body, the one case whose G4 path used hop, took legs and torso and
then declined, with arms, vault and rhythm each rejected by the
held-out test. It ends at 0.477 against G4's 0.461 on the fitting
run and 0.288 against 0.279 on the held-out mean. G4's hop state has
a base twin at `knee_off` 1.40 and `freq` 1.91, well inside the
ranges; the legs class moves `knee_off` and the rhythm class moves
`freq`, and neither move on its own lowers the held-out mean, so the
greedy path never makes them together. Hop made them together in one
fit. It owned no direction (`poc/gait/hop_equivalence.py`, exact on
every body) and it had search value: a coordinated move of base
parameters that one class at a time does not find. That is the
linearisation gap in another form: the value of a repair can lie in a
combination the ranking, and here the greedy step, does not see.

**Identity, consumers, controls and generalisation are G4's (K1 to
K4).** With the one-leg bodies moved out of the identity count, every
design body and both mirrors name their damage first, and the other
three bars read exactly as G4's, which K6 guarantees.

## What G6 establishes

1. The gait grammar has five impairment classes, each with a
   direction of its own on the exclusivity table (G2's, hop rows
   removed), and the one-leg gait is a base state. The workflow's
   growth rule is G4's: fit on one run, accept on the mean of two
   held-out runs, guard each consumer by the runs' own distance. On
   this teacher it names the damage on every design body and both
   mirrors and generalises on nine damaged bodies of nine.
2. A class can be worth having for search and not for identity. Hop
   named nothing that the base does not, and it reached a state the
   base's greedy refits do not reach, worth three percent of V0 on
   one body. Where a class is an exact combination of base
   parameters, the honest use is as a move offered to the fitter and
   not as a label on the terminal state; the same check that found
   the redundancy (an exact twin) says which classes those are.
3. A range is part of the fitter. The sweep's resolution follows the
   range, so a bound is a modelling choice with a cost in every fit of
   that class (G5); widening one is not free and needs its own test.
4. The pre-build checks for the next grammar are now three, all run
   before a teacher is fitted: the twin check where a class is an
   algebraic combination of the base, the redundancy screen for
   first-order duplicates (with its threshold limit named), and the
   exclusivity table for absorption between classes.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
