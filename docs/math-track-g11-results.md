# G11 results: outcome C, as predicted. With a consumer that reads where the feet go, the fitted states swing their feet at the teacher's speed and step forward; growth generalises on nine of nine; the names are gone from the locked knees

Preregistration: `docs/math-track-g11-prereg.md`, frozen at commit
`fa194ad`, unchanged. Raw output: `poc/results/g11.json`, `g11.log`,
`g11_report.md` (the scorer's output, `poc/g11_score.py`), one picture
per case (`poc/results/g11_*_checked.png`), and the web viewer rebuilt
from these states (`poc/results/damaged-gait-player.html`). Fourteen
cases run, thirteen scored, six steps, 867 seconds on three workers,
scored against G10, the same teacher and grammar without the block.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **0 of 3, 0 of 3, 1 of 2** | **fail** |
| K4 growth generalises | mean held-out below V0's on `>= 7` of 9 | 9 of 9, both runs lower on 8 of 9 | pass |
| K2 consumers | none beyond tolerance on `>= 7` of 9 | 9 of 9 (worse on some block: 9 of 9) | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | 2 (limp on the left weak hip, weak on the intact body's second run) | pass |

K1 fails and K4 holds: **C**, the predicted letter.

## The round's claim (K6): the feet travel

Swing speed of each foot while off the floor, fitted state against
teacher, m/s:

| body | left foot | right foot |
|---|---|---|
| intact | 1.61 / 1.65 | 1.26 / 1.00 |
| weak left hip | 1.43 / 1.07 | 1.45 / 1.55 |
| locked left knee | 1.13 / 1.90 | 0.99 / 0.99 |
| short left shank | 0.71 / 0.96 | 0.93 / 0.88 |
| weak right hip | 1.59 / 1.59 | 1.44 / 1.24 |
| locked right knee | 0.73 / 1.25 | 1.77 / 3.17 |
| short right shank | 0.79 / 0.36 | 1.03 / 0.91 |
| left stump | (stump) | 0.80 / 0.69 |
| right stump | 1.48 / 1.77 | (stump) |
| left one-leg | (none) | 0.86 / 1.33 |
| right one-leg | 0.00 / 0.69 | (none) |

On every walking body and both stumps the swing speeds are within a
factor of two of the teacher's, most within a third, where the G10
states were at a third of the teacher's speed and backward on a third
of the frames. The travel block's error falls from V0 on eleven cases
of thirteen. Step lengths are longer than the teacher's on most
bodies (the intact body 0.30 and 0.20 m against 0.15 and 0.12): the
fit buys swing speed with stride. The exception is the right one-leg
body, whose fitted state never lifts its foot (swing 0.00, its ground
speed 0.000): it moves by the planting rule alone, at the teacher's
speed, and reads as a slide. The left one-leg body hops.

The emergent speeds match the teacher's on every body but the right
locked knee (0.29 against 0.39), within 0.05 m/s elsewhere. The
viewer (`damaged-gait-player.html`, version 4) shows bodies that step
forward.

## What it cost

**Identity.** No design body names its class first or within two:
the left locked knee takes rhythm and arms and stops; the stumps
take vault first (33 percent at V0 against limp's 31); the legless
body takes arms. The right locked knee names weak, then stiff. The
table said this before the run: stiff was under 3 percent on the left
knee at V0, and four class pairs were over a half, the travel block
coupling every class through the feet. The short shanks, which have
no designed class, name limp first on the correct side, both sides,
as the block's own reading of a limp.

**Terminal errors** are above G10's on eleven cases of thirteen,
which is the new block's residual and not a like-for-like comparison.
The guard fired fifteen times against four in G10, on the travel and
contact blocks.

## What G11 establishes

1. The runtime now steps forward: the fourth consumer fix of the 3D
   case, after the clock, the support counts and the coupling (V0
   pilots), and the planting constraint (G9). Each was a defect a
   viewer saw at once and no block measured, and each was fixed by
   giving the fit the quantity a viewer reads.
2. Every consumer added for the viewer has cost the classes their
   separability: planting coupled them through the speed (G9), the
   travel block through the feet (G11). The consumers a viewer wants
   and the consumers that name damage by class are not the same set,
   and the arc's naming results (G7, G8) stand on the earlier set.
3. The growth rule is untouched by any of it: nine of nine and both
   held-out runs on eight, under a fourteenth block it had never seen.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
