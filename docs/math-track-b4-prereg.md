# Math Track B4: theorem-measurement alignment for the corner law. Preregistration (frozen before any run)

Everything from B3 (`docs/math-track-b3-prereg.md`) is kept: consumer
model, 10 m stalk field for the six holdout trajectories, corner rule
(`|theta'| > 3 rad/s`), kink term `K = sum 2 sin(|Theta|/2)`, mandatory
stop atoms, anisotropic smooth term with `m_perp = 1`, tolerance sweep of
64 values from 1.0 m to 0.1 mm, probe-only calibration. Two changes and
one addition, nothing else:

1. **Score: global RMS is replaced by the local supremum.**
   `E_inf = max over frames and over stalks within 1.5 m of the dense path
   of |G_dense - G_compressed|`. Thresholds, fixed from the mean reference
   peak bend of 483.8 mm at 1, 2, 4, 8 percent: `eps_inf` in {4.84, 9.68,
   19.35, 38.70} mm. Primary thresholds: 9.68 and 19.35 mm. The RMS score
   is still recorded on every run for the dilution control only.
2. **Tangential probe replaced.** `tangential_probe`: straight line, speed
   0.6 -> 1.6 -> 0.6 -> 1.2 -> 0.6 m/s with 0.8 s smooth transitions,
   never below 0.6 m/s while walking, no turning, no interior stop.
3. **Transfer-invariance probes added.** The B3 corner (90 degrees in
   0.15 s at the corner probe's cruising speed) embedded at the midpoint
   of straight walks of total length L = 4, 8, 16, 32 m, each paired with
   a cornerless twin of the same length and speed profile. The L = 8 pair
   is the B3 corner probe and calibrates `B`. Stalks for these probes are
   a 0.25 m lattice restricted to within 2 m of the dense path (the score
   only uses stalks within 1.5 m). Duration scales with length.

`N_corner(L, eps) = N(corner_L, eps) - N(straight_L, eps)`.

## Hypotheses and bars (frozen)

- **B4-H0 transfer invariance (primary).** Under the supremum score, at
  each evaluable threshold, `max_L N_corner / min_L N_corner <= 1.5` over
  L in {4, 8, 16, 32}, with every `N_corner > 0`. Dilution control: under
  the RMS score on the same runs, `N_corner(32) / N_corner(4) >= 1.5` at
  the RMS primary thresholds (1.30 and 2.61 mm). If H0 fails, the
  dilution diagnosis was wrong and the corner theory is not rescued.
- **B4-H1 ranking.** At both primary sup thresholds, over the six holdout
  trajectories, Spearman(`N_hat`, `N`) > 0.8 and greater than
  Spearman(total turning, `N`).
- **B4-H2 residuals.** Zigzag relative residual `|N - N_hat| / N` at or
  below 0.35 at both primary thresholds (B3 had 1.13 and 0.47 at its
  primaries; B2's linear fit had 0.37 and 0.24). Stop/start relative
  residual at or below 0.30 at both primary thresholds (B3: 0.18, 0.09).
- **B4-H3 cross-threshold.** H1's conditions also at 38.70 mm.
- **B4-H4 mechanism.** At 19.35 mm, at least 75 percent of corner bins
  (12 bins over the walking interval) show kept-vertex density above the
  smooth prediction scaled by the trajectory's clean-bin ratio. Clean-bin
  Spearman is reported without a bar.
- Secondary, no bars: `m_par` per threshold and its spread; `A_eps`
  against the predicted `eps^(-1/2)` scaling; R^2 of `N_hat` against `N`.

## Outcome rules (frozen)

- H0 fails: the dilution diagnosis is wrong; stop rescuing the corner law.
- H0 holds, H1 or H2 fails: the corner law is wrong under a matched
  metric; total turning is the predictor at tight tolerance; no B5.
- H0, H1, H2 hold: the singular term is provisionally established under
  the certificate (supremum) metric.

Results go in `poc/results/b4.md`; nothing above is edited after the run.
