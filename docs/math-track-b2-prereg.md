# Math Track B2: Causal Path Complexity. Preregistration (frozen before any run)

## Object under test

A cause worldline `Gamma(t) = (p(t), t)` on `0 <= t <= T`, a consumer `G`,
and a compressed worldline `p-hat(t)`: piecewise linear in `t` between kept
vertices, time preserved exactly. Chord error over a segment of duration
`h` is bounded by `h^2 / 8 * sup |p''|`; with a locally Lipschitz consumer
the local error is about `h^2 / 8 * L_G(t) |p''(t)|`. Define

```
q_G(t)  = L_G(t) |p''(t)|
C_G[p]  = integral_0^T sqrt(q_G(t)) dt
```

Prediction: `N_G(eps) ~ C_G[p] / sqrt(8 eps)` up to compressor constants,
and the claim to falsify is `N_G(eps) proportional to C_G[p]` at fixed
`eps`. Isotropic sensitivity only; no metric tensor in this run.

## Consumer and error (frozen)

The consumer is the fitted two-term cheap model (wake + presence, parameters
from `poc/results/gpu_sweep.json`) evaluated on the 1600-stalk grid at 60 Hz
for 10 s, driven by a path token. Ground truth for each trajectory is the
model driven by the dense 200 Hz worldline. No teacher is involved, so the
measurement isolates path compression.

- Primary error: RMS over all frames of the bend difference on stalks
  within 1.5 m of the dense path, in metres (absolute).
- Secondary (recorded, no hypothesis): sup over those stalks and frames.
- Thresholds, fixed from the mean reference local RMS of 32.56 mm at 2, 4, 8
  and 16 percent: `eps` in {0.65, 1.30, 2.61, 5.21} mm. Primary thresholds
  for H2 and H3 are 1.30 and 2.61 mm; 0.65 and 5.21 are reported.
- `N_G(eps)` = the smallest vertex count among the compressor's tolerance
  sweep whose error is at or below `eps`.

## Compressor (frozen)

Weighted time-parametrised Douglas-Peucker on the 200 Hz worldline: a
segment `[a, b]` is split at the sample maximising
`L_G(t_i) * |p_i - p-hat(t_i)|` where `p-hat` is linear in `t` between the
endpoints, whenever that maximum exceeds the tolerance. Endpoints always
kept. Tolerance sweep: 48 values, geometric from 1.0 m to 0.5 mm.
Consumer A has `L_G = 1`.

## Acceleration estimator (frozen)

Analytic `p''(t)` is available for every trajectory (they are built from
analytic speed and heading). It is primary. The sampled estimator is:
200 Hz samples, Gaussian smoothing of position with sigma 25 ms truncated
at 4 sigma, two applications of `numpy.gradient` (second-order central,
one-sided at the ends). Never tuned per trajectory. Both `C_G` values are
reported; disagreement is attributed to the estimator, not the theory.

## Trajectory family (frozen, `poc/reactive/worldlines.py`)

All 10 s at 200 Hz, walking ends by 8.5 s, 0.5 s smoothstep ramps at every
start and stop, inside the 10 m field.

| name | description | expected C_G (from the track) |
|---|---|---|
| straight | constant speed, 8 m in 8 s | very low |
| s_curve | one sinusoidal heading swing, constant speed | low / moderate |
| stop_start | four 2 m dashes with 0.6 s pauses, straight | moderate |
| slalom | three heading periods, constant speed | moderate / high |
| zigzag | six sharp turns of 1.4 rad over 0.15 s, constant speed | high |
| wandering | slow heading wander, two pauses, one reversal | highest |
| two_speed | straight, slow then fast (acceleration without turning) | probe |
| circle | constant-speed circle, radius 2.5 m (turning without speed change) | probe |

The two probes are additions to the track's six; they test the isotropic
form directly and are included in H1, H2, H3, H6 (n = 8).

## Control for H4 (frozen)

The wandering trajectory twice. Consumer A: `L_G = 1`. Consumer B:
`L_G(t) = 1` while `p(t)_x < 4.5` m (40 percent of walking time), `alpha =
0.05` otherwise; B's error metric weights each stalk by 1 or `alpha` by the
same rule (weighted RMS). `C_{G_B} = integral sqrt(L_G(t) |p''|) dt`. Also
recorded: B's error when the path is compressed with the *unweighted*
compressor (H4b).

## Hypotheses and bars (frozen)

- H1: Spearman(`C_G`, `N_G(eps)`) > 0.8 at each threshold, n = 8.
- H2: linear fit `N = a + b C_G` has R^2 > 0.8 at the primary thresholds.
- H3: with `Z = N sqrt(eps) / C_G`, the coefficient of variation of `Z`
  over all (trajectory, threshold) pairs is below half that of `N`.
- H4: `N_{G_B}(eps) < N_{G_A}(eps)` at every threshold. H4b: the weighted
  compressor needs fewer vertices than the unweighted one for consumer B.
- H5: per trajectory, 12 equal time bins over the walking interval;
  Spearman between kept-vertex density at the 2.61 mm threshold and the
  bin mean of `sqrt(q_G)` exceeds 0.6 for the median trajectory.
- H6: `C_G` predicts `N_G(eps)` better (higher Spearman and R^2 at the
  primary thresholds) than path length, total turning `integral |theta'|
  dt`, `integral |p''| dt`, and the number of stops (downward crossings of
  0.05 m/s before the final stand). Dense sample count is constant here
  and is not a baseline.

## Outcome rules (frozen)

Strong success: H1, H2, H3, H4 and H6 hold. Partial: H1 and H4 hold, H2 or
H3 fail. Failure: a baseline in H6 matches or beats `C_G`, or H1 fails.
Results go in `poc/results/b2.md`; nothing above is edited after the run.
