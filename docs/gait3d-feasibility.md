# 3D gait feasibility: the planar teacher's question asked of a body that can fall sideways

A feasibility build, not a preregistered experiment, following
`docs/gait-feasibility.md`. The 2D case ended with a grammar of five
impairment classes, a growth rule with no constants, and four lessons
for the next body (`docs/math-track-g6-results.md`): run the twin,
redundancy and exclusivity checks on the grammar before any teacher is
fitted; keep an exact-combination class as a fitter move and not a
label; choose the teacher's cost so the base gait does not already
carry an impairment's signature; treat ranges as part of the fitter.

The body (`poc/gait3d/biped3d.py`) is the planar biped with a free
root, hip abduction and ankle roll on each leg, and box feet: 14
actuators intact, 21 coordinates. The planner (`poc/gait3d/mpc3d.py`)
is the planar one with the pitch term replaced by the torso's up and
forward axes, a lateral-velocity term, and a speed target of 0.6 m/s
instead of 0.8: the planar teacher at 0.8 was airborne a quarter of
the time, which made flight the base's and left the hop class nothing
to own. Same morphologies, same damage, one cost for every body. Five
seconds per body, metrics over the last three.

## What would count, written before the run

| morphology | expected gait | counts as feasible if |
|---|---|---|
| intact | walk | speed over 0.35 m/s; lateral drift under 1 m over the run; mean tilt under 0.35 rad; double support at least 15 percent; flight under 10 percent |
| weak hip, locked knee, short shank | limp | speed over 0.25 m/s; drift under 1.5 m; tilt under 0.5 rad; stance asymmetry at least 0.1 |
| stump | limp on the stump | speed over 0.2 m/s; stump and foot alternating; asymmetry at least 0.15 |
| one leg | hop or crutch on an arm | speed over 0.15 m/s; flight or a hand in contact at least 20 percent |
| no legs | crawl on the arms | speed over 0.15 m/s; a hand in contact at least 30 percent; torso centre below 0.6 m |

The 2D thresholds are lowered by a little for the lower speed target.
"Feasible" means the motion is one a person would name as the row
does; a run that meets the numbers and does not look like the word
fails the row. The strips show a side view and a front view.

## The iterations, in order

1. **The planar cost, transposed.** Intact body, 5 s: it walks off
   upright, then drops to its knees at 2.5 s and shuffles forward on
   thighs and feet at 0.47 m/s with the head at 1.15 m against its
   standing 1.55 m. The head-height term at weight 3 costs that
   posture half a unit a step, and every upright attempt the sampler
   saw fell, which costs more. Kneeling is a stable optimum of this
   cost in three dimensions where it was not in two.
   (`gait3d_iter1_*`)

2. **Head weight 3 to 20.** (a) Intact body, 5 s, nothing else
   changed: an upright walk. Speed 0.37 m/s, drift 0.25 m, tilt 0.22
   rad, feet alternating 75 percent of the time, double support 15
   percent, flight 10 percent, stance asymmetry 0.19 (the right foot
   down more), the feet crossing the midline in the front view. The
   row's numbers are met at the margin on flight. (b) The same with
   256 samples and noise 0.25 instead of 160 and 0.35: the same speed at a lower crouch
   (torso 1.07 m), on the left foot 81 percent of the time and the
   right 24, asymmetry 0.54, a skip rather than a walk, at half again
   the compute. The 160-sample planner with noise 0.35 is kept, and
   head weight 20 becomes the default.
   (`gait3d_iter2a_*`, `gait3d_iter2b_*`)

