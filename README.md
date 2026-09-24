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
| `unity/Fire/`, `docs/unity-fire-integration.md` | The cheap fire as a Unity package: parcel maths on CPU and GPU, a procedural billboard shader whose max blend is the intensive physics rather than a look, the five fitted presets with the still-image reference beside each score, a gameplay API for burn, ignition and hazard queries, and an account of what is measured (the decisions), what is not (how it looks), and what has never been tried (three dimensions, a headset, two fires at once). Uncompiled. |
| `docs/quest-notes.md` | What to ship, where to evaluate it, and what to measure on Quest. |
| `docs/math-track-b0-review.md` | Review of the behavioural pseudometric track, with the tolerance-sweep results. |
| `poc/knee_experiment.py` | Cost-versus-error envelope per consumer, liveness and path-tolerance scaling laws. |
| `poc/path_compression.py` | Preregistered: spatial vs spacetime vs behaviour-weighted path compression, and the corrected liveness bound. |
| `docs/math-track-b2-prereg.md`, `docs/math-track-b2-results.md` | Frozen preregistration and verdict for causal path complexity (B2). |
| `poc/b2_experiment.py`, `poc/reactive/worldlines.py` | The B2 experiment and its frozen trajectory family. |
| `docs/math-track-b3-prereg.md`, `docs/math-track-b3-results.md`, `poc/b3_experiment.py` | B3: anisotropic smooth term plus corner atoms, probe-calibrated; verdict and diagnosis. |
| `docs/math-track-b4-prereg.md`, `docs/math-track-b4-results.md`, `poc/b4_experiment.py` | B4: the corner law under the local supremum; transfer invariance; the tangent-dependence finding that closes the branch. |
| `docs/math-track-w1-prereg.md`, `docs/math-track-w1-results.md`, `poc/w1_experiment.py` | W1: transfer to water. Observation-order law confirmed with four exponents; liveness law finds its boundary; superposition threshold measured. |
| `docs/math-track-w2-prereg.md`, `docs/math-track-w2-results.md`, `poc/w2_analysis.py` | W2: with exponents fixed by theory and two coarse grids per curve, required resolution and the binding consumer are predicted on held-out tolerances. |
| `docs/math-track-w3-prereg.md`, `docs/math-track-w3-results.md`, `poc/w3_experiment.py`, `poc/w3_residual_diagnostic.py` | W3: amplitude-conditioned unary token vs pair interaction. Failure by the frozen rules; gain and dispersion carry the nonlinearity, half the error is unreachable by conditioning, and a post-hoc diagnostic says what the rest is. |
| `docs/math-track-w4-prereg.md`, `docs/math-track-w4-results.md`, `poc/w4_experiment.py` | W4: event-coordinate conditioning. Coordinate confirmed on three never-run amplitudes: the large-amplitude splash is the base token started earlier, the delay is predicted from one calibration amplitude, and the dispersion slope W3 found vanishes once timing is free. |
| `docs/math-track-b5-prereg.md`, `docs/math-track-b5-results.md`, `poc/b5_experiment.py` | B5: smooth, singular, event decomposition on fresh corn paths. Failure by the frozen rules (three bars mis-defined, two substantive), with the residual naming the class before any repair, class repairs working where the residual lives, dwell a pure event coordinate, and a constant-free law within a factor 1.5. |
| `docs/math-track-rgre1-prereg.md`, `docs/math-track-rgre1-results.md`, `poc/rgre/`, `poc/rgre1_experiment.py` | RGRE-1: residual-guided representation expansion on 78 fresh cases in two domains. Outcome A by the frozen tree (median oracle value 1.00 at a sixth of the evaluations, 0.88 two-step recovery, 5 of 6 unknowns abstain); the coherence-weighted score and known-case abstention lose to plain per-direction projection, which never loses. |
| `docs/math-track-rgre1b-prereg.md`, `docs/math-track-rgre1b-results.md`, `poc/rgre/bench_b.py`, `poc/rgre1b_experiment.py` | RGRE-1b: the simplified selector replicates on 30 fresh cases. All four frozen bars hold, and the coherence rule it replaces is worse on every case the two disagree about. |
| `poc/web/bendbench.html`, `docs/bendbench-results.md` | The on-device profiling step: a WebGL2 harness that measures what the bend arithmetic costs against vertex and fill cost, and the measurement from a phone. Six terms cost a third of the frame at half a million stalks and under 1% at a realistic 15,000; the bend texture costs nothing; op counts mispredict measured cost by up to 8x. A Quest 2 two-eye resolution is included for a run in the headset's browser, which has not yet been done. |
| `poc/fire/` | Fire teacher: 2-D buoyant reacting flow with fuel, soot and obstacles, four game-relevant consumers, and five validated scenes. Preparation for the end-to-end test. |
| `docs/math-track-f1-prereg.md`, `docs/math-track-f1-results.md`, `poc/f1_experiment.py` | F1: RGRE end to end on fire, nothing chosen by hand. Selection transfers at full value and a tenth of the search; the carried-over abstention threshold stops every scene early; an amendment records that three classes were unreachable by the fitter. |
| `docs/math-track-f2-prereg.md`, `docs/math-track-f2-results.md`, `poc/f2_experiment.py` | F2: a replacement stopping rule gets eight of nine decisions wrong; the run exposes the inert-class defect and names a non-exclusive outcome tree. |
| `docs/math-track-f3-prereg.md`, `docs/math-track-f3-results.md`, `poc/f3_experiment.py` | F3: no stopping rule, fitter fixed. Greedy reaches 96 percent of a joint fit; the joint fit still leaves 0.63 against a 0.35 bar and seed noise of 0.003; the vocabulary, not the search, is the limit, and F1's bar was unreachable when frozen. |
| `docs/fire-shapes-added.md`, `poc/fire/tokens.py`, `poc/fire/rgre_fire.py` | Three source shapes (split, puff, bed) and two fitted profile exponents, unfrozen. Each activates only where its physics applies; the floor moves 0.63 to 0.58; optimiser slack of up to 20 percent is measured and the conclusion survives it. |
| `docs/fire-decisions.md`, `poc/fire_decisions.py` | What a game would decide from the cheap fire: burn and passable decisions 1 to 4 percent wrong on the two simplest scenes and 10 to 19 percent on the rest; misses outnumber false alarms three to one; proposed per-consumer bars for the owner to set. |
| `docs/rgre-writeup.md` | RGRE consolidated: the procedure as it stands, the evidence across three domains, and the ten failures in full. |
| `docs/math-track-f4-prereg.md`, `docs/math-track-f4-results.md`, `poc/fire/puffs.py`, `poc/fire/rgre_puffs.py`, `poc/f4_experiment.py` | F4: a stateless parcel-train fire grammar against the column on seven unseen scenes, after a declared three-round pilot. Outcome D by the frozen tree (glow correlation 0.64 median, floor below the column on 5 of 7); underneath, the better representation by 8 to 20 percent wherever there is a bed, ignition misses from 28 to 67 percent down to 6 to 11, the first cheap fire that looks like the teacher's on `twin`, and the two misses inside the optimiser's own disagreement. |
| `docs/math-track-f5-prereg.md`, `docs/math-track-f5-results.md`, `poc/f5_experiment.py`, `poc/fire_law_control.py` | F5: a quasi-static sway law, a parcel budget in the objective, and a glow measure shown unable to test motion. Outcome A by the frozen tree, overturned by its own control: the law it replaced sways better, the 23 percent it buys is error not motion, the visual defect is plume height, and the gust amplitude is still fitted rather than read from the cause. |
| `docs/fire-height-control.md`, `poc/fire_height_control.py` | The height diagnosis tested before a round was built on it: one scene of two, and the strongest fact against it is a scene whose free fit matches the teacher's plume height exactly and has the worst visual error. What the passing case shows instead is that pinning one measured parameter reaches a glow correlation of 0.84 on seven parcels, the best and cheapest state in the arc, while the fitting objective scores it worse and would never select it. |
| `docs/fire-physics-first.md`, `poc/fire_physics_first.py` | Seven constants measured once on a reference teacher and substituted for the token's parameters: worse on every one of five scenes, 28 percent of visual error, correlation 0.80 to 0.56. The recorded verdict reads that the grammar rather than the objective is the limit; the document says why that over-claims, since pinning one of the same seven had produced the arc's best visual result. A token's parameters are not observables of the teacher even when they share a name and units. |
| `docs/fire-pin-one.md`, `poc/fire_pin_one.py` | Each measured constant pinned alone: six of eight improve the look, two improve the fitting error as well, and the two that fail are the two predicted in advance to conflate ensemble with per-parcel quantities. Combining is not additive. Carries the correction that the static-blob reference is scene-dependent, 0.99 where the teacher barely moves and 0.80 to 0.86 where it sways, which re-reads every correlation claim in the preceding documents. |
| `docs/math-track-rgre-ml1-prereg.md`, `docs/math-track-rgre-ml1-results.md`, `poc/rgre_ml/` | RGRE-ML-1: the procedure as a model-growing and deferral method for structured models, on 114 fresh cases in a fourth domain. Outcome A: its selection rule is matching pursuit and is named so; what it adds is an out-of-vocabulary detector (AUC 0.96) and a sequencing protocol (full two-step recovery). The consumer-space residual halves the diagnosis when a consumer is thresholded, so diagnose on the field and score on the consumers; the borrowed threshold fails a third time; the deferral claim turns out to be unmeasurable by the frozen case design (measured in RGRE-ML-1b). |
| `docs/math-track-rgre-ml1b-prereg.md`, `docs/math-track-rgre-ml1b-results.md`, `poc/rgre_ml/` (`--mixed`) | RGRE-ML-1b: the deferral claim on 36 mixed cases (one missing module plus one foreign term). Holds by the frozen bars, narrowly: deferring where the residual is unexplainable beats deferring where it is large on 64% of cases and by about 2% of the error in median; the margin over random deferral in median is 0.001, and the growth step took the missing module on only 42% because two of the four foreign terms are partly absorbable by the pair module. |
| `docs/fire-diag-space.md`, `poc/fire_diag_space.py` | Cross-check of RGRE-ML-1's diagnosis-space finding against fire: step-0 picks on nine scenes from the consumer residual and from the raw field capture the same value (medians 0.85 and 0.86) and find the oracle on two and three scenes. The effect does not appear where the consumers are smooth or averaged thresholds, so the rule narrows to per-sample decision consumers, and the fire arc's diagnoses stand. The support templates put the mechanism ahead of the value at step zero, an observation not acted on. |
| `docs/math-track-rgre-ml2-prereg.md`, `docs/math-track-rgre-ml2-results.md`, `poc/rgre_ml/real.py`, `poc/rgre_ml/run_real.py`, `poc/rgre_ml/data/` | RGRE-ML-2: the procedure on six real regression datasets, 30 splits, 240 growth steps. Outcome D: selection captures 0.48 of the oracle because the useful modules on real data are free-shape (bumps, sinusoids on 233 of 240 steps) and a tangent at a canonical on-state does not say where their fit will end; on the 7 fixed-shape steps it is the oracle every time. The abstention quantity separates shuffled from real targets on 30 of 30 splits and predicts a wasted growth step at AUC 0.84 against 0.62 for the step index, mostly between datasets. Deferral by orthogonality ties magnitude and is dropped for real data. The grown model beats linear and kNN on 83% of cases. |
| `docs/math-track-rgre-ml3-prereg.md`, `docs/math-track-rgre-ml3-results.md`, `poc/rgre_ml/ml3_run.py`, `poc/rgre_ml/ml3_score.py` | RGRE-ML-3: the one percent stopping constant replaced by a permutation test on the procedure's own statistic, scored on the RGRE-ML-2 path. Half: it beats the constant on 15 cases to 9 and in median regret, grows where the constant stopped at zero and declines on shuffled targets every time, and fails the mean-regret bar on one case where an exponential module extrapolated on a test outlier; the shuffle budget (9, 19, 49) changes the stop on one case of 30. |
| `docs/linearisation-gap.md`, `poc/fire_lin_gap.py` | The linearisation gap, the fraction of a fitted repair outside the tangent span the ranking read, measured on 240 real-data steps and nine fire scenes. Projection captures full value where the gap is under 0.1 and half where it is over 0.25, in both domains; in fire the plume's rise, the oracle's first step on five scenes of nine, has a gap of 0.98 and was invisible to the projection on every scene. A dictionary check for the next run. |
| `docs/math-track-f6-prereg.md`, `docs/math-track-f6-results.md`, `poc/f6_experiment.py`, `poc/f6_score.py` | F6: the dictionary check and the constant-free stop folded into the fire workflow, fifteen scenes, three selection rules, eight steps, the full oracle at every step. Outcome B with the tree's description of B wrong: fitting the six large-gap classes and projecting the rest takes per-step value from 0.45 to 1.00 of the oracle at half its cost and beats the arc's selector on 14 scenes of 15, reaching 0.90 of the oracle's terminal gain against a bar of 0.95; the check transfers to six unseen scenes at 86%, with `amp` and `deflect` changing sides along a path. The shuffle-null stop never stops in fire, as predicted: the residual is structured everywhere and reachable almost nowhere. |
| `docs/xi-hankel-ladder-check.md`, `poc/xi/` | Side track: exact-arithmetic check of a handed-over draft on an alternating spectral ladder for the xi Hankel kernel. Every checkable claim holds; the constants depend only on the quadratic jet; one corollary's factor of two is corrected. |
| `docs/planar-triples-gaussian-frontier.md`, `poc/hyper/` | Side track, continued: the second note checked exactly (two corrections), the degree-six cumulant test run to k = 30, the marginal central limit theorem completed, the parity-mobile obstruction removed so the joint Gaussian law follows, the critical surface expanded exactly so the first unforced joint cumulant constants are exact rationals, a literature check that places the underlying series in Arquès 1986, and the explicit bridge: the parity-mobile system is the Arquès parametrisation, the series is `pqr(1-p-q-r)`, proved from the mobile side; the exact joint coefficient is a Lagrange-Good triple sum with no product form, and the local limit constant and the large-deviation rate function from the fold are confirmed against exact coefficients to k = 301. |
| `docs/planar-triples-transverse.md`, `poc/hyper/` | Side track: proof of a handed-over conjecture, `Q = M^2/(1+M)` for the colour-imbalance second moment of genus-zero permutation triples, by symmetry, Euler and one vertex-pointed bijection; exact verification to order 24 in the data and 96 in the series; a validated uniform sampler of planar hypermaps with exact-moment oracles. |
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

