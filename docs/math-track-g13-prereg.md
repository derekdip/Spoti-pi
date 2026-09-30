# G13: the grammar's classes as edits on the teacher's own cycle. Preregistration (frozen before any scored case is run)

After G11 the locomotion case had two descriptions of a damaged body
(`docs/gait3d-runtime.md`, last section): the fitted grammar state,
which names the damage and generalises to held-out runs and which a
viewer faulted four times, and the teacher's own cycle, which plays
right and names nothing. For a VR pipeline the clip is a run of the
physics teacher per body, and damage that combines (a locked knee
and a weak hip on the other side) or arrives mid-motion has no clip.
The question of this round: do the grammar's classes carry as edits
of the clip, and for which damages. A damage the edits reach is a
dial on one clip; a damage they do not reach is a clip of its own,
and the runtime switches.

## The change

`poc/gait3d/clip_edit.py`. The base is the intact teacher's mean
cycle (seed 0, 32 phase bins, `poc/gait3d/cycle_runtime.py`). A
grammar state S is read as an edit of it relative to a fixed
reference R, the G11 V0 walk base (`poc/results/gait3d_v0.json`),
each parameter acting on the clip's own curves the way it acts in
the grammar's closed form:

- an amplitude scales the clip's oscillation by S/R (the knee's
  flexion above its minimum; the hip's, ankle's, abduction's and
  arm's swing about their means), with the impairments' terms in
  the same places as in the grammar (stiff scales the knee and adds
  hip amplitude; weak scales the hip; hold replaces the hip's swing
  and offsets it; limp lifts and sinks the other knee);
