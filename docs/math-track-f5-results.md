# F5 results: outcome A by the frozen tree, and a control that says the premise was wrong

Preregistration: `docs/math-track-f5-prereg.md`, frozen at commit
`b248643`, unchanged. Raw output: `poc/results/f5.json`, `f5_run.log`,
`f5_report.md` (the frozen-bar scorer, `poc/f5_report.py`, committed
before any glow correlation had been seen), `f5_compare.png` with the
crops `f5_compare_a.png` and `f5_compare_b.png`, and
`poc/results/law_control.log`. One run, nine scenes, 1 h 49 min.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| B1 motion | median sway ratio in [0.5, 1.5], median phase error `<= 45` deg | 0.73, 34 deg | pass |
| B2 shape | median glow correlation `>= 0.70` | 0.800 | pass |
| B3 decisions | burn `<= 5%`, passable `<= 5%`, missed alight `<= 25%` | 11.1%, 7.4%, 20% | **fail** |
| B4 cost | `<= 20` parcels on every fresh scene | max **16** | pass |
| B5 transfer | ratio in [0.5, 1.5], phase error `<= 60` deg on both | fast_gust 140% / 31 deg; strong_gust **38%** / 34 deg | **fail** |
| B6 paired | error no worse than F4 by more than 10 percent | +11.8%, +1.1%, +11.5% | **fail** |

The tree is exclusive on B1 and B2, both pass, so the letter is **A**.
The letter is not the result. Two of this document's findings say the
letter should not be believed, and both were produced by controls this
preregistration asked for.

## Per scene, fresh

| scene | gust | V0 | floor | sway model / teacher | ratio | phase err | glow corr | burn wrong | passable wrong | parcels | greedy / floor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gust_shelf | 1.8 m/s @ 0.7 Hz | 0.787 | 0.519 | 6.3 / 10.1 cm | 63% | 31 deg | 0.80 | 11.1% | 7.4% | 12 | 0.71 |
| fast_gust | 1.6 m/s @ 1.4 Hz | 0.624 | 0.461 | 3.5 / 4.7 cm | 73% | 54 deg | 0.66 | 4.6% | 4.1% | 16 | 0.26 |
| strong_gust | 2.6 m/s @ 0.7 Hz | 0.795 | 0.496 | 11.3 / 16.8 cm | 68% | 34 deg | 0.80 | 11.4% | 9.4% | 11 | 0.55 |
| gust_twin | 1.5 m/s @ 0.7 Hz | 1.219 | 0.402 | 3.9 / 5.1 cm | 76% | 109 deg | 0.85 | 1.9% | 2.0% | 4 | 0.84 |
| bed_chain | 2.0 m/s @ 0.7 Hz | 0.833 | 0.532 | 9.6 / 12.5 cm | 77% | 26 deg | 0.81 | 15.0% | 12.7% | 12 | 0.70 |

`bed_chain` also misses 20 percent of alight frames across three beds,
against the column grammar's 28 to 67 percent on one or two.

## The control that overturns the premise

F5 exists because F4's gusted scenes were fitted as the mean of a
swaying flame, and because the old drift law carried each parcel's
birth phase upward, which is thirty times too much phase gradient
against the teacher's measured 0.07 rad/m. The arithmetic is right. The
conclusion drawn from it, that the old law therefore could not sway,
is wrong.

`poc/fire_law_control.py` fits **both laws** on the bedless pilot by
identical code with identical settings, so nothing but the law differs:

| on `gusty`, both fitted | error | sway tracked | phase error | v_rise | parcels |
|---|---|---|---|---|---|
| old law, F4's | 0.602 | **106%** | **29 deg** | 0.37 | 12 |
| new law, F5's | **0.464** | 67% | 37 deg | 0.77 | 11 |

The old law tracks the sway better on both measures. So **B1 passing is
not evidence the fix worked**: the law it replaced would have passed
B1 more comfortably. What the new law did buy is 23 percent of error
and a rise speed that doubled, neither of which is what it was frozen
for.

The reason the phase-gradient argument fails to predict behaviour is
visible once stated: the coarse glow is dominated by the youngest,
brightest parcels near the source, which share a phase under either
law. The phase gradient acts on the upper plume, which contributes
little glow, so a centroid-based sway measure barely discriminates the
two laws. The diagnosis measured a real property of the law and
attributed to it a defect it does not cause.

**What the visual defect actually is.** The pictures
(`f5_compare_a.png`) show the teacher's plume climbing from a low
lean at 0.8 s to a tall tapering tongue by 3.2 s, while both fits look
the same at all four times: a leaning stub. The fitted `v_rise` is 0.43
to 0.61 m/s on four of the eight fitted scenes against a measured front
speed of 2.25 m/s, so **P1 fails** as well. The fire leans correctly
and is far too short, and height, not sway, is what the glow is paying
for.

## The transfer test, which failed for a reason worth having

The pilot's state, applied unchanged where only the cause differs:

| | teacher sway | model sway | ratio | phase error | error vs V0 |
|---|---|---|---|---|---|
| fast_gust, frequency doubled | 4.7 cm | 6.6 cm | 140% | 31 deg | 0.692 vs 0.624, worse |
| strong_gust, amplitude 1.6x | 16.8 cm | 6.4 cm | **38%** | 34 deg | 0.555 vs 0.795, better |

