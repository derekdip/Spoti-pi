# Math Track W2 results: predictive representation selection

Preregistration: `docs/math-track-w2-prereg.md`. Data: W1 run 2, Q2 (no
new simulation). Raw outputs: `poc/results/w2.md`, `w2.json`, `w2.png`.

## Verdict by the frozen rules: strong, with one caveat that must be stated

| hypothesis | bar | result |
|---|---|---|
| H1 resolution within one grid step | >= 75% of reachable targets | 100% (30 of 30); mean step error 0.23 |
| H2 representation winner | >= 80% of non-tied targets | 86% (6 of 7) |
| H3 crossover | within one interval, or outside on the right side | no crossover in range; predicted 0.42 (height) and 0.73 (slope), both above the loosest target with bicubic winning throughout: consistent |
| H4 slope crossover looser than height | | 0.73 > 0.42: consistent |
| H5 beat the two-point power law | on log error or step error | log error 0.315 vs 0.370; mean step error 0.23 vs 2.17: pass on both |
| H6 binding consumer | >= 80% of non-tied pairs | 100% (69 of 69; 41 height-bound, 28 slope-bound) |

Outcome rule: H1, H2 and H5 hold with H3/H4 consistent: **strong**.

## The caveat

Within the reachable tolerance range bicubic is the cheaper representation
everywhere, for both consumers. The frozen model predicts exactly that
(both crossovers lie above 0.3, looser than any tolerance a game would
request), and the prediction is correct, but so is the dumb baseline
"always bicubic" (100%) and the "lower error at n = 64" rule (100%). The
model's 86% is one predicted tie at the loosest height target. So on this
data H2 and the deployment map cannot distinguish the theory from a
constant choice; the map has no boundary inside the range. The content of
H2 to H4 here is only that the theory places the crossovers on the correct
side, in the correct order, without seeing the held-out points.

## What is discriminating

**H1 and H5.** Calibrated on two grids (64 and 96) with exponents fixed
from theory, the model predicts the grid needed at every reachable
tolerance within one step, extrapolating to grids up to seven times
larger in cell count and errors ten to thirty times smaller. All seven
one-step misses are on the optimistic side (one grid coarser than
needed), consistent with W1's measured exponents being slightly shallower
than the frozen ones. The two-point fit through the same two calibration
points gets exponents 0.77, 0.43, 1.37 and 1.01 against the frozen 1,
0.5, 2 and 1.5 (the calibration grids are still pre-asymptotic in slope),
under-predicts resolution by two steps on average, and declares one
target unreachable that was reached. Transferred theory beats local
curve-fitting at extrapolation by a wide margin, which is the point of
the exercise.

**H6.** Over 69 tolerance pairs, 41 are height-bound and 28 slope-bound
in the actual data, and the model identifies the binding consumer
correctly in every case. This is the deployment-relevant result: when
normals bind, spending on height fidelity buys nothing, and the model
knows which regime a requested pair of tolerances is in.

## What W2 establishes

The observation-order law is predictive, not just descriptive: with the
exponents fixed by `(p_R - k_G) / d` and two coarse measurements per
curve, required resolution and the binding consumer are predicted on
held-out tolerances with near-perfect accuracy on this teacher.
Representation choice between bilinear and bicubic is correctly predicted
but not tested, because no crossover exists in range. W2-B (measured
runtime cost) was not run; there are no measured costs, and the true
deployment choice depends on the cost exponent `gamma_R` and the constant
overheads that W2-A sets to one and zero.

## Suggested next

W3 as sketched: an amplitude-conditioned token, `theta(A) = theta_0 +
theta_1 log(A / A_0)` on a small frozen subset of the chirp parameters,
with the preregistered prediction that unary amplitude dependence
recovers most of the nonlinear error before pair interactions are needed
(W1 measured cross-terms of 0.5 to 3.4 percent in the design regime
against single-splash distortion of 34 to 155 percent).
