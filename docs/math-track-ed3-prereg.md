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

| quantity | value | source |
|---|---|---|
| transform | alternating capitalisation | pilot: base held-out cross-entropy 6.68; single rank-2 modules gain 0.3 to 0.4 nats on held-out |
| deployment objective | held-out cross-entropy (full vocabulary) plus `1e-7` per parameter for the format case; held-out distortion plus the same for the planted case | the distortion on the support is blind under this shift (1.004 to 1.000) while cross-entropy moves by a third of a nat; the planted case's teacher target is a distribution, where ED2 showed distortion separates modules |
| fit | 60 Adam steps at 1e-3 | pilot on upper-casing: 1e-3 generalised where 3e-3 overfitted on two of three modules; the alternating-caps pilot runs at it |
| students | best of 3 fits; restarts beating the first by 10 percent counted | ED2's extend case |
| teacher | rank 2 on `fc@7`, 60 steps at 1e-3 on the format targets, delta doubled | a generalising teacher: fitted on the rule, not on memorised tokens |
| library | `v, o, fc, proj` at layers 3, 7, 11 | as ED2; attention and MLP modules both present, where the literature expects a difference |
| `eps_g`, `D_max`, `eps_H`, budget, sketches, linearised fit, beam, equivalence, spent | as ED2's config | unchanged; `D_max` is moot on the format case (`D` near 1) and kept for the planted one |
| probes | 96 contexts of 16 tokens each side, every position, support 256 | as ED2's real case |
| selectors | held-out gain (the rule's), matched-`p`, Auto-RGN, random (one draw and the expectation over 2000), the sweep | read off the one sweep |
| world | seed 1 | the pilot is seed 0 |

## The declared pilot

World seed 0 (the scored run uses seed 1). Logs:
`poc/results/ed3/pilot0_format.log` (upper-casing) and
`pilot1_altcaps.log` (alternating capitalisation). Excluded from
every bar; nothing is changed after it.

- **Upper-casing, the first candidate shift.** Base held-out
  cross-entropy 5.02. Single rank-2 modules after 60 steps at 3e-3
  or 120 at 1e-3: `v@7` 5.09 and 5.01, `fc@7` 5.31 and 5.28, `fc@11`
  5.30 and 5.23, `v@3` 4.85 and 4.84. Held-out distortion 0.952 to
  0.974 against the base's 0.965. Too weak and too mixed a regime:
  one module gains 0.17 nats, the MLP modules lose, and the learning
  rate decides as much as the module.
- **Alternating capitalisation.** Base held-out cross-entropy 6.68,
  distortion 1.004. Every single rank-2 module after 60 steps at
  1e-3 gains: `proj@3` 6.19, `fc@3` 6.22, `o@3` 6.29, `proj@7` 6.31,
  `fc@11` 6.32, `v@3` 6.36, `fc@7` 6.45, `o@11` 6.50, `o@7` 6.51,
  `v@11` 6.60, `proj@11` 6.60, `v@7` 6.62. A spread of 0.43 nats
  across modules, the early and middle MLP modules ahead, the
  student's own module (`v@7`) last. Held-out distortion stays
  between 0.996 and 1.001 for all twelve: blind, hence the
  cross-entropy objective.
- **The planted case.** The teacher (rank 2 on `fc@7`, 60 steps at
  1e-3 on the format targets, doubled) moves the state by 0.72 on
  the training probes and 0.71 on the held-out probes: a
  generalising delta, where ED2's memorising teachers had a held-out
  effect a fifth of the training one. The best-of-3 student on
  `v@7` reaches `D` 0.58 (held-out 0.58), `s` 0.32; no restart beat
  the first fit. Joint fits, held-out distortion: `fc@7` 0.283,
  `proj@7` 0.350, `o@7` 0.377, `v@11` 0.4297; the planted module wins
  by 19 percent over the next.
- **Costs.** A 60-step fit 70 to 130 s at 96 contexts on every
  position; the extend block 10 minutes; the twelve-module scan 30.

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

- **G1 holds.** The student is inadequate (`D` 0.58 against 0.015),
  stationary (`s` 0.32 against 0.5), the budget of 2 finds nothing
  (no restart beat the first fit in the pilot), the held-out gain
  puts `fc@7` in the beam (the teacher's effect is large and
  generalising, so the linearised rank-2 fit on the planted module
  transfers to held-out where the others' do not), and the joint fit
  on `fc@7` wins by about 20 percent: EXPAND on `fc@7`. The named
  risk is the beam: if two other modules' first-order held-out gains
  exceed the planted one's, the case is lost on the beam as the
  matched-`p` score would have lost it in ED2.
- **G2 holds.** The sweep's best addition to the `v@7` student is an
  early or middle MLP module (`proj@3`, `fc@3` or `proj@7`) at about
  6.2 nats against the current's about 6.6; the held-out gain's beam
  contains at least one of them and lands within 1 percent of the
  sweep's best; random placement's expectation over draws of three
  sits near 6.33, which the beam beats; Auto-RGN's beam, a
  sensitivity ranking, is predicted to favour the MLP modules too and
  to tie or lose by under 0.1 nats. The rule returns EXPAND on the
  beam's best; the base (6.68) and the current (about 6.6) lose to
  it.
- **G3.** The first-order held-out gain correlates with the fitted
  cross-entropy gain at Spearman 0.5 or better on the format case;
  the matched-`p` beam contains none of the top three modules; the
  equivalence stage collapses nothing; the restarts beat the first
  fit in no case.
- Letter **A**, the beam on the planted case the way it becomes C.

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
