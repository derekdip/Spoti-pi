# G10: the iteration-7 teacher. Preregistration (frozen before any scored case is run)

The web viewer of the G9 states showed a runtime that no longer slid
and a gait that was the teacher's: a shuffle with the hips nearly in
phase and still arms. The owner asked for a walk that reads as one.
`docs/gait3d-feasibility.md`, iteration 7, rebuilt the teacher in
seven recorded probes: a clean-walk reference from the grammar's own
clock in the cost, the arms scripted on that clock where the body has
legs, sampling centred on the reference, and the shoulders moved out
to 0.20 m after the hands were found to catch on the pelvis box,
which is why every earlier teacher had still arms. The teacher now
has a gait prior, which the earlier teachers did not; the case's
question is unchanged: whether the grammar's growth fits what physics
does to that walk under damage, generalises across runs, and names
the damage.

G10 is G9's procedure, grammar (planted grounding, five impairment
classes) and consumers on the iteration-7 teacher set: twelve bodies,
three runs each, the same fourteen cases and designed classes, the
same pilot. V0 is refitted on the new intact teacher; the redundancy
screen and exclusivity table are rerun.

## The teacher set

Thirty-six runs, `poc/results/gait3d_teacher_{morph}_s{seed}_qpos.npy`,
about five minutes each with two in parallel (`gait3d_teacher_all.*`,
the legless rerun in `gait3d_teacher_nolegs_rerun.log`). The intact
body walks at all three seeds (0.22 to 0.39 m/s, arms swinging) and
so do the weak hips, the locked knees (stiff-leg, the locked foot down
longer) and the short shanks (on the long leg, the short foot down 7
to 36 percent); the stumps hop on the good foot at four seeds of six
and kneel-step on the stump at two; the one-leg bodies hop, one seed
falling to its hands; the legless body crawls on hands and pelvis at
0.38 to 0.47 m/s under iteration 6's planner. Per run:

- intact_s0: speed 0.39, tilt 0.19, stance foot_l 0.66, foot_r 0.50, airborne 0.08
- intact_s1: speed 0.37, tilt 0.21, stance foot_l 0.52, foot_r 0.56, airborne 0.15
- weak_hip_left_s0: speed 0.39, tilt 0.28, stance foot_l 0.61, foot_r 0.64, airborne 0.06
- intact_s2: speed 0.22, tilt 0.22, stance foot_l 0.63, foot_r 0.54, airborne 0.19
- weak_hip_left_s1: speed 0.44, tilt 0.25, stance foot_l 0.64, foot_r 0.72, airborne 0.04
- weak_hip_left_s2: speed 0.31, tilt 0.18, stance foot_l 0.76, foot_r 0.65, airborne 0.05
- locked_knee_left_s0: speed 0.33, tilt 0.18, stance foot_l 0.76, foot_r 0.52, airborne 0.06
- locked_knee_left_s1: speed 0.38, tilt 0.18, stance foot_l 0.86, foot_r 0.55, airborne 0.02
- short_shank_left_s0: speed 0.39, tilt 0.25, stance foot_l 0.53, foot_r 0.54, airborne 0.21
- locked_knee_left_s2: speed 0.27, tilt 0.23, stance foot_l 0.51, foot_r 0.65, airborne 0.10
- short_shank_left_s1: speed 0.16, tilt 0.27, stance foot_l 0.34, foot_r 0.60, airborne 0.15
- short_shank_left_s2: speed 0.24, tilt 0.28, stance foot_l 0.31, foot_r 0.65, airborne 0.11
- stump_left_s0: speed 0.15, tilt 0.29, stance foot_r 0.37, thigh_l 0.78, airborne 0.10
- stump_left_s1: speed 0.36, tilt 0.37, stance foot_r 0.85, airborne 0.15
- noleg_left_s0: speed 0.34, tilt 0.36, stance foot_r 0.81, airborne 0.19
- stump_left_s2: speed 0.24, tilt 0.30, stance foot_r 0.87, airborne 0.13
- noleg_left_s1: speed 0.24, tilt 0.48, stance foot_r 0.42, hand_l 0.33, hand_r 0.10, pelvis 0.50, airborne 0.14
- noleg_left_s2: speed 0.46, tilt 0.38, stance foot_r 0.75, thigh_r 0.08, airborne 0.24
- nolegs_s0: speed 0.47, tilt 1.99, stance hand_l 0.76, hand_r 0.52, pelvis 0.16, airborne 0.12
- nolegs_s1: speed 0.38, tilt 1.11, stance hand_l 0.51, hand_r 0.51, pelvis 0.44, airborne 0.13
- nolegs_s2: speed 0.44, tilt 1.07, stance hand_l 0.53, hand_r 0.45, pelvis 0.39, airborne 0.14
- weak_hip_right_s0: speed 0.29, tilt 0.29, stance foot_l 0.79, foot_r 0.53, airborne 0.11
- weak_hip_right_s1: speed 0.36, tilt 0.19, stance foot_l 0.65, foot_r 0.63, airborne 0.13
- weak_hip_right_s2: speed 0.39, tilt 0.25, stance foot_l 0.71, foot_r 0.58, airborne 0.12
- locked_knee_right_s0: speed 0.43, tilt 0.24, stance foot_l 0.60, foot_r 0.78, airborne 0.06
- locked_knee_right_s1: speed 0.26, tilt 0.21, stance foot_l 0.71, foot_r 0.67, airborne 0.05
- locked_knee_right_s2: speed 0.28, tilt 0.21, stance foot_l 0.55, foot_r 0.79, airborne 0.04
- short_shank_right_s0: speed 0.27, tilt 0.25, stance foot_l 0.36, foot_r 0.72, airborne 0.19
- short_shank_right_s1: speed 0.27, tilt 0.26, stance foot_l 0.32, foot_r 0.70, airborne 0.19
- short_shank_right_s2: speed 0.23, tilt 0.30, stance foot_l 0.86, foot_r 0.07, airborne 0.14
- stump_right_s0: speed 0.20, tilt 0.36, stance foot_l 0.93, airborne 0.07
- stump_right_s1: speed 0.40, tilt 0.33, stance foot_l 0.82, airborne 0.18
- stump_right_s2: speed 0.16, tilt 0.31, stance foot_l 0.36, thigh_r 0.59, airborne 0.20
- noleg_right_s0: speed 0.25, tilt 0.36, stance foot_l 0.76, airborne 0.24
- noleg_right_s1: speed 0.37, tilt 0.32, stance foot_l 0.78, airborne 0.22
- noleg_right_s2: speed 0.39, tilt 0.29, stance foot_l 0.83, airborne 0.17

