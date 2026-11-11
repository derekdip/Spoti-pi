# ED9 results: the knee and the stopping rule for larger adapters

Written 2026-11-11 from the frozen scorer's report
(`poc/results/ed9/run/report.md`), which is the record.
Preregistration: `docs/math-track-ed9-prereg.md`, frozen at eb3fce8.
The run started at 19:16 UTC from that commit and ended at 20:32 with
no restart; each condition was committed as it finished. The diff of
`poc/tools/lora_big.py`, `poc/tools/lora_knee.py`, the config and the
preregistration against eb3fce8 is empty.

## Outcome, by the frozen bars: all four hold

| bar | result | verdict |
|---|---|---|
| B1: rank does not move the knee; within each reach the three knees have a c.v. below 0.2 | largest c.v. 0.07 | holds |
| B2: reach moves it; the all-matrix knee is more than 1.2 times the one-matrix knee in every condition | 1.46, 1.61, 1.21 | holds, narrowly on leet |
| R1: at each adapter's own `g*`, positive in 18 of 18 and two thirds of the peak in at least 15 | 18 positive, 16 above two thirds | holds |
| R2: at one shared `g*`, the same | 18 positive, 15 above two thirds | holds, at the bar |

## The knees

Training gain at the test peak (step of the peak):

| condition | `r2-one` | `r8-one` | `r32-one` | `r2-all` | `r8-all` | `r32-all` |
|---|---|---|---|---|---|---|
| plain, 8 | 1.25 (45) | 1.15 (65) | 1.04 (75) | 1.51 (35) | 1.79 (55) | 1.71 (75) |
| plain, 32 | 1.22 (80) | 1.16 (105) | 1.12 (145) | 1.91 (60) | 1.83 (80) | 1.89 (120) |
| leet, 32 | 1.65 (105) | 1.52 (140) | 1.54 (205) | 1.92 (60) | 1.86 (80) | 1.94 (120) |

- **The knee belongs to the data and the adapter's reach, not to its
  rank or learning rate.** From rank 2 to 32, with learning rates that
  differ thirtyfold and peaks from step 35 to 205, the knee stays
  within 7% inside a reach (c.v. 0.02 to 0.07). Between reaches it
  moves: an adapter on all 48 matrices turns 1.2 to 1.6 times later in
  training gain than one on a single matrix.
- **One small trend inside B1.** On one matrix the knee falls a little
  with rank in all three conditions (1.25, 1.15, 1.04; 1.22, 1.16,
  1.12; 1.65, 1.52, 1.54). The bar allowed it; it is not noise-sized
  only by its consistency.
- **The gap between reaches narrows on leet** (1.21 against 1.46 and
  1.61 on plain text): the one-matrix knee rises with the format shift
  and the all-matrix knee hardly does. B2 held by 0.01.
- **Larger adapters gain more, and more so with more data.** The
  all-matrix adapters' peak test gain is 1.1 to 1.3 times the
  one-matrix ones' at 8 contexts and 1.1 to 1.4 times at 32. Rank adds
  nothing inside a reach: rank 32 is never better than rank 2.

## The rule

Share of the peak kept:

| condition | own `g*`: mean (lowest) | shared `g*`: mean (lowest) | validation minimum |
|---|---|---|---|
| plain, 8 | 0.83 (0.66) | 0.76 (0.50) | 1.00 |
| plain, 32 | 0.98 (0.93) | 0.87 (0.72) | 1.00 |
| leet, 32 | 1.00 (0.99) | 0.98 (0.95) | 1.00 |

- **At 32 contexts the rule works for every adapter size**: 0.93 to
  1.00 of the peak at the adapter's own `g*`, with nothing held out.
- **At 8 contexts it overshoots**, as in ED4, ED6 and ED7's pilot: the
  one-matrix adapters at rank 8 and 32 kept 0.66, just under two
  thirds. The all-matrix adapters kept 0.90 to 0.98.
- **One shared `g*` is worse than the adapter's own** (0.87 against
  0.94 on average) because it sits between the two reaches' knees; on
  plain text it stops the one-matrix adapters late. R2 passed at the
  bar. Measure `g*` with the reach you will use.

## Departures and defects

- **The preregistration says it was written "at about 19:20 UTC"; the
  freeze commit and the run's start were at 19:15 to 19:16.** The text
  was written before the run; the stated time was a guess.
- **The cost estimate was 2.5 to 3 hours; the run took 1 h 16 min.**
- **`r8-one` and `r2-all` were not piloted**; their learning rates were
  interpolated and both peaked after 35 steps or more as intended.
- **ED7 was paused for this run** (`poc/results/ed7/run/PAUSED.md`).
- **One model (GPT-2 base), one corpus, three samples, 16-token
  contexts.** LoRA without the usual alpha/r scaling, so rank and
  learning rate are not separable here; the learning rates were chosen
  per adapter to make the turn measurable.
- **The pilots' first sample** (seed 60) had the rank-2 adapter end
  below the unadapted model at its own `g*` (-0.38 of its peak), the
  first time in any run. It was a pilot and is not scored; the scored
  8-context sample did not repeat it.

## What it means

A stopping budget in training gain can be measured once per kind of
data and adapter layout (one matrix or all of them) and reused across
ranks and learning rates. It cannot be shared between layouts. The
cross-fit that measures it needs more than 8 examples to be reliable.
