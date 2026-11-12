# Math Track B3: smooth + singular causal path complexity. Preregistration (frozen before any run)

Builds on B2 (`docs/math-track-b2-prereg.md`, `docs/math-track-b2-results.md`).
Consumer, error metric, thresholds, compressor (with Amendment 1) and the
eight B2 trajectories are unchanged. Additions and rules below.

## Model under test

```
N_hat(eps) = A_eps * C_smooth + B_eps * K + N_event
C_smooth   = integral over non-corner time of (m_par a_par^2 + m_perp a_perp^2)^(1/4) dt,  m_perp = 1
K          = sum over corners j of 2 sin(|Theta_j| / 2)
N_event    = number of forced stop vertices (mandatory atoms, coefficient 1, not fitted)
```

`a_par = v'` (tangential acceleration), `a_perp = v theta'` (normal
acceleration), both analytic from the worldline generator.

**Corner rule (frozen).** A corner is a maximal interval where
`|theta'(t)| > 3 rad/s`; `Theta_j` is the integral of `|theta'|` over it.
The smooth integral excludes corner intervals. Justification: 3 rad/s is
about the fastest sustained heading rate of a walking human. It was chosen
knowing the family's peak rates (slalom 2.4, zigzag 14, wandering reversal
9.4 rad/s); a follow-up should vary it.

**Tolerance sweep (changed from B2).** 64 values, geometric from 1.0 m to
0.1 mm, so that the 0.65 mm threshold is evaluable for high-curvature
paths. `N(eps)` is otherwise as in B2.

## Calibration (probes only; everything else is holdout)

Per threshold `eps`, with `N* = N - N_event`:

1. `two_speed` (pure tangential acceleration) and `circle` (pure normal
   acceleration in the constant-speed part) jointly determine `A_eps` and
   `m_par`: solve `N*_two = A (m_par)^(1/4) S_two` and `N*_circle = A
   integral (m_par a_par^2 + a_perp^2)^(1/4) dt` for `A` and `m_par` by
   one-dimensional root finding in `m_par` on `[1e-4, 10]`.
2. `m_par` is a consumer property and must not depend on `eps`: the frozen
   value is the geometric mean of the per-threshold estimates over the
   evaluable thresholds; `A_eps` is then recomputed from the circle at
   each threshold with that `m_par`.
3. `corner_probe` (constant speed, one 90 degree turn of 0.15 s, `K =
   2 sin(45 deg) = 1.414`) determines `B_eps = (N* - A_eps C_smooth) / K`.

`A_eps`, `m_par`, `B_eps` are then frozen and applied to the six holdout
trajectories: straight, s_curve, stop_start, slalom, zigzag, wandering.

## Hypotheses and bars (frozen)

- **B3-H1 ranking.** At 1.30 and 2.61 mm, Spearman(`N_hat`, `N`) over the
  six holdout trajectories exceeds 0.8 *and* exceeds Spearman(total
  turning, `N`). A tie does not count.
- **B3-H2 residual repair.** Relative residual `|N - N_hat| / N` for
  zigzag and for stop_start is smaller than B2's linear-fit residual
  `|N - (a + b C_G)| / N` at the same threshold (a, b from
  `poc/results/b2.json`), at both primary thresholds. Both must shrink.
- **B3-H3 cross-threshold stability.** B3-H1's conditions also hold at
  5.21 mm and, if evaluable for all six, at 0.65 mm.
- **B3-H4 local density.** Per holdout trajectory, 12 equal time bins over
  the walking interval. Away from corners and stops: Spearman between
  kept-vertex density at 2.61 mm and the bin mean of `(a_par^2 m_par +
  a_perp^2)^(1/4)` exceeds 0.6 for the median trajectory with at least
  six non-corner bins of varying predictor. In corner bins: observed
  density exceeds the smooth prediction scaled by the trajectory's
  non-corner ratio, for the majority of corner bins.

Secondary, reported without bars: R^2 of `N_hat` against `N`; the
calibrated `m_par`, `A_eps`, `B_eps`; the B2 isotropic `C_G` Spearman for
comparison; Spearman p-values (n = 6 is small; the one-sided 5 percent
critical value is 0.83).

## Outcome rules (frozen)

Success: H1, H2, H3 hold. Partial: H1 and H2 hold, H3 fails (the law is
threshold-bound). Failure: H1 fails or H2 fails in either direction.
Results go in `poc/results/b3.md`; nothing above is edited after the run.
