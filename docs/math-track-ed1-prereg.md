# ED1: ECS-Decision v1 on a model with adapters. Preregistration (frozen before any scored case is run)

`docs/ecs-decision-v1-handoff.md` froze a decision rule for growing a
representation: given a fit, decide among STOP, REFINE,
REPARAMETERIZE, GLOBALIZE, EXPAND and FALLBACK from the residual's
geometry, and among COLLAPSE and KEEP DISTINCT for candidate
extensions, with a twelve-case synthetic suite, sweeps and five
ablations. Its editorial left every threshold "to be frozen". This
round runs that rule, unchanged in structure, on an actual model: a
small transformer language model whose representation is grown by
adapters, where every case's right action is known by construction.
The question is the handoff's own: does the geometry (stationarity,
conditioning, curvature, the tangent quotient, novel-span equivalence,
a deployment objective) pick the right action, and does each layer
earn its place against the ablations.

## The model and the state

`poc/ecsdec/model.py`. A decoder-only transformer, vocabulary 16,
width 32, one attention head, two layers, MLP width 64, context 16,
pre-norm, learned positions, double precision, trained from scratch
by Adam (1500 steps of 64 sequences) on a synthetic language: a sparse
Markov chain with a copy rule at offsets 2 and 3, so attention is
needed. One head is deliberate: with one head a change of the value
matrix and a change of the output matrix of the same layer span one
first-order space exactly (`delta_v Wo = Wv delta_o`), which is the
handoff's Case 8 by construction; with two heads they do not (the
first pilot measured their mutual containment at 0.74).

The state the rule reads is the model's predictive distribution on a
fixed probe set: 256 training contexts and 256 held-out contexts
sampled from the language, 16 probabilities each, flattened (4096
numbers per set). A family of adapters is a list of modules with a
kind: a LoRA pair `B A` of a given rank on a weight matrix, a dense
delta, or a logit bias; `G(theta)` is the adapted model's training
probe distribution, and the target `x` is the probe distribution of
the base model with planted deltas. Distortion is normalised,
`D = ||x - G(theta)|| / ||x||`, on the training probes for the rule
and on the held-out probes for the deployment objective.

A fit is Adam at learning rate 0.02 for a frozen 300 steps on
`F = 0.5 ||x - G(theta)||^2`, keeping the best iterate. All Jacobians
are exact (forward-mode automatic differentiation in chunks), the
Hessian is the exact Jacobian of the gradient.

## The rule, as implemented

`poc/ecsdec/decide.py`, the handoff's sections 4 to 16 in order.

1. **Adequacy.** `D <= D_max` returns STOP.
2. **Stationarity.** `s = ||J^T r|| / (sigma_max(J) ||r||)`. If
   `s > eps_g`: REFINE when the Jacobian is well conditioned,
   REPARAMETERIZE when `kappa = sigma_max / sigma_min > kappa_max`.
   Conditioning is read on the numerical rank: singular values below
   `1e-8 sigma_max` are null. This is forced by the adapters: a LoRA
   pair has the exact gauge `(B M, M^-1 A)`, so `r^2` directions of
   its Jacobian are exactly zero at every point, and the handoff's
   literal `sigma_min` would return REPARAMETERIZE for every LoRA
   student. The tangent projector uses the same rank, as the
   editorial asked.
3. **Curvature.** If `lambda_min(H_F) < -eps_H ||H_F||`, the first
   stage is GLOBALIZE; otherwise LOCALLY EXHAUSTED.
4. **Bounded globalization (section 7).** For GLOBALIZE and LOCALLY
   EXHAUSTED alike: 8 fits of the same family from random factors at
   scale 0.2 (A and B both random, so the all-zero saddle is left),
   each at the frozen budget. If the best lowers `F` by 10 percent of
   `F(theta)`, the action is GLOBALIZE; otherwise the rule continues
   to expansion, as section 7 says. The editorial's 16-per-axis grid
   on at most three axes is dropped: an adapter has no three
   distinguished axes.
5. **Candidate geometry (sections 8 to 11).** A candidate syntax is a
   module: `wv@0, wo@0, wv@1, wo@1, w1@1, w2@1, out_bias`. Its
   first-order block `K` is the Jacobian of the dense delta on that
   module at the neutral state with the current adapter folded in (a
   LoRA's Jacobian at `B = A = 0` is zero, so the dense delta is the
   only first-order object). The novel block is `K` projected off the
   current tangent; its principal subspaces at `p in {1, 3, 12}` and
   its full span (numerical rank) give `eta` at each `p` and on the
   full span, coherence `mu` and projector distance `d` at each `p`
   (equal dimensions, so `d` is the sine of the largest principal
   angle), directed containment on the full spans, and the winning
   atoms' alignment.
