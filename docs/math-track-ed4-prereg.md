# ED4 preregistration: does a pre-screen pick the module, and is the real share a stopping rule?

Written 03:15 UTC 2026-11-11, after the pilot and before any scored
run. Frozen by the commit that adds this file and
`poc/results/ed4/config.json`; the scorer is
`poc/ecsdec/score4.py`, the run `poc/ecsdec/prescreen.py run`.
After that commit neither the code, the config nor this text
changes; a defect found later is named in the results, not repaired.

## 1. The question

ED3 chose where to extend an existing adapter from a first-order
estimate, on a squared-error form of the estimate. ED4 asks the
plainer version on the cross-entropy loss, before any adapter
exists: from scores computed on the unadapted GPT-2 (base, 124M),
which single weight matrix should a rank-2 LoRA go on? And it tests
one thing the theory note suggested and its pilot took back: whether
the real share of a matrix's leading direction
(`docs/prescreen-theory.md`, sections 6 to 11) says anything about
how long that adapter can be trained.

## 2. What the pilot showed, and what it changed

Four sweeps (16 matrices each, a rank-2 LoRA fitted alone on each for
60 Adam steps) and one set of long fits, all on seed 0:

| pilot condition | contexts (train / scored on) | base loss | sweep's best, gain | `line` beam's best | `slope` beam's best | random three | `rgn` beam's best |
|---|---|---|---|---|---|---|---|
| alternating caps | 96 / 96 | 6.781 | `proj@8` +1.085 | +1.085 | +1.060 | +0.960 | +0.676 |
| plain | 8 / 8 | 6.463 | `proj@8` +0.761 | +0.761 | +0.610 | +0.585 | +0.444 |
| alternating caps | 8 / 8 | 6.929 | `proj@8` +0.827 | +0.827 | +0.792 | +0.720 | +0.635 |
| plain | 32 / 96 test | 6.063 | `proj@8` +0.674 | +0.674 | +0.633 | +0.577 | +0.633 |

1. **There is no no-go case.** Every matrix gained on held-out text
   in every sweep, down to 8 contexts of plain text (smallest gain
   +0.13). The go or no-go gate this experiment was first drafted
   around has nothing to reject here and is dropped.
2. **The same matrix wins everywhere.** `proj@8` is the sweep's best
   in all four, and the order is mostly by kind of matrix (MLP output,
   MLP input, attention output, attention value). A fixed choice made
   once would have matched the sweep. So the scored run carries a
   fixed choice as a competitor, named below.
3. **No cheap score ranks the sixteen.** Rank correlations with the
   fitted gain are between -0.23 and +0.48 for every score. What differs
   is whether a score's best three contain a good matrix: `line` (the
   held-out gain at the training line-search step, logits linearised)
   held `proj@8` in four of four; `slope` reached 80 to 98% of the
   best gain and never held the best; `rgn` was at or below a random
   three in three of four and the gradient norm in all four.
4. **The 30-step linearised fit (`full`) is not a pre-screen.** It
   ranked best on the one sweep it was computed for (+0.49) and cost
   3390 s for 16 matrices against 3943 s for the 16 real fits. It is
   left out of the scored run.
5. **Long fits go bad at every share.** Eight LoRA fits on 8 contexts
   of plain text, run to 300 steps: every one peaks within 110 steps
   and ends 1.1 to 4.1 nats below the unadapted model, at real shares
   from 0.22 to 0.59; stopping at the validation minimum keeps 95 to
   100% of the peak (`docs/prescreen-theory.md`, section 11). The
   scored run tests this on fresh contexts.

**The four predictions of the theory note's section 6, on the
pilot's own numbers.** (1) `line / trainline` close to `2 rho - 1`:
on alternating capitals at 96 contexts the mean absolute difference
is 0.094 (correlation 0.74); on plain text at 8 contexts the measured
median is +0.39 against a predicted +0.16. Partly holds, cautious, as
in section 8. (2) Alternating capitals at 96: every `line` positive
and close to its `trainline`. Holds, 16 of 16, median ratio 1.00.
(3) Plain text at 96 contexts was never run in the pilot (below).
(4) Plain text at 8: `line` negative for half the matrices or more.
Fails, 1 of 16.

