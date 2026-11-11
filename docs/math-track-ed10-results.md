# ED10 results: the online share does not replace the cross-fit, as designed

Written 2026-11-11 from the frozen scorer's report
(`poc/results/ed10/run/report.md`), which is the record.
Preregistration: `docs/math-track-ed10-prereg.md`, frozen at 7b0cb2a.
The run started at 21:30 UTC and ended at 23:28 with no restart; each
condition was committed as it finished. The diff of the run's code,
config and preregistration against 7b0cb2a is empty.

## Outcome, by the frozen bars: C

| bar | result | verdict |
|---|---|---|
| O1: the online share keeps a positive gain in 24 of 24 and two thirds of the peak in 20 | 22 positive, 18 above two thirds | fails |
| O2: its mean is within 0.05 of the cross-fitted rule's | 0.695 against 0.940 | fails |
| O3: it beats the published signals as implemented | 0.695 against 0.030, 0.177, 0.270 | holds |

Share of the peak kept, over 24 fits: cross-fitted rule 0.94 (lowest
0.77, 24 above two thirds), online share 0.70 (-0.24, 18), raw
disparity 0.03, relative disparity 0.18, EB 0.27 (7 above two
thirds), validation minimum 1.00.

| condition | reach | rule | share | best published (which) | validation |
|---|---|---|---|---|---|
| plain, 8 | one | 0.90 | 0.76 | 0.02 (disparity) | 1.00 |
| plain, 8 | all | 0.87 | -0.08 | 0.02 (disparity) | 1.00 |
| plain, 16 | one | 0.94 | 0.96 | 0.29 (EB) | 1.00 |
| plain, 16 | all | 0.95 | -0.11 | 0.35 (relative disparity) | 1.00 |
| plain, 32 | one | 0.94 | 0.91 | 0.52 (EB) | 0.99 |
| plain, 32 | all | 0.96 | 0.62 | 0.44 (relative disparity) | 1.00 |
| leet, 32 | one | 0.98 | 0.83 | 0.92 (EB) | 1.00 |
| leet, 32 | all | 1.00 | 1.00 | 0.46 (EB) | 1.00 |

## What went wrong, and why

- **On the all-matrix adapters the raw share stops late or never**
  (plain text: -0.08, -0.11 and 0.62 by condition). It stays positive
  past the test peak. The identity of section 12 is about the step
  taken; Adam's step is the gradient rescaled per coordinate, and on
  48 matrices that rescaling is far from uniform, so the agreement of
  raw gradients is not the real share of Adam's step. This is a
  defect of the design, not of the identity; it was visible in the
  first condition's interim reading and the run was left to finish as
  frozen.
- **On one-matrix adapters it stops early at times**: a single reading
  at or below zero ends the fit, and at 8 contexts (halves of 4) one
  noisy dip stopped `v@2` at 0.31 of its peak. Over the 16 one-matrix
  fits it kept 0.87 on average against the rule's 0.94; at 16 and 32
  contexts on plain text 0.96 and 0.91.
- **The published signals, as rebuilt from memory, are worse still.**
  Raw disparity rises from the start of a LoRA fit and stops at the
  first evaluation every time; relative disparity and EB fire late or
  never. They are adapted versions, unchecked against the papers.

## Departures and defects

- **The raw-gradient share ignores the optimiser's preconditioning**
  (above). Named, not repaired; ED11 (`poc/tools/lora_online2.py`)
  tests the share in Adam's metric with two consecutive readings to
  stop, on fresh samples, after its own pilot.
- **The cost estimate was 2 to 2.5 hours; the run took 1 h 59 min.**
- **The cross-fitted rule here interpolates between evaluations**
  (as ED5's scorer did); the pilot's first scoring did not, which
  moved its lowest value from 0.93 to 0.95.
- **One model, one corpus, four samples.**

## What it means

The cross-fitted rule stays the one that works from the training
contexts alone (0.94 on average, never below two thirds). An online
estimate of the real share is the right quantity by the identity, but
measured on raw gradients it is wrong for Adam on many matrices and
too noisy to stop on a single reading at 8 contexts.
