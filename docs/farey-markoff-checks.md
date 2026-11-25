# Checks of the two Markoff/Farey notes, and where the stopping rule comes from

Written 2026-11-25. Two notes were handed over in conversation: "Electrical
Geometry of the Markoff Tree and Its Tropical Boundary" and "Farey–Schauder
Geometry, Recursive Compression, and Low-Dimensional Deformation Coding".
Their exact claims were checked numerically; neither note's text is copied here.

## Electrical geometry (`poc/farey/electrical_check.py`, log beside it)

15 of 15 checks pass, on Markoff triples reached by Vieta moves from (3,3,3):
the series law 1/(cc') = 1/a^2 + 1/b^2; the star network's DtN form and rank
2; Lambda_0 = (2/27) P_A2 and the metric (2/9)[[2,1],[1,2]] at (3,3,3); the
(l, u) parametrisation, the Vieta moves u -> -u and u -> 2l - u, and
dx ^ dy = du ^ dl; |x+y| + |x-y| = 2 max(|x|,|y|); the edge profile's kinks at
the opposite Farey vertices; the closed form of the ray 3, 3, 6, 15, 39; the
modular cusp |tr A P^n| = 3(2n+1); the cusp conductances (18.2), (18.3); the
Mobius recurrence and g(r); the odd multiplicative action; the log divergence
6|s|^2 log N at Re s = 1/2 (measured slope 25.500 for s = 1/2 + 2i).

Points to state carefully: the Clifford relation of section 5 holds for any
two-dimensional metric near an isotropic point, so it is true but generic;
the agreement of the covariance form (4.5) with the electrical form is forced
by the three-fold symmetry of (3,3,3), and the form's source is not given;
the tropical part is close to standard cluster/Teichmuller tropicalisation;
sections 10 and 12 are open as the note says. No literature search was done.

## Farey–Schauder geometry (`poc/farey/schauder_check.py`, log beside it)

All exact claims tested pass, at 300 digits on the Farey tree from traces
(3,3): the forward child solves the Markoff equation; the McShane cell
recursion Phi(a,b) = Phi(a,c) + Phi(c,b) + h(c); the max-heap property of h;
the gap law g_m = log(c^2/(c^2-4)) = 2 log coth F(m) = -2 log(1 - 2h_m),
derived here from the fans k m +- x (error 1e-92); D/h > 4 on every cell
tested; the Green transform D(x,y) = sum min(alpha,beta) g over the cell's
mediants, at three cells to 1e-6 (truncated sum). The series
D/Phi = 4 + 4xy + 8xy(x+y) + (4xy/3)(15x^2+37xy+15y^2) + ... has a remainder
that shrinks exactly like e^5 when x and y are scaled by e: correct through
fourth order. (A first numerical test of it, on cells touching the root where
x = 1/9 is not small, was unfair and is not the check.)

Not re-run here: the root-exponential fit (section 10), the deep-coefficient
prediction experiments (11), the deformation concentration figures (12), the
template exponents 1.9989 and 2.96 (13, 14; these follow from Taylor's theorem
for any smooth family), and the warp experiments (16).

## The lineage to the stopping rule

The Farey note's section 15, X = G(theta) + r (a shared generator, a few
deformation coordinates, a residual), is the starting equation of
`docs/ecs-theory-snapshot.md`. Its tangent templates (section 13: first-order
deformation along Psi_A, Psi_B) become the snapshot's tangential improvement
certificate tau = |P_T r|^2 / |r|^2 (section 19): the share of the residual a
first-order move along the model's tangent can remove. ECS-Decision
(`docs/ecs-decision-v1-handoff.md`) turns that into a rule for fitting the
current model better versus changing the representation; ED1 to ED3 test it
on adapters; the pre-screen theory (`docs/prescreen-theory.md`) asks what share
of an adapter's first-order direction is real on fresh data; section 12 there
turns that share into the knee and the cross-fitted stopping rule. So the
stopping rule descends from this work through the ECS framework: the idea that
carried over is the first-order (tangent) measure of how much improvement is
available, and the certified stop of the Farey decoder (section 9: refine
until the frontier certificate is below tolerance) has its counterpart in
stopping when the improvement is no longer real. The Markoff identities
themselves are not used by the rule.

