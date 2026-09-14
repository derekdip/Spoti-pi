# Reactive fields: compressing expensive simulation into cheap, cause-driven reconstruction

This branch is a fresh start. The previous contents of this repository (a
Spotify / Raspberry Pi project) are untouched on `main` and remain in this
branch's history before commit `ebbcdec`.

## What this is

A working proof of concept and a written review of the idea:

> cause → compressed world effect → local reconstruction,
> keeping information only while it retains a future capability.

The question being tested is whether an expensive, stateful, neighbour-coupled
vegetation simulation can be replaced at runtime by a small set of banked
cause tokens (footsteps, a walked path, the live player) evaluated through
cheap closed-form kernels, and how much that costs in fidelity.

## Layout

| path | what |
|---|---|
| `docs/review.md` | Correctness review of the write-up: what holds, what is wrong as stated, and the fix for each. |
| `docs/data-sources.md` | Where to get teacher data cheaply, ranked, and which experiment to run first. |
| `poc/reactive/teacher.py` | Expensive reference: coupled nonlinear stalk lattice with player contact, drag, stiffening and plastic crush. |
| `poc/reactive/causes.py` | The cause side: player path, stride events, banked path token. |
| `poc/reactive/primitives.py` | The cheap Quest grammar: stateless closed-form kernels (presence, radial impulse, causal ring wave, path wake, crush, saturate). |
| `poc/reactive/search.py` | Greedy compositional search with a rollout + cost objective (a stand-in for the ECS search). |
| `poc/reactive/field.py` | Level-1 coarse field bake and bilinear sampling. |
| `poc/run_experiment.py` | End to end: teacher → record → search → report. |
| `poc/holdout.py` | Scores the discovered model on a walk it was never fit to. |
| `poc/results/` | Output of the last run: `summary.md`, `summary.json`, `comparison.png`, `holdout.md`. |

## Run it

```
pip install -r requirements.txt
python -m pytest poc/tests -q
python poc/run_experiment.py --quick     # ~10 min, 576 stalks
python poc/run_experiment.py             # ~12 min, 1600 stalks
```

## Results so far

Full run: 1600 stalks, 10 s, an S-curve walk followed by 4 s of standing.
Details and the greedy search path are in `poc/results/summary.md`.

| what | value |
|---|---|
| banked causes | 693 floats (18 stride events + a 201-point path) |
| equivalent per-stalk state | 6400 floats, plus substepped neighbour-coupled integration |
| cheap model cost | ~124 ops per stalk per frame, stateless, no neighbour reads |
| teacher cost | ~320 ops per stalk per frame plus 4 neighbour reads per substep |
| per-stalk state error (relative RMS) | 0.39 overall, 0.35 in the persistence phase |
| 16×16 coarse-field error (what an AI queries) | 0.22 |
| correlation of late coarse fields | 0.98 |
| trail overlap on the coarse grid | 0.95 |

Reading of that: the write-up's claim holds at the level it actually
matters. A handful of banked causes evaluated through closed-form kernels
reproduce what consumers see (the trail, where it is, which way it leans,
how it fades) at a fraction of the cost and with no simulation state. It
does not reproduce per-stalk state, and no smooth kernel will: the residual
is scatter from the teacher's threshold contact and crush, which is exactly
the detail the write-up says to regenerate from a seed rather than keep.
The single biggest lesson is that the path-anchored wake carries almost all
of the fit (0.43 alone versus 0.39 for six terms); per-event tokens are the
wrong description of locomotion. See `docs/review.md` for the rest.

Held-out check (`poc/holdout.py`, results in `poc/results/holdout.md`): the
same parameters on a faster diagonal walk with a hook turn, never seen
during the fit, give 0.38 per-stalk error, 0.21 coarse-field error and 0.99
late-field correlation. The fit is to the physics, not to the one walk.

## Where this should go next

1. Replace the synthetic walks with recorded SquishLabVR hand and foot
   tracks (see `docs/data-sources.md`). Hands and crouching are different
   causes from a walking cylinder.
2. Port the discovered primitives to HLSL as a stateless vertex function
   and profile the composed shader on Quest; feed measured milliseconds back
   into the cost term.
3. Then snow (Taichi MPM teacher), then water (corrected ring wave), then
   crowds (real pedestrian data), then fire.
