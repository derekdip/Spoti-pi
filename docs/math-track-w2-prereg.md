# Math Track W2: predictive representation selection. Preregistration (frozen before any analysis)

Uses only W1 run 2 data (`poc/results/w1.json`, Q2 errors for bilinear and
bicubic representations under the height and slope consumers on grids
n in {12, 16, 24, 32, 48, 64, 96, 128, 192, 256}, N = n^2). No new
simulation. Cost is `C = N` (W2-A). W2-B (measured runtime cost) is not run:
no measured costs exist and none are manufactured from operation counts.

## Frozen model

`E_RG(N) = a_RG N^{-alpha_RG}` with `alpha` fixed from the observation-order
law, `alpha = (p_R - k_G) / d`, `d = 2`: bilinear height 1, bilinear slope
1/2, bicubic height 2, bicubic slope 3/2. Only `a_RG` is calibrated:
`log a = mean_j [log E_j + alpha log N_j]` over the calibration points.

## Frozen calibration and holdout

Calibration points: `n = 64` and `n = 96` for every curve (the two coarsest
grids inside the regime where the W1 exponents were fitted; the law is
asymptotic and claims nothing where the field is unresolved). Held-out
grids: 128, 192, 256 (and 12 to 48, where the model is expected to fail
and which only enter as candidates for the actual smallest grid).

Tolerance targets: `eps` in {0.3, 0.2, 0.14, 0.1, 0.07, 0.05, 0.035,
0.025, 0.018, 0.0125, 0.009, 0.006, 0.004, 0.003, 0.002}. A target is
*reachable* for a representation if some grid in the sweep has `E <= eps`.
Predicted grid `n-hat(eps)`: the smallest sweep grid with
`N >= (a / eps)^(1/alpha)`. Actual grid `n*(eps)`: the smallest sweep grid
with measured `E <= eps`. `D = |rank(n-hat) - rank(n*)|` in sweep steps.

## Hypotheses and bars (frozen)

- **H1 resolution.** Over reachable (curve, target) pairs, at least 75
  percent have `D <= 1`.
- **H2 winner.** For each consumer and target where both representations
  are reachable and the actual cheaper one (smaller `n*`) is unique, the
  predicted cheaper representation (smaller `n-hat`) matches the actual in
  at least 80 percent of cases.
- **H3 crossover.** Predicted `log eps* = (alpha_B log a_A - alpha_A log
  a_B) / (alpha_B - alpha_A)` per consumer. Empirical crossover: the
  target between which the actual cheaper representation switches. If an
  empirical crossover exists among the targets, the predicted one must lie
  within one target interval of it; if none exists, the prediction must
  lie outside the target range on the side consistent with which
  representation wins throughout.
- **H4 order.** `eps*` for slope is looser (larger) than `eps*` for
  height, judged where both are observable or both predicted.
- **H5 baselines.** Baselines: A always bilinear; B always bicubic; C
  choose the representation with lower error at `n = 64`; D unconstrained
  two-point power law (alpha fitted from the same two calibration points).
  The frozen-exponent model must beat D on held-out log-error (mean
  `|log E-hat - log E|` over grids 128, 192, 256) or on mean `D` over
  reachable targets; both are reported.
- **H6 binding consumer.** For every pair of targets `(eps_h, eps_n)`,
  each representation's required grid is the max over the two consumers,
  and the binding consumer is the one attaining the max. For the actually
  cheaper representation at each pair, the predicted binding consumer
  matches the actual one in at least 80 percent of non-tied pairs.
- After scoring: the deployment map over `(eps_h, eps_n)` with the
  predicted cheapest representation and the actual decision overlaid.

## Outcome rules (frozen)

Strong: H1, H2 and H5 hold, H3/H4 consistent where observable. Partial:
H1 holds, H2 or H3 fails. Failure: H5 fails (frozen exponents extrapolate
worse than the two-point fit) or H2 falls below 50 percent. Results go in
`poc/results/w2.md`; nothing above is edited after the run.
