# Gait feasibility: does one objective give a walk, a limp, a hop and a crawl as legs are removed?

A feasibility day, not a preregistered experiment. The question is
whether a physics teacher for damaged locomotion can be had cheaply
enough to build the next case on: a planar biped in MuJoCo
(`poc/gait/biped.py`), driven by predictive sampling
(`poc/gait/mpc.py`) with one cost for every body. Legs are removed and
nothing else changes. Five seconds per morphology, metrics over the
last three. Raw output per iteration under
`poc/results/gait_iter*_*` and the run log
`poc/results/gait_feasibility_run.log`; the stick-figure strips are the
check on the numbers.

## What would count, written before the run

| morphology | expected gait | counts as feasible if |
|---|---|---|
| intact | walk | speed over 0.4 m/s; both feet in stance at least 20 percent of the time; single support (one foot down) at least 40 percent |
| left shank and foot removed | limp on the stump | speed over 0.3 m/s; forward progress on the stump and the foot alternating; stance asymmetry between stump and foot at least 0.15 |
| left leg removed at the hip | hop, or crutch on an arm | speed over 0.2 m/s; either flight phases (no ground contact) or a hand in contact at least 20 percent of the time |
| both legs removed | crawl on the arms | speed over 0.2 m/s; a hand in contact at least 30 percent of the time; torso centre below 0.6 m |

"Feasible" means the teacher produces, from one cost and no gait
prior, motions a person would name the way the table does. A gait
that meets a row's numbers and does not look like the row's word fails
the row.

## The iterations, in order

Every change below was made after looking at the previous run, which
is what a feasibility day is for and what a preregistered run must not
do. They are listed so that the final cost and body are not mistaken
for a first guess.

1. **Torque actuators, cost = speed toward 0.8 m/s + 0.3 pitch² +
   20 (0.35 − head height)₊² + 0.02 effort, horizon 0.5 s, 5 knots,
   96 samples.** Every body, the intact one included, flopped forward
   and dragged itself head-first along the floor at 0.4 to 0.5 m/s;
   the legless body ended balanced on its head. The cost made falling
   cheap and the head term was too low to matter.
2. **Head target = the head height of the body's own initial pose,
   weight 3; a 50-weight penalty below 0.25 m; pitch weight 2; horizon
   0.6 s, 6 knots, 128 samples.** The intact body fell in the first
   second and never got up (speed 0.10 m/s, hands on the floor 99
   percent of the time); the legless body lay still. Torque sampling
   over half a second cannot balance a 47 kg biped from a standing
   start, and once down, getting up is outside the horizon.
3. **Position actuators (target joint angles as the action, kp 100 to
   300, joint damping 3) and a 0.1-weight term on joint angles.** Zero
   action now holds the standing pose, and the sampler explores steps
   from a body that stands by default. The intact body walked upright
   at 0.78 m/s with alternating feet. The stump body knelt on the
   stump and stepped with its foot at 0.74 m/s. The one-legged body
   hopped, fell to its hands and came back to its knee at 0.74 m/s.
   The legless body balanced upright on the rounded end of its torso
   and hopped along at 0.66 m/s, a thing no body can do. Also found:
   the touch sensors counted hands brushing the torso as stance, so
   contact is now read from the contact list against the floor only.
4. **A flat pelvis box at the bottom of the torso.** The intact walk
   (0.75 m/s, single support 43 percent, double support 35, 22 percent
   airborne), the kneel-and-step on the stump (0.79 m/s, stump and foot
   alternating 38 percent, asymmetry 0.17) and the one-legged lurch
   (0.79 m/s, 40 percent airborne, the head on the floor 5 percent of
   the time) all stand. The legless body now sits stably with zero
   action, and under the controller tips forward onto its face chasing
   speed and stays there: 0.00 m/s, pelvis and head on the floor for
   the whole window, hands never touching the ground.
5. **Horizon 1.0 s, 8 knots.** So that the fall, which iteration 4's
   planner could not see past the speed it gained on the way down, is
   inside the horizon. About 60 to 90 seconds per morphology.

## Result (iteration 5, with iteration 4 beside it where they differ)

| morphology | speed m/s | torso height | what it does | row |
|---|---|---|---|---|
| intact | 0.73 | 1.14 | an upright walk, feet alternating 52 percent of the time, 32 percent airborne, one skip in the strip | **holds** |
| left shank and foot removed | 0.76 | 0.73 | kneels on the stump and steps with the foot, stump and foot alternating 33 percent; asymmetry 0.08 here, 0.17 in iteration 4 | numbers hold in iteration 4 and miss on asymmetry here; **the word fails**: it is a kneel-and-step, not a limp |
| left leg removed at the hip | 0.70 | 0.96 | hops upright on the one leg for three seconds, 55 percent airborne, then drops to its knee and hops on that | **holds** |
| both legs removed | 0.14 | 0.17 | sits, tips forward at 2.4 s, lies face down; one hand on the floor 13 percent of the time | **fails** |

Three of four bodies produce a distinct, morphology-adapted gait from
one cost and no gait prior, at about a minute of compute each on four
cores. That is the feasibility answer: the teacher exists at this
price. Two things it does not do, and why:

**No crawl.** From a sitting start the planner leans into the speed
term, topples, and from prone cannot find the arm sequence that
raises the body within a one-second horizon: pushing up costs more,
in head height and speed, over the next second than lying still does.
Predictive sampling with Gaussian noise around one nominal plan is the
weakest of the sampling planners; a cross-entropy or MPPI update with
more samples, or a longer horizon, would likely find the push-up, and
a "get up" primitive certainly would. This is the first thing to fix
before a crawl is a teacher signal. It is also worth saying that no
body here was asked to crawl: the cost asks for speed and head height,
and lying still is a local optimum of that cost for a body with no
legs and arms that start beneath it.

**No limp.** A leg removed at the knee gives a kneel, because the
stump is 0.42 m shorter than the foot and the body cannot stand on
both. A limp needs a leg that is present and impaired: a locked knee,
a weak hip actuator, a shortened shank. Those are cheap morphologies
to add and were not in the four chosen. The "remove a leg and it
limps" of the original ask is really "damage a leg and it limps", and
the teacher can be asked that.

**What the next case would look like.** Teacher: this biped and
planner, over a family of damage conditions (weak hip, locked knee,
shortened shank, missing shank, missing leg, and, once the planner
can find it, missing both). Consumers: foot and knee contact times,
root path and speed, reach envelope of the hands, a coarse silhouette
at a few frames per cycle. Student: a phase-based gait grammar with
classes for the impairments, each with parameters and a canonical
on-state, closed-form per phase, and the dictionary check
(`docs/linearisation-gap.md`) run on it before the first fit. The RGRE
run then follows the fire pattern with `hybrid_pick`. The teacher's
cost per gait, about a minute, is the same order as a fire scene's.

Nothing here is a claim; it is the state of a one-day build.
