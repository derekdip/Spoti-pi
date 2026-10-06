# ECS-Decision v1: frozen implementation handoff (preserved 2026-10-06)

> **Status.** The handoff as pasted from the math-side chat on 2026-10-06, preserved verbatim below
> with display-math fences added for rendering. An editorial freeze sheet follows it.

### Purpose

Implement and evaluate the first frozen version of ECS-Decision, whose goal is not merely to reconstruct data well but to diagnose why the current representation is failing and choose the correct next action.

The central research question is:

$$
\boxed{ \textbf{Can residual geometry distinguish "fit the current model better" from "change the representation language"?} }
$$

The implementation must be frozen before any benchmark results are inspected.

Do not change thresholds, candidate rules, grammar structure, or scoring after seeing the synthetic-suite outcomes. Any later revision becomes ECS-Decision v2 and must be evaluated separately.

---

### 1. Inputs

For an observation

$$
x\in\mathbb R^N,
$$

current executable model

$$
G(\theta),
$$

current fitted parameters

$$
\hat\theta,
$$

candidate extension families

$$
\{H_j\},
$$

generic fallback family

$$
\mathcal F,
$$

and a deployment objective.

The current residual is

$$
\boxed{ r=x-G(\hat\theta). }
$$

Define reconstruction objective

$$
\boxed{ F(\theta) = \frac12\|x-G(\theta)\|^2. }
$$

---

### 2. Current-model geometry

Compute the Jacobian

$$
\boxed{ J=DG(\hat\theta). }
$$

Compute the gradient

$$
\boxed{ \nabla F(\hat\theta) = -J^\top r. }
$$

Compute the objective Hessian

$$
\boxed{ H_F = \nabla^2F(\hat\theta). }
$$

For nonlinear least squares,

$$
H_F = J^\top J - \sum_{a=1}^N r_a \nabla^2G_a.
$$

If analytic Hessians are unavailable, use a numerically stable automatic-differentiation or finite-difference approximation.

Compute singular values of J:

$$
\sigma_{\max}(J), \qquad \sigma_{\min}(J).
$$

Define

$$
\boxed{ \gamma = \sigma_{\min}(J), }
$$

and

$$
\boxed{ \kappa = \frac{ \sigma_{\max}(J) }{ \sigma_{\min}(J) }. }
$$

When rank-deficient, use the numerical rank and pseudoinverse consistently.

---

### 3. Tangent residual

Let

$$
\boxed{ P_T = JJ^\dagger }
$$

be the orthogonal projector onto the current executable tangent space.

Decompose

$$
\boxed{ r = r_\parallel + r_\perp, }
$$

where

$$
r_\parallel=P_Tr
$$

and

$$
r_\perp=(I-P_T)r.
$$

Define the tangent opportunity ratio

$$
\boxed{ \tau = \frac{ \|r_\parallel\|^2 }{ \|r\|^2 }. }
$$

Interpretation: $\tau$ is the fraction of current squared residual energy accessible to first-order parameter changes inside the current model family. It is an explanatory/effect-size statistic, not by itself the formal stopping condition.

---

### 4. Normalized stationarity score

Compute

$$
\boxed{ s = \frac{ \|J^\top r\| }{ \|J\|_2\|r\|+\epsilon }. }
$$

Use this as the numerical first-order stationarity test.

The threshold $\epsilon_g$ must be frozen before running the suite. Avoid arbitrary large thresholds. It should reflect optimizer/numerical precision.

---

### 5. Adequacy criterion

Define application distortion D(r). For the synthetic suite, use a frozen normalized reconstruction criterion, for example

$$
D_{\mathrm{norm}} = \frac{ \|r\| }{ \|x\|+\epsilon }.
$$

Freeze an adequacy threshold $D_{\max}$.

If

$$
\boxed{ D(r)\le D_{\max}, }
$$

the correct action is

$$
\boxed{\text{STOP}.}
$$

No grammar growth should occur for already adequate models.

---

### 6. ECS-Decision first-stage action rule

Use the following action hierarchy.

STOP

$$
If D(r)\le D_{\max}, return
$$

$$
\boxed{\text{STOP}.}
$$

REFINE

