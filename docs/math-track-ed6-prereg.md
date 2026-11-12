# ED6 preregistration: do the knee and the stopping rule hold on other models?

Written 15:35 UTC 2026-11-11, after a cross-check of the PyTorch port
and a declared pilot, and before any scored run. Frozen by the commit
that adds this file, `poc/results/ed6/run/config.json` and
`poc/ecsdec/score6.py`; the run is
`poc/tools/lora_knee.py run poc/results/ed6/run/config.json poc/results/ed6/run`.
After that commit neither the code, the config nor this text changes;
a defect found later is named in the results, not repaired.

## 1. The question

On GPT-2 base a LoRA fit's gain on fresh text turns at a training
gain common to the matrices of a sample, and stopping at a
cross-fitted estimate of it kept a positive gain in 36 of 36 long
fits (ED4's checks and ED5, `docs/prescreen-theory.md`, sections 12
and 13). One model. ED6 asks whether that is a fact about GPT-2 base
or holds on three other models that can be reached from here:

| model | what differs from GPT-2 base |
|---|---|
| `distilgpt2` | half the layers (6), distilled from GPT-2 |
| `openai-gpt` (GPT-1) | another design (layer norm after each block), other training text (books), another tokenizer (lower-cased, 40k pieces) |
| `gpt2-medium` | twice the layers (24), wider (1024), 355M parameters |

All three are older models of one lineage. Nothing newer or of
another family could be downloaded.

## 2. The port and the pilot

The experiment runs in PyTorch (`poc/tools/lora_knee.py`) since the
JAX model is GPT-2 base only. **Cross-check**
(`poc/results/ed6/xcheck_gpt2/`): GPT-2 base from the Hugging Face
weights on ED5's plain-text condition at 32 contexts. The contexts
hash to the JAX run's; the test peaks fall at the same steps (70, 80,
120, 160); the training gain at the peak is 1.12, 1.18, 0.87, 1.20
against 1.07, 1.16, 0.87, 1.20; `g*` is 1.12 against 1.16.

**Pilot** (seed 0, plain text, 8 contexts, two matrices per model,
`poc/results/ed6/pilot/`):

| model | matrix | base test loss | peak test gain (step) | training gain at the peak | kept at `g*` | at step 60 |
|---|---|---|---|---|---|---|
| `distilgpt2` | MLP output, layer 4 | 6.288 | +0.387 (50) | 1.08 | 0.94 | 0.95 |
| `distilgpt2` | attention value, layer 1 | 6.288 | +0.304 (70) | 0.76 | 1.00 | 0.94 |
| `openai-gpt` | MLP output, layer 8 | 6.340 | +0.205 (30) | 1.08 | 0.97 | -0.72 |
| `openai-gpt` | attention value, layer 2 | 6.340 | +0.127 (80) | 0.88 | 0.90 | 0.90 |
| `gpt2-medium` | MLP output, layer 16 | 6.182 | +0.682 (80) | 1.86 | 1.00 | 0.92 |
| `gpt2-medium` | attention value, layer 4 | 6.182 | +0.435 (130) | 1.55 | 0.96 | 0.30 |

All six fits and all twelve half-fits turned, well inside the caps.
What the pilot set: that the three models load and train, the caps
(800 and 500 steps, as in ED5), and the cost (a matrix at 8 contexts
takes about 45 s on the two small models and 5 minutes on
`gpt2-medium`). It also shows the knee is not one number across
models: about 1 nat on the two small models and 1.7 on the larger.
The bars below do not ask for that.

## 3. The scored run

- **Per model, three conditions**: plain text at 8 training
  contexts, leet at 8, plain text at 32; 32 validation and 96 test
  contexts each; seeds 31 to 39, none used before. Text, windows and
  the three disjoint sets of files as in ED4 and ED5, each model with
  its own tokenizer.
- **Matrices** (four per model, the counterparts of ED5's): the MLP
  output matrix of an early layer and of a layer two thirds of the
  way up, the value block of the early layer's attention, and the
  attention output matrix of the upper layer. Early and upper are
  layers 1 and 4 of `distilgpt2`, 2 and 8 of `openai-gpt`, 4 and 16
  of `gpt2-medium`.
- **Fits, knees and the rule** exactly as in ED5 (section 3 of
  `docs/math-track-ed5-prereg.md`): rank 2, Adam at 1e-3; a full fit
  per matrix until its test gain has fallen to a quarter of its peak
  or 800 steps; two half-fits per matrix until the other half's gain
  has fallen to half its peak or 500 steps; `g*` the median of the
  condition's eight half-fit knees.

## 4. The bars, per model

ED5's four, over the model's 12 full fits:

- **E1.** In every condition the training gain at the test peak has
  a coefficient of variation below 0.35 across the four matrices.
- **E2.** Stopped at `g*`, the test gain is positive in all 12 and
  at least two thirds of the peak in at least 10, with at least 3 of
  4 in every condition.
- **E3.** At least 10 of the 12 full fits turn within the cap.
- **E4.** The share of the peak kept, averaged over the 12, is not
  lower at `g*` than at step 60.

Reported, with no bar: the knee's training gain by model, text and
size beside GPT-2 base's; the share kept at the validation minimum
and at the last step; the spread of the half-fit knees.

## 5. Outcomes

Per model, as in ED5: **A** if E1 to E4 hold, **B** if E2 holds and
another bar fails, **C** if E2 fails. Overall the result is stated as
the three letters.

What they would mean. A on all three: the knee and the rule are not
particular to GPT-2 base, within this lineage. A or B on all three
with some B: the rule is safe on these models and the failed bars
say what differs. Any C: the rule fails on that model, and the
results say whether it stopped too early or too late and on which
matrices; a rule that fails on one of three older models of the same
lineage is not one to recommend.

## 6. Run

About 3 h 30 min to 4 h from the pilot's timed units, most of it
`gpt2-medium` at 32 contexts, which runs last. Every fit is
checkpointed with a hash of its contexts; a process lost to a
machine restart is relaunched with the same command and continues.
No other job runs on the machine during the run.
