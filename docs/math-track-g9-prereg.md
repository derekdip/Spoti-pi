# G9: the grammar with planted grounding. Preregistration (frozen before any scored case is run)

The web viewer of the runtime (`docs/gait3d-runtime.md`,
`poc/results/damaged-gait-player.html`) showed the fitted 3D gaits
sliding: the bodies moved forward at the fitted speed while their
feet barely swung, and only the one-legged hop read as a gait. That
is a defect of the grammar's grounding, not of the fit. The root
moved at a fitted `speed` and the lowest part of the body was put on
the floor, so a stance foot skated under the body; no consumer
measured foot slip, so the fit never had to match stride to speed.
Under the planted grounding described below, the G7 intact state
moves at 0.003 m/s: all of its 0.37 m/s was the free parameter.

## The change

`poc/gait3d/grammar3d.py`: the root's forward motion comes from the
part that is on the floor. Frame by frame, the lowest part is planted
where it touched down and the root moves so that it does not slide;
while nothing is down (a lift), the root keeps its last velocity; a
new part touching down is planted where it lands. `speed` is no
longer a parameter: it is what the legs (or the arms, on the legless
body) produce from stride and cadence. The rhythm class has four
parameters. The runtime player (`poc/gait3d/runtime.py`) uses the same
rule, integrating across state blends and body switches, and re-plants
after a body switch. Nothing else in the grammar, the consumers or the
procedure changes; the consumers still have a speed block, so the fit
must now produce the teacher's speed with its stride.

This is a grammar change, so V0 is refitted, the redundancy screen and
the exclusivity table are rerun, and the procedure is G7's on the same
fourteen cases with the same designed classes and the same pilot.

## V0

`poc/gait3d/v0.py` on the planted grammar, 27 base parameters, two
seeds, the better kept (`poc/results/gait3d_v0.json`, from
`gait3d_v0_planted_s0.json`, error 0.354; the other seed 0.394; the
G7 V0 is kept as `gait3d_v0_g7.json`). The default state's error is
1.469 under planting, against 0.609 before: a default gait that does
not stride now does not move. The fitted state moves at 0.368 m/s
from its stride against the teacher's 0.356, with the speed block at
0.04; hip amplitude 0.195 rad, cadence 0.425 Hz, stance fraction
0.84, the legs 0.85 rad from in phase, torso pitch and roll
oscillations of 0.26 and 0.29 rad, arm swing 0.24 rad. Per block:
contact 0.33, coupling 0.29, stance 0.39, joint statistics 0.54,
asymmetries 0.32 and 0.24, height 0.02, orientation 0.59, lateral
0.00, rhythm 0.30, reach 0.12, phase-binned pose 0.62
(`gait3d_compare_intact_v0.png`). The fit follows the teacher's own
gait, a shuffle with long double support and the hips nearly in
phase (its left-right hip correlation is +0.15); that is the
teacher's, and the base reproduces it without sliding.

## Redundancy screen and exclusivity table

Redundancy screen (`poc/results/gait3d_redundancy_check_g9.*`): class
steps stiff 0.79, limp 0.49, hold 0.68, vault 0.74, weak 0.82, higher
than on the G7 grammar (0.71, 0.51, 0.63, 0.64, 0.81) except limp:
with planting, any parameter that changes the stride changes the
speed, and the base has more of every sided change at first order.

Exclusivity table (`poc/results/gait3d_dictionary_check_g9.*`): eight
pairs over a half where the G7 grammar had none. Weak is absorbed by
stiff 0.81, hold 0.81, lateral 0.77, legs 0.75 and limp 0.65; legs
absorbs stiff 0.55 and hold 0.53; weak absorbs stiff 0.52. Per body
at V0: the left locked knee, stiff and limp tied at 22.6 percent
each on the correct side, stiff with a gap of 0.00 and limp 0.08,
hold 13 on the wrong side; the left stump, torso at 48 percent, then
vault at 33 and limp at 31 on the correct side, hold at 2; the
legless body, arms at 26 and torso next, vault under a percent. The
planted grounding couples every class to the speed and contact
blocks through the stride, and the classes are less separable for
it. This is recorded, not repaired: the round tests the grounding, and
a grammar whose classes separate under planting is the next design
question, not this run's.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g9_pilot.*`): torso (fitting 0.780 to 0.647, held-out
mean 0.776 to 0.648, both runs lower), then declined: arms rejected by
the guard on speed (with planting, an arm refit on a body that moves
on its arms changes its speed), rhythm by the held-out test, torso
and vault spent. Excluded from every bar. No change was made after
it.

## Bars (frozen)

As G7's (`poc/g9_score.py`, committed with this document, comparing
with `poc/results/g7.json`).

- **K1, identity.** First impairment repair names class and side on
  `>= 2` of 3 design bodies, within two on 3 of 3, mirrors 2 of 2.
- **K4, growth generalises.** Mean held-out error below V0's on `>= 7`
  of 9 damaged bodies.
- **K2, consumers.** None beyond tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.
- **K5, no slip.** Reported, not a bar, since it holds by
  construction: the planted part's ground speed while down is zero on
  every terminal state; the teacher's own figure is reported beside
  it, measured the same way from its contacts.

## Predictions

K4 holds, as in G7 and G8: the rule does not depend on the grounding.
K2 holds; K3 is open (weak is absorbed by everything, and the base
may or may not pass a weak repair on the weak hips). K1 is predicted
to **fail**: stiff and limp tie on the left locked knee at V0, so the
first impairment repair there is a coin toss between the designed
class and its neighbour; on the stumps vault and limp are within two
percent; on the legless body vault is under a percent. Design 1 or 2
of 3 first, mirrors 1 of 2, letter C. The round's claim is K5: the
terminal states do not slide, which holds by construction, and the
web viewer rebuilt from them is the check a viewer makes.

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails.
- **D**: neither.

K2, K3 and K5 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
grammar, the consumers, the rules or the budget after this commit.
Results go in `docs/math-track-g9-results.md`; nothing above is
edited after the run.
