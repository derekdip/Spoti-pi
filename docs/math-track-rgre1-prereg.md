# RGRE-1: residual-guided representation expansion. Preregistration (frozen before the benchmark seed is run)

Claim under test: can consumer residuals choose the next executable
representation repair more efficiently than class-free search? The
procedure is mechanistic (projection, localisation, coherence, cost);
no classifier is trained anywhere.

## Frozen algorithm

Given teacher `F`, representation `R`, consumer `G`: `r = G(F) -
G(F_R)`. Two kinds of class diagnostic, both computed from the
representation and the cause's kinematics alone, never from repair
evaluations:

- signed classes supply tangent fields of the representation
  (subspaces); ownership `q_j = ||P_j r||^2 / ||r||^2` with `P_j` the
  orthogonal projection onto the class subspace alone;
- template classes supply a nonnegative energy template over consumer
  points and are read after the joint least-squares fit on all signed
  subspaces is removed. Support-type templates (corner, stop) own the
  energy on their support when the residual is concentrated there,
  enrichment `share / support fraction >= 2` (B5's constant), and that
  energy is then set aside; otherwise they own nothing. Shape-type
  templates (smooth, interaction) are fitted to the remaining per-point
  energy by nonnegative least squares (each normalised to unit total);
  `q_j` is the energy assigned to template `j` over `||r||^2`.

`q_perp` is the residual energy left by all three stages (for shape
templates: the part of the per-point energy above the fitted
templates). The development run showed why the support rule is needed:
a least-squares fit of a broad template to a residual concentrated at a
few apex stalks under-assigned it and left 50 to 83 percent of known
corner cases unexplained. Coherence
`mu_j` is the largest, over other classes, of the largest canonical
correlation between signed subspaces, or the cosine between energy
profiles when either class is a template. Score `S_j = q_j (1 - mu_j)`.

Selection: if `q_perp > tau_perp` abstain ("unknown"); else take the
largest `S_j`; if that class is unrepairable (water's floor) abstain
("atom"); else evaluate only that class's repair set and pick the best
`dE / C` within it. `tau_perp = min(0.9, max q_perp over the calibration
cases + 0.1)`, the calibration cases being B5's five fresh paths under
the base corn representation and W4's nonlinear singles at A = 4, 6, 8
under the base water token (all seen, all known-class).

## Vocabulary (frozen)

| class | diagnostic | domain | repairs (cost) |
|---|---|---|---|
| coordinate | signed: d/dt of the representation | both | shift (1) |
| unary shape | signed: kernel width and amplitude (corn); gain, g_eff, v_max, k_cut (water) | both | width (1), amp (1); gain (1), shape (3) |
| tail | signed: persistence lam (corn); lam, m (water) | both | decay (1); lam (1), m (1) |
| stop / temporal event | template: representation field energy on stalks within 0.3 m of any stop of >= 0.2 s (interior and terminal) | corn | events (3 per vertex added) |
| singular geometry | template: field energy on stalks within 0.3 m of a corner interval (`|theta'| > 3 rad/s`) | corn | corner_tighten (3 per vertex), tangent_alloc (3 per vertex) |
| smooth geometry | template: field energy times the anisotropic smooth density `(0.0231 a_par^2 + a_perp^2)^{1/4}` at the stalk's pass time, off corner and stop stalks | corn | smooth_adaptive (3 per vertex), smooth_uniform (3 per vertex) |
| interaction | template: sum over frames of the product of the two causes' representation field magnitudes | water | pair (1) |
| floor | signed: the base token's own calibration residual at A = 1, translated to each cause and scaled by the gain | water | none (abstain: wrong atom) |
| unresolved | `q_perp` above threshold | both | abstain |

Class and repair are separate: a diagnosed corner evaluates both corner
repairs, per B5. Every repair evaluation costs one consumer evaluation
of the repaired representation (grid repairs cost more compute but count
as one repair). Costs are in banked floats: one per kernel or token
parameter, three per path vertex.

Corn representation and repairs (`poc/rgre/corn.py`): base tolerance
0.03 m, spacetime DP with start/end event vertices forced; shift = best
of 21 offsets in [-0.2, 0.2] s; events = force interior stop events;
corner_tighten = tolerance halved on samples within 0.25 s of a corner;
tangent_alloc = chord-direction criterion at 0.08 rad; smooth_adaptive =
weights `1 + density / mean` on smooth moving samples; smooth_uniform =
tolerance halved; decay, width = best multiplier on a 9-point grid; amp
= least-squares amplitude. Error = relative RMS over B4's scored stalks
and all frames. Water (`poc/rgre/water.py`): W1's grid, fit subset and
evaluation set; shift = best of 41 offsets in [-0.15, 0.05] s; gain =
least squares; shape = Powell on log-multipliers of g_eff, v_max, k_cut
(150 evaluations); pair = best of 41 coefficients; lam = 9-point
multiplier grid; m = 11-point offset grid. Fits on the fit subset,
scored on the evaluation set.

## Fresh benchmark (seed 20260915; none of these was run before the freeze)

Corn, six each: smooth (three-harmonic random heading, peak `|theta'|`
in [0.8, 2.8] rad/s); corner (2 to 4 random corners of 50 to 160
degrees, 0.1 to 0.3 s); stop (1 to 2 interior stops of 0.4 to 1.5 s,
interior events missing from the representation); coordinate (gentle
path, token times offset by 0.05 to 0.15 s); tail (gentle path,
persistence multiplied by [0.3, 0.6] or [1.6, 3]); unary (gentle path,
kernel width multiplied by [0.5, 0.75] or [1.3, 1.8]). Water, six each:
coordinate (linear teacher delayed by 3 to 8 frames at 60 Hz);
unary (linear teacher with impulse width 0.02, 0.025, 0.04, 0.05 m or
depth 0.25, 0.7 m); tail (linear teacher with nu 4e-4, 7e-4, 1e-3 or
gamma0 0.5, 0.75, 1.0; 1.5e-3 was first written and overdamps the
solver's diagonal short waves, caught by the development run); interaction (nonlinear pairs at A in {5, 6, 8},
D in {0.1875, 0.28125} m, singles fitted per W4 so the unary part is
right). Mixtures, twelve: corn corner+stop (2), coordinate+corner (2),
tail+smooth (1), unary+stop (1); water coordinate+unary (nonlinear
singles at A = 3.5, 5, 7), interaction+coordinate (pairs with gain-only
singles, 2), tail+unary (1). Unknown, six: corn travelling gust field
(2), hidden second walker (1); water hidden second splash (2), moving
pressure source (1). Ground-truth class = the injected defect(s).

A development run with seed 1 and one case per class was used to debug
the code before this freeze and is declared; its outputs are not
scored. Nothing in the vocabulary, thresholds or bars changes after the
seed-20260915 run.

## Oracle and value

For every case every repair is evaluated from the base state; `a* =
argmax dE_a / C_a`. `V_cap = (dE_RGRE / C_RGRE) / (dE_a* / C_a*)`, with
RGRE's pick the best `dE / C` within its evaluated set, and 0 on
abstention. Raw `dE` is reported alongside.

## Hypotheses and bars (frozen; scored on the 72 known cases unless stated)

- **H1** median `V_cap >= 0.75`.
- **H2** median `N_RGRE / N_all <= 1/3` with H1 holding (by
  construction every class set has at most one third of the repairs;
  the content is H1).
- **H3** RGRE's median `V_cap` exceeds each of three baselines at the
  same per-case evaluation budget `k = max(N_RGRE, 1)`: cheapest-first
  (repairs by cost); largest generic opportunity (classes by raw share,
  no coherence, no abstention); class-free best local projection
  (individual diagnostics by their own fraction). A random-`k` baseline
  is reported.
- **H4** mixtures: diagnose, repair, re-diagnose, repair. Two-step
  recovery `dE^(2)_RGRE / dE^(2)_oracle` (oracle = best ordered pair of
  repairs) median `>= 0.7`. Reported: on how many mixtures the first
  repair lowers its own class's ownership and raises the other injected
  class's.
- **H5** at least 5 of 6 unknown cases abstain and at most 10 percent
  of known cases abstain.
- **H6** identity (chosen class = oracle's class) is lower among cases
  whose chosen class has `mu >= 0.5` than among those with `mu < 0.5`;
  the oracle's attainable `dE` in the two bins is reported.
- **H7** on mixtures, re-diagnosis beats executing the two top initial
  classes without re-diagnosis in more than half of the non-tied cases.

## Outcome tree (frozen)

- **A, procedure supported:** H1, H2, H4, H5 hold.
- **D, no useful compression of search:** H3 fails (checked before B and
  C).
- **B, diagnosis works, selection does not:** identity against the
  injected class `>= 0.7` and H1 fails.
- **C, opportunity works, identity does not:** the oracle's class is in
  the top two scores in `>= 75` percent of cases, identity against the
  oracle `< 0.7`, and H1 fails.
- Otherwise: no named outcome; the failing bars are listed.

If A occurs the next step is the end-to-end test on a new expensive
simulation with neither the cheap representation nor the defect sequence
chosen by hand. Results go in `poc/results/rgre1.md`; nothing above is
edited after the run.