## Generalisation probe: the one-holed torus (2026-11-25)

`poc/farey/generalise.py`, log beside it. The generalised Markoff
equation x^2 + y^2 + z^2 - xyz = mu covers the punctured torus (mu = 0)
and the one-holed torus with a boundary geodesic of length L
(mu = 2 - 2 cosh(L/2) < 0). The first five results below were derived by
hand before the run and checked at mu = 0, -0.5, -2, -8, -20 on the Farey
tree from traces (4, 4); the sixth was found in the run.

| property | at the cusp (mu = 0) | with a boundary (mu < 0) | check |
|---|---|---|---|
| cell recursion | atom h(c) | atom h(c) - mu/(2abc): one extra term from the parents | exact to 1e-80 |
| atoms | positive, max-heap | positive, max-heap | every cell |
| total | sum of atoms = Phi(root) | the same, with d(a,b) = sqrt(1 - 4/a^2 - 4/b^2 + 4mu/(a^2 b^2)) | frontier below 1e-17 |
| stable-norm gap at a rational | log(c^2/(c^2 - 4)) | log((c^2 - mu)/(c^2 - 4)) | error below 1e-117 |
| electrical series law | 1/(cc') = 1/a^2 + 1/b^2 | plus a fixed resistor -mu/4 in series | exact |
| Farey-Schauder ratio D/Phi deep in the tree | 4 | 2(4 - mu)/(2 - mu) | to 12 digits at mu = -0.1, -1, -5, -30 |

Leading order, with x = 1/a^2, y = 1/b^2: Phi = (2 - mu) xy/2 and
D = (4 - mu) xy, so D/Phi -> 2(4 - mu)/(2 - mu). The boundary makes the
deep coefficients smaller relative to the McShane mass, down to the limit
2 as the boundary grows.

What is likely known: McShane-type identities for one-holed tori
(Mirzakhani; Tan, Wong and Zhang for generalised Markoff maps, arXiv
math/0411184); the atoms here are attached to cells and may regroup into
their per-geodesic form. Not found in the searches so far, and to be
checked when arXiv is reachable: the gap law in either form, the series
law with its boundary resistor, and the D/Phi limit.

## Markoff-Hurwitz quads reduce to one-holed tori (2026-11-25)

`poc/farey/quads.py`, log beside it. For quads a^2 + b^2 + c^2 + d^2 = abcd,
hold one coordinate fixed and rescale the others, X = ab, Y = ac, Z = ad:

    X^2 + Y^2 + Z^2 - XYZ = a^2 (b^2 + c^2 + d^2 - a bcd) = -a^4,

and the quad move d -> abc - d is the Markoff move Z -> XY - Z. So every
region of the quad tree (the quads sharing one coordinate value) is the
one-holed-torus tree with mu = -a^4, a boundary of length L with
2 cosh(L/2) = 2 + a^4. Checked on the integer quads from (2, 2, 2, 6): the
regions of 2, 6 and 22 (94 vertices each) lie exactly on their rescaled
equations; the region of 2 is the mu = -16 tree from (4, 4) (first child
12 = 2 x 6), with the exact cell recursion, heap, certificate, gap law and
D/Phi -> 2(4 - mu)/(2 - mu) = 20/9 all holding.

So inside each region the whole Farey machinery holds, with the region's
coordinate setting the boundary. What is not obtained: one certificate for
the whole quad tree. Every quad lies in four regions, and a McShane-type
identity over all of it is known (Huang and Norbury, "Simple geodesics and
Markoff quads", arXiv 1312.7089) but not yet expressed here as a sum of
the per-region certificates. The structure suggests a two-level hierarchy:
regions indexed by one coordinate's values, each a one-holed-torus tree.

## Literature check, with arXiv reachable (2026-11-25)

Papers read: Huang-Norbury (arXiv 1312.7089), Sorrentino-Veselov (1707.03901),
McShane-Rivin (math/0005220), Tan-Wong-Zhang (math/0411184), Gaster
(2107.13499), O'Sullivan (2609.14149, September 2026).

| result here | status |
|---|---|
| gap law g = log(c^2/(c^2-4)) and the one-sided derivatives of Fock's function | **known**. Sorrentino-Veselov asked for them (section 5); Hines (2020) and Gaster (2021, Proposition 1.8) computed them. `poc/farey/fock_derivatives.py` re-derives them in another form (psi'(1/2 +-) = +-log(9/8)) and checks them to 12 digits. |
| gap law with a boundary, log((c^2-mu)/(c^2-4)) | **known**: O'Sullivan, S' - S = n log((u^2 - D)/(u^2 - 4)), equation (4.10), by the same factorisation. Checked here on Sorrentino-Veselov's a-family (mu = 4 - 4a^6), a = 2, 3. |
| cell recursion with the boundary atom h(c) - mu/(2abc) | **known in another normalisation**: Hu-Tan-Zhang (2015); O'Sullivan Theorem 9.9, whose Upsilon(b, b') = 1 - m_q/(m_b m_b') splits with -D/(m_b m_q m_b') per vertex. |
| McShane cell recursion at mu = 0 | **known**: Bowditch (1996). |
| one exact certificate for a quad tree | **known**: Huang-Norbury's splitting 1 = a/S + b/S + c/S + d/S, S = a + b + c + d, for their quads (a + b + c + d)^2 = abcd. Note their quads differ from the Markoff-Hurwitz a^2 + b^2 + c^2 + d^2 = abcd used here; they relate at n = 4 by a change of coordinates (their Remark 2, via Hu-Tan-Zhang). |
| Markoff-Hurwitz region = one-holed torus with mu = -a^4 | not found in these papers; elementary, and plausibly in Hu-Tan-Zhang, not read. |
| electrical series law and its boundary resistor -mu/4 | not found; algebraically shallow (the Vieta product rewritten). |
| D/Phi -> 2(4 - mu)/(2 - mu), with the note's Phi and the Farey-Schauder defect D | not found in these papers. |
| Farey-Schauder expansion as certified anytime compression, deformation coding | not found; the algorithmic reading appears to be the new part. |