3. **All seven design bodies with head weight 20.** Intact: the walk
   of 2a. Weak left hip: a skip on the left foot (down 65 percent
   against the right's 16, flight 24 percent) at 0.46 m/s for two
   seconds, then it drops to its knees at 4 s and finishes kneeling;
   the row's numbers are met and the last second is not a limp.
   Locked left knee: a stiff-leg walk, upright, double support 27
   percent, asymmetry 0.09 against the row's 0.1. Short left shank: a
   skipping limp on the long leg (down 71 percent), asymmetry 0.62.
   Stump: stands and steps for two seconds, falls at 2.8 s, and
   kneel-steps on the stump and the foot at 0.51 m/s from then on,
   the 2D stump's gait after a fall. One leg: hops on the remaining
   leg, upright (torso 1.11 m, tilt 0.27) at 0.40 m/s, facing
   backwards (yaw 2.5 rad): the heading term penalised only sideways
   facing, so turning round was free. No legs: an arm crawl for two
   seconds, hands down 54 percent, torso at 0.42 m, then a roll onto
   the pelvis with the arms in the air. Two defects to fix: the
   heading term, and the kneeling attractor that takes the weak hip
   and, after a fall, the stump. (`gait3d_iter3_*`)

4. **Head weight 40, on the two bodies that knelt or nearly did.**
   Weak left hip: an upright walk for the whole run, torso 1.12 m,
   both feet down 56 percent, double support 27 percent, flight 15
   percent, no asymmetry at all; the weak hip no longer limps and no
   longer kneels, which is what the 2D weak hip did too. Intact: still
   a walk, faster (0.49 m/s), bouncier (flight 26 percent), asymmetry
   0.28. Head weight 40 becomes the default: a body that stays up is
   worth more to the teacher than a body that limps for two seconds.
   (`gait3d_iter4_*`)

5. **Heading term fixed, head weight still 20, on the two bodies that
   turned.** The term was the squared sideways component of the
   torso's forward axis, which is zero facing backwards; it is now the
   squared distance of that axis from +x. One leg: hops facing
   forward (yaw 0.34 rad) at 0.38 m/s, drifting 0.58 m to the side,
   and goes down at 4.5 s. No legs: a hand-and-pelvis crawl at 0.28
   m/s, torso at 0.35 m, hands down 50 percent, stalling in the last
   second. (`gait3d_iter5_*`)

6. **Head weight 40 and the heading fix, all seven design bodies.**
   The teacher's configuration. Intact: a walk at 0.36 m/s, drift
   0.14 m, tilt 0.27 rad, double support 23 percent, flight 6
   percent. Weak left hip: a walk with a mild limp, asymmetry 0.21,
   double support 20 percent, upright throughout. Locked left knee: a
   stiff-leg walk, the left foot down 77 percent, asymmetry 0.34.
   Short left shank: a skipping limp on the long leg, asymmetry 0.67,
   flight 18 percent. Stump: a hop on the right foot with the stump
   held forward and off the floor (thigh contact 3 percent), 0.48 m/s,
   flight 33 percent; at head weight 40 the body no longer kneels on
   the stump as it did at 20 and as the 2D stump did, so this row's
   "stump and foot alternating" is not met and the gait is a one-leg
   hop with a stump. One leg: a hop, upright (torso 1.15 m), 0.32 m/s,
   facing forward, no drift. No legs: a crawl on the hands with the
   pelvis dragging, 0.34 m/s, hands down 74 percent, torso at 0.30 m.
   (`gait3d_iter6_*`; these runs are the seed-0 teachers,
   `gait3d_teacher_*_s0_qpos.npy`.)

7. **A gait clock in the cost, after the runtime viewer.** The web
   player of the fitted states (`docs/gait3d-runtime.md`) showed the
   teacher's own gait for what it is: a shuffle with the hips nearly
   in phase (left-right hip correlation +0.15), still arms, feet
   crossing. The owner asked for a walk that reads as one. Iteration
   7 adds a gait prior, which the earlier iterations deliberately did
   not have: each foot follows a half-wave height reference at 1 Hz,
   the two half a cycle apart, and each shoulder a swing against its
   own leg on the same clock (`mpc3d.gait_cost`); bodies without a
   foot have no foot term. (a) Weights 40 on the feet and 0.5 on the
   arms, horizon 1.0 s: the intact body walks more upright with
   visible alternating steps, double support 34 percent, at 0.40
   m/s, but the terms are too small against the rest of the cost (an
   8 cm miss costs a quarter of a unit a step against hundreds): the
   shoulders never move (spread 0.01 rad) and the feet lift 26 to 39
   cm, from the walk's dynamics rather than the reference. (b) The
   same with a 1.5 s horizon: slower (0.23 m/s), a fall at 2.5 s, costs
   twice as high, at half again the compute; with the same 160
   samples a longer horizon dilutes the search, and it is dropped. (c) Weights 600 and 20, horizon
   1.0 s: faster (0.55 m/s) with the feet
   alternating 70 percent of the time, and not clean: the hips are
   still correlated (+0.30), only the right arm swings (spreads 0.02
   and 0.22 rad), the body yaws 0.9 rad, and the planner's cost is
   unstable. A sampling planner with 160 samples cannot follow a clock
   on four joints while balancing with the rest. (d) The prior as a
   full reference instead: the planner tracks every joint of a clean
   walk from the grammar's own clock (the default grammar state at 1
   Hz, legs half a cycle apart, arms against the legs), and does what
   physics allows: upright (tilt 0.17 rad) at 0.38 m/s with
   double support 41 percent, and still not the reference: the hips
   correlate +0.27, the shoulders do not move (spread 0.02 rad), the
   body yaws 0.67 rad. With 160 samples and one elite over fourteen
   actuators, the arm terms are lost in the noise of balancing. (e)
   The arms scripted from the clock when the body has legs (the
   sampler plans the legs and torso only) and the leg reference at
   weight 20: the body walks sideways (1.4 m of drift
   for 0.05 m forward: at weight 20 the joint reference outweighs
   heading and speed), and the arms still stop: they swing in the
   first second (shoulder spread 0.09 rad) and are still by the last
   (0.01). That is not the planner. The hands hang at pelvis height,
   the pelvis box is 0.13 m wide and the arms sit 0.14 m from the
   midline, so the hand sphere catches on the pelvis within a second
   and stays there. Every teacher up to this one had still arms
   because of a collision, not a cost. (f) Shoulders at 0.20 m, the
   arms scripted from the clock, the leg reference at weight 5:
   the arms swing for the whole run (shoulder
   spread 0.21 and 0.22 rad, the same in the last second), which
   settles the arms; the legs are still not a walk: the hips
   correlate +0.55, one leg kicks out sideways at 2.8 s, 0.29 m/s.
   The planner samples around its previous plan, so the reference
   only pulls through the cost. (g) Sampling around the reference:
   each replan's nominal is the clean walk at the current clock plus
   the shifted deviation the last replan found, and the lateral
   joints (hip abduction, ankle roll) get a third of the noise:
   an upright walk at 0.39 m/s with the arms
   swinging against the legs for the whole run (shoulder spread 0.20
   and 0.21 rad), the feet alternating 68 percent of the time with
   double support 24 percent and flight 8 percent, tilt 0.19 rad, no
   sideways drift. The hips are still only weakly anti-phase
   (correlation +0.10) and the feet lift high (22 and 31 cm, the
   reference asks 8): a sampling planner tracks the clock's rhythm
   and not its amplitudes. This is the teacher of iteration 7: the
   clean-walk reference from the grammar's own clock, the arms
   scripted on it where the body has legs, sampling centred on it,
   shoulders at 0.20 m. It has a gait prior, which iterations 1 to 6
   did not, and it says so here. (`gait3d_iter7*_*`; the teacher set
   is rerun with it, the iteration-6 set kept under
   `poc/results/teacher3d_iter6/`.)