If $D(r)>D_{\max}$ and $s>\epsilon_g$, the current fit is not first-order stationary. If conditioning is acceptable, $\gamma\ge\gamma_{\min}$, return

$$
\boxed{\text{REFINE}.}
$$

Record $\tau$ as the predicted first-order opportunity.

REPARAMETERIZE / REGULARIZE

$$
If s>\epsilon_g but \gamma<\gamma_{\min} or \kappa>\kappa_{\max}, return
$$

$$
\boxed{\text{REPARAMETERIZE}.}
$$

This means useful descent may exist but the current coordinates are unstable or non-identifiable. Do not immediately expand the grammar.

GLOBALIZE

If $s\le\epsilon_g$ but $\lambda_{\min}(H_F)<-\epsilon_H$, the fit is first-order stationary but not a local minimum. Return

$$
\boxed{\text{GLOBALIZE}.}
$$

Interpretation: the current model family still contains a descent direction, but first-order refinement alone may fail to reveal it. Possible implementation action: escape saddle; trust-region expansion; multistart optimization; coarse parameter search. Do not expand the grammar yet.

LOCALLY EXHAUSTED

If $s\le\epsilon_g$, $\lambda_{\min}(H_F)\ge-\epsilon_H$, and $D(r)>D_{\max}$, mark the current model

$$
\boxed{\text{LOCALLY EXHAUSTED}.}
$$

This means no obvious first- or second-order local optimization opportunity remains. It does not imply global exhaustion of the family.

---

### 7. Bounded globalization

Before grammar expansion, use a fixed bounded globalization budget. Examples: fixed number of multistarts; fixed coarse-grid search budget; fixed trust-region restarts. The budget must be frozen.

If globalization discovers a substantially better fit within the same family, classify the case as

$$
\boxed{\text{GLOBALIZE}.}
$$

If bounded globalization fails and distortion remains inadequate, continue to grammar expansion.

This preserves the distinction

$$
\boxed{ \text{local exhaustion} \neq \text{global family exhaustion}. }
$$

---

### 8. Candidate grammar extensions

Each candidate extension family $H_j$ introduces additional parameters $\alpha_j$. Require a neutral state

$$
H_j(0)=0.
$$

At the neutral state compute its infinitesimal extension block

$$
\boxed{ K_j = \left. D_{\alpha_j}H_j \right|_{\alpha_j=0}. }
$$

Remove directions already represented by the current model:

$$
\boxed{ K_j^\perp = (I-P_T)K_j. }
$$

Define its genuinely novel first-order extension subspace

$$
\boxed{ U_j = \operatorname{range}(K_j^\perp). }
$$

---

### 9. First-order extension value

Compute

$$
\boxed{ \eta_j = \frac{ \|P_{U_j}r_\perp\|^2 }{ \|r_\perp\|^2+\epsilon }. }
$$

Interpretation: $\eta_j$ is the maximal fraction of the current normal residual energy that candidate family j can remove in the linearized augmented model. This score is only a proposal score. It does not prove that nonlinear fitting will achieve the same improvement.

---

### 10. Matched-complexity comparison

Do not compare raw full candidate dictionaries if they have different effective rank.

For each candidate family, compute principal novel subspaces at frozen effective dimensions

$$
\boxed{ p\in\{1,3,12\} }
$$

or another preregistered fixed set if dimensionality makes these impossible. Use identical p across families. This avoids automatically rewarding richer candidate dictionaries.

---

### 11. Candidate-extension geometry

For family i, let $Q_i^{(p)}$ be an orthonormal basis of the top-p principal novel subspace.

Compute mutual coherence

$$
\boxed{ \mu_{ij}^{(p)} = \| Q_i^{(p)\top} Q_j^{(p)} \|_2. }
$$

For equal-dimensional spaces compute projector distance

$$
\boxed{ d_{ij}^{(p)} = \| P_i^{(p)}-P_j^{(p)} \|_2. }
$$

For potentially unequal effective spaces compute directed containment

$$
\boxed{ c_{i\to j} = \frac{ \|P_jQ_i\|_F^2 }{ \dim U_i }. }
$$

Where useful, also compute alignment of the actual winning atoms.

