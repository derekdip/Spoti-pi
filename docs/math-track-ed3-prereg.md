# ED3: where to put an adapter. Preregistration (frozen before any scored case is run)

ED2 (`docs/math-track-ed2-results.md`) found that on a real model no
training-residual geometry ranks the module an adapter should go on,
that a first-order held-out gain ranked the planted module third of
twelve on one pilot case, and that on real next-token data at that
scale no module helped at all. The literature pass
(`docs/ed3-literature.md`) fixed the question: the field already has
a single-run validation-gradient selector (surgical fine-tuning's
Auto-RGN) and the cross-validation sweep it loses to, a negative
result on layer selection against combinatorial baselines, and one
finding that placement is not load-bearing at 3B. So ED3 asks, on a
target where an adapter generalises and modules differ: does the
first-order held-out gain select a module at least as well as the
held-out gradient norm and as random placement, and within one
percent of the full sweep, at the sweep's cost divided by four; and
does it find a planted module.

## The model, the data, the state

As ED2: GPT-2 base in JAX (`poc/ecsdec/gpt2.py`), this repository's
documents split by file into training and held-out probes, 96
contexts of 16 tokens each side, every position a target on the base
model's top-256 support with the true token swapped in (393216 state
numbers), float32, adapters as LoRA pairs, Adam fits at a frozen
budget, distortion normalised, the deployment objective on held-out.

The documents are passed through a format transform before
tokenisation: **alternating capitalisation**, every letter's case the
opposite of the previous letter's. It is a rule, not a memory: an
adapter that learns it gains on every held-out context, and GPT-2
without it is at held-out cross-entropy 6.68 (6.04 on the plain
documents, 5.02 upper-cased). The pilot on upper-casing, the first
candidate shift, found gains under one percent with the MLP modules
overfitting (`poc/results/ed3/pilot0_format.log`), too weak a
regime to separate selectors.

## The rule and the selectors

`poc/ecsdec/sketch.py`, as ED2 froze it (stationarity by products,
Lanczos curvature, the bounded budget, the tangent sketch, candidate
sketches, the linearised held-out gain, the base model as the
fallback, the deployment objective), with two additions, both
reported from the same run:

- **Auto-RGN per module** (Lee et al. 2023): the norm of the held-out
  loss's gradient with respect to the module's weights, one VJP of
  the held-out state against the held-out residual, over the
  weights' norm.
- **Every selector read off the sweep.** With the sweep run in full
  (every library module fitted jointly with the current adapter),
  each selector's outcome is the best deployment objective among the
  modules it would have fitted: the held-out gain's beam of 3, the
  matched-`p` score's beam, Auto-RGN's beam, a random beam of 3 (one
  seeded draw, and the expectation over 2000 draws), and the sweep
  itself as the ceiling. No selector costs an extra fit.
- **The predictor's accuracy.** For every module, the first-order
  held-out gain against the fitted held-out gain
  (`1 - D_held(joint) / D_held(current)`), with Pearson and Spearman
  correlations.

Students are the best of 3 fits, and the number of restarts that beat
the first fit by the budget's 10 percent is recorded (ED2's extend
case was lost to this).

## The cases

| case | target | student | truth |
|---|---|---|---|
| extend | a rank-2 teacher adapter on `fc@7` fitted on the format targets, doubled | rank 2 on `v@7`, best of 3 | EXPAND on `fc@7` |
| real | the format targets | rank 2 on `v@7`, best of 3 | none |

Both run the sweep. The teacher is fitted on the format targets (not
on the next tokens of the plain documents as in ED2), so its delta
is a generalising one and its held-out effect is large.

## The frozen values

`poc/results/ed3/config.json`, committed with this document.

VALUES_TABLE

## The declared pilot

PILOT_NUMBERS

## Bars (frozen)

`poc/ecsdec/score3.py`, committed with this document.

- **G1, the planted module.** The rule returns EXPAND on `fc@7`.
- **G2, the selectors on the format shift.** The held-out gain's
  beam reaches a best deployment objective at least as good as
  Auto-RGN's beam and as the random beam's expectation, and within 1
  percent of the sweep's best.
- **G3, reported.** The predictor's per-module accuracy and
  correlations on both cases; the first stage, budget and restart
  counts; held-out cross-entropy of the base and the current; the
  sweep's held-out distortions; time per stage.

## Predictions

PREDICTIONS

## Outcome (frozen, exclusive)

- **A**: G1 and G2 hold.
- **B**: G1 holds, G2 fails.
- **C**: G2 holds, G1 fails.
- **D**: neither.

G3 is reported under every letter. No rescue, no second run on the
scored world, no change to the model, the data, the transform, the
state, the cases, the rule, the thresholds or the budgets after this
commit. Results go in `docs/math-track-ed3-results.md`; nothing above
is edited after the run.
