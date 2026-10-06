# The runtime: a body driven from a grammar state, with no physics and no teacher

`poc/gait3d/runtime.py` is the deployable side of the locomotion
case, built after G8 (`docs/math-track-g8-results.md`) established
that the fitted grammar state, not the class label, is what
generalises. Two design checks were run on it
(`poc/gait3d/runtime_check.py`, `poc/results/gait3d_runtime_check.*`),
declared here as design checks and not preregistered.

## What it is

- A **player** holds a body (its MuJoCo model, used for kinematics
  only) and a grammar state, about forty numbers. `advance(dt)`
  moves a phase clock and the forward position and returns the frame:
  every joint's angle from the grammar's closed form at that phase,
  the root's roll and pitch, and the root's position with the body's
  lowest part on the floor plus the state's lift. Any frame rate; no
  teacher, no rollout, no contact solver.
- A **transition** blends to another state over a chosen time, in
  parameter space, with the lags taken along the shorter arc. If the
  body changed (a leg removed), the model is switched at the start of
  the blend: the joints that remain keep their angles, the root is
  re-grounded on the new body. The phase and the forward position are
  integrated, so a change of frequency or speed makes no jump.
- An **export** gives an engine what it reads: joint names, per-frame
  angles, root position and orientation as a quaternion.
- The states come from a growth run: `load_states` reads the terminal
  state of every case in `poc/results/g7.json`.

## Blend check

For each of six damaged design bodies, the straight blend from the
intact body's fitted state to the damaged body's fitted state, played
on the damaged body, scored against the damaged teacher at eleven
points from w = 0 to 1.

| body | error at w = 0 | at 0.5 | at 1 | largest bump above both ends | where the error moves |
|---|---|---|---|---|---|
| weak hip | 0.368 | 0.326 | 0.255 | none | gradually |
| locked knee | 0.574 | 0.541 | 0.272 | none | most of it in the last tenth |
| short shank | 1.033 | 0.476 | 0.308 | none | a cliff between 0.4 and 0.5 |
| stump | 0.663 | 0.654 | 0.274 | none | a cliff between 0.5 and 0.6 |
| one leg | 0.694 | 0.721 | 0.659 | 0.045 | rises to 0.738 at 0.8, then falls |
| no legs | 0.651 | 0.528 | 0.446 | none | unevenly |

The blend is continuous in joint space by construction and not in
contact. The two cliffs are the stance blocks: on the short shank at
w = 0.4 the blended state stands on the long leg with the short foot
never down (stance asymmetry 2.9 scales off), and at 0.5 the
grounding flips and both feet touch; on the stump the same flip
between 0.5 and 0.6. The one-leg body's bump is real: its fitted
state is not the end of a monotone path from the walk, and the blend
passes through states worse than either end by 0.045. Joint-range
violations are small at every point (the locked knee's fitted state
puts a joint outside the body's range 7 percent of the time, at w = 0
as at w = 1; the others 0 to 2 percent).

## Transition check

The intact body walks from its fitted state; at 2.0 s its left leg
is removed and the player blends to the one-leg body's fitted state
over one second, then walks on (`gait3d_runtime_transition.png`, the
export of the frames after the switch in
`gait3d_runtime_transition.json`).

| quantity | at the switch | in the steady gait after |
|---|---|---|
| largest joint speed (rad/s) | 1.82 across the switch frame, 2.13 in the first 0.2 s | 0.81 |
| root height step (m) | 0.0045 | 0.0143 largest between frames |

The root does not jump: the re-grounding on the new body moves it by
less than the gait's own bob. The joints move at twice their steady
speed for a fraction of a second, which is the blend, and the strip
shows a walk that becomes a hop on the remaining leg without a
discontinuity a viewer would see.

## What this says for the VR case

- A damaged body's motion is a state, not an asset: forty numbers
  and a closed form, fitted once per body offline against the physics
  teacher, played at any frame rate with no physics at runtime.
  Damage mid-motion is a transition between states with a model
  switch, and the transition needs nothing the state does not
  already carry.
- A straight blend is right for the joints and wrong for the
  contacts: where the body's support changes (which part is on the
  floor), the grounding flips at a threshold. A blend that wants a
  smooth footfall must schedule the support change, which is a phase
  event, not a parameter one; the phase clock is there to hang it on.
- The blend check is the consumers again: the same blocks that scored
  the growth score a transition, so a runtime rule (when to switch
  support, how long to blend) can be chosen against the teacher's own
  numbers rather than by eye.

## After G11: the fitted state abandoned for the viewer, and the cycle runtime

The web viewer showed the fitted states to a viewer four times, and
each time the viewer faulted what the objective did not measure.
Each round's objective was met by its own numbers and the next fault
was already there.

