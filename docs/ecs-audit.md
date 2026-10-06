# Audit of the ECS theory snapshot: what is elementary, what is known, what survives

First audit pass, 2026-10-06, of `docs/ecs-theory-snapshot.md` (the
frozen snapshot). Each section of the snapshot's mathematics was read
for correctness, checked numerically where a construction exists
(`poc/ecs_audit.py`, results in `poc/results/ecs_audit.md`), placed
in the literature, and classified. Six references were confirmed
against their sources today; the rest are marked as still to verify.
The verdict is at the end, with the paper structure that follows from
it.

Classes used: **elementary** (a textbook fact restated), **known**
(stated in the literature under another name), **formulation** (a
definition or framing, not a theorem), **protocol** (a procedural
claim, testable but not mathematics), **empirical** (a measured claim;
its record is either here or not), **open**.

## Section by section

### 2. Executable against linear dimension
Definition. `e_n^lin` of a finite family is its Kolmogorov n-width.
The "separation" is a statement about two different kinds of
coordinate (nonlinear parameters against a linear basis), and the
paper has to say so where it counts coordinates. **Formulation.**

### 3. Orthogonal separation
Correct. Proof: for orthonormal `x_i`, `sum_i ||P x_i||^2 = tr(P X X^T) <= tr(P) = n`.
Numerically (M = 50): the mean error squared equals `1 - n/M`
exactly for any basis and the worst case sits above it (1.000 at n =
25 against the bound 0.500). The average-case version is the one that
is tight. **Elementary.**

### 4. Low-coherence extension
Correct as an inequality (Gershgorin on the Gram matrix gives
`lambda_max <= 1 + (M-1) mu`, and `sum_i ||P x_i||^2 <= n lambda_max`).
Overstated as a result: the bound is informative only when
`(M-1) mu = O(1)`, that is when the coherence decays like `1/M`. At
M = 50 and `mu = 0.13` the bound is negative (vacuous) while the true
rank-10 worst error squared is 0.91. "Robustness of the separation
under approximate orthogonality" therefore holds only for coherence
that shrinks with the family's size, which a family of overlapping
translates does not have; section 9 is the version that works for
them. **Elementary**, with the caveat to be written in.

### 5. Localized transformation families
Correct for disjoint supports (then `mu = 0` and section 3 applies
with `M = (L/w)^d`); for overlapping placements it needs section 9.
This is the Kolmogorov barrier for transport-dominated problems:
reduced-basis methods fail on translated structures because the
n-width decays slowly, which is the whole reason the shifted and
registered methods below exist. **Known** (Ohlberger and Rave 2016,
confirmed; Greif and Urban 2019, confirmed, for the rate; Donoho and
Grimes 2005, confirmed, for the non-differentiability of the
translated-bump manifold).

### 6. Hybrid representation
The count `k + q` against `M + q` is correct as stated for orthogonal
executable states and an orthogonal residual, and compares a
nonlinear parameterisation's dimension with a linear subspace's; the
paper must say "degrees of freedom of the description" and not
"dimension". The construction itself, a transformed template plus a
residual expanded in a basis, is symmetry-reduced Karhunen-Loeve:
`x = g(theta) (x_bar + U z)` with `g` the group action (Rowley and
Marsden 2000, confirmed), extended to several transports by the
shifted POD (Reiss, Schulze, Sesterhenn and Mehrmann 2018, confirmed)
and current in operator-inference form (symmetry-reduced model
reduction of shift-equivariant systems, arXiv 2507.18780, 2025, seen
in search, to verify). ECS's generalisation is that `G` need not be a
group action; none of the snapshot's theorems uses more than the
group case. **Known**, framing generalised.

### 7. Moving residual frames
`U(theta) z` is the residual expressed in the moving frame, which is
exactly what the symmetry-reduced expansion does. Correct, **known**
(Rowley and Marsden 2000).

