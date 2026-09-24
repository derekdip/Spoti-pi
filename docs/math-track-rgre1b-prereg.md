# RGRE-1b: replication of the simplified selector. Preregistration (frozen before the benchmark seed is run)

RGRE-1 supported the core procedure and falsified one addition to it.
The coherence-weighted score `S_j = q_j (1 - mu_j)` and the abstention
on known cases cost value against a class-free per-direction projection
of the residual, which never lost on any of the 72 known cases. That
observation is post hoc on those cases. RGRE-1b asks one question only:
does it replicate on fresh ones?

This is a replication, not a research track. Four bars, thirty cases,
nothing tuned.

## Frozen algorithm

Diagnosis is unchanged from RGRE-1 (`docs/math-track-rgre1-prereg.md`,
`poc/rgre/core.py::diagnose`): signed tangent subspaces, support-type
templates gated by energy density inside against outside, shape-type
templates by nonnegative least squares, and the same `q_perp`
bookkeeping. Nothing in that function changes, so the threshold below
means the same thing it meant in RGRE-1.

Selection is replaced by the rule RGRE-1 identified
(`poc/rgre/core.py::select_projection`):

- if `q_perp > tau` abstain;
- otherwise rank the individual diagnostics by their own residual
  fraction. For a tangent direction that is `<r, d_j>^2 / (||d_j||^2
  ||r||^2)`, one number per direction, not per class. For a template
  class it is the share of the remaining per-point energy on its
  support. These are the same `items` the winning RGRE-1 baseline
  ranked, on the same mixed scales, deliberately unaltered;
- take the class of the top-ranked item. If it is unrepairable (water's
  floor) abstain as "wrong atom". Otherwise evaluate that class's repair
  set and keep the best error reduction per unit cost.

No coherence multiplier, no class-level aggregation, no learned weights.

`tau = 0.5834212065969504`, RGRE-1's calibrated value, carried over
verbatim. It is not recalibrated, and no calibration stage runs.

## Mixtures and the spent-repair rule

Two steps: diagnose, repair, recompute the residual, diagnose again,
repair. One rule is added, from RGRE-1's finding that re-diagnosis
re-commits to a class after a worthless repair: a repair that reduced
the error by less than one percent of its starting value is spent and
cannot be chosen again. Only the tested repair is blacklisted, not its
class; a class is skipped at step two only when every repair it owns is
spent. The one percent constant is declared here and is not tuned.

## Fresh benchmark (seed 20260916, `poc/rgre/bench_b.py`)

Thirty cases: 24 known, 5 out of vocabulary, 1 reported and unscored.

| group | cases |
|---|---|
| isolated tangent (10) | corn tail x3 (two with persistence cut to 0.3 to 0.6, RGRE-1's flipped regime, one raised), corn coordinate x2, corn unary x1, water coordinate x2, water unary x1, water tail x1 |
| isolated support (6) | corn stop x2 (no event vertices at all), corn corner x2, water interaction x2 (fresh amplitudes 5.5 and 7.0, separations 0.234 and 0.328 m, singles fitted with gain and shift so only the cross-term is missing) |
| mixtures (8) | water interaction+coordinate x2 and corn unary+stop x2, the two regimes where RGRE-1's coherence penalty flipped a correct raw diagnosis; corn coordinate+corner, corn tail+smooth, corn corner+stop, water coordinate+unary |
| out of vocabulary (5) | corn travelling gust field x2, corn hidden second walker, water hidden second splash x2 |
| reported, unscored (1) | water splash displaced 0.72 m from where the token sits |

Every corn trajectory comes from the fresh seed. Water teachers use
fresh parameters with two declared exceptions: the water coordinate case
at a five-frame delay is an exact repeat of RGRE-1's `coordinate_2` and
serves as a replication anchor, and the remaining water parameters are
new values on the same small discrete grids.

**Construct validity of the unknowns, checked before the freeze.** A
case counts as out of vocabulary only if no single repair removes more
than 10 percent of its error. The check reads the repair oracle alone
and never the threshold or the selector, so it cannot tune the
procedure. Two consequences, both declared here:

- The dragged pressure source is dropped. RGRE-1 established that a gain
  repair removes 55 percent of its error and the oracle agrees. It was
  mislabelled.
- A splash displaced from the token's centre was written as its
  replacement and fails the same check: a gain repair removes 22 to 26
  percent at every offset tried, by turning a wrongly placed token down.
  It is kept as one reported case outside every bar, because the gap it
  exposes is real and is the kind fire is expected to surface. The
  vocabulary has a time coordinate and no space coordinate, so a
  mislocated cause has no repair that addresses it.

The five retained unknowns pass the check: the two water hidden splashes
at 0.5 percent, and the corn gust and hidden-walker generators at 0.3 to
0.6 percent in RGRE-1, which this benchmark reuses unchanged.

## Bars (frozen, scored on the 24 known cases unless stated)

- **B1** median oracle value captured `>= 0.90`.
- **B2** median repairs evaluated `<= 1/3` of the repair set.
- **B3** at least 80 percent of the 5 unknown cases abstain, and at most
  10 percent of the known cases falsely abstain.
- **B4** median two-step recovery over the 8 mixtures `>= 0.75`.

Reported without bars: what RGRE-1's coherence-weighted rule would have
chosen on the same cases and the value it would have captured, identity
against the injected class and against the oracle's class, value by
class, and the vocabulary-gap case.

## Outcome (frozen)

All four bars hold: the simplified selector is confirmed on fresh cases
and is the version that goes to fire. Any bar fails: it is named, and
the failure decides whether fire waits.

No further hypotheses, no rescue, no third round on this benchmark.
Results go in `poc/results/rgre1b.md`; nothing above is edited after the
run.
