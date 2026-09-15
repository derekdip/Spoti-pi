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
| `poc/gpu_sweep.py` | How few terms to ship, and bend-texture cell size versus error. |
| `poc/wind_experiment.py` | Travelling gust tokens versus global Fourier modes on synthetic turbulent wind. |
| `poc/water/` | Exact linear-wave teacher, ripple tokens, a TensorFlow-free reader for the DeepMind water datasets, and slosh fits on real data. |
| `toolkit/` | One card per effect: token, kernel, fitted parameters, teacher, scores, known limits. |
| `unity/` | Reference HLSL kernels and C# constant helpers mirroring the Python (not yet compiled on device). |
| `docs/quest-notes.md` | What to ship, where to evaluate it, and what to measure on Quest. |
| `docs/math-track-b0-review.md` | Review of the behavioural pseudometric track, with the tolerance-sweep results. |
| `poc/knee_experiment.py` | Cost-versus-error envelope per consumer, liveness and path-tolerance scaling laws. |
| `poc/path_compression.py` | Preregistered: spatial vs spacetime vs behaviour-weighted path compression, and the corrected liveness bound. |
| `docs/math-track-b2-prereg.md`, `docs/math-track-b2-results.md` | Frozen preregistration and verdict for causal path complexity (B2). |
| `poc/b2_experiment.py`, `poc/reactive/worldlines.py` | The B2 experiment and its frozen trajectory family. |
| `docs/math-track-b3-prereg.md`, `docs/math-track-b3-results.md`, `poc/b3_experiment.py` | B3: anisotropic smooth term plus corner atoms, probe-calibrated; verdict and diagnosis. |
| `docs/math-track-b4-prereg.md`, `docs/math-track-b4-results.md`, `poc/b4_experiment.py` | B4: the corner law under the local supremum; transfer invariance; the tangent-dependence finding that closes the branch. |
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

Shipping cut (`poc/gpu_sweep.py`, results in `poc/results/gpu_sweep.md`):
wake plus presence alone score 0.40 per-stalk and 0.98 late-field
correlation at 48 ops, against 0.39 and 124 ops for all six terms. A bend
texture baked at cells no larger than the stalk spacing matches direct
token evaluation; 0.5 m cells lose the 0.13 m wide trail.

Wind (`poc/wind_experiment.py`, results in `poc/results/wind.md`): on
synthetic turbulence, travelling gust tokens capture the same energy per
term as global Fourier modes but cost 2 to 4 evaluations per vertex instead
of 32 to 128. A resonant canopy's bend is striped at U/f0, so the right
token is a travelling wave packet, and everything below about 1.5 m of
correlation length is better done as seeded per-stalk noise than as tokens.

Water (`poc/water/`, results in `poc/results/water.md`, `slosh_pulse.md`,
`slosh.md`): against an exact linear-wave solver, a dispersive chirp ring
with a viscous cutoff fits a splash at 0.31 height and 0.33 slope error and
recovers g = 9.8 on its own, while the fixed-wavelength ring is worse than
nothing; a wake is the Huygens sum
of splash tokens along the path at 0.6 error with 6 to 22 live tokens per
point. Against real MPM puddle data (DeepMind WaterDrop), neither standing
modes nor a bouncing pulse extrapolate past the fit window: confined
large-amplitude slosh is not a token, only its period and decay are.

Tolerance sweep (`poc/knee_experiment.py`, results in `poc/results/knee.md`):
the cost-versus-error curve has a knee at 26 to 48 ops per stalk for the
visual consumer and 20 ops for the gameplay consumer; beyond it the grammar
is flat until the teacher itself. Live tokens grow like log(1/eps) as
predicted (slope 25% low from ring-down lobes); path points grow like
tolerance^-0.44 as predicted, but error falls sub-linearly with tolerance
because of pass-time interpolation.

Path compression (`poc/path_compression.py`, results in
`poc/results/path_compression.md`): compressing the walk in spacetime
(position and time together) instead of space alone cuts the excess error
about tenfold at equal point counts on the held-out walk and reaches the
dense-path reference at about 20 vertices. Behaviour weighting was not
distinguishable from plain spacetime here because the kernel's time scale
nearly equals the walking speed.

Causal path complexity, preregistered (`docs/math-track-b2-*.md`): the
isotropic functional `integral sqrt(L |p''|) dt` ranks eight trajectories'
vertex requirements almost perfectly at loose tolerance (Spearman 0.95)
but is beaten by total turning at tight tolerance, because the square
root cannot see the cost of sharp turns and it overcharges along-track
acceleration. Verdict by the frozen rules: failure at the primary
thresholds, with the residuals pointing at an anisotropic two-term law.

B3 (`docs/math-track-b3-*.md`) added an anisotropic smooth term and a
corner term calibrated on probes only. The anisotropy held (along-track
acceleration counts about a third as much as across-track, and the
stop/start miss dropped from 135% to 18%); the corner term over-predicted
corner-dense paths two to one because the global RMS score dilutes an
isolated probe's corner. Verdict: failure at tight tolerance by the frozen
rules; the metric, not the geometry, is the identified cause.

B4 (`docs/math-track-b4-*.md`) scored by the local supremum. The corner's
cost is identical inside 4, 8 and 16 m walks but a 32 m outlier fails the
preregistered invariance rule, and the corner law is closed. The finding
that replaces it: the wake consumer reads the path's tangent, so its error
is first order in chord length on curves; measured error exponents are
about -2 on straight walks and -1 on curved ones, which makes total
turning the derived complexity at tight tolerance and the anisotropic
square-root law the complexity at loose tolerance. B3's dilution diagnosis
had the wrong sign and is corrected.

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
