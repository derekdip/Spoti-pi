# RGRE-ML-3: a stopping rule with no constant, calibrated on the procedure's own null. Preregistration (frozen before the scored splits run)

Four borrowed constants have failed in transfer across this arc: two
stopping rules in fire, the abstention threshold in RGRE-ML-1, and the
one percent dead rule in RGRE-ML-2, which stopped growth at step zero
on the two datasets where eight steps still gained held-out error and
at step one on two where the best step was two or three. Every one of
them sits on an energy fraction, and every time the quantity under the
constant held while the constant did not. This experiment replaces the
constant with a test the procedure runs on itself.

## The rule

At each growth step the statistic is `q_top`, the largest share of the
training residual's energy that any one candidate class's tangent
subspace explains; the abstention quantity `q_perp` is one minus it.
The null is the same statistic on the same residual shuffled across
samples: the residual keeps its values and loses its relation to the
inputs, which is the hypothesis "nothing here is structure a candidate
can find". The rule declines the step, and growth stops, when any of
the first M shuffles reaches the observed value. That is a permutation
test at level 1/(M+1), with M a computational budget rather than a
tuned number. M = 19 is the rule scored (the classic one in twenty);
M = 9 and M = 49 are recorded from the same shuffles and reported, so
that the reader can see how much the choice of budget matters. No fit
is needed to apply the rule: the tangents are computed before any
repair, as they were in every domain.

The growth path is RGRE-ML-2's (`poc/rgre_ml/ml3_run.py` re-grows it
deterministically; the scorer checks the modules added against the
frozen ML-2 run and reports any difference). Nothing about the
dictionary, the picks, the data or the splits changes. Only the stop
is new, and it is evaluated by the held-out error of the model at the
step it chose, against the same curve the other rules read.

## Comparators, on the same 30 cases

- the one percent rule (decline when the fitted pick's in-sample drop
  is under one percent), the constant RGRE-ML-2 used;
- never stopping (the eight-step model);
- not growing (the linear model);
- hindsight (the step with the lowest held-out error, a bound).

Regret is held-out error at the chosen stop minus held-out error at
the hindsight best, in units of the target's standard deviation.

## The declared pilot

Split seed 0 on auto mpg, excluded from every bar
(`poc/results/rgre_ml3_pilot.*`): the path reproduced RGRE-ML-2's
exactly; the rule stopped at step 7, 5 and 3 for M = 9, 19 and 49,
where the held-out best was step 8 and the one percent rule ran to 8.
So on that case the null rule was the more conservative of the two,
which is not what the RGRE-ML-2 result suggested for datasets with
structure, and the prediction below is adjusted to say so. On permuted
targets the rule declined at step zero.

## Bars (frozen)

Six datasets, split seeds 1 to 5, 30 cases. Scorer
`poc/rgre_ml/ml3_score.py`, committed with this document.

- **C1, against the constant.** The null rule at M = 19 has lower
  held-out error at its stop than the one percent rule on more cases
  than it has higher, and lower mean regret.
- **C2, a stopping rule and not a rename.** Its mean regret is below
  never stopping's and below not growing's.

Reported: the same for M = 9 and M = 49; stop steps by dataset; the
share of cases each rule stops at the hindsight best; the rule's
decline rate on permuted targets at step zero (about M/(M+1) by
construction, reported as a check); and the linearisation gap below.

## Outcome (frozen)

- **Holds** if C1 and C2 both hold: the constant is replaced by the
  self-calibrated test, and the write-up's open item on thresholds is
  closed with it.
- **Half** if exactly one holds, named.
- **Fails** if neither.

Prediction: C2 holds. C1 is open: the null rule will grow where the one
percent rule did not (abalone, California, where `q_top` at step zero
sits far above its null) and may stop earlier where the one percent
rule ran on (auto mpg on the pilot); which of those two effects wins on
held-out error is what the run decides.

## The linearisation gap, recorded in the same run (post-hoc, no bar)

For every candidate the oracle fits at every step, the fraction of its
fitted contribution outside the tangent span the ranking used,
`1 - cos^2(f*, span T_c)`. Zero by construction for a one-parameter
linear module; for a free-shape module it is how far the fit ended from
where the tangent pointed. Reported: the gap by module kind; the
Spearman correlation between the oracle's module's gap and the value
the projection captured, over 240 steps; the gap against the anchored
span of the declared variant; and the same quantity on the nine fire
scenes at step zero (`poc/fire_lin_gap.py`), where projection selected
well, as the contrast. On the pilot the oracle's gap was 0.06 on the one
step where the projection captured full value and 0.37 to 0.77 on the
others. This is a diagnostic being characterised, not a claim being
tested, and the results say what it looks like.

No rescue, no second run on the scored splits, no change to M or to
the rule after this commit. Results go in
`docs/math-track-rgre-ml3-results.md`; nothing above is edited after
the run.
