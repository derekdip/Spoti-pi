# Literature pass before ED3: linearised predictors of fine-tuning, and where to put an adapter

Written 2026-10-31 between ED2 (`docs/math-track-ed2-results.md`) and
ED3. Scope: the two questions ED2 left open. When is a first-order
(linearised) estimate of a fine-tune's held-out gain a reliable
proxy for the full fit, and what is known about choosing the module
an adapter goes on. A limitation up front: this sandbox cannot fetch
paper text (arXiv and its mirrors, PMLR, OpenReview, ACL, NSF and
Semantic Scholar all fail at the proxy), so every statement below
rests on the search tool's abstract-level summaries, and the numbers
are the ones those summaries quote. Nothing here is from memory.
Where a secondary summary and a paper's own abstract disagree, both
versions are given.

## 1. Fine-tuning as a linearised (kernel) process

**Malladi, Wettig, Yu, Chen, Arora, "A Kernel-Based View of Language
Model Fine-Tuning" (ICML 2023).** Prompt-based few-shot fine-tuning
of RoBERTa-base (16 or 64 examples per label, 14 tasks) is often
described by the empirical neural tangent kernel at the pretrained
point: the eNTK solves 11 of 14 tasks comparably to fine-tuning and
8 or 9 of those show kernel dynamics during the fine-tune (the
abstract versions differ on the count). A secondary summary puts the
linearised model at over half of the fine-tuning gain, with the
kernel staying close before and after the fine-tune; without a
prompt the gap to the real model is up to 16 points, with one about
3. The view extends to Adam and is used to argue why low-rank
updates such as LoRA suffice. Stated limits: few-shot classification
only, one masked model, and failures on entailment (MNLI, SNLI).
What it says for ED2: the first-order gain ED2 computes is a
restricted eNTK prediction (one module, rank 2); the regime where
that prediction is trustworthy is "small moves from the pretrained
point on a prompted task", which the kernel paper validates, and
"many steps on an unprompted objective" is where it reports failure.

**Afzal, Esmaeilbeig, Soltanalian, Ohannessian, "Linearization
Explains Fine-Tuning in Large Language Models" (NeurIPS 2025).** An
explicit distance-to-pretrained penalty puts fine-tuning in the
linearised regime, where the dynamics equal learning with the
positive-definite NTK; when linearisation holds, the NTK's
eigenvalue spectrum correlates strongly with adaptation
performance, with bounds on the empirical risk; validated on LoRA
with a bound on the gap between the full and the LoRA kernel. For
ED3 this is the cleanest statement that a kernel-level quantity
predicts adaptation performance, and that the regime can be
induced by regularising toward the base, which a small budget at
a small learning rate also does.

**Li and co-authors, "Scalable Fine-tuning from Multiple Data
Sources: A First-Order Approximation Approach" (arXiv 2409.19458).**
A first-order expansion from function values and gradients at a
meta-initialisation predicts the fine-tuning loss of a data subset;
across twelve transformer models up to Llama-3-8B the approximation
error is 1e-5 to 1e-3 near the initialisation; the estimates run on
CPU in seconds and the loss-based selection beats gradient- and
representation-similarity selection by up to 3.8 points. This is the
same move as ED2's held-out gain, applied to data subsets instead of
modules, and it is the strongest evidence that the estimate is
accurate where the fine-tune stays close to its start.

**Validation-gradient data selection (ICONS, arXiv 2501.00654; ROSE,
2412.00631; Train-on-Validation, 2510.00386; and a 2026 note on
first- versus second-order terms, 2604.00001).** A family of methods
scores a training example by the first-order change it makes to a
validation loss, as the inner product of its gradient with the
validation gradient or by one validation step and a Taylor
expansion. The second-order note observes that gradient matching
and second-order expansions share the first-order alignment term
and differ in the quadratic one, which at fine-tuning learning
rates near 1e-4 gradient matching over-weights. ED2's score is this
idea with "example" replaced by "module": the held-out gain of the
best rank-2 delta on a module, at first order.