## V0

`poc/gait3d/v0.py` on the iteration-7 intact teacher (seed 0), 27
base parameters under planted grounding, two seeds, the better kept
(`poc/results/gait3d_v0.json`, from `gait3d_v0_iter7_s0.json`, error
0.322; the other 0.327; the G9 V0 is kept as `gait3d_v0_g9.json`).
The default state's error is 1.235. The fitted state is a striding
walk: hip amplitude 0.43 rad, knee amplitude 1.0, cadence 0.51 Hz,
stance fraction 0.52, the legs 1.77 rad apart, arms swinging 0.32
rad, and it moves at 0.317 m/s from its stride against the teacher's
0.416 (the speed block at 0.23 is the largest gap after contact
timing 0.58 and the phase-binned pose 0.62). Per block: coupling
0.30, stance 0.39, joint statistics 0.40, asymmetries 0.17 and 0.03,
height 0.01, orientation 0.28, lateral 0.22, rhythm 0.04, reach 0.13
(`gait3d_compare_intact_v0.png`). The teacher's shoulders are
anti-phase (correlation -0.77, the scripted swing) and its hips
weakly so (+0.10).

## Redundancy screen and exclusivity table

Redundancy screen (`poc/results/gait3d_redundancy_check_g10.*`): class
steps stiff 0.66, limp 0.75, hold 0.84, vault 0.81, weak 0.51.

Exclusivity table (`poc/results/gait3d_dictionary_check_g10.*`): no
pair over a half; the largest are legs absorbing limp 0.47, stiff
0.46 and hold 0.41. Per body at V0: the left locked knee, lateral 24
percent, then stiff 8 on the correct side with a gap of 0.01, limp 3;
the left stump, legs 16, hold 15 and weak 11 on the right (the
stepping leg), limp 8 also on the right, stiff nothing; the short
shank, limp 32 percent on the correct side, its oracle; the legless
body, torso 17, rhythm 15, vault 13, arms 12. Under the new teacher
the left stump kneel-steps on the stump (its thigh is down 78 percent
of the time), so the class the preregistration carried over from G7,
limp with the stump as the short side, describes a hop that this
teacher's seed-0 run does not do; the classes that fit it put their
side on the stepping leg. The designed classes are kept as G7's so
that the run is comparable, and the stump's is predicted to fail.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g10_pilot.*`): torso, then arms, both runs lower each
time; fitting 0.580 to 0.526, held-out mean 0.622 to 0.533. Excluded
from every bar. No change was made after it.

## Bars (frozen)

As G9's (`poc/g10_score.py`, committed with this document, comparing
with `poc/results/g9.json` where the cases are the same bodies on the
old teacher, so only as a reference and not a like-for-like).

- **K1, identity.** First impairment repair names class and side on
  `>= 2` of 3 design bodies, within two on 3 of 3, mirrors 2 of 2.
- **K4, growth generalises.** Mean held-out error below V0's on `>= 7`
  of 9 damaged bodies.
- **K2, consumers.** None beyond tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.
- **K5, reported.** Ground speed of the parts near the floor, and the
  emergent speed against the teacher's, per case.

## Predictions

K4 holds: the rule has generalised on nine of nine in every 3D round.
K2 holds. K3 is open. K1 fails: the left stump's designed class is
worth 8 percent on the wrong side at V0 and the right stump's teacher
hops, so neither stump names limp on its side within two; the locked
knees name stiff after a lateral refit if the held-out test admits
it, and the legless body names vault within two at 13 percent against
the base classes' 12 to 17. Design 1 or 2 of 3 first, mirrors 0 or 1
of 2, letter C. The round's claim is in the viewer: the fitted states
walk, limp, hop and crawl with swinging arms, which no earlier teacher
gave.

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails.
- **D**: neither.

K2, K3 and K5 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
teacher, the grammar, the consumers, the rules or the budget after
this commit. Results go in `docs/math-track-g10-results.md`; nothing
above is edited after the run.
