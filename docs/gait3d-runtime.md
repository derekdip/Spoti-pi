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