6. **Equivalence (section 12).** COLLAPSE when the full novel spans
   contain each other: `c_ij >= 0.95` and `c_ji >= 0.95`, section
   11's directed containment, both ways. The editorial proposed the
   matched-`p` rule (`d <= 0.2` and `mu >= 0.95` at every `p`); the
   pilot shows that rule reads parameterisation, not span: the pair
   that spans one space by construction has distinct principal
   directions because `Wo` and `Wv` weigh the directions
   differently. The matched-`p` verdict is computed and reported
   beside the primary one on every pair. When two syntaxes collapse,
   the cheaper (by fitted parameters) stays, the first named on a
   tie.
7. **Beam (section 13).** The survivors ranked by `eta` at `p = 12`,
   the largest matched dimension; the top 3 are fitted in full as
   the augmented model: the current adapter and a rank-4 adapter on
   the module (the bias as itself) fitted together at the budget,
   from the current state and the usual initialisation. The dense
   delta is not what is fitted: the first pilot fitted dense deltas
   and a 2048-parameter delta on 256 probes overfitted (train 0.058,
   held-out 0.199 on the extend case). Nor is the current adapter
   frozen: the second pilot fitted candidates beside a frozen
   current and the candidate on the planted module could not reach
   the target (held-out 0.060 on the reuse case against the
   fallback's 0.025), because the frozen rank-1 fit is not a
   component of the planted rank-4 delta. The fallback is the
   current adapter with rank-4 adapters on every module and the
   bias, fitted the same way.
8. **Deployment objective (section 14).** `J = D_held + lambda_s n`,
   `n` the adapter's parameter count (current plus added), with
   `lambda_s = 1e-5` per parameter: a candidate's 256 to 384 added
   parameters cost 0.003 to 0.004 and the fallback's 1808 cost
   0.018, which is the editorial's principle (a state cost
   comparable to the distortion differences the suite produces, here
   a few hundredths between a candidate and the fallback on held-out
   probes). The shared-bytes, encoding and decode terms are zero and
   said to be: every fit has the same budget and the base model is
   shared by every candidate.
9. **EXPAND (section 15).** The best fitted candidate's `J` must be
   under `(1 - 0.01) J_current` (the spent rule) and not above the
   fallback's; otherwise FALLBACK, naming the fallback when it beats
   the current by the same margin and "current" when nothing does.

## The frozen values

`poc/results/ed1/config.json`, committed with this document.

| quantity | value | source |
|---|---|---|
| `eps_g` | 5e-2 | pilot: students fitted to the budget on a target their family cannot reach sit at 1.6e-3 to 1.6e-2 (the best iterate of a budgeted Adam run is not a stationary point to better than that); students after 5 to 10 percent of the budget sit at 0.21 to 0.27; the editorial's 1e-6 assumes an exact least-squares solver |
| `D_max` | 0.05 | the editorial's value, on the normalised distortion |
| rank cutoff | `1e-8 sigma_max` | the editorial's `gamma_min`, used as the numerical rank |
| `kappa_max` | 1e6 | the editorial's value; pilot: healthy students 6.7e3 to 1.0e5, the collinear construction 5.8e7 to 8.8e7 |
| `eps_H` | `1e-8 ||H_F||` | the editorial's value |
| `p` | {1, 3, 12} | the handoff's set |
| equivalence | containment >= 0.95 both ways on the full novel spans | see the rule, item 6; the matched-`p` rule (`d <= 0.2`, `mu >= 0.95`) reported |
| beam | 3 | the editorial's value |
| globalization | 8 multistarts at scale 0.2, "substantially better" = 10 percent of `F` | the editorial's value, without the grid |
| candidate rank | 4 | contains every planted delta (ranks 2 and 4 against a rank-1 student) |
| `lambda_s` | 1e-5 per parameter | see the rule, item 8 |
| spent | 1 percent | the repository's rule |
| planted scale | 1.0 (base to target 0.44) | pilot |
| refine fractions | 5 and 10 percent of the budget | pilot: `D` 0.19 and 0.11 against `D_max` 0.05 (20 percent already reaches 0.048), `s` 0.27 and 0.21 |
| collinear tolerance | 1e-6 | pilot: `kappa` 8.8e7 with the collinear directions above the rank cutoff (at 1e-8 they fall under it and the rank drops to 151 of 256) |
| noise case level | 0.5 of the target's rms | pilot: the fitted student stays at 0.44 |
| student restarts | best of 4 | pilot: a budget of 8 then finds nothing better than 0.4 percent |
| noise levels | {0, 0.01, 0.05, 0.1} of the rms | the editorial's set |
| misspecification | {0.01, 0.03, 0.1, 0.3, 1} of the planted scale | the editorial's set; pilot: crosses `D_max` between 0.1 and 0.3 |
| scored world | seed 1 | the pilot is seed 0 |