RGRE-1b (`docs/math-track-rgre1b-*.md`) is the short replication that
RGRE-1's result demanded. RGRE-1 identified, post hoc on its own cases,
that plain per-direction residual ownership beats the coherence-weighted
score it had frozen. RGRE-1b freezes that simpler rule, carries RGRE-1's
abstention threshold over without recalibration, and runs 30 fresh cases
on a new seed. All four bars hold: median oracle value captured 1.00
(mean 0.98) while evaluating a sixth of the repair space, five of five
out-of-vocabulary cases abstain with no false abstention among the 24
known, and mixtures recover 0.93 of the two-step oracle in median. The
rule it replaces differs on six cases and is worse on all six, including
both regimes the preregistration targeted. Identity rose from 0.69 to
0.96 against the oracle's class. One case remains below the bar, a corn
tail defect read as unary, which is the same overlapping-tangent problem
W4 met in water and the thing to watch in fire.

RGRE-1 (`docs/math-track-rgre1-*.md`) froze the residual-guided
procedure itself, mechanistic only (projection, localisation, coherence,
cost, no classifier), and tested it on 78 fresh cases: 60 isolated
defects across seven classes in the corn and water domains, 12
two-defect mixtures, 6 out-of-vocabulary cases. By the frozen outcome
tree the result is A: the median oracle value captured is 1.00 while
evaluating a sixth of the repair space, mixtures recover 0.88 of the
two-step oracle in median with the first class's ownership collapsing
and the second's rising after a correct first repair, and five of six
unknowns abstain with 4 of 72 known cases falsely abstaining. Three bars
fail and they are the content: the coherence-discounted score and
abstention on known cases cost value against a class-free per-direction
projection baseline that never loses (mean 0.94 against 0.82), because a
lone template class is undiscounted while coherent tangent classes are
cut by 0.7 to 0.9; identity does not fall with coherence; and
re-diagnosis re-commits to a wrong class after a worthless repair. The
procedure to carry forward is the projection without the weighting.

