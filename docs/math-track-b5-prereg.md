# Math Track B5: smooth, singular, event decomposition. Preregistration (frozen before any run)

The track owner's message calls this "B3 (return)". It is numbered B5
here because `docs/math-track-b3-*` and `b4-*` already exist and are
not edited. Question: on the corn path, does the residual of a
smooth-only representation localise at a defect class (corner, stop),
does the class predict the representation type, and does adding that
type repair trajectories that were never seen?

## What is already established and not re-run

- B3 calibrated the anisotropic smooth law on the two probes and a corner
  mass `K = sum 2 sin(|Theta|/2)` on one isolated corner; the corner term
  over-predicted the zigzag two to one and total turning beat the law at
  the three tighter thresholds. B4 scored by the local supremum and found
  the reason: the wake consumer reads the path tangent, so on curves the
  vertex count follows total turning with an `eps^-1` law. B4-H1
  ("beat total turning" at the tight thresholds) failed; B4-H2 (both B2
  residuals reduced) passed at 19.35 mm. Those two hypotheses are the
  owner's B3-H1 and B3-H2 and are not re-run.
- Stops are events (B2 Amendment 1): forced vertices at the crossings of
  0.05 m/s and at zero-speed edges. On-path and medial-axis stalks are
  non-Lipschitz points of this consumer (B4 Amendments 2 and 3) and are
  excluded from the score exactly as in B4.

## Declared design pilot (seen trajectories only)

Before freezing, zigzag, stop_start and the B4 corner probe (`corner_L8`)
were run once with four representations to fix definitions. Seen: a
forced apex vertex changes the zigzag's count from 135 to 132 (a no-op);
tightening the tolerance by 0.3 inside corner neighbourhoods changes it
to 114 and the probe's from 31 to 23; under the smooth-only
representation the residual energy lies 97 percent within corner
neighbourhoods on the probe; without stop events stop_start needs 354
vertices at every threshold and its residual is 2.9 times enriched at
stops. The B4 corner probe therefore calibrates the two corner repairs
below, and none of the fresh trajectories was run.

## Definitions (frozen)