The model's sway is 6.4 to 6.6 cm in both, which is the pilot's own
6.4 cm: it does not respond to the cause at all in amplitude. The
reason is mine. The gust **frequency** was made a property of the cause
that the grammar reads; the gust **amplitude** was left a fitted
parameter, so nothing told the model the wind had changed and the
amplitude could not transfer by construction. Refitting on
`strong_gust` reaches 68 percent, against 38 transferred, which
separates the two explanations cleanly: the law can produce the larger
sway and was never told to.

The frequency result is the sharper one. The teacher's sway halves when
the frequency doubles, 9.5 to 4.7 cm, which is amplitude proportional
to `1/omega`. The model's does not move. Common phase across height
with amplitude proportional to `gust / omega` is exactly a rigid
translation by the **air's displacement**, so the law both diagnostics
point at is

```
offset = response * (gust_amp / omega) * sin(omega t - lag) * height factor
```

with `gust_amp` and `omega` read from the cause and one dimensionless
fitted `response`. That is strictly more cause-driven than what was
frozen here, which is this project's own thesis, and it is the next
thing to build rather than a fourth source shape.

## The bar that was too weak, and it is mine

B2 passes at 0.800. The measure check frozen in the preregistration
says a **perfect static blob** reaches 0.85 on these scenes. The model's
median shape agreement is therefore **below what a model with no motion
at all achieves**, and it passed the bar. The bar was set at 0.70 from a
pilot that was itself below the static reference, so it could not have
failed a shaped-but-motionless model and did not test what its name
says. That is the fourth bar or outcome-tree defect across five fire
freezes, and unlike the earlier three it was avoidable: the static
reference was measured and printed in the same preregistration that set
the bar at 0.70.

A further defect in the frozen text: B1 reads "the four gusted fresh
scenes" when all five fresh scenes carry a gust. It was scored over all
five, which is what the words mean, and the count is wrong.

## What did work

**The parcel budget.** Maximum 16 parcels per source across five fresh
scenes, against F4's 32, and on the pilot the budgeted fit reached
0.464 with 11 parcels where the unbudgeted achievability fit reached
0.518 with 18. Putting cost in the objective cost nothing and bought a
better basin. `gust_twin` reached the best fresh-scene error in the run,
0.402, on four parcels.

**The two optimisers converged.** On three fresh scenes DE and the
two-stage Powell agreed to within 0.001, where F4 saw disagreements up
to 15 percent. The floor is being measured more reliably than at any
earlier point in the arc.

**Decisions on the simple scenes.** `gust_twin` 1.9 and 2.0 percent,
`fast_gust` 4.6 and 4.1: both inside B3's 5 percent. The failures are
the shelf and bed scenes at 11 to 15 percent, the same split every fire
experiment has found.

## The cross-evaluation rule selects against motion

The look fit tracks the sway better than the standard fit on seven of
nine scenes and loses on error on eight of nine, often by under one
percent (`strong_gust`: 89% of the teacher's sway at 0.4985 against 68%
at 0.4960). The frozen rule picks by error, so it discarded the
better-moving state on eight of nine scenes. `gust_twin` is the
exception where the look fit is worse on motion too, so the pattern is
strong and not universal.

`windy`'s look fit reports a 437 percent sway ratio, which is
meaningless: `windy` has no gust, so the teacher's sway at that
frequency is numerical noise and the ratio divides by it. The sway
measure should have been reported only where `gust_amp > 0`.

## The paired re-measurement

| scene | F4 error | F5 error | change | F5 parcels | F4 parcels |
|---|---|---|---|---|---|
| ignition | 0.481 | 0.538 | +11.8% | 13 | 26 |
| full | 0.470 | 0.475 | +1.1% | 11 | 7 |
| windy | 0.329 | 0.367 | +11.5% | 6 | 6 |

B6 fails, and the comparison is confounded: F5 reduced the DE budget
from 30 generations to 22 to fit the run in the time available, so this
is not like-for-like on search effort. On `ignition` the error rose 12
percent while the parcel count halved, which is the budget doing its
job. On `windy` the parcel count is identical in both, so neither the
budget nor the cost explains its 11.5 percent, and **P2 fails**: the
claim that the two laws agree for a steady wind is not supported at the
precision this compares at.

A paired motion comparison on `ignition` and `full`, each state under
the law it was fitted with, gives F4 118 and 158 percent against F5's
103 and 86. Those are bedded scenes where a bed lighting downwind moves
the glow centroid on its own, which is why the bedless pilot exists and
why the pilot control above is the one to believe.

## What F5 establishes

1. The quasi-static law is a 23 percent error improvement on the pilot
   and doubles the fitted rise speed, and it is **not** the reason the
   fire sways; the law it replaced sways slightly better.
2. The visual defect is plume **height**, not sway. Fitted rise speeds
   sit near 0.5 m/s against a measured 2.25, and the pictures show a
   leaning stub against a climbing tongue.
3. The representation is not yet cause-driven where it matters: the
   gust amplitude is fitted, so nothing about the cause's strength
   reaches the model, and the sway has no `1/omega` dependence where the
   teacher's has exactly that. One law fixes both.
4. Cost belongs in the objective. It halved the parcel count and cost
   no accuracy.
5. A bar set from a pilot can be weaker than a reference measured in
   the same document. B2 passed a model that is worse than a static
   blob at the thing B2 is named for.

No rescue and no second run on the fresh scenes. Nothing above is
edited after the run.
