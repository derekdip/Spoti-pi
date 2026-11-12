# A walker under full physics, in real time: what was tried, 2026-11-12

A feasibility build, not a preregistered experiment. The aim: a 3D
biped (`poc/gait3d/biped3d.py`, intact body) that walks in MuJoCo with
contacts, gravity and its own actuators, cheaply enough to run inside
a VR frame budget (20 ms of control per 20 ms of game time). All runs
are on this session's machine: 4 CPU threads, no GPU.

## 1. Distil the teacher into a network: fails

`poc/gait3d/distill.py`. The predictive-sampling teacher (`mpc3d.py`:
160 rollouts of 1 s every 20 ms) walks but costs about 19 times real
time. A 2x256 MLP from body state and gait clock to controls costs
0.1 ms per tick. Trained by behaviour cloning and DAgger:

| version | data | longest the student stayed up alone, of 10 s |
|---|---|---|
| 1 (`poc/results/distill/`) | 3 clean teacher walks, 5 DAgger rounds | 1.6 s |
| 2 (`poc/results/distill2/`) | plus 12 noisy teacher walks (DART) and mid-cycle takeovers, 3 rounds | 2.8 s |

The student learns the motion and not the balance. The teacher's
action is the best of 160 random plans warm-started from its last
plan, so it is not a consistent function of the body's state, and a
regression onto it averages unlike recoveries.

## 2. Run the teacher itself, smaller: close

`poc/gait3d/rt_mpc.py`; raw output `poc/results/rt_mpc{,2,3,4,5}.{json,log}`.

- **A 1.0 s look-ahead is needed.** With 0.6 s, 0 of 5 settings walked
  10 s; with 1.0 s, 5 of 5 in the first sweep.
- **Replanning every 80 ms fails** whatever the samples (falls within
  2.3 s); every 40 ms is the most that held.
- **Planning on a 4 ms physics step** (the body itself keeps 2 ms)
  halves the cost with no loss.
- **Over 30 s** (five seeds each):

| samples | replan every | plan step | x real time, 4 threads | walks of 30 s |
|---|---|---|---|---|
| 32 | 20 ms | 4 ms | 2.1 | 4 of 5 (one fell at 8.3 s) |
| 48 | 40 ms | 4 ms | 1.55 | 0 of 5 (all fell at 18.7 to 20.5 s) |

- **The 48-sample falls are a steering failure**: the torso's heading
  wanders until it faces backwards at about 17 s, then the body falls.
  Raising the heading weight from 1 to 5 or 10 did not fix it (1 of 3
  walks of 30 s at either weight, falls at 9 to 14 s).
- **Sideways drift** of 1 to 4 m per 10 to 30 s is common: the cost
  penalises lateral speed, not lateral position.

## Where it stands

The best setting found walks 30 s in 4 of 5 tries at about 2.1 times
real time on 4 threads. Scaled by cores (the rollouts split across
threads), that is about real time on 8 cores; this was not measured.
It does not yet walk indefinitely and it drifts. The next levers are
outside this machine: more cores or a GPU for many more samples (MJX
rollouts), a better planner (MuJoCo MPC's iLQG or gradient sampling),
or a reinforcement-learned policy trained on a GPU, which is reactive
by construction.
