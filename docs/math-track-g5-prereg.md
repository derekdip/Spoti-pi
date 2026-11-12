# G5: the grammar without the hop class. Preregistration (frozen before any scored case is run)

The plan after G4 was to give hop a flight phase the walk base could
not produce, so that a base refit could not absorb it on the one-leg
bodies. Read against the grammar and the teacher before anything was
changed, that plan was wrong twice over, and this round does something
else.

## What the record shows

**The teacher's intact walk is airborne.** The intact body's three
runs have no floor contact 28, 27 and 21 percent of the time (seeds 0,
1 and 2); the planner's cost asks for 0.8 m/s and
nothing about flight, and it runs. So flight belongs to the base: V0
carries it as `bob_amp` 0.047 m, and a base that could not leave the
floor would not fit the intact teacher, and hop would then be named on
the undamaged body.

**Every hop parameter is a base parameter.** In `joint_angles`, the
cycle rate is `freq * hop_rate`, the right leg's phase is `phase_r *
(1 - hop_sync)`, both knees carry `knee_off + hop_crouch`, and the
lift is `max(0, hop_flight * max(0, sin 2phi) + bob_amp * sin 2phi)`,
which is `max(0, (hop_flight + bob_amp) sin 2phi)`. A state with hop
on therefore has an exact base-only twin (`poc/gait/hop_equivalence.py`,
run at commit `388686e`): on all eleven bodies that can hop, the hop
on-state and its twin give identical consumer vectors, difference
0.0 to floating point, where the on-state differs from V0 by 1.2 to
7.8 scale units. The two terminal states of G3 and G4 that had hop on
are the same: the G4 one-leg terminal differs from its twin by 0.0,
the G3 right-stump terminal, which also had limp's hitch in the lift,
by 0.002. What hop added was range: the twin of the on-state has
`bob_amp` 0.127 where the base's limit was 0.1, and `knee_off` can
reach 1.84 where the limit was 1.5.

So the exclusivity table's "a third of hop absorbable by a base
refit" (G2) was the base within its bounds, and the three selection
rules that never named hop on the right one-leg body (G2, G3, G4)
were right: on a one-leg body the hop is the walk base on one leg,
and the design body named hop first only because the hop fit reached
the twin state before the legs and torso refits did, with the base's
bounds in the way.

**A first-order check was built and is kept, with its limit.**
`poc/gait/redundancy_check.py` regresses each impairment parameter's
finite-difference tangent on the span of the base parameters'
tangents. Under the old grammar it puts `hop_crouch` at 1.00 and
`hop_rate` at 0.73, and `hop_flight` at only 0.26 although it is
algebraically the same direction as `bob_amp`: the contact consumers
are step functions of the lift, so two finite differences with
different steps (4 percent of each parameter's range) see different
"tangents". The exact twin is the decisive check where one exists;
the first-order table is a screen. Its full output for the old
grammar is `poc/results/gait_redundancy_check.log` (its json was
overwritten by a rerun and is not kept); for the new grammar,
`gait_redundancy_check_g5.*`. Vault's other parameters (drive, off,
pitch, elbow) read 0.90 to 1.00 on every body: they are the arm base with
different bounds and a different sign convention, and vault's lift is
what vault owns. That is noted, not acted on here.

## The change

The hop class is removed from the grammar: its four fields, its
terms in `joint_angles`, its entries in the class, range and on-state
tables. The base's `knee_off` range becomes (0, 2.0) and `bob_amp`
(0, 0.35), which cover the twins of every hop state the old ranges
allowed. V0 is unchanged (the loader restricts the saved state to the
base parameters, and no base value moved). The one-leg bodies have no
designed class: their gait is the base on one leg, as the short-shank
bodies' limp is their geometry. Everything else, the procedure, the
consumers, the teachers, G4's two rules and its candidate order, is
G4's; `poc/g5_experiment.py` is G4's script with the designed-class
table changed and the output paths.

The exclusivity table was rerun on the new grammar before this
document was frozen (`poc/results/gait_dictionary_check_g5.*`):
every pair of the remaining classes is within 0.01 of G2's table
except one, legs absorbs kneel, 0.40 against 0.57, the legs grid now
laid over the wider `knee_off` range. The two pairs over a half are
G2's, legs absorbs limp 0.61 and limp absorbs kneel 0.55.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g5_pilot.*`): vault then torso, both runs lower each
time, fitting error 0.724 to 0.356 as in G4's pilot; the held-out
mean is 0.343 against G4's 0.342, because the torso refit's grid now
spans the widened `bob_amp` range. That is the only way the change
reaches a body that cannot hop: the legs and torso grids are laid
over wider bounds. Excluded from every bar.

## Bars (frozen)

Three design bodies with a designed class (locked knee, stump,
legless), two mirrors (right locked knee, right stump), nine damaged
bodies (those five, the two short shanks, the two one-leg bodies),
four controls, the pilot excluded. Scored against G4 on the same
fitting teachers (`poc/results/g4.json`).

- **K1, identity is kept.** The first impairment repair names the
  class and side on `>= 2` of the three design bodies, within two on
  3 of 3, and within two on 2 of the 2 mirrors.
- **K5, nothing was lost with hop.** On both one-leg bodies the
  terminal fitting error is not above G4's terminal by more than one
  percent of the case's V0 error (the spent rule's unit). Reported
  with it: whether the right stump's first impairment repair is kneel
  with no guard rejection, which in G4 took the guard stopping hop.
- **K2, consumers.** No consumer beyond its tolerance on `>= 7` of
  the nine damaged bodies.
- **K3, controls.** At most 4 impairment repairs in total on the four
  controls, G4's count.
- **K4, growth generalises.** Mean held-out error below V0's on
  `>= 7` of the nine damaged bodies; both-run count reported.

Reported: every case's terminal fitting error against G4's, repairs
per case, rejections by reason, held-out agreement, value against the
best fitting drop, pictures.

## Predictions

K1 holds at 3 of 3, 3 of 3, 2 of 2: with hop gone, kneel is the top
impairment on both stumps once the legs have refitted, and the right
stump no longer needs the guard. K5 holds: the base with the widened
bounds contains the one-leg terminals of G4, and the greedy path has
six steps to reach them. K2, K3, K4 hold as in G4. Terminal errors
stay close to G4's on every body that never took hop, the only
difference being the legs and torso grids over the widened bounds.
The predicted letter is A.

## Outcome (frozen, exclusive)

Determined by K1 and K5.

- **A**: both hold. Hop was a duplicate; the grammar has five
  impairment classes and the one-leg gait is a base state.
- **B**: K1 holds, K5 fails. The base's greedy refits do not reach
  what hop's single fit reached: hop was a search shortcut, not a
  direction.
- **C**: K5 holds, K1 fails.
- **D**: neither.

K2, K3 and K4 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
grammar, the rules or the budget after this commit. Results go in
`docs/math-track-g5-results.md`; nothing above is edited after the
run.
