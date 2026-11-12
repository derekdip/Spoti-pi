# ED6 results: the knee and the stopping rule hold on three other models

Written 18:22 UTC 2026-11-11 from the frozen scorer's report
(`poc/results/ed6/run/report.md`), which is the record.
Preregistration: `docs/math-track-ed6-prereg.md`, frozen at fc91a9e.
The run started at 15:36 UTC from that commit and finished at 18:21
with no restart (`run.log`, `rows.json`, a checkpoint per condition).

## Outcome, by the frozen rules: A, A, A

| model | E1: c.v. of the knee in each condition (below 0.35) | E2: positive; at least 2/3 of the peak (all 12; 10, 3 per condition) | E3: turned (10) | E4: kept at `g*` against step 60 | letter |
|---|---|---|---|---|---|
| `distilgpt2` | 0.15, 0.11, 0.10 | 12; 12 | 12 | 0.976 against 0.743 | A |
| `openai-gpt` | 0.05, 0.12, 0.12 | 12; 12 | 12 | 0.949 against 0.720 | A |
| `gpt2-medium` | 0.07, 0.20, 0.04 | 12; 11 | 12 | 0.898 against 0.726 | A |

The preregistration's reading: the knee and the rule are not
particular to GPT-2 base, within this lineage.

## What the 36 fits show

- **Every long fit went bad**, on every model: all 36 fell to a
  quarter of their peak test gain within the cap, ten of them already
  below the unadapted model when stopped.
- **The knee is common to the matrices of a sample on every model.**
  Within a condition the four matrices turn at steps that differ up
  to sixfold (60 to 360 on `openai-gpt` on leet) and at training
  gains with
  a c.v. of 0.04 to 0.20.
- **The knee is not one number across models.** Mean training gain
  at the test peak:

  | model | plain, 8 | plain, 32 | leet, 8 |
  |---|---|---|---|
  | `distilgpt2` (82M) | 1.09 | 1.04 | 1.53 |
  | `openai-gpt` (117M) | 1.02 | 0.96 | 2.16 |
  | GPT-2 base (124M; ED4, ED5) | 1.15 | 1.07 | 1.82 |
  | `gpt2-medium` (355M) | 1.51 | 1.37 | 1.80 |

  On every model it is higher on leet than on plain text and hardly
  moves from 8 to 32 contexts. On plain text the largest model's is
  about a third higher than the others'.
- **The rule kept a positive gain in 36 of 36** and at least two
  thirds of the peak in 35. Share of the peak kept, mean and lowest:

  | model | at `g*` | at step 60 | at the validation minimum |
  |---|---|---|---|
  | `distilgpt2` | 0.98, 0.90 | 0.74, 0.19 | 0.98, 0.94 |
  | `openai-gpt` | 0.95, 0.77 | 0.72, -0.59 | 0.98, 0.89 |
  | `gpt2-medium` | 0.90, 0.48 | 0.73, 0.32 | 0.99, 0.97 |

- **A 60-step budget fails differently on each model.** On
  `openai-gpt` an MLP matrix peaks at step 30 and is below the
  unadapted model by step 60; on `gpt2-medium` the attention output
  matrix needs 150 to 230 steps and has a third of its gain at 60.

## Where the rule is weakest

On `gpt2-medium` at 8 contexts the cross-fit overshoots: `g*` is
2.00 against a mean knee of 1.51 on plain text and 2.21 against 1.80
on leet. Half-samples of four contexts turn later, in training gain,
than the full sample of eight does on this model, which they did not
on the smaller ones. The cost is the two lowest fits of the run, 0.71
and 0.48 of their peak; both keep a positive gain, and E2 holds at 11
of 12. At 32 contexts on the same model `g*` equals the mean knee
(1.37) and every fit keeps 0.99 or more. So the rule's error grows
when the halves are very small and the model is large; four contexts
per half is too few to rely on.

The half-fits' knees are also most scattered at 8 contexts (c.v. up
to 0.73 on `openai-gpt` plain text, where `g*` came out 20% low and
one fit kept 0.77).

## Departures and defects

- **Older models of one lineage.** `distilgpt2`, GPT-1 and
  `gpt2-medium` are what could be downloaded. Nothing here says the
  knee exists in a current model, in another family, at another rank
  or learning rate, or with full fine-tuning.
- **PyTorch, not the JAX code of ED4 and ED5.** The port was checked
  against the JAX run on GPT-2 base before the pilot
  (`poc/results/ed6/xcheck_gpt2/`): same contexts by hash, test peaks
  at the same steps, `g*` 1.12 against 1.16.
- **Interim readings were reported before the scorer ran.** Nothing
  frozen was changed (the diff of the tool, the scorer, the config
  and the preregistration against fc91a9e is empty).
- **The run took 2 h 46 min against an estimate of 3 h 30 min to
  4 h.**
- **`openai-gpt`'s tokenizer** fell back to the library's basic
  pre-tokenizer (its usual text-cleaning packages are not installed
  here); the model is scored on its own tokens throughout, so losses
  are not comparable between models, only within one.
- **One corpus, one learning rate, rank 2, four matrices per model,
  8 and 32 contexts.**
