# Gait feasibility: does one objective give a walk, a limp, a hop and a crawl as legs are damaged or removed?

A feasibility build, not a preregistered experiment. The question is
whether a physics teacher for damaged locomotion can be had cheaply
enough to build the next case on: a planar biped in MuJoCo
(`poc/gait/biped.py`), driven by predictive sampling
(`poc/gait/mpc.py`) with one cost for every body. Legs are damaged or
removed and nothing else changes. Five seconds per morphology, metrics
over the last three. Raw output per iteration under
`poc/results/gait_iter*_*`, the run log
`poc/results/gait_feasibility_run.log`, the crawl probe
`poc/results/gait_crawl_probe.log` and `gait_probe_*.png`; the
stick-figure strips are the check on the numbers.

## What would count, written before the run

| morphology | expected gait | counts as feasible if |
|---|---|---|
| intact | walk | speed over 0.4 m/s; both feet in stance at least 20 percent of the time; single support (one foot down) at least 40 percent |
| left shank and foot removed | limp on the stump | speed over 0.3 m/s; forward progress on the stump and the foot alternating; stance asymmetry between stump and foot at least 0.15 |
| left leg removed at the hip | hop, or crutch on an arm | speed over 0.2 m/s; either flight phases (no ground contact) or a hand in contact at least 20 percent of the time |
| both legs removed | crawl on the arms | speed over 0.2 m/s; a hand in contact at least 30 percent of the time; torso centre below 0.6 m |

Added before iteration 6, for the three impaired-leg bodies (weak
left hip, locked left knee, short left shank), each expected to limp:
speed over 0.3 m/s; both feet in stance at least 15 percent of the
time; stance asymmetry between the feet at least 0.15.

"Feasible" means the teacher produces, from one cost and no gait
prior, motions a person would name the way the table does. A gait
that meets a row's numbers and does not look like the row's word fails
the row.

## The iterations, in order

Every change below was made after looking at the previous run, which
is what a feasibility build is for and what a preregistered run must
not do. They are listed so that the final cost and body are not
mistaken for a first guess.

1. **Torque actuators, cost = speed toward 0.8 m/s + 0.3 pitch² +
   20 (0.35 − head height)₊² + 0.02 effort, horizon 0.5 s, 5 knots,
   96 samples.** Every body, the intact one included, flopped forward
   and dragged itself head-first along the floor at 0.4 to 0.5 m/s;
   the legless body ended balanced on its head. The cost made falling
   cheap and the head term was too low to matter.
2. **Head target = the head height of the body's own initial pose,
   weight 3; a 50-weight penalty below 0.25 m; pitch weight 2; horizon
   0.6 s, 6 knots, 128 samples.** The intact body fell in the first
   second and never got up; the legless body lay still. Torque
   sampling over half a second cannot balance a 47 kg biped from a
   standing start, and once down, getting up is outside the horizon.
3. **Position actuators (target joint angles as the action, kp 100 to
   300, joint damping 3) and a 0.1-weight term on joint angles.** Zero
   action holds the standing pose and the sampler explores steps from a
   body that stands by default. The intact body walked upright at 0.78
   m/s. The stump body knelt on the stump and stepped. The one-legged
   body hopped, fell to its hands and came back to its knee. The
   legless body balanced upright on the rounded end of its torso and
   hopped along at 0.66 m/s, a thing no body can do. Also found: the
   touch sensors counted hands brushing the torso as stance, so contact
   is read from the contact list against the floor from here on.
4. **A flat pelvis box at the bottom of the torso.** The walk, the
   kneel-and-step and the one-legged lurch stand. The legless body sits
   stably with zero action and under the controller tips forward onto
   its face chasing speed and stays there.
5. **Horizon 1.0 s, 8 knots.** The one-legged body now hops upright
   on its one leg for three seconds before dropping to a knee. The
   legless body still topples and lies face down.
