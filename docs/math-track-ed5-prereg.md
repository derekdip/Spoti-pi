# ED5 preregistration: does the knee, and the stopping rule built on it, hold at 32 and 64 contexts?

Written 07:08 UTC 2026-11-11, after a declared pilot and before any
scored run. Frozen by the commit that adds this file,
`poc/results/ed5/config.json` and `poc/ecsdec/score5.py`; the run is
`poc/ecsdec/knee.py run`. After that commit neither the code, the
config nor this text changes; a defect found later is named in the
results, not repaired.

## 1. The question

On 24 long LoRA fits at 8 training contexts (ED4 and the checks
beside it, `docs/prescreen-theory.md`, section 12) the gain on fresh
text turned at a training gain common to the matrices of a sample,
and stopping a fit at a cross-fitted estimate of that training gain
kept a positive gain in 24 of 24 and two thirds of the peak in 23.
Nothing was tried at larger samples, where a 60-step fit does not
turn at all. ED5 asks whether the same holds at 32 and 64 contexts.

## 2. The pilot

Seed 0, plain text, 32 training contexts, two matrices
(`poc/results/ed5/pilot.log`, `pilot.json`):

| matrix | peak test gain (step) | training gain at the peak | kept at `g*` = 1.04 | at step 60 | at the validation minimum | at the last step (steps run) |
|---|---|---|---|---|---|---|
| `proj@8` | +0.702 (80) | 1.12 | 0.99 | 0.95 | 1.00 | +0.25 (220) |
| `v@2` | +0.514 (140) | 0.89 | 0.93 | 0.87 | 1.00 | +0.22 (330) |

Both fits turned; the four half-fits' knees were 1.42, 1.22, 0.85
and 0.78. A matrix cost about 10 minutes, full fit and both
half-fits. What the pilot set: the caps (800 steps for a full fit,
500 for a half-fit, neither reached), and that a condition of four
matrices fits in about 40 minutes at 32 contexts. It also shows the
60-step budget is already close to the peak at this size, so the
rule has less to add here than at 8 contexts; E4 is written knowing
that.

## 3. The scored run

- **Model, adapter, text** as in ED4: GPT-2 base, a rank-2 LoRA on
  one matrix, Adam at 1e-3; `docs/*.md` at commit `73b70e42`, windows
  of 16 tokens; training, validation and test contexts from three
  disjoint sets of files.
- **Conditions** (three, seeds 21 to 23, none used before): plain
  text at 32 training contexts, leet at 32, plain text at 64; 32
  validation and 96 test contexts each.
- **Matrices** (four): `proj@2`, `proj@8`, `v@2`, `o@8`, two MLP
  output matrices and two attention matrices.
- **Per matrix.** A full fit on all the training contexts, losses on
  validation and test contexts every 10 steps, run until the test
  gain has fallen to a quarter of its peak at least 50 steps after
  the peak, or to 800 steps. Two half-fits, each on one half of the
  training contexts with the loss on the other half every 10 steps,
  run until that gain has fallen to half its peak at least 50 steps
  after it, or to 500 steps.
- **The rule.** A half-fit's knee is its training gain where the
  other half's loss is lowest. `g*` is the median of the condition's
  eight knees. A full fit is stopped where its training gain first
  reaches `g*` (linear interpolation between recorded steps); if it
  never does, at its last recorded step.

## 4. The bars

- **E1, the knee is common to the matrices.** In every condition the
  training gain at the test peak has a coefficient of variation below
  0.35 across the four matrices.
- **E2, the rule keeps the gain.** Stopped at `g*`, the test gain is
  positive in all 12 full fits and at least two thirds of the peak in
  at least 10, with at least 3 of 4 in every condition.
- **E3, long fits go bad at this size.** At least 10 of the 12 full
  fits turn within the cap, that is, their test gain falls to a
  quarter of its peak.
- **E4, the rule is at least as good as the 60-step budget.** The
  share of the peak kept, averaged over the 12 fits, is not lower at
  `g*` than at step 60.

Reported, with no bar: the share kept at the validation minimum and
at the last step; `g*` against the mean training gain at the test
peak; the spread of the half-fits' knees and how many half-fits
turned; the training gain at the knee at 32 and 64 contexts beside
the 1.15 to 1.82 seen at 8; the test gain over the training gain in
the first 30 steps.

## 5. Outcomes

**A** if E1 to E4 all hold. **B** if E2 holds and any of E1, E3, E4
fails. **C** if E2 fails.

What each would mean. A: the knee and the rule carry to these sizes
as they stood at 8 contexts. B: the rule is safe to use here, with
the failed bar saying what is different: the knee is not common to
the matrices (E1), long training is no longer the danger it was
(E3), or a plain step budget does as well (E4), in which case the
rule's use is at small samples only. C: the rule does not carry;
the results say where it stopped a fit too early or too late.

## 6. Run

About 3 h 20 min from the pilot's timed units (40 minutes for each
condition at 32 contexts, about two hours at 64, where a step costs
twice as much and the turn may come later). Every fit is
checkpointed with a hash of its contexts; a process lost to a
machine restart is relaunched with the same command and continues.
No other job runs on the machine during the run.
