# ED7 preregistration (DRAFT, not frozen): the rule against holding data out

Draft written 2026-11-11, before any run on a real model. It becomes
the preregistration only when a commit says "ED7 freeze" and adds the
scored config; until then the bars below may change after the pilot,
and every change will be listed here.

## 1. The question

The use the stopping rule was proposed for: with only `n` examples,
spend all of them on training and stop at the cross-fitted knee `g*`,
instead of holding some out to see when to stop. Every comparison so
far (ED4, ED5) kept the training set fixed and gave validation 32 to
96 contexts of its own, which is not that trade
(`docs/prescreen-theory.md`, section 14). The one look at the real
trade, ED4's half-fits read after the fact, had the rule ahead on leet
text and level on plain text, against a 4+4 split, the weakest way to
hold out. ED7 asks: **for the same `n`, does the rule leave the model
better on fresh text than stopping on held-out examples taken from the
`n`?** It is measured in nats of test gain, not as a share of each
fit's own peak.

## 2. Arms, per condition and matrix

All fits as in ED5 and `poc/tools/lora_knee.py`: rank 2, Adam at
1e-3, the same corpus draws, CTX 16. Tool: `poc/tools/lora_trade.py`.

- **rule**: a full fit on all `n` contexts; the condition's eight
  half-fits (four matrices, both ways round); stop where the full
  fit's training gain reaches `g*`, the median of the eight knees.
- **hold25**: split the `n` into 4 folds; for each fold, fit on the
  other three quarters and stop at the fold's lowest loss. The arm's
  value is the mean over the 4 folds (the expected result of one
  random split).
- **hold12**: the same with 8 folds, folds 0 and 1 only (cost).
- **hold25+refit@step**, **hold25+refit@gain** (and the same for
  hold12): what practitioners do next, refit on all `n` for the
  chosen number of steps, or to the chosen training gain. Read off the
  rule's full fit, with no new training. `refit@gain` is the rule with
  a single asymmetric split instead of a median of eight.
- Reference, not in the trade: **extra_val** (stop on 32 extra
  contexts) and **peak** (the best the full fit reached on test).

The test contexts (96) are never used to stop anything.

## 3. Conditions (proposed)

GPT-2 base, the matrices of ED5 (`proj@2`, `proj@8`, `v@2`, `o@8`),
plain text and leet at `n` = 8, 16 and 32: six conditions, 24
(condition, matrix) pairs. Seeds 41 to 46, none used before. Caps
800 and 500 steps as in ED5.

## 4. Bars (proposed, to be fixed after the pilot)

Over the 24 pairs, against **hold25** and against **hold12** each:

- **T1.** The rule's mean test gain is higher.
- **T2.** The rule is ahead in at least 16 of 24 pairs.
- **T3.** In no condition is the rule behind by more than 0.05 nats
  on average over its four matrices.

Against the refit arms the same numbers are reported with no bar:
they are the stronger practice and the question is how close the
rule gets, not whether it wins.

Outcomes: **A** if T1 to T3 hold against both splits (the rule is
the better use of a small sample here); **B** if T1 holds against
both and T2 or T3 fails somewhere; **C** otherwise (holding data out
is at least as good, and the rule's claimed use does not stand on
GPT-2 base).

## 5. Pilot (declared, not scored)

One condition (plain, `n` = 8, seed 40) with two matrices, to time
the arms and check that the held-out fits turn within the cap
(`poc/results/ed7/pilot/config.json`). Before it, a port check: this
session has transformers 5.22 where the ED6 cross-check had an older
version, so ED5's plain-text condition at 32 contexts (seed 21) must
give the same context hash and base test loss (6.392) again. The
proposed scored config is `poc/results/ed7/run/config.draft.json`.

Steps once the weights can be fetched:

    poc/tools/fetch_gpt2.sh $SCRATCH/gpt2_hf      # the path in the configs
    python3 poc/tools/lora_trade.py run poc/results/ed7/pilot/config.json poc/results/ed7/pilot
    python3 poc/tools/lora_trade.py score poc/results/ed7/pilot

Cost, from ED5's timings scaled: about 4 to 5 hours on this
machine's 4 CPU threads for the six scored conditions, most of it at
32 contexts.

## 6. What is not in reach from this session

The model weights: huggingface.co is not allowed by this session's
network. The pipeline is checked on a tiny random GPT-2 with a
byte-level vocabulary (`smoke/` in the session's scratch space), which
tests the code and nothing else.
