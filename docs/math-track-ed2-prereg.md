# ED2: ECS-Decision with sketched geometry on GPT-2. Preregistration (frozen before any scored case is run)

ED1 (`docs/math-track-ed1-results.md`) ran the decision rule on a
toy transformer with exact Jacobians and Hessians and found it right
on every constructed case, with two instruments doing less work than
the handoff assumed. ED2 asks the two questions ED1 could not: does
the rule survive the move to a real pretrained language model, where
every geometric quantity has to be estimated by products rather than
formed; and on real data, where no truth is planted, does its choice
of where to add capacity match what a full sweep finds, at what cost
in fits.

## The model, the data, the state

`poc/ecsdec/gpt2.py`: GPT-2 base (124M parameters, 12 layers, 12
heads, width 768) in JAX, loaded from the Keras NLP preset's weights,
verified before the freeze by its loss on this repository's README
and by greedy continuations ("import numpy as" gives " np;"). Float32
throughout. Module keys `q@l, k@l, v@l, o@l, fc@l, proj@l`.

The data is this repository's own documentation, `docs/*.md`:
even-indexed files give the training probes, odd-indexed files the
held-out probes, a probe being 16 consecutive tokens and the token
that follows. A world is a seed, 48 training and 48 held-out probes
for the planted cases, 96 and 96 for the real-data case.

The state is the model's next-token distribution on each probe,
restricted to a support: the base model's top 256 tokens for that
probe with the document's actual next token swapped in for the
lowest-ranked one. 12288 numbers for 48 probes. The full vocabulary
(50257 numbers per probe) would make the candidate sketches too
large for this machine; the support carries most of the mass and the
true token always. Held-out cross-entropy on the full vocabulary is
reported beside the state distortion on the real-data case.

Adapters are LoRA pairs `B A` on a module. A fit is Adam at a frozen
learning rate for a frozen number of steps on
`F = 0.5 ||x - G(theta)||^2`, best iterate kept. Distortion is
`D = ||x - G(theta)|| / ||x||`, on training probes for the rule and
on held-out probes for the deployment objective.

## Targets

**Teacher adapters, for the planted cases.** A first pilot planted
random-direction deltas and found the model insensitive to them: a
delta as large as the weight matrix itself moved the state by 0.3.
A fine-tune delta is small and lies in sensitive directions, so the
targets are teacher adapters: a LoRA of known module and rank fitted
on the training probes' next tokens for 10 steps at learning rate
3e-3, then frozen. The truth (module, rank) is known by construction
and the delta is the kind a fine-tune produces. Its effect on the
held-out probes is 5 to 7 times smaller than on its own (the pilot
measured 0.22 to 0.37 against 0.03 to 0.06), which is what a
10-step adapter is: partly memorisation. Held-out distortion
therefore has a small range on the planted cases and the size term
of the deployment objective is set well below it.

**The documents themselves, for the real-data case.** The target is
the one-hot of the actual next token on the support at every
position of every context (96 contexts of 16 tokens, 1536 targets),
the Brier form of the fine-tuning objective, with the same on 96
held-out contexts for the deployment objective. The pilot's
last-position version (96 targets) overfitted at every setting
(held-out distortion 1.01 against the base's 0.97, held-out
cross-entropy 6.5 against 5.5), which is what 96 examples do to an
adapter; every position costs no extra forward pass. No truth is
planted: the question is whether the rule's choice matches a full
sweep, or says, when it is so, that no adapter beats the base.

## The rule with sketched geometry

`poc/ecsdec/sketch.py`. The handoff's sections in the same order as
ED1, with every quantity formed from Jacobian-vector, vector-Jacobian
and Hessian-vector products:

1. **Adequacy.** `D <= D_max` returns STOP.
2. **Stationarity.** `s = ||J^T r|| / (sigma_max(J) ||r||)` with
   `J^T r` one VJP and `sigma_max` by 6 power iterations on `J^T J`.
   `s > eps_g` returns REFINE. There is no conditioning test and no
   REPARAMETERIZE: a sketch cannot estimate the smallest singular
   value, and ED1 already measured that test with the exact
   spectrum. The collinear case is not constructed.
3. **Curvature.** `lambda_min(H_F)` and `||H_F||` by 12 steps of
   Lanczos with full reorthogonalisation on Hessian-vector products;
   `lambda_min < -eps_H ||H_F||` marks the first stage GLOBALIZE,
   otherwise LOCALLY EXHAUSTED. ED1 showed every budgeted fit is
   indefinite, so this label is recorded and the budget decides.
4. **Bounded globalization.** 2 multistarts of the same family from
   random factors at scale 0.02 (both factors random), each at the
   budget; a 10 percent fall in `F` returns GLOBALIZE, otherwise the
   rule continues to expansion.