## Result against the table (iteration 6; iteration 7's teacher is recorded below it)

| morphology | expected | got | numbers | by eye |
|---|---|---|---|---|
| intact | walk | walk | met | walk |
| weak hip | limp | walk with a mild limp | met (asymmetry 0.21) | a walk; the limp is in the numbers more than the eye |
| locked knee | limp | stiff-leg walk | met (asymmetry 0.34) | stiff-leg limp |
| short shank | limp | skipping limp on the long leg | met (asymmetry 0.67) | limp |
| stump | limp on the stump | hop on the good leg, stump held up | speed met; alternation not met | hop, not a stump-limp |
| one leg | hop or crutch | hop | met (flight 9 percent, airborne) | hop |
| no legs | crawl | hand-and-pelvis crawl | met (hands 74 percent, torso 0.30 m) | crawl |

Six rows of seven as written; the stump row is a hop, which the head
weight that keeps every other body upright buys at the price of the
stump's kneel. The 3D teacher exists: six iterations against the
planar build's seven, one cost, about 140 seconds per run. The
question it was built for, whether a body that can fall sideways
gives the same family of gaits from the same cost, is answered yes,
with the stump the one gait that changed.

## What is carried to the grammar

- The base gait has little flight (6 percent on the intact body):
  flight will belong to the impairments here, hop's in particular,
  and the twin check (`docs/math-track-g6-results.md`) says whether
  any class is a combination of the base before a fit is made.
- Three seeds per body from the start (`poc/gait3d/teacher.py`), so
  the growth rule is G4's without a new teacher run mid-arc.
- The consumers gain lateral terms: drift, roll, yaw, hip abduction
  and ankle roll statistics; the phase-binned pose block reads every
  present joint as before.

## The teacher set

Thirty-six runs, `poc/results/gait3d_teacher_{morph}_s{seed}_qpos.npy`
for the seven design bodies and the five right-side mirrors at seeds
0, 1 and 2 (`gait3d_teacher_all.json`, `.log`), about four minutes a
run with two in parallel. The seed-to-seed variability the 2D case
met is here too and larger on the bodies that have two ways to go:
the left stump hops with the stump up at seeds 0 and 2 and
kneel-steps on it at seed 1 (thigh down 37 percent); the legless body
crawls on its hands at all three seeds but at seed 1 with the torso
turned over (tilt 2.7 rad). The intact body walks at all three seeds
(speed 0.32 to 0.37, airborne 6 to 17 percent), the locked knees at
all six, the one-leg bodies hop at all six, facing forward. Which run
is the fitting run and which are held out is the growth rule's
business, not the teacher's.