### 8. Block-coherence theorem
Correct: block Gershgorin (Feingold and Varga 1962, confirmed) on the
block Gram matrix gives `lambda_max <= 1 + (M-1) mu_B`, and the rest
is section 3's argument on frames. Block coherence as a notion is
from block-sparse recovery (Eldar, Kuppinger and Bolcskei 2010, to
verify). Numerically the bound holds and is loose (random frames:
`lambda_max` 1.84 against 6.29). **Elementary.**

### 9. Local-overlap improvement
Correct, and this is the useful statement: with the row sum
`rho_B` in place of `(M-1) mu_B` the bound is `1 + rho_B`, so bounded
overlap gives `n = Omega(M)`. Numerically, thirty translated
three-dimensional local frames with two overlapping neighbours each
have `rho_B = 1.12` against `(M-1) mu_B = 20`, and the bound says 38
of 90 directions are needed for a block error of 0.1 where the
worst-case form says nothing. It is the Riesz-sequence bound of frame
theory (a family with summable overlaps is a Riesz sequence with
bounds `1 +- rho_B`; Christensen's frame book, to verify the
statement's form), applied to approximation. **Elementary**; the
discrete form of the Kolmogorov barrier for local families, worth one
lemma in the paper.

### 10. Continuous orbit formulation
Definitions. The executable width is the nonlinear width with the
decoder restricted to a grammar: DeVore, Howard and Micchelli 1989
define nonlinear widths; manifold and library widths are surveyed in
Cohen and DeVore 2015 (both to verify). No theorem is proved. **Formulation.**

### 11. Random translation and Fourier PCA
Correct: the covariance of a uniformly translated template on the
torus is a convolution operator, its eigenfunctions are the Fourier
modes and its eigenvalues `|f^(n)|^2`. Numerically exact to 1e-15 on
a 1024-point torus. Classical (Karhunen-Loeve of a stationary
process; stated for translating structures in Rowley and Marsden
2000). **Known.** One omission: with the mean subtracted the `n = 0`
mode drops; the snapshot does not say whether PCA is centred.

### 12. Translated Gaussian theorem
Correct, with the constant: for an RMS tolerance `eps` the rank is
about `0.41 sigma^-1 sqrt(log 1/eps)` counting both signs of the
frequency (measured 0.410, 0.429, 0.410, 0.410 at `sigma` = 0.08 to
0.01), and the `sqrt(log 1/eps)` dependence shows as ranks in the
ratio 1 : 1.4 : 1.7 for `eps` = 0.1, 0.01, 0.001. The d-dimensional
statement follows by the product. It is a one-line consequence of
section 11 with a Gaussian spectrum. **Elementary consequence**; at
most a lemma, not a theorem.

### 13. Template regularity
Correct: a translated step has `lambda_n ~ 1/n^2`, the tail `~ 1/m`,
and `m eps^2` is constant numerically (0.45, 0.41, 0.28 for `eps` =
0.3, 0.1, 0.03). This is Greif and Urban 2019's `N^-1/2` rate for a
discontinuous transported profile, seen as a mode count. **Known.**

### 14. Representation against coding
A heuristic table. The point, that a parametric generator compresses
the dictionary itself, is the standard argument for analytic
dictionaries over learned ones. **Formulation**, keep as discussion.

### 15. Executable rate scaling
Correct: quantising a bounded k-parameter domain of a K-Lipschitz
family at step `eps/K` costs `k log(K diam / eps)` bits; for the
translated Gaussian of width 0.02 the Lipschitz constant is 35 per
unit shift and the cost grows by 3.3 bits per decade of `eps`, as
`k = 1` says. The snapshot's own disclaimer (not a rate-distortion
superiority result) is right. **Elementary** (covering numbers).

### 16 and 17. Deployment frontier and ECS-Search
A penalised objective over distortion, state bytes, model bytes and
two costs, with a generic fallback that must be allowed to win. This
is a rate-distortion-complexity or MDL framing (Rissanen; Grunwald
2007, to verify for the citation form). The fallback rule is the one
part with teeth, and it is a protocol rule. **Formulation** and
**protocol.** This repository measured the frontier rather than
assuming it: the cost-error knee per consumer and the eightfold
disagreement between op counts and measured milliseconds
(`docs/math-track-b0-review.md`, `docs/bendbench-results.md`).