## The cases (`poc/ecsdec/suite.py`)

Each case is a target (the base with planted deltas), a current
family and its state, and the right action by construction.

| case | target | student | truth |
|---|---|---|---|
| refine_early | rank 2 on `wv@0` | rank 2 on `wv@0`, 5 percent of the budget | REFINE |
| refine_mid | the same | 10 percent of the budget | REFINE |
| saddle | the same | `theta = 0` (stationary, indefinite) | GLOBALIZE |
| reuse | rank 4 on `wv@0` | rank 1 on `wv@0`, fitted | EXPAND on `wv@0` (or `wo@0`, its exact equivalent with one head) |
| collinear | rank 2 on `wv@0` | rank 4 on `wv@0` with its four `A` rows equal to 1e-6, `B` fitted with `A` held | REPARAMETERIZE |
| extend | rank 2 on `w2@1` | rank 2 on `wv@0`, fitted | EXPAND on `w2@1` |
| noise | the base plus independent noise on each probe set | rank 2 on `wv@0`, fitted | FALLBACK |
| adequate | rank 2 on `wv@0` | rank 2 on `wv@0`, fitted | STOP |
| pair 1 | the extend residual | `wv@1` against `wo@1` | COLLAPSE |
| pair 2 | the extend residual | `wv@0` against `w2@1` | KEEP DISTINCT |

Sweeps: noise at the four levels on refine_early, reuse, extend and
adequate (reported); the extend magnitude at the five levels, scored
against the truth the deployment bar defines (STOP when the fitted
student's `D` is within `D_max`, else EXPAND on `w2@1`).

The handoff's Case 12 (a genuine local minimum with a much better
minimum elsewhere in the family) has no construction here and is
not claimed; the saddle case is its Case 3.

Ablations, each the full rule minus one layer:

- **A, magnitude only.** Adequacy, then straight to expansion: no
  stationarity, conditioning, curvature or globalization; candidates
  ranked by `eta` on the full span.
- **B, gradient only.** Adequacy and stationarity; no conditioning,
  curvature or globalization.
- **C, no conditioning.** Everything but the `kappa` test.
- **D, no tangent quotient.** Candidates scored against the raw
  residual with the unprojected block.
- **E, no equivalence.** No COLLAPSE; the beam may hold two
  equivalent syntaxes.

Arms run as separate processes on the same world (`arm <name> 1`),
merged by `merge`; the per-case record keeps every diagnostic the
handoff lists in its metrics section.

## The declared pilot

World seed 0, `poc/results/ed1/pilot_h1.log`, `pilot2_h1.log` and
`pilot3_h1.log` (a first pilot with two heads, dense candidate fits
and a frozen current adapter, `pilot.log` and `pilot2.log`, is kept
for the three construction defects it found, named above). Excluded
from every bar; nothing is changed after it.

- The base reaches loss 1.805; the planted rank-2 delta at scale 1
  puts the target 0.361 from the base.
- The rank-2 student on its own target after 15, 30, 60, 120 and 300
  steps: `D` 0.191, 0.106, 0.048, 0.026, 0.013; `s` 0.27, 0.21,
  0.10, 0.027, 0.017; `kappa` 1.1e4 to 4.1e4; `lambda_min` negative
  at every stage (-1.3 to -1.7e-3 against `||H||` 9.5 to 24): a
  budgeted Adam iterate is never a local minimum to the curvature
  test's precision, so every fitted student's first stage reads
  GLOBALIZE and the budget decides.
- At `theta = 0`: `s = 0`, rank 0, `lambda_min = -4.78 = -||H||`.
- The collinear student (`A` held, `B` fitted): `D` 0.374, `s`
  0.18 to 0.29, `kappa` 7.6e7, 8.8e7 and 5.8e7 at tolerances 1e-4,
  1e-6 and 1e-8.
- Students fitted to the budget on reuse, extend and noise (best of
  1 and of 4): `s` 1.6e-3 to 1.6e-2, `tau` 0.00 to 0.06, the budget
  of 8 multistarts improves `F` by 0.2 to 1.1 percent. The adequate
  student: `D` 0.010.
- Candidate `eta` at `p = 12` on reuse: `wv@0` 0.11, `wo@0` 0.10,
  `out_bias` 0.10, `w2@1` 0.09, `w1@1` 0.08, `wv@1` 0.07, `wo@1`
  0.10; on extend: `w2@1` 0.13, `w1@1` 0.10, `out_bias` 0.08, the
  rest 0.01 to 0.03. On the full span the largest dictionary leads
  (`w1@1` 0.95 and 1.00), as the handoff warns.