- an offset adds S − R; a lag shifts the curve by the difference;
- a stance fraction (duty, limp's duty) or a side's delay (weak)
  re-times that side's leg curves through the grammar's warp about
  the clip's own stance start, the change against R applied to the
  clip's own stance fraction; the root and the arms follow by the
  mean of the two sides' re-timing, so the trunk's pitch and yaw
  stay with the stride; the right leg's phase shifts its curves; the
  frequency scales the duration;
- the root's pitch, roll, lateral offset and lift take the grammar's
  difference S − R added to the clip's (the rotation composed);
- progress follows the stance feet: the clip's own root displacement
  is scaled by the ratio of the edited to the raw kinematic stride,
  each foot's travel extent relative to the root over its stance
  run (a leg without a foot uses its thigh; a body without legs
  keeps the clip's progress).

At S = R every operator is the identity (checked to 1e-15) and the
clip plays as the teacher did. The round's V0 is R: the raw clip on
every body, with the joints the body lacks dropped. A base class is
an edit through the same operators as an impairment, so the
candidate set, the fitter (grid sweeps over the class's parameters
within RANGES), the rules and the budget are G11's unchanged:
G11's teacher, fourteen consumer blocks, held-out acceptance on the
mean of two runs, the per-consumer guard at the runs' distance, the
spent rule at 1 percent, six steps, the same cases, designed classes
and pilot. The comparison is G11's run (`poc/results/g11.json`), the
parametric fit on the same teachers and consumers.

## Pre-build checks on the operator

Declared here because they shaped the operator before the freeze.
None fitted a scored case except the three class fits named last,
which the exclusivity table repeats for every class on every design
body.

1. **Progress.** The first progress model was the planted rule's
   travel on the edited clip minus on the raw one, added to the
   clip's displacement. On the intact clip it turned stiff's
   on-state (the left knee clamped) into a stop (0.04 m/s from 0.40)
   and limp's (the right knee lifted) into a sprint (0.79): the
   handoff geometry of a straight or a lifted leg, the same artefact
   the parametric fits paid for in G9 to G11. Replaced by the stride
   ratio. Its first form, the foot's position at touchdown minus at
   toe-off, read the teacher's shuffle wrongly: its feet stay behind
   the pelvis and travel by knee flexion more than by hip swing, and
   a larger hip swing read as a shorter stride. The extent over the
   stance run is the form kept.
2. **Re-timing.** The warp was first taken about the grammar's stance
   fraction (R's duty, 0.553); the clip's feet are down for 0.84 and
   0.88 of the cycle by the consumers' contact threshold (a shuffle
   with long double support), and a duty edit moved the clip's real
   toe-off into the stance run and doubled the stride. The warp is
   now about the clip's own stance fraction, and the root and arms
   follow the legs (with the legs re-timed alone, the trunk's pitch
   and yaw fell out of step with the stride and the foot's travel
   read jagged).
3. **On-states on the intact clip** (left side; knee range, hip range,
   speed, from 0.76 rad, 0.63 rad, 0.40 m/s): stiff 0.08, 0.96, 0.59;
   weak 0.73, 0.37, 0.42; hold 0.76, 0.43 with the hip offset from
   −0.10 to −0.50, 0.35; limp 0.74, 0.62, 0.54 (the right knee lifted
   and sunk, the left stance shortened); vault unchanged at 0.40 with
   the lift. Base edits: frequency ×1.5 gives 0.60 m/s; duty +0.1,
   +0.3, −0.15 give 0.50, 0.51, 0.44; hip amplitude ×0.5 and ×1.5
   give 0.43 and 0.74 (the hip contributes little to this shuffle's
   foot travel and the extent grows with the larger swing); knee
   amplitude ×0.3 gives 0.42; the right leg's phase +0.5 rad gives
   0.59; weak's delay alone 0.47.
4. **Three class fits at V0** (`RG.fit_class`, the growth's own
   fitter): the left locked knee's stiff 0.581 to 0.559, side −0.44,
   knee scale 0.0, no lift (the knee's range 0.42 rad against the
   teacher's 0.15); the left short shank's limp 0.573 to 0.515, side
   −0.33, sink 0.27; the left weak hip's weak 0.501 to 0.451, side
   +0.44 (the wrong side), scale 0.17, roll 0.4.

## V0: the raw clip on every case

The error of the identity edit against the fitting run (G11's V0 in
brackets, the grammar's walk base fitted to the intact teacher):
intact 0.443 [0.340], weak hip left 0.501 [0.398], locked knee left
0.581 [0.666], short shank left 0.573 [0.987], stump left 0.815
[0.842], one leg left 0.479 [0.767], legless 0.834 [0.885]; the
mirrors weak hip right 0.613 [0.479], locked knee right 0.717
[0.629], short shank right 0.630 [0.934], stump right 0.437 [0.746],
one leg right 0.535 [0.732]; intact seed 1 0.504 [0.879], legless
seed 1 1.028 [0.726]. The raw clip on the intact teacher's own run
scores worse than the grammar fitted to it (0.443 against 0.340):
the mean cycle is periodic and the teacher is not, and the fitted
grammar matched the run's statistics (rhythm 0.87, lateral 0.79,
pose 0.75 on the clip) better than the run's own mean cycle does.
On every damaged body but the weak hips the raw walk scores better
than the walk base did, and on the one-leg bodies by a third: a
one-legged walk and a hop are close in consumer space, which is the
limit of what this round's error can say (below).

Nothing in the clip was fitted to any damaged run, so its error is
the same kind of number on every run of a body; against the two
held-out runs it reads 0.671 (locked knee left), 0.680 (short shank
left), 0.797 (stump left), 0.748 (one leg left), 1.017 (legless),
0.630, 0.569, 0.650, 0.442 on the mirrors. The body's own clip (its
mean cycle or loop from the fitting run) against the same runs reads
0.566, 0.552, 0.728, 0.593, 0.568, 0.981, 0.658, 0.640, 0.364: on the
right locked knee the intact walk scores better than the body's own
cycle. The teacher's runs differ by more than the damage does on
several bodies, and a consumer floor for "reached" does not exist.

## Redundancy screen and exclusivity table

Redundancy screen (`poc/results/gait3d_redundancy_check_g13.*`):
class steps stiff 0.92, weak 0.93, vault 0.81, limp 0.76, hold 0.45
(G11: 0.94, 0.82, 0.94, 0.85, 0.80). On the clip the base edits
have most of what the impairments have, as on the grammar; hold's
step is the exception (0.45, min 0.19), an offset of the hip the
legs' offsets can follow only halfway.

Exclusivity table (`poc/results/gait3d_dictionary_check_g13.*`):
EXCLUSIVITY

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g13_pilot.*`): torso (one of two runs lower), then
arms (both lower); fitting 1.028 to 0.953, held-out mean 0.920 to
0.861; vault worth nothing at either step, rhythm under 1 percent.
Excluded from every bar. No change was made after it.

## Bars (frozen)

`poc/g13_score.py`, committed with this document, comparing with
`poc/results/g11.json`.

- **K1, identity.** First impairment repair names class and side on
  `>= 2` of 3 design bodies, within two on 3 of 3, mirrors 2 of 2.
- **K4, growth generalises.** Mean held-out error below V0's on `>= 7`
  of 9 damaged bodies.
- **K2, consumers.** None beyond tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.
- **K5, K6, reported.** Ground speed and foot travel, as G11.
- **K7, reported, the round's claim.** Per damaged case: the held-out
  error of the raw clip and of the terminal on each run, G11's
  parametric terminal on the same runs, the terminal's speed and
  airborne fraction against the teacher's, and the edits applied.
  Reported and not barred because the consumer error cannot tell a
  one-legged walk from a hop (V0 above): which damages the edits
  reach is settled by the terminal clips in the viewer, exported as
  a clip group beside the teacher and the parametric fit, and by the
  numbers in this table.

## Predictions

PREDICTIONS

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails.
- **D**: neither.

K2, K3, K5, K6 and K7 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
teacher, the clip, the operator, the consumers, the rules or the
budget after this commit. Results go in
`docs/math-track-g13-results.md`; nothing above is edited after the
run.