6. **Three impaired-leg bodies added, and the nominal plan made the
   mean of the twelve best samples instead of the best one (160
   samples).** The locked knee produced a clean stiff-legged walk at
   0.70 m/s, the first limp. But the averaged update blurred the phase
   of every other gait: the intact body walked for three seconds then
   dropped to its knees, the one-legged hop was lost, the legless body
   lay face down. **Reverted to the single best sample.** A crawl
   probe (`poc/gait/crawl_probe.py`) then showed the legless body,
   started prone with the arms ahead of its head, getting up and
   hopping along on its pelvis at 0.75 m/s with the arms as flails:
   the iteration-3 exploit again, on a box. Position actuators with
   unbounded force will launch a body off any surface.
7. **Actuator force limits (hip and knee 150 N·m, ankle and shoulder
   60, elbow 40) and each body started at its own rest pose, the
   legless one prone with the hands on the floor ahead of the head.**
   Result below. About 100 seconds per body on four cores.

## Result (iteration 7)

| morphology | speed m/s | torso height | what it does | row |
|---|---|---|---|---|
| intact | 0.75 | 1.12 | upright walk, feet alternating 56 percent, 28 percent airborne | **holds** |
| weak left hip | 0.71 | 1.10 | an upright walk with stance asymmetry 0.05, an arm flung out and one stumble in the strip | speed and stance hold, asymmetry does not: **the word fails**, it walks |
| locked left knee | 0.79 | 1.13 | a stiff-legged walk, the left leg swung straight, stance asymmetry 0.14 | asymmetry misses by 0.01; **the word holds**, a peg-leg limp |
| short left shank | 0.74 | 1.07 | an upright walk with the short leg lifted high and planted short, stance asymmetry 0.47 | **holds**, a limp |
| left shank and foot removed | 0.72 | 0.71 | kneels on the stump and steps with the foot, alternating 34 percent, asymmetry 0.16 | numbers hold; a kneel-and-step, not a limp |
| left leg removed at the hip | 0.72 | 0.70 | hops on the one leg with the knee as a second contact, 41 percent airborne | **holds** |
| both legs removed | 0.65 | 0.36 | sits on the pelvis, plants a hand, vaults the body forward over the arm, lands on the pelvis; hands on the floor 42 percent, pelvis 22, airborne 27 | numbers hold; an arm-vault, which is how a legless body does move, not a prone crawl |

Seven bodies, one cost, seven distinct gaits, and five of them are
what a person would call them: a walk, two kinds of limp, a hop, and
an arm-supported vault. The two that are not are named as what they
are. That is the feasibility answer: **the teacher exists, at about a
hundred seconds per gait.**

Three things the build says about the teacher, for the case to come:

**The physics has to be honest before the cost can be.** Three of the
seven iterations fixed the body rather than the objective: a flat
pelvis, force limits, a rest pose. Each time the planner had found a
motion the cost rewarded and no body can perform. A teacher that can
exploit its own physics teaches the wrong gait, and the check is the
strip, not the number.

**A weak joint is not a visible impairment at this level of damage.**
The weak hip walked. Either the gain has to fall further, or the
impairment has to be a range limit, which the locked knee and the
short shank show is enough on its own.

**The removed-leg gaits are kneeling gaits.** Without a prosthesis a
stump kneels, a single leg hops with the other knee down, a legless
body vaults on its arms. These are the gaits the grammar has to hold,
and none of them is a walk with a parameter changed. The grammar's
impairment classes are therefore not perturbations of the walk but
separate contact patterns, which is the thing to know before writing
the grammar.

## What the case looks like from here

Teacher: this biped and planner over the seven bodies, plus a right-
side mirror of each impairment for the transfer set. Consumers: foot,
knee, hand and pelvis contact fractions per phase bin; root path,
height and pitch; the reach envelope of the hands; joint angles at a
few phases per cycle as the silhouette. Student: a phase-based gait
grammar with a walk base and classes for stiff leg, short leg,
kneel-and-step, one-leg hop and arm vault, each with parameters and a
canonical on-state, closed-form per phase; the dictionary check
(`docs/linearisation-gap.md`) run on it before the first fit, and the
growth done with `hybrid_pick`. Nothing here is a claim; it is the
state of a two-day build.
