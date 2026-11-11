# Stopping without held-out data: what is already known

Written 2026-11-11 from a search of the Hugging Face paper index, the
only literature source reachable from this session. Entries marked
*recalled* were not in the index and are from memory, unchecked.

## Close prior work

- *Recalled.* Mahsereci, Balles, Lassner and Hennig, "Early Stopping
  without a Validation Set" (2017). Stops when the mean gradient is
  indistinguishable from per-example noise (the "EB" criterion).
- *Recalled.* Forouzesh and Thiran, "Disparity Between Batches as a
  Signal for Early Stopping" (2021). The distance between the gradients
  of two batches of the training data; stop when it rises. Aimed at
  small and label-noisy samples, without a validation set.
- Chatterjee, "Coherent Gradients" (arXiv 2002.10657, 2020).
  Generalisation as the agreement of per-example gradients.
- Zeng et al., "GradES" (arXiv 2509.01842, 2025). Stops the updates of
  each transformer matrix separately when its gradient changes fall
  below a threshold; no validation passes.
- Gao, Schulman and Hilton, "Scaling Laws for Reward Model
  Overoptimization" (arXiv 2210.10760, 2022), and Rafailov et al. for
  direct alignment (arXiv 2406.02900, 2024). The true reward peaks at a
  predictable distance from the starting policy, measured in KL, not in
  steps: the same shape as the knee in training gain.
- Perez, Kiela and Cho, "True Few-Shot Learning with Language Models"
  (arXiv 2105.11447, 2021). Choosing settings without held-out examples
  is unreliable; the problem this track addresses.

## What this means for the track

The online signals (gradient agreement or disparity between halves,
the EB criterion) are not new, and the cross-fitted knee is a form of
two-fold cross-validation. Not found in this search: that the stopping
point measured in training gain is shared across the matrices, ranks
and learning rates of an adapter of a given reach, and across models
of one lineage (ED4 to ED6, ED9), so that a budget in training gain
calibrated once could be reused. The search was a handful of queries
over one index; this is not a claim of novelty.

ED10 (`poc/tools/lora_online.py`) puts the recalled signals beside the
cross-fitted knee and held-out stopping on the same fits.