---

### 12. Local extension equivalence

Two candidate syntaxes should be treated as locally redundant when their novel principal subspaces are equivalent under frozen geometric tolerances. Conceptually:

$$
\boxed{ U_i\approx U_j \Rightarrow \text{COLLAPSE}. }
$$

The exact thresholds for $d_{ij}^{(p)}$ and $\mu_{ij}^{(p)}$ must be frozen before evaluation.

If candidates are geometrically equivalent, choose the cheaper syntax according to grammar/deployment cost rather than fitting both.

If they have similar extension scores but geometrically distinct dominant directions, return

$$
\boxed{\text{KEEP BOTH}.}
$$

They remain in the expansion beam.

---

### 13. Expansion beam

After equivalence clustering:

1. rank extension classes by $\eta_j$ or a complexity-adjusted variant;
2. retain a frozen top-k or confidence beam;
3. fully fit only surviving representatives;
4. compare final deployment objective against the current model and fallback.

Do not permit a candidate to enter the permanent grammar solely because $\eta_j$ is high.

---

### 14. Deployment objective

Use a frozen deployment score for full candidate comparison:

$$
\boxed{ J = D + \lambda_s B_s + \lambda_m B_m + \lambda_e C_e + \lambda_d C_d. }
$$

Where D is normalized reconstruction distortion; $B_s$ per-state bytes; $B_m$ shared model bytes; $C_e$ encoding/search cost; $C_d$ decode/runtime cost.

If runtime measurement is inconvenient for the synthetic suite, use frozen surrogate costs, but record them explicitly. Preserve all raw metrics separately.

---

### 15. EXPAND decision

Grammar expansion is correct only if:

1. current representation is inadequate;
2. local refinement is exhausted;
3. bounded globalization failed;
4. at least one candidate extension produces a better frozen deployment objective after full fitting.

Then return

$$
\boxed{\text{EXPAND}.}
$$

Also record the selected extension class and syntax.

---

### 16. FALLBACK decision

If current model is inadequate and no candidate structured extension beats the generic fallback economically, return

$$
\boxed{\text{FALLBACK}.}
$$

Fallback is a valid outcome. Do not force executable structure.

---

### 17. Frozen action set

The first-stage classifier returns one of:

$$
\boxed{ \{ \text{STOP}, \text{REFINE}, \text{REPARAMETERIZE}, \text{GLOBALIZE}, \text{EXPAND}, \text{FALLBACK} \}. }
$$

The candidate-equivalence stage additionally emits:

$$
\boxed{ \{ \text{COLLAPSE}, \text{KEEP DISTINCT} \}. }
$$

---

### 18. Synthetic decision suite

The suite should test diagnosis, not merely reconstruction. Every case has a known intended action before execution.

Case 1, correct family, wrong center. Truth $x=G(c^*$); initial fit uses incorrect c. Expected: REFINE.

Case 2, correct family, wrong amplitude/width. Truth is in the current family; initial parameters are inaccurate. Expected: REFINE.

Case 3, stationary saddle/local maximum. Use $G(\theta)=(\cos\theta,\sin\theta$), current $\theta=0$, target x=(-1,0). Then $\nabla$ F=0 but $\lambda_{\min}(H_F)<0$. Expected: GLOBALIZE. This case explicitly defeats a gradient/tangent-only policy.

Case 4, true local minimum, wrong family. Use $G(\theta)=(\theta,0$), target x=(0,1). Expected: LOCALLY EXHAUSTED then EXPAND.

Case 5, poor conditioning. Use two nearly collinear parameter effects or two heavily overlapping Gaussian mechanisms. Expected: REPARAMETERIZE. Do not expand.

Case 6, missing additional instance of existing primitive. Truth $x=g_1+g_2$; current model contains one Gaussian. Expected: EXPAND via REUSE with an additional Gaussian instance.

Case 7, missing genuinely new primitive. Truth contains a translated step or triangle; current grammar contains only Gaussian-like mechanisms. Expected: EXPAND via EXTEND.

Case 8, equivalent candidate syntaxes. Construct two candidate extension families with $U_1=U_2$ or very small projector distance. Expected: COLLAPSE. Only one syntax should proceed to full fitting.