- Pairs on the extend residual: `wv@1|wo@1` containment 1.00/1.00,
  winning atoms aligned 1.000, matched-`p` `mu` 0.62/0.72/0.93 and
  `d` 0.79/0.93/1.00 at `p` 1/3/12; `wv@0|w2@1` containment
  0.79/0.54; `wv@0|wo@0` 1.00/1.00; `w1@1|w2@1` 0.58/0.94.
- Joint fits (held-out `D`): reuse, `wv@0` 0.012, `wo@0` 0.016,
  fallback 0.024, the rest 0.23 or worse; extend, `w2@1` 0.023,
  fallback 0.050, `w1@1` 0.165, the rest 0.235 or worse; noise,
  every fit 0.468 or worse against the current 0.465.
- Extend at 0.01, 0.03, 0.1 and 0.3 of the scale, fitted: `D`
  0.002, 0.007, 0.024, 0.070.
- The two-head pilot: `wv@1|wo@1` containment 0.74/0.74; dense
  candidate fits train 0.058 against held-out 0.199.

## Bars (frozen)

`poc/ecsdec/score.py`, committed with this document.

- **E1, actions.** The full rule returns the truth on at least 7 of
  the 8 cases, with both EXPAND cases naming the planted module (for
  reuse, `wv@0` or `wo@0`).
- **E2, equivalence.** Pair 1 collapses and pair 2 stays distinct
  under the frozen rule.
- **E3, the layers earn their place.** Ablations A, B and C each
  miss at least one case the full rule gets right; E runs at least
  one redundant fit (a fit of a syntax equivalent, under the frozen
  rule, to one already fitted in that case) where the full rule runs
  none.
- **E4, reported.** The misspecification sweep scored against its
  bar-defined truth; the noise sweep's actions; D's agreement with
  the full rule; every candidate `eta`, the pairs' geometry under
  both equivalence rules, the fallback's held-out distortion, and
  the number of fits per case.

## Predictions

- **E1 holds, 8 of 8.** refine_early and refine_mid: REFINE
  (`s` about 0.2, `kappa` about 1e4). saddle: first stage GLOBALIZE,
  the budget improves `F` by over 90 percent, GLOBALIZE. reuse:
  first stage GLOBALIZE, the budget under 10 percent, `wo@0`
  collapses into `wv@0` and `wo@1` into `wv@1`, beam `wv@0`,
  `out_bias`, `w2@1` in some order with `wv@0` first, `J` about
  0.015 against the fallback's 0.043 and the current's 0.30:
  EXPAND on `wv@0`. collinear: `s` about 0.2, `kappa` about 1e8:
  REPARAMETERIZE. extend: beam `w2@1`, `w1@1`, `out_bias`, `J` about
  0.03 against the fallback's 0.07: EXPAND on `w2@1`. noise: first
  stage GLOBALIZE, the budget under 10 percent, no fit improves
  held-out: FALLBACK naming the current. adequate: STOP. The named
  risk: the `eta` margins at `p = 12` are a hundredth wide, so on
  the scored world the planted module may miss the beam; E1 allows
  that one miss.
- **E2 holds.** Pair 1 containment about 1.00 both ways, pair 2
  under 0.8. The matched-`p` rule says KEEP DISTINCT on pair 1
  (`d` at `p = 1` about 0.8): the handoff's principal-subspace
  equivalence reads the parameterisation, not the span, and would
  fail its own Case 8 here.
- **E3 holds.** A misses refine_early, refine_mid, saddle and
  collinear (every inadequate case goes to expansion); B misses
  saddle (stationary, so exhausted, so expansion) and collinear
  (REFINE); C misses collinear (REFINE); E runs one redundant fit on
  reuse (`wo@0` beside `wv@0`) and none elsewhere; D agrees with the
  full rule on every case (`tau` at most 0.06 on the exhausted
  students, so the quotient removes almost nothing). Letter **A**.
- **E4.** Misspecification: STOP at 0.01, 0.03 and 0.1, EXPAND on
  `w2@1` at 0.3 and 1, 5 of 5. Noise: at 0.01 every action holds;
  at 0.05 and 0.1 the adequate case turns inadequate (`D` about the
  noise level) and ends FALLBACK naming the current, refine_early
  stays REFINE, reuse and extend stay EXPAND on the planted module
  with the held-out gain shrinking.

## Outcome (frozen, exclusive)

- **A**: E1, E2 and E3 hold.
- **B**: E1 holds; E2 or E3 fails.
- **C**: E1 fails by one case (6 of 8) and E2 holds.
- **D**: otherwise.

E4 is reported under every letter. No rescue, no second run on the
scored world, no change to the model, the language, the cases, the
rule, the thresholds or the budgets after this commit. Results go in
`docs/math-track-ed1-results.md`; nothing above is edited after the
run.
