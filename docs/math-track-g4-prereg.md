# G4: acceptance against two held-out runs of the teacher. Preregistration (frozen before any scored case is run)

G3 (`docs/math-track-g3-results.md`) established that acceptance
against a second run of the same teacher generalises the growth on
every damaged body and keeps the design-body identity, and left three
things on record: the right stump's kneel was rejected four times by
the one held-out run before it passed; the strict consumer clause
failed inside the teacher's own run-to-run spread, with the measured
guard never firing; and the bodies used as controls have structure a
second run confirms. G4 changes one thing: the held-out side of the
acceptance rule goes from one run to the mean of two. The grammar, the
consumers, V0, the fourteen fitting teachers, the guard's form, the
spent rule and the candidate order are G3's.

## What is not changed, and why

The plan put to the owner after G3 also had impairment classes offered
before base refits, so that a base refit could not absorb hop on the
right one-leg body. G3's own record, read before this document was
written, shows that ordering would have named the wrong class on a
design body: at step zero on the left stump the fitting drops were hop
0.32, limp 0.28, kneel 0.24, and it was the legs refit at 0.38, taken
first, that left kneel as the top impairment at step one. Offering
impairments first trades the stump's identity for the one-leg body's,
so it is dropped. The right one-leg body's hop is absorbed by the base
on that run, as G2's exclusivity table predicted a third of it could
be; no selection rule recovers a class the base can express, and that
is a grammar question, left open here.

## The third run

Every body gets a third teacher run, seed 2, by `poc/gait/teacher.py
third` (twelve runs, the same planner and cost). The fitting run of
each case is the one G2 and G3 fitted (seed 0, and seed 1 for the two
reseeds); the other two runs are held out.

## The rules

**Held-out acceptance.** A repair fitted on the fitting run is applied
only if it lowers the mean of the errors against the two held-out
runs. How many of the two it lowers (0, 1 or 2) is recorded for every
applied repair.

**Per-consumer guard.** As G3, with the tolerance the mean, over the
two held-out runs, of the distance between the fitting run and that
run on the consumer at V0's scale.

Candidates in order of fitting drop, the first that passes the spent
rule (one percent of the current error), the held-out test and the
guard is applied, declined when none passes. Six steps.
`poc/g4_experiment.py`, scorer `poc/g4_score.py`, committed with this
document.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g4_pilot.*`), run to check the path executes. It is
excluded from every bar by the scorer, which G3's scorer did not do
for G3's pilot: without that case G3's K2 reads 3 of 9 and 9 of 9 and
its K4 9 of 9, and its letter is unchanged.

Pilot result: vault, then torso, each lowering both held-out runs;
fitting error 0.724 to 0.356, held-out runs 0.728 and 0.739 to 0.379
and 0.305, nothing rejected. No change was made after it.

## Bars (frozen)

Nine damaged bodies (the pilot excluded), four design bodies, three
mirrors, four controls. Scored against G3's one-run path on the same
fitting teachers (`poc/results/g3.json`).

- **K1, identity is kept.** G2's three bars: the first impairment
  repair names the class and side on `>= 3` of the four design
  bodies, within two on `>= 3` of four, and within two on `>= 2` of
  the three mirrors.
- **K2, consumers.** At the terminal, against V0 on the fitting run,
  no consumer is worse beyond its tolerance on `>= 7` of the nine
  damaged bodies. The strict clause is reported and not a bar: G3
  showed every loss inside the teacher's run-to-run spread, and a loss
  inside that spread is not evidence.
- **K3, controls.** The four control cases add at most 5 impairment
  repairs in total, G3's count. The premise that these bodies have
  nothing for an impairment class to name is wrong (G3), so the bar is
  that the two-run rule admits no more than the one-run rule did.
- **K4, growth generalises.** The terminal state's mean held-out error
  is below V0's on `>= 7` of the nine damaged bodies. How many bodies
  improve on both held-out runs is reported.

Reported: repairs applied per case against G3's, rejections by reason,
the number of held-out runs each applied repair lowered, the step at
which each designed class arrives, the value of the applied repair
against the best fitting drop, the short-shank bodies, pictures of
teacher against terminal.

## Predictions

K1 holds with the mirrors at 2 of 3: the right stump's kneel within
two impairment repairs once the held-out side averages two runs, the
right locked knee as before, the right one-leg body's hop absorbed as
before. K2 holds (G3 had 10 of 10 within tolerance). K3 holds. K4
holds. The predicted letter is A.

## Outcome (frozen, exclusive)

Determined by K1 and K2.

- **A**: both hold. Two held-out runs are the acceptance rule for the
  gait workflow.
- **B**: K1 holds, K2 fails.
- **C**: K2 holds, K1 fails. Two runs are not enough either.
- **D**: neither.

K3 and K4 are reported under every letter.

No rescue, no second run on the scored cases, no change to the rules,
the tolerance's definition or the budget after this commit. Results go
in `docs/math-track-g4-results.md`; nothing above is edited after the
run.