5. **Tangent quotient.** A random 16-direction sketch of the current
   family's tangent space (16 JVPs, orthonormalised); the residual's
   component in it is removed. The sketched `tau` is a lower bound
   on the exact one and is reported as such.
6. **Candidates.** The library is four module kinds (`v, o, fc,
   proj`) at layers 3, 7 and 11 (12 syntaxes), with one compiled JVP
   and one compiled VJP serving every module's dense first-order
   block at its neutral state, the current adapter folded in. Two
   scores are computed for each candidate:
   - the handoff's matched-`p` score, reported: a sketch of 8 random
     direction matrices pushed through one JVP each, one round of
     subspace iteration (8 VJPs and 8 JVPs) toward the block's top
     principal directions, projected off the tangent sketch and
     orthonormalised; `eta` at `p in {1, 3, 12}`, coherence,
     projector distance, containment, winning atoms. The pilot found
     this score does not rank the planted module (8th of 12 on the
     extend case): with 48 contexts any module's rank-2 adapter can
     mimic the target on the training probes, so no training-residual
     geometry separates modules, and the top principal directions
     measure a module's sensitivity rather than its relevance.
   - the **linearised held-out gain**, the preregistered ranking
     score, the handoff's "complexity-adjusted variant" of section
     13: a rank-2 adapter on the module fitted to the training
     residual in the linearised model by 30 Adam steps (one JVP and
     one VJP per step, explicit chain rule through the factors), then
     the fraction of the current held-out residual that the same
     delta removes at first order (one held-out JVP). It asks, at
     first order and at the deployment data, what the full fit will
     be judged on. Candidates are ranked on it.
7. **Equivalence.** COLLAPSE when the sketched spans contain each
   other at 0.95 both ways; the matched-`p` rule reported beside it.
   GPT-2 has twelve heads, so no pair of modules spans one
   first-order space (ED1's two-head pilot measured 0.74 for the
   value and output pair); no COLLAPSE truth is constructed and the
   stage is expected to fire on nothing.
8. **Beam and full fits.** The top 3 survivors by held-out gain are
   fitted in full as the augmented model (the current adapter and a
   rank-2 adapter on the module, together, from the current state);
   the beam the matched-`p` score would have given is recorded. The
   fallback of the decision is the base model, no adapter: the safe
   default of a fine-tune, and the only answer available when
   fitting hurts held-out, which the pilot's real-data case did. The
   all-modules adapter (rank 2 on all 12) is fitted and reported, as
   ED1's fallback was, but does not enter the decision.
9. **Deployment objective.** `J = D_held + lambda_s n`, `n` the
   adapter's parameter count (zero for the base). EXPAND when the
   best fitted candidate's `J` is under `(1 - 0.01) J_current` and
   not above the base's; otherwise FALLBACK naming the base when it
   beats the current by the same margin, else the current.

## The cases

| case | target | student | truth |
|---|---|---|---|
| refine | teacher rank 2 on `v@7` | rank 2 on `v@7`, 10 percent of the budget | REFINE |
| saddle | the same | `theta = 0` | GLOBALIZE |
| extend | teacher rank 2 on `fc@7` | rank 2 on `v@7`, fitted | EXPAND on `fc@7` |
| noise | the base state plus independent noise on each probe set | rank 2 on `v@7`, fitted | FALLBACK |
| adequate | teacher rank 2 on `v@7` | rank 2 on `v@7`, fitted at twice the budget | STOP |
| real | the documents' next tokens | rank 2 on `v@7`, fitted; then the rule with every candidate also fitted (the sweep) | none |

Teachers are amplified twofold (their delta doubled) so that the
held-out range is usable. There is no reuse case: the pilot found a
rank-1 student fits a rank-3 teacher on the same module to within
1.3 of a rank-3 student on the training probes and within 1.2 on
held-out, at this budget, so no bar separates them (the numbers are
in the pilot section). ED1 tested reuse with exact geometry.

## The frozen values

`poc/results/ed2/config.json`, committed with this document.

