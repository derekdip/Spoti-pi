# G11: the foot-travel consumer. Preregistration (frozen before any scored case is run)

The web viewer of the G10 states showed bodies that took steps and
seemed to step back. Measured, the fitted states' swing feet moved
forward through the air at 0.3 to 0.5 m/s where the teachers' swing
at 1 to 2.3 m/s, and backward on a quarter to a half of the swing
frames. Every consumer block is body-relative: joint statistics,
contacts, root speed, posture, coupling. None looks at where a foot
goes in the world, so a state that lifts a foot and puts it down
where it was matches every block while the planted root carries the
body forward. As with the sliding (G9), a defect a viewer sees at
once is a consumer the fit never had.

## The change

`poc/gait3d/rgre_gait3d.py` gains a fourteenth block, **travel**: for
every stepping part (feet, thighs, hands; not the pelvis), its
forward world speed while off the floor and the forward distance
between its consecutive touchdowns, both zero for a part that never
lifts or never lands. On the intact teacher the feet swing at 1.65
and 1.00 m/s with steps of 0.15 and 0.12 m; the G10 fitted state read
0.56 and 0.56 m/s with steps of 0.30 and 0.23. The block is scaled by
its own rms as the others are. Nothing else changes: G10's teacher,
grammar, rules, cases, designed classes and pilot.

This is a consumer change, so V0 is refitted, the redundancy screen
and the exclusivity table are rerun, and the run is G10's procedure.

## V0

`poc/gait3d/v0.py` on the iteration-7 intact teacher with fourteen
blocks, two seeds, the better kept (`poc/results/gait3d_v0.json`,
from `gait3d_v0_travel_s1.json`, error 0.340; the other 0.345; the
G10 V0 is kept as `gait3d_v0_g10.json`). The default state's error is
1.360. The fitted state is an alternating walk: the legs 3.05 rad
apart, cadence 0.84 Hz, stance fraction 0.55, hip amplitude 0.29 rad,
knee 0.56, arms 0.43 rad, moving at 0.36 m/s from its stride against
the teacher's 0.42. Its feet swing forward at 1.58 and 1.44 m/s
against the teacher's 1.65 and 1.00, with steps of 0.30 and 0.23 m
against 0.15 and 0.12: the travel block is at 0.24. The other blocks:
contact 0.33, coupling 0.52, stance 0.21, joint statistics 0.53,
asymmetries 0.18 and 0.02, speed 0.13, height 0.01, orientation
0.18, lateral 0.14, rhythm 0.12, reach 0.17, phase-binned pose 0.85
(`gait3d_compare_intact_v0.png`). Against G10's V0 the walk is
slower in cadence and longer in stride; the coupling and pose blocks
are worse and the travel block is what the fit bought.

## Redundancy screen and exclusivity table

Redundancy screen (`poc/results/gait3d_redundancy_check_g11.*`): class
steps stiff 0.94, limp 0.85, hold 0.80, vault 0.94, weak 0.82, the
highest of any grammar so far: the travel block reads foot motion,
which every leg parameter moves.

Exclusivity table (`poc/results/gait3d_dictionary_check_g11.*`): four
pairs over a half where G10 had none: legs absorbs limp 0.70, limp
absorbs weak 0.64, legs absorbs weak 0.63, legs absorbs hold 0.57.
Per body at V0: the left locked knee, lateral 24 percent, stiff 2.7
on the correct side, nothing else above 0.3; the short shank, limp 59
percent on the correct side with a gap of 0.00, its oracle; the left
stump, vault 33 and limp 31 on the correct side, hold 15 on the
right; the legless body, arms 33. The travel block couples the
classes through the feet as planting coupled them through the speed
(G9), and it is recorded, not repaired: this round is for the viewer.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g11_pilot.*`): torso, then rhythm (arms rejected by the
held-out test), both runs lower each time; fitting 0.726 to 0.522,
held-out mean 0.797 to 0.551. Excluded from every bar. No change was
made after it.

## Bars (frozen)

As G10's (`poc/g11_score.py`, committed with this document, comparing
with `poc/results/g10.json`, the same teacher and grammar without the
block).

- **K1, identity.** First impairment repair names class and side on
  `>= 2` of 3 design bodies, within two on 3 of 3, mirrors 2 of 2.
- **K4, growth generalises.** Mean held-out error below V0's on `>= 7`
  of 9 damaged bodies.
- **K2, consumers.** None beyond tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.
- **K5, reported.** Ground speed near the floor and emergent speed
  against the teacher's, per case.
- **K6, reported, the round's claim.** Each foot's swing speed and
  step length at the terminal against the teacher's, per case, and
  the travel block's error against V0's. The claim is that the swing
  speeds land within a factor of two of the teacher's on the walking
  bodies, which is what the viewer can tell apart; it is reported,
  not barred, because the block is new and its scale is its own rms.

## Predictions

K4 holds. K2 holds. K3 open. K1 fails: stiff is worth under 3 percent
on the left locked knee at V0 and is predicted spent before it is
named on both knees; the stumps have limp on the correct side within
two percent of vault, a coin toss, and are predicted to name limp
within two on at most one side; the legless body is predicted not to
name vault. Design 0 or 1 of 3 first, mirrors 0 or 1 of 2, letter C.
The round's claim (K6) is predicted to hold: swing speeds within a
factor of two of the teacher's on the walking bodies, as V0's already
are, and the viewer shows bodies that step forward.

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails.
- **D**: neither.

K2, K3, K5 and K6 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
teacher, the grammar, the consumers, the rules or the budget after
this commit. Results go in `docs/math-track-g11-results.md`; nothing
above is edited after the run.
