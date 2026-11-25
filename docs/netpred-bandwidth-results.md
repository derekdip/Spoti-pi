# NB1 results: bandwidth of model-predictive avatar sync

Written 2026-11-25 from the frozen scorer's report
(`poc/results/netpred/bw_run/report.md`). Preregistration
`docs/netpred-bandwidth-prereg.md`, frozen at 89a1539; the run ended at
18:44 UTC with no restart; the diff of the code, config and
preregistration against 89a1539 is empty. Synthetic motion, no network delay.

## By the frozen bars

| bar | result | verdict |
|---|---|---|
| W1: learned receiver 30% below the best simple one at every tolerance | 9%, 9%, 0% at 0.5, 1, 2 cm | fails |
| W2: error never above the tolerance | every receiver, every player, every frame | holds |
| W3: personalising saves 5% more at 1 cm | -0.3% | fails |
| W4: the width-256 receiver below the width-64 one at every tolerance | 695 against 776, 412 against 478, 316 against 366 | holds |

Bytes per second per player, mean over 24 (streaming every frame: 1980):

| receiver | 0.5 cm | 1 cm | 2 cm |
|---|---|---|---|
| hold | 1131 | 732 | 435 |
| dead reckoning, last two frames | 1277 | 994 | 847 |
| dead reckoning, velocity over six frames | 763 | 452 | 316 |
| learned, width 64 | 776 | 478 | 366 |
| learned, width 256 | 695 | 412 | 316 |
| learned, personalised | 704 | 413 | 314 |

Per player, the learned receiver against smoothed dead reckoning: median
7.9%, 6.8%, -3.4% fewer bytes at 0.5, 1, 2 cm; better for 22, 19 and 9 of 24.

## What it shows

- **The protocol is the large effect**: sending a tracker only when the
  receiver would be off by more than the tolerance cuts bandwidth by 61
  to 84% against streaming, with any reasonable predictor, and the
  error guarantee holds exactly. This is the established
  dead-reckoning-with-threshold technique (as in the DIS simulation
  standard), not a new one.
- **A learned shared model adds little** over smoothed dead reckoning:
  about 7 to 9% at tight tolerances and nothing at 2 cm.
- **A larger receiver model sends less than a small one** (8 to 14%):
  more decoder computation buys bandwidth, as the Farey note's section
  14 suggests, but the small learned model is no better than smoothed
  dead reckoning.
- **Personalising does not help bandwidth.**
- The pilot's 40 to 60% saving was against weak baselines (hold and
  unsmoothed dead reckoning); the same caution applies to NP1's 78%,
  which was measured against unsmoothed constant velocity.

## Departures and defects

- One value of smoothed dead reckoning was seen before the freeze (named
  in the preregistration); the bars were left as planned.
- The synthetic motion is built from minimum-jerk curves, which suit
  constant-velocity extrapolation; real motion may favour the learned
  receiver more. No network delay was modelled.