Case 9, distinct candidate directions with similar scores. Construct $\eta_1\approx\eta_2$ but with large principal-angle separation. Expected: KEEP DISTINCT. Both remain in the beam.

Case 10, noise-like residual. No structured extension has stable held-out advantage. Expected: FALLBACK.

Case 11, already adequate model. Residual is nonzero but below deployment tolerance. Expected: STOP. No expansion.

Case 12, better minimum exists elsewhere in same family. Create a multimodal objective where the fitted point is a genuine local minimum but a much better minimum exists elsewhere within the same family. Expected: GLOBALIZE. The fixed globalization budget should discover the better same-family solution before grammar expansion. This is the hardest and most important test of local exhaustion not equal to family exhaustion.

---

### 19. Noise sweeps

Run each synthetic case under multiple frozen noise levels, for example

$$
\boxed{ \sigma \in \{0,\sigma_1,\sigma_2,\sigma_3\}. }
$$

Do not retune thresholds between noise levels. Measure when decisions degrade. This tests robustness of stationarity, conditioning, candidate equivalence and fallback.

---

### 20. Misspecification sweeps

For missing-structure cases, sweep the strength of the missing mechanism. Example:

$$
x = g_1 + A_2g_2
$$

with increasing $A_2$. At sufficiently tiny $A_2$, the correct deployment-aware decision may be STOP rather than EXPAND. At larger $A_2$, EXPAND should become worthwhile. This tests whether ECS reacts to economically meaningful structure, not merely detectable structure.

---

### 21. Ablations

Run the exact same suite with the following decision systems.

Ablation A, residual magnitude only. Rule: $D>D_{\max}$ implies EXPAND. Purpose: measure unnecessary grammar growth.

Ablation B, gradient only. Use first-order stationarity but no Hessian/globalization distinction. Purpose: test necessity of second-order/local-minimum handling.

Ablation C, gradient + Hessian only. Use optimization geometry but no tangent quotient or extension equivalence. Purpose: measure value of ECS extension geometry.

Ablation D, raw candidate correlation. Score candidate additions against raw residual r instead of normal residual $r_\perp$. Purpose: test whether quotienting out current-model directions prevents false expansion.

Ablation E, no equivalence clustering. Fit every high-scoring syntax independently. Purpose: measure redundant search/model growth.

Full ECS-Decision uses: adequacy; gradient; Hessian; conditioning; bounded globalization; tangent quotient; normal candidate scoring; matched-complexity geometry; extension equivalence; deployment-aware final selection; fallback.

---

### 22. Primary metrics

The primary benchmark target is decision quality, not raw RMSE.

Record action accuracy over {STOP, REFINE, REPARAMETERIZE, GLOBALIZE, EXPAND, FALLBACK}.

Also report: wrong grammar expansions; missed refinements; missed globalization cases; fallback precision/recall; candidate fits executed; redundant syntax fits avoided; final deployment score; final reconstruction distortion; search/optimization cost.

For equivalence cases separately report COLLAPSE versus KEEP-DISTINCT accuracy.

---

### 23. Required benchmark tables

Save at minimum: $decision_summary.csv$, $decision_confusion_matrix.csv$, $equivalence_summary.csv$, $ablation_summary.csv$, $per_case_metrics.csv$, $noise_sweep.csv$, $misspecification_sweep.csv$, config.json.

Also preserve per-case diagnostics: $residual_norm$, $normalized_distortion$, $gradient_norm$, $stationarity_score$, tau, $sigma_min$, $condition_number$, $hessian_min_eigenvalue$, $globalization_improvement$, $candidate_eta$, $candidate_projector_distances$, $candidate_coherences$, $candidate_containments$, $final_action$, $ground_truth_action$.

---

### 24. Visualization outputs

Produce at least: a decision confusion matrix for full ECS and each ablation; a wrong-expansion rate bar/table comparing methods; action accuracy against noise; action transitions against missing-mechanism amplitude (STOP to EXPAND); candidate geometry for equivalence/distinct cases; search cost against decision quality.

---

### 25. Frozen-policy transfer experiment

