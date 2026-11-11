# ED5 results: the knee and the stopping rule hold at 32 and 64 contexts

Written 11:06 UTC 2026-11-11 from the frozen scorer's report
(`poc/results/ed5/report.md`), which is the record. Preregistration:
`docs/math-track-ed5-prereg.md`, frozen at 81f4474. The run started
at 07:08 UTC from that commit and finished at 11:05 with no restart
(`run.log`, `ed5.json`, a checkpoint per condition).

## Outcome, by the frozen rules: A

| bar | result | verdict |
|---|---|---|
| E1: the training gain at the test peak has a c.v. below 0.35 across the four matrices, in every condition | 0.12, 0.10, 0.10 | holds |
| E2: stopped at `g*`, every fit keeps a positive test gain and at least 10 of 12 keep two thirds of the peak, 3 of 4 in every condition | 12 of 12 positive; 12 of 12 above two thirds; lowest 0.86 | holds |
| E3: at least 10 of 12 full fits turn within the cap | 12 of 12 | holds |
| E4: the rule keeps on average at least what a 60-step budget keeps | 0.972 against 0.681 | holds |

The preregistration's reading of A: the knee and the rule carry to
these sizes as they stood at 8 contexts.

## The fits

Share of each fit's peak test gain kept by each way of stopping:

| condition | matrix | peak test gain (step) | training gain at the peak | at `g*` | at step 60 | at the validation minimum |
|---|---|---|---|---|---|---|
| plain, 32 | `proj@2` | +0.710 (70) | 1.07 | 1.00 | 0.98 | 1.00 |
| plain, 32 | `proj@8` | +0.718 (80) | 1.16 | 1.00 | 0.94 | 0.99 |
| plain, 32 | `v@2` | +0.601 (120) | 0.87 | 0.86 | 0.46 | 1.00 |
| plain, 32 | `o@8` | +0.736 (160) | 1.20 | 1.00 | 0.45 | 1.00 |
| leet, 32 | `proj@2` | +1.316 (110) | 1.69 | 1.00 | 0.72 | 0.99 |
| leet, 32 | `proj@8` | +1.410 (140) | 1.81 | 0.98 | 0.77 | 1.00 |
| leet, 32 | `v@2` | +1.043 (190) | 1.39 | 0.99 | 0.49 | 0.99 |
| leet, 32 | `o@8` | +1.399 (200) | 1.77 | 0.98 | 0.38 | 1.00 |
| plain, 64 | `proj@2` | +0.576 (80) | 0.98 | 0.98 | 0.95 | 0.98 |
| plain, 64 | `proj@8` | +0.678 (120) | 1.15 | 1.00 | 0.88 | 1.00 |
| plain, 64 | `v@2` | +0.517 (180) | 0.88 | 0.89 | 0.70 | 1.00 |
| plain, 64 | `o@8` | +0.685 (200) | 1.11 | 1.00 | 0.46 | 0.99 |

| condition | training gain at the test peak, mean | the eight half-fit knees, c.v. | `g*` |
|---|---|---|---|
| plain, 32 | 1.07 | 0.10 | 1.16 |
| leet, 32 | 1.67 | 0.19 | 1.64 |
| plain, 64 | 1.03 | 0.14 | 1.13 |

- **Long fits go bad at these sizes too.** All twelve fell to a
  quarter of their peak test gain within 160 to 750 steps. They were
  stopped there by design, so that none ends below the unadapted
  model says nothing about where they would have ended.
- **The knee is common to the matrices and hardly moves with the
  sample.** The test peak comes at step 70 to 200 depending on the
  matrix and at nearly one training gain within a condition. Across
  sizes, on plain text: 1.15 and 1.29 at 8 contexts (ED4 and its
  pilot), 1.07 at 32, 1.03 at 64. On leet: 1.82 at 8, 1.67 at 32. It
  differs between the two kinds of text by half as much again and
  between sample sizes by a tenth to a fifth.
- **The cross-fit finds it.** `g*` is within 11% of the mean knee in
  all three conditions, all 24 half-fits turned, and their spread is
  smaller than at 8 contexts (c.v. 0.10 to 0.19 against 0.18 to
  0.37). The two fits below 0.9 are both `v@2`, whose own knee is the
  lowest of its condition, so the common `g*` stops it a little late.
- **A budget in steps does not transfer.** Sixty steps keeps 88 to
  98% of the peak for the MLP matrices on plain text and 38 to 77%
  everywhere else, because the attention matrices and the format
  shift need two to three times as many steps to reach the same
  training gain. Sixty was ED4's budget and was not tuned for these
  sizes; E4 was written knowing the pilot had it close to the peak.
- **Validation stopping remains the best**, 0.98 to 1.00 with 32
  validation contexts. The rule gets within 2% of it on average
  using none.

Reported: the test gain over the training gain in the first 30
steps is 0.63 to 0.88 on plain text at 32, 0.92 to 1.01 on leet at
32 and 0.72 to 0.84 on plain text at 64, against 0.25 to 0.61 at 8
contexts: with more contexts more of the early training gain is
real, as the share predicts, and the knee still comes.

## What the rule costs

Eight half-fits, each on half the contexts and run to a little past
its turn (110 to 390 steps here, the turn itself at 60 to 170). In
steps of a full-size fit that is 630 to 990, against 70 to 200 for
one fit stopped at its knee: the rule costs about five to seven
fits. What it buys is the validation contexts, and one `g*`
serves every matrix fitted on that sample.

## Departures and defects

- **The run took 3 h 57 min against an estimate of 3 h 20 min.** The
  fits on leet and at 64 contexts ran longer before turning than the
  pilot's.
- **Interim readings were reported before the scorer ran.** Nothing
  frozen was changed (the diff of the run code, the scorer, the
  config and the preregistration against 81f4474 is empty) and the
  bars are mechanical.
- **One fit came close to the cap.** `o@8` at 64 contexts turned at
  750 of 800 steps. Had it not, E3 would still have held at 11 of 12.
- **The pilot had two matrices and one condition**, so the caps and
  the E1 threshold were set on little.
- **One model, one corpus, one learning rate, rank 2, four
  matrices.** Three conditions, of which two share a kind of text.
  The rule has now been tried at 8, 32 and 64 contexts and nowhere
  else.