Bottom line: the exact identities of both notes are largely known, several
very recently (O'Sullivan, September 2026, studies these trees for all D
in a self-contained way). What stands as possibly new is the algorithmic and
coding use of them, the electrical reading, and the D/Phi limit.

## The convergence rate of best-first Farey-Schauder refinement (2026-11-25)

`poc/farey/rate.py`, log beside it. The Farey note fitted
log E_N ~ 0.478 - 3.312 sqrt(N) - 0.538 log N (section 10). Derived before the
run, then checked:

**Rate law.** For best-first Farey-Schauder refinement of the stable norm of a
hyperbolic punctured or one-holed torus, on the cone spanned by a unimodular
root pair,

    log E_N = -c sqrt(N) + O(log N),   c = 2 pi / sqrt(6 A),   i.e.  c^2 A = 2 pi^2 / 3,

where A = (1/2) int_0^1 f(t)^-2 dt is the area of the stable-norm unit ball in
that cone (f the stable norm on the projective slice). The product c^2 A is
the same for every surface.

**Why (heuristic, three steps).** (i) The normalised detail a_v = D_v/M_v decays
like e^{-2F} in the half-length F of the cell's mediant, up to factors
polynomial in F (deep in the tree D = (4 - mu) xy at leading order, and the
heights M grow polynomially); (ii) best-first by a_v therefore refines nodes
in order of F up to those factors; (iii) the primitive lattice points of the
cone with stable norm at most L number (6/pi^2) A L^2 (the classical count in
a dilated convex region), so after N refinements L = sqrt(N pi^2/(6A)) and
E_N = e^{-2L} up to polynomial factors.

**Checks** (best-first by a_v at 400 digits, fits of log E_N on 1, sqrt N,
log N over N in [1000, 6000)):

