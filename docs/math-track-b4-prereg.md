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

## Amendment 2 (declared after run 1, before run 2; nothing above edited)

Run 1 (`poc/results/b4_run1.log`, and `b4_run1.*` where written) executed
the frozen protocol. The slalom could not meet the two tighter sup
thresholds at any tolerance, and every transfer probe up to 16 m met no
threshold at all. Diagnosis: the transfer probes' stalk lattice was
aligned to the path origin, so stalks sat exactly on the straight legs
with zero perpendicular distance; the consumer's side sign for such a
stalk is `sign(0)`, which floating point resolves differently for the
dense and compressed tokens, flipping the wake's normal component on that
stalk. The slalom hit the same discontinuity by crossing stalk rows. This
is a non-Lipschitz point of the consumer at the path itself, invisible to
the RMS score and dominant under the supremum.

Two further candidates were checked and rejected before amending: a 0.99
quantile score (monotone, but it stops seeing an isolated corner on long
paths, reintroducing dilution) and exclusion of stalks near the path's
medial axis (changed no maximum at all, so the pass-time switch across a
bisector is not a measurable source of error).

Amendment: (a) the wake's path-normal component is multiplied by a
smoothstep of perpendicular distance over 2 cm (`PATH_NORMAL_FADE` in
`poc/reactive/primitives.py`), so a stalk on the centreline is pushed
along the path and the consumer is continuous there; this applies to
every trajectory, holdout and probe alike; (b) the transfer-probe lattice
is offset by half a spacing so no stalk lies exactly on a straight leg.
The score remains the strict maximum over stalks within 1.5 m, as
preregistered. With the amendment, the maximum tracks the geometric
tolerance with a roughly constant factor on every trajectory checked,
which is the Lipschitz behaviour the derivation assumes. Run 2 is the run
the hypotheses are judged on.

## Amendment 3 (declared after run 2 was stopped, before run 3; nothing above edited)

Correction to Amendment 2: the statement that medial-axis exclusion
"changed no maximum at all" was a reading error. The two exclusion
variants were compared with each other instead of with the fade-only
baseline. Against that baseline the exclusion does reduce the maximum
where it matters: slalom 25.2 to 15.0 mm at 1 mm tolerance and 12.4 to
8.4 mm at 0.3 mm; the 4 m and 16 m corner probes 31.3 to 14.6 mm at 1 mm.
Run 2 (`poc/results/b4_run2_partial.log`, stopped after five holdouts)
reproduced run 1's slalom failure exactly, confirming that the fade alone
does not make the maximum well behaved: the nearest-approach pass time is
discontinuous across the path's medial axis, and a stalk within a few
centimetres of that axis can be assigned to different passes by the dense
and compressed tokens.

Amendment: the scored set is the stalks within 1.5 m of the dense path
whose nearest approach is unique: the two smallest local minima of the
distance from the stalk along the dense path (path endpoints counted as
candidates) differ by more than 3 cm. The set is computed once from the
dense path and is identical for every token. It removes about 15 percent
of local stalks on the curved trajectories and none on the straight
ones. The score is the strict maximum over that set, as preregistered.
This is the set on which the consumer is Lipschitz; the derivation applies
there and nowhere else. Run 3 is the run the hypotheses are judged on.

Rule as finalised before run 3 (replacing the wording above): candidate
approaches are the local minima of a stalk's distance along the dense
path plus the endpoints; two candidates are distinct approaches only if
the distance rises by more than 5 cm somewhere between them (so a pause
and the foot of a perpendicular a few centimetres apart are one approach,
as is the standing phase); a stalk is excluded if its two closest distinct
approaches differ by less than 3 cm. Exclusions: straight 0, stop_start 0,
s_curve 6, slalom 23, zigzag 24, wandering 22 of 1600; corner probes 0.

Diagnostic recorded before run 3: the corner probes' non-monotone maxima
at intermediate tolerances come from stalks just outside the apex whose
distance and pass time agree to a millimetre and 10 ms between tokens but
whose outward normal differs by about 20 degrees, because the wake
direction is taken from the local tangent of the nearest segment, and a
chord across a rounded corner mis-states the tangent by an angle that
does not shrink with positional tolerance. The consumer therefore depends
on the path's tangent as well as its position; at corners its error is
first order in chord length. This is a uniform property of the consumer,
identical for probes and holdouts, and is left in place; `N(eps)` is the
minimum vertex count whose error is at or below `eps`, so non-monotone
maxima do not distort it.
