# G7 results: outcome C, as predicted. The growth rule carries to 3D on every damaged body and both of its held-out runs; the naming carries on the locked knees and the left stump and not on the legless body or the right stump

Preregistration: `docs/math-track-g7-prereg.md`, frozen at commit
`d9820d3`, unchanged. Raw output: `poc/results/g7.json`, `g7.log`,
`g7_report.md` (the frozen scorer's output, `poc/g7_score.py`), and
one picture per case in side and front view
(`poc/results/g7_*_checked.png`). Fourteen cases run, thirteen scored
(the declared pilot excluded), six steps, 634 seconds on three
workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **2 of 3, 2 of 3, 1 of 2** | **fail** |
| K4 growth generalises | mean held-out error below V0's on `>= 7` of 9 | **9 of 9**, both runs lower on 9 of 9 | pass |
| K2 consumers | none beyond its tolerance on `>= 7` of 9 | 9 of 9 | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | **0** | pass |

K1 fails and K4 holds, so the letter is **C**, the predicted letter.
The prediction named the legless body as the reason and it was; the
right stump is the second reason and was not predicted.

## What each bar means

**Growth generalises, on both held-out runs of every damaged body
(K4).** Nine of nine damaged bodies end below V0 on the mean of the
two runs they were never fitted to, and on each run separately. The
2D case at its best (G4, G6) had six of nine on both runs. The 3D
teachers have more run-to-run spread than the 2D ones and the rule
rejected more for it (70 held-out rejections against 26 to 35 in 2D),
and what it admitted holds. The controls took no impairment class at
all (K3): the intact body and both weak hips were fitted by base
refits alone, where in 2D the intact body grew vault and the weak hip
three classes.

**Identity carries where the class owns the damage (K1).** Both
locked knees name stiff first, on the correct side, at step zero,
with the second candidate less than half its drop. The left stump
names limp on the stump's side as its first impairment repair, after
a torso and an arm refit, and its picture is a one-legged hop with
the stump held forward, which is the teacher's gait.

**Where it does not (K1).** The legless body took arms and torso and
then every class was spent; vault was worth 5 percent at V0 and 0.3
after the two refits, as the exclusivity table predicted and the
preregistration said. The 3D legless teacher crawls on its hands with
the pelvis dragging and almost no lift; in this grammar that is the
base prone, and vault, the one thing the base cannot do, is not what
the body does. The right stump took the lateral class first, at 49
percent, then arms, then vault at 4 percent and hold on the right at
3, and limp, worth 27 percent at V0 on the correct side, was never
above 3 percent after the lateral refit. On the left stump the torso
refit came first and left limp at 36 percent; on the right the
lateral refit absorbed the stump-side asymmetry limp would have
named. The two stump teachers are not the same gait (the left hops
with a third of its time airborne, the right shuffles on its foot 87
percent of the time), and which base class refits first decides what
is left for a sided class to name.

**Consumers (K2).** Nine of nine within tolerance, two of nine worse
on nothing. The guard fired three times, all on the left one-leg
body, on height and contact timing.

## Reported

- Repairs per case, median 4; rejections 85 spent, 70 held-out, 3
  guard; 35 applied repairs of 50 lowered both held-out runs, 15 one.
- The left one-leg body took stiff on its remaining leg first (6
  percent, both runs lower): the hopping leg keeps its knee straight,
  and stiff is the class that says so. It has no designed class and
  the repair is reported. Its lateral class was the oracle at every
  step (27 to 48 percent) and was never admissible: rejected by the
  guard once and by the held-out test after, the two other runs of
  that body swaying differently from the fitting run.
- The short shanks took legs (both) and vault and torso (the left);
  neither took limp, as in 2D, where the geometry carries the limp.
- The value of the applied repair against the best fitting drop is
  1.00 in median.

## What G7 establishes

1. The growth rule built in 2D (fit on one run, accept on the mean of
   two held-out runs, guard each consumer by the runs' own distance)
   carries to the 3D body without change and generalises on every
   damaged body and both of its held-out runs, while adding nothing
   to the undamaged ones. That is the workflow claim, and it held on
   the first 3D run.
2. Identity carries where the class owns what the body does: the
   locked knee's stiffness on both sides, the stump's limp on the
   side it was designed on. It does not carry where the teacher's
   gait is the base in another posture (the legless crawl) or where a
   base refit reaches the asymmetry first (the right stump). The
   exclusivity table predicted the first before the run; the second
   is the order of the base refits, which the table does not read.
3. The pre-build checks earned their place: the first draft's two
   twin terms were found and removed before the freeze, the table's
   per-body oracles said which identities to expect, and the run
   agreed on every body but one.
4. Open on the record: the stump's naming depends on which base class
   refits first, and a class whose damage a base refit can reach is
   named or not by that order. A rule that fits impairment classes on
   top of a full base refit rather than one class at a time would
   test whether the right stump's limp survives; that is a change to
   the procedure and is not made here.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