| quantity | value | source |
|---|---|---|
| `eps_g` | 0.5 | pilot: the student after 10 percent of the budget sits at `s` 0.87 to 0.88; students fitted to the budget at 0.17 to 0.23, at twice the budget 0.04; a budgeted Adam run on this model is not stationary to better than a tenth, so the threshold sits between the start of a fit and its end |
| `D_max` | 0.015 | pilot: the adequate student (twice the budget on its own teacher) at 0.0071, the extend student at 0.049, the refine student at 0.17; a factor 2.1 below and 3.3 above |
| `eps_H` | `1e-6 ||H_F||` | relative, as in ED1, loosened for float32 |
| budget | 2 multistarts at scale 0.02, better = 10 percent of `F` | pilot: the budget found 0.0 percent on the extend student; two is the cost this machine allows |
| tangent sketch | 16 directions | one JVP each |
| candidate sketch | 8 directions, one subspace iteration | for the reported matched-`p` score |
| linearised fit | 30 Adam steps at 3e-3, rank 2 | pilot: train gains 0.65 to 0.88, held-out gains -0.33 to 0.37 on the extend case |
| ranking | held-out gain | see the rule, item 6 |
| beam | 3 | the handoff's value |
| candidate rank | 2 | the teachers' rank |
| equivalence | containment 0.95 both ways on the sketched spans | as ED1; expected to fire on nothing |
| `lambda_s` | 1e-7 per parameter | a candidate's 3072 to 7680 parameters cost 0.0003 to 0.0008 and the fallback's 55k cost 0.0055, against held-out distortions of a few hundredths |
| spent | 1 percent | the repository's rule |
| fit | 60 Adam steps at 3e-3 | pilot: 60 steps brings a student to `D` 0.017 on its own teacher from 0.21; 120 to 0.007; a fit is 50 to 70 seconds |
| teachers | 10 steps at 3e-3 on the training probes' next tokens, doubled | pilot: base to target 0.21 to 0.49 on the training probes, 0.05 to 0.06 held out |
| refine fraction | 10 percent (6 steps) | pilot: `D` 0.17, `s` 0.88 |
| adequate | twice the budget | pilot: `D` 0.0071 |
| noise case | 0.5 of the state's rms | the base plus independent noise on each probe set |
| probes | 48 and 48 for the planted cases, 96 and 96 for the real-data case; 16-token contexts; support 256 | memory and time |
| library | `v, o, fc, proj` at layers 3, 7, 11 | 12 syntaxes; the planted module among them |
| worlds | seed 1 (planted), seed 2 (real) | the pilot is seed 0 |

## The declared pilot

World seed 0 (the scored run uses seed 1 for the planted cases and
seed 2 for the real-data case). A first pilot on a 64-token support,
`pilot0_support64.log`, is kept for the sizing defect it found (2048
state numbers against 3072 adapter parameters, so fits were
underdetermined) and the random-direction targets it used. Excluded
from every bar; nothing is changed after it.

Logs: `pilot1_teacher_scan.log` (teachers, fit curves),
`pilot2.log` (the chosen teacher: students, budget, tangent, the
matched-`p` candidate scores on an 18-module library),
`pilot3_mimicry.log`, `pilot4_heldgain.log` (the held-out gain on the
extend case, joint fits), `pilot5_allpositions.log` (the real-data
case on every position); `pilot2_oomkilled.log` is the block the
memory cgroup killed when every program still folded the weights in.

- **Teachers.** Fitted on the training probes' next tokens, a
  rank-2 teacher on `v@7` moves the training-probe state by 0.007,
  0.028 and 0.142 after 5, 10 and 20 steps at 1e-3 and by 0.222
  after 10 steps at 3e-3; on `fc@7` by 0.014, 0.067, 0.295 and 0.370.
  Held-out effects are 5 to 7 times smaller. Doubled, the `v@7`
  teacher of the chosen block sits at 0.208 (held-out 0.055), the
  `fc@7` teacher at 0.49 (0.049).
- **A student on its own teacher (rank 2 on `v@7`, doubled).** After
  6, 60 and 120 steps at 3e-3: `D` 0.171, 0.017, 0.0071; held-out
  0.050, 0.021, 0.017; `s` 0.88, 0.19, 0.041.
- **The extend student (rank 2 on `v@7` against the `fc@7` teacher).**
  `D` 0.049, held-out 0.053, `s` 0.17, `lambda_min` -0.025 against
  `||H||` 2.5; the budget of 2 lowers `F` by 0.0 percent; the sketched
  `tau` 0.19 (0.085 at single amplitude).
- **Mimicry.** On 48 contexts at the budget, the wrong family fits
  the training state nearly as well as the right one: for the `fc@7`
  teacher, a `v@7` student reaches 0.029 (0.060 doubled) against an
  `fc@7` student's 0.019 (0.041); for a rank-3 `v@7` teacher a rank-1
  student reaches 0.014 against a rank-3 student's 0.011; at 96
  contexts the right family is not even ahead on training distortion
  (0.028 against 0.019). Held-out separates by about 2 (0.040 against
  0.020; 0.087 against 0.036 doubled). Hence no reuse case and the
  held-out gain as the ranking.