### 18. Tangent and normal residual
The residual's orthogonal split against the Jacobian's range is
Gauss-Newton geometry. "Refine before expanding if the residual is
tangential" is a sound first-order rule. **Elementary.** Its measured
limit is this repository's linearisation gap
(`docs/linearisation-gap.md`): where the fitted repair lies outside
the tangent span the first-order split under-reads the grammar's
reach, and on real data that was the common case.

### 19. Tangential certificate on ECG
**Empirical, not in this record.** The values 0.389, 0.510 and 0.004
and the statement that refinement consumed the tangent energy come
from a program whose code, data and frozen configuration are not in
this repository. Cannot be audited here.

### 20. Candidate extension scoring
Correct and exact for what it claims: `S(a)` equals the gain of the
linearised augmented fit `||P_[J,a] r||^2 - ||P_J r||^2` to 1e-15
numerically, because `a_perp` is orthogonal to the tangent space.
This is the orthogonal matching pursuit selection rule with the
current span projected out (Pati, Rezaiifar and Krishnaprasad 1993;
Mallat and Zhang 1993 for matching pursuit; to verify). **Known.**
The caveat is section 18's: the score is first order, and the
linearisation gap measures how far the nonlinear refit departs from
it.

### 21 and 22. Direction before syntax
Principal angles, projector distance and containment are the standard
subspace comparisons (Bjorck and Golub 1973, to verify). The rule
"collapse syntaxes that share a local direction before fitting
either" is a **protocol** contribution, and a good one; its ECG
instance (0.923, 0.995, 0.097) is **empirical, not in this record**.
Its nonlinear form is in this record: the exclusivity table
(absorption of one class's fitted effect by another), which predicted
the naming outcomes of G2 to G6 and G13.

### 23 and 24. The frozen real-data sequence and the falsified prediction
**Empirical, not in this record.** The sequence (v1 to v3, MoteStrain,
Earthquakes, SonyAIBORobotSurface1) and the falsified
derivative-of-Gaussian prediction need their artefacts attached
before a paper cites them. The practice they describe, frozen
predictions scored as returned, is this repository's practice in
every round, and the gait rounds G13 and G14 are two further
instances of a prediction falsified without the procedure being
touched.

### 25. Discovery protocol
**Protocol.** The loop is RGRE's loop (`poc/rgre/core.py`,
`docs/rgre-writeup.md` section 2) with two additions the implementation
handoff makes explicit: second-order and conditioning checks before
expansion, and equivalence collapse before fitting. Testable by
ECS-Decision v1.

### 26. Learning-theoretic interpretation
Standard uniform convergence over a finite class; the `log |G|`
dependence is the usual one and the proposal-then-verify separation
is the standard reason for held-out evaluation. **Elementary.**

### 27 and 28. Where it should work; networking
Predictions. The networking principle holds for bandwidth and state
(bank causes, not outcomes) and is bounded for latency: local
reconstruction of a cause's effect beats a streamed render only when
the round trip exceeds `e_local * tau_eff`, 76 to 118 ms for the
vegetation case, predicted within 10 ms with no fitted constant
(`docs/streaming-latency-check.md`). **Empirical, in this record**, and
the claim should be stated with that threshold.

### 29. Established against open
The "established mathematically" list is correct as a list of true
statements and should not be called results: items 1 to 6 are
elementary or known under the names above. The "established
empirically" list is half in this record and half not (see the
snapshot's reconciliation section). The "not established" list is
right and already concedes the point about novelty.

### 30. The inverse problem
**Open**, with a literature the paper must engage from the start:
learning Lie-group transformations from data (Rao and Ruderman 1999;
Sohl-Dickstein, Wang and Olshausen 2010; to verify), symmetry
discovery, registration-based model reduction (Taddei 2020, to
verify) and transported subspaces (Rim, Peherstorfer and Mandli, to
verify). The snapshot's route (PCA failure, then detecting transformed
repetition among modes, then inferring an orbit) is the symmetry-
reduction route in reverse and should be positioned as such.