Only after the synthetic suite and ablation are complete:

1. freeze ECS-Decision thresholds;
2. freeze candidate library;
3. freeze equivalence thresholds;
4. freeze globalization budget;
5. freeze deployment weights;
6. select new physical datasets by name only;
7. do not inspect their waveforms/residuals manually;
8. run ECS-Decision automatically.

The transfer question is:

$$
\boxed{ \textbf{Does a frozen representation-repair policy transfer to unseen real data?} }
$$

This is stronger than the previous v3 experiment, which only tested transfer of a frozen representation.

---

### 26. Rules for the real-data policy test

No manual residual interpretation. No grammar additions. No threshold changes. No dataset-specific candidate selection.

If ECS returns REFINE, perform only frozen refinement. If GLOBALIZE, use only the frozen globalization budget. If EXPAND, the candidate beam must be generated entirely by the frozen candidate library and geometry. If FALLBACK, accept fallback.

The algorithm must be allowed to fail.

---

### 27. Success criteria

The central question is not whether full ECS wins every case. The architecture earns its complexity if it does materially better than simpler baselines in at least the following ways:

1. fewer unnecessary expansions;
2. more correct REFINE decisions;
3. correct handling of stationary saddle/globalization cases;
4. reduced redundant candidate fitting through extension equivalence;
5. similar or better final deployment quality;
6. reasonable robustness under noise;
7. nontrivial transfer of the frozen policy to unseen physical data.

If gradient + Hessian alone performs essentially as well as full ECS, simplify the paper. If equivalence clustering does not reduce meaningful computation or grammar proliferation, remove or demote that layer. If normal-space scoring does not outperform raw residual correlation, do not claim it as a meaningful contribution.

Negative outcomes are useful.

---

### 28. Frozen conceptual claims

The benchmark is testing the following specific hypotheses.

H1, parameter under-optimization: a model with accessible same-family improvement should be diagnosed as REFINE rather than EXPAND.

H2, local non-minimum: a first-order stationary point with negative Hessian curvature should be diagnosed as GLOBALIZE.

H3, local model exhaustion: only approximately stationary, locally minimal, inadequate models should proceed toward grammar expansion.

H4, tangent quotient: projecting candidate extensions into the normal complement should reduce false/redundant expansion caused by directions already available to the current model.

H5, conditional extension equivalence: different candidate syntaxes that add effectively the same novel local subspace should be collapsible before full fitting.

H6, distinct tied candidates: candidates with similar extension scores but distinct novel geometry should remain jointly represented in the beam.

H7, deployment awareness: detectable structure should only be promoted when it improves the frozen deployment objective.

H8, fallback legitimacy: noise-like or poorly structured cases should be allowed to choose generic fallback.

---

### 29. Current theoretical interpretation

The frozen architecture has three layers.

Optimization geometry answers: is the current executable model actually locally exhausted? Uses $\nabla$ F, $\nabla^2F$, $\gamma$, $\tau$.

Extension geometry answers: what genuinely new local directions would a grammar extension provide? Uses $K_j^\perp$, $U_j$, $\eta_j$, principal angles/projector distances.

Deployment / grammar economics answers: which syntax, if any, should actually be promoted? Uses D, $B_s$, $B_m$, $C_e$, $C_d$, plus reuse/grammar cost.

The core principle is:

$$
\boxed{ \textbf{optimization before expansion, direction before syntax, syntax before promotion.} }
$$

---

### 30. Interpretation if the benchmark succeeds

If full ECS materially outperforms the simpler ablations, the paper's central contribution becomes: a geometry-conditioned decision framework for diagnosing representation failure before adapting an executable representation language.

The important result would no longer be merely that executable coordinates can outperform PCA. It would be that a frozen system can distinguish "fit better" from "search elsewhere in the same family" from "change the representation language" from "use generic fallback".

That is the specific claim this implementation should now test.


---

# Editorial: what the implementation chat must freeze before the first run

Written 2026-10-06, to be read with the handoff above. The handoff
leaves every threshold and budget "to be frozen"; the implementation
must set them, record them in `config.json`, and commit that
configuration before any suite result is inspected, as this
repository's rounds do (`docs/math-track-g13-prereg.md` is the
pattern: V0, checks, a declared pilot, bars, predictions, then a
freeze commit, then one run). The values below are **proposals**, not
the freeze; the implementation chat may change any of them, but only
before the freeze commit, and must say why.

