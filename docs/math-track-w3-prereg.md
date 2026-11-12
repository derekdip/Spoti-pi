# Math Track W3: unary nonlinearity before interaction complexity. Preregistration (frozen before any run)

Question: when nonlinear error is primarily single-cause, does improving
the atom beat adding interaction order? Teacher, token and consumer as in
W1 (`docs/math-track-w1-prereg.md`): mildly nonlinear water, the chirp
token with parameters `theta_0` fitted at base amplitude (`poc/results/
w1.json`), height consumer, RMS within 2 m from 0.15 s.

## Frozen conditioned family

`theta_j(A) = theta_j0 + theta_j1 log(A / A0)`, `A0 = 1`, `theta_j0` frozen
from W1. Amplitude gain: the token amplitude scales as `A^(1 + s1)` (`s1 =
0` is the fixed token). Shape parameters allowed to depend on amplitude,
in the predeclared cumulative order (damping first because the dominant
nonlinearity is amplitude-dependent damping, then dispersion because the
cubic restoring term shifts the effective gravity, then front speed, then
the viscous cutoff):

| model | conditioned quantities | conditioned parameters |
|---|---|---|
| M0 fixed | none | 0 |
| M_gain (H5 ablation) | gain only | 1 |
| M1 | gain + `lam` | 2 |
| M2 | M1 + `g_eff` | 3 |
| M3 | M2 + `v_max` | 4 |
| M4 | M3 + `k_cut` | 5 |

## Calibration and holdout (frozen)

Amplitudes available: 0.5, 1, 2, 4, 8 times base. Calibration: 1 and 4
(with `theta_0` frozen at the A = 1 fit, the slopes are determined by
A = 4). Holdout: 0.5 (extrapolation down), 2 (interpolation), 8
(extrapolation up). Slopes are fitted by Powell on W1's fit subset at
A = 4; all scores are on W1's evaluation set.

## Recoverable error (frozen definition)

The fixed token's error at A = 0.5 equals its error at A = 1 (0.344), so
0.344 is the token family's own misfit and is not amplitude-shaped.
Recoverable error: `E_rec(A) = max(E(A) - E_floor, 0)` with `E_floor =
E_fixed(1)`. H1, H2 and H5 are scored on `E_rec` over the holdouts where
the fixed token has `E_rec > 0.05` (A = 2 and 8); at A = 0.5 the
conditioned token must not degrade: `E_cond(0.5) <= 1.1 E_fixed(0.5)`.

## Hypotheses and bars (frozen)

- **H1 unary generalisation.** Median over {2, 8} of
  `(E_rec_fixed - E_rec_cond) / E_rec_fixed >= 0.5` for M4, and no
  degradation at 0.5.
- **H2 approach to the interaction floor.** `R(A) = E_rec(A) / I12(A)`
  with `I12` W1's measured pair interaction at the nearest separation
  (0.281 m). Median over {2, 8} of `R_cond / R_fixed <= 0.25` for M4.
- **H3 unary beats pair complexity per parameter.** Pair models added to
  the *fixed* unary pair reconstruction: P1 = a scaled copy of the base
  chirp centred at the pair midpoint with amplitude `c1 A_i A_j`
  (1 parameter); P2 = P1 with its own decay rate (2 parameters). Fitted
  on the (A = 4, D = 0.281) pair residual. Scored on held-out pairs
  (A in {2, 8}, D in {0.281, 0.609}). Efficiency `eta = (error reduction on
  held-out pairs) / (parameters added)`. Prediction: `eta(M_gain) >= 2
  eta(P1)` and `eta(M1) >= 2 eta(P2)`.
- **H4 residual structure.** On every held-out pair, the true cross-term
  `pair - single_i - single_j` accounts for a larger share of the
  remaining residual under the conditioned unary model than under the
  fixed one: `||cross|| / ||pair - condU_i - condU_j|| > ||cross|| /
  ||pair - fixedU_i - fixedU_j||`.
- **H5 shape beats gain.** Median over {2, 8} of `E_rec(M1..M4) <
  E_rec(M_gain)`, i.e. amplitude-only scaling is not enough.
- **Knee (reported).** Cumulative gain from M_gain to M4; whether two
  conditioned quantities (M1) recover at least 90 percent of M4's gain.

## Outcome rules (frozen)

Strong: H1, H2, H3, H5 hold. Partial: H1 and H5 hold, H2 or H3 fails.
Failure: H5 fails (amplitude-only scaling is as good), or H1 fails.
Results go in `poc/results/w3.md`; nothing above is edited after the run.
