# RGRE-ML-2: the procedure on real data. Preregistration (frozen before any scored split is run)

RGRE-ML-1 and 1b characterised the procedure on synthetic teachers: its
selection is matching pursuit, its abstention quantity separates
out-of-vocabulary residual from known residual, its sequencing protocol
recovers two missing modules, and deferring the regions the tangent
span cannot explain beats deferring the largest regions by a small
margin. All of that was with an exact teacher and two percent noise.
This is the first test on real data, where there is no teacher, the
noise is whatever the data has, and the only arbiter is held-out error.

## Setting

Six tabular regression datasets, processed once by
`poc/rgre_ml/prep_data.py` and committed under `poc/rgre_ml/data/`
(sources in its README): diabetes (442 rows, 10 features), auto mpg
(392, 6), concrete (1030, 8), red wine quality (1599, 11), abalone
(4177, 7), California housing (3000 rows drawn with a fixed seed, 8).
Each case is one dataset and one seeded 70/30 split; features are
z-scored on the training part and divided by three, the target is
z-scored on the training part, so every error below is in units of the
target's standard deviation.

The student (`poc/rgre_ml/real.py`) is an intercept, a linear term, and
modules grown from a dictionary defined per feature and per pair: a
square, a cube, a sinusoid, a sigmoid step, an absolute value and an
exponential of each feature; a product and a two-dimensional Gaussian
bump of each pair. 66 to 176 candidates per dataset. Each gated module
has one canonical on-state, bounds and a cost equal to its parameter
count, as the synthetic dictionary did. One consumer, the prediction:
RGRE-ML-1 and the fire cross-check settled where to diagnose.

Per case (`poc/rgre_ml/run_real.py`): the linear student, then eight
growth steps. Before each step the training residual is diagnosed with
`poc/rgre/core.py` unchanged and the pick is the class of the single
tangent direction with the largest squared cosine to the residual,
abstention off, so that every step is taken and the abstention
quantity is scored by what it predicted rather than by a threshold.
The exhaustive oracle fits every candidate at every step. The fitted
pick is added whether or not the in-sample dead rule (one percent)
would have declined it; the first declined step defines the "dead
stop" student. Deferral is ranked at step zero over twelve k-means
regions of the training inputs and scored on held-out points outside
the three deferred regions. A permuted-target control repeats the
step-zero diagnosis on the same split with the targets shuffled.

**The abstention quantity is redefined, and the reason is stated.**
RGRE-ML-1 scored `q_perp` as the residual energy left after projecting
on every candidate direction jointly. On a per-feature dictionary that
joint span has more directions than a small dataset has training rows
(186 directions on 274 rows for auto mpg, about 500 on 309 for
diabetes), so the joint projection explains most of a pure-noise
residual and the quantity is degenerate: 0.22 on auto mpg, 0.03 on
diabetes, against 0.45 and 0.02 on their permuted targets. The quantity
scored here is the single-class version, one minus the largest share
of residual energy any one class's subspace explains, which is what
the selection rule itself reads. The joint version is reported beside
it.

## The declared pilot, and what it changed

Split seed 0 on the two smallest datasets, diabetes and auto mpg, was
run before this document was written (`poc/results/rgre_ml2_pilot.*`)
and is excluded from every bar. It found two testbed defects and one
thing that is not a defect:

1. The deferral criterion RGRE-ML-1b validated, energy left after the
   best single class's global projection, reproduces the magnitude
   ranking exactly on both pilot cases, because no single class
   explains more than a few percent of a real residual. **A top-S
   version was added**: energy left after the joint projection onto
   the eight top-ranked classes, the span the growth budget can reach.
   B3 is on the top-S version; the single-class version is reported.
2. The pooled AUC of `q_perp` between permuted and real targets mixes
   datasets whose noise levels differ, which is not the claim. **B4 is
   paired within each split.**