| surface | fitted c | 2 pi / sqrt(6A) | A | complete node count, 2/sqrt(C) |
|---|---|---|---|---|
| modular torus (traces 3, 3) | 3.3281 | 3.3267 | 0.59453544 | 3.29 |
| one-holed, mu = -2 (traces 4, 4) | 4.7415 | 4.7407 | 0.29276311 | 4.72 |
| one-holed, mu = -8 | 4.7004 | 4.6981 | 0.29810719 | 4.69 |
| one-holed, mu = -20 | 4.5842 | 4.5808 | 0.31356910 | 4.55 |

For the modular torus 2 pi/sqrt(6A) = 3.3267 equals sqrt(2/C) for Zagier's
constant C = 0.180717 in the count of Markov numbers, C (log 3x)^2; that is
A = pi^2 C / 3. So the note's 3.312 is this constant, fitted on a shorter
range. An earlier run at 150 digits gave wrong rates for mu < 0: the errors
there fall below 1e-150 by N = 6000 and the fits measured rounding.

**Status.** The count in step (iii), and its link to the unit ball, is
classical (McShane-Rivin count simple geodesics by length through the stable
norm ball; Zagier counts Markov numbers). Not found in the papers read: the
rate law for the refinement algorithm, c^2 A = 2 pi^2/3. Steps (i) and (ii)
are heuristic here; making them rigorous would also fix the log N term
(fitted -0.44 here, -0.54 in the note).

## Universality and the moduli dependence of the rate (2026-11-25)

`poc/farey/universal.py`, logs `universal_sphere.log`, `universal_moduli.log`.

**The law needs the detail decay exponent.** On the four-punctured sphere
(X^2 + Y^2 + Z^2 - XYZ + 8(X + Y + Z) + 28 = 0, mediant rule Z' = XY - 8 - Z,
symmetric point (7, 7, 7)), best-first refinement fits c = 3.3281 with ball
area A = 0.14863: c^2 A = 1.6463, a quarter of the torus value. Its curve
lengths are exactly twice the modular torus's (7 = 3^2 - 2, so the sphere's
half-length is twice the torus's), so its details decay like e^{-F}, not
e^{-2F}. With kappa the exponent of that decay,

    c^2 A = kappa^2 pi^2 / 6 = kappa^2 zeta(2),

which both cases meet to 0.1% (torus 6.5852/4 = 1.6463, sphere 1.6463/1;
pi^2/6 = 1.6449). The zeta(2) is the density 6/pi^2 of primitive lattice
directions. The earlier statement c^2 A = 2 pi^2/3 is the kappa = 2 case.

**Moduli dependence.** The intrinsic area covers every direction up to sign:
A = A(cone e0, e1) + A(cone e0, -e1). Over 160 reduced triples a <= b <= o of
the punctured torus (a in [2.02, 3], b in [2.02, 4.5]), A is smallest at the
modular torus (3, 3, 3), A = 1.7836, c = 2 pi/sqrt(6A) = 1.921, and grows as
a curve shortens (A = 1.909, c = 1.857 at a = 2.27). Among the surfaces
sampled the modular torus compresses fastest. A one-cone area is not
intrinsic (a short curve outside the cone lowers it), and an earlier scan
that used one is superseded.

A is Mirzakhani's B(X) up to normalisation (for the punctured torus, B(X) is
the measure of the unit ball of the length function), so the rate is
c(X) = kappa pi / sqrt(6 A(X)). Whether B is minimised at the modular torus
on all of moduli space, and whether that is known, is not checked here.

## Mode-locking in the sine circle map: the Farey structure carries over, the rate law does not (2026-11-25)

`poc/farey/circle_map.py`, log beside it. The driven-oscillator model
theta -> theta + Omega - (K/2 pi) sin(2 pi theta); for each p/q the rotation
number locks on an Omega-interval (an Arnold tongue), computed here exactly
as the Omega where the extremum over theta of f^q(theta) - theta - p crosses
zero, each tongue searched between its Farey parents' tongues. Tongues with
q <= 22 to 26 on [0, 1/2]; the 0/1 tongue comes out at the exact +-K/2 pi.

