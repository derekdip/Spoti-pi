# G5 results: outcome D. The run does not test the change it was for: widening two base ranges coarsened every legs and torso grid sweep, and that moved the paths on bodies that never hopped

Preregistration: `docs/math-track-g5-prereg.md`, frozen at commit
`793cc91`, unchanged. Raw output: `poc/results/g5.json`, `g5.log`,
`g5_report.md` (the frozen scorer's output, `poc/g5_score.py`), and
one picture per case (`poc/results/g5_*_checked.png`). Fourteen cases
run, thirteen scored (the declared pilot excluded), six steps, 354
seconds on three workers, scored against G4 on the same fitting
teachers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity kept | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **2 of 3, 2 of 3, 1 of 2** | **fail** |
| K5 nothing lost with hop | both one-leg terminals within one percent of V0 of G4's | **0 of 2** (0.496 against 0.461; 0.258 against 0.245) | **fail** |
| K2 consumers | none beyond its tolerance on `>= 7` of 9 | 9 of 9 | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | 2 | pass |
| K4 growth generalises | mean held-out error below V0's on `>= 7` of 9 | 8 of 9 | pass |

K1 and K5 both fail, so the letter is **D**. The predicted letter was
A. The prediction failed for a reason the preregistration named and
misjudged: "the only difference being the legs and torso grids over
the widened bounds".

## What happened

**The grids.** A class fit sweeps each parameter over seven points
spread across its range, then seven more around the best
(`rgre_gait._sweep`). Widening `knee_off` from 1.5 to 2.0 and
`bob_amp` from 0.1 to 0.35 spread those seven points over a third
more and three and a half times more, so every legs and every torso
refit in the run landed on different values from G4's. Nothing else
in the procedure changed for a body that cannot hop, and the paths
changed on most of them:

- The left locked knee took legs, and after that refit the
  impairment ranking was limp 0.126, kneel 0.075, stiff 0.067, where
  in G4 stiff had been second at 0.185 before the refit and first
  after it. Stiff was never named; limp on the correct side was.
- The right locked knee had legs and stiff both rejected by the guard
  at step zero, on height and on stance, took torso, then legs, then
  kneel on the right. Stiff was never named.
- The right stump had legs rejected by the guard on reach at step
  zero, took limp on the right, then kneel on the right, so kneel is
  within two and the mirror bar is met by that body and lost on the
  locked knee.
- The guard fired five times against once in G4, all on base refits
  or on stiff, all on consumers whose tolerance is small (reach,
  height, stance): the coarser sweeps overshoot where the finer ones
  did not.
- The intact body's first run took torso and then every class was
  spent, vault included, which in G4 was worth a step after the finer
  torso refit.

**The one-leg bodies.** The left one, the body that named hop in G2
to G4, took legs and torso and ended at 0.496 where G4's hop, torso,
legs ended at 0.461. Vault, arms and rhythm were each rejected by
the held-out test with one run of two lower. G4's hop terminal has a
base twin at `knee_off` 1.40, `freq` 1.91 and `bob_amp` 0.014; to
reach it the base needs the legs and rhythm classes to move together,
and each alone did not lower the held-out mean. The right one took
the same four repairs as in G4 and a fifth, and ended 0.013 above
G4's terminal on the coarser grids.

## A check made after the run, and named as such

G4's only terminal state with hop on, the left one-leg body's, has a
twin whose `knee_off` (1.40), `bob_amp` (0.014) and `freq` (1.91)
all lie inside the old ranges. The widening that caused the grid
change was not needed for anything on the record. Three G4 terminals
(both stumps, the right one-leg body) sit at `knee_off` exactly 1.5,
the old limit, so that bound was binding on those bodies; whether a
wider bound with the same grid spacing would help them is a separate
question, not asked here.

## What G5 establishes, and what it does not

1. The algebra stands and is prior to the run: every hop state has an
   exact base twin (`poc/gait/hop_equivalence.py`, at commit
   `388686e`), so hop owns no direction. G5 was to show that removing
   it costs nothing; it did not show that, because it changed the
   grids as well.
2. Grid resolution is tied to range in this fitter, so a range is not
   a free choice: widening one changes every fit of that class. The
   preregistration saw the grids as the only difference and predicted
   they would not matter. That is the defect in this freeze.
3. There is a second hypothesis the run cannot separate from the
   first: hop may be a coordinated move of base parameters that the
   greedy base path does not find one class at a time, even though it
   is no direction of its own. The left one-leg body's rejections are
   consistent with that and with the grid. G6, hop removed and the
   ranges left exactly as G4's, separates them: every case that never
   fitted hop in G4 must then reproduce G4 to the digit, and the left
   one-leg body alone is the test.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