| quantity | handoff section | proposed value | reason |
|---|---|---|---|
| stationarity threshold `eps_g` | 4 | 1e-6 | the score `s` is scale-free; this is optimiser precision for double arithmetic with finite-difference Jacobians at step `1e-6` |
| adequacy `D_max` | 5 | 0.05 of `||x||` on the synthetic suite | one twentieth is below any synthetic case's designed defect and above numerical noise |
| conditioning `gamma_min`, `kappa_max` | 2, 6 | `gamma_min = 1e-8 * sigma_max(J)`, `kappa_max = 1e6` | tie the numerical rank used in `P_T = J J^+` to the same `gamma_min`, so REPARAMETERIZE and the projector agree |
| curvature `eps_H` | 6 | `1e-8 * ||H_F||_2` | relative, so Case 3 (`lambda_min = -1`) and a flat direction (0) are told apart at any scale |
| principal dimensions `p` | 10 | {1, 3, 12}, dropping any that exceed a family's rank with the drop recorded | the handoff's set |
| equivalence tolerances | 12 | COLLAPSE if `d_ij <= 0.2` and `mu_ij >= 0.95` at every `p`; KEEP DISTINCT otherwise | consistent with the ECG200 pair the snapshot reports (0.097, 0.995) and the ECGFiveDays pair it calls distinct; to be frozen, not tuned |
| beam `k` | 13 | 3 | enough for Case 9 to keep both and Case 8 to collapse to one |
| globalization budget | 7 | 8 multistarts from a Latin hypercube over the parameter box, plus a 16-per-axis grid on at most 3 axes; "substantially better" means the objective falls by 10 percent of `F(theta^)` | fixed, cheap, and enough for Case 12 by construction |
| deployment weights | 14 | `lambda_s = 1e-3` per state byte, `lambda_m = 1e-5` per shared byte, `lambda_e = 1e-6` and `lambda_d = 1e-5` per surrogate op | 16 floats of state cost 0.064, comparable to the distortion differences the suite produces; shared bytes amortised a hundredfold |
| noise levels | 19 | `sigma in {0, 0.01, 0.05, 0.1}` of `||x||` | spans numerical noise to a tenth of the signal |
| misspecification sweep | 20 | `A_2 in {0.01, 0.03, 0.1, 0.3, 1}` of `||g_1||` | crosses `D_max` so STOP turns into EXPAND inside the sweep |
| spent repair | 13, 15 | a fitted extension that lowers the deployment objective by under one percent is blacklisted | this repository's spent rule, carried since RGRE-1 |

Three consistency checks done on the handoff's own cases before
passing it on: Case 3 has `F(theta) = 1 + cos(theta)`, so `F'(0) = 0`
and `F''(0) = -1`, a maximum, and GLOBALIZE is the right label; Case 4
has `F = (theta^2 + 1)/2`, residual `(0, 1)` orthogonal to the tangent
`(1, 0)`, `tau = 0`, `s = 0`, curvature 1, distortion 1, so LOCALLY
EXHAUSTED then EXPAND follows from the rule as written; the score `s`
in section 4 is invariant to rescaling `x` and `G`, which the
thresholds above rely on.

What this repository already implements, for reuse rather than
rewriting: `poc/rgre/core.py` has the tangents (finite differences,
secants from a declared on-state), the projection diagnosis, the
unexplained fraction and the abstention threshold 0.5834, the
per-class fit from an on-state, and the one-percent blacklist. It has
no Hessian, no stationarity or conditioning test, no globalization
budget and no equivalence clustering; those are ECS-Decision v1's
additions. The exclusivity table (`poc/gait3d/dictionary_check3d.py`)
is the nonlinear form of the equivalence stage and the right
cross-check for Cases 8 and 9. The frozen-round pattern, the stop
hook that insists on committing, and the habit of naming defects
after the freeze (`docs/math-track-g14-results.md`, first paragraph)
are the methodology to keep.
