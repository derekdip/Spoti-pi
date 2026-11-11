# A pre-screen for LoRA fine-tuning (`poc/tools/lora_prescreen.py`)

A single-file PyTorch tool that, before any training, tells you for
every candidate weight matrix of a causal language model how fast
the loss would fall along the best low-rank direction, how much of
that is real rather than sampling noise, and how much rank the data
can support. It is the portable form of what the ED rounds and
`docs/prescreen-theory.md` measured on GPT-2 in JAX.

## Use

    python poc/tools/lora_prescreen.py --model PATH_OR_NAME --train train.txt \
        [--held held.txt] [--rank 2] [--contexts 96] [--ctx 64] [--targets REGEX] [--top 3] [--json out.json]

`--model` is anything `transformers.AutoModelForCausalLM` loads.
`--train` and `--held` are plain text files; the tool samples
`--contexts` windows of `--ctx` tokens from each. `--targets` is a
regular expression over parameter names (the default covers
attention and MLP projections and skips embeddings, norms and the
output head). As a library: `prescreen(model, train_tokens,
held_tokens)` takes token tensors and returns the table as a dict.

It needs torch and transformers, one gradient pass over the training
windows (taken as two halves) and one over the held-out windows if
given. No training, no adapters, no extra memory beyond one gradient
per target matrix. Singular values are computed exactly, which is
fine to a few thousand rows and columns per matrix.

## The columns

| column | meaning |
|---|---|
| `train` | the first-order rate at which the training loss falls per unit Frobenius norm of a rank-r change to this matrix |
| `shrunk` | the part of `train` predicted to hold on fresh data, from training data alone (singular-value shrinkage at the noise edge measured by splitting the training windows in half) |
| `floor` | a guaranteed lower bound on the fresh-data rate: `train` minus the measured noise |
| `held` | the rate measured on the held-out windows (only with `--held`) |
| `snr` | the leading singular value of the gradient over that of the noise; near 1 the direction is noise |
| `above` | how many leading directions clear the noise edge: a floor on the rank the data supports, usually far below it |
| `cf` | the cross-fitted real share: the rank-r direction is taken from one half of the training windows and its rate is measured on the other half, as a fraction of its rate on its own half, averaged both ways. No noise model. It describes a direction fitted on half the data, so it reads low |
| `rank` | how many leading directions have a cross-fitted share above one half: a cautious estimate of the rank worth fitting |

Rows are sorted by `held` when held-out text is given and by
`shrunk` otherwise. The closing lines name the leading modules and
say, from the median `snr`, whether the data is enough for the
ranking to mean anything, and, from the median `cf`, whether the
leading direction is mostly signal or mostly sampling noise. The last
line is a standing warning: none of these numbers says how long to
train (`docs/prescreen-theory.md`, section 11).

## What is established, and what is not

- **The numbers are right.** Run on GPT-2 from the Hugging Face
  weights, the tool reproduces the JAX implementation (run from the
  Keras preset's weights) on the same token windows: both losses to
  six digits and every slope, shrunk slope and noise edge to 7e-5
  relative (`poc/tools/crosscheck_gpt2.py`,
  `poc/tools/crosscheck_jax_ref.py`). Two frameworks, two weight
  files, one answer. The cross-fitted share agrees to 3.4e-6 and the
  cross-fitted rank on 12 of 12 matrices.
- **`shrunk` predicts `held`.** On GPT-2 base, three text conditions,
  training sets of 8 to 128 contexts, 16 matrices: mean absolute log
  error 0.105, against 0.247 for `train`, and three to four times
  better at 8 contexts. `floor` held in 238 of 240 cases.
  (`docs/prescreen-theory.md`.)
- **`rank` is cautious and `above` is only a floor.** Same model and
  conditions, first eight directions of each matrix, a direction
  counted as worth fitting when more than half of its rate is real
  against 192 held-out contexts. `rank` never exceeded the number
  worth fitting (15 of 15 conditions) and was off by 1.4 directions
  on average; `above` stayed near 2 while the true number rose to 6
  to 8 at 128 contexts, off by 2.8 on average. With 8 or 16 contexts
  neither is reliable. `cf` read low in 13 of 15 conditions; halving
  its distance to one corrects for the halved sample and then
  predicts `held` as well as `shrunk` does (error 0.100 against
  0.097), except at 8 contexts of plain text, where it overshoots.
  `cf` cannot see a difference between the training text and the
  text the model will meet. (`docs/prescreen-theory.md`, sections 9
  and 10.)
- **A first-order held-out estimate chose the right module** on a
  planted case and on one real format shift (ED3,
  `docs/math-track-ed3-results.md`), in a squared-error form of the
  estimate.
- **The ranking does not say which matrix gains most over a whole
  fit.** ED4 (`docs/math-track-ed4-results.md`) fitted a rank-2 LoRA
  on each of 16 matrices of GPT-2 base in four text conditions. The
  slope's best three never held the best matrix and beat three drawn
  at random by 0.03 nats; the preregistered look-ahead selector did
  worse than random; no first-order score had a rank correlation
  above 0.46 with the fitted gain. A fixed choice of the MLP output
  matrices, named before the run, held the best in four of four. Read
  the ranking as "where a small change helps most" and nothing more;
  for placement on a model, run one sweep once.
- **The share is not a stopping rule.** The half rule of the theory
  note (a direction less than half real loses if fitted to its
  training optimum) held in a linearised check and did not carry to
  real training: in a pilot at 8 contexts, eight LoRA fits run to 300
  Adam steps all ended 1.1 to 4.1 nats below the unadapted model on
  fresh text, at shares from 0.22 to 0.59, two of them above one
  half. Stopping at the minimum of a validation loss kept at least
  95% of each fit's peak gain. Use a validation set to stop, or,
  with no text to spare, the cross-fitted knee of
  `docs/prescreen-theory.md`, sections 12 and 13: it kept a positive
  gain in 36 of 36 long fits at 8, 32 and 64 contexts and 97% of the
  peak at the two larger sizes (ED5, `docs/math-track-ed5-results.md`).
  The tool does not compute it; `poc/ecsdec/knee.py` does, for the
  JAX model.
- **Not established.** A slope is an infinitesimal rate. It is
  positive for every matrix even where a full fine-tune overfits, so
  the tool does not say whether to fine-tune at all, and it does not
  say how far a module can usefully move. One model family (GPT-2
  base) has been measured.

## Example (GPT-2 base, 32 contexts of 16 tokens of this repository's documents in alternating capitalisation)

    training loss 6.639, held-out loss 6.738; 32 contexts; rank 2; ranked by held_slope

    module                                         shape    train   shrunk    floor     held    snr above     cf  rank
    transformer.h.2.mlp.c_proj.weight         3072x768     1.3323   1.1753   0.8372   1.0877   2.75     2   0.77     2
    transformer.h.2.mlp.c_fc.weight            768x3072    1.1229   1.0060   0.6890   0.9638   2.61     2   0.75     2
    transformer.h.5.attn.c_attn.weight         768x2304    0.9995   0.8952   0.6157   0.9059   2.62     2   0.84     2
    ...
    transformer.h.8.attn.c_proj.weight         768x768     0.1938   0.1616   0.1094   0.1675   2.35     1   0.78     2

    largest held_slope: transformer.h.2.mlp.c_proj.weight, transformer.h.2.mlp.c_fc.weight, transformer.h.5.attn.c_attn.weight
    median signal-to-noise 2.57: the leading directions are real at this data size
    median cross-fitted share 0.78: above one half: the leading direction is predicted to hold on more text like the training text
    none of these numbers says how long to train: hold text out and stop when its loss turns