B5 (`docs/math-track-b5-*.md`) returned to the corn path to test the
procedure itself on five fresh trajectories, a corner-sharpness series
and a dwell series: does the smooth-only residual localise at a defect
class before any repair, and does the class's representation repair
paths never seen? Verdict by the frozen rules: failure, five bars missed.
Three of the misses are defects of the frozen definitions that the data
exposes (the stop mask excluded the terminal stop, which holds 73% of the
residual; an enrichment bar is ill-posed on a featureless path; a
position-only baseline cannot represent a straight walk at all). What
held: corners hold 99.9% of the smooth-only residual on the corner paths
and none of a difficult smooth control; stop events make every stop path
reachable at a count identical across 0, 0.5, 1 and 2 s of dwell; the
corner allocation calibrated on one probe cuts 14 to 29% on every fresh
corner path at the perceptual threshold; the singular mass is flat as a
corner sharpens from 0.8 to 0.2 s under that allocation; and B4's
tangent law with no fitted constant predicts all five fresh vertex counts
within a factor 1.5. What failed substantively: the class-free tangent
criterion I predicted would dominate wins only for sharp turns at tight
tolerance and loses for spread turning, so the class does not dissolve
into a coordinate here and the regime decides.

W4 (`docs/math-track-w4-*.md`) tested whether W3's missing degree of
freedom was an event coordinate rather than a shape parameter, on three
amplitudes the teacher had never been run at (3, 6, 10 times base). All
four frozen hypotheses held: the fixed token's residual already points
along the time tangent before any shift is fitted; a linear delay law
calibrated at one amplitude predicts the fitted shift within 0.5 ms at 3
and 6 times base and 11 ms at 10 times; one timing number beats one
dispersion number at every new amplitude; and once timing is free the
dispersion slope collapses to zero. The tangent-coherence prediction also
held: the dispersion parameter's tangent is 82% aligned with the time
tangent, the envelope parameters' below 10%, which is why W3's optimiser
could counterfeit a time shift with g_eff. The runtime fix is one banked
number per token and no extra operations. The base-amplitude floor is 98%
orthogonal to every tangent of the token, so it needs a different atom,
and water pauses here.