3. Selection value on the pilot was 0.46 in median, far below the
   synthetic 1.00. The oracle's pick is usually a bump or a sinusoid
   whose fitted shape ends far from its canonical on-state, so the
   on-state tangent does not predict what the fit will do. This is the
   limitation RGRE-ML-1's preregistration stated ("a candidate must
   have a direction before it is fitted"), met on real data. It is not
   a defect and the bar is not moved. **A variant with several fixed
   on-states per gated module is declared and reported, not barred**;
   on the pilot it was worse (0.18), because more directions give
   noise more chances to correlate with one of them.

Pilot values, for the record: B1 0.46 (bar 0.90), B2 AUC 0.88 against
step index 0.77, B3 top-S wins one of two with one tie, B4 paired 2 of
2. The pilot also showed the dead rule stopping diabetes at step zero
while its held-out error kept falling to step five, and never stopping
auto mpg, whose held-out error fell at every step and beat ten-nearest-
neighbours; both are reported, neither is a bar.

## Bars (frozen)

Six datasets, split seeds 1 to 5: 30 cases, 240 growth steps. Scorer
`poc/rgre_ml/score_real.py`, committed with this document.

- **B1, selection value.** Median over all 240 steps of the pick's
  in-sample error drop over the best single candidate's, `>= 0.90`,
  and above random and gradient-norm selection on median and mean.
  This is matching pursuit's value by the identity RGRE-ML-1 stated.
- **B2, the abstention quantity as a stopping signal.** A step is
  wasted if the pick's held-out error drop is under one percent. AUC of
  the single-class `q_perp`, read before the step and without any fit,
  for predicting a wasted step, `>= 0.75`, and above the AUC of the
  step index, the trivial baseline that says later steps are wasted.
  The in-sample drop of the fitted pick, which costs a fit, is reported
  beside it.
- **B3, deferral.** On the dead-stop student, deferring the three
  regions with the most top-S unexplained energy leaves less held-out
  error outside the deferred regions than deferring the three with the
  most residual energy on `>= 60%` of the 30 cases, ties against, and
  its median is below magnitude's and random's. The same on the
  eight-step student is reported.
- **B4, noise detection.** On `>= 90%` of the 30 splits the step-zero
  single-class `q_perp` on permuted targets is above the value on the
  real targets.

Reported, not barred: the anchored-tangent variant's value; the joint
`q_perp`; the dead rule's behaviour on permuted targets (the spurious
best drop among 66 to 176 candidates was 0.7 and 1.1 percent on the
pilot, on either side of the one percent constant, so the rule is
predicted to be at the noise floor on the small datasets); held-out
error of the linear model, the dead-stop model, the eight-step model,
the best step in hindsight and ten-nearest-neighbours; the kinds of
module grown and the kinds the oracle would have grown.

## Predictions

B1 is predicted to fail, on the pilot's evidence and for the reason
above. B2 is the open question: on the pilot the quantity beat the
step index, and the step index is strong. B3 is predicted to fail:
the training residual's magnitude is the direct predictor of held-out
residual, and growth removes little of it on real data, so there is
little for orthogonality to anticipate. B4 is predicted to hold.

## Outcome (frozen, exclusive)

- **A**: B1, B2 and B3 hold. Everything measured on synthetic data
  transfers to real data.
- **B**: B1 and B2 hold, B3 fails. Growing and stopping transfer;
  deferral by orthogonality is dropped for real data.
- **C**: B1 holds, B2 fails. Selection transfers and is matching
  pursuit; the abstention quantity is not a stopping signal on real
  data.
- **D**: B1 fails. The projection does not select well on real data
  with free-shape modules. B2, B3 and B4 are still scored and reported,
  and if B2 holds the write-up says so: the quantity can be a stopping
  signal for a growth procedure whose selection is done some other way.

B4 failing under any letter is reported as the abstention quantity
being unable to tell structure from noise on real data.

No rescue, no second run on the scored splits, no change to the
dictionary, the anchors, the region count or any constant after this
commit. Results go in `docs/math-track-rgre-ml2-results.md`; nothing
above is edited after the run.