**Defects and limits of the pilot.** The first pilot process was
lost to a machine restart after its first condition; the plain-text
condition at 96 contexts was restarted in a second process and then
stopped by hand before its scores, when points 1 and 2 had made the
design change. The first three sweeps scored their selectors and
their fits on the same held-out contexts; the fourth and the scored
run keep them apart. The first process read `docs/*.md` from the
working tree; every later one reads a named commit. The scored
run's contexts are drawn from the same files as the pilot's with
other seeds, so some windows will coincide.

## 3. The scored run

- **Model and adapters.** GPT-2 base; a rank-2 LoRA on one matrix,
  `A` random at 0.02, `B` zero, Adam at 1e-3. Sixteen candidate
  matrices: the value and output blocks of attention and the two MLP
  matrices in layers 2, 5, 8 and 11.
- **Text.** `docs/*.md` at commit `73b70e42`, windows of 16 tokens,
  from three disjoint sets of files: training (every second file),
  validation and test (alternate files of the rest). Scores may look
  at training and validation contexts. Fitted adapters are judged on
  test contexts only.
- **Placement conditions** (four): 32 training, 32 validation and 96
  test contexts of leet, devowelled, word-reversed and plain text.
  The first three transforms were never piloted. Each: all scores for
  the sixteen matrices, then the sweep (60 steps, best iterate by
  training loss).
- **Stopping conditions** (two): 8 training, 96 validation and 96 test
  contexts of leet and of plain text. Each: for the eight matrices of
  layers 2 and 8, the scores, then a fit of 300 steps with every loss
  recorded each 10 steps.
- **Seeds.** Condition `i` draws its contexts with seed `11 + i` and
  its fits with key `4000 + i`. The pilot used 0.
- **Selectors.** Primary: `line`, beam of three. Baselines: `rgn`
  (Auto-RGN's score, on the validation gradient), the training
  gradient norm, the expected outcome of three matrices drawn at
  random (exact, over all 560 triples), and the fixed choice
  `proj@8`, `proj@2`, `proj@5`: the three matrices with the highest
  mean gain over the four pilot sweeps, each sweep's gains divided by
  its best.

## 4. The bars

- **H1, the pre-screen picks well.** On at least three of the four
  placement conditions the `line` beam contains a matrix whose test
  gain is at least 90% of the sweep's best; and the beam's best test
  loss, averaged over the four, is below that of `rgn`, of the
  gradient norm and of a random three.
- **H1p, it is no worse than a fixed choice.** The same average is
  not more than 0.01 nats above the fixed choice's.
- **H2a, a long fit goes bad whatever its share.** In all 16 long
  fits the test gain at step 300 is below half its peak.
- **H2b, stopping on validation keeps the gain.** In at least 14 of
  the 16 the test gain at the step of lowest validation loss is at
  least 90% of the peak.

Reported, with no bar: each score's rank correlation with the fitted
gain and whether its beam holds the sweep's best, including `slope`,
`step` and `cfslope` (the training slope times the cross-fitted
share, a training-only estimate); which matrix wins each sweep; for
the long fits, the real share `rho` (validation slope over training
slope) and the cross-fitted share beside each outcome, their rank
correlation with the final gain, and how many fits with `rho` above
one half are among those that fall.

## 5. Outcomes

Placement: **A** if H1 and H1p hold, **B** if H1 holds and H1p
fails, **C** if H1 fails. Stopping: **confirmed** if H2a and H2b
hold, otherwise **not confirmed**. The two are reported side by
side and neither rescues the other.

What each would mean. A: the look-ahead finds a matrix as good as
the one a full sweep of this model would name, without a sweep; it
does not show the pre-screen beats knowing the model, since the
fixed choice is expected to do as well. B: placement on this model
belongs to the model and not to the text; one sweep, once, is the
better tool and the pre-screen adds nothing to it. C: the look-ahead
does not reliably put a good matrix in its best three; the pilot's
four of four was luck or tied to its seed. Stopping confirmed: the
share is not a stopping rule and the tool's standing warning stays;
not confirmed: the pilot's collapse was particular to its sample,
and the results say which fits held and at what share.

## 6. Run

About 2 h 50 min from timed units of the pilot (a long fit 219 s, a
32-context fit 99 s, scores 67 s per sweep). Every fit is
checkpointed with a hash of its contexts; a process lost to a
machine restart is relaunched with the same command and continues,
which is not a change to the run. The stopping conditions run first.