W3 (`docs/math-track-w3-*.md`) conditioned the splash token's parameters
on cause amplitude, `theta(A) = theta_0 + theta_1 log A`, and asked whether
that beats adding a pair-interaction term. Verdict by the frozen rules:
failure. Two of five conditioned quantities carry all of the nonlinearity
the family can express (a saturating gain, exponent 0.75 to 0.8, and a
dispersion stiffening of 2.4% per doubling); damping, front speed and
cutoff carry none, so the predeclared order scored the wrong pair and the
knee test failed. Conditioning recovers half of the large-amplitude error
and stops, at the calibration point as well as on extrapolation, and the
pair residual stays 80 to 95 percent single-cause, so the predicted
transition to interaction-dominated residuals did not happen. Per
parameter, unary conditioning is still nine to twelve times more efficient
than pair terms, and pair terms fitted before the unary atom is adequate
transfer negatively. A post-hoc residual diagnostic (unregistered) finds
the remaining residual is axisymmetric and mostly gain and phase, and a
direct check shows the phase part is an amplitude-dependent onset time:
starting the base token 36 ms earlier at four times base amplitude and 77
ms earlier at eight times beats the dispersion slope with the same
parameter count and makes it vanish. The event time was not among the
parameters W3 allowed to depend on amplitude, which is what the next
preregistration should condition.