| K | tongues | heap violations down the Farey tree | fitted exp(-c sqrt N) c | predicted pi/sqrt(6A) | power-law fit of the remainder |
|---|---|---|---|---|---|
| 0.5 | 76 | 0 | 1.47 | 2.19 | N^-3.0 |
| 0.8 | 91 | 0 | 0.69 | 1.37 | N^-1.6 |
| 0.95 | 107 | 0 | 0.43 | 1.06 | N^-1.2 |
| 1.0 | 107 | 0 | 0.36 | 0.98 | N^-0.95 |

- **What carries over:** tongue widths decrease down the Farey tree with no
  exception, so best-first refinement and pruning (stop a subtree once its
  tongue is narrower than the target) are exact.
- **What does not:** the root-exponential rate law. The prediction assumed
  widths fall like exp(-q lambda(p/q)) everywhere. Next to a wide tongue they
  fall like a power instead (the 1/q tongues beside 0/1 at K = 0.8 fall like
  q^-3.2): at a tongue edge the dynamics is a saddle-node, a parabolic point,
  and the fans of fractions accumulating on it have widths decaying
  polynomially. The remainder then decays like a power of N, steeper for
  weaker coupling. This is the dichotomy of the electrical note's sections
  14-15: exponential (hyperbolic) fans give root-exponential compression, as
  on the Markoff tree, where every fan is hyperbolic; parabolic fans give
  power laws. The rate law c^2 A = kappa^2 zeta(2) belongs to the hyperbolic
  case.
- **Cost, as implemented** (an unoptimised edge solver, about 1.5e6 map
  evaluations per tongue), against a uniform Omega sweep with two points per
  target width and 2000 iterations per point: for all tongues of width at
  least 1e-4, Farey costs 5e7 to 2e8 and the sweep 2e7; for 1e-6, Farey 1.1e8
  to 2.2e8 against 2e9 for the sweep, about 10 times fewer, with edges to
  machine precision rather than to the grid spacing. The Farey cost grows with
  the number of tongues above the target, the sweep's with 1/(target width);
  a Newton solve for the saddle-node edges, not tried, would cut the
  per-tongue cost by a large factor.

## Identity search (2026-11-25)

`poc/farey/identity_search.py`, log beside it. Twelve natural sums over the
cells of the modular torus's tree, to about 60 digits, tested by PSLQ against
{1, log 2, log 3, log 5, log lam3, log(3 + 2 sqrt 2), pi^2, sqrt 5, sqrt 5 log lam3},
lam3 = (3 + sqrt 5)/2, coefficients up to 2000.