Consumer, score, exclusions, tolerance sweep: as B4 (wake + presence
model, local supremum over stalks within 1.5 m of the dense path with
the unambiguous-approach exclusion, thresholds 4.84, 9.68, 19.35, 38.70
mm, primary 9.68 and 19.35 mm, 48 tolerances from 1 m to 0.1 mm). Stalks:
a 0.25 m lattice within 2 m of the dense path (B4's strip grid) for
every trajectory here. `N_eps` is the smallest vertex count in the sweep
whose supremum is at or below `eps`.

Classes, from the trajectory's own kinematics (nothing is fitted):

- corner: maximal interval with `|theta'| > 3 rad/s` (B3's rule), angle
  `Theta_j`, sample count `n_j`;
- stop: interval with speed at or below 0.05 m/s lasting at least 0.2 s
  and not within 0.3 s of the walk's start or end;
- smooth: everything else while moving.

Neighbourhoods on the consumer: a scored stalk belongs to a class if its
foot on the dense path (the sample at its pass time) lies within 0.3 m of
any sample of that class's interval (corner, stop), else to smooth. (A
time window was tried first and missed stops entirely, because the stalk
lattice's half-spacing offset puts the nearest columns 0.28 s outside a
stop's interval; the neighbourhood is spatial for that reason, fixed
before the freeze.) For R3, the tolerance is tightened on path samples
within 0.25 s of a corner interval.

Residual and its localisation, computed on the smooth-only representation
before any repair is fitted (the analogue of W4's `P_t`): for a kept
vertex set, `r_i = sum over frames |G_dense - G_compressed|^2` at scored
stalk `i`; the share of class X is `sum_{i in X} r_i / sum_i r_i`; the
enrichment is that share divided by X's share of scored stalks. For the
negative control, which has no corner by the rule, the reported mask is
the top quartile of `|theta'|` over moving samples (no widening).

Representations (all use the dense 200 Hz samples as candidate vertices):

| name | rule |
|---|---|
| R0 spatial | 2-D Douglas-Peucker on positions, vertex times kept, nothing forced |
| R1 smooth-only | spacetime DP (`weighted_time_dp`), nothing forced |
| R2 + stop events | R1 with the stop event vertices forced |
| R3 + corner class | R2 with the position tolerance multiplied by `f` inside corner neighbourhoods |
| R4 + tangent coordinate | R2 with a second split criterion: a chord is refused if its direction differs from the dense tangent at any interior moving sample by more than `dtheta = c eps / peak`, `peak = 0.4838 m` (B4's reference peak bend), `eps` the threshold being scored |

Calibration, on `corner_L8` only: `f` from {0.5, 0.3, 0.2, 0.1, 0.05} and
`c` from {0.5, 0.71, 1, 1.41, 2} minimise `N_eps(19.35 mm)`; ties go to
the larger `f` and the larger `c`. The same `f` and `c` are used at every
threshold and on every other trajectory.

Fresh trajectories (`reactive.worldlines.fresh_family`, `corner_tau`,
`dwell_probe`; generated after B4, never run before this freeze):

| name | classes by the rule | role |
|---|---|---|
| three_corners | corners 55, 106, 148 degrees (0.2 s), no stop | corner repair, law |
| corner_stop_corner | corners 88, 117 degrees (0.15 s), one 1 s stop | both repairs |
| bend_then_corner | smooth half-period bend then a 97 degree corner | mixed |
| reversal | one 175 degree corner (0.3 s) | corner repair, law |
| tight_slalom | no corner (peak `|theta'|` 2.51 rad/s), turning 12.8 rad | negative control |
| corner_tau, tau in {0.8, 0.4, 0.2, 0.1, 0.05} s | 90 degree corner; the rule calls 0.8 smooth and the rest corners | H4 |
| dwell, D in {0, 0.5, 1, 2} s | straight, one stop of duration D (D = 0 is the momentary stop) | H5 |

`straight_L8` (B4) is the straight twin for the corner probes.

Parameter-free tangent law (from B4, no constant fitted here):
`N_hat(eps) = N_straight(eps) + N_interior_events + sum_j min(Theta_j
peak / (2 eps), n_j) + Theta_smooth peak / (2 eps)`, with `Theta_smooth`
the turning outside corner intervals and `N_straight` the straight
twin's count at `eps`.

## Hypotheses and bars (frozen)

Scored on fresh trajectories only, at both primary thresholds unless
stated. A threshold a trajectory never reaches in the sweep is void for
that trajectory and reported.

- **M1 residual localises at stops.** Under R1, on corner_stop_corner and
  dwell 0.5, 1, 2, stop-neighbourhood enrichment >= 2 (taken at the
  smallest-N row with supremum <= 38.70 mm, or the smallest-supremum row
  if none).
- **M2 residual localises at corners.** Under R2 at `N_eps(19.35)`, the
  corner-neighbourhood share of residual energy >= 0.8 on three_corners,
  reversal and corner_stop_corner. Reported: bend_then_corner's share
  (expected >= 0.5) and tight_slalom's top-quartile enrichment (expected
  <= 2, against >= 3 on every corner path).
- **R-stop the event atom repairs stops.** `N_eps(R2) <= 0.5 N_eps(R1)` at
  19.35 mm on the four stop trajectories (R1 unreachable and R2 reachable
  also counts), and under R2 the stop enrichment falls below 2.
- **R-corner the class atom repairs corners on fresh paths.** `N_eps(R3)
  <= 0.9 N_eps(R2)` on three_corners, corner_stop_corner,
  bend_then_corner and reversal, both primaries.
- **R-tangent the coordinate repair does at least as well, and also
  repairs the control.** `N_eps(R4) <= N_eps(R3)` on the four corner
  paths, both primaries, and `N_eps(R4) <= 0.9 N_eps(R2)` on tight_slalom
  (where R3 = R2 by construction). Stated prediction: passes; then the
  corner class is a special case of the tangent coordinate for this
  consumer, as W4's dispersion was a special case of event time.
- **H4 singular mass is stable as the corner sharpens.** Under R2,
  `N_corner(tau) = N(corner_tau) - N(straight_L8)` at 19.35 mm is
  positive for every tau, and over tau in {0.8, 0.4, 0.2} its max/min
  <= 1.5. The B2 smooth predictor gives a ratio of 2 over that range
  (`C_s ~ sqrt(tau)`); the B3 step predictor jumps from 9 to 23 at the
  class boundary between 0.8 and 0.4 s; the tangent law says flat.
  Reported: tau = 0.1 and 0.05 against the sampling cap `200 tau`.
- **H5 dwell is an event coordinate.** Under R2, `|N_eps(D) - N_eps(0)|
  <= 2` for D in {0.5, 1, 2} at both primaries. Under R0,
  `N_eps(D = 2) >= 2 N_eps(D = 0)` at 19.35 mm, or D = 2 unreachable
  while D = 0 is reached.
- **L tangent law (scored on the two pure-corner paths).** `N / N_hat`
  within [0.67, 1.5] on three_corners and reversal at 19.35 mm. Reported
  with stated expectations: corner_stop_corner and bend_then_corner
  within [0.67, 1.5]; tight_slalom about 1.8 (the old slalom's ratio),
  which the law's `eps^-1` form does not explain.
- **Negative control.** No corner detected on tight_slalom (verified
  before the freeze and re-stated by the run), so R3 = R2 there; its
  residual under R2 is spread (M2's reported enrichment bound).

## Outcome rules (frozen)

- **Procedure transfers:** M1, M2, R-stop, R-corner, H4 and H5 hold. The
  residual named the class before the repair was fitted, the class's
  representation repaired fresh trajectories, the singular mass is
  stable and dwell is a coordinate. R-tangent then decides the type: if
  it also holds, the corner class dissolves into the tangent coordinate
  (coordinate over class); if it fails on the control, the corner class
  stands as its own representation type.
- **Localises but does not repair:** M1 and M2 hold, R-corner fails. The
  class is detectable but the singular allocation is the wrong repair;
  R-tangent's result says whether the tangent criterion is the right one.
- **Does not localise:** M2 fails. Residual-guided expansion does not
  transfer to this consumer and the decision procedure is not built on
  it.
- H4, H5 and L are scored independently and reported whatever the above.

Results go in `poc/results/b5.md`; nothing above is edited after the run.