## What survives as a contribution

1. **The protocol with its failure mode.** A frozen residual-guided
   growth procedure with a generic fallback, abstention on the
   unexplained fraction, and a spent rule, replicated in four
   simulation domains at a sixth to a tenth of the search, and shown
   to fail exactly where the repair is not first order in the
   parameters (the linearisation gap: full value under 0.1, half over
   0.25, invisible at 0.98). The failure mode is as much the result
   as the success.
2. **Direction before syntax, in two forms.** The first-order form
   (principal angles on novel subspaces) and the nonlinear form (the
   exclusivity table, with its algebraic twin check), the second with
   a predictive record across seven rounds.
3. **What names against what generalises.** Held-out acceptance
   generalised in eleven of eleven 3D rounds while naming held only
   where classes were exclusive and the base had none of the damage;
   on a real clip, naming followed the base's own asymmetry. This is
   the one result here that the literature above does not contain.
4. **The deployment side measured.** The knee per consumer, the
   op-count against milliseconds disagreement, the dropped-part and
   composition results, and the latency threshold.
5. **The real-data program**, once attached and audited to the same
   standard.

Not contributions, to be cited and passed over in a page: sections 2
to 15 (the executable advantage is the Kolmogorov barrier for
transport, seen from the decoder's side, plus the standard coherence
and covering bounds) and sections 18, 20 and 26 (Gauss-Newton,
orthogonal matching pursuit, uniform convergence).

## The paper that follows

1. Problem and framing, one page: causes against outcomes, with the
   transport barrier and symmetry-reduced POD as the prior art it
   generalises.
2. Background, two pages: the barrier (sections 3 to 13 compressed to
   three cited statements and the one lemma of section 9), the hybrid
   with a moving frame as symmetry reduction.
3. The procedure: ECS-Search and ECS-Discover as RGRE, with the
   deployment objective and the fallback.
4. Evidence: the table of frozen rounds, with the linearisation gap
   and the exclusivity table as the two instruments.
5. Failure modes, in full, as the rounds recorded them.
6. ECS-Decision v1, when it has run, as the test of whether the
   geometry layers earn their cost.
7. The inverse problem, positioned against transformation learning.

## Citations confirmed today

- Greif, C., Urban, K. (2019). Decay of the Kolmogorov N-width for
  wave problems. Applied Mathematics Letters 96, 216-222. arXiv
  1903.08488.
- Ohlberger, M., Rave, S. (2016). Reduced basis methods: success,
  limitations and future challenges. arXiv 1511.02021.
- Rowley, C. W., Marsden, J. E. (2000). Reconstruction equations and
  the Karhunen-Loeve expansion for systems with symmetry. Physica D.
- Reiss, J., Schulze, P., Sesterhenn, J., Mehrmann, V. (2018). The
  shifted proper orthogonal decomposition: a mode decomposition for
  multiple transport phenomena. SIAM J. Sci. Comput. 40(3),
  A1322-A1344.
- Donoho, D. L., Grimes, C. (2005). Image manifolds which are
  isometric to Euclidean space. J. Math. Imaging and Vision.
- Feingold, D. G., Varga, R. S. (1962). Block diagonally dominant
  matrices and generalizations of the Gerschgorin circle theorem.
  Pacific J. Math. 12(4).

Still to verify before citing: Welch 1974; Eldar, Kuppinger and
Bolcskei 2010; DeVore, Howard and Micchelli 1989; Cohen and DeVore
2015; Christensen (frames); Bjorck and Golub 1973; Mallat and Zhang
1993; Pati, Rezaiifar and Krishnaprasad 1993; Grunwald 2007; Rao and
Ruderman 1999; Sohl-Dickstein, Wang and Olshausen 2010; Taddei 2020;
Rim, Peherstorfer and Mandli; arXiv 2507.18780.
