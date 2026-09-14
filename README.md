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
| `poc/results/` | Output of the last run: `summary.md`, `summary.json`, `comparison.png`. |

## Run it

```
pip install -r requirements.txt
python -m pytest poc/tests -q
python poc/run_experiment.py --quick     # ~10 min, 576 stalks
python poc/run_experiment.py             # 1600 stalks
```

## Results so far

Pending: the calibration run is in progress. Numbers land in `poc/results/summary.md` and here in the next commit.

## Where this should go next

1. Replace the synthetic S-curve with recorded SquishLabVR hand and foot
   tracks (see `docs/data-sources.md`).
2. Add a held-out walk. A model fit and tested on the same walk proves
   little.
3. Port the discovered primitives to HLSL as a stateless vertex function
   and profile the composed shader on Quest; feed measured milliseconds back
   into the cost term.
4. Then snow (Taichi MPM teacher), then water (corrected ring wave), then
   crowds (real pedestrian data), then fire.