## 2. Why any module fits the training data: intrinsic dimension

**Aghajanyan, Zettlemoyer, Gupta, "Intrinsic Dimensionality
Explains the Effectiveness of Language Model Fine-Tuning" (ACL
2021).** Optimising 200 parameters projected into the full space by
a random map reaches about 90 percent of full fine-tuning on MRPC
with RoBERTa; pretraining lowers the intrinsic dimension and larger
models have lower ones; compression bounds give generalisation
guarantees that do not depend on the parameter count. ED2's mimicry
(a rank-2 adapter on any module removes 65 to 88 percent of a
planted target's training residual at first order) is this result
seen from the other side: at the training data, a random
low-dimensional subspace is enough, so the training residual cannot
tell modules apart. The intrinsic-dimension result goes further
than ED2 measured, since it reports held-out accuracy, which means
that on a prompted task even a random subspace generalises; ED2's
targets (a memorising teacher, then 1536 next tokens) are not that
task, and the held-out separation ED2 saw is the regime where the
subspace does matter.

## 3. The rank at which LoRA has no spurious minima

**Jang, Lee, Ryu, "LoRA Training in the NTK Regime has No Spurious
Local Minima" (ICML 2024).** In the NTK regime full fine-tuning on
N points admits a solution of rank about the square root of N;
LoRA of rank r with r(r+1)/2 > KN (K the output dimension, N the
samples; the secondary summaries agree on this form and one adds an
epsilon-perturbed loss) has no spurious local minima and its
low-rank solution generalises. Below that rank the theorem is
silent, and a follow-up ("LoRA Training Provably Converges to a
Low-Rank Global Minimum or It Fails Loudly", arXiv 2502.09376) has
the failure mode in its title; another ("Rethinking the Rank
Threshold for LoRA Fine-Tuning", 2026) argues that for
cross-entropy there is no threshold even at rank 1. ED2's extend
case is a rank-2 adapter on 12288 training numbers, far below any
such bound, and two restarts found a same-family fit 15 percent
better than the first: the loud failure, measured. ED3 keeps
best-of-restarts students and records how often the restarts beat
the first fit.

## 4. Choosing where to adapt

**Lee, Chen, Tajwar, Kumar, Yao, Liang, Finn, "Surgical Fine-Tuning
Improves Adaptation to Distribution Shifts" (ICLR 2023).** Tuning
one contiguous block beats full fine-tuning under shift, and which
block depends on the shift (first block for input-level corruption,
later blocks for feature-level, the last layer for output-level).
Auto-RGN scores each tensor by the ratio of its gradient norm to
its parameter norm, with the gradient taken on the validation loss
per one summary, normalised across layers, and selects the large
ones; among single-run methods it is best, ahead of full
fine-tuning, gradual unfreezing, L1 and a signal-to-noise variant;
cross-validation over blocks (one fine-tune per block, pick by
held-out) is stronger still but costs a run per block. This is the
literature's version of ED2's question with the literature's
answer: a validation-gradient criterion gets most of the way, a
sweep gets the rest. Auto-RGN is a gradient norm, not a gain; it
ranks sensitivity, which is what ED2's matched-p score also ranked
and found uninformative on its planted case. ED3 runs Auto-RGN as a
comparator.

**A negative result (arXiv 2603.28921, 2026).** With seven layer
groups and three to choose there are 35 selections; a diagnostic's
chosen triple ranked 11th of 35, no better than random, on a
stable protocol, although the top-ranked single layer did carry an
effect (combinations containing it averaged +6.2 against -1.4
without). The authors ask for combinatorial baselines for every
layer-selection claim.

**Placement at scale (arXiv 2604.17573, 2026; 2604.17177; a May
2026 study on GRPO).** On a Qwen 2.5 3B scheduling task, eight
random layers scored 40.7 against 39.8 for activation-probed
layers, statistically indistinguishable: placement "not
load-bearing" at that scale, rank and task. A depth-profile study
found plasticity-guided placement beating random in 5 of 6
comparisons on Mamba but not clearly on BERT; a reinforcement
fine-tuning study found random placement failing where
gradient-informed placement recovered standard LoRA. Together: how
much placement matters depends on scale, rank and training regime,
and a random-placement baseline belongs in any placement test.

**Which kind of module (Biderman et al., "LoRA Learns Less and
Forgets Less", TMLR 2024; and three 2025 to 2026 studies).** On
Llama-2-7B code fine-tuning, attention-only adapters underperform
MLP-only and all-module adapters, most of the gain coming from the
MLP; the recommendation is all modules at high rank when memory
allows, and LoRA is especially sensitive to the learning rate. A
safety-alignment study finds the MLP up-projection matters most, a
document-memory study finds attention-only adapters weakest by 0.02
to 0.09 ROUGE-L, and an interpretability study finds MLP
components carry more of the reasoning signal. ED2's planted module
was an MLP input projection, and the held-out gain ranked the two
other same-layer modules above it; ED3's library keeps both kinds.

**Recent single-run selectors (Aletheia, arXiv 2604.15351;
AdaGradSelect, 2512.15764; Act-LoRA, Information 2026; LoRA-drop;
LAARA).** Gradient probes before training that keep the top half of
layers, activation-norm probes reported as more stable across seeds
than gradient ones, output-norm pruning, and rank allocation from a
diagonal Fisher. All are sensitivity scores on the training signal;
none, in the summaries available, scores a candidate by its
first-order effect on held-out loss.

## 5. What this fixes for ED3

1. **The question is sharper than "does the rule find the module".**
   The literature already has a validation-gradient selector
   (Auto-RGN) and the cross-validation sweep it loses to; the open
   question is whether a first-order held-out *gain* (ED2's score)
   does better than a held-out gradient *norm* at a fraction of the
   sweep's cost, and whether either beats random placement, which
   one study at 3B found it does not.
2. **The regime must be one where the linearisation is trustworthy
   and placement matters.** Small moves from the base (a short
   budget at a small learning rate, as the kernel papers want), a
   target that an adapter generalises on rather than memorises (ED2's
   next-token targets did not), and a library with both attention
   and MLP modules, where the literature expects a difference.
3. **Best-of-restarts students, and a count of restarts that beat
   the first fit**, since rank 2 is far below the no-spurious-minima
   bound.
4. **Combinatorial and random baselines**: random placement with the
   same rank and the same fits, and the full sweep as the ceiling.
5. **Report the predictor's accuracy, not only its ranking**: the
   first-order held-out gain against the fitted held-out gain for
   every module, which is the number the kernel papers say should
   agree when the regime holds.

Sources (search summaries, as fetched 2026-10-31): Malladi et al.
2023 (proceedings.mlr.press/v202/malladi23a); Afzal et al. 2025
(arXiv 2602.08239); Li et al. (arXiv 2409.19458); ICONS (arXiv
2501.00654), ROSE (2412.00631), Train-on-Validation (2510.00386),
first- versus second-order note (2604.00001); Aghajanyan et al.
2021 (ACL 2021.acl-long.568); Jang, Lee, Ryu 2024 (PMLR v235
jang24d), arXiv 2502.09376, "Rethinking the Rank Threshold" (2605.03724);
Lee et al. 2023 (arXiv 2210.11466); arXiv 2603.28921; arXiv
2604.17573; arXiv 2604.17177; Biderman et al. 2024 (arXiv
2405.09673); arXiv 2507.17075, 2606.05698, 2511.06739; Aletheia
(2604.15351), AdaGradSelect (2512.15764), Act-LoRA (Information,
doi 10.3390/info17030283); Sung, Nair, Raffel 2021 (FISH mask, arXiv
2111.09839) and the skill-localisation note on it (2302.06600).
