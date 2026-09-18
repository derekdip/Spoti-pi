# Math Track B2 results: causal path complexity

Preregistration: `docs/math-track-b2-prereg.md` (frozen, with Amendment 1).
Raw outputs: `poc/results/b2.md`, `b2.json`, `b2.png`. Run 1, invalid
because of the stop degeneracy, is kept in `b2_run1.md`.

## Verdict by the frozen rules: failure at the primary thresholds

The outcome rule said: failure if a baseline in H6 matches or beats `C_G`,
or if H1 fails. Both happened at the primary thresholds (1.30 and 2.61
mm). Total turning `integral |theta'| dt` predicts the required vertex
count better than `C_G` there. The loose threshold (5.21 mm) is a clean
success for `C_G`. The tightest threshold (0.65 mm) was floor-limited for
the slalom and zigzag (the tolerance sweep's finest setting did not reach
it) and is not evaluated, as the preregistration allowed.

| hypothesis | bar | 1.30 mm | 2.61 mm | 5.21 mm | verdict |
|---|---|---|---|---|---|
| H1 Spearman(C_G, N) | > 0.8 | 0.69 | 0.79 | 0.95 | fails primary, passes loose |
| H2 R^2 of N = a + b C_G | > 0.8 | 0.48 | 0.66 | 0.75 | fails |
| H3 CV(Z) < 0.5 CV(N) | | CV(N) 0.76, CV(Z) 0.36 | | | passes, narrowly (0.36 vs 0.38) |
| H4 N_B < N_A at every threshold | | 2 of 4 thresholds | | | fails as stated |
| H4b weighted compressor < unweighted for consumer B | | 4 of 4 | | | passes |
| H5 median Spearman of vertex density vs sqrt(q) | > 0.6 | 0.78 | | | passes |
| H6 C_G beats all baselines | | turning 0.98 / 0.92 vs C_G 0.69 / 0.48 | turning 0.88 / 0.66 vs 0.79 / 0.66 | C_G 0.95 vs turning 0.73 | fails primary |

`C_G` from the frozen sampled estimator agrees with the analytic value
within 2% on seven trajectories and 14% on the zigzag (smoothing rounds
the sharp turns). The estimator is not the cause of any failure.

## What the residuals say

Two trajectories carry the failure, in opposite directions.

**Zigzag: far more vertices than `C_G` predicts.** `C_G = 3.98`, the
second lowest, but 71 vertices at 1.30 mm, as many as the circle at
`C_G = 8.84`. Six turns of 1.4 rad in 0.15 s each. The square root in
`C_G` is the problem: a turn of angle `Theta` taken in time `tau` at
speed `v` contributes `sqrt(v Theta / tau) * tau = sqrt(v Theta tau)` to
`C_G`, which goes to zero as the turn sharpens, while the compressor
still needs several chords inside the turn to hold a millimetre
tolerance across 1.4 rad. `C_G` is the correct asymptotic density for
smooth curves and misses a kink cost that scales with turning angle and
does not vanish. That is exactly why total turning wins at tight
tolerance: three of the eight trajectories are dominated by turns.

**Stop/start: far fewer vertices than `C_G` predicts.** `C_G = 8.59`,
the third highest, but only 34 vertices at 1.30 mm. Its acceleration is
entirely along the track (eight 0.5 s ramps at 7.5 m/s^2 on a straight
line). The consumer is much less sensitive to along-track error than to
across-track error: along-track error only shifts pass times, across-track
error moves the trail itself, and the wake kernel is sharp across the
trail (`q` near 1.2, `w` 0.13 m). The isotropic form `L_G |p''|` charges
both directions equally and overcharges speed changes.

**The two probes agree with this reading.** `two_speed` (acceleration
without turning) needs 16 vertices at `C_G = 2.77`; `circle` (turning
without speed change) needs 69 at `C_G = 8.84`. Per unit of `C_G` the
turning probe costs about 1.4 times what the speed probe costs.

**H5 supports the mechanism where it can be tested.** Vertex placement
tracks `sqrt(q)` at 0.83 to 0.98 on the five trajectories where `q`
varies. On the slalom (0.11) and circle (0.23) `|p''|` is nearly
constant, so the predictor is flat and the correlation is undefined in
practice; that is a limit of the test, not evidence against it.

**H4 is a commensurability problem, not a physics one.** Consumer B's
weighted error normalises by the weights, so its thresholds are not the
same metres as consumer A's; comparing `N_A(eps)` with `N_B(eps)` at
equal `eps` was not well posed. The well-posed comparison, H4b, holds at
every threshold: for the same consumer, the compressor that knows what
the consumer cares about needs fewer vertices (40 versus 53 at 2.61 mm).
Geometry was identical, so that part of the claim stands.

## What this means for the branch

By the frozen rules this is a failure of the *isotropic* functional at
tight tolerance, and the track said in advance what to do then: inspect
the residuals. They point at two corrections, both stated before the run
as possibilities and neither tuned to the data:

1. **Anisotropy.** Replace `L_G |p''|` with `(p''^T M_G p'')^{1/2}` where
   `M_G` weights across-track acceleration more than along-track. The
   stop/start and two-speed results fix the along-track weight; the
   circle and s-curve fix the across-track weight.
2. **A kink term.** Add a turning-angle term so that sharp turns keep a
   finite cost as their duration goes to zero:
   `N(eps) ~ C_G / sqrt(8 eps) + kappa(eps) * integral |theta'| dt`.
   The zigzag fixes `kappa`.

The honest statement of where the theory stands: at loose tolerance the
smooth-curve law ranks trajectories almost perfectly (0.95) and beats
every baseline; at tight tolerance the required representation is
governed by turning, which the square-root functional cannot see. A
two-term anisotropic law is the natural B3, and it should be preregistered
with `M_G` and `kappa` fixed from the two probes only, then tested on the
other six plus new trajectories.

## Protocol notes

- Amendment 1 (stops are events) was declared after run 1 and before run
  2 and is recorded in the preregistration. It exposed a real property of
  the consumer: the nearest-point pass time is not Lipschitz in path
  position where speed vanishes.
- The 0.65 mm threshold needs a finer tolerance sweep to be evaluable for
  high-curvature paths.
- The compressor's stop vertices count toward `N`; they are 4 to 16 per
  trajectory and do not change any verdict.
