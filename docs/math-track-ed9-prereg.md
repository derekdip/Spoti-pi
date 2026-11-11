# ED9 preregistration: the knee and the stopping rule for larger adapters

Written 2026-11-11 at about 19:20 UTC, after two declared pilots and
before any scored fit. Frozen by the commit "ED9 freeze", which adds
this file, `poc/results/ed9/run/config.json` and the version of
`poc/tools/lora_big.py` that runs and scores it. After that commit
none of them changes; a defect found later is named in the results.
Run: `python3 poc/tools/lora_big.py run poc/results/ed9/run/config.json poc/results/ed9/run`;
report: `python3 poc/tools/lora_big.py score poc/results/ed9/run`.
ED7 is paused for this (`poc/results/ed7/run/PAUSED.md`).

## 1. The question

Everything from ED4 to ED7 used the smallest adapter that works: a
rank-2 LoRA on one matrix. Practice uses rank 8 to 64 on every
matrix. Two questions:

1. Does the knee (the training gain at the test peak) move with the
   adapter's size, and if so with its rank or with its reach (one
   matrix or all of them)?
2. Does the cross-fitted stopping rule still keep the gain, with
   `g*` measured for each adapter and with one `g*` shared by all six?

## 2. The pilots (declared, not scored)

GPT-2 base, plain text, 8 contexts, seed 60
(`poc/results/ed9/pilot/`, `pilot2/`).

- At Adam's 1e-3, adapters on all 48 matrices peaked at step 5 to 10,
  between the first evaluations, so their knees could not be located.
  The rank-32 one-matrix adapter peaked at step 20.
- With learning rates lowered so each adapter needs 50 or more steps
  to peak, the knee was 1.27 to 1.38 for one matrix (rank 2 and 32)
  and 1.79 to 1.95 for all 48 (rank 8 and 32, learning rates 1e-4 to
  1e-5). Halving the rank-2 adapter's rate moved its peak from step 50
  to 85 and its knee from 1.26 to 1.27, as section 15's check K6 of
  `docs/prescreen-theory.md` predicts.
- On this sample the half-fits ran high for every adapter (`g*` 2.1
  to 2.9). In the first pilot the rank-2 adapter stopped at its own
  `g*` ended below the unadapted model (-0.38 of its peak), the first
  time in any run.

## 3. The scored run

GPT-2 base; plain text at 8 and at 32 training contexts and leet at
32, with 32 validation and 96 test contexts each; seeds 61 to 63,
none used before. Corpus, windows and files as ED4 to ED7.

Six adapters, each target matrix with its own LoRA (A at 0.02, B
zero, no scaling), all trained by one Adam:

| adapter | reach | rank | learning rate |
|---|---|---|---|
| `r2-one` | `proj@2` (layer 2 MLP output) | 2 | 1e-3 |
| `r8-one` | `proj@2` | 8 | 3e-4 |
| `r32-one` | `proj@2` | 32 | 1e-4 |
| `r2-all` | all 48 block matrices | 2 | 3e-4 |
| `r8-all` | all 48 | 8 | 1e-4 |
| `r32-all` | all 48 | 32 | 3e-5 |

The learning rates are chosen so each adapter peaks after 50 or more
steps; `r8-one` and `r2-all` were not piloted and their rates are
interpolated. Loss recorded every 5 steps. Per condition and adapter:
a full fit until its test gain has fallen to a quarter of its peak or
1000 steps; two half-fits until the other half's gain has fallen to
half its peak or 700 steps. Own `g*`: the mean of the adapter's two
half-fit knees. Shared `g*`: the median of the condition's twelve.

## 4. Bars, over the 18 full fits

- **B1** (rank does not move the knee): in each condition, within each
  reach, the three knees have a c.v. below 0.2.
- **B2** (reach does): in each condition the mean all-matrix knee is
  more than 1.2 times the mean one-matrix knee.
- **R1** (the rule, own `g*`): the test gain is positive in all 18 and
  at least two thirds of the peak in at least 15.
- **R2** (one shared `g*`): the same, at the shared `g*`.

Reported with no bar: the knees per adapter and condition, the share
kept at the validation minimum, the steps to the peak, and how far
past the peak each fit fell.

## 5. What the outcomes would mean

- **B1 and B2 hold**: the knee belongs to the data and the adapter's
  reach, not to its rank or learning rate. A stopping value measured
  once per data kind and adapter layout could then be reused across
  ranks and learning rates.
- **B1 fails**: rank moves the knee as well, and a stopping value has
  to be measured for every adapter configuration.
- **B2 fails**: the pilot's difference between one and all matrices
  was that sample's; a single knee per kind of data may serve all
  sizes.
- **R1 holds**: the rule carries to adapters of practical size. **R1
  fails at 8 contexts only**: the overshoot of section 15 again; the
  rule is then for 16 or more examples. **R2 fails while R1 holds**:
  measure `g*` with the adapter you will use.

## 6. Cost

About 2.5 to 3 hours on 4 CPU threads (the 8-context pilot of six
adapters took 20 minutes; contexts per step scale it fourfold at 32).
Each condition's rows and checkpoints are committed and pushed as it
finishes.