W2 (`docs/math-track-w2-*.md`) used W1's data only: with the observation-order
exponents fixed by theory and two coarse grids per curve, the grid needed at
every held-out tolerance is predicted within one step (30 of 30, against a
two-step average miss for a two-point power-law fit) and the binding
consumer in 69 of 69 tolerance pairs. Bicubic wins everywhere in range, so
the representation-winner test cannot yet separate the theory from a
constant choice.

W1 (`docs/math-track-w1-*.md`) transferred the laws to a mildly nonlinear
water teacher. The observation-order law held with four predicted
exponents (bilinear height -0.87 vs -1, slope -0.40 vs -0.5; bicubic
-1.91 vs -2, -1.23 vs -1.5). The logarithmic liveness law failed because
the water token's envelope decays as a power of time (geometric spreading,
weak damping), which the first review had flagged. Superposition of
independent splash tokens is within 1.3% at game amplitudes and fails only
above four times that within 0.3 m; the nonlinearity is single-cause.

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

Two side tracks sit outside the runtime work. `docs/xi-hankel-ladder-check.md`
checks a handed-over draft on an alternating spectral ladder for the xi
Hankel kernel in exact arithmetic: every checkable claim holds, the
constants depend only on the quadratic jet of the kernel, and a factor of
two in one corollary is corrected. `docs/planar-triples-transverse.md`
proves a handed-over conjecture on genus-zero permutation triples, that
the second moment of the colour imbalance is `M^2/(1+M)` in terms of the
cycle-pointed series, by a route the note did not take: symmetry and
Euler's relation reduce the signed statistic to the second moment of the
vertex count, which one vertex-pointed bijection gives in closed form.
Each step is verified exactly against the character-formula data to
order 24 and the series to order 96, and the same bijection becomes a
uniform sampler of planar hypermaps whose output is checked against the
proved moments.
A second note on the same problem is checked in
`docs/planar-triples-gaussian-frontier.md`: two of its formulas are
corrected, its degree-six cumulant test is run on exact data to k = 30,
the marginal central limit theorem it sketches is completed, and the
obstruction it met on the parity-refined mobile is removed by not
weighting the pointed vertex, after which the joint Gaussian law it
conjectures follows from standard theorems.