| objective | what the fit did | what the viewer saw |
|---|---|---|
| G7 consumers | matched the teacher's contact clock, stance and joint statistics | the stance foot skated; the arms did not move (a teacher defect, the hands jammed on the pelvis box, fixed for G10) |
| G9 planted grounding | speed from the stride, no sliding | the bodies stepped back; the feet swung at a third of the teacher's speed |
| G10 teacher with a gait prior | the teacher itself reads as a walk | the fitted states still stepped in place |
| G11 foot travel (swing speed, step length) | swing speeds within a factor of two | steps that hardly move the body: the parametric runtime plays the G11 stump backwards at 0.11 m/s and the one-leg hop at 0.03 (teacher 0.16 and 0.34) |
| G12 draft, the support foot from the grammar's clock (`docs/math-track-g12-prereg.md`, not run) | the intact state's four-second advance from 1.47 m to 2.25 m on replay | the V0 refit under it lunged, feet 0.71 m apart on average (teacher 0.22) |
| a pose fit (`poc/gait3d/pose_fit.py`): every parameter against the teacher's own frames, then against its mean cycle (`gait3d_pose_*.json`, `.png`) | frame error down | shuffled steps from averaging irregular cycles; then two touchdowns a cycle to game the cycle profile |

Six objectives, each one number the viewer's eye had used, and the
eye always had another. The teacher, meanwhile, reads right. So the
deployable description is now the teacher's own motion, and the
runtime keeps what the parametric player had that a clip does not: a
clock, root motion, a blend, a body switch and the style layer.
`poc/gait3d/cycle_runtime.py`:

- For the bodies that walk (intact, weak hip, locked knee, short
  shank), the **mean cycle**: the teacher's frames cut at a foot's
  touchdowns, resampled to 32 phase bins and averaged, joint angles,
  root height, the root's orientation as a quaternion (mean of the
  cycles' quaternions, sign-aligned) and the root's displacement
  across the cycle. About 500 numbers.
- For the gaits with no clean cycle (the stump's kneel-step, the
  one-leg hop, the legless crawl), the **loop**: the teacher's
  four-second window as one clip, the first 0.3 s crossfaded onto
  the last 0.3 s and dropped, root displacement from the clip.
- The player interpolates the profile at its clock's phase, moves
  the root by the profile's own displacement (root motion, so the
  clip's speed is the teacher's), and never lets the lowest part go
  below the floor. A transition blends two profiles in phase space
  (the shorter resampled to the longer's bins, orientation by
  normalised interpolation) and switches the body if it changed.
- The style layer (`styled`) offsets the shoulders and elbows, keeps
  a quarter of the arms' own swing, and pitches the torso 0.22 rad in
  its own frame; the crawl keeps its arms and its pitch.

Design check, the runtime against its teacher (seed 0, 8 s at 50
frames a second, the consumers' own speed and airborne measures):

| body | clip | length | speed, runtime / teacher (m/s) | airborne fraction, runtime / teacher |
|---|---|---|---|---|
| intact | mean cycle | 0.93 s | 0.40 / 0.42 | 0.00 / 0.01 |
| weak hip | mean cycle | 0.86 s | 0.42 / 0.41 | 0.00 / 0.00 |
| locked knee | mean cycle | 1.23 s | 0.34 / 0.34 | 0.00 / 0.00 |
| short shank | mean cycle | 0.77 s | 0.26 / 0.33 | 0.03 / 0.07 |
| stump | loop | 3.70 s | 0.16 / 0.16 | 0.02 / 0.03 |
| one leg | loop | 3.70 s | 0.35 / 0.34 | 0.05 / 0.06 |
| no legs | loop | 3.70 s | 0.43 / 0.44 | 0.07 / 0.05 |

The largest joint step across a loop's seam is 0.12 rad (stump), 0.11
(one leg) and 0.25 (no legs). The short shank is the one body the
mean cycle loses something on: its skipping gait's flight averages
out (airborne 0.03 against 0.07) and it plays at 0.26 m/s against
0.33. In the transition (intact cycle, leg removed at 2 s, one-second
blend to the one-leg loop) the joints move at up to 9.2 rad/s in the
first 0.2 s, against the hop's own 12.7; the blend crosses a 0.93 s
cycle with a 3.7 s loop, so during the second the walk's clock slows
and the hop's quickens, a crossfade and not a path.

What this changes in the claim. The grammar state remains the object
of the growth rounds: it is what named the damage (G7, G8) and what
generalised to the held-out runs (every 3D round), and the parametric
runtime, the blend check and the transition check above stand as
they were. It is not, on this teacher and these consumers, a motion a
viewer accepts, and no consumer block added for the viewer closed
the gap without opening the next. The clip is heavier (500 to 2,600
numbers against 44), cannot be edited along a class (a limp is not a
dial on it), and its transitions are crossfades, not paths in a state
space. It is what plays. The viewer
(`poc/results/damaged-gait-player.html`) shows both, the cycle
runtime first and the G11 states beneath it for comparison.

G13 (`docs/math-track-g13-results.md`) then asked whether the
grammar's classes carry as edits of the clip: they do as a
representation the growth rule can grow, they name the damage only
relative to the clip's own asymmetry, and they reach the walking
damages and not the kneel-step, the hop or the crawl, which stay
clips of their own.
G14 (`docs/math-track-g14-results.md`) added clearance grounding to
the cycle runtime (a profile carries its own lowest part's height,
so a body that has lost the parts a clip stood on comes down to the
floor) and showed that a dropped part needs no edit, that two edits
compose to within a quarter of a fresh fit, and that a body the
physics cannot move has no clip to switch to.
