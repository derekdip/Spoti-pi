# ED4 results: a fixed choice beats the pre-screen for placement; the share is not a stopping rule

Written 06:27 UTC 2026-11-11 from the frozen scorer's report
(`poc/results/ed4/report.md`), which is the record. Preregistration:
`docs/math-track-ed4-prereg.md`, frozen at 0616910. The run started
at 03:15 UTC from that commit and finished at 06:25 with no restart
(`run.log`, `ed4.json`, a checkpoint per condition).

## Outcome, by the frozen rules

**Placement: C. Stopping: confirmed.**

| bar | result | verdict |
|---|---|---|
| H1: the `line` beam reaches 90% of the sweep's best gain on at least 3 of 4 conditions, and its mean best test loss is below random's, RGN's and the gradient norm's | 1 of 4; 5.892 against random 5.843, RGN 5.983, gradient norm 5.983 | fails on both parts |
| H1p: that mean is within 0.01 nats of the fixed choice's | 5.892 against 5.700 | fails |
| H2a: all 16 long fits end below half their peak test gain | 16 of 16, every one below the unadapted model | holds |
| H2b: stopping at the validation minimum keeps 90% of the peak in at least 14 of 16 | 16 of 16 | holds |

The preregistration's reading of C: the look-ahead does not reliably
put a good matrix in its best three, and the pilot's four of four was
luck or tied to its seed. That is the finding.

## Placement

Thirty-two training contexts, scores on 32 validation contexts,
fitted adapters judged on 96 test contexts.

| condition | base test loss | sweep's best, gain | `line` beam's best | the fixed choice's best | random three | RGN beam's best |
|---|---|---|---|---|---|---|
| leet | 6.266 | `proj@8` +1.049 | +1.049 | +1.049 | +0.887 | +0.573 |
| devowelled | 6.460 | `proj@8` +0.880 | +0.687 | +0.880 | +0.741 | +0.476 |
| word-reversed | 7.413 | `proj@8` +0.922 | +0.641 | +0.922 | +0.755 | +0.847 |
| plain | 6.169 | `proj@5` +0.656 | +0.362 | +0.656 | +0.555 | +0.479 |

- **The selector failed.** `line` put `v@11` first in every
  condition and filled its beam with layer-11 matrices in two of
  four. The
  linearised look-ahead is largest where a long step along one
  direction is cheap, and those are not the matrices a real fit gains
  most from. Its beam was worse than three matrices drawn at random.
- **The fixed choice did not.** `proj@8`, `proj@2`, `proj@5`, named
  from the pilot before the run, held the sweep's best matrix in four
  of four conditions, three of them text formats the pilot never saw.
  Its mean best test loss, 5.700, is the sweep's own. `proj@8` alone
  gives 5.702.
- **Placement here belongs to the kind of matrix.** Mean gain as a
  share of each sweep's best: MLP output 0.86, MLP input 0.77,
  attention output 0.59, attention value 0.47; by layer 0.69, 0.70,
  0.70, 0.60. Every one of the 64 fits gained (smallest +0.27), and
  the worst matrix reached 40% of the best in every condition.

Reported, with no bar. No cheap score ranks the sixteen: rank
correlations with the fitted gain run from -0.45 to +0.46.

| score | mean best test loss of its beam | holds the sweep's best | within 90% of the best |
|---|---|---|---|
| `step` (look-ahead at a fixed step) | 5.727 | 3 of 4 | 3 of 4 |
| `slope`, `trainslope`, `cfslope` | 5.812 | 0 of 4 | 1 of 4 |
| `trainline` | 5.840 | 1 of 4 | 2 of 4 |
| random three | 5.843 | | |
| `line` (the preregistered selector) | 5.892 | 1 of 4 | 1 of 4 |
| RGN, gradient norm | 5.983 | 0 of 4 | 1 of 4 |
| the fixed choice | 5.700 | 4 of 4 | 4 of 4 |

`step` would have met H1's first part and beaten random; it was not
the preregistered selector, it scored below `line` in the pilot
(two of four against four of four), and it is still 0.027 nats behind
the fixed choice. It is reported, not promoted. The slope the
portable tool ranks by (`slope` with held-out text, a training-only
estimate without) beat a random three by 0.03 nats and never held
the best matrix.

## Stopping

Eight training contexts, 300 Adam steps (five times the sweep's
budget), losses on 96 validation and 96 test contexts every 10
steps, eight matrices per condition.

| condition | real share `rho` | peak test gain | step of the peak | test gain at step 300 | kept by stopping at the validation minimum |
|---|---|---|---|---|---|
| leet | 0.43 to 0.58 | +0.48 to +0.93 | 60 to 140 | -0.68 to -3.07 | 98 to 100% of the peak |
| plain | 0.29 to 0.44 | +0.33 to +0.50 | 50 to 100 | -1.41 to -4.34 | 100% |

All 16 fits end below the unadapted model while their training loss
falls by 3.1 to 5.8 nats. Six had a real share above one half and
fell with the rest. Within a condition the share does not order the
final gain (rank correlations -0.21 and +0.48). So the reading of
the half rule as a stopping rule (theory note, sections 6 and 8) is
withdrawn for real fits, as section 11 recorded from the pilot, and
ordinary validation stopping recovers the peak.

## What this leaves of the earlier claims

- **The tool's ranking.** `docs/prescreen-tool.md` said that whether
  the slope ranks matrices by their fitted gain was ED4's to decide.
  It does not, on this model: the tool's numbers describe the first
  step of a fit, and which matrix gains most over a whole fit is
  decided by something a first step does not see. The tool's text is
  changed to say so.
- **ED3.** ED3 chose among extensions of an existing adapter with a
  linearised held-out fit, on a squared-error loss, and its outcome
  stands as recorded. The nearest thing here, the 30-step linearised
  fit, ranked best in the one pilot sweep it was computed for (+0.49)
  and cost as much as the sweep, which is why it was left out. ED4
  does not test ED3's rule; it shows that the cheap first-order
  scores are not a substitute for it.
- **The share.** What survives is in the theory note, section 12,
  outside this experiment's bars: on these same 16 long fits the
  share is the rate at which test gain accrues at the start
  (rank correlation 0.83), the turn comes at a training gain common
  to the matrices of a sample, and stopping at a cross-fitted
  estimate of it kept a positive gain in all 16.

## Departures and defects

- **Side jobs slowed the run.** Two exploratory checks
  (`knee_check.py`) ran on one core from 05:08 to 06:05. The scores
  of the last two placement conditions took 468 s against 83 and 90 s
  for the first two. The computations are deterministic; only the
  timings in `ed4.json` are affected.
- **The scored rows were read before the scorer ran.** Interim
  readings of finished conditions were reported as the run went, and
  the knee check read the two stopping conditions' rows after they
  were complete and before the placement conditions finished. Nothing
  frozen was changed (the diff of the run code, the scorer, the
  config and the preregistration against 0616910 is empty), and the
  bars are mechanical.
- **The pilot's selector choice did not hold.** `line` was chosen
  because it held the sweep's best in four of four pilot sweeps; in
  three of those the scores had looked at the same contexts the fits
  were judged on. The scored run kept them apart.
- **One model, small samples.** GPT-2 base, 32 and 8 contexts of 16
  tokens from this repository's documents, rank 2, one learning rate.
  That the same matrix wins everywhere is a statement about this
  model and these texts.