- **Candidate scores on the extend case.** Matched-`p` `eta` at
  `p = 12` ranks the planted `fc@7` 8th of 18 (with `q, k` in the
  library) and 4th of 12 (0.110 behind `proj@11` 0.154, `proj@3`
  0.124, `v@3` 0.118). The linearised train gains are 0.65 to 0.88
  for every module. The held-out gains: `proj@7` 0.366, `o@7` 0.362,
  `fc@7` 0.288, `o@3` 0.174, `v@7` 0.132, `fc@3` 0.110, `proj@3`
  0.068, the layer-11 modules and `v@3` negative (-0.08 to -0.33).
  Joint fits (held-out `D`): `fc@7` 0.028, `proj@11` 0.032, `v@11`
  0.032, `v@3` 0.035, the current 0.053; `proj@7` and `o@7` were not
  fitted in the pilot.
- **The real-data case, every position (96 contexts, 1536 targets).**
  Base `D` 0.98 (held-out 0.99), held-out cross-entropy 6.04. The
  rank-2 `v@7` student after 60 steps: at 3e-3 `D` 0.955, held-out
  0.986, cross-entropy 6.02, `s` 0.016, `lambda_min` -2.6 against
  `||H||` 207; at 1e-3 held-out 0.984 and cross-entropy 5.94. Held-out
  gains: `fc@11` 0.001, `v@3` -0.019, `proj@7` -0.018 (train 0.02 to
  0.03). The joint fit with `fc@11`: training 0.87, held-out 1.03,
  cross-entropy 8.2. At this budget an added rank-2 module anywhere
  overfits; the last-position version (96 targets) did so even for
  the student alone.
- **Costs.** A 60-step fit 50 to 70 s on 48 contexts, 130 to 220 s on
  96; a candidate's two scores 165 s on 48 contexts and 270 s on 96;
  Lanczos 30 to 70 s; peak memory 2 to 3.5 GB.

## Bars (frozen)

`poc/ecsdec/score2.py`, committed with this document.

- **F1, the planted cases.** The rule returns the truth on at least 4
  of the 5 cases, with the extend case naming `fc@7`.
- **F2, the real-data case.** The rule's choice (the chosen module,
  the base, or the current, whichever it returns) has a deployment
  objective within 1 percent of the sweep's best single module, or
  better. Fits used by each are reported.
- **F3, reported.** The sketched `tau`, every candidate `eta`, the
  pairs under both equivalence rules, the held-out cross-entropy of
  the base, the current and the chosen adapter on the real-data
  case, the fallback's distortions, time per stage.

## Predictions

- **F1 holds, 5 of 5, with one named risk.** refine: REFINE (`s`
  about 0.9 against 0.5). saddle: first stage GLOBALIZE, the budget
  lowers `F` by far more than 10 percent, GLOBALIZE. adequate: STOP
  (`D` about 0.007 against 0.015). noise: inadequate, stationary,
  the budget finds nothing, every held-out gain near zero, no fit
  improves held-out, the base (at the noise level, about 0.5) beats
  the current (about 0.57) by more than 1 percent: FALLBACK naming
  the base. extend: inadequate (`D` about 0.05), stationary, first
  stage GLOBALIZE, the budget finds nothing; the held-out gain puts
  `fc@7` in the beam with `proj@7` and `o@7` (the pilot's order:
  `proj@7`, `o@7`, `fc@7`); the joint fit on `fc@7` wins on held-out
  by 10 to 20 percent over the others and `J` falls under the
  current's by half: EXPAND on `fc@7`. The risk: the two same-layer
  modules above it were not fitted in the pilot, and if one lands
  within that margin the case is lost on the module name alone;
  F1 then fails although the rule's action and the deployment gain
  are right.
- **F2 holds, by the base and the current beating every module.**
  The real student is stationary and indefinite, the budget finds
  nothing, every held-out gain is within 0.02 of zero, every joint
  fit overfits (held-out above 1.0 against the current's 0.986 and
  the base's 0.99); the rule returns FALLBACK naming the current
  (the base is not 1 percent better); the sweep's best module has
  `J` above 1.0; the rule's choice is better. The finding to expect:
  on 1536 real targets at this budget no rank-2 module anywhere
  improves held-out, and the first-order held-out gain says so
  before any fit.
- **F3.** The matched-`p` beam on extend excludes `fc@7`; the
  equivalence stage collapses nothing (containments below 0.6);
  sketched `tau` 0.1 to 0.2 on the planted cases.
- Letter **A**, with the extend module name as the way it becomes B.

## Outcome (frozen, exclusive)

- **A**: F1 and F2 hold.
- **B**: F1 holds, F2 fails.
- **C**: F2 holds, F1 fails.
- **D**: neither.

F3 is reported under every letter. No rescue, no second run on the
scored worlds, no change to the model, the data, the state, the
cases, the rule, the thresholds or the budgets after this commit.
Results go in `docs/math-track-ed2-results.md`; nothing above is
edited after the run.