The bend arithmetic has now been measured on real hardware
(`docs/bendbench-results.md`), which closes the oldest open item in the
Quest notes. A WebGL2 harness draws the identical field from the identical
instance buffers in one instanced call and varies only the per-vertex
arithmetic, timing it with a forced GPU sync rather than frame deltas,
which quantise to whole vsync periods. On a phone, all six terms cost 37%,
36% and 7% of frame time across three load shapes at 400,000 to 575,000
stalks, and under 1% of a 72 Hz budget once scaled to the 15,000 stalks a
real field uses. Baking the field to a texture and sampling it per
instance, which the notes recommended on cost-model grounds, costs nothing
measurable on any load shape. The uncomfortable finding is that the same
arithmetic in the same compiled program costs eight times more per vertex
invocation in one preset than in another, so the op-count cost term the
compositional search uses does not predict milliseconds and should be
treated as a tie-breaker rather than a budget.

## Where this should go next

1. Replace the synthetic walks with recorded SquishLabVR hand and foot
   tracks (see `docs/data-sources.md`). Hands and crouching are different
   causes from a walking cylinder.
2. Profile on a headset. The WebGL2 harness has now done this on a phone
   (`docs/bendbench-results.md`); the Unity/HLSL path on Quest is still
   unmeasured, and the measured milliseconds still need to replace the op
   counts in the search's cost term.
3. Then snow (Taichi MPM teacher), then water (corrected ring wave), then
   crowds (real pedestrian data), then fire.