- The two known ones are recovered exactly: sum h = (sqrt 5 - 2)/6
  (McShane, via the cell certificate) and sum M g = log(5 lam3/9) (Hines;
  O'Sullivan Theorem 9.14). The search is sensitive enough to find
  identities of this kind.
- No relation in this basis for: sum D, sum D/M, sum D/(XYM), sum M h, sum g,
  sum 1/c^2, sum M/c^2, sum D M, sum h/M, sum XY g.

**The Green principle.** The curvature of the stable norm on the slice is
purely atomic (O'Sullivan: infinitely flat at irrationals), with mass
M_w g_w at each rational t_w. So

    f(t) = L_0(t) - sum_w M_w g_w G(t, t_w),   G(t, s) = min(t, s)(1 - max(t, s)),

G the Green function of -d^2/dt^2 on [0, 1], and every linear functional of
f is an identity. The note's Green transform is f evaluated at one mediant.

**A lemma and a corollary.** For a node w, the sum of min(alpha, beta) over
the cells containing it (w = alpha L + beta R in the cell (L, R)) is M_w - 1:
descending into the child cell containing w is one subtractive Euclid step,
which lowers alpha + beta by min(alpha, beta), down to (1, 1) at w's own cell.
Checked for every p/q with q <= 13. With the note's Green transform this gives

    sum over cells of D_v = sum over nodes of (M_w - 1) g_w,

so with Hines, **sum_v D_v + sum_w g_w = log(5 lam3/9)** on the modular torus
(0.21369313299 + 0.16094385223 = 0.37463698522), and for any discriminator D
with O'Sullivan's right side of (9.16). Similarly the weight of g_w in
sum_v D_v/(X_v Y_v M_v) is alpha_w beta_w / M_w (checked: 2/5 -> 6/5,
3/7 -> 12/7, 3/8 -> 15/8), which is the integral
int_0^1 f = (F(e0) + F(e1))/2 - (1/2) sum_w g_w alpha_w beta_w / M_w.
These are consequences of known facts plus Green-function and Euclid
algebra: correct and, as far as the papers read go, not stated, but not deep.

**Electrical harmonic functions: none simple.** Ten symmetric candidates
u(A, B, C) were tested for Kirchhoff balance with the note's conductances
g = 4/(A^2 + B^2) at 400 random Markoff triples. The only balanced one,
A/(BC) + B/(AC) + C/(AB), is identically 1 on the Markoff surface. No
conservation law from a simple harmonic function.

## The four-holed sphere: gap law and a Hines-type identity (2026-11-25)

Script `poc/farey/sphere.py`, output `poc/farey/sphere.log` (120 digits).

**Setting.** On a four-holed sphere with boundary traces (α, β, γ, δ), simple
closed curves are again indexed by Farey slopes. Their traces satisfy the
Fricke relation, which has linear terms:

    X² + Y² + Z² − XYZ + pX + qY + rZ + s = 0,
    p = αβ + γδ,  q = βγ + αδ,  r = αγ + βδ,
    s = α² + β² + γ² + δ² + αβγδ − 4.

A slope (P, Q) picks up the coefficient of its parity class: (1,0) takes p,
(0,1) takes q, and (1,1) takes r. The mediant rule becomes
c = ab − κ(class of c) − (trace of the opposite vertex).

**Gap law.** It was derived symbolically first, using the fan recurrence
t_{k+1} + t_{k−1} = c t_k − κ with its period-2 particular solution. At a
curve of trace c with coefficient κ_m, where κ_x and κ_y are the coefficients
of the other two classes:

    g = log[ (c² + κ_m c + s)/(c² − 4) + (κ_x² + κ_y² + κ_x κ_y c)/(c² − 4)² ].

When all κ = 0 this reduces to the generalised torus law
log((c² − μ)/(c² − 4)), with μ = −s. The second term exists only because the
coefficient alternates along each fan.

**Hines-type identity.** Over the rationals of (0, 1), with M the height
p + q:

    Σ M g = F(e₀) + F(e₁) − log K₀ − log K₁,

where F = arccosh(t/2), and K₀, K₁ are the leading coefficients of the two
end fans (each with its alternating particular solution).

**Checks.** The gap law was compared with brute force along fans of length 70,
on the first 30 cells. The identity was summed over 4000 cells.

| Boundary traces | Gap-law error | Σ M g | Identity error | Non-positive defects |
|---|---|---|---|---|
| (2, 2, 2, 2), four cusps | 3e−106 | 0.74927397043 | 2e−87 | 0 |
| (2.5, 2.2, 3.0, 2.1) | 5e−118 | 0.40388368512 | 2e−107 | 0 |
| (3, 2, 2, 4) | 4e−118 | 0.37518525822 | 2e−112 | 0 |

For the four-cusped sphere, the sum is twice the modular torus's Hines
constant. This is consistent with the two-fold cover relating the two
surfaces.

**Literature status.** I read Maloni–Palesi–Tan (arXiv 1304.5770) and
Hu–Tan (arXiv 1402.1573) directly:

- Maloni–Palesi–Tan studies the domain of discontinuity and BQ-conditions for
  this Fricke relation. It contains no slope-gap or stable-norm formula. It
  defers McShane generalisations to future work, following Hu–Tan–Zhang's
  Coxeter-group view.
- Hu–Tan gives Luo–Tan dilogarithm identities. It uses the sphere to torus
  link, but has no gap law.
- A web search turned up no stable-norm or derivative results for the
  Fricke cubic.

So: **not found in the literature checked; not an exhaustive search.** The
torus case is known (Hines; Gaster; O'Sullivan eq. 4.10, Thm 9.14), so the
sphere version is the natural generalisation. Its most likely home is
Hu–Tan–Zhang or later work on Coxeter actions on quartic varieties; check
that before calling it new.

## Generalisation: one principle for every Vieta tree, and a vector Hines identity (2026-11-25)

Script `poc/farey/general.py`, output `poc/farey/general.log` (80 digits).

The setting is any cubic X² + Y² + Z² − XYZ + pX + qY + rZ + s = 0, with real
or complex coefficients. The one-holed torus is the case p = q = r = 0 with
s = −μ. The four-holed sphere has the Fricke coefficients. Cantat–Loray show
that every real or complex (p, q, r, s) arises as a four-holed-sphere
character variety, so this family is the general one.

**Energy principle (proved; it is a short computation).**

- Fix a curve m with trace c. The traces t_k of the curves L + k·m, for k in
  ℤ, satisfy a linear recurrence: t_{k+1} + t_{k−1} = c·t_k − κ_{k+1}. The
  forcing κ alternates between the parity classes of L and R.
- Subtract the period-2 particular solution, giving w_k. Then the quantity
  I = w_k² + w_{k+1}² − c·w_k·w_{k+1} is the same at every k.
- Writing w_k = Kλ^k + K′λ^{−k} gives I = −(c² − 4)·K·K′.
- The two ends of this bi-infinite fan are the two fans k·m + L and k·m − L.
  So the gap is

      g_m = log K + log K′ = log( −I / (c² − 4) ).

The cubic, evaluated at the cell, gives I. That is the only place the surface
enters, and it produces the torus law and the four-holed-sphere law as special
cases. Numerically the closed-form gap law agrees with the energy computation
to 10⁻⁶³ or better in every case.

**Vector Hines identity.**

- On the cone between e₀ and e₁, the gradient of the stable norm N jumps by
  g_m·(−q, p) at each rational m = (p, q).
- The one-sided gradients at the cone's edges come from the end fans:
  ∇N(e₀⁺) = (F(e₀), log K₀) and ∇N(e₁⁻) = (log K₁, F(e₁)).
- Summing the jumps therefore gives two separate identities:

      Σ p·g_m = F(e₁) − log K₀,
      Σ q·g_m = F(e₀) − log K₁.

Their sum is the Hines-type identity (for the torus, Hines / O'Sullivan
Thm 9.14). On symmetric surfaces the two halves are equal, so the split
carries no new information there. On asymmetric surfaces the halves differ
and each is a separate identity.

The proof is complete, apart from the claim that the second-derivative
measure of N is purely atomic at the rationals. That claim is what makes
"sum of jumps = total change" exact. The numbers below are consistent with it
everywhere.

| Case | Σ p·g error | Σ q·g error |
|---|---|---|
| Modular torus (3, 3) | 5e−76 | 5e−76 |
| Punctured torus (2.6, 4.1) | 2e−78 | 2e−78 |
| One-holed torus μ = −7 | 6e−79 | 2e−79 |
| Torus with cone point μ = 1.5 | 9e−79 | 7e−80 |
| Four-holed sphere (2.5, 2.2, 3.0, 2.1) | 1e−79 | 1e−79 |
| Quasi-Fuchsian torus (3 + 0.4i, 3.2 − 0.3i) | 7e−80 | 2e−78 |
| Arbitrary real cubic (1.3, −0.7, 2.9, 5.1) | 3e−79 | 8e−79 |
| Arbitrary complex cubic | 1e−78 | 7e−80 |
| Complex four-holed sphere | 1e−78 | 3e−78 |

The complex cases use principal branches near the real locus. The tree sums
converge because each start point lies in Bowditch's Q-condition region,
where traces grow along every path of the tree. That convergence condition is
the natural boundary for these identities.

An earlier run left a constant 2·10⁻²⁰ residual on the generic sphere, with
equal errors in the two components. It came from passing the boundary traces
as double-precision floats. With exact inputs the residual is gone.

**Literature status.** The torus Hines identity is known. The vector
(two-component) split was not seen in O'Sullivan, Hines or Gaster as checked
earlier, and the energy formulation was not seen in any of these sources. The
extension to the general cubic, including complex coefficients, was not found
either. Same caveat as above: Hu–Tan–Zhang still needs checking.
