# G4 results: outcome A. The mean of two held-out runs keeps the design identity, names the damage on two mirrors of three, generalises on every damaged body, and admits repairs that one of the two runs rejects

Preregistration: `docs/math-track-g4-prereg.md`, frozen at commit
`7507bc3`, unchanged. Raw output: `poc/results/g4.json`, `g4.log`,
`g4_report.md` (the frozen scorer's output, `poc/g4_score.py`), and
one picture per case (`poc/results/g4_*_checked.png`). Fourteen cases
run, thirteen scored (the declared pilot excluded), six steps, 441
seconds on three workers, scored against G3's one-run path on the same
fitting teachers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity kept | first `>= 3` of 4, within two `>= 3` of 4, mirrors `>= 2` of 3 | **4 of 4, 4 of 4, 2 of 3** | pass |
| K2 consumers | none beyond its tolerance on `>= 7` of 9 | **9 of 9** (none worse at all: 2 of 9) | pass |
| K3 controls | `<= 5` impairment repairs on the four controls | **4** | pass |
| K4 growth generalises | mean held-out error below V0's on `>= 7` of 9 | **9 of 9** (both runs lower: 6 of 9) | pass |

K1 and K2 hold, so the letter is **A**, the predicted letter, with the
mirrors at the predicted 2 of 3 and K3 and K4 as predicted.

## What each bar means

**The right stump names its damage, and the guard did it (K1).** In
G3 the right stump took hop first, then three more classes, and its
kneel was rejected four times by the one held-out run. In G4 hop was
again the top fitting candidate at step zero and was rejected by the
per-consumer guard, on reach, whose tolerance on this body is 0.02:
the two teacher runs agree on the reach of the stump to within that,
and the hop fit moved it further. The guard fired once in the whole
run, here. The legs refit followed, then kneel on the right side at
step one with both held-out runs lower, then the step was declined,
rhythm and hop lowering neither run. The right locked knee is as
before. The right one-leg body again takes four base refits and no
hop, with every class then spent; the base absorbs that run's hop,
as G2's table said it could and as G3 found, and no acceptance rule
touches that.

**Every consumer loss is inside the teacher's spread (K2).** Nine of
nine damaged bodies are within tolerance on every consumer; two of
nine are worse on none, one fewer than G3 in proportion. The bar is
the one G3 argued for, and it holds without the guard doing anything
on eight of the nine.

**The controls grew one class fewer (K3).** The intact body's first
run took torso and vault, both held-out runs lower on vault, and its
weak class, which G3's one run had admitted, was rejected with one
run of two lower. The right weak hip took the same three classes as
in G3, each on both runs or on the mean. Four impairment repairs
against G3's five.

**Growth generalises on the mean, and one run of one body says no
(K4).** Nine of nine damaged bodies end below V0 on the mean of the
two held-out runs; six of nine on both runs. The three that improve
on one run only: the two short shanks, whose second run moves by a
thousandth either way, and the left stump, whose seed-1 run goes from
0.475 to 0.490 while its seed-2 run goes from 0.515 to 0.241. The
left stump's three runs are not one gait: seed 2 resembles the fitting
run and seed 1 does not, and the mean followed seed 2. G3's single
held-out run on that body was seed 1, which is why G3's stump barely
generalised (0.475 to 0.470) and G4's does on the mean.

## Reported

- Repairs applied per case, median 3, as G3. Rejections: 32 by the
  held-out test, 85 spent, 1 by the guard.
- Of 43 applied repairs, 31 lowered both held-out runs and 12 lowered
  one; none lowered neither, which the mean rule cannot admit. The
  twelve include the intact body's second run taking legs at step zero
  with its seed-0 run rising from 0.300 to 0.361 and its seed-2 run
  falling from 0.502 to 0.403; G3's one held-out run, seed 0, had
  rejected that repair. V0 was fitted on the intact body's seed-0 run,
  so that run scores 0.300 against V0 where the other two score 0.49
  and 0.50: V0 is seed 0's walk, and the intact body's runs differ
  from each other by as much as a damaged body's do from the walk.
- The value of the applied repair against the best fitting drop is
  1.00 in median.
- The short-shank bodies take one legs refit each and decline, as in
  G2 and G3; the geometry carries the limp.

## A scorer defect, named

The frozen scorer's line "designed class arrives as impairment repair
N" prints G4's position counting from one and G3's from zero (the
G3 figure in brackets is a list index). The right stump's "1 (G3:
[3])" means first in G4 and fourth in G3. No bar reads this line.

## What G4 establishes

1. Two held-out runs and the measured guard together name the damage
   on the mirrors that a single run could not, without losing the
   design bodies or admitting more on the controls. With G3, the
   growth rule for the gait workflow is: fit on one run, accept on
   the mean of two others, guard each consumer by the runs' own
   distance.
2. The mean of two is a looser test than either run: twelve of
   forty-three repairs pass on one run's say-so. Where the teacher's
   runs are not one gait, as on the left stump, the mean follows the
   run that resembles the fitting run. A rule that requires both runs
   to improve would have rejected those twelve and, on the record
   here, both of the left stump's base refits after kneel; whether
   that is better is a question for a body with more runs.
3. The right one-leg body's hop is a grammar question, now confirmed
   under three selection rules (G2, G3, G4): the base's lift can
   express a one-legged hop, so the class is never worth a percent
   after the base has refitted. The exclusivity table predicted this
   before G2; the fix is in the grammar, a flight phase the base
   cannot produce, and is not attempted here.
4. The teacher's runs of an undamaged body differ from each other by
   as much as damage does. Every bar that compares a student to a
   teacher in this case is bounded by that, and the walk base V0 is
   one run's walk.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
