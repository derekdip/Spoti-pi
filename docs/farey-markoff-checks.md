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

## Literature check: Hu–Tan–Zhang (2026-11-25)

Maloni–Palesi–Tan cite a 2012 preprint, "Coxeter group actions on quartic
varieties". Its published form is Hu–Tan–Zhang, *Polynomial automorphisms of
Cⁿ preserving the Markoff–Hurwitz polynomial* (arXiv 1501.06955). I also read
Hu–Tan–Zhang, *A new identity for SL(2, C)-characters of the once punctured
torus group* (arXiv 1402.3904).

**What is already known.**

- **The torus energy principle is in 1402.3904, eq. (24).** Along the
  neighbours of a curve X, the traces are y_n = Aλⁿ + Bλ⁻ⁿ, and "by the vertex
  relation" AB = (x² − μ)/(x² − 4). This holds for complex characters that
  satisfy Bowditch's conditions. Our gap g = log(AB) is exactly this. They use
  it as a lemma towards McShane-type sums, not for the stable norm, but the
  fact itself is theirs.
- **1402.3904, Thm 1.3, splits McShane's identity by parity class.** Using the
  three Z₂-homology classes, Σ_i Σ_{X ∈ Ω_i} h_{μ,p_i}(x) = 1/2 holds for any
  weights p₁ + p₂ + p₃ = 1. This is a decomposition with the same flavour as
  our vector Hines identity, but for a different sum, and the split is by
  parity class rather than by gradient component.
- **1501.06955** proves McShane-type identities for the n-variable
  Markoff–Hurwitz equation, using the "Fibonacci growth" of log⁺|φ|. It has
  no slope gaps or stable-norm identities.

**What is still not found.**

1. The sphere gap law, with its second term from the alternating parity
   forcing. Neither Hu–Tan–Zhang paper treats Fricke cubics with linear terms
   in this way, and Maloni–Palesi–Tan has no such formula.
2. The vector Hines identity, Σ p·g = F(e₁) − log K₀ and
   Σ q·g = F(e₀) − log K₁, for the torus or the general cubic.
3. The Hines-type identity for the four-holed sphere and for the general
   (complex) cubic.

**Revised status.**

| Result | Status |
|---|---|
| Energy principle, torus | Known (Hu–Tan–Zhang 2014, eq. 24) |
| Energy principle with periodic forcing (sphere, general cubic) | A direct extension of it |
| Items 1–3 above | Not found in Hines, Gaster, O'Sullivan, Maloni–Palesi–Tan, Hu–Tan, or either Hu–Tan–Zhang paper |

The search is still not exhaustive: Mirzakhani-style length identities for
the four-holed sphere and the Painlevé VI literature on the Cantat–Loray cubic
have not been checked.

## The gap law as a conic invariant, and no parity split of Hines (2026-11-25)

Script `poc/farey/parity_split.py`, output `poc/farey/parity_split.log`.

**Most general form of the gap law.**

- Fix the trace c of a curve m. The cubic then becomes a conic in the other
  two traces:

      Y² + Z² − cYZ + κ_x·Y + κ_y·Z + (c² + κ_m·c + s) = 0.

- Let M₃ be this conic's 3×3 symmetric matrix. Expanding the determinant
  gives −4·det M₃ = (c² + κ_m·c + s)(c² − 4) + κ_x² + κ_y² + κ_x·κ_y·c.
  So the four-holed-sphere law is exactly

      e^g = −4·det M₃ / (c² − 4)².

  Here (c² − 4)/4 = −det M₂, the determinant of the conic's quadratic part.
- The gap at a curve is therefore the ratio of the two determinant invariants
  of the conic cut out at that curve's trace. Nothing else about the surface
  enters.
- The statement holds for any cubic surface with Vieta flips whose slices are
  conics. If the leading coefficients b, c on Y² and Z² are not 1, rescale to
  get e^g = −bc·det M₃ / (4·(det M₂)²).
- Numerically the conic form agrees with the gap law to 5e−91 on the modular
  torus, a punctured torus and a four-holed sphere. The check uses the first
  200 cells. Further down the tree mpmath's generic determinant underflows
  (traces of 10¹⁰⁰ and more), and that is the cause of an "inf" in a first run.

**Parity-class split of the Hines sum: none found.**

- Hu–Tan–Zhang split McShane's identity across the three Z₂ classes with free
  weights (1402.3904, Thm 1.3). I tested whether the Hines-type sums do the
  same.
- I formed the six sums S(class)·{p·g, q·g} and ran PSLQ against 13 constants
  of the root cell: F and log(x² − 4) of the four root traces, the end-fan
  coefficients K₀ and K₁, both fans around e₀ + e₁, and 1 and log 2.
- **Each sum alone:** no relation with coefficients up to 200, on all three
  surfaces.
- **Jointly:** the only relation found is the vector Hines identity
  (Σ over classes of q·g = F(e₀) − log K₁), which is the control.
- **With that removed:** drop the (1, 1)-class sums and K₀, K₁, and there is
  no relation with coefficients up to 100, on the punctured torus or the
  sphere.

**Reading.** McShane's identity splits because it is built from a per-vertex
identity: a sum over the neighbours of each region with a closed form (their
eq. 26). Hines' identity is a global telescoping: the gradient jumps add up to
the change in the gradient between the two edges of the cone. Only the two
end fans enter, and a parity class sees no boundary of its own. So the
parity-split route does not carry over, and the vector identity looks like
the complete set of linear identities of this kind.

This is a negative result for this basis only; it does not exclude closed
forms in other constants.

## Number theory: Ghosh–Sarnak surfaces and Rosenberger equations (2026-11-25)

Script `poc/farey/numtheory.py`, output `poc/farey/numtheory.log`. Tree
recursions run in exact integers; logarithms are taken at 80 digits or more,
with the precision of the defect test growing with the size of the trace.

### A. Ghosh–Sarnak surfaces x² + y² + z² − xyz = k

- For each k, I took one integer root of the solution tree (traces ≥ 3,
  growing cone) and followed the integer orbit.
- The gap at a node of value c is the log of a rational number:

      e^g = (c² − k)/(c² − 4).

- The vector Hines identity becomes an infinite product of rationals over the
  integer orbit:

      Π_m ((c_m² − k)/(c_m² − 4))^{p_m} = λ(Y)·√(X² − 4) / (W − Y/λ(X)),

  with λ(t) = (t + √(t² − 4))/2. The same holds with p ↔ q and X ↔ Y.

| k | Root (X, Y; opposite) | Gap law vs integer fans | Product rel. error | Defects ≤ 0 (of 3000) | Product^p |
|---|---|---|---|---|---|
| −20 | (3, 5; 6) | 2e−78 | 9e−78 | 0 | 1.5110562 |
| 0 | (3, 3; 3) | 1e−78 | 5e−76 | 0 | 1.2060113 |
| 4 | (3, 3; 2) | 2e−78 | 5e−78 | 2620 | 1 exactly |
| 5 | (3, 4; 2) | 3e−78 | 5e−78 | 3000 | 0.9850077 |
| 8 | (3, 5; 2) | 2e−78 | 1e−77 | 3000 | 0.9660488 |
| 13 | (3, 6; 2) | 2e−78 | 1e−77 | 3000 | 0.9507270 |
| 20 | (3, 5; 1) | 3e−78 | 1e−77 | 3000 | 0.8861451 |
| 52 | (4, 6; 0) | 2e−78 | 1e−77 | 3000 | 0.9016608 |
| 100 | (6, 8; 0) | 5e−78 | 1e−77 | 3000 | 0.9551530 |

For k = −5, −1, 1, 2 and 3 there is no growing integer root with
3 ≤ X ≤ Y < 60.

**Reading.**

- **The gap law and both product identities hold for every k.** That
  includes k > 4, where no hyperbolic torus lies behind the equation (the
  commutator trace k − 2 is greater than 2). They are statements about the
  Vieta tree, not about geometry.
- **Geometry shows up in the sign.**
  - For k < 4 the gaps are positive and every defect is positive: the
    "norm" is convex, as for a hyperbolic surface.
  - At k = 4 every gap is 0 and the norm is linear. This is the reducible
    (abelian) case, and the product is exactly 1.
  - For k > 4 every gap is negative and every defect is negative: the norm
    is concave at every rational, and the product is less than 1.
- So a single sign, of k − 4, separates "comes from a hyperbolic surface"
  from "does not", while the identities themselves do not care.
- An earlier run showed 829 non-positive defects at k = −20. That was
  precision: D ~ 1/c² falls below 80-digit resolution once traces pass about
  10⁴⁰. It disappears with adaptive precision.

### B. Rosenberger equations ax² + by² + cz² = dxyz

**Rescaling.** Setting T_i = d·x_i·√(a_i)/√(abc) turns any such equation into
the Markoff equation T₁² + T₂² + T₃² = T₁T₂T₃. So every one is a
punctured-torus character, with *rational* squared traces
T_i² = d²·x_i²·a_i/(abc).

**Search.** I searched a ≤ b ≤ c ≤ 6, d ≤ 12, with solutions below 30, and
reduced each equation to its minimal triple by descending Vieta moves. This
gives 97 distinct tori. The modular torus (9, 9, 9) collects 31 equations,
and (8, 8, 16) collects 24.

**Integer form.** In raw integers, the parity class of a slope is exactly
which of the three variables the node belongs to. A node of variable i with
value v has

    e^g = d²v² / (d²v² − 4·a_j·a_k).

**Products over 3000 integer nodes**, identified with mpmath.identify:

| Equation | Root | Π (d²v²/(d²v² − 4a_ja_k))^{p} | Rel. error |
|---|---|---|---|
| x² + y² + z² = 3xyz (Markoff) | (1, 1, 1) | (5 + √5)/6 | 5e−76 |
| x² + y² + 2z² = 4xyz | (1, 1, 1) | 1 + √2/2 | 3e−61 |
| x² + 2y² + 3z² = 6xyz | (1, 1, 1) | 1 + √6/3 | 1e−60 |
| x² + y² + 5z² = 5xyz | (1, 2, 1) | 1 + 2√5/5 | 1e−58 |

The last three errors are larger only because of the heap-order truncation;
the leftover terms are below 10⁻⁵⁸.

**Example.** For Markoff numbers this reads

    Π over the Markoff tree on slopes in (0, 1) of (9m²/(9m² − 4))^{p(m)} = (5 + √5)/6.

Its square, the p + q product, is the known Hines identity in product form.
The p-half is new information only when the root is asymmetric. Here that is
x² + 2y² + 3z² = 6xyz, whose root traces are (√6, 2√3, 3√2).

The four equations in the table are, I believe, Rosenberger's distinguished
list. Their link to the arithmetic once-punctured tori (Takeuchi) is recalled
from memory and was not checked in this session.

**Literature status.** Ghosh–Sarnak and later work study integer points,
orbits and local–global failures on these surfaces. I have not seen the
products above, or the k − 4 sign dichotomy of the norm, in what I have read.
That literature was not searched in this session.

## Literature check (a): Hines, O'Sullivan, Goldman, Doan–Li–Nguyen, Ghosh–Sarnak (2026-11-25)

Papers read this round:

- Hines 2020 (arXiv 2001.05557).
- O'Sullivan §9.3 (arXiv 2609.14149).
- Goldman 2003 (math/0305096).
- Doan–Li–Nguyen 2026 (arXiv 2605.14574).
- An arXiv search on Markoff surfaces and integral points. It returned
  Ghosh–Sarnak 1706.06712, Colliot-Thélène–Wei–Xu, Dao, Browning–Wilsch,
  Chen and Mitankin–Uhlemann. These study integral points, Hasse principles
  and Brauer–Manin obstructions. None has length-type products.

**Corrections to the previous section.**

- **The integer products are Hines's, for k = 0.** Hines already writes the
  Markoff-number product, e.g. Π(1 − 4/(9m²))^{−6h} for the modular torus.
  He also remarks that any Markoff triple gives an infinite product of
  rationals equal to a product of three quadratic units, and that traces in a
  number field give relative quadratic units. The Rosenberger products are
  instances of this, by the rescaling.
- **The total identity for any k is O'Sullivan's.** His Theorem 9.14 holds for
  any discriminator D (our k) on rising trees with labels > 2, including
  D > 4. His proof also telescopes slopes, with exponentially small error
  terms. So the total Ghosh–Sarnak products are instances of his theorem.
- **"No geometry behind k > 4" is wrong for k > 20.** Goldman shows that for
  t = k − 2 > 18 the level set contains wandering domains Γ·Ω₀. These are
  discrete faithful characters of hyperbolic three-holed spheres, where X, Y
  and Z are the boundary curves. Vieta-flipping (x, y, −|z|) gives
  all-positive trees, so some positive trees with k > 20 are pants orbits.
  Their tree curves are then non-simple primitive curves on the pants. For
  4 < k ≤ 20 the action is ergodic and there are no discrete faithful points.
- **What this does to the k = 52 and k = 100 examples.** Those integer roots
  contain the trace 0, an elliptic element of order 4, so they are not pants.
  A genuine pants example, boundary traces (−3, −3, −3) giving k = 54, is
  checked below.
- **The sign dichotomy has a geometric reading.**
  - For k < 4 (tori), the axes of the generators cross, and ℓ(ab) < ℓ(a) + ℓ(b).
  - For pants, the axes are ultraparallel, and ℓ(ab) > ℓ(a) + ℓ(b).
  - So the norm is convex in the first case and concave in the second. The
    identities hold in both.
- **Doan–Li–Nguyen.**
  - They prove that rational directions are genuine corners with angle
    ≍ ht(w)·e^{−‖w‖}.
  - They prove differentiability at irrational directions and an exact
    flatness formula.
  - Their Theorem 1.3 is a dual-area identity, Area(B*) = 4 Σ_γ ℓ log coth(ℓ/2),
    for complete finite-area once-punctured tori only.
  - They do not treat holes, cone points, spheres, or a vector form.

**Updated status.**

| Result | Status |
|---|---|
| Torus gap law, any μ, complex | Known (Hines; Hu–Tan–Zhang eq. 24; O'Sullivan eq. 4.10) |
| Total Hines identity, real, any D | Known (Hines for D = 0; O'Sullivan Thm 9.14) |
| Integer products, k = 0 | Known (Hines) |
| Integer products, other k | Instances of O'Sullivan's theorem |
| Four-holed-sphere gap law and Hines-type identity | Not found |
| Conic-determinant form of the gap law | Not found |
| Vector (one-coordinate) Hines identity | Not found; it is the same telescoping on a non-compact slice, so a modest variant |
| Complex-trace Hines identities | Not found |
| The proof below and its corollaries | See next section |

## Proof (b): the vector Hines identity, and two corollaries (2026-11-25)

Scripts `poc/farey/proof_check.py` and `poc/farey/dual_area.py`, with logs.

**Notation.** For a Farey pair (L, R):

- K(L; R) is the leading coefficient of the fan t_k = tr(kL + R), so that
  t_k ≈ K·λ_L^k, plus the period-2 particular solution in the sphere case.
- D_L^R = log K(L; R), N = F = arccosh(tr/2), and β(L, R) = N(R) − D_L^R.

**Fact 1.** D_L^{L+R} = D_L^R + N(L). The fan through L + R is the same
sequence shifted one step.

**Fact 2.** g_m = D_m^L + D_m^R − N(m), for m = L + R. The bi-infinite fan
through L around m has its two ends at k·m + L and k·m + R, and the second is
shifted by one step.

Both facts are exact identities about linear recurrences. They hold with
periodic forcing too, so they cover the sphere and the general cubic.

**Finite identity.** For every depth n, by induction on n:

    Σ_{m of depth < n} p_m·g_m + Σ_{(L, R) at depth n} [L_p·β(L, R) + R_p·β(R, L)] = N(e₁) − D_{e₀}^{e₁},

and the same with q, N(e₀) and D_{e₁}^{e₀}. The induction step splits (L, R)
at m into (L, m) and (m, R), rewrites coordinates, and uses only Facts 1
and 2.

**Remainder.** Take the torus (no linear terms) with traces > 2.

- The fan around L through R has coefficients K and K′ with K·K′ = G = e^{g_L}
  and K + K′ = b = tr R. Since c_m > tr(R − L), K is the larger root. So,
  exactly,

      β(L, R) = log[(b + √(b² − 4)) / (b + √(b² − 4G))],

  and |β| ≤ C·|G − 1|/b² ≤ C′/(tr L · tr R)².
- Since tr L · tr R ≥ c_m, the depth-n remainder is at most C″·Σ_{m at depth n+1} |m|/c_m².
- Depth classes are disjoint, so this is a tail of Σ_m |m|/c_m². That series
  converges, because traces grow exponentially in |m| on rising trees
  (Bowditch / Fibonacci growth; O'Sullivan Prop. 3.2) and the number of
  primitive m with |m| ≤ R is O(R²).
- So the remainder tends to 0, and the identity holds.

This proves the vector identity, and with it the total identity, for real
tori with any k on rising trees with labels > 2. That includes k > 4 and the
pants orbits.

For the sphere and the general cubic, the finite identity is proved, and the
remainder is seen numerically to decay geometrically. The closed form for β
with forcing has not been written out. For complex traces, the same argument
should go through under Bowditch's conditions; that is not done here.

**Numerical check** (`proof_check.log`, 220 digits).

- Fact 1, Fact 2 and the β closed form are exact to about 10⁻²²⁰.
- The finite identity is exact at every depth from 1 to 12, to about
  10⁻²¹⁶, on five cases: a punctured torus, a one-holed torus at k = −20, the
  Ghosh–Sarnak surface at k = 5, the pants at k = 54, and a four-holed sphere.
- The remainder falls by a factor of 4 to 7 per level. It is positive for
  k < 4 and negative for k > 4.

**Corollary 1 (pure-jump gradient).**

- The gradient of N, as the direction sweeps the cone, is a monotone curve.
  Its change is the sum of its jumps plus a possible continuous part ν.
- The vector identity says the jumps alone add up to the total change, so
  ∫(−sin θ, cos θ) dν = 0.
- All these vectors lie in one open half-plane, because the cone is narrower
  than π. So ν = 0: the gradient changes only by jumps at the rationals.

This is the "purely atomic" property that the earlier sections assumed. It is
now proved wherever the vector identity is (real tori, any k). For cusped
tori it also follows from Doan–Li–Nguyen's Theorem 1.3.

**Corollary 2 (dual-area identity, extended).**

- Since the gradient is pure-jump, B* is swept entirely by the jump
  triangles (0, ∇⁻N(w), ∇⁺N(w)). Each has area g_w·N(w)/2, and corners come in
  pairs ±w. So

      Area(B*) = Σ over simple closed curves γ of g_γ·N(γ),   N = ℓ/2.

- In the norm ℓ (Doan–Li–Nguyen's convention) this is 4·Σ_γ (g_γ/2)·ℓ_γ.
- Cusped tori have g = 2 log coth(ℓ/2), which gives their formula exactly.
- One-holed and cone tori have g = log((c² − μ)/(c² − 4)).
- Four-holed spheres use the sphere gap law.

**Check of Corollary 2** (`dual_area.log`). The direct side is
(1/2)∮ N*(u)⁻² dθ, with N* the dual norm, computed from traces of 5002
primitive vectors only (no fans and no gap law), on a 400 000-point
quadrature.

| Surface | Σ g·N | Direct Area(B*) | Rel. diff |
|---|---|---|---|
| Modular torus | 2.69708988043 | 2.697089880428 | 6e−13 |
| Punctured torus (2.6, 4.1) | 2.67005821681 | 2.670058216806 | 7e−13 |
| One-holed torus μ = −20 | 5.29226592029 | 5.292265920294 | 1e−12 |
| Cone-point torus μ = 1.5 | 2.18640278194 | 2.186402781944 | 2e−12 |
| Four-holed sphere (2.5, 2.2, 3.0, 2.1) | 12.6806292539 | 12.680629253859 | 3e−12 |
| Four-punctured sphere | 10.7883595217 | 10.788359521710 | 6e−13 |

The cone-point torus is included as a surface with a cone singularity; the
proof's convexity input there is assumed from geometry, not proved here.

**Assessment of novelty.**

- The proof idea, telescoping slopes, is O'Sullivan's.
- What is added:
  1. an exact finite identity at every depth;
  2. an exact closed form for the remainder;
  3. the vector (one-coordinate) form;
  4. coverage of forced fans (spheres, the general cubic);
  5. the pure-jump corollary for non-cusped surfaces;
  6. the extension of Doan–Li–Nguyen's dual-area identity to one-holed tori,
     cone tori and four-holed spheres.
- Items 5 and 6 are the most likely to interest specialists. Still to check:
  Doan–Li–Nguyen's §6 (further directions) and anything citing them.

**Doan–Li–Nguyen §6, read.** They name, as further directions, extending
their method to

- hyperbolic one-holed tori and cone tori;
- the four-holed sphere ("forthcoming work");
- the generalised k-Markoff equations of Gyoda–Matsushita,
  x² + y² + z² + k₁yz + k₂zx + k₃xy = (3 + k₁ + k₂ + k₃)xyz.

Corollary 2 above covers the first two, for the dual-area identity. The
Gyoda–Matsushita equations have conic slices with a different quadratic
part, so they are a natural next test of the conic form, using the rescaled
version e^g = −bc·det M₃ / (4(det M₂)²).

## Sphere remainder bound: the proof is complete for four-holed spheres (2026-11-25)

Script `poc/farey/sphere_bound.py`, output `poc/farey/sphere_bound.log`
(1300 digits).

**What changes with forcing.** The fan around L through R is

    t_j = K·λ^j + K′·λ^{−j} + u_j,

where u is the period-2 particular solution. Its value at the R slot is

    u_e = (a·κ(L+R) + 2κ(R)) / (a² − 4),   a = tr L.

**The exact remainder term.** The energy identity gives K·K′ = G = e^{g_L},
and t₀ = b = tr R gives K + K′ = b̃ = b − u_e. K is the larger root, because
c_m > tr(R − L). Hence, exactly,

    β(L, R) = log[ (b + √(b² − 4)) / (b̃ + √(b̃² − 4G)) ].

**The bound.**

- Here u_e = O(1/a) and G − 1 = O(1/a), because the sphere gap law has a
  κ_m/c term. So |β| ≤ C/(a·b), which is one power weaker than the torus.
  The leading term is β ≈ κ(L+R)/(a·b).
- Since a·b = c_m + κ(m) + tr(opposite) ≥ c_m, the depth-n remainder is at
  most C′·Σ_{m at depth n+1} |m|/c_m.
- That is a tail of Σ_m |m|/c_m. The series converges, because traces grow
  exponentially in |m|: ℓ(m) ≥ α·|m| for a hyperbolic structure, and
  c_m ≈ e^{ℓ/2}.
- So the remainder tends to 0, and the vector Hines identity is proved for
  four-holed spheres. That includes cone points of trace in (−2, 2) whenever
  the tree is rising with traces > 2.

**Corollaries 1 and 2 for spheres.**

- These also need the length function N to be convex on the cone. That holds
  for hyperbolic four-holed spheres by Mirzakhani's convexity of length in
  train-track coordinates (as used by Doan–Li–Nguyen, [Mir04, Thm A.1]).
  Every defect computed here is positive.
- With convexity, the pure-jump gradient and the dual-area identity
  Area(B*) = Σ_γ g_γ·N(γ) follow for spheres exactly as for tori.

**Numerical check** (1300 digits; at 120 digits the deepest intervals were
unresolved, since β ≈ 10⁻¹⁰⁰⁰ there):

- The closed form for β is exact to about 10⁻¹²⁹⁸ on every interval to
  depth 12.
- The table shows sup |β|·a·b over all intervals and the ratio of the
  remainder to Σ_{m at depth n+1} |m|/c_m, at depths 2 to 12:

  | Sphere | sup \|β\|·a·b | Remainder ratio |
  |---|---|---|
  | (2.5, 2.2, 3.0, 2.1) | 15.52 | 13.7–13.8 |
  | (2, 2, 2, 2) | 11.2 | 9.5–9.6 |
  | (3, 5, 4, 6) | 44.01 | 43.0–43.1 |

- β·a·b/κ(L+R) lies in [1, 1.28], [1, 1.40] and [1, 1.048] respectively.
  Its infimum is exactly 1, the leading-term prediction, attained deep in
  the tree.

## Gyoda–Matsushita k-Markoff equations are four-holed spheres (2026-11-25)

Script `poc/farey/kmarkoff.py`, output `poc/farey/kmarkoff.log`.

**The substitution.** The equation is

    x² + y² + z² + k₁yz + k₂zx + k₃xy = S·xyz,   S = 3 + k₁ + k₂ + k₃.

Substitute τ_x = Sx − k₁, τ_y = Sy − k₂, τ_z = Sz − k₃. Then:

- The integer Vieta move z ↦ S·xy − k₁y − k₂x − z becomes the mediant rule
  τ_z′ = τ_x·τ_y − (2k₃ + k₁k₂) − τ_z.
- The equation becomes the Fricke cubic of a four-holed sphere with boundary
  traces (α, β, γ, δ) = (k₂, k₃, k₁, 2):
  - p = 2k₁ + k₂k₃ = αβ + γδ, and likewise for q and r;
  - s = Σk_i² + 2k₁k₂k₃ = α² + β² + γ² + δ² + αβγδ − 4.

**What each k_i means.** There is always one cusp. A "boundary" of trace k is:

- k = 0: a cone point of order 2 (k = (0, 0, 0) is the Markoff equation,
  i.e. the modular torus divided by its elliptic involution);
- k = 1: a cone point of order 3;
- k = 2: a cusp (k = (2, 2, 2) is the four-punctured sphere);
- k ≥ 3: a geodesic boundary.

The variable of an integer node is the parity class of its slope.

**Checks**, on seven equations at the smallest solution (1, 1, 1) (gap law
against brute-force integer fans of 80 steps each way):

| k | τ root | Gap-law error | Vector Hines (p, q) errors | Dual-area rel. diff |
|---|---|---|---|---|
| (0, 0, 0) | (3, 3, 3) | 1e−67 | 3e−69 | 6e−13 |
| (1, 1, 1) | (5, 5, 5) | 2e−55 | 3e−55 | 6e−13 |
| (2, 2, 2) | (7, 7, 7) | 9e−68 | 6e−69 | 6e−13 |
| (1, 2, 3) | (8, 7, 6) | 1e−72 | 2e−72 | 5e−13 |
| (0, 0, 5) | (8, 8, 3) | 8e−73 | 2e−76 | 4e−12 |
| (3, 3, 3) | (9, 9, 9) | 9e−77 | 5e−79 | 3e−13 |
| (0, 1, 4) | (8, 7, 4) | 8e−73 | 3e−73 | 8e−13 |

The conic-invariant form agrees with the sphere law in every case. The two
components of the vector identity differ for the asymmetric (1, 2, 3) and
(0, 1, 4).

**Literature.**

- **The sphere identification is known.** Banaian–Gyoda (arXiv 2507.06900,
  eq. at their line 138) write exactly this Fricke form, coefficients
  included. Gyoda (arXiv 2611.23868, November 2026) realises the equations
  on a hyperbolic orbifold on a sphere with four marked points. He applies
  the Tan–Wong–Zhang McShane identity there to Lagrange-spectrum gaps,
  extending Gaster–Loustau. Banaian–Sen (2210.07366) and Gyoda–Matsushita
  (2201.10919) give the cluster-algebra and orbifold picture.
- **The rest is not found there.** None of these has slope gaps of the
  length function, Hines-type or vector identities, the dual-area identity,
  or the conic form. Gyoda's "gaps" are Lagrange-spectrum gaps, which are a
  different object.
- So on these orbifolds the following are new, as far as checked: the gap
  law, the vector Hines identity, and the dual-area identity
  Area(B*) = Σ g_γ·N(γ).
- This also answers the Gyoda–Matsushita direction named in
  Doan–Li–Nguyen §6.

## The rate law explained, and refined for mixed parity classes (2026-11-25)

Script `poc/farey/rate_classes.py`, output `poc/farey/rate_classes.log`
(400 digits for the refinement runs, 700 for the cell-by-cell check).

**Why ζ(2) appears.** The law c²A = κ²ζ(2) is a primitive-lattice-point count
in disguise. Primitive vectors have density 6/π² = 1/ζ(2) in Z², and
best-first refinement refines, up to a logarithmic band, exactly the
primitive vectors m whose decay exponent κ·N(m) is below a threshold L. The
error is then E_N = e^{−L}.

**Proof sketch.**

1. **Detail asymptotics.**
   - *Torus.* The hyperbolic cosine rule for once-crossing geodesics, with
     crossing angle θ, gives cosh N(L+R) = cosh N(L)·cosh N(R) + sinh N(L)·sinh N(R)·cos θ.
     Here sin²θ = 4(4 − μ)/((a² − 4)(b² − 4)). This gives
     D = Θ((4 − μ)·e^{−2N(m)}), so κ = 2.
   - *Sphere, mediant class coefficient κ_m ≠ 0.* The mediant rule
     c = ab − κ_m − o gives D ≈ κ_m/(ab) = Θ(e^{−N(m)}), so κ = 1.
   - *Sphere, κ_m = 0, at least one neighbour class nonzero.* The product
     relation c·o = a² + b² + κ_a·a + κ_b·b + s gives D ∋ κ_a/(a·b²). So
     −log D = N(m)·(1 + ρ) + O(1), where:
     - ρ = N(zero-class endpoint)/N(m), if exactly one endpoint class is
       nonzero;
     - ρ = min(N(L), N(R))/N(m), if both are.
2. **Distribution of ρ.** For primitive m, the Farey parents have
   denominators q′ ≡ ±p⁻¹ (mod q), and these are equidistributed. The parents
   also converge in direction to m, so N(parent)/N(m) ≈ q′/q. Hence:
   - ρ is uniform on (0, 1) for "the parent of a given class", since that
     parent is equally likely to be the larger or the smaller;
   - ρ is uniform on (0, 1/2) for the smaller parent.
3. **Counting.**
   - The number of primitive m in the cone with N(m) ≤ X is
     (6/π²)·A·X² + O(X log X), where A is the area of the norm ball in the
     cone.
   - These are split equally among the three classes mod 2.
   - Class i contributes (1/3)(6/π²)·A·L²·w_i, where
     w_i = E[(κ_i(1 + ρ))⁻²]-type weights:

     | Class | Weight w_i |
     |---|---|
     | Coefficient ≠ 0 | 1 |
     | Coefficient = 0, all coefficients zero (torus) | 1/4 |
     | Coefficient = 0, one neighbour class nonzero | E[(1 + ρ)⁻²] with ρ ~ U(0, 1), = 1/2 |
     | Coefficient = 0, both neighbours nonzero | E[(1 + ρ)⁻²] with ρ ~ U(0, 1/2), = 2/3 |

4. **Inverting the count:**

       log E_N = −c·√N + O(log N),   c²·A = 3ζ(2) / Σ_i w_i.

**Predictions against the earlier law.**

| Class pattern | Example | Σw | Refined law | Earlier law (wrong for mixed) |
|---|---|---|---|---|
| All zero | torus | 3/4 | 4ζ(2) = 6.580 | 6.580 |
| All nonzero | four-punctured sphere, k-Markoff (1, 2, 3) | 3 | ζ(2) = 1.645 | 1.645 |
| (0, 0, ≠0) | k-Markoff (0, 0, 5), (0, 0, 1) | 2 | (3/2)ζ(2) = 2.467 | 3.290 |
| (0, ≠0, ≠0) | cubic (p, q, r) = (0, 3, 5) | 8/3 | (9/8)ζ(2) = 1.851 | 2.193 |

**Measured** (best-first runs of 9000 cells; fits of log E_N on
[1, √N, log N] over two windows):

| Case | c²A, N in [1000, 5000) | c²A, N in [3000, 9000) | Refined law |
|---|---|---|---|
| Torus | 6.619 | 6.459 | 6.580 |
| Four-punctured sphere | 1.655 | 1.615 | 1.645 |
| k-Markoff (1, 2, 3) | 1.650 | 1.622 | 1.645 |
| k-Markoff (0, 0, 5) | 2.457 | 2.520 | 2.467 |
| k-Markoff (0, 0, 1) | 2.457 | 2.515 | 2.467 |
| Cubic (0, 3, 5) | 1.834 | 1.816 | 1.851 |

All agree to within about 2%, which is the same spread as the uniform cases
and comes from the O(log N) term. The earlier law misses the mixed cases by
25% and 18%.

**Cell-by-cell check of step 1.** (−log D − predicted exponent)/N(m) over all
cells at depths 8 to 12:

| Case | Mean | Max \|·\| | Cells |
|---|---|---|---|
| k-Markoff (0, 0, 5) | −0.012 | 0.13 | 3968 |
| Cubic (0, 3, 5) | −0.007 | 0.08 | 3968 |
| Torus | −0.017 | 0.18 | 3968 |
| Four-punctured sphere | −0.013 | 0.13 | 3968 |

These are O(1)/N(m), with no class-dependent bias.

**Status.** Step 1 is proved for the torus. For the sphere it is derived from
the product relation, with the constants not made uniform. Step 2 is the
classical equidistribution of modular inverses, plus convergence of parent
directions. Step 3 is standard for convex regions. The band argument for
best-first order is a sketch. So: a theorem up to routine uniformity
estimates, with the mixed-class constants (3/2)ζ(2) and (9/8)ζ(2) as
genuinely new predictions, confirmed numerically.

**Note.** The fitted log N coefficient varies between −1.9 and +1.0 across
windows and cases. It is not stable enough to identify, and the proof gives
only O(log N).

## Closed-form search for the dual area (2026-11-25)

Script `poc/farey/dual_closed.py`, output `poc/farey/dual_closed.log`
(140 digits).

**Setup.** On the modular torus, sum over all simple closed geodesics mod
sign. That is e₀, e₁ and the interiors of the cones (e₀, e₁) and (e₀, −e₁):
46 440 curves, best-first, until terms fall below 10⁻¹²⁵.

**Controls.**

- McShane's identity over the same set gives Σh = 1/2 to 2·10⁻¹²⁸, and PSLQ
  returns it as 1/2.
- F(3) is recovered as log λ, with λ = (3 + √5)/2.

**Constants:**

    A* = Area(B*) = Σ_γ g_γ·N_γ = 2.69708988042923281133551647802882...
    Area(B)                     = 3.56721266403154336675263074793896677798...

Area(B) is the area of the polygon through the corners ±v/N(v). Moving the
tolerance from 10⁻¹²⁵ to 10⁻⁹⁵ changes it by 10⁻¹⁰¹. For the norm ℓ, as
Doan–Li–Nguyen use, multiply A* by 4.

**PSLQ basis.** 19 elements: 1, π², ζ(3), log λ, log²λ, log³λ, √5, √5·log λ,
√5·log²λ, π²·log λ, log 2, log 3, log 5, Li₂(λ⁻²), Li₃(λ⁻²), Li₂(λ⁻¹),
Catalan's constant, π and π²·√5. Coefficients up to 10⁴, at 115 digits.

- **No relation** for any of these sums: A*, Σg, Σg·N², Σh·N, ΣN/c², or
  ΣLi₂(4/c²).
- **Area(B), Area(B)·A*, A*/Area(B) and 1/Area(B)**, against a 15-element
  basis including 1/log λ and √5/log λ: no relation. At 85 digits one
  15-term relation with coefficients near 4000 appeared for A*/Area(B). At
  100 digits it disappears, so it was spurious.

**By-products.**

- **Sphere and torus.** A*(four-punctured sphere at (7, 7, 7)) = 4·A*(modular
  torus), to 40 digits. This is a scaling, not an identity: the sphere traces
  are t² − 2 of the torus traces, so N_sphere = 2·N_torus and B*_sphere =
  2·B*_torus.
- **Mahler volume.** Area(B)·Area(B*) = 9.62109317749848... For centrally
  symmetric planar convex bodies the Mahler bound gives 8 and Blaschke–Santaló
  gives π² = 9.8696 (ellipses). The modular norm ball reaches 0.97482 of the
  Santaló maximum, so it is close to an ellipse in this sense.

**Reading.** McShane's and Hines' identities have closed forms because each is
a telescoping or boundary sum. The dual area weights each corner by N(γ),
which is not linear, so no telescoping applies. The negative PSLQ result fits
that: A* behaves like a genuinely new constant of the modular torus. It is not
proved to be new, only shown not to be a small combination of these
constants.

## Extremal properties over the moduli space of cusped tori (2026-11-25)

Script `poc/farey/moduli_mahler.py`, output `poc/farey/moduli_mahler.log`
(40 digits; tail 10⁻³⁰).

**Quantities.** All three are invariant under change of homology basis (SL₂(Z)):

- Area(B), the area of the stable-norm ball;
- Area(B*) = Σ g·N, the dual area;
- the Mahler volume Area(B)·Area(B*).

The Mahler volume is also affine-invariant. For centrally symmetric planar
bodies it lies between 8 (parallelograms) and π² (ellipses).

**Domain.** The fundamental domain of Markoff triples a² + b² + c² = abc is

    2 < a ≤ 3,   max(a, 2a/√(a² − 4)) ≤ b ≤ a/√(a − 2),

with c the smaller Vieta root. I sampled 466 points, plus both boundary edges.

**Results.**

| Quantity | Extremum at the modular torus (3, 3, 3) | Opposite extreme among the 466 points |
|---|---|---|
| Area(B) | minimum, 3.567213 | 6.538 at (2.02, 14.25, 14.39) |
| Area(B*) | maximum, 2.697090 | 1.391 at (2.02, 14.25, 14.39) |
| Mahler volume | maximum, 9.621093 = 0.97482π² | 9.093 at (2.02, 14.25, 14.39) |

The opposite extremes all sit at the sample point nearest a → 2.

- **Square torus** (2√2, 2√2, 4): Area(B) = 3.578123, Area(B*) = 2.687102,
  Mahler volume 9.614781 = 0.97418π². That is below the modular torus.
- **Along the edge b = a**, from the modular point to the square point: all
  three quantities are monotone. The Mahler volume falls from 9.621093 to
  9.614781. Near the modular point the change is quadratic: −7·10⁻⁵ at
  Δa = 0.02 and −4.5·10⁻⁴ at Δa = 0.05. So this is a smooth extremum at the
  hexagonal orbifold point, not a corner of the sampling. The other edge,
  b = a/√(a − 2), behaves the same way.
- **Degeneration a → 2** (a geodesic pinching):

  | a | Mahler volume |
  |---|---|
  | 2.3 | 9.533 |
  | 2.1 | 9.351 |
  | 2.03 | 9.152 |
  | 2.01 | 9.004 |
  | 2.003 | 8.875 |

  The volume decreases towards 8, the parallelogram value. This is expected:
  as ℓ(α) → 0, N(p, q) ≈ |i(·, α)|·2 log(1/ℓ_α) + |p|·ℓ_α, which is an
  ℓ¹-type norm, so the normalised ball tends to a parallelogram.

**Statements, numerical and not proved:**

1. The modular torus minimises the area of the stable-norm ball. This was
   seen earlier, and is now confirmed on a dense sample.
2. The modular torus maximises the dual area Σ_γ ℓ_γ log coth(ℓ_γ/2) (times
   the normalisation). This is Doan–Li–Nguyen's McShane-type sum, so it is a
   statement about a McShane-type sum over the simple length spectrum.
3. The modular torus maximises the Mahler volume, at 0.97482π². The infimum
   over moduli is 8, approached at the boundary and not attained.

The symmetry of the hexagonal point forces it to be a critical point; that it
is the global extremum is the content of these statements. They sit
alongside Schmutz Schaller's theorem that the modular torus maximises the
systole. Statement 2 says the McShane-type sum Σ ℓ log coth(ℓ/2) is largest
where the spectrum is "most spread out". Literature status: not checked. A
search on stable-norm extremal problems (Massart and others) is the next step
before calling these new.

## Limits: flat, tropical, pinching (2026-11-25)

Script `poc/farey/limits.py`, output `poc/farey/limits.log` (double precision;
curves best-first until g·N < 10⁻¹³, up to 108 504 curves).

### Flat limit, μ → 4

This is the cone-point limit: cone angle 2π − δ, where δ is the hyperbolic
area and μ − 2 = 2 cos(δ/2).

**Predictions.** 4 − μ ≈ δ²/4, and lengths are √δ times flat lengths. Then:

- the dual-area sum Σ g·N becomes a Riemann sum of r/(4 sinh²r) over primitive
  vectors. With density 6/π² and ∫₀^∞ r²/sinh²r dr = π²/6, this gives
  A* → π·δ/4;
- Area(B) → 4π/δ (a Euclidean disk);
- the Mahler volume → π², the ellipse value.

**Measured.**

| Case | Mahler/π² | A*/(πδ/4) | Area(B)/(4π/δ) |
|---|---|---|---|
| (a, a, a), a = 2.6 | 0.98417 | 0.864 | 1.139 |
| (a, a, a), a = 2.1 | 0.99807 | 0.991 | 1.007 |
| (a, a, a), a = 2.01 (32 616 curves) | 0.999923 | 0.99969 | 1.00023 |
| Asymmetric lattice, ε = 0.04 (108 504 curves) | 0.999991 | 0.99996 | — |

In this limit the dual-area identity reduces to ∫ r²/sinh²r = ζ(2). The same
ζ(2) appears in the rate law.

### Tropical limit, μ → −∞

This is the long-boundary limit. The surface collapses onto a theta ribbon
graph with edge lengths l₁, l₂, l₃, where log a = l₁ + l₃, log b = l₂ + l₃ and
log c = l₁ + l₂ (c the trace of e₀ − e₁).

**Predictions.**

- N(p, q) → l₁|p| + l₂|q| + l₃|p − q|, a piecewise-linear norm.
- B tends to a hexagon, and B* to the zonotope Σ l_i·[−u_i, u_i], of area
  4(l₁l₂ + l₁l₃ + l₂l₃).
- **The gap law tropicalises:** g(e₀) = log((a² − μ)/(a² − 4)) → 2l₂, and
  similarly g(e₁) → 2l₁ and g(e₀ − e₁) → 2l₃. Only these three corners
  survive. The dual-area identity becomes
  Σ g·N = 2l₂(l₁ + l₃) + 2l₁(l₂ + l₃) + 2l₃(l₁ + l₂) = 4Σ_{i<j} l_i l_j,
  which is exactly the zonotope area.

**Measured, symmetric case** (a, a, a), with l = log(a)/2:

| a | Mahler | Area(B)·l² | A*/l² | g(e₀)/(2l) |
|---|---|---|---|---|
| 6 | 9.2916 | 0.80407 | 11.5556 | 0.83944 |
| 100 | 9.0096 | 0.75084 | 11.99942 | 0.99570 |
| 10⁵ | 9.000004 | 0.75000 | 12.00000 | 1.00000 |
| Regular-hexagon prediction | 9 | 0.75 | 12 | 1 |

**Measured, asymmetric shapes** (log-trace ratios scaled by a growing factor):

| Shape | Theta lengths at the largest scale | Mahler | Hexagon prediction |
|---|---|---|---|
| (1, 1.5, 2.2) | (51, 81, 9) | 8.417273 | 8.417273 |
| (1, 3, 3.5) | (45, 165, 15) | 8.392869 | 8.392857 |

In both shapes g(e₀)/(2l₂) and g(e₁)/(2l₁) reach 1.00000.

**Hexagon Mahler volume over theta shapes.** It ranges over (8, 9]: the
maximum 9 at l₁ = l₂ = l₃ (the regular hexagon), and the infimum 8 as two
lengths go to 0 (the parallelogram).

### Pinching, a → 2 at μ = 0

| ℓ(α) | 0.20 | 0.11 | 0.063 | 0.035 |
|---|---|---|---|---|
| Mahler | 9.0036 | 8.8753 | 8.7826 | 8.7007 |

The Mahler volume decreases towards 8, but slowly. (M − 8)·log(1/ℓ) grows from
1.62 to 2.36, so the decay is slower than 1/log(1/ℓ). The exact rate was not
identified.

### Picture

Along the symmetric family (a, a, a), the Mahler volume of the stable-norm
ball rises monotonically with μ:

| μ | −10¹⁵ | −108 | 0 (modular) | 2.70 | → 4 |
|---|---|---|---|---|---|
| Mahler | 9 | 9.29 | 9.621 = 0.9748π² | 9.71 | π² |

So it interpolates between three geometries:

- **tropical:** a hexagon, values in [8, 9];
- **hyperbolic:** the modular torus, which maximises among cusped tori;
- **Euclidean:** the flat torus, an ellipse at π².

Pinching sends it to 8. Each limit matches its predicted body exactly: the
gap law tropicalises to the theta-graph edge lengths, and the dual-area
identity becomes the zonotope area in one limit and ζ(2) in the other.

## Going complex: holomorphic continuation and its limits (2026-11-25)

Script `poc/farey/complex_limits.py`, output `poc/farey/complex_limits.log`
(double precision complex).

**Setup.** With complex traces (quasi-Fuchsian characters), use the complex
length N = arccosh(t/2) = (length + i·twist)/2 in place of N. Three quantities
then become holomorphic in the traces wherever the tree sums converge:

- the dual area A* = Σ g·N;
- the polygon formula Area(B) = ½ Σ cross(v_i, v_{i+1}) / (N_i·N_{i+1}), with
  the v_i in angular order;
- the Mahler product M = Area(B)·A*.

**The branch matters.** Complex length is only defined modulo 2πi, and
g = log(·) is defined modulo 2πi as well.

- With principal branches, long curves have their twist wrapped back into
  (−π, π].
- The dual area barely notices, because long curves carry tiny g. Area(B)
  weights every curve's 1/N² equally, so it does notice.
- The first run, with principal branches, gave M/π² stuck at
  0.85 + 0.63i (φ = 0.8) and 0.63 + 1.00i (φ = 1.2) in the complex flat limit.
  It gave A*/zonotope stuck at 0.93 − 0.17i in an asymmetric complex tropical
  case, where the true gap 2l₂ = 108 − 16i had its imaginary part wrapped.

**The fix.** Quasi-Fuchsian space is contractible, so each N_γ and g_γ has a
unique holomorphic continuation from the Fuchsian locus. The script tracks it
along a path from a real point, choosing the nearest of ±N + 2πik and
g + 2πik at each step.

### Results with the continuation

**Complex flat limit.** a = 2 + r·e^{iφ} for symmetric (a, a, a), with
μ − 2 = 2 cos(δ/2) and δ complex.

| φ | r | M/π² | A*/(πδ/4) | Area(B)·δ/(4π) |
|---|---|---|---|---|
| 0.4 | 0.01 | 0.999935 − 0.000043i | 0.999744 − 0.000173i | 1.000191 + 0.000131i |
| 0.8 | 0.01 | 0.999969 − 0.000072i | 0.999885 − 0.000287i | 1.000084 + 0.000216i |
| 1.2 | 0.01 | 1.000014 − 0.000078i | 1.000067 − 0.000303i | 0.999947 + 0.000225i |

The holomorphic Mahler function tends to π² at the flat point μ = 4 from
every complex direction tested. A* ≈ πδ/4 and Area(B) ≈ 4π/δ hold with δ the
complex "area".

**Complex tropical limit.** The log-traces carry imaginary parts (twists),
switched on along the path. The theta lengths l_i are complex.

| Shape | Scale | g(e₀)/(2l₂) | A*/zonotope | M | Hexagon formula |
|---|---|---|---|---|---|
| (1 + 0.3i, 1.5 − 0.2i, 2.2 + 0.1i) | 15 | 0.99973 | 1.000000 | 8.425409 − 0.005184i | 8.424236 − 0.005140i |
| (1 + 0.3i, 1.5 − 0.2i, 2.2 + 0.1i) | 40 | 1.000000 | 1.000000 | 8.424236 − 0.005140i | 8.424236 − 0.005140i |
| (1 + 0.8i) all equal | 15 | 1.000000 | 1.000000 | 9.000000 | 9 |

In this limit the gap law becomes g → 2l_i with complex l_i, the length plus
twist of each theta-graph edge. The dual area becomes the complex zonotope
area 4Σ l_i l_j, and the Mahler function becomes the hexagon formula, a
degree-0 rational function of complex edge lengths. So complex Mahler values
such as 8.424 − 0.005i are genuine values of the continuation.

The symmetric shape (1 + 0.8i) at scale 40 overflowed double precision
(traces near e⁴⁰ with large twists; the curve set hit its 400 000 cap). That
line is a numerical failure, not a result.

### Reading

- The real picture survives complexification intact, as holomorphic
  functions on quasi-Fuchsian space:
  - at the flat point μ = 4 the Mahler function is pinned to π², the
    Blaschke–Santaló constant;
  - at the tropical end it becomes a rational function of complex edge
    lengths;
  - the dual-area identity still reduces to ζ(2) in the flat limit and to the
    zonotope area in the tropical one.
- The only subtlety is the branch. The identities hold for the continuation
  from the Fuchsian locus, not for principal values. That is the same
  phenomenon as the complex-length ambiguity in quasi-Fuchsian geometry.
- **Not done yet:** mapping where the continuation stops converging in a
  one-parameter complex slice. That is the boundary of quasi-Fuchsian space
  (fractal), together with how A* and M behave there.

## The edge of quasi-Fuchsian space (2026-11-25)

Scripts `poc/farey/qf_slice.py` (figure `docs/figures/qf_slice.png`) and
`poc/farey/qf_boundary.py`, with logs.

**Slice.** Cusped characters (μ = 0) with tr e₀ = 3 and b = tr e₁ complex.
The modular torus is the point b = 3, and the Fuchsian locus is the real ray
b ≥ 6/√5. The figure shades the points that pass a depth-11 Bowditch test and
colours them by Re A* (principal branches, accurate near the real locus). The
half-plane Re b < 0 is a mirror copy (b ↦ −b, a sign change of the lift); it
is omitted because principal branches give N(−t) = iπ − N(t) there.

- The region has the expected scalloped, self-similar boundary.
- A* is smooth inside. It is lighter (smaller) at the inward cusps of the
  boundary and darker along its convex parts.
- The depth-limited test is conservative: its boundary moves inward with
  depth and growth threshold (1.835 at depth 11, 1.668 at depth 14 on the
  vertical ray). The figure says so.

**True boundary along rays.** Locate it where some simple curve's trace
actually reaches [−2, 2].

- **Vertical ray.** The exit is exactly b = 3 + 2i, where c = tr(e₀ − e₁) = 2,
  since b² − 6b + 13 = 0. The curve e₀ − e₁ becomes an accidental parabolic,
  so this is a cusp point of the boundary. The real-axis cusp is b = 2, where
  e₁ is parabolic.
- **Generic rays** leave the region where no single trace hits [−2, 2], as
  expected: generic boundary points are degenerate, not cusps. On the 120°
  ray the first exact crossing found, at distance 3.26, lies well beyond the
  growth-test boundary at about 1.65.

**Approach to a cusp is complex pinching.** Holomorphic continuation along
the straight path from b = 3:

| Fraction of the way | 3 + 2i: N(e₀ − e₁) | A* | M | b = 2 (real): N(e₁) | A* | M |
|---|---|---|---|---|---|---|
| 0.90 | 0.293 − 0.129i | 2.1237 − 0.3871i | 9.3147 − 0.1784i | 0.315 | 2.0904 | 9.3071 |
| 0.97 | 0.159 − 0.073i | 1.5338 − 0.3873i | 9.0602 − 0.1706i | 0.173 | 1.5428 | 9.0610 |
| 0.99 | 0.092 − 0.043i | 1.0768 − 0.3181i | 8.21 + 0.39i (unreliable) | 0.100 | 1.0996 | 8.8520 |
| 0.995 | — | — | — | 0.071 | 0.8688 | 8.7239 |

At equal pinched length the complex approach tracks the real one closely:
A* to within 2% in modulus, and M to 0.001 at 0.97.

- **The dual area goes to zero.** A* ≈ 4.7·N·log(1/N) on the real side: the
  ratio is 4.78 at N = 0.1, 4.65 at N = 0.071, and 4.69 from the earlier
  pinching run. The pinched curve's own corner contributes g·N ≈ 2N·log(1/N);
  curves crossing it supply the rest.
- **The Mahler function tends to 8,** the parallelogram value, as in real
  pinching.
- Beyond 0.99 of the way, double precision fails: traces overflow, and the
  fans around a nearly parabolic curve grow too slowly for the curve cap. The
  complex M at 0.99 jumps in its imaginary part and is marked unreliable.

**Picture of the continuation.**

- Inside quasi-Fuchsian space, the dual area and the Mahler function are
  holomorphic.
- At the flat point they are pinned to πδ/4 and π².
- At the tropical end they become rational functions of complex theta lengths.
- At cusp points of the boundary they degenerate exactly as in real pinching:
  A* → 0 like N·log(1/N), and M → 8.
- At generic (degenerate) boundary points, behaviour was not resolved here:
  infinitely many curves shorten and double precision is not enough.

## Weil–Petersson averages of the dual area (2026-11-25)

Scripts `poc/farey/wp_average.py` (tori) and `poc/farey/wp_average_sphere.py`
(spheres), with logs.

**Principle.** The dual area is a sum over simple closed curves,
A* = Σ_γ g_γ·N_γ with N = ℓ/2 (the extended Doan–Li–Nguyen identity), so
Mirzakhani's integration formula applies.

### One-holed tori (boundary L; L = 0 is cusped)

**The gap law in length form.** With μ = 2 − 2cosh(L/2),

    e^g = (cosh ℓ + cosh(L/2))/(cosh ℓ − 1) = cosh((ℓ+y)/2)·cosh((ℓ−y)/2)/sinh²(ℓ/2),   y = L/2.

**Unfolding.** There is one mapping-class orbit of simple curves, the
stabiliser is the Dehn twist, and the pants volume V₀,₃ = 1. So

    ∫ A* = ∫₀^∞ (ℓ²/2)·log((cosh ℓ + cosh y)/(cosh ℓ − 1)) dℓ.

**Closed form.** Write log cosh u = |u| − log 2 + log(1 + e^{−2|u|}) and
log sinh u = u − log 2 + log(1 − e^{−2u}). The integral splits into four
pieces:

| Piece | Value |
|---|---|
| Polynomial part | y⁴/24 |
| The two log(1 + e^{−u}) terms combined | (7/4)ζ(4) + π²y²/12 |
| The log(1 − e^{−ℓ}) term | 2ζ(4) |

So

    ∫_{M₁,₁(L)} A* = L⁴/384 + π²L²/48 + π⁴/24 = (L² + 4π²)²/384    (fundamental-domain normalisation),

and with Vol = (L² + 4π²)/24 = 2V₁,₁(L):

    **average A* = (L² + 4π²)/16 = 3·V₁,₁(L)**;  equivalently ∫ A* = 3·V₁,₁(L)² in Mirzakhani's orbifold normalisation.

**Consistency.**

- Cusped tori: the average is π²/4 = 2.4674, below the modular torus's 2.6971,
  as it should be if the modular torus is the maximum.
- Cone tori: put L = iθ. The average (4π² − θ²)/16 vanishes at θ = 2π, the
  flat limit, where A* ≈ πδ/4 → 0.

**Independent check.** Integrate over a fundamental domain in
Fenchel–Nielsen coordinates (ℓ, τ) of a curve α, with ω = dℓ∧dτ (Wolpert),
D = {α is the systole, |τ| ≤ ℓ/2}. The traces are a = 2cosh(ℓ/2) and
b = C·cosh(τ/2), with C = 2√((a² − μ)/(a² − 4)). This satisfies the trace
relation for every τ, and τ ↦ τ + ℓ is the Dehn twist. For μ = 0 it is the
classical cosh(ℓ_β/2) = cosh(τ/2)·coth(ℓ_α/2), which reproduces the modular
torus at ℓ = 2 arccosh(3/2), τ = ℓ/2. Quadrature uses 48 × 20 Gauss nodes,
and every A* is summed until terms fall below 10⁻¹².

| L | Vol (predicted) | ∫ A* (predicted) | Average (predicted) |
|---|---|---|---|
| 0 | 1.646192 (1.644934) | 4.062090 (4.058712) | 2.467568 (2.467401) |
| 2 | 1.814542 (1.811601) | 4.931583 (4.922846) | 2.717812 (2.717401) |
| 5 | 2.694784 (2.686601) | 10.863418 (10.826735) | 4.031275 (4.029901) |

The 0.08–0.18% excess in both Vol and ∫A* is the same quadrature error at the
curved edge of the domain. It cancels in the average, which agrees to
0.007%, 0.015% and 0.034%. The edge error grows with L, as the domain's
boundary curve lengthens.

### Four-holed spheres (boundary lengths L₁, …, L₄)

**Factorisation of the gap law.** For a curve of length x separating {1, 2}
from {3, 4}, the sphere gap law factors with one factor per pair of pants
bounded by the curve:

    e^g = P(x; L₁, L₂)·P(x; L₃, L₄),
    P(x; A, B) = (cosh(x/2) + cosh((A+B)/2))·(cosh(x/2) + cosh((A−B)/2)) / sinh²(x/2).

The worst relative error over 2000 random (x, L) is 6·10⁻¹³, so this is an
identity of the Fricke-cubic gap law.

**Unfolding.** The three mapping-class orbits are the three pairings, which
are the parity classes. Both pants have volume 1. So

    ∫ A* = Σ over pairings, Σ over the two pairs (A, B), of 4[K((A+B)/2) + K((A−B)/2)],
    K(y) = ∫₀^∞ u²·log((cosh u + cosh y)/sinh u) du = y⁴/12 + π²y²/6 + π⁴/24.

K(y) is computed by the same series method as the torus. Each pair i < j
appears exactly once across the pairings, so the cross terms complete a
square:

    ∫_{M₀,₄(L)} A* = (ΣL_i² + 4π²)²/8 = V₀,₄(L)²/2,
    **average A* = (ΣL_i² + 4π²)/4 = V₀,₄(L)/2**   (V₀,₄ = (ΣL_i² + 4π²)/2, Mirzakhani).

**Independent check.** Integrate over a fundamental domain, with one
Fenchel–Nielsen chart per pairing.

- For the class (1, 0) curve α with X = 2cosh(x/2), the transverse traces are
  Y = u_e + 2√G·cosh τ and tr(α ± β) = u_o + 2√G·cosh(τ ± x/2). Here
  G = e^{g_α} and u is the period-2 particular solution of the fan.
- τ ↦ τ + x is the Dehn twist, which is two fan steps.
- The chart satisfies the Fricke cubic and the Vieta relation to 2·10⁻¹⁶.
- The domain is |τ| ≤ x/2, with α shorter than its three transverse
  neighbours. Quadrature uses 40 × 16 nodes per chart.

| Boundary lengths | Vol (predicted) | ∫ A* (predicted) | Average (predicted) |
|---|---|---|---|
| (0, 0, 0, 0) | 19.733814 (19.739209) | 194.760017 (194.818182) | 9.869355 (π² = 9.869604) |
| (1, 2, 0.5, 1.5) | 23.519627 (23.489209) | 276.263000 (275.871465) | 11.746062 (11.744604) |
| (3, 0, 2, 4) | 34.272215 (34.239209) | 586.788750 (586.161710) | 17.121413 (17.119604) |

The volume agrees within 0.13%, which also confirms the domain and the
normalisation. The averages agree within 0.013%.

**Consistency.** The four-punctured sphere's average, π², is 4 times the
cusped torus's π²/4. That matches the factor 4 between the modular torus and
the (7, 7, 7) sphere, which comes from the double cover (lengths double, so
the dual ball doubles and its area scales by 4).

### Summary

| Surface | Average dual area over moduli space |
|---|---|
| Cusped tori | π²/4 |
| One-holed tori | (L² + 4π²)/16 = 3·V₁,₁(L) |
| Four-holed spheres | (ΣL_i² + 4π²)/4 = V₀,₄(L)/2 |

In both families, ∫ A* is a constant times the square of the Weil–Petersson
volume polynomial. Both formulas are proved, given the dual-area identity
(Corollary 2) and Mirzakhani's integration formula, and both are checked
independently by direct integration over a fundamental domain.

**Literature.** Doan–Li–Nguyen prove the dual-area identity at a single
cusped torus and do not average it. Mirzakhani's method is standard. I have
not seen these averages, or the pants factorisation of the gap, stated
anywhere; not searched beyond the papers already read.

## Higher genus: twist gaps are sums of orthogeodesic terms (2026-11-25)

Script `poc/farey/twist_gap.py`, output `poc/farey/twist_gap.log` (80 digits).

**The gap laws are orthogeodesic formulas.**

- **Torus.** In a one-holed torus with boundary L, the orthogeodesic d from α
  back to itself satisfies sinh(ℓ_α/2)·sinh(d/2) = cosh(L/4). Hence
  cosh²(d/2) = (cosh ℓ + cosh(L/2))/(cosh ℓ − 1) = e^g, exactly the torus gap
  law. This also gives the Fenchel–Nielsen formula used earlier:
  cosh(ℓ_β/2) = cosh(d/2)·cosh(τ/2), with C/2 = cosh(d/2).
- **Pants.** P(x; A, B) = cosh²(d/2), where d is the return orthogeodesic of
  the cuff x around the pants. This was checked to 20 digits on two surfaces:

  | Surface | P(x; L₁, L₂) | cosh²(d/2) |
  |---|---|---|
  | S1 | 8.2895832197961887879 | 8.2895832197961887879 |
  | S2 | 2.7290892316588561289 | 2.7290892316588561289 |

  So the four-holed-sphere factorisation e^g = P·P says the gap is a product
  of cosh²(d/2) over the two arcs of the transverse curve, one in each pair of
  pants.

**General statement (any surface, any closed geodesic β).** Let γ be a simple
closed geodesic, and cut β at γ into arcs a₁, …, a_m (m = i(γ, β)), with
orthogeodesic lengths d_j in each arc's class. Then

    lim_{k→∞} [ℓ(T_γ^k β) + ℓ(T_γ^{−k} β) − 2k·m·ℓ_γ] = 4·Σ_j log cosh(d_j/2).

**Proof sketch.** In trace terms, T^kβ is a product of factors γ^k·z_j·γ^{−k}.
As k → ∞ each γ^{±k} is e^{kℓ/2} times a rank-one projector onto γ's fixed
points. The matrix coefficient of the piece z_j between γ's attracting and
repelling eigenvectors equals cosh(d_j/2), since z_j moves the axis of γ to
an axis at distance d_j along a common perpendicular. The trace is therefore
e^{kmℓ/2}·Π_j cosh(d_j/2)·(1 + o(1)), and the same holds for −k. The
single-arc case is the classical quadrilateral formula, so the statement may
well be folklore. Literature not checked: an arXiv search returned nothing
for these phrasings.

**Test surface.** A five-holed sphere: the orientation-preserving subgroup
of the reflection group in five disjoint geodesics of the disc (the double of
a right-angled decagon). Boundary loops are a_i = r_i·r_{i+1}, with
a₁a₂a₃a₄a₅ = ±I to 5·10⁻⁷⁸. The twisting curve is γ = a₁a₂, separating holes
{1, 2} from {3, 4, 5}, and the Dehn twist conjugates the {1, 2}-side pieces by
γ^k. The test curves include:

- a simple curve around holes 2 and 3;
- curves crossing γ four times;
- non-simple curves whose arcs wander through the three-holed side, which is
  not a pair of pants adjacent to γ.

**Results**, two surfaces (S1 with ℓ_γ = 6.431, S2 with ℓ_γ = 9.675). The
twist gap at k = 2, 5, 10, 20 against the orthogeodesic sum:

| β | Arcs | S1 at k = 10 | S1 orthogeodesic sum | S2 at k = 10 | S2 orthogeodesic sum |
|---|---|---|---|---|---|
| a₂·a₃ (simple) | 2 | 9.7174015755284 | 9.7174015755284 | 4.6227099954141 | 4.6227099954141 |
| a₁·a₄ | 2 | 15.065123184742 | 15.065123184742 | 11.396788789995 | 11.396788789995 |
| a₂a₃a₁a₄ | 4 | 24.782524760271 | 24.782524760271 | 16.019498785409 | 16.019498785409 |
| (a₁a₂²)(a₃a₄⁻¹)(a₂)(a₄a₃) | 4 | 46.478549231999 | 46.478549231999 | 36.492512272076 | 36.492512272076 |
| (a₂a₁⁻¹a₂)(a₃a₄²a₃) | 2 | 51.966617505641 | 51.966617505641 | 50.175160531281 | 50.175160531281 |

Agreement is to all 14 printed digits from k = 10 on. At k = 2 the error is
about e^{−2kℓ_γ}-small, as expected.

### What this gives in higher genus

- The length function ℓ_X on measured laminations has, at each simple closed
  curve γ, a corner in every transverse direction β. Its size, the two-sided
  twist gap, is the local, explicit quantity 4·Σ log cosh(d_j/2) over the
  orthogeodesic arcs of β relative to γ.
- In complexity one there is essentially one transverse direction, and this
  is the gap g_γ.
- In higher genus the corner is a function of the transverse class, additive
  over arcs, so it is determined by the orthogeodesics from γ to itself.
- This replaces the Farey-tree machinery, which does not exist beyond
  complexity one. Every complexity-one result then holds on each one-holed-
  torus or four-holed-sphere subsurface of a higher-genus surface, with that
  subsurface's boundary lengths.

**Open next steps.**

1. The higher-genus analogue of the dual-area identity: the volume of the
   dual length ball in ML* as a sum over faces, built from these corners.
2. Mirzakhani-type averages of orthogeodesic sums Σ_γ Σ_η ℓ_γ·log cosh(d_η/2),
   which should connect to the Basmajian and Bridgeman orthogeodesic
   identities.

## Averages of the ball area, the product law, and what survives in higher genus (2026-11-25)

Script `poc/farey/wp_ball_average.py`, output `poc/farey/wp_ball_average.log`.

### The ball area averages, and ⟨Area(B)⟩·⟨Area(B*)⟩ = π²

**The ball area.**

- In complexity one, the curve count is a lattice count:
  #{γ : ℓ_γ ≤ R} ≈ (3/(4π²))·Area(B)·R². That is primitive vectors mod sign in
  the ball of radius R/2, in N = ℓ/2 units.
- Mirzakhani's unfolding gives ∫ #{ℓ ≤ R} = R²/2 per mapping-class orbit
  (V₀,₃ = 1), whatever the boundary.
- Hence ∫ Area(B) = 2π²/3 for one-holed tori, for every L, and 2π² for
  four-holed spheres (three orbits).

This is the complexity-one case of Mirzakhani's theorem on the average of the
Thurston volume B(X) of the length ball.

| Surface | ⟨Area(B)⟩ | ⟨A*⟩ (earlier section) |
|---|---|---|
| One-holed tori | 16π²/(L² + 4π²), = 4 for cusped | (L² + 4π²)/16 |
| Four-holed spheres | 4π²/(ΣL_i² + 4π²), = 1 for cusped | (ΣL_i² + 4π²)/4 |

So, in both families and for every choice of boundary lengths,

    **⟨Area(B)⟩ · ⟨Area(B*)⟩ = π²,**

the Blaschke–Santaló constant (the Mahler volume of an ellipse). Equivalently,
∫Area(B)·∫Area(B*) = π²·Vol². Individual surfaces lie below π², with the
modular torus at 0.975π² (as far as sampled, and up to π² in the flat limit
of cone tori). The averages saturate the bound exactly. The mechanism is that
∫A* is a constant times Vol², while ∫Area(B) does not depend on the boundary.
It holds for both families; whether it reflects a general principle is open.

**Consistency.**

- The modular torus, at 3.567, lies below the average 4: it is the minimum.
- The cusped sphere's average, 1, is the torus's 4 divided by 4: the double
  cover doubles the norm.
- In the tropical limit L → ∞, ⟨Area(B)⟩ → 0. In the flat limit of cone tori
  (L = iθ, θ → 2π), ⟨Area(B)⟩ → ∞. Both match the limit sections.

**Check.** Direct integration over the same fundamental domains as before
(Area(B) from the polygon through the corners ±v/N(v)):

| Case | ∫ Area(B) (predicted) | ⟨Area(B)⟩ (predicted) | ⟨Area(B)⟩·⟨A*⟩ |
|---|---|---|---|
| Torus, L = 0 | 6.584240 (6.579736) | 3.999679 (4) | 9.868813 |
| Torus, L = 2 | 6.589232 (6.579736) | 3.631347 (3.632001) | 9.867828 |
| Sphere, cusped | 19.734223 (19.739209) | 1.000021 (1) | 9.869809 |
| Sphere, L = (1, 2, 0.5, 1.5) | 19.761628 (19.739209) | 0.840219 (0.840352) | 9.868035 |

π² = 9.869604, so every product agrees to within 0.02%.

### Higher genus: what carries over and what does not

1. **Corners.** On any hyperbolic surface, at every simple closed geodesic γ,
   the length function on ML has a corner in each transverse direction β. Its
   size is 4·Σ log cosh(d_j/2) over the orthogeodesic arcs of β relative to γ.
   This is proved by the rank-one asymptotics and verified to 14 digits on
   five-holed spheres (previous section).
2. **Complexity-one subsurfaces.** For every embedded one-holed torus or
   four-holed sphere Y with geodesic boundary, lengths of curves in Y are
   intrinsic to Y. So, for every such Y in any surface:
   - the stable norm of Y, its gap law in orthogeodesic form, the vector
     Hines identity and the dual-area identity Area(B*_Y) = Σ_{γ⊂Y} g_γ·N_γ
     all hold;
   - with Y's boundary lengths, the moduli averages above hold for Y.
3. **No canonical dual ball.** Measured laminations ML(S) are piecewise linear,
   of dimension 6g − 6 + 2n, not a vector space. So the dual of the length
   ball, and the dual-area identity, have no canonical global meaning beyond
   complexity one. The canonical ball volume is the Thurston volume B(X)
   (Mirzakhani), whose average is known. The missing ingredient for a
   higher-genus "dual volume" is a canonical choice of dual. Candidates are
   chart-wise duals in maximal train-track coordinates, or a definition
   through the corners in point 1. That is left open.
4. **Divergence of the natural totals.** Summing A*(Y) over all complexity-one
   subsurfaces Y of a closed surface diverges, because ⟨A*(Y)⟩ grows like L²
   in Y's boundary length. Higher-genus orthogeodesic sums with log cosh
   kernels likewise need decaying weights to converge. That distinguishes them
   from Basmajian's log coth kernel, which converges.

## Is the product law structural? Other moments, the covariance, mixtures (2026-11-25)

Script `poc/farey/wp_moments.py`, output `poc/farey/wp_moments.log`. Cusped
tori, the same fundamental-domain integration as before, with every
quantity computed at each point.

**Moment family.** With g = 2 log coth(x/2) and N = x/2, unfolding gives
∫ Σ_γ g·N^s = ∫₀^∞ x·(x/2)^s·g dx, and

    ∫₀^∞ x^m·log coth(x/2) dx = 2·m!·(1 − 2^{−(m+2)})·ζ(m+2).

| Moment | Prediction | Measured | Rel. diff |
|---|---|---|---|
| s = 0: ⟨Σ g⟩ | 21ζ(3)/π² = 2.557670 | 2.557443 | 9·10⁻⁵ |
| s = 1: ⟨A*⟩ | π²/4 = 2.467401 | 2.467568 | 7·10⁻⁵ |
| s = 2: ⟨Σ g·N²⟩ | (93/16)ζ(5)·6/π² = 3.664063 | 3.664209 | 4·10⁻⁵ |
| ⟨Area(B)⟩ | 4 | 3.999679 | 8·10⁻⁵ |

**Where the π² comes from.** The product law is

    ⟨Area(B)⟩·⟨A*⟩ = 4·(15/4)ζ(4)/ζ(2) = 15ζ(4)/ζ(2) = π²,

which is Euler's relation ζ(4) = (2/5)ζ(2)². The dual area is the s = 1 moment,
whose Mellin transform lands on the even value ζ(4). That pairs with the
primitive-lattice density 1/ζ(2) in ∫Area(B) = 4ζ(2). Other moments land on
odd zeta values: ⟨Area(B)⟩·⟨Σ g⟩ = 84ζ(3)/π² = 10.229, which is not a power
of π. So the π² is specific to the dual pair (B, B*). It is the natural pair,
because Area(B*) = Σ g·N is exactly the moment whose weight is the norm
itself.

**Covariance.** Measured ⟨M⟩ = ⟨Area(B)·Area(B*)⟩ = 9.515454 = 0.96412π². So

    Cov(Area(B), Area(B*)) = ⟨M⟩ − π² = −0.3540.

Every individual surface satisfies M ≤ π² (Blaschke–Santaló), but the product
of the averages equals π² exactly. The two areas are anticorrelated across
moduli space, and the average Santaló deficit, π² − ⟨M⟩, equals minus their
covariance.

**Mixtures of boundary lengths.** At fixed L, ∫Area(B) does not depend on L
and ∫A* = c·Vol². Averaging over a mixture of boundary lengths therefore
gives ⟨Area(B)⟩·⟨A*⟩ = π²·∫w∫wV² / (∫wV)², which is at least π² by
Cauchy–Schwarz, with equality iff only one boundary length is present. For an
equal-weight mixture of L = 0, 2 and 5 the product is 10.3609. So π² is the
minimum over mixtures, reached exactly at fixed boundary data.

**Summary.** The π² is structural in a precise sense. It comes from
(i) primitive-lattice density 1/ζ(2) for the ball, (ii) the ζ(4) moment for
the dual, and (iii) Euler's evaluation of even zeta values. Altering the
weight breaks it into odd zeta values. Mixing boundary data lifts it above π²
by Cauchy–Schwarz.

## Moment polynomials: the dual area is singled out (2026-11-25)

Script `poc/farey/moment_polys.py` (sympy), output `poc/farey/moment_polys.log`.

**The moments.** For the corner measure μ_X = Σ_γ g_γ·δ_{N_γ}, unfolding
gives

    I_s = ∫ over moduli of Σ_γ g·N^s = ∫₀^∞ (ℓ^{s+1}/2^s)·g(ℓ) dℓ.

**Parity.** For s odd the weight ℓ^{s+1} is even. Then the two
log(1 + e^{−u}) pieces of the log-cosh decomposition combine into a single
integral over the whole line, and everything reduces to even zeta values:
I_s is a polynomial in L and π². For s even, polylogarithms of e^{−L}
survive, and the odd values ζ(3), ζ(5), … appear (as in ⟨Σg⟩ = 21ζ(3)/π²).

**One-holed tori** (y = L/2; each formula checked against direct quadrature
at y = 0.7, to 10–14 digits):

| s | I_s(y) |
|---|---|
| 1 | (y² + π²)²/24 (the dual area) |
| 3 | (y² + π²)²·(y² + 3π²)/240 |
| 5 | (y² + π²)²·(3y⁴ + 22π²y² + 51π⁴)/5376 |
| 7 | (y² + π²)²·(y² + 5π²)·(y⁴ + 8π²y² + 31π⁴)/11520 |
| 9 | (y² + π²)²·(y⁸ + 20π²y⁶ + 190π⁴y⁴ + 964π⁶y² + 2073π⁸)/67584 |

Every odd moment is divisible by (y² + π²)² ∝ V₁,₁(L)².

**The reason** is the flat point. The double root is at L = 2πi, a cone angle
of 2π, where the surface becomes flat. Near it, with hyperbolic area δ:

- g ≈ (4 − μ)/(4N²) with 4 − μ ~ δ², and the curve count grows like δ⁻¹, so
  each moment goes like δ;
- V₁,₁ ∝ 4π² − θ² ~ δ.

So the integral, average times volume, vanishes like δ². For tori,
V₁,₁ = 0 is exactly the flat locus, so this divisibility is forced for every
odd s.

**Four-holed spheres** (exact symbolic division; each checked against direct
quadrature at L = (0.3, 0.8, 0.5, 1.1), to 14 digits):

| s | Divisible by V₀,₄²? | Divisible by V₀,₄? | Vanishing order at the pillowcase L_i = iπ |
|---|---|---|---|
| 1 | yes: I₁ = V₀,₄²/2 | yes | 2 |
| 3 | no | no | 2 |
| 5 | no | no | 2 |
| 7 | no | no | 2 |

The quotients for s = 3 and s = 5 are recorded in the log. The volume
V₀,₄ = (ΣL_i² + 4π²)/2 vanishes on the hypersurface Σθ_i² = 4π² (with
L_i = iθ_i). Flatness is Σθ_i = 4π (Gauss–Bonnet). These meet only at the
pillowcase, four cone points of angle π.

- **At the pillowcase,** every odd moment vanishes to order 2. That is the
  flat-point scaling, the same as for tori.
- **On the rest of V₀,₄ = 0,** only the dual area vanishes. The higher moments
  are not even divisible by V₀,₄ once.

**Conclusion.** Among the polynomial (odd) moments of the corner measure, the
dual area s = 1 is the unique one whose moduli integral is a function of the
Weil–Petersson volume alone: ∫A* = 3V₁,₁² (orbifold normalisation) and
∫A* = V₀,₄²/2. This is what makes the product law
⟨Area(B)⟩·⟨Area(B*)⟩ = π² hold for every boundary. So the dual body is
distinguished, not only by convex-geometric duality but by this volume
structure.

## Why s = 1: locality, degree, and an n = 4 coincidence (2026-11-25)

Script `poc/farey/s1_uniqueness.py`, output `poc/farey/s1_uniqueness.log`.

**Claim.** Among the odd moments of the corner measure, only the dual area
satisfies ∫ over moduli = c·V², and that is the input of the product law.

**Argument.**

1. **Locality.** Mirzakhani's unfolding writes ∫Σ_γ g·N^s as a sum over
   mapping-class orbits of ∫ x^{s+1}·g(x) dx. By the orthogeodesic (pants)
   factorisation of the gap, each term is a sum over the pants adjacent to
   the curve. Each pants contributes K_s((A+B)/2) + K_s((A−B)/2), a
   polynomial in its other two boundary lengths A, B of degree s + 3.
2. **Degree.** c·V² has degree 4 in the lengths, so s = 1.
3. **Matching at s = 1.**
   - *Torus:* I₁ has degree 4 and a double root at the flat point L = 2πi
     (forced by the flat-limit scaling), so I₁ = c·(y² + π²)² ∝ V₁,₁².
   - *Sphere:* the pants sums must assemble into (ΣL²)². The degree-4 part
     needs

         Σ_{i<j} [(L_i + L_j)⁴ + (L_i − L_j)⁴] = 2(n−1)·ΣL⁴ + 12·Σ_{i<j} L_i²L_j²

     to be a multiple of (ΣL²)² = ΣL⁴ + 2Σ_{i<j}L_i²L_j². That requires
     2(n−1) : 12 = 1 : 2, so **n = 4**. Checked with sympy for n = 3, 4, 5, 6:
     the remainder is 4e₂, 0, −4e₂ and −8e₂ in the elementary symmetric
     function e₂ of the L_i². The lower-order terms also match:
     (ΣL²)²/32 + π²ΣL²/4 + π⁴/2 = (ΣL² + 4π²)²/32.
   - *Sphere, s ≥ 3:* a function of ΣL² of degree 2k ≥ 6 contains the triple
     products L_i²L_j²L_k². A pants only sees two other boundary lengths, so
     pants sums can never produce them. Checked: the coefficient of
     L₁²L₂²L₃² in I₃ is 0, while in (ΣL²)³ it is 6.
4. **Ball area.** ∫Area(B) does not depend on the boundary (Mirzakhani's
   count, V₀,₃ = 1). Together with c·V² this gives ⟨Area(B)⟩·⟨A*⟩ = constant,
   and the constant is π² by Euler's evaluation of ζ(2) and ζ(4).

**Link to Mirzakhani's recursion.** The L-derivative of the gap is the
complement of her recursion kernel:

    ∂_L g(x; L) = ½·sinh(L/2)/(cosh x + cosh(L/2)) = ½·(1 − H(L, 2x)),
    H(x, y) = 1/(1 + e^{(x+y)/2}) + 1/(1 + e^{(x−y)/2})

(worst error 2·10⁻¹⁷). With ∫₀^∞ x²/(cosh x + cosh a) dx = a(a² + π²)/(3 sinh a),
checked to 18 digits at a = 0.5, 2 and 5, this gives

    d/dL ∫A* = L(L² + 4π²)/96 = (L/2)·V₁,₁(L),

checked at L = 0, 2 and 5 to 15 digits. Since V₁,₁′ = L/24, this is
d/dL(6V₁,₁²), so ∫A* = 6V₁,₁² in the fundamental-domain normalisation. The
recursion's kernel computes V₁,₁; the same kernel, weighted by one extra
power of x, computes ∫A*. That extra x is the norm N = x/2 in A* = Σ g·N. So
the dual area is the moment for which the kernel integral reproduces the
volume's own derivative, d(V²)/dL = 2V·V′.

**Summary.** The product law is a consequence of:

- pants-locality of the gap (the orthogeodesic form);
- the degree count, which allows only s = 1;
- at s = 1, an algebraic coincidence: the flat-point double root for tori,
  and the binomial identity that holds exactly for n = 4 boundaries on the
  sphere.

This suggests looking for higher-complexity analogues where the
corresponding pants combinatorics again close up into powers of the volume.

## Searching for other surfaces where the product-law structure holds (2026-11-25)

Scripts `poc/farey/higher_volumes.py` and `poc/farey/orbifold_product.py`,
with logs.

### Higher complexity: no

**The candidate.** On S_{g,n} with n ≥ 2, the canonical analogue of the
dual area is the *pants-corner sum*. For each pair of boundaries {i, j},
sum over the curves γ cutting off a pair of pants containing boundaries i
and j, of (ℓ_γ/2)·log P(ℓ_γ; L_i, L_j). For S₀,₄ this is exactly A*. It
converges because the other side of γ is the fixed surface S_{g,n−1}.

**Its average.** Mirzakhani's formula, with the cut surface
S₀,₃ ⊔ S_{g,n−1}, gives

    F_{g,n}(L) = Σ_{i<j} ∫ (x²/2)·log P(x; L_i, L_j)·V_{g,n−1}(x, L_rest) dx,

and every piece is one of the K_s polynomials.

**Volumes.** These come from Mirzakhani's recursion, implemented
symbolically with the kernel moments
F_{2k+1}(t) = (2k+1)!·Σ_i ζ(2i)(2^{2i+1} − 4)·t^{2k+2−2i}/(2k+2−2i)!. The
recursion reproduces the known V₀,₄, V₁,₂ and V₀,₅ exactly.

**Result.** deg F = deg V + 2 always, while deg V² = 2·deg V. These agree
only when deg V = 2, that is, in complexity one. Beyond that, F is not even
divisible by V once:

| (g, n) | deg V | deg F | F divisible by V |
|---|---|---|---|
| (0, 4) | 2 | 4 | yes: F/V = (ΣL² + 4π²)/4 |
| (0, 5) | 4 | 6 | no |
| (1, 2) | 4 | 6 | no |
| (0, 6) | 6 | 8 | no |
| (1, 3) | 6 | 8 | no |
| (2, 2) | 10 | 12 | no |

So the volume structure behind the product law is a complexity-one
phenomenon. Beyond complexity one the average of the pants-corner sum is a
genuinely new polynomial, not a function of the volume.

### Complexity-one orbifolds: yes, every one

Spheres with cone points and cusps have the same volume polynomials at
L_i = iθ_i (Do–Norbury, for cone angles ≤ π). So the product law predicts,
for every choice of cone data:

    Vol = (4π² − Σθ_i²)/2,   ⟨A*⟩ = (4π² − Σθ_i²)/4,   ⟨Area(B)⟩ = 4π²/(4π² − Σθ_i²),   product π².

**Direct integration** over the fundamental domain. The Fenchel–Nielsen
charts are built from the traces 2cos(θ/2) directly.

| Orbifold | Vol (predicted) | ⟨A*⟩ (predicted) | ⟨Area(B)⟩ (predicted) | Product (π² = 9.86960) |
|---|---|---|---|---|
| k-Markoff (1, 1, 1): three order-3 points + cusp | 13.12695 (13.15947) | 6.57856 (2π²/3 = 6.57974) | 1.50030 (1.5) | 9.86983 |
| (2, 2, 2, ∞): three order-2 points + cusp | 4.93283 (4.93480) | 2.46731 (π²/4 = 2.46740) | 4.00017 (4) | 9.86966 |

The volume shows the usual edge-of-domain quadrature excess (0.25% and
0.04%), which cancels in the averages.

**Consistency check.** The (2, 2, 2, ∞) orbifold is the cusped torus divided
by its elliptic involution. The double cover maps simple curves to simple
curves of the same length, so the norm, and both averages, must equal the
cusped torus's 4 and π²/4. They do.

### Conclusion of the search

The product law ⟨Area(B)⟩·⟨Area(B*)⟩ = π² holds on exactly the complexity-one
family: one-holed tori, four-holed spheres, and all their cusp and cone-point
(orbifold) versions with cone angles ≤ π. It fails beyond, for a degree
reason: the average of the natural corner sum has degree deg V + 2, which
equals 2·deg V only when deg V = 2. The n = 4 binomial coincidence and the
flat-point double root are what make the complexity-one cases close up.

## The higher-complexity corner polynomials F_{g,n} (2026-11-25)

Script `poc/farey/corner_moments.py`, output `poc/farey/corner_moments.log`.

### Structure: the volume recursion is the previous moment of the same pants factor

Let f(x; A, B) = ½·log P(x; A, B) = log cosh(d/2), where d is the pants'
return orthogeodesic. Then, exactly,

    ¼·[H(x, A+B) + H(x, A−B)] = ½ − ½·coth(x/2) − ∂_x f(x; A, B),

where H is Mirzakhani's kernel (worst error 4·10⁻¹⁸). Integrating by parts,
the B-term of her recursion becomes

    ½∫ x·[H(x, L₁+L_j) + H(x, L₁−L_j)]·V dx = 2∫ f(x; L₁, L_j)·∂_x(x·V) dx + ∫ x(1 − coth(x/2))·V dx.

This was checked on the (1, 2) recursion at (L₁, L₂) = (1.3, 0.6): the two
sides agree to 20 digits (10.920367925897440059).

So the volume recursion and the corner sum are built from the same
orthogeodesic pants factor. They differ only in the weight:

- ∂_x(x·) for the volumes, which is (2k+1)·x^{2k} on x^{2k}: the s = −1
  moment;
- x² for the corner polynomials F_{g,n} = Σ_{i<j}∫ x²·f(x; L_i, L_j)·V_{g,n−1}(x, L_rest) dx:
  the s = +1 moment.

In complexity one the s = +1 moment closes up into V². Beyond, it is a new
polynomial, and its relation to the s = −1 moment, Mirzakhani's recursion,
is open.

### Cusped averages ⟨F⟩ = F_{g,n}(0)/V_{g,n}(0)

All values are exact rational multiples of π². The volumes come from the
symbolic recursion, which reproduces the known values 10π⁴, 244π⁶/3,
2758π⁸/3, π⁴/4, 14π⁶/9 and 529π⁸/36.

| (g, n) | V(0) | ⟨F⟩/π² | Pairs | Per pair /π² |
|---|---|---|---|---|
| (0, 4) | 2π² | 1 | 6 | 1/6 = 0.16667 |
| (0, 5) | 10π⁴ | 22/15 | 10 | 0.14667 |
| (0, 6) | 244π⁶/3 | 3327/1708 | 15 | 0.12986 |
| (0, 7) | 2758π⁸/3 | 50576/20685 | 21 | 0.11643 |
| (0, 8) | 199784π¹⁰/15 | 7307330/2472327 | 28 | 0.10556 |
| (1, 2) | π⁴/4 | 11/45 | 1 | 0.24444 |
| (1, 3) | 14π⁶/9 | 2403/3920 | 3 | 0.20434 |
| (1, 4) | 529π⁸/36 | 58456/55545 | 6 | 0.17540 |
| (2, 2) | 787π¹⁰/480 | 11684383/49085190 | 1 | 0.23804 |
| (2, 3) | 1498069π¹²/64800 | 83414025/136324279 | 3 | 0.20396 |
| (3, 2) | 2800144027π¹⁶/65318400 | 0.232714… | 1 | 0.23271 |
| (4, 2) | 909612310986473π²²/362125209600 | 0.229174… | 1 | 0.22917 |

The (3, 2) and (4, 2) averages are exact rationals with large numerators;
they are in the log.

**Observations** (empirical):

- **Genus 0, growing n.** The total ⟨F⟩ grows roughly linearly: 1, 1.467,
  1.948, 2.445, 2.956 (×π²), with increments 0.47, 0.48, 0.50, 0.51. Each added
  cusp adds about π²/2, with a slowly rising increment. The per-pair average
  falls like 1/n.
- **n = 2, growing genus.** The per-pair average decreases slowly: 0.2444,
  0.2380, 0.2327, 0.2292. A fit a + b/g to g = 3, 4 gives a ≈ 0.219, so the
  large-genus limit looks finite, about 0.22π² ≈ 2.2. A naive Mirzakhani–Petri
  estimate (V_{g,1}(x)/V_{g,1}(0) ≈ sinh(x/2)/(x/2)) makes the integral
  diverge, so the finite limit has to come from the breakdown of that
  approximation at x ~ √g. Identifying the constant needs the refined
  large-genus asymptotics. That is open.
- **Genus and boundary trade-off.** At fixed n the per-pair value barely
  depends on genus. Compare (1, 3) at 0.2043 with (2, 3) at 0.2040, and (1, 2)
  at 0.2444 with (2, 2) at 0.2380. So the per-pair corner average is mostly a
  function of the number of boundary components.

## A Mirzakhani-type recursion for F_{g,n} (2026-11-25)

Script `poc/farey/F_recursion.py` (sympy), output `poc/farey/F_recursion.log`.

**Notation.**

- Pair transform: T_ij[V](L) = ∫₀^∞ x²·f(x; L_i, L_j)·V(x, L_rest) dx, with
  f = ½·log P = log cosh(d/2) the pants return-orthogeodesic factor.
- F^S_g(L) = Σ over pairs {i, j} ⊂ S of T_ij[V_g(x, L_rest)]. S is a set of
  "active" boundary labels: only curves that cut off a pair of active
  boundaries count. F of a pair of pants is 0, and F_{g,n} = F^{all}.

**Recursion.** Take the distinguished boundary L₁ and set S′ = S ∖ {1}:

    ∂_{L₁}(L₁·F^S_g)
      = 𝓜_{L₁}[F^{S′}]
      + Σ_{i<j ∈ S′} T_ij[𝓘₁]
      + [1 ∈ S]·Σ_{j ∈ S′} ∂_{L₁}(L₁·T_{1j}[V_g(x, L_rest)]).

The three terms:

- **𝓜_{L₁}** is Mirzakhani's operator with F in place of V. The new
  boundaries created by surgery are inactive.
  - Connected term: ½∫∫ xy·H(x+y, L₁)·F^{S′}_{g−1}(x, y, …).
  - Disconnected term: ½∫∫ xy·H(x+y, L₁)·[F₁V₂ + V₁F₂] (Leibniz rule).
  - B-terms: ½∫ x·[H(x, L₁+L_k) + H(x, L₁−L_k)]·F^{S′∖{k}}_g(x, L without 1, k).
- **Interaction.** 𝓘₁(x) = ½∫ y·[H(y, L₁+x) + H(y, L₁−x)]·V_g(y, L_rest ∖ L₁) dy.
  This is the pants containing β₁ whose other cuff is the {i, j}-curve. When
  V_g(x, L_rest) is a pair of pants, 𝓘₁ = 1.
- **Pairs containing 1:** explicit, ∂_{L₁}(L₁·T_{1j}V).

**Derivation.** T_ij commutes with ∂_{L₁}(L₁·) whenever 1 ∉ {i, j}, so
Mirzakhani's recursion for V_{g,n−1}(x, L_rest) can be applied underneath it.
Each of her terms becomes the corresponding term for a smaller F, with one
exception: the B-term pairing L₁ with the integration curve x gives the
interaction.

**Verification.** Both sides are computed independently. The left uses the
definition of F; the right uses only smaller F's, volumes and kernel moments.
The difference is exactly 0, as a polynomial identity in all L_i and π, for
(g, n) = (0, 4), (0, 5), (0, 6), (0, 7), (1, 2), (1, 3) and (2, 2).

**Reading.**

- Together with Mirzakhani's recursion for V, this determines F_{g,n} from
  smaller (g, n): F = L₁⁻¹·∫₀^{L₁} (right-hand side). The base case is
  F_{0,3} = 0.
- The system (V, F) is a coupled linear recursion. F enters the right-hand
  side linearly, with the disconnected terms obeying the Leibniz rule
  F₁V₂ + V₁F₂. So F behaves like a first-order deformation (a tangent
  vector) of Mirzakhani's recursion, sourced by two explicit terms: the
  pants factor on pairs containing β₁, and the interaction pants.
- In complexity one the recursion closes up into F = V²/2 (S₀,₄) and
  F = 6V₁,₁² (one-holed torus, seam version), giving the π² product law.
  Beyond, the interaction and pair sources do not factor through V, which is
  why F_{g,n} is a new polynomial there.

## The deformation identified: the corner kernel is Mirzakhani's B-kernel on x·V, integrated once (2026-11-25)

Script `poc/farey/deformation.py` (sympy), output `poc/farey/deformation.log`.

**The shared smoothing operator.** Let ρ(u) = sech²(u/4)/8, the logistic
density. On polynomials, convolution with ρ is the Bernoulli operator

    S = 2πD / sin(2πD),   D = d/dX.

**Mirzakhani's side.** Since ∂_t H(x, t) = ρ(x − t) − ρ(x + t), her B-term,
as a function of t = L₁ ± L_j, satisfies d/dt B[V](t) = ½·S[t·V(t)]. On
moments: d/dt F_{2k+1}(t) = S[t^{2k+1}], checked exactly for k = 0, …, 3.
This is the source of the ζ(2k) in the volumes.

**The corner side.** The pair transform T_ij[V] = G[V](L_i + L_j) +
G[V](L_i − L_j) depends only on X = L_i ± L_j. Differentiating its
log-cosh decomposition twice, the delta function from the kink cancels the
polynomial part, and

    d²G/dX² = ¼·S[X²·V(X)],   i.e.   G[V](X) = ½∫₀^X B[x·V](u) du + G[V](0).

The constant is

    G[V](0) = ½∫ x²·log coth(x/4)·V dx,
    G[x^{2k}](0) = (2k+2)!·2^{2k+3}·(1 − 2^{−(2k+4)})·ζ(2k+4) = π⁴/6, 4π⁶/5, 68π⁸/7, 1984π¹⁰/9, 88448π¹²/11, …

**Checks.**

- For V = x^{2k}, k = 0, …, 4, G[x^{2k}](2y) = 2^{2k+2}·K_{2k+1}(y) holds
  exactly (sympy).
- The constants agree with direct quadrature to 20 digits.

**Statement.** The corner pair transform is Mirzakhani's B-transform applied
to the length-weighted volume x·V(x) instead of V(x), integrated once in the
combined length X = L_i ± L_j. The extra factor x is the norm N = x/2 in the
dual area A* = Σ g·N. The extra integration matches the one-higher moment:
s = +1 against Mirzakhani's s = −1.

So the deformation in the F recursion is V ↦ x·V inside the B-kernel. The
Leibniz rule F₁V₂ + V₁F₂ in the recursion is what such a weighted insertion
produces at first order, and the interaction term is the same insertion
landing on a cut curve.

## The tautological form of F_{g,n} (2026-11-26)

Script `poc/farey/tautological.py`, output `poc/farey/tautological.log`.

**Where each pair term lives.** Mirzakhani's theorem gives
V(L) = ∫ exp(2π²κ₁ + Σ L_i²ψ_i/2). So each pair term of F_{g,n} is an
integral over the boundary divisor D_ij ≅ M̄₀,₃ × M̄_{g,n−1}, where i and j
bubble off, with an insertion at the node:

    F_ij = ∫_{M̄_{g,n−1}} 𝒢(L_i ± L_j; ψ_node)·exp(2π²κ₁ + Σ_rest L²ψ/2),
    𝒢(X; ψ) = ¼·D⁻²·S[X²·e^{X²ψ/2}] + const,   S = 2πD/sin(2πD).

**Top degree (π → 0).** Here S becomes the identity and the constants G(0),
which are proportional to π^{2k+4}, vanish. So the top-degree part is a pure
ψ-class (Kontsevich) object, a tropical pants gluing:

    F^top_{g,n}(L) = Σ_{i<j} Σ_± ¼∫₀^{X} (X − s)·s²·V^top_{g,n−1}(s, L_rest) ds,   X = L_i ± L_j.

The cut curve has length s ≤ L_i ± L_j and weight (X − s)·s²/4. As a node
insertion this is

    (X⁴/4)·∫₀¹ (1 − u)·u²·e^{u²X²ψ/2} du,   using [x^{2k}]V^top = ⟨τ_k τ_rest⟩/(2^k·k!).

Verified as an exact polynomial identity for (0, 4), (0, 5), (0, 6), (0, 7),
(1, 2), (1, 3) and (2, 2).

**Lower orders.** The Bernoulli terms of S supply the π-corrections. This is
the same mechanism that produces the κ₁ (2π²) shifts in the volumes: at top
degree Mirzakhani's kernel H(x, t) becomes the step θ(t − x), and S is its
smoothing.

**Reading.** At top degree, F_{g,n} is the Kontsevich (metric ribbon graph)
volume with a pair of boundaries glued through a pants whose cut curve
carries the extra weight s². That weight is the length factor x·N of the
dual area. The full F_{g,n} is this tropical gluing, smoothed by the same
Bernoulli operator that turns Kontsevich volumes into Weil–Petersson
volumes.

**Open.** A closed formula for the top coefficients in terms of ⟨τ τ⟩
without the integral. No simple relation to V_{g,n}'s own coefficients was
found; the boundary-divisor bubbling gives no string-equation-type identity
for general a, b.

## The large-genus limit: exactly 2·φ(L_i)·φ(L_j) (2026-11-26)

Scripts `poc/farey/genus_profile.py` and `poc/farey/genus_limit.py`, with
logs.

**What sets the limit.** Write V_{g,1}(x) = Σ c_k x^{2k} and
r_k = c_k·2^{2k}·(2k+1)!/c₀ = [τ_k]_{g,1}/V_{g,1}. These are Mirzakhani–
Zograf's normalised intersection numbers; r_k = 1 for all k exactly when
V_{g,1}(x) = V(0)·sinh(x/2)/(x/2). The per-pair cusped average is

    a_g = 16·V_{g,1}(0)·Σ_k (2k+2)·r_k·ζ-factor / V_{g,2}(0).

**The exact profile is not flat.** For g = 4: r₁ = 0.982, r₂ = 0.930,
r₃ = 0.811, r₄ = 0.643, r₅ = 0.454, r₆ = 0.278, r₇ = 0.142. It collapses
roughly in x = k²/g. If r_k were ≡ 1, the sum would diverge.

**Profile from Mirzakhani–Zograf** (arXiv 1112.1151, Thm 3.2 and eq. 3.7):

    [τ_{k+1}]_{g,1} / [τ_k]_{g,1} = 1 − (2k − ½)/(π²g) + O(1/g²).

Multiplying up gives r_k → exp(−(k² − 3k/2)/(π²g)), so the limiting profile
is r(x) = e^{−x/π²}. Higher-order terms contribute k³/g² ~ x^{3/2}/√g → 0.

**The limit.** With V_{g,2}(0) ≈ 4π²(2g−1)·V_{g,1}(0) and
∫2k·e^{−k²/(π²g)} dk = π²g:

    lim_{g→∞} a_g = 2   (= 2/π² · π² = 0.20264 π²).

The "+2" in the weight and the finite-g profile give corrections of order
1/√g, so convergence is slow. Exact data for g = 1, …, 5 fitted to
a + b/√g + c/g gives a = 0.20198π² = 1.9934, within 0.3% of 2. A fit
a + b/g gave 0.214π², which was the wrong model.

**With boundaries (conjecture).** For large x the pants factor is
f ≈ 2·cosh(L_i/2)·cosh(L_j/2)·e^{−x/2}, and the volumes carry sinh(L/2)/(L/2).
So

    lim_{g→∞} ⟨F_ij⟩(L) = 2·φ(L_i)·φ(L_j),   φ(L) = (L/2)·coth(L/2).

**Test.** R_g(L) = [F_{g,2}(L)/V_{g,2}(L)] / [2φ(L₁)φ(L₂)], from exact
polynomials:

| g | L = (0, 0) | (1, 1) | (2, 0.5) | (3, 3) |
|---|---|---|---|---|
| 1 | 1.20628 | 1.19134 | 1.18376 | 1.11600 |
| 2 | 1.17469 | 1.16913 | 1.16630 | 1.13972 |
| 3 | 1.14839 | 1.14496 | 1.14318 | 1.12648 |
| 4 | 1.13093 | 1.12844 | 1.12713 | 1.11486 |

All columns decrease together toward 1. The φφ factor (a 2.75× change at
(3, 3)) is matched to within 1.5% at g = 4.

**Small check at n = 3.** The per-pair values at (1, 3) and (2, 3) are
0.2043π² = 2.016 and 0.2040π² = 2.013, already close to 2.

**Status.** The limit 2 follows from Mirzakhani–Zograf's profile, granted
that their O(1/g²) error is uniform enough in k (k up to about √g) to pass
to the integral. That uniformity is the step to prove. The boundary formula
is a conjecture supported by the table above.

## Fast engine to genus 11, and the 1/√g correction (2026-11-26)

Scripts `poc/farey/mz_engine.py` and `poc/farey/mz_profile2.py`, with logs.

**The engine.** It implements Mirzakhani–Zograf's recursion (III)
(arXiv 1112.1151, eqs. 2.2–2.4) for the normalised intersection numbers
[τ_d]_{g,n}, at 40 digits with memoisation. It reproduces V₀,₅(0) = 10π⁴,
V₁,₂(0) = π⁴/4, V₂,₂(0) = 787π¹⁰/480, and every exact per-pair value for
g ≤ 5. Genus 10 takes about 4 minutes, where the symbolic recursion needed
hours at genus 6.

**Per-pair cusped average** a_g, in absolute units (the conjectured limit
is 2):

| g | a_g | √g·(a_g − 2) |
|---|---|---|
| 1 | 2.41257 | 0.41257 |
| 2 | 2.34939 | 0.49411 |
| 3 | 2.29677 | 0.51403 |
| 4 | 2.26185 | 0.52371 |
| 5 | 2.23701 | 0.52996 |
| 6 | 2.21819 | 0.53446 |
| 7 | 2.20329 | 0.53786 |
| 8 | 2.19110 | 0.54051 |
| 9 | 2.18088 | 0.54264 |
| 10 | 2.17215 | 0.54439 |
| 11 | 2.16458 | 0.54584 |

So a_g = 2 + C/√g + …, confirming the limit 2 numerically. The increments
of √g·(a_g − 2) fall roughly like g^{−1.8}. Extrapolating gives C ≈ 0.56–0.58:

- 0.5605 if the next correction is 1/g;
- 0.564 with the fitted exponent;
- 0.576 if it is 1/√g.

Candidate closed forms in that range include 7/(2√π) − √2 = 0.5605 and
1/√π = 0.5642. None is identified.

**Why the 1/√g coefficient is not "second order".** In the scaling regime
x = k²/g, the term k^{2j−2}/g^j of the ratio ρ_k = r_{k+1}/r_k contributes at
order 1/√g for every j. So C needs the full scaling function Ψ in

    ρ_i = 1 − (2i − ½)/(π²g) + Ψ(i²/g)/g.

- With Ψ = 0, Euler–Maclaurin gives C = 7/(2√π) = 1.975, far from the data.
  The Ψ-part contributes about −1.4.
- Extracting Φ(x) = √g·[log r_k + (k² − 3k/2)/(π²g)] from the exact numbers,
  the profile has not yet collapsed by g = 10. At x ≈ 8, Φ/x^{3/2} is
  −0.044, −0.039, −0.036, −0.034, −0.032, −0.031, −0.030 for g = 4, …, 10.
  A fit at g = 9–10 implies C = −0.36, which contradicts the directly
  measured +0.55. The next corrections are still large at these genera.
- **Analytic route.** For n = 1 the recursion reduces at large g to the
  B-term in [τ_{k₁}τ_{k₂}]_{g−1,2}. Ψ is therefore determined by the
  two-point profile of the n = 2 numbers. A naive closure (independent
  Gaussians) wrongly predicts a linear term in r_k at small k, contradicting
  Mirzakhani–Zograf's quadratic first-order term. So the two-point
  correlations matter.

**Status.**

- Limit 2: derived, and numerically confirmed to genus 11.
- C ≈ 0.56–0.58: numerical. Its derivation needs the scaling function of the
  two-point intersection numbers.
- The uniformity proof for the limit is still open.

## Proof of lim a_g = 2, conditional on one uniform lemma (2026-11-26)

Script `poc/farey/uniformity_check.py`, output `poc/farey/uniformity_check.log`.
Notation: r_k = [τ_k]_{g,1}/V_{g,1} and ρ_k = r_{k+1}/r_k.

**Theorem (conditional).** Assume

> **Lemma U.** There are C and g₀ such that for all g ≥ g₀ and 1 ≤ k ≤ 3g − 3,
> |ρ_k − 1 + (2k − ½)/(π²g)| ≤ C·(1 + k²)/g².

Then the per-pair cusped corner average a_g = F_{g,2}(0)/V_{g,2}(0) tends to 2.

**Proof.**

1. **Rewrite.** a_g = 16·(V_{g,1}/V_{g,2})·Σ_k (2k+2)·λ_k·r_k, with
   λ_k = (1 − 2^{−2k−4})·ζ(2k+4) = 1 + O(4^{−k}). By Mirzakhani–Zograf
   Thm 1.4, V_{g,2}/(8π²g·V_{g,1}) → 1. So it suffices to show
   (1/(π²g))·Σ_k 2k·r_k → 1. The parts 2r_k and (λ_k − 1)·r_k contribute
   O(1/√g) and O(1/g).
2. **The step from k = 0.** r₁ = 1 − 1/(2π²g) + O(1/g²) (Mirzakhani–Zograf).
   Together with Lemma U and log(1 − t) = −t + O(t²), for k ≥ 1:

       log r_k = −(k² − 3k/2 + 1)/(π²g) + O((k + k³)/g²) + O(k³/g²).

3. **Profile.** For k ≤ A√g the error is O(A³/√g) → 0 uniformly, so
   r_k = e^{−k²/(π²g)}·(1 + o(1)).
4. **Tail.** For k ≤ βg with β = 3/(2π²C′), where C′ absorbs the error
   constants, step 2 gives log r_k ≤ −k²/(2π²g) + O(k/g). For k > βg,
   monotonicity r_{k+1} < r_k (Mirzakhani–Zograf Thm 3.2(ii), lower
   difference bound) gives r_k ≤ r_{⌊βg⌋} ≤ e^{−β²g/(2π²)+O(1)}. Those at
   most 3g terms contribute O(g·e^{−cg}).
5. **Dominated convergence.** With u = k/√g,

       (1/(π²g))·Σ 2k·r_k → (1/π²)∫₀^∞ 2u·e^{−u²/π²} du = 1,

   with domination by 2u·e^{−u²/(2π²)} from step 4. Hence a_g → 2. ∎

**Numerical verification of the inputs (g = 2, …, 10).**

| Input | Status |
|---|---|
| L1: r_k ≥ 1 − 2k²/(π²g) | Holds (minimum slack 0) |
| L2: r_k strictly decreasing | Holds |
| Lemma U | max over 1 ≤ k ≤ 3g−3 of g²·\|ρ_k − 1 + (2k−½)/(π²g)\|/(1+k²) = 0.185, 0.141, 0.125, 0.118, 0.113, 0.110, 0.107, 0.106, 0.104: bounded and decreasing |
| Tail | min_k (−g·log r_k/k²) is attained at k = 1 and tends to 1/(2π²) = 0.0507 (0.0577 at g = 10) |
| k = 0 step | g²·(r₁ − 1 + 1/(2π²g)) → about −0.07 |

**What remains.** A proof of Lemma U: Mirzakhani–Zograf's fixed-k ratio
asymptotics (their Remark 3.3 and eq. 3.7), with the error tracked
uniformly in k. Their proof is an induction on g through recursion (III),
whose weights a_l increase to 1. Lemma U amounts to checking that each
error term in that induction is O((1+k²)/g²) with constants independent of
k. Numerically the constant is about 0.10 and decreasing.

**Boundary version.** The same argument with the pants factor
f ≈ 2·cosh(L_i/2)·cosh(L_j/2)·e^{−x/2}, and the volumes' sinh(L/2)/(L/2)
factors (Mirzakhani–Petri), gives 2·φ(L_i)·φ(L_j). It is conditional on
Lemma U together with the corresponding uniform statement for
V_{g,n}(L)/V_{g,n}(0).

## Horocycle equidistribution and the Riemann zeros (`poc/farey/horocycle_rate.py`)

Context: RH is equivalent to the closed horocycle of height y on the modular surface equidistributing at rate
O(y^(3/4-eps)) (Zagier 1981). Test function: the incomplete Eisenstein series with psi(t) = exp(-1/t). Unfolding the
horocycle through the Farey/Ford structure gives the exact formula

    a(y) = int_0^1 f(x+iy) dx = e^(-1/y) + sqrt(pi y) * sum_c phi(c)/c * exp(-c^2 y),     mean = 3/pi,

where denominator c contributes its phi(c) Farey fractions. The Mellin transform is zeta(2s-1)/zeta(2s) * sqrt(pi) Gamma(s-1/2),
and the poles at the Gamma function and at s = 1/2 cancel, leaving the explicit formula

    a(y) - 3/pi = sum_rho R_rho y^(1-rho/2) + sum_k T_k y^(1+k),   R_rho = sqrt(pi) zeta(rho-1) Gamma((rho-1)/2) / (2 zeta'(rho)).

Each nontrivial zero rho = beta + i gamma contributes size y^(1-beta/2); on the critical line that is y^(3/4).

Numerics, with 80-bit sums, y from 1e-1 to 1e-11:
- Measured equals predicted (30 zeros plus trivial terms) to 1e-15 absolute for y <= 0.03, which is float rounding.
  The first zero alone accounts for all but 0.4% of the error for y <= 1e-4.
- E(y)/y^(3/4) oscillates with constant envelope 2|R_1| = 2.39e-5 over every decade from 1e-5 to 1e-11.
  E/y^(1/2) tends to 0 and E/y grows, so the rate is exactly y^(3/4).
- A fit of E/y^(3/4) = A cos(w log y + p) gives w = 7.054, against gamma_1/2 = 7.067. The amplitude is 2.50e-5, against 2.39e-5;
  the second zero accounts for the difference.

Reading: the error of the horocycle average is literally a sum over the Riemann zeros, with the first zero (14.1347)
audible as a log-periodic oscillation of period 4 pi/gamma_1 = 0.889 in log y. A zero off the line at beta > 1/2 would
show as a term of size y^(1-beta/2), which decays more slowly than y^(3/4). No numerics can exclude that for zeros of
arbitrary height. The test confirms the mechanism, not RH. Our earlier identities (gap law, dual areas, pi^2 law) are
exact and do not depend on RH. RH enters only through error terms of counts over Farey fractions like the one above.

## Twisted horocycles on Y_1(N) and Dirichlet L-zeros (`poc/farey/horocycle_dirichlet.py`)

Weight each Farey denominator by an even primitive character: f_chi(z) = sum_{Gamma_inf\Gamma} chi(c) psi(Im gamma z).
Right multiplication by Gamma_1(N) preserves c mod N, so f_chi is a function on the modular curve Y_1(N). Its closed
horocycle of height y at the cusp at infinity unfolds exactly to

    a_chi(y) = sqrt(pi y) sum_c chi(c) phi(c)/c exp(-c^2 y),   Mellin = L(2s-1,chi)/L(2s,chi) sqrt(pi) Gamma(s-1/2).

The mean is 0, since L(2s-1,chi) has no pole. The explicit formula is

    a_chi = sum_rho R_rho y^(1-rho/2) + sum_k T_k y^(1+k),   R_rho = sqrt(pi) L(rho-1,chi) Gamma((rho-1)/2) / (2 L'(rho,chi)).

The trivial zero of L(2s,chi) at s = 0 gives a smooth y^1 term. GRH for chi is equivalent to the nontrivial part being
O(y^(3/4-eps)).

| chi (even, primitive) | lowest zeros used | max \|measured - formula\| | max \|E\|/y^(3/4) per decade, 1e-4..1e-11 | sum \|R_rho\| |
|---|---|---|---|---|
| Legendre mod 5 | t = 6.648, 9.831 | 5e-14 | 0.024 - 0.027 | 0.028 |
| Kronecker mod 8 | t = 4.900, 7.628 | 9e-14 | 0.134 - 0.155 | 0.158 |
| cubic mod 7 (complex) | t = 4.356, -6.201 | 8e-14 | 0.120 - 0.129 | 0.133 |
| sextic mod 13 (complex) | t = -3.661, 4.455 | 1e-13 | 0.371 - 0.510 | 0.525 |

The table uses the zeros with |t| < 60 found on the line; all are found at Re = 1/2 to 1e-17. For each character,
E/y^(3/4) stays bounded by sum |R_rho| and does not decay over seven decades, while E/y^(1/2) tends to 0. For
complex characters the zeros are not symmetric in t, so a_chi is complex and genuinely sees both L(s,chi) and its
conjugate. The lower first zeros (3.7 to 6.6, against 14.1 for zeta) give much larger coefficients, so the
L-function zeros dominate a twisted horocycle far more visibly than the zeta zeros dominate the plain one.

Also: the Mirzakhani-Zograf run reached g = 12, with a_g = 2.15792771813311 and sqrt(g)(a_g - 2) = 0.54708, before
it was stopped at its time limit.

## Where zeta enters our own objects: simple geodesics as primitive points of the stable-norm ball (`poc/farey/simple_zeta.py`)

**Exact identities (symbolic).** By McShane-Rivin, simple closed geodesics on a one-holed or cusped torus correspond to
primitive v in Z^2 up to sign, with length l = N(v), where N is the stable norm (convex and homogeneous). Homogeneity
and Moebius inversion give, for every such surface:

    D(s) = sum_{gamma simple} l_gamma^-s = Z_B(s) / (2 zeta(s)),      Z_B(s) = sum_{v in Z^2 \ 0} N(v)^-s,
    P(R) - (3/pi^2) Area(B) R^2 = (1/2) sum_{d >= 1} mu(d) E_B(R/d) - (1/2) Area(B) R^2 sum_{d > R/l_sys} mu(d)/d^2,

Here P(R) = #{simple gamma : l <= R}, and E_B(R) = #{v != 0 : N(v) <= R} - Area(B) R^2 is the lattice-point error of
the stable-norm ball B. So the counting error splits exactly into two parts:
- a geometric part: the lattice-point problem for B;
- an arithmetic part: the tail of sum mu(d)/d^2. That is o(R) unconditionally and O(R^(1/2+eps)) under RH.

The Riemann zeros are formally poles of D(s), with residues Z_B(rho)/(2 zeta'(rho)). They separate from the
geometric part only if Z_B continues past Re s = 1/2, which needs E_B = o(R^(1/2)).

**Check, modular torus, R <= 1000, 271 050 simple geodesics.** Area(B) = 0.891803166 with N = l; the docs' 3.5672
uses N = l/2.
- P/R^2 = 0.271048, against (3/pi^2) Area = 0.271076.
- E_B has envelope about R^0.54 (22 to 72 over the range), circle-problem behaviour.
- The Moebius (arithmetic) part alone stays below 11.
- The total error P - main grows like R^0.44 to R^0.54 and is dominated by E_B.

So the zeta zeros are present, but at the same R^(1/2) scale as the lattice-point error of B, and numerically they
are swamped by it. RH would bound the arithmetic half. The geometric half is a lattice-point problem for a convex body
whose boundary is a polygon with a corner at every rational direction. Its corner jumps are exactly our gap law, and
its dual area is our Sigma g N.

**Our gap-weighted series are non-arithmetic.** Since g(v) ~ 4 e^(-N(v)), any Dirichlet series sum g(v)^a N(v)^-s
converges absolutely for all s, so it is entire and has no zeta factor. The gap law, the dual-area identity, the Hines
identities and the pi^2 law involve neither zeta nor RH. The only route from them to the Riemann zeros is the lattice
problem of B.

## The lattice error of the stable-norm ball: B is a polygon of exact faces (`poc/farey/ball_lattice*.py`, `polygon_control.py`)

**Symbolic structure.** Fix a corner v with Farey neighbour w, and write t_k = trace(kv + w). Then t_k = A lambda^k + B lambda^-k,
with lambda = e^(N(v)/2) and A, B fixed by t_0 = t_w and t_1 = t_(v+w). Hence

    N(kv + w) = k N(v) + c(v,w) + O(lambda^-2k),     c(v,w) = 2 log A = 2 log[(t_(v+w) - t_w/lambda) / sqrt(t_v^2 - 4)].

So next to each corner, B has a face that is flat up to exponentially small error: the line N(v) a + c(v,w) b = 1 in the
basis (v, w). The same holds for N(kv + jw) with fixed j. The two faces at a corner satisfy

    c(v,w) + c(v,-w) = 2 log(AB),   AB = (t_0 t_2 - t_1^2)/(lambda - 1/lambda)^2 = (t_v^2 - mu)/(t_v^2 - 4),

using the Markoff relation. This is exactly the gap law, in the normalization N = l. **The gap law is the sum of the
offsets of the two flat faces meeting at the corner.** So B is a polygon with one pair of faces per rational corner;
only the faces' far ends are curved.

Checked at 30 digits for v = e0 of the modular torus:
- N0 = 2 log phi^2, and c(e0,e1) = -0.374636985217088 (closed form and limit agree).
- Face flatness: 0.375, 0.050, 0.0073, 0.0011, ..., about (phi^-4)^k.
- N(k e0 + 2 e1) - (k N0 + 2c) = 1e-8 at k = 21.
- A B = 9/5 = t^2/(t^2 - 4).

**Consequence for the lattice error.** Each face is a lattice-triangle edge, and its error is a Birkhoff sum of the
rotation by -c(v,w)/N(v). A face at corner v has length about R/N(v)^2 in R B, so the faces with N(v) <= sqrt(R)
matter, and there are about R of them. Independent signs then predict an error of about sqrt(R) times a slowly growing
factor. Faces with near-rational offsets produce bursts. For v = e0, -c/N0 = [0; 5, 7, 3, 1, 37, 2, ...]: the partial
quotient 37 after the denominator 149 predicts resonance over R from about 10^2 to 6 x 10^3.

**Numerics.** 11.45 million simple geodesics; rms of E_B over windows [R, 2R], two independent seeds agreeing to 3%.

| window R | 100 | 200 | 400 | 800 | 1600 | 3200 |
|---|---|---|---|---|---|---|
| rms E_B | 9.6 | 12.5 | 18.4 | 32.9 | 55.3 | 83.3 |
| rms E_disk (same area) | 14.9 | 20.3 | 28.0 | 38.0 | 57.2 | 77.8 |
| E_B / sqrt(R_mid) | 0.79 | 0.72 | 0.75 | 0.95 | 1.13 | 1.20 |

- Local exponents for B: 0.38, 0.56, 0.84, 0.75, 0.59. The burst sits in the predicted resonance range and is fading.
- For the disk, E/sqrt(R) stays at 1.15 +- 0.05.
- E_B shows no periodicity in R at the systole or any other short length (Fourier coefficients about 0.01).
- Polygon controls: the 36-corner truncation of B grows like B. The same polygon under a generic area-preserving shear
  stays flat, with local exponents 0.02 to 0.14. Small perturbations go either way, depending on whether some face lands
  near a rational slope. So the growth comes from how B's faces sit relative to Z^2, as the face formula says.

**Verdict on the Riemann zeros.** E_B is at least of order sqrt(R), probably with a slowly growing factor. Then
Z_B(s) = Area s/(s-2) + s int E_B R^(-s-1) dR does not continue past Re s = 1/2. The terms R^rho from the zeros of
zeta, of size R^(1/2), stay entangled with the geometric error for this single surface. Separating them would need
averaging that kills E_B but not the Moebius tail. The full Weil-Petersson average kills both: Mirzakhani integration
makes the averaged count exactly quadratic, and the Moebius sum then closes with no tail.

## Partial (twist) average: an exact arithmetic core, but the tips keep a lattice problem (`poc/farey/twist_*.py`)

**Unfolding (exact).** In Fenchel-Nielsen coordinates (a, tau) for a curve alpha, the full Dehn twist maps the class
(r, q) to (r + q, q). For any weight w, the twist average of sum_gamma w(l_gamma) therefore equals

    w(a) + (1/a) sum_{q>=1} sum_{r in (Z/q)^*} int_R w(l_{r,q}(tau)) dtau,

a one-dimensional sum over q. Here w is the Riesz weight (R - l)_+.

**V-profile (exact asymptotics, 40 digits).** On the cusped torus with alpha = e0 (trace 3), every class satisfies

    l_{r,q}(tau) = q |tau - tau0(r,q)| + q log(9/5) + o(1)   as |tau| -> infinity.

- The slopes are exactly +-q.
- tau0 is linear in r/q.
- The height is exactly q times the gap law of alpha, log(t^2/(t^2 - 4)) at t = 3, for every r.

This was checked for all r at q = 1, 2, 3, 5, 7, 8, 13. So the wings contribute the arithmetic core

    (g^2/a) sum_{q<=X} (phi(q)/q)(X - q)^2,   X = R/g,

whose explicit formula is (g^2/a)[2X^3/pi^2 - X/3 + sum_rho 2 zeta(rho-1) X^(rho+1) / ((rho-1) rho (rho+1) zeta'(rho))].
This was verified against the direct sum with 100 zeros to 1e-3 or better for R from 30 to 400. The first zero's
coefficient is 1.09e-3.

**What the numerics show (2290 classes, R <= 150).**
- The twist average cuts the residual against a cubic from 23.5 (single modular torus) to 3.56, a factor of 7.
- The residual still grows like R^(3/2): 5.2e-3, 5.8e-3 and 3.5e-3 times R^1.5 on three ranges. The core's zero terms are
  5 to 7 times smaller throughout.
- Fitting the predicted Z(R) gives a meaningless beta = -3. A free fit at gamma_1 has the wrong amplitude and phase.

The obstruction is at the tips. min over tau of l_{r,q} is about 1.73 q, far above the asymptotic height 0.588 q, and
it depends on r/q: its spread is 0.04 q at q = 5 and 0.15 q at q = 60, converging to a limit profile mu(r/q). So
counting tips is again a 2D lattice problem, the points (r, q) with q mu(r/q) <= R, and its error has the same order
R^(kappa + 1/2) as the zero terms for every Riesz order kappa.

**Verdict.** Averaging over twists alone isolates an exact zeta core, which is the gap law appearing as the V-height,
but it does not yet expose the zeros: on the modular torus the tip lattice error is several times larger at every
scale. The next candidate is a local 2D average: uniform in tau, plus a smooth bump in a away from 0. The bump damps the
tip lattice error by averaging over dilations. The core's zero terms only acquire the factor int bump(a) g(a)^-(rho+1) da,
which is nonzero for the low zeros. The systole stays bounded, so the Moebius tail survives, unlike the full
Weil-Petersson average.

## Correction, and the result: smoothed simple-geodesic counts carry the Riemann zeros on a single surface (`poc/farey/local_average*.py`, `zero_truncation.py`)

**Explicit formula (exact, symbolic).** Let A(R) = sum over all lattice classes v != 0 of (R - N(v))_+, using the
stable norm and its homogeneity, and P(R) = sum over simple gamma of (R - l_gamma)_+. Then P(R) = sum_d mu(d) d A(R/d),
so P^(s) = A^(s)/zeta(s-1). If A = c3 R^3 + c2 R^2 + c1 R + c0 + e_A with e_A = O(R^theta), theta < 3/2, then

    P(R) = (6/pi^2) c3 R^3 - 2 c1 R - 12 c0 + sum_rho 2 Re[A^(1+rho) R^(1+rho) / zeta'(rho)] + O(R^(theta+eps)).

The R^2 term drops out because zeta(1) is a pole. A^(1+rho) is the continued Mellin transform of A, computed from the data.

**Data.** R <= 150. Coefficients come from A alone, with no free parameters. The zero sum is truncated at 30 zeros.

| surface or average | rms of e_A | rms of P residual | rms of predicted zero sum | correlation | mismatch |
|---|---|---|---|---|---|
| single modular torus | 0.661 | 24.89 | 24.77 | 0.9964 | 2.12 (8.5%) |
| twist average (sigma_a = 0) | 0.117 | 3.87 | 3.87 | 0.9937 | 0.44 (11%) |
| twist plus a-bump sigma_a = 0.03 | 0.040 | 3.72 | 3.72 | 0.9952 | 0.36 (9.8%) |
| twist plus a-bump sigma_a = 0.06 | 0.050 | 3.42 | 3.42 | 0.9942 | 0.37 (11%) |

- With 1, 3, 10, 30 and 60 zeros, the single-torus mismatch is 67%, 61%, 18%, 8.5% and 5.7%.
- Beyond about 60 zeros the estimated coefficients stop decaying, a floor set by estimating A^ from R <= 150.
- Spectral peaks of residual/R^1.5 in log R include 14.0, 21.7 to 22.8, 29 and 37.5, against zeros at 14.13, 21.02,
  30.42 and 37.59. The resolution is about +-3, so leakage peaks also appear.

**What was wrong before.**
1. "The zeros stay entangled for a single surface" holds for the sharp count only. Riesz smoothing integrates zero
   terms R^rho into R^(1+rho)/(1+rho), gaining a power of R, while the lattice error oscillates in R and gains nothing.
   It stays about R^(1/2), against R^(3/2) for the zero terms. Smoothing, not averaging, separates them.
2. "The tips leave a lattice error of the same order" was wrong. The twist-average residual that the V-core failed to
   explain is the zero sum itself: its coefficients A^(1+rho) depend on the whole small-R structure, tips included, not
   only on the V-core. Averaging lowers e_A, from 0.66 to 0.04, but is not needed.

**Reading.** On a single hyperbolic torus, the Riesz-smoothed count of simple closed geodesics is a smooth cubic plus a
sum over the Riemann zeros, with geometric coefficients A^(1+rho)/zeta'(rho), plus an error of order R^(1/2). Under
RH the oscillating part is O(R^(3/2+eps)). A zero off the line at beta would appear as R^(1+beta). The mechanism is the
standard one for primitive lattice points, here carried by the stable-norm ball. The gap law enters through B's
corner and face structure, and through the twist V-height q log(9/5).

## Poisson-dual of the stable norm: a Voronoi series over simple geodesics (`poc/farey/stable_voronoi*.py`)

**1. Fourier transform as a sum over corners (exact).** N is linear on each face-cone and its gradient is pure-jump
(proved earlier). Integrating Phi(N) over the cones and telescoping gives, for any profile Phi,

    F[Phi(N)](xi) = (1/2 pi i) sum_{v primitive, +-} G(v) <v,xi> K_Phi(<v,xi>/N(v)) / (<J n_v^+, xi> <J n_v^-, xi>),
    K_Phi(a) = int_0^inf Phi(t) e^{-2 pi i t a} dt,   n_v^+ - n_v^- = G(v) J v,   G(v) = 2 log(t_v^2/(t_v^2 - 4)).

- The gap law is the vector jump of the gradient at each corner. The one-sided gradients have closed forms from the
  face offsets c(v, +-w).
- <v,xi> is an integer, and terms with <v,xi> = 0 vanish.

Checks with Phi = e^-t:
- The jump identity holds to 1e-13.
- The corner sum built from B's closed-form data equals the exact Fourier transform of the polygon on the corners with
  N <= 40, to 1e-10 at five xi.
- Brute-force quadrature agrees to 1e-3, its grid error.
- Poisson, sum over x of e^(-eps N(x)) against the dual sum: the truncation error halves when M doubles (|xi|^-3 decay).
  Extrapolated, 2.271886 against 2.271892 at eps = 1, and 7.524652 against 7.524657 at eps = 1/2.

**2. The lattice error is a Voronoi series (exact).** Sum the dual vectors along each line <v,xi> = k in closed form,
using sum_j 1/((j+a)(j+b)) = pi (cot pi a - cot pi b)/(b - a). The gap law cancels:

    E_B(R) = sum_{gamma simple} sum_{k>=1} [cot(pi k a_gamma^+) - cot(pi k a_gamma^-)]/(pi k) * cos(2 pi k R / l_gamma) + C,
    a^+- = <J n^+-, xi0>/l   (any xi0 with <v, xi0> = 1),   a^- - a^+ = G(v)/l_gamma.

Each simple geodesic contributes a periodic function of R with period equal to its own length. Its amplitudes are the
Hardy-Littlewood cotangent sums of the rotation numbers of the two faces at its corner. Checked with Gaussian
smoothing sigma = 0.5 and 0.3, against the actual smoothed lattice count for R in [20, 100], with 4590 geodesics:
the residual is 3.2e-10, the correlation 1.000000, and the constant C = -0.6537 is the same at both sigma. Its
closed form is open: the undamped cotangent series does not converge numerically. For a long geodesic,
a^+ - a^- = -G/l = O(e^-l), so its amplitude is about (G/l) pi k csc^2(pi k a). It is negligible unless k a is close to an
integer. This makes the face-resonance burst mechanism of the earlier section exact.

**3. The Riemann-zero amplitudes in closed form.** With A(R) = sum over v of (R - N(v))_+, A^(s) = Z_B(s-1)/(s(s-1)).
So in the smoothed simple-geodesic count (mod sign) the zero rho has coefficient

    Z_B(rho) / (2 rho (rho+1) zeta'(rho)).

Z_B continues to Re s > theta_A - 1, about -1/2, because the Riesz-smoothed error is O(R^(1/2)); my earlier claim that
it stops at 1/2 was wrong. Check: Z_B(rho_1) from a smoothed lattice sum is 0.6457 + 5.9625i, stable over X = 30 to
60. The predicted |coefficient| is 1.8806e-2, against 1.88e-2 fitted from the simple-geodesic data in the previous
section.

## Z_B(0): a toric twelve, a McShane-type sum, and a Weil-Petersson average of zero (`poc/farey/stable_dual_zeta.py`, `stable_zeta_zero*.py`)

**A dual formula that does not converge, recorded as negative.** Mellin-transforming the Voronoi series term by term
suggests Z_B(s) = -((2 pi)^s/pi) Gamma(1-s) cos(pi s/2) sum_gamma l^-s [C_{a+}(1-s) - C_{a-}(1-s)], with
C_a(w) = sum_k cot(pi k a) k^-w. It does not hold as written. The cosine Mellin transforms need -1 < Re s < 0, while at a
resonance (||ka|| about 1/k) a cotangent term has size about k^(Re s + 1), so the series needs Re s < -1. Numerically the
partial sums, even Riesz-weighted up to k = 10^6, wander: at s = -0.3 they range from -3.7 to 1.4, against the direct
value -0.436. The sum over geodesics converges fast, and the trouble is entirely in k. The dual side must stay a
lattice-ordered double sum.

**Z_B(0) = -0.6537, three independent ways.**
- Theta function: Theta(eps) - 1 - 2 Area/eps^2 = -0.653608 at eps = 0.015, using 4.3 million geodesics.
  Extrapolation gives -0.6526 to -0.6541.
- Riesz linear coefficient: -0.65377 free, -0.65365 with R^3 = Area/3 and R^2 = 0 imposed. The free fit gives exactly
  Area/3 for R^3 and 2e-7 for R^2.
- The mean C of the lattice error: -0.6537.

So Z_B(0) is not -1, the quadratic-form value. Rough check: for the square max(|x|,|y|), Z(0) = 8 zeta(-1) = -2/3.

**Theorem (polygon norms, proved here).** Let N be a symmetric norm whose unit ball is a polygon with corners on
primitive lattice rays. Refine to a complete unimodular fan v_1, ..., v_n with v_(i-1) + v_(i+1) = b_i v_i, so that N is
linear on each cone. Then

    Z_N(0) = -1 + (1/12) sum_i G(v_i)/N(v_i),     G(v_i) = N(v_(i-1)) + N(v_(i+1)) - b_i N(v_i)   (the gradient jump; n^+ - n^- = G J v).

Proof:
1. Z_N(s) = sum over cones of the Barnes zeta zeta_2(s; w1 + w2 | w1, w2) + zeta(s) sum over rays of N(v_i)^-s, with
   (w1, w2) = (N_i, N_(i+1)).
2. Barnes gives zeta_2(0; w1 + w2 | w1, w2) = (w1^2 + w2^2 + 3 w1 w2)/(12 w1 w2), and zeta(0) = -1/2.
3. Hence Z_N(0) = -n/4 + (1/12) sum_i (N_(i-1) + N_(i+1))/N_i.
4. The toric-surface identity sum_i b_i = 3n - 12 turns this into the stated form. The "12" is Noether's.

Checks: the square gives -1 + 4/12 = -2/3, and ellipses, with no corners, give -1.

**For the stable norm** every primitive direction is a corner and the gradient is pure-jump, with jump G = 2g, where
g = log(t^2/(t^2 - 4)) is the gap law. The limit of the theorem reads

    Z_B(0) = -1 + (1/3) sum_{gamma simple} g_gamma / l_gamma.

On the modular torus (1/3) sum g/l = 0.346348 (with G = 2g, sum G/l = 2.078090; ratio 1/6 to 5e-6), against
1 + Z_B(0) = 0.34635 +- 2e-4. The limit from polygons to B is not proved; the numerics support it.

**Weil-Petersson average (exact, given the limit formula).** g depends on l alone: g = log((cosh l + cosh(L/2))/(cosh l - 1)),
which reduces to 2 log coth(l/2) at the cusp. Use Mirzakhani integration with the convention of the earlier average
sections: the integral of sum_gamma F(l_gamma) is int F(l) l dl, and Vol = (L^2 + 4 pi^2)/24. With
int_0^inf log((cosh x + cosh a)/(cosh x - 1)) dx = (pi^2 + a^2)/2 and a = L/2. Proof: at a = 0 the integrand is
2 log coth(x/2) = 4 sum_{n odd} e^(-nx)/n, which integrates to pi^2/2; and d/da of the integral is
sinh a * int dx/(cosh x + cosh a) = a. Numerical quadrature reproduces the a-dependence exactly but carries a
constant error of about 1e-3 from the log singularity at x = 0:

    int (1/3) sum_gamma g/l = (1/3)(L^2 + 4 pi^2)/8 = Vol,   so   < Z_B(0) >_WP = 0   for every boundary length L.

Individual surfaces sit below the average: Z_B(0) = -0.654 on the modular torus. This is the same pattern as the pi^2
product law.

## Z_B at the negative integers: Barnes cone sums, trivial zeros at odd -m, and Farey-cell sums (`poc/farey/stable_zeta_negative.py`)

**Exact for polygon norms** with corners on lattice rays, refined to a unimodular fan. With zeta_2 the Barnes double zeta,

    Z_N(-m) = sum_cones T_m(N_i, N_(i+1)),   T_m(a,b) = zeta_2(-m; a+b | a, b) + zeta(-m)(a^m + b^m)/2,

and zeta_2(-m; w1+w2 | w1, w2) = m!/(m+2)! B_{2,m+2}, read off from t^2/((1 - e^(-w1 t))(1 - e^(-w2 t))). Symbolically (sympy):

| m | zeta_2(-m; w1+w2 \| w1, w2) | per-cone T_m |
|---|---|---|
| 0 | (w1^2 + 3 w1 w2 + w2^2)/(12 w1 w2) | (w1^2 - 3 w1 w2 + w2^2)/(12 w1 w2) |
| 1 | (w1 + w2)/24 | 0 |
| 2 | -(w1^4 - 5 w1^2 w2^2 + w2^4)/(360 w1 w2) | the same |
| 3 | -(w1 + w2)(w1^2 - w1 w2 + w2^2)/240 | 0 |
| 4 | (w1^2 + w2^2)(2 w1^4 - 9 w1^2 w2^2 + 2 w2^4)/(2520 w1 w2) | the same |
| 5 | (w1 + w2)(w1^4 - w1^3 w2 + w1^2 w2^2 - w1 w2^3 + w2^4)/504 | 0 |

- **Trivial zeros at the negative odd integers.** Z_N(-1) = Z_N(-3) = Z_N(-5) = 0 for every polygon norm. Quadratic forms
  vanish at every negative integer; here the even values are generally nonzero.
- **Square check.** It has 8 rays of norm 1, so Z(-2) = 8 T_2(1,1) = 1/15 = 8 zeta(-3).
- **Refinement invariance.** Inserting a ray where N stays linear leaves the cone sum unchanged. Checked by hand for T_2.

**For the stable norm.** Start from the root hexagon (e0, e0+e1, e1 and their negatives, all of length l3). Insert the
mediant corner of each Farey cell (u, w) with c = N(u + w) <= N(u) + N(w). The polygons B_T increase to B, and

    Z_B(-m) = 6 T_m(l3, l3) + 2 sum_{Farey cells} [T_m(a, c) + T_m(c, b) - T_m(a, b)],   a = N(u), b = N(w), c = N(mediant).

These are cell sums over Markoff triples, like the McShane cell recursion. The atoms are exponentially small in depth;
cutting at N <= 35 or N <= 45 agrees to 1e-12. Results against the theta expansion
Theta(eps) - 1 = 2 Area/eps^2 + sum_n Z(-n)(-eps)^n/n!, fitted with degree 5 on eps in [0.025, 0.4]:

| | Farey-cell Barnes sum | theta fit |
|---|---|---|
| Z_B(0) | -0.653651620281668 | -0.653652 |
| Z_B(-1) | 0 | -0.000007 |
| Z_B(-2) | 0.387555229910911 | 0.387172 (limited by the fit) |
| Z_B(-3) | 0 | -0.014 (fit noise) |
| Z_B(-4) | -2.116651789288 | |

The cell sum for Z_B(0) also equals the toric formula -1 + (1/3) sum g/l = -0.653652. The theta function is computed
directly from B's lattice, so this agreement confirms the polygon-to-B limit numerically at m = 0 and m = 2. A proof is
still open.

## Z_B is meromorphic on C with one pole: the Farey-cell decomposition (`poc/farey/stable_zeta_continuation.py`)

**Exact cell decomposition.** Insert the mediant m = u + w of a Farey cell (u, w), with corner deficiency
delta = N_u + N_w - N_m. The gauge changes only inside that cone: N(au + bw) = a N_u + b N_w - delta min(a, b). Hence

    Z_B(s) = 6 l3^-s zeta(s - 1) + 2 sum_{Farey cells} Delta_cell(s),
    Delta_cell(s) = zeta_2(s; N_u+N_m | N_u, N_m) + zeta_2(s; N_m+N_w | N_m, N_w) + zeta(s) N_m^-s - zeta_2(s; N_u+N_w | N_u, N_w),

where zeta_2 is the Barnes double zeta. The root hexagon contributes 6 l^-s (zeta(s-1) - zeta(s)) + 6 zeta(s) l^-s.

Properties:
- Delta_cell vanishes identically when delta = 0, because the same lattice points are counted on both sides.
- Its residues at s = 1 cancel; numerically the t^-1 coefficient is below 6e-42 in every cell.
- Its residue at s = 2 is the cell's area increment.

**The deficiencies are exponentially small.** The Markoff relation gives t_m t_d = t_u^2 + t_w^2 exactly in every cell,
which cancels the leading terms of delta. Numerically, over 849 cells,

    8 <= delta e^{N_u + N_w} <= 15.23,   and   delta e^{max(N_u, N_w)} <= 2.22.

The lower value 8 is approached deep in the tree.

**Consequence.** Bound Delta_cell(s) by delta times polynomial growth in N, uniformly on compact sets of s away from
s = 2. Since delta = O(e^-(N_u + N_w)), the cell sum converges locally uniformly on C \ {2}. For Re s > 2 it equals Z_B,
because every lattice point's gauge is exact after finitely many insertions. So:

- Z_B is meromorphic on C, with a single simple pole at s = 2 of residue 2 Area(B).
- The cell sum evaluates Z_B everywhere.
- Every polygon formula passes to the limit at the negative integers, which closes the open point of the last two
  sections: Z_B(-1) = Z_B(-3) = ... = 0; Z_B(-2k) are the cell sums; and Z_B(0) = -1 + (1/3) sum g/l. For the last,
  the partial cell sums are the Z_{B_T}(0), and the corner jumps G_T(v) decrease to G(v), with sum G/N convergent.
- The bound on Delta_cell is sketched, not written out in full.

**Checks.** Delta_cell is computed from its Mellin integral, with the small-t part replaced by the exact Bernoulli series
of 1/(e^x - 1), 40 terms, on t < 0.05.
- s = 3: the cell sum gives 1.466432453, against the direct sum 1.465998 plus a tail estimate of 4.3e-4.
- s = rho_1: cells up to N = 12, 18 and 24 give 0.6457574867 + 5.962834096i, 0.6457543857 + 5.962831556i and
  0.64575439 + 5.962831543i. The smoothed lattice sums of the earlier section, 0.64423, 0.64546 and 0.64566 (real
  parts at X = 30, 45 and 60), converge toward this. So Z_B(rho_1) = 0.64575439 + 5.96283154i to about 9 digits, and the
  Riemann-zero amplitude Z_B(rho)/(2 rho (rho+1) zeta'(rho)) is now known to that precision.
- s = 1/2: Z_B = -1.1064650681.

## Literature check for the stable-norm zeta results (2026-11-26)

arXiv abstracts and full texts were read through the shell. The web-fetch tool could not reach arxiv.org. Four
directly relevant sources:

- **Doan, Li, Nguyen, "Stable-norm boundary geometry on once-punctured tori", arXiv 2605.14574** (v1 14 May 2026,
  v3 9 Oct 2026).
  - Theorem 1.2: rational directions are genuine corners with exponentially small exterior angles.
  - Proposition 4.1: computes the corner exactly, lambda(u) - mu(u) = 2 log A+ + 2 log A- = 4 log coth(L/2). This is our
    gradient jump G = 2g, with the same A+ A- product.
  - Proof of Theorem 1.3: the rational corners account for the full normal turn, which is our pure-jump result.
  - Theorem 1.3: Area(B*) = 4 sum l log coth(l/2), the dual-area identity already attributed to them.
  - Theorem 1.4: (log L)^2 bounds for points on dilated boundaries.
  - So the corner structure, the gap as a jump and pure-jump are theirs, at least in the l/2-normalised form. Our
    face-offset formula c(v,w) = 2 log A is the same computation.
- **Risager, "Counting Markov triples and simple geodesics", arXiv 2610.36069** (26-28 Oct 2026).
  - Theorem 12: N_X(R) = vol(B_X) R^2 + O(R/(log R)^(3/2)) for the full lattice count of the modular torus. It is
    proved by smoothing, Poisson summation and bounds on Fourier coefficients along radial lines, using the DLN
    turn estimates.
  - Theorem 13 and Theorem 1: Moebius inversion with zero-free regions gives M(x) = C log^2(3x) + o(log x),
    unconditionally via Vinogradov-Korobov and sharper under a "quasi-RH" zero-free half-plane.
  - It quotes the McShane-Rivin conjecture that the error is (log x)^(1/2 + eps), i.e. R^(1/2 + eps), and their claim
    that for a dense set of tori the error is not o(L).
  - No exact Fourier transform, Voronoi series, zeta function Z_B, explicit formula over zeros, or Barnes decomposition.
- **Kalinin, Lupercio, Shkolnikov, "Residues of a tropical zeta function for convex domains", arXiv 2604.21709**
  (Apr-Jun 2026). A different zeta, the integral of rho^(s-2) of a tropical distance function. For rational polygons it
  is meromorphic with residue -K^2 at s = 0, the toric canonical class, and its boundary series runs over Farey pairs.
  Same family of ideas as our toric "12", K^2 = 12 - n, but not our Z_N = sum N(v)^-s.
- **Garoufalidis and Pommersheim, JAMS 14 (2001); Shintani.** Zeta values at negative integers of linear forms on
  two-dimensional cones, through Todd power series and Dedekind sums. Our cone terms are Shintani/Barnes zetas of a
  linear form on unimodular cones, so the per-cone values at -m are classical. The global assembly
  Z_N(0) = -1 + (1/12) sum G/N via sum b_i = 3n - 12 is an elementary consequence; it may be stated somewhere, and we
  did not find it.
- Also: Massart, GAFA 1997, local structure of stable-norm balls at rational directions; Sorrentino-Veselov
  (arXiv 1707.03901), differentiability of Fock's psi exactly at the irrationals.
- Searches for a Fourier transform, Poisson summation or zeta function of the stable norm itself found nothing
  beyond Risager's bounds.

**What appears to be new here.** None of these was found in the sources above.
1. The exact Fourier transform of Phi(N) as a gap-weighted corner sum, and the exact Voronoi series for E_B with
   Hardy-Littlewood cotangent amplitudes of the face rotation numbers. Risager has only bounds on these coefficients.
2. The meromorphic continuation of Z_B to C with one pole, through the Barnes Farey-cell decomposition, with
   delta ~ e^-(N_u + N_w).
3. The explicit formula over the Riemann zeros for smoothed simple-geodesic counts on a single torus, with amplitudes
   Z_B(rho)/(2 rho (rho+1) zeta'(rho)). Risager uses only zero-free regions.
4. Z_B(0) = -1 + (1/3) sum g/l, the vanishing at the negative odd integers, the cell sums at the negative even integers,
   and <Z_B(0)>_WP = 0.

Context: Risager's Theorem 12 bound R/(log R)^(3/2) is far above what we measure (rms about R^(1/2) times a slowly
growing factor), which is consistent with the McShane-Rivin conjecture. The Voronoi series is a natural tool for it.

**Face rotation numbers, resonances, and Risager's Lemma 5.**
- In our Voronoi series the amplitude of a geodesic blows up exactly when a face rotation number a^+- = c(v, +-w)/l_v is
  rational. Then cot(pi k a) is infinite for k divisible by the denominator, lattice points line up along a dilated face,
  and the error grows linearly in R. Rational faces occur on a dense set of tori, consistent with McShane-Rivin's claim
  that the error is not o(L) there.
- On the modular torus, e.g. at v = e0, A = 3/(phi sqrt 5) and lambda^2 = phi^2, so a = log(3/(phi sqrt5))/(2 log phi)
  = -0.1946320547976377. Gelfond-Schneider makes this irrational, in fact transcendental.
- Risager's Lemma 5 (arXiv 2610.36069) is this separation, in norm form: |2 log(r^d(v) A+^-d(u))| >= e^(-M |d| A^2). It
  uses that r is a unit and N(A+-) = t^2/(t^2 - 4) > 1, his Proposition 4.
- A Baker-Wuestholz lower bound for this two-log linear form would give roughly |d|^(-C A^2) instead. Whether that
  improves his final exponent has not been checked.

**Direct moduli check of <Z_B(0)> = 0** (`poc/farey/wp_zeta0.py`; the same Fenchel-Nielsen domain and quadrature as
`wp_average.py`). At L = 0, the integral of (1 + Z_B(0)) is 1.645385 on the 48 x 20 grid and 1.646259 on 72 x 28,
against the predicted Vol = pi^2/6 = 1.644934. The averages are 0.99951 and 0.99855. The quadrature's own volume is off
by 0.08% and 0.2%, so this agrees with <Z_B(0)> = 0 to within the quadrature error. The runs at L = 2 and 5 were still
going when this was written.

## Write-up, and proofs of the remaining steps (2026-11-26)

The write-up is a Docs artifact, "The Lattice Zeta Function of the Stable-Norm Ball"
(https://claude.ai/artifact/SEpspK3dKxbyqgJ7DuY6rD). New in it, beyond the earlier sections:

- **Closed form of the cell integrand.** D(t) = e^{ct}(e^{delta t} - 1)/((e^{at}-1)(e^{bt}-1)(e^{ct}-1)), from
  1 + 1/(e^{at}-1) + 1/(e^{bt}-1) = (e^{(a+b)t}-1)/((e^{at}-1)(e^{bt}-1)). It vanishes at delta = 0. Its Laurent
  coefficients are d_-2 = delta/(abc) and d_-1 = 0 identically, so each cell has only the s = 2 pole.
  Checked to 15 digits, with d_-1 = 1e-33 (`poc/farey/cell_lemmas.py`).
- **The deficiencies.** delta = 2[-log(1 + eta) + log(1 + lambda_m^-2)] with eta = -3/(lambda_u^2 lambda_w^2) + ...,
  so delta e^{N_u + N_w} -> 8. H = delta e^{N_u + N_w} is a continuous function of (1/t_u, 1/t_w) on [0, 1/3]^2 and
  hence bounded. Numerically H decreases in each trace: H(3,3) = 15.2305, H(3, inf) = 9.3666, H(inf, inf) = 8.
- **Odd negative integers, all m.** x/(1 - e^-x) = x/2 + (x/2) coth(x/2), and the second term is even, so
  zeta_2(-m; a+b | a, b) = -zeta(-m)(a^m + b^m)/2 for every odd m. Hence T_m = 0 and Z_N(-m) = Z_B(-m) = 0.
- **The limit for Z_B(0).** G_T(v) decreases to G(v), and at insertion G_T(v) equals the cell's delta. Dominated
  convergence passes the toric formula to B.
- **Non-locality of Z(-2).** The hexagon norm, Z(-2) = 6 zeta(-3) = 1/20, and the square, Z(-2) = 8 zeta(-3) = 1/15,
  have SL(2,Z)-equivalent corner germs but per-corner values 1/120 and 1/60. So no corner-local formula exists for
  Z(-2); Z(0) is local only through Noether's identity.

Still open: explicit constants in Step 4 of the continuation proof; polynomial vertical growth of Z_B, needed for the
explicit formula; monotonicity of H; and the Weil-Petersson average of Z_B(-2), via Farey pairs.

## The averaged lattice count is exact; <Z_B(s)> = 0; Farey beat packets drive the lattice error (2026-11-26)

**1. On average over moduli the stable-norm ball has no lattice-point error at any scale.**

    int_M #{v != 0 : N_X(v) <= t} dV = 2 sum_{k>=1} int_0^{t/k} l dl = zeta(2) t^2 = int_M Area(B_X) t^2 dV,

in the normalisation int_M sum_gamma F(l_gamma) = int F(l) l dl, Vol = (L^2 + 4 pi^2)/24, for every L. Since
Z_X(s) = s int_0^inf (A_X(t) - Area t^2) t^(-s-1) dt, Fubini gives int_M Z_X(s) dV = 0 for 1 < Re s < 2. Fubini needs
the convex lattice bound |E| <= C(1 + t Perim(B_X)) with Perim(B_X) ~ 1/sys, and the moduli measure is about sys
d(sys); both sides of the strip are then integrable for sigma < 2, and the large-t side for sigma > 1. By analytic
continuation <Z_B(s)> = 0 wherever Z_X(s) stays locally uniformly integrable over moduli. Near the cusp the cell sums
give |Z_X(-m)| ~ (1/sys) polylog(1/sys), which is integrable: at sys = 0.0019, Z(0) = 2440, Z(-2) = -14813,
Z(-4) = 6.6e5. In particular the Riemann-zero amplitudes Z_B(rho) average to 0, which matches the absence of zero terms
in moduli-averaged counts.

Direct check (`poc/farey/wp_zeta_neg.py`, general-surface Farey-cell sums, Fenchel-Nielsen quadrature 40 x 16):
<Z_B(0)> = +0.00014 at L = 0, where the quadrature volume is off by 2e-4. The m = 2 and 4 runs are still going.

**2. The Voronoi series is exact for small smoothing.** It matches the smoothed lattice error at sigma = 0.3, 0.15, 0.08
and 0.05 to 2e-10, 2e-10, 1e-9 and 1e-8, with l <= 40 (`voronoi_small_sigma.py`). So single-geodesic amplitudes far
larger than the actual error are real.

**3. The amplitudes come in Farey beat packets.** For a Farey cell (u, w, m), the resonant terms (k_u, l_u),
(k_w, l_w) and (k_u + k_w, l_m) have frequencies agreeing to |k_u l_w - k_w l_u|/(l_u l_w) up to an O(k delta/l^2)
correction. Their amplitudes nearly cancel. The main example: traces 15 and 39 and their mediant, with k = 31, 42 and 73,
at frequency 5.733158, spread 1.6e-5, amplitudes +16.2, +27.2, -43.8 (each x6 by symmetry), net -0.56
(`beat_partners.py`).

**4. Two packets carry the observed growth.** Keep the 183 terms with |A| > 0.05 and cluster them with gap 1e-3 (34
packets). Treating packets as orthogonal gives rms 7.6, 10.6, 14.3, 27.5, 47.9 and 69.2 for windows w = 100 to 3200,
identical to the full truncated series (l <= 40, frequency <= 6: 8.3 ... 69.3). With frequencies up to 12 the full series
gives 8.8, 11.1, 14.3, 29.7, 50.9 and 73.8, against the measured 9.6, 12.5, 18.4, 32.9, 55.3 and 83.3. The packet at
5.7332 grows from rms 1.9 to 57.6, and the one at 4.2544 (spread 1.1e-3) from 4.8 to 38.0 (`beat_packets.py`).

Consequences:
- The error growth seen for R <= 6400 is the transient opening of two packets with beat periods of about 6e4 and 900.
  Exponent fits at these R do not measure the McShane-Rivin exponent.
- Prediction: the 5.733 packet saturates at rms about (sum |A_j|^2/2)^(1/2), about 94, near R ~ 3-6e4.
- The conjecture E = O(R^(1/2+eps)) is a statement about packets. The sum over Farey cells and convergents k_w/k_u of
  l_w/l_u of (packet amplitude)^2 min(1, (X Delta f)^2) must be at most X^(1+eps). The amplitudes are about
  1/(pi^2 k ||k a||), and Risager's arithmetic separation bounds ||k a|| from below.

(Correction to the first attempt: summing |amplitude|^2 per geodesic, or per length, gives rms about 125 or 300
regardless of X. Those models ignore the packet cancellations, and their failure is what led to the packets.)

## Exact Farey-cell decomposition of the sharp lattice count, and a plateau of the lattice error up to R = 2e6 (2026-11-26)

**Decomposition (exact).** Insert the mediant m of a Farey cell (u, w). Inside the cone the gauge changes from
a l_u + b l_w to a l_u + b l_w - delta min(a, b), at x = au + bw. So

    A(R) = A_root(R) + 2 sum_cells S_cell(R),   S_cell(R) = #{(a, b) >= 1 : a l_u + b l_w - delta min(a, b) <= R < a l_u + b l_w}.

Each cell's discrepancy S_cell - R^2 delta/(2 l_u l_w l_m) is a difference of two Hardy-Littlewood sawtooth sums. Per
branch it is sum_b [psi(x_b) - psi(x_b + b delta/l_u)], with x_b = (R - b l_w)/l_u, i.e. rotations by
alpha = l_w/l_u and alpha' = (l_m - l_u)/l_u, plus the mirror branch. Ostrowski's bound then controls each cell by the
partial quotients of alpha and alpha' up to denominators R/l. Cells with delta R^2 << 1 contribute negligibly, so only
polylog(R) cells matter (`poc/farey/cell_count.py`).

**Validation.** At 8 radii up to R = 1100 the decomposition equals the direct lattice count to every digit printed,
using 93-135 cells. Lowering the cell cutoff from 1e-3 to 1e-7 changes nothing to 1e-6.

**A new algorithm.** E_B(R) for R up to 2e6 with at most 381 cells, about 0.5 s per value. Direct enumeration at
that scale would need about 1e12 points.

| window [w, 2w] | 1e3 | 3e3 | 1e4 | 3e4 | 1e5 | 3e5 | 1e6 |
|---|---|---|---|---|---|---|---|
| rms E_B | 39.5 | 75.6 | 198.5 | 312.0 | 246.4 | 307.0 | 339.7 |
| max \|E_B\| | 99 | 211 | 482 | 841 | 598 | 839 | 758 |
| cells used | 153 | 177 | 201 | 231 | 297 | 339 | 381 |

The lattice error **plateaus** from about 3e4 to 2e6. Growth like R^(1/2) from w = 1e3 would give about 1250 at 1e6.
The apparent R^0.6 growth below 3e4 is a transient carried by a few cells with very large partial quotients
(`cell_ranking.py`, `cell_ranking2.py`):
- the cell (l_u, l_w) = (7.326, 5.407), delta = 2.4e-5, has alpha = [0; 1, 2, 1, 4, 1, 1, 496, ...] and alpha' with 269
  (or 159 in the mirror branch); its rms is 93.7 at w = 3e4;
- the cell (5.407, 1.925) has alpha' = [...; 1, 1, 496, 1, 7].

These are the beat packets of the previous section, seen as single cells.

**Conjecture.** For the modular torus, E_B(R) = R^(o(1)), and is polylogarithmic if the partial quotients of the cell
rotation numbers behave like those of typical reals. Then the geometric part of the simple-geodesic counting error is
negligible, and the McShane-Rivin exponent 1/2 comes from the Moebius / Riemann-zero part: the sharp count's oscillation
is sum_rho Z_B(rho) R^rho/(2 rho zeta'(rho)). The first zero gives an amplitude of about 0.535 R^(1/2) (mod sign). A
test at R up to 2e6 is running (`primitive_large.py`).

(Bookkeeping note: the root hexagon has rational faces, alpha = 1, and its O(R) error cancels against its three root
cells. Ranked per-cell figures exclude them; the "root group" rms printed by `cell_ranking2.py` is a bookkeeping
artefact.)

## The exponent 1/2 is sharp, and arithmetic (2026-11-26; `poc/farey/primitive_large.py`)

The simple-geodesic count at large R: P(R) = (1/2) sum_d mu(d) A(R/d). A(t) comes from direct enumeration for t < 3000
and from the Farey-cell decomposition above that. It reproduces direct counts exactly at R = 500, 1500 and 2900.

| window [w, 2w] | rms of P error | rms(error/sqrt R) | max \|error\|/sqrt R |
|---|---|---|---|
| 1e4 | 94.8 | 0.77 | 1.85 |
| 1e5 | 408.0 | 1.08 | 2.45 |
| 1e6 | 1393.7 | 1.15 | 2.39 |

The simple-geodesic error grows like R^(1/2), while the lattice error E_B plateaus near 300. So the exponent is
arithmetic.

**Theorem (unconditional).** On the modular torus, E_P(R) = P(R) - (3/pi^2) Area R^2 is not O(R^(1/2 - eps)) for any
eps > 0. Proof:
- If E_P = O(R^theta), its Mellin transform is analytic on Re s > theta, so D(s)/s = (Mellin of P) is meromorphic there
  with its only pole at s = 2.
- But D(s) = Z_B(s)/(2 zeta(s)) has a pole at rho_1. Z_B is analytic there (continuation theorem),
  Z_B(rho_1) = 0.64575439 + 5.96283154i != 0, and rho_1 is a simple zero of zeta.
- Hence theta >= 1/2. No hypothesis on the zeros is used.

In Markov terms, M(x) - C log^2(3x) is not O((log x)^(1/2 - eps)). This is the matching lower bound for the McShane-Rivin
conjecture (log x)^(1/2 + eps); Risager's upper bound is o(log x). The same holds on every once-punctured torus with
Z_X(rho) != 0 for some zero rho. That is all of moduli space outside a proper real-analytic subset, since Z_X(rho_1) is
real-analytic in X and averages to 0 over moduli, so it is not identically zero.

## Making the lower bound airtight, an explicit Omega_+- constant, and the conditional theorem for E_B (2026-11-26)

**Certificate for Z_B(rho_1) != 0** (`poc/farey/certify_rho1.py`).
- The 261 cells with max N <= 22 are computed with mpmath; the quadrature plus series error totals 3.1e-21.
- Lambda = |Delta_cell(rho_1)|/delta ranges from 0.018 to 2.69, and Lambda/(a+b)^4 falls from 1.2e-2 to 1.1e-7 across the
  cells. The envelope K (a+b)^4 with K = 0.0245 (2x margin), together with delta <= 15.24 e^-(N_u+N_w), bounds the tail of
  cells up to N = 60 by 4.9e-5, and the part beyond 60 by 5e-16.
- Result: Z_B(rho_1) = 0.645754390276 + 5.96283154319i and |Z_B(rho_1)| >= 5.997696 - 4.9e-5 > 0. The envelope
  constant is measured; the rotated-ray lemma guarantees a bound of this form.

**Lemma (uniform cell bound, the written form of Step 4).** Write s = sigma + iu, 0 < sigma < 3, and
Delta_cell = delta Lambda. Subtract d_-2 t^-2 e^{-kappa t}(1 + kappa t), with kappa = 1/(a+b) and using d_-1 = 0; its
Mellin transform is d_-2 kappa^(2-s) Gamma(s-2)(s-1). Rotate to arg t = pi/2 - eta, eta = 1/(1+|u|). There
|e^{xt} - 1| >= e^{x q} - 1 with q = r sin eta, |e^{delta t} - 1| <= delta r e^{delta q}, and |t^(s-1)| = r^(sigma-1) e^{-theta u},
which cancels 1/Gamma's e^{pi |u|/2} growth up to e. Cauchy estimates on |t| = pi/(2c) handle the O(1) remainder near 0.
Result: |Lambda| <= C(sigma)(1 + |u|)^(sigma+3) P(a, b, 1/min(a, b)).

**Omega_+- with an explicit constant (Ingham).** lim sup E_P(R)/sqrt R >= 2|c_1|(1 - gamma_1/gamma_2) = 0.17516, and
lim inf <= -0.17516, where c_1 = Z_B(rho_1)/(2 rho_1 zeta'(rho_1)) and |c_1| = 0.26732 (`omega_constant.log`). The
Landau step uses lambda sqrt R - E_P >= 0, which also excludes zeros off the line, so RH is not assumed; the Fejer kernel
of width T < gamma_2 isolates rho_1. In Markov terms the error in M(x) is Omega_+-((log x)^(1/2)).

**Theorem (conditional).** If, for all cells with N_u + N_w <= 2 log R + C, the four rotation numbers have
sum_{q_k <= R} a_{k+1} = O(R^eps), then E_B(R) = O(R^eps log^2 R). The proof combines the cell decomposition,
Ostrowski's bound for each Hardy-Littlewood sum, the O(log^2 R) relevant cells, and the fact that each lattice point
crosses level R in at most one cell. Numerically (`ostrowski_bound.py`): the largest partial quotient in range stays
496 up to R = 2e6, and the bound grows like log^2 R, from 6.1e4 to 2.0e5, against a measured max |E_B| of 99 to 841.

**Moduli average of Z_B(-2)** (`wp_zeta_neg.py`, L = 0, 40 x 16 nodes): the integral is -0.000658 and the average
-0.00040. For scale, Z_B(-2) is 0.39 on the modular torus and about -1.5e4 near the moduli cusp. This confirms
<Z_B(s)> = 0 off the strip 1 < Re s < 2, where it is proved. The m = 4 and L = 2 runs continue.

## Certificate without fitted constants, and the cusp lemma for <Z_B(s)> = 0 (2026-11-26)

**Fully explicit certificate** (`poc/farey/certify_rho1_rigorous.py`). Every tail cell gets the explicit rotated-ray
bound. That bound uses:
- G = D - d_-2 t^-2 e^{-kappa t}(1 + kappa t), kappa = 1/(a+b), on the ray arg t = pi/2 - eta, eta = 1/(1 + gamma_1);
- the maximum principle on |t| <= pi/c, with |e^z - 1| >= m0 |z| for |z| <= pi and m0 = 0.304554 (minimum modulus);
- |e^{xt} - 1| >= e^{xq} - 1 beyond that;
- the exact Mellin term d_-2 kappa^(2-s) Gamma(s-2)(s-1);
- delta <= 15.24 e^{-(a+b)} wherever delta underflows; the bound is increasing in delta.

It dominates all 120 checked computed cells, by factors of 150 to 3500 with no violations. The tail is <= 2.54e-7 for
cells with max N in (22, 60]. Beyond 60, the explicit bounds' envelope 1.49e-8 (a+b)^6 delta times the cell count
(S+1)^2 per unit of a+b gives 1.3e-18. Hence **|Z_B(rho_1)| >= 5.997696 - 2.6e-7**, with no fitted constant.

**Lemma M (cusp asymptotics; numerical evidence and proof sketch).** As a simple curve alpha shrinks (length l -> 0),

    Z_X(-m) = 2 zeta(-m) l^m + (1/l) P_m(log(1/l)) + o(1/l),   P_m a polynomial of degree about m + 1,

independent of the twist (`cusp_asymptotics.log`). For m = 0 this is exact from the toric formula:
P_0 = (2/3)(log(1/l) + log 2). At l = 0.00625 the measured l(Z + 1) is 3.8456, against 3.8456 predicted. For m = 2 the
third differences are constant, giving a cubic with leading coefficient about -0.09; m = 4 is about degree 5.

Proof sketch. Root the cell decomposition at a triangle containing alpha. The chain cells (alpha, k alpha + beta)
satisfy delta <= l_alpha (measured delta/(2 l) <= 0.5); this cancels the single 1/min(a, b) factor in the rotated-ray
bound. There are about log(1/l)/l chain cells with non-negligible delta. All other cells satisfy
delta <= 16.4 e^{-(a+b)}/l_alpha (measured H l_alpha <= 16.4 at l = 0.1 and 0.01), and their lengths are at least
about 2 log(1/l). Summing gives (1/l) polylog.

Consequence. For Re s < 2 the term 2 zeta(s) l^-s is integrable against the moduli measure (about l dl), and so is
(1/l) polylog. So Z_X(s) is locally uniformly integrable over moduli on Re s < 2, and the average <Z_B(s)> is analytic
there. It vanishes on 1 < Re s < 2, so it vanishes on all of Re s < 2: at the negative integers, at s = 0, and at every
zero rho. The direct checks agree: the average is 0.00014 at s = 0 and -0.0004 at s = -2.

## Exact sandwich for the cell deficiency (proved; `poc/farey/delta_sandwich.py`)

Set sigma = sqrt(t^2 - 4) = 2 sinh(N/2), X = sigma_u sigma_w and K = 16 - 4 mu (K = 16 at the cusp). Then:
- **Discriminant.** t_u^2 t_w^2 - 4(t_u^2 + t_w^2 - mu) = X^2 - K.
- **Comparison trace.** With t_Sigma = 2 cosh((N_u + N_w)/2), cosh A cosh B + sinh A sinh B = cosh(A + B) gives
  t_u t_w + X = 2 t_Sigma.
- **Hence**, for the larger root t_m (cells oriented away from the Bowditch sink),
  t_Sigma - t_m = K / (2 (X + sqrt(X^2 - K))).
- **Sandwich.** delta = int_{t_m}^{t_Sigma} 2 dt / sqrt(t^2 - 4), so

    K / (2 X sigma_Sigma)  <=  delta  <=  K / ((X + sqrt(X^2 - K)) sigma_m).

Consequences:
- Both sides tend to 8 e^{-(N_u + N_w)} at the cusp, which proves the constant 8.
- With a short curve (sigma_u about l_u), delta <= 16 e^{-(N_u + N_w)}/l_u roughly; this was the measured
  H l <= 16.4.
- delta <= min(N_u, N_w), since t_m >= t_u t_w/2 >= max(t_u, t_w).

So the two inputs of the cusp lemma (Lemma M) are proved, and the compactness argument for H is replaced by an explicit
bound. Check: about 23 000 cells (modular torus; cusped tori with l = 0.5, 0.05, 0.005; boundaries L = 2 and 6). The
identity holds to 1e-33, both inequalities hold everywhere, and both are sharp (minimum ratio 1.000000). Cells whose
mediant is the smaller root (one cone of a non-sink root) are excluded; a sink-rooted decomposition has none.

## Metric theorem: polylog lattice error for almost every torus (2026-11-26; `cell_count_general.py`, `random_tori_large.py`)

**Theorem.** For WP-almost every once-punctured torus X, E_{B_X}(R) = O_X((log R)^A).

Proof:
1. If some partial quotient a_{k+1} >= Q has q_k <= R, then alpha lies within 1/(Q q^2) of a reduced p/q with q <= R. So
   the measure of such alpha is <= sum_{q<=R} phi(q) 2/(Q q^2) <= 2(1 + log R)/Q.
2. In Fenchel-Nielsen coordinates (l_u, tau_u), where the WP form is dl dtau, the cell rotation numbers l_w/l_u and
   (l_m - l_u)/l_u have nonvanishing gradient. d/dtau vanishes only at the twist minimum, and there d/dl = (l_u l_w' - l_w)/l_u^2 < 0.
   The coarea formula then bounds the pushforward measure by C_K poly(N) |I| on compacts.
3. Borel-Cantelli over the O(log^2 R) relevant cells at dyadic scales, with Q = (log R)^B, gives partial quotients
   <= (log R)^B eventually, for a.e. X.
4. Theorem 8 (Ostrowski) finishes the proof.

(The length-length coordinates (l_u, l_w) would have an integrable 1/sinh(tau/2) density singularity, which is why
Fenchel-Nielsen coordinates are used.)

**Exact sink-rooted algorithm.** The cell count rooted at the Bowditch sink of a general cusped torus matches direct
enumeration exactly on 3 random tori at 4 radii each. Large-R results on 4 random tori and the modular torus:

| sink traces | rms E_B at w = 1e3 / 1e4 / 1e5 / 1e6 | largest partial quotient in range |
|---|---|---|
| (2.502, 3.348, 3.921) | 9.1 / 19.6 / 24.4 / 51.9 | 1278 |
| (2.714, 3.067, 3.421) | 30.4 / 43.8 / 46.0 / 64.0 | 1706 |
| (2.620, 3.100, 3.925) | 42.9 / 46.5 / 136.9 / 347.4 | 30494 (appears at 1e6) |
| (2.244, 4.449, 4.701) | 22.4 / 181.7 / 573.7 / 411.5 | 4895 |
| modular (3, 3, 3) | 39.5 / 198.5 / 246.4 / 339.7 | 496 |

Growth occurs only while a large partial quotient is active, and its size matches Gauss-Kuzmin statistics over about 2e4
quotients in range. All surfaces stay far below R^(1/2). The modular torus is a single point of moduli space, so its
own case (Theorem 8's hypothesis) remains open.

## Sharp counts and the zeta zeros: explicit formula test and a multi-zero Ingham bound (2026-11-26)

**Coefficients.** c_k = Z_B(rho_k)/(2 rho_k zeta'(rho_k)) from Farey-cell sums (`sharp_explicit.py`). The working
precision must exceed log10 |1/Gamma(rho)|, about pi gamma/(2 ln 10). At 30 digits the values from k = 9 on were
garbage; with adaptive precision:

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| \|c_k\| | 0.267 | 0.183 | 0.209 | 0.118 | 0.179 | 0.121 | 0.082 | 0.138 | 0.058 | 0.087 |

**Explicit-formula test.** 400 exact E_P(R) values at log-uniform R in [3e4, 3e5] have rms E_P/sqrt R = 1.168
(`sharp_samples.py`). The prediction sum_{k<=K} 2 Re[c_k e^{i gamma_k log R}], with no fitted parameters, has
correlation 0.29, 0.37, 0.43, 0.45 and 0.53 for K = 1, 2, 3, 5 and 10; the residual rms goes from 1.12 to 0.99
(`sharp_compare_partial.log`). The correlation keeps rising, as expected for a slowly converging sharp explicit
formula. With 10 zeros it is not yet decisive; the 20-zero run is in progress.

**Multi-zero Ingham bound (unconditional).** For T below the next zero,
lim sup E_P/sqrt R >= sup_y P_T(y) and lim inf <= inf_y P_T(y), where
P_T(y) = sum_{gamma_k < T} 2(1 - gamma_k/T) Re(c_k e^{i gamma_k y}). Searching y in [0, 400] (`ingham_multi.log`):

| zeros used | 1 | 3 | 5 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|
| sup_y P_T | 0.175 | 0.474 | 0.721 | 1.060 | 1.190 | 1.321 |
| inf_y P_T | -0.175 | -0.474 | -0.716 | -1.051 | -1.189 | -1.361 |

The sup comes within 10% of the trivial maximum sum 2(1 - gamma/T)|c|. Observed extremes on [3e4, 3e5] are +3.50 and
-2.82. The weights decay slowly, so sum |c_k| appears to diverge. Under the linear-independence hypothesis for the
zeros, E_P(R)/sqrt R would then be unbounded in both directions: a Mertens-type conjecture |E_P| << sqrt R fails for
simple geodesics, while E_P = O(R^(1/2+eps)) remains possible. Unconditionally, each additional computed zero raises the
proved constant. Caveat: only c_1 carries the full tail certificate; c_2, ..., c_12 are computed at adaptive precision
with the same cell sums.

## The four-holed sphere: same structure, same Riemann-zero lower bound (`poc/farey/sphere_zeta.py`, `sphere_zeta2.py`)

Simple closed curves on a four-holed sphere are indexed by slopes. Their lengths extend to a convex homogeneous norm on
R^2, because every Farey cell has a positive defect, so every corner is genuine. Hence sum_slopes l^-s = Z_B(s)/(2 zeta(s))
exactly. The Farey-cell decomposition uses the Fricke mediant rule c = ab - kappa(class of c) - d.

- **The symmetric cusped sphere (7, 7, 7) is the modular torus scaled by 2**: 2 arccosh(3.5) = 2 x 2 arccosh(1.5).
  So Z_sphere(s) = 2^-s Z_torus(s), and Z(0) = -0.653651620282 for both. This case is not independent.
- **Non-symmetric cusped sphere, base traces X = 7, Y = 9** (Z(e0 - e1) = 5.81475, Z(e0 + e1) = 49.18525; 331 cells, all
  defects positive):
  - Z_B(0): the Barnes cell sum gives -0.64805289917628. The toric formula -1 + (1/3) sum_slopes g/l, using the sphere
    gap law with its linear Fricke terms, gives -0.64805289918345. They agree to 7e-12. This is an independent test of
    the toric formula and of the sphere gap law.
  - Z_B(3): the cell decomposition gives 0.18674. The direct sum over slopes with l <= 50 gives 0.18015, plus a tail
    estimate of about 0.007.
  - Z_B(rho_1) = -1.0140 - 1.4070i, |Z_B(rho_1)| = 1.73 != 0. By the argument of Theorem 6, the error in counting simple
    closed geodesics on this sphere is Omega_+-(R^(1/2)), forced by the Riemann zeros; no RH is assumed.

**Correction to the high-zero coefficients.** Even with adaptive precision, quadrature on the real t-axis fails from
about gamma = 60: k = 14 gives |c| = 1.06 and k >= 15 explodes. The oscillating integrand's quadrature error is multiplied
by 1/|Gamma(rho)|. The fix is to compute Delta_cell on the rotated ray arg t = pi/2 - 1/(1 + gamma), with the Bernoulli
series continued along the ray (`zeros_rotated.py`). It reproduces k = 1 to 1e-6 (0.6457537 + 5.9628325i) and k = 2. The
12-zero Ingham constant 1.32 and the 10-zero correlation are provisional until c_10, c_11 and c_12 are confirmed by the
rotated run (20 zeros, in progress). The constants with k <= 9 agree between the two methods.

## Zero average for all complexity-one surfaces, and the sharp bound reduced to a Lindelof-type hypothesis (2026-11-26)

**Theorem (general zero average).** Let X range over one-holed tori or four-holed spheres, with any fixed boundary
lengths. Cutting along a simple curve leaves pairs of pants (V_{0,3} = 1), so Mirzakhani gives
int_M sum_{gamma in orbit} F(l_gamma) = c_orb int F(l) l dl. Hence

    int_M A_X(t) dV = 2 sum_k sum_orb c_orb int_0^{t/k} l dl = C zeta(2) t^2   exactly, for every t.

Dominated convergence (A/t^2 <= Area + C(Perim/t + 1/t^2), integrable) then forces int Area(B_X) = C zeta(2). So
int (A_X(t) - Area t^2) dV = 0 at every scale, and <Z_B(s)> = 0 on 1 < Re s < 2, extending by continuation as before.
The earlier separately computed value int Area = zeta(2) is a consequence, not an input.

**Theorem 10 (conditional sharp upper bound).** For a.e. X (Theorem 9), assume RH and the Lindelof-type bound
Z_X(1/2 + eps + it) << |t|^eps. Then E_P(R) = O(R^(1/2 + eps)), and the exponent is exact by Theorem 6. Proof:
- Truncated Perron at height T has error O(R^2/T), since #{gamma : |l - R| <= R/T} << R^2/T + polylog by Theorem 9.
- Shifting to Re s = 1/2 + eps, using 1/zeta << |t|^eps (RH) and the hypothesis, gives R^(1/2+eps) T^eps.
- Take T = R^(3/2).

The hypothesis is the analogue of Lindelof for Epstein zetas. A polylog lattice error gives only the trivial
|Z_X| << |t|, and stationary phase suggests about |t|^(1/2) without further structure. This is why a sharp
McShane-Rivin upper bound is as hard as a Lindelof-type problem.

(Correction to an earlier note: the moduli-average run `wp_zeta_neg.py` stopped at its 2-hour limit, but only after
these results.)

| L | m | average of Z_B(-m) over moduli (40 x 16 nodes) |
|---|---|---|
| 0 | 0 | +0.00014 |
| 0 | 2 | -0.00040 |
| 0 | 4 | +0.126 |
| 2 | 0 | -0.00040 |
| 2 | 2 | -0.00006 |

The boundary-length cases confirm the zero average. The m = 4 value is not clearly zero. Z_B(-4) grows like
(1/l) log^5(1/l) near the cusp (6.6e5 at l = 0.0019), which strains this quadrature. The scale of the integral of
|Z_B(-4)| is being computed to judge it (`abs_integral_m4.py`).

## Correction: the Lindelof route to a sharp upper bound is probably closed; a variance-growth conjecture instead

The "Theorem 10" hypothesis Z_X(1/2 + eps + it) << |t|^eps is probably false. A two-dimensional lattice zeta is centred
on Re s = 1: for an ellipse, Z(s) is an Epstein zeta at s/2 with functional equation s <-> 2 - s, so
|Z(1/2 + it)| is of order |t|^(1/2). The computed |Z_B(rho_k)| fit gamma^0.57 over 13 zeros, with
|Z_B|/sqrt(gamma) = 2.20 +- 0.63 and no trend (`zb_vertical_growth.log`).

The Euclidean comparison Z = 4 zeta(s/2) beta(s/2) is inconclusive at these heights. Its predicted sqrt(gamma) growth
is only (tau/2pi)^(1/2), with tau = gamma/2, which is swamped by fluctuations of zeta beta(3/4 - i tau); the computed
values even fall, 7.9 -> 5.0.

**Conjecture (under RH + LI).** The variance of E_P/sqrt R grows like log R. The terms have squared size about
1/(gamma |zeta'(rho)|^2), and by Gonek-Hejhal sum_{gamma <= T} |zeta'(rho)|^-2 ~ 6T/pi^3, so their sum diverges
logarithmically. Hence E_P(R)/sqrt(R log R) should have a limiting distribution. This is consistent with
O(R^(1/2+eps)) and incompatible with O(sqrt R). The measured rms of E_P/sqrt R rises slowly (0.77, 1.08, 1.15) but
cannot yet separate sqrt(log R) from a constant.

**Scale check for the m = 4 average** (`abs_integral_m4.py`, 20 x 8 nodes): the integral of |Z_B(-4)| over moduli is 25.9,
against the signed integral 0.208, about 0.8%. For m = 2 the ratio is 0.00066/1.40, about 0.05%. So the m = 4
average is not convincingly zero, but it is within what this quadrature can resolve: the signed integrand has a
(1/l) log^5(1/l) cusp tail. Unresolved; a cusp-adapted integrator is needed.

**The near-vertical rotated ray is also unreliable at high zeros.** The arg t = pi/2 - 1/(1+gamma) method at 30 digits gave
k = 11: -38.3 + 16.0i. At 40 digits it gives -20.095 + 0.002i, which agrees with the adaptive real-axis value. At k = 16
the result depends on the angle: -39.5 - 41.8i at eta = 1/(1+gamma), and 8.8 - 10.4i at eta = 2/(1+gamma). The ray
passes close to the poles of D at 2 pi i k/x and the quadrature misses the spikes. Now running: arg t = pi/4, where D is
smooth, with precision raised by (pi/4) gamma/ln 10 to absorb the cancellation, cross-validated at arg t = pi/3
(`zeros_angle.py`). Until those agree, only c_1 (certified) and c_2, ..., c_6 (the two methods agree to about 1e-4 - 1e-3 relative) are
trusted. The 12-zero Ingham constant 1.32 is withdrawn. The bound from 6 zeros, about 0.83, stands up to those 1e-3-level
uncertainties in c_2, ..., c_6.

## Validated 20-zero coefficients: Ingham bound 1.62 / -1.70, a retraction, and an inconclusive explicit-formula test

**Validation.** Z_B(rho_k) on the rays arg t = pi/4 (k = 1..20) and pi/3 (k = 1, 5, 8, 11, 16, 20) agree to 1e-12 at
k = 16 and 1e-6 at k = 20 (`zeros_angle.py`, `twenty_zero_analysis.log`). The adaptive real-axis values are correct for
k <= 11, 0.5% off at k = 12, and wrong from k = 13. The near-vertical rotated ray at 30 digits was the method that failed.

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| \|Z_B(rho_k)\| | 6.00 | 8.76 | 14.33 | 9.34 | 16.27 | 17.66 | 9.96 | 21.93 | 8.71 | 12.26 | 20.10 | 15.68 | 4.42 | 14.89 | 7.73 | 3.90 | 7.72 | 10.65 | 0.48 | 8.82 |

**Ingham (unconditional).** lim sup E_P/sqrt R >= sup P_T and lim inf <= inf P_T give:

| zeros used | 6 | 10 | 12 | 16 | 20 |
|---|---|---|---|---|---|
| sup P_T | 0.834 | 1.190 | 1.321 | 1.465 | 1.623 |
| inf P_T | -0.828 | -1.189 | -1.361 | -1.559 | -1.701 |

So lim sup E_P/sqrt R >= 1.623 and lim inf <= -1.701. The 12-zero values are reinstated, since their coefficients were
correct.

**Retraction.** The claim |Z_B(rho_k)| ~ 2.2 sqrt(gamma) came from corrupted coefficients. Validated values show no growth:
the mean is 12.5 for k <= 10 and 9.4 for k = 11..20, with fitted exponent -0.44 over 20 zeros. So:
- The Lindelof-type hypothesis of Theorem 10 is not refuted by the data. The theoretical expectation of size
  |t|^(1/2), from the centre Re s = 1, is a heuristic only. Theorem 10 stands as an open conditional statement.
- The sqrt(log R) variance conjecture is withdrawn. If |Z_B(rho)| stays bounded on average, then
  sum |c_k|^2 < infinity (by Gonek-Hejhal-type averages), and E_P/sqrt R should have a limiting distribution with finite
  variance, as M(x)/sqrt x does under RH + LI. Since sum |c_k| still diverges, E_P/sqrt R is unbounded under LI.

**Sharp explicit-formula test.** The correlation with exact E_P/sqrt R is 0.29, 0.45, 0.53, 0.545 and 0.550 for 1, 5, 10, 15
and 20 zeros, explaining 30% of the variance. The 20 zeros carry variance 2 sum |c|^2 = 0.53 against the observed 1.37.
The remainder would need a long tail of small coefficients (|c| about 0.03 for k = 11..20). This is consistent with an
all-zero explicit formula but not a demonstration of it.

## Exact cusp asymptotics of Z_X, and the m = 4 average resolved (`poc/farey/cusp_model.py`, `wp_cusp_subtracted.py`)

**Theorem (cusp asymptotics; derivation plus numerics).** As a simple curve alpha shrinks to length l, the fan formula
t ~ (4/l) cosh(x/2) gives the limiting strip norm N(p alpha + q beta) ~ |q| (W + F(p l/q - tau)), with W = 2 log(4/l)
and F(y) = 2 log cosh(y/2). Summing over p by Euler-Maclaurin removes the twist tau, which is why the values are
twist-independent. Hence

    Z_X(s) = 2 zeta(s) l^-s + (2/l) zeta(s-1) I(s, W) + o(1/l),
    I(s, W) = 2 (W - 2 log 2)^{1-s}/(s-1) + int_R [ (W + F(y))^-s - (W + |y| - 2 log 2)^-s ] dy.

For s = -m, write F = |y| - 2 log 2 + h with h = 2 log(1 + e^-|y|). Then I is a polynomial in L = log(1/l), built from
the moments int h = pi^2/3, int |y| h = 3 zeta(3), int h^2 = 2 zeta(3), and so on.
- m = 0: P_0 = (2/3)(L + log 2), exactly the toric-formula result.
- m = 2: leading coefficient -4/45 = -0.0889 (measured cubic coefficient about -0.09).

Model against cell sums, l (Z(-m) - 2 zeta(-m) l^m), at l = 0.1 ... 0.00625:

| l | 0.1 | 0.05 | 0.025 | 0.0125 | 0.00625 |
|---|---|---|---|---|---|
| m = 0 model / cells | 1.9972 / 1.9981 | 2.4593 / 2.4595 | 2.9214 / 2.9214 | 3.3834 / 3.3835 | 3.8455 / 3.8456 |
| m = 2 | -1.5725 / -1.5707 | -3.4927 / -3.4923 | -6.3581 / -6.3581 | -10.3465 / -10.3465 | -15.6352 / -15.6353 |
| m = 4 | -20.8127 / -20.8113 | -5.1824 / -5.1740 | 49.6688 / 49.6760 | 175.3713 / 175.3796 | 415.8864 / 415.9086 |

This replaces the proof sketch of Lemma M with an explicit leading term.

**The m = 4 average resolved.** Integrate l >= 0.05 by 2D Gauss (48 x 20; smooth) and l < 0.05 exactly from the model;
the twist window has width l, checked to 6 digits. Results at L = 0:

| m | smooth part | cusp part | total | average |
|---|---|---|---|---|
| 0 | -0.153707 | 0.155046 | 0.00134 | 0.0008 |
| 2 | 0.469323 | -0.470142 | -0.00082 | -0.0005 |
| 4 | -12.711576 | 12.715884 | 0.00431 | 0.0026 |

The parts cancel to 3e-4 of their size, the same residual level as the m = 0 and m = 2 controls, whose averages are
known to be zero; the grid's volume error is 0.13%. So <Z_B(-4)> = 0 within accuracy, and the earlier 0.126 was
quadrature error at the cusp.

**Proof of the cusp asymptotics.** Write M_X(s) = 2 zeta(s) l^-s + (2/l) zeta(s-1) I(s, W).
1. *Lengths.* The exact fan t(k alpha + beta) = 2 coth(l/2) cosh(y_k/2) (from AB = coth^2(l/2)) gives
   N(k, 1) = W + F(y_k) + O(l^2). The model and N are both convex, with model'' <= l^2/2, so the chord and
   neighbouring-chord sandwich gives |N(x, 1) - model(x)| <= C l^2 for all real x. By homogeneity,
   |N(p, q) - q model(p/q)| <= C q l^2.
2. *Re s > 2.* Replacing N by the model costs O(l W^-sigma). Poisson summation over p for the model, which is analytic
   in |Im y| < pi, gives (q/l) int G up to O(e^{-cq/l}), and the twist drops out. Hence
   psi(s) = l (s - 2)(Z_X - M_X) = O(l^2) on 2.5 <= Re s <= 3.
3. *Continuation.* On a rectangle, Z_X and M_X are O((1/l) polylog(1/l)):
   - the chain cells have delta <= l, cancelling the 1/l of the cell bound, and decay like e^{-y_k};
   - all other cells contribute O(l^3) by the sandwich;
   - M_X's poles at 1 cancel and the pole at 2 is removed by the factor (s - 2).
   Hadamard's two-constants theorem gives |psi| <= C l^{2 omega(s)} polylog(1/l), so psi = o(1).
Remaining sketch-level ingredient: the per-cell bound with a single factor 1/min(a, b), as in Theorem 3.

## Is the sharp error the zero sum? Exact explicit formula, variance accounting, and a smoothing test (`smoothed_completeness.log`)

**Explicit formula.** In P(R) = (1/2 pi i) int D(s) R^s ds/s with D = Z_B/(2 zeta), the residues are:
- s = 2: the main term;
- each zero rho: c_rho R^rho;
- s = 0: D(0) = Z_B(0)/(2 zeta(0)) = -Z_B(0) = +0.6537;
- the trivial zeros: O(R^-2).

So E_P(R) = 0.6537 + sum_rho c_rho R^rho + O(R^-2), with no other source of error, wherever the contour shift is
justified.

**Variance accounting.** If sum |c_rho|^2 < infinity, then E_P/sqrt R as a function of log R is B^2-almost periodic with
Fourier series sum c_rho e^{i gamma log R} (Rubinstein-Sarnak, Ng), and its mean square is 2 sum |c_rho|^2. The measured
mean square is 1.365 and the first 20 zeros carry 0.53, so a complete formula needs about 0.83 from the zeros beyond
gamma_20. The coefficients decay slowly and 1/|zeta'(rho)|^2 is heavy-tailed, so this is plausible.

**Smoothing test.** A box average of width h in log R multiplies each zero term by sinc(gamma h/2). Applied to the 400
exact samples and to the 20-zero sum:

| h | none | 0.040 | 0.063 | 0.110 | 0.156 | 0.202 |
|---|---|---|---|---|---|---|
| explained by 20 zeros | 30.1% | 76.3% | 80.8% | 83.5% | 83.2% | 80.1% |
| correlation | 0.55 | 0.875 | 0.900 | 0.914 | 0.912 | 0.896 |
| rms data / zero sum | 1.168 / 0.678 | 0.693 / 0.636 | 0.618 / 0.583 | 0.493 / 0.468 | 0.402 / 0.379 | 0.321 / 0.303 |

So the 70% the raw 20-zero sum misses is high-frequency content in log R, where the uncomputed zeros sit. The
remaining 16-20% matches the partially suppressed tail (sinc about -0.2 near gamma = 80-100) and edge effects. There
is no evidence of a non-zero component.

**Theorem (smoothed explicit formula; given the polynomial vertical growth of Z_B from the cell lemma).** The log-scale
box smoothing E_{P,h} satisfies

    E_{P,h}(R)/sqrt R = sum_rho c_rho sinc(gamma h/2) R^{i gamma} + O(R^{-1/2}),

with absolute convergence, since |c_rho sinc| << |Z_B(rho)|/(gamma^2 |zeta'(rho)|), plus routine contour shifting with
polynomial growth; RH is not needed. So the smoothed sharp error is completely the zero sum. The raw sharp count is the
conditionally convergent limit h -> 0. Its completeness is the analogue of the sharp explicit formula for M(x), known
only under RH plus simple zeros with chosen truncation heights (Titchmarsh 14.27).

## A surface where the first Riemann zero disappears (`zb_moduli.py`, `zb_scan.py`, `zb_root.py`, `zero_blind_count.py`)

**Method.** `zb_moduli.py` computes Z_B(s) for any cusped once-punctured torus, rooted at its Bowditch sink (x, y, z):

    Z_B = 2 zeta(s) sum a^-s + 2 sum_{3 root cones} zeta_2(s; p, q) + 2 sum_cells Delta.

Each piece is a Mellin integral evaluated on the ray arg t = theta, vectorised in double precision, with cell lengths from
60-digit traces.

**Validation.**
- At the modular torus it reproduces the certified Z_B(rho_1) = 0.645754390 + 5.962831543i to 1e-9 (theta = pi/3).
- At real s = 2.6, 3, 4 on the new surface it matches the direct sum 2 zeta(s) sum_simple l^-s, corrected for the l > 60
  tail, to 5e-6.

**Scan.** A 40 x 30 grid over the fundamental domain was scanned: 2 < x <= 3, max(x, sqrt(4 + 16/(x^2-4))) <= y <= x/sqrt(x-2),
with corners at the hexagonal point (3,3,3), the square point (2v2, 2v2, 4) and the cusp. Exactly one grid cell had
nonzero winding. Near the cusp |Z_B(rho_1)| grows (3.6 to 4.3 as x goes from 2.10 to 2.07) and is twist-independent, as
Theorem 11 predicts, since zeta(rho) = 0 kills the leading term there.

**The zero.** Newton refinement finds Z_B(rho_1) = 0 at

    X*: sink traces (2.671687609484, 3.111739620736, 3.479943422263)
        lengths (1.59641, 2.02161, 2.30360), Area(B) = 0.896125.

- Residual |Z| is below 4e-12 at theta = pi/3 and 1e-10 at 0.4 pi, stable in the cell cutoff.
- The Jacobian of (Re, Im) with respect to the coordinates (x, v) has determinant 80.5. So the zero is nondegenerate with
  local degree +-1, and it survives any small perturbation of the computation.
- X* is chiral: it lies on no mirror edge. Its mirror image is the second zero on the oriented moduli space, with the
  opposite degree.

**Spectral verification on the actual counts.** The exact simple-length spectrum was computed up to 3000 (2.45M curves).
E_P(R)/sqrt R on R in [50, 3000] was projected onto R^{i gamma} with a Hann window in log R:

| k | gamma | modular: measured / predicted abs(c_k) | X*: measured / predicted abs(c_k) |
|---|---|---|---|
| 1 | 14.135 | 0.2662 / 0.2673 | **0.0002 / 0** |
| 2 | 21.022 | 0.1843 / 0.1833 | 0.0709 / 0.0699 |
| 3 | 25.011 | 0.2090 / 0.2088 | 0.0779 / 0.0764 |
| 4 | 30.425 | 0.1231 / 0.1177 | 0.0262 / 0.0222 |
| 5 | 32.935 | 0.1812 / 0.1787 | 0.0421 / 0.0401 |
| 6 | 37.586 | 0.1194 / 0.1213 | 0.0297 / 0.0291 |
| 7 | 40.919 | 0.0966 / 0.0817 | 0.0619 / 0.0600 |
| 8 | 43.327 | 0.1499 / 0.1380 | 0.0419 / 0.0396 |

The gamma_1 oscillation is absent from the simple-geodesic count of X*. Every other zero's amplitude matches the explicit
formula zero by zero, on a second, unrelated surface. X* is also much quieter overall: rms E_P/sqrt R is 0.396 against
0.951, because all its abs(Z_B(rho_k)), k <= 8, are 1.8 to 7.3, against 6 to 22 on the modular torus.

## Residual after 20 zeros vs the lattice error (`residual_lattice.py`)

E_P = (1/2) sum_d mu(d) A(R/d) exactly. The residual left by the 20-zero sum (rms 324) correlates with the ball lattice
errors E_A(R/d). A joint regression on d <= 6 recovers the Moebius coefficients mu(d)/2:

    (0.42, -0.46, -0.39, -0.01, -0.32, 0.49)  vs  (0.5, -0.5, -0.5, 0, -0.5, 0.5).

The share of residual variance carried by M_6 = (1/2) sum_{d<=6} mu(d) E_A(R/d) falls from 0.46 on [3e4, 9.5e4] to 0.25 on
[9.5e4, 3e5]. So at finite R, much of the deficit is the Diophantine (partial-quotient) lattice error entering through the
first Moebius terms. Its normalised size decays, since E_A plateaus at rms ~300 while sqrt R grows. This is what the
explicit formula predicts if it is complete at the sqrt R scale: that content lives in the high zeros, or in the leftover
contour integral on Re s = sigma0 < 1/2.

## Lemma C: an explicit per-cell bound, and polynomial vertical growth of Z_B (proved; `lemma_c_check.py`)

This closes the per-cell ingredient that earlier sections left at sketch level: Step 4 of the continuation (Theorem 3),
the single 1/min(a, b) factor in the cusp lemma (Theorems 7 and 11), and the polynomial vertical growth assumed by the
smoothed explicit formula.

**Setting.** A cell has lengths a = N_u, b = N_w, c = N_m and deficiency delta = a + b - c, with 0 < delta <= min(a, b),
so c >= max(a, b). Its integrand is

    D(t) = e^{ct}(e^{delta t} - 1)/((e^{at} - 1)(e^{bt} - 1)(e^{ct} - 1)),

with Laurent coefficients d_-2 = delta/(abc) and d_-1 = 0. Set kappa = 1/(a + b) and

    G = D - d_-2 t^-2 e^{-kappa t}(1 + kappa t).

G is analytic on |t| < 2 pi/c: its t^-1 coefficient vanishes because d_-1 = 0. It decays in |arg t| < pi/2. For Re s > 2,
int t^{s-3} e^{-kappa t}(1 + kappa t) dt = kappa^{2-s} Gamma(s-2)(s-1), and Gamma(s-2)(s-1)/Gamma(s) = 1/(s-2), so

    Delta(s) = (1/Gamma(s)) int_ray t^{s-1} G(t) dt + d_-2 kappa^{2-s}/(s-2),                         (*)

The ray integral converges for Re s > 0, so (*) continues Delta there. The ray arg t = theta can be any angle in
(-pi/2, pi/2), because the integrand is analytic in the sector and decays at both ends.

**Elementary inequalities.**
1. |e^z - 1| <= |z| e^{max(Re z, 0)}.
2. |e^{xt} - 1| >= e^{x Re t} - 1, by the reverse triangle inequality.
3. e^y - 1 >= e^y y/(1 + y) for y > 0.
4. |e^z - 1| >= m_R |z| on |z| <= R < 2 pi (minimum modulus principle), with m_pi = 0.304554 and m_{1.5pi} = 0.210300.

**Lemma C.** Let 0 < sigma < 2, tau >= 0 (the case tau < 0 follows by conjugation), s = sigma + i tau. If tau >= 1, take
eta = 1/(1 + tau) and theta = pi/2 - eta; otherwise take theta = 0 and eta = pi/2. Let r1 = pi/c and q1 = r1 sin eta. Then

    |Delta(s)| <= e^{-theta tau}/|Gamma(s)| * [ M r1^sigma/sigma
                   + delta (sin eta)^{-sigma-1} int_{q1}^inf q^sigma e^{-cq} prod_{x=a,b,c} (1 + 1/(xq)) dq
                   + d_-2 (1 + 1/(e sin eta)) r1^{sigma-2}/(2 - sigma) ]
                 + d_-2 kappa^{2-sigma}/|s - 2|,

    M = e^{c r1} delta r1 e^{delta r1}/(m_pi^3 abc r1^3) + d_-2 r1^-2 e^{kappa r1}(1 + kappa r1).

*Proof.*
- **Disk, r <= r1.** On |t| = r1 every |xt| <= c r1 = pi. Inequalities 1 and 4 give |D| <= e^{c r1} delta r1 e^{delta r1}
  /(m_pi^3 abc r1^3), and the subtracted term is at most d_-2 r1^-2 e^{kappa r1}(1 + kappa r1). So |G| <= M on the circle,
  and hence on the disk by the maximum principle. With |t^{s-1}| = r^{sigma-1} e^{-theta tau}, this part contributes
  M r1^sigma/sigma.
- **Ray, r > r1, D term.** Write q = r sin eta = Re t. By 1, 2 and 3,

      |D| <= delta r e^{(c + delta)q}/prod(e^{xq} - 1) <= delta r e^{-cq} prod_x (1 + 1/(xq)).

  Substituting r = q/sin eta gives the second term.
- **Ray, subtracted term.** |e^{-kappa t}| = e^{-kappa q} and kappa r e^{-kappa q} <= 1/(e sin eta), so the integral is
  at most d_-2 (1 + 1/(e sin eta)) int_{r1}^inf r^{sigma-3} dr. ∎

**Size.** The three bracket terms are
- delta c^{1-sigma}/(ab) * O(1),
- delta c^{1-sigma}/(ab) * O((sin eta)^{-sigma-4}), using (1 + 1/(aq))(1 + 1/(bq)) <= (1 + c/(pi a sin eta))(1 + c/(pi b sin eta))
  and c >= a, b,
- delta c^{1-sigma}/(ab) * O(1/sin eta).

By Stirling, e^{-theta tau}/|Gamma(s)| <= C(sigma) (1 + tau)^{1/2 - sigma} e^{eta tau} for tau >= 1, and
e^{eta tau} <= e. The pole term is at most delta c^{sigma-3}/(ab |s - 2|), since a + b >= c. Hence, uniformly over cells,

    |Delta(sigma + i tau)| <= C(sigma1, sigma2) (1 + |tau|)^{9/2} * delta max(c^{1-sigma}, c^{sigma-3})/(ab)   on [sigma1, sigma2] in (0, 2).

Since c/(ab) <= 2/min(a, b), the right side has a single factor 1/min(a, b). This is the ingredient the cusp lemma
needed.

**Extension to Re s <= 0.** Fix K >= 1. On |t| = 1.5 r1, inequality 4 with m_{1.5pi} gives |G| <= M' with M' of the same
shape as M. Cauchy's estimates then give
- Taylor coefficients |g_k| <= M' (1.5 r1)^{-k};
- |G - P_K| <= 3 M' (2/3)^K (r/r1)^K on |t| <= r1, where P_K is the degree-(K-1) Taylor polynomial.

Write int_0^{r1} t^{s-1} G = int_0^{r1} t^{s-1}(G - P_K) + sum_{k<K} g_k (r1 e^{i theta})^{s+k}/(s+k). The poles at
s = -k cancel against the zeros of 1/Gamma. So, on sigma in [-K + eps, 2 - eps],

    |Delta(s)| <= C(K, eps)(1 + |tau|)^{A(K)} * delta (1 + c)^{K+2}/(ab).

**Summing the cells.**
- The sandwich gives delta <= K_X/((X + sqrt(X^2 - K_X)) sigma_m). With a, b >= systole l0 and c >= a + b - delta, this
  gives delta <= C(l0, mu) e^{-(a+b)}.
- Each cell is indexed by its mediant m, and N_m >= a + b - C. So McShane-Rivin quadratic growth gives at most
  C (S + 1)^2 cells with a + b <= S.
- Hence sum_cells delta (1 + c)^{K+2}/(ab) < infinity. The root terms are Barnes double zetas and zeta(s) a^-s: the same
  argument with the t^-2 and t^-1 parts subtracted, or the classical bounds, gives polynomial growth for them too.

**Theorem (polynomial vertical growth).** For every once-punctured or one-holed torus X, Z_B(s) is meromorphic on C with
a single simple pole at s = 2. On every vertical strip sigma1 <= Re s <= sigma2 with |s - 2| >= 1,
Z_B(s) = O((1 + |Im s|)^A), where A depends only on the strip (A = 9/2 on (0, 2)). For Re s > 2 it is bounded by the
Dirichlet series. Near s = 2, use (s - 2) Z_B(s) and Phragmen-Lindelof.

**Consequences.**
- **Theorem 3 is now fully proved**, without "sketched" constants.
- **The cusp lemma (Lemma M) gets its per-cell input.** This completes the proofs of Theorem 11 and of <Z_B(s)> = 0 on
  Re s < 2 (Theorem 7).
- **Smoothed explicit formula, unconditionally.** Let w be smooth with compact support in log R, and let
  E_{P,w}(R) = int E_P(R e^u) w(u) du. Then w-hat decays faster than any power. Titchmarsh Thm 9.7 gives, in each
  [T, T+1], a height T* with |zeta(sigma + i T*)|^{-1} << T*^B for -1 <= sigma <= 2. Integrating D(s) w-hat(s) R^s/s
  around the rectangles [-1, 3] x [T*_n, T*_{n+1}] yields

      E_{P,w}(R) = -Z_B(0) w-hat(0) + sum_n ( sum_{T*_n < gamma < T*_{n+1}} Res_rho ) + O(R^{-1}),

  where the block sums are O(T_n^{-N}) for every N. The left side at sigma = -1 is controlled by the functional
  equation for zeta and the growth theorem.
- No RH, simple zeros or bound on 1/zeta'(rho) is needed. A multiple zero would give R^rho log^j R terms.

**Numerical check of the explicit constants** (`lemma_c_check.py`). Exact Delta_cell(s) was computed by mpmath on a
rotated ray, with precision raised by (pi/2 - theta) tau/ln 10, for 24 cells each on the modular torus and on the
zero-blind surface X*, at sigma in {0.3, 0.5, 1.5} and tau in {0.5, 5, 20, 60}. Across all 576 cases,
|Delta|/bound lies between 1.5e-4 and 1.19e-2. So the explicit bound holds everywhere with a margin of at least 84x. The margin
shows no sign of shrinking with tau (worst values at tau = 20: 4.3e-3, 5.8e-3, 1.05e-2 on the modular torus) or between
surfaces.

## Zero-blind surfaces for rho_2 ... rho_6 (`zb_scan.py k`, `zb_roots_multi.py`)

Method: the same 40 x 30 scan for each k, then Newton from every cell with nonzero winding. A zero is kept only if
abs(Z) < 1e-7 inside the domain, after deduplication. Each kept zero is nondegenerate, and its sign is the local degree.

| k | gamma_k | blind surfaces found | degrees |
|---|---|---|---|
| 1 | 14.13 | 1 | + |
| 2 | 21.02 | 3 | + - + |
| 3 | 25.01 | 4 | + - - + |
| 4 | 30.42 | 8 | - + + - + + - + |
| 5 | 32.94 | >= 4 (6 flagged) | + - - + |
| 6 | 37.59 | >= 0 (7 flagged; Newton from the coarse cells did not converge) | |

Traces are in `zb_roots_multi.log`. No surface appears in two rows. Counting 4 real conditions against 2 real moduli,
simultaneous blindness to two zeros should be non-generic, but this is not proved.

The counts grow roughly like gamma^2: 1, 3, 4, 8 against (gamma/gamma_1)^2 = 1, 2.2, 3.1, 4.6. A heuristic explains this:
arg Z_B(rho) varies over moduli at rate about gamma times the gradient of the log-lengths, so the density of
phase-vortices scales like gamma^2. The k >= 5 counts are lower bounds, because the grid aliases there.

**Conjecture.** The number of surfaces blind to rho is about C gamma^2, with signed count 0 on the oriented moduli space
(each zero pairs with its mirror image).

## Certificate for the zero-blind surface X* (`certify_xstar.py`)

Argument principle on the circle of radius 0.02 about X* in the chart (x, v), with 400 samples (chord 3.1e-4).

| Error term | How it is bounded | Size |
|---|---|---|
| Cell tail | Explicit Lemma C bound, summed over the 678 actual cells with 40 < a+b <= 64; envelope beyond 64; x1.5 for the whole loop | 7.2e-14 |
| Quadrature/rounding | 10 x the disagreement between the rays theta = pi/3 and 0.4 pi | 1.5e-9 |
| Between samples | Lipschitz L = 10 x the largest central-difference gradient on 320 points of the annulus r/2..3r/2 (max 15.3); L h/2 | 2.4e-2 |

The minimum of abs(Z) on the loop is 0.119, five times the 0.024 margin required. The largest phase step between
samples is 0.035 rad. The winding number is exactly 1. **So X* carries a zero of Z_B(rho_1) of degree 1.**

The certificate is rigorous except in two places, which are numerical with a 10x safety factor:
- the quadrature error, estimated by comparing two rays rather than by interval arithmetic;
- the Lipschitz constant, estimated from sampled gradients rather than by a validated derivative bound.
It is at the same standard as the rho_1 certificate on the modular torus. Interval arithmetic would close both.

## Higher genus: the Riemann zeros live in every embedded one-holed torus (`boundary_torus.py`)

**Boundary case.** The whole theory (Lemma C, the sandwich with K = 16 - 4 mu > 16, the cell formula, the explicit
formula) holds for one-holed tori with geodesic boundary, x^2 + y^2 + z^2 - xyz = 2 - 2 cosh(Lb/2). The exact counts
confirm it in amplitude and phase. For Lb = 2 (2.20M curves to 3000):

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| measured abs | 0.1856 | 0.0602 | 0.0404 | 0.0440 | 0.0475 | 0.0611 | 0.1025 | 0.0986 |
| predicted abs | 0.1858 | 0.0603 | 0.0390 | 0.0429 | 0.0462 | 0.0616 | 0.0937 | 0.0878 |
| measured phase | -0.975 | +0.578 | -1.777 | -2.808 | +2.223 | -1.151 | +2.975 | +1.719 |
| predicted phase | -0.975 | +0.592 | -1.801 | -2.907 | +2.319 | -1.173 | +2.914 | +1.806 |

For Lb = 6 (1.22M curves), gamma_1 measured 0.0661 at phase +0.679, against 0.0661 at +0.676 predicted. The other
zeros agree to 1-30% in amplitude and within 0.1 rad in phase.

**Consequence for every genus.** Let X be any closed or cusped hyperbolic surface of genus >= 1 and Y an embedded
incompressible one-holed torus with geodesic boundary. The simple closed geodesics of X lying in Y are exactly the
non-peripheral simple geodesics of Y. Their count is Area(B_Y) R^2/(2 zeta(2)) + sum_rho c_rho(Y) R^rho + ..., with
c_rho(Y) = Z_{B,Y}(rho)/(2 rho zeta'(rho)), and the error is not O(R^{1/2-eps}) whenever some Z_{B,Y}(rho) != 0. The
same holds for embedded four-holed spheres. So every hyperbolic surface of genus >= 1, and every cusped one of
complexity >= 1, carries the Riemann zeros in the simple-length spectrum of each such subsurface, and the subsurface
moduli decide their amplitudes.

**Why the full count in genus >= 2 should not show them.**
- In complexity one, every integral measured lamination is k gamma for a single simple curve gamma. So
  2 zeta(s) eta(s) = Z_ML(s) exactly, where eta(s) = sum_gamma l^-s, and Z_ML is the lattice zeta, which is smooth
  (Theorem 3).
- In complexity >= 2, ML(Z) also contains multicurves sum k_i gamma_i. One only has zeta(s) eta(s) = Z_ML^(1)(s), the
  one-component stratum, and nothing makes that stratum smooth.
- Even if it were, the zeros would contribute L^{1/2} against a main term L^{6g-6+2n}. Mirzakhani-type error terms
  (power savings, Eskin-Mirzakhani-Mohammadi) sit far above L^{1/2}.

**Conjecture.** In complexity >= 2 the total simple-geodesic count has no detectable zeta-zero oscillation. The zeros
are visible exactly through complexity-one subsurfaces.

## The flat/hyperbolic dictionary: Z_B is a hyperbolic Epstein zeta function (2026-11-26)

**Poincare-series form.** Simple closed curves on the once-punctured torus correspond to Gamma_inf\SL2(Z), where
Gamma_inf is the stabiliser of alpha (Dehn twists). So

    P_s(X) := sum_{gamma simple} l_gamma(X)^-s = sum_{g in Gamma_inf\SL2Z} l_alpha(gX)^-s,
    Z_B(s; X) = 2 zeta(s) P_s(X).

P_s is a Poincare series on Teichmuller space (= H), invariant under the mapping class group. Its flat counterpart is
the Eisenstein series. For a unit-area flat torus of modulus z, the length of (m, n) is |mz + n|/sqrt y, and

    Z_flat(s) = sum_{(m,n) != 0} (y/|mz+n|^2)^{s/2} = 2 zeta(s) E(z, s/2)      (Epstein = zeta x Eisenstein).

| Flat torus (classical) | Hyperbolic torus (this project) |
|---|---|
| Epstein zeta = 2 zeta(s) E(z, s/2) | Z_B = 2 zeta(s) P_s |
| E(z, s) has poles at zeros of xi(2s); E* = xi(2s) E is entire except at 0, 1 | P_s has poles at the zeta zeros rho with residue Z_B(rho)/(2 zeta'(rho)); Z_B is entire except at 2 (Theorem 3, Lemma C) |
| Constant term y^s + phi(s) y^{1-s}, phi = xi(2s-1)/xi(2s) | Theorem 11: 2 zeta(s) l^-s + (2/l) zeta(s-1) I(s, W) + o(1/l); the hyperbolic collar puts W^{1-s} where the flat case has l^{s-1} |
| Chowla-Selberg: Poisson in one variable, Fourier terms sigma_{1-2s}(n) K_{s-1/2}(2 pi n y) | Hyperbolic Chowla-Selberg (below): Fourier terms sigma_{1-s}(m) h_m(l, tau) |
| Siegel mean value: the average lattice count is exactly the volume | Averaged lattice count is exactly zeta(2) t^2 (Theorem 7); this is Mirzakhani's integration formula for M_{1,1} (cut along gamma, V_{0,3} = 1) |
| Zagier: renormalised int_F E(z, s) dmu = 0 | <Z_B(s)> = 0 on Re s < 2: Mirzakhani gives the formal integral prop. to int_0^inf l^{1-s} dl, which converges nowhere and is 0 after regularisation; the cusp lemma is what makes the moduli integral converge |
| Primitive points in ellipses: Riemann zeros in the error, amplitude prop. to E*(z, rho/2) | Simple geodesics: amplitude Z_B(rho)/(2 rho zeta'(rho)) |
| Blind flat tori: zeros of E*(., rho/2) | Blind hyperbolic tori: zeros of Z_B(rho; .) |

Honest attribution: the averaging results (Theorem 7) are Mirzakhani's integration formula plus a convergence argument.
The new parts are the hyperbolic Chowla-Selberg identity, the continuation (Theorem 3 with Lemma C), and the blind
surfaces.

**Hyperbolic Chowla-Selberg formula (exact).** Use Fenchel-Nielsen coordinates (l, tau) about alpha, and write
N(x) = N_X(x alpha + beta) for the stable norm on the line q = 1. Homogeneity gives N(p alpha + q beta) = q N(p/q)
exactly. Then:
- Poisson summation over p in each class mod q gives sum_{(p,q)=1} N(p/q)^-s = sum_m c_q(m) h(m), with Ramanujan sums
  c_q(m) and h(m) = int_R N(x)^-s e^{-2 pi i m x} dx.
- Ramanujan's identity sum_q c_q(m) q^-s = sigma_{1-s}(m)/zeta(s) then gives

      Z_B(s) = 2 zeta(s) l^-s + 2 zeta(s-1) h(0) + 2 sum_{m != 0} sigma_{1-s}(|m|) h(m).

  This holds for Re s > 2, and by continuation wherever both sides converge.

**Evaluation.** N is the piecewise-linear interpolation of the exact fan lengths
2 acosh(coth(l/2) cosh((tau + kl)/2)), corrected by the deeper Farey deficiencies, which are about e^{-2W}. Keeping only
the piecewise-linear part (`cusp_whittaker2.py`), the relative error against the true Z_B is:

| l | rho_1 | rho_4 | rho_10 |
|---|---|---|---|
| 0.3 | 3e-4 | 4e-4 | 1.3e-3 |
| 0.6 | 6e-3 | 9e-3 | 1.7e-2 |
| 1.0 | 6e-2 | 3e-2 to 2e-1 | 1.2e-1 to 1.7e-1 |

The flat version of the same derivation is the classical Chowla-Selberg formula.

**Blind flat tori** (`flat_blind.py`, `flat_degrees.py`). Zeros of E*(z, rho_k/2) on the half fundamental domain, each
confirmed by Newton:

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| flat zeros | 1 | 3 | 4 | 8 | 7 | 10 | 12 | 11 | 18 |
| flat signed count = boundary winding | +1 | +1 | 0 | +2 | +1 | +2 | +4 | +3 | +2 |
| hyperbolic zeros (fine census) | 1 | 3 | 4 | 8 | 7 | ? | ? | ? | ? |
| hyperbolic boundary winding (adaptive, steps < 0.3 rad) | +1 | +1 | 0 | +2 | -1 | +2 | +1 | -2 | +1 |

The flat zeros all lie below the turning point of the first Fourier mode, y = gamma/(4 pi), up to an Airy tail: y = 1.17
against 1.12 for k = 1. Their number grows like gamma^2, about gamma^2/150.

**Threshold law, hyperbolic.** The m-th twist harmonic h(m) has stationary points iff gamma l M(W) >= 2 pi m, where
M(W) = max_u tanh u/(W + 2 log cosh u) and W = 2 log(2 coth(l/2)). Below the m = 1 threshold all harmonics are
exponentially small apart from twist-independent corner terms, so Z_B is twist-independent and nonzero.

| gamma | predicted m = 1 threshold | smallest blind systole |
|---|---|---|
| 14.1 | 1.58 | 1.596 |
| 30.4 | 0.99 | 0.97 |
| 49.8 | 0.714 | 0.707 |

At larger gamma the smallest blind systole sits just above the m = 2 threshold instead: 0.599 vs 0.577 at gamma = 133.5,
0.522 vs 0.498 at gamma = 163. The constant term carries zeta(rho - 1), which grows about like gamma/(2 pi), so a single
harmonic is no longer enough to cancel it.

The zero counts agree for k = 1..5. The signed counts agree for k = 1-4 and 6, and differ for k = 5, 7, 8, 9. A zero can
leave the mirror triangle through a mirror edge by merging with its reflection, so the signed count in the triangle is
not invariant under deformation. The k = 5 hyperbolic boundary path passes within 0.006 of a zero.

For k >= 6 the Newton census does not converge from the coarse cells, so those counts are open.

**Shape coordinates.** The flat zeros and the hyperbolic zeros correspond one to one, in order, for k = 1..5:
(|z|, |z-1|) for the flat torus against (b/a, c/a) for the hyperbolic sink lengths. The hyperbolic points are
systematically stretched (`shape_compare.py`).

## The cone-angle deformation: blind hyperbolic tori ARE deformed blind flat tori (`cone_track*.py`, `flat_limit.py`)

**The family.** Hyperbolic tori with one cone point of angle theta have Fricke relation x^2 + y^2 + z^2 - xyz = kappa,
kappa = 2 - 2 cos(theta/2) in [0, 4), and area A = 2 pi - theta.
- kappa = 0 is the cusp; kappa < 0 gives geodesic boundary.
- As kappa -> 4, the surfaces rescaled to unit area tend to flat tori.
- All the machinery works for kappa < 4, since the sandwich constant K = 16 - 4 kappa > 0.

**Why the limit is flat.** Put t = 2 + A n^2/4, with n the unit-area flat length. Then the Fricke relation becomes, at
order A^2, Heron's formula: -A^2 T^2 = -(4 - kappa), with T = 1/2 the area of the flat triangle (1, |z|, |z-1|). So
A = 2 sqrt(4 - kappa), which is exactly Gauss-Bonnet. The Markoff recursion t_m + t_d = t_u t_w becomes the
parallelogram law n_{u+w}^2 + n_{u-w}^2 = 2 n_u^2 + 2 n_w^2. The Markoff tree degenerates into the Euclidean lattice.

**Values.** A^{rho/2} Z_{B,kappa}(rho) -> 2 pi^{rho/2} E*(z, rho/2)/Gamma(rho/2). At the hexagonal and square points,
for rho_1 and rho_2, the relative error is 8-13% at A = 0.635, 3.6-5.9% at 0.401 and 1.05-1.7% at 0.200, about
O(A^1.8). Proof strategy: the hyperbolic Chowla-Selberg expansion converges term by term to the classical one.

**Zeros.** Each blind surface was tracked by continuation in kappa (log-length variables, a guard against jumping
between zeros, |Z| < 1e-9 at every step), and the shape was extrapolated linearly in A to A = 0:

| zero | kappa = 0 (cusped) | last tracked | extrapolated to A = 0 | flat blind torus |
|---|---|---|---|---|
| rho_1 (X*) | (1.2663, 1.4430) | (1.2169, 1.3654) at A = 0.283 | (1.2117, 1.3571) | (1.2117, 1.3571), z = 0.3133 + 1.1705 i |
| rho_2 a | (1.6768, 1.8226) | (1.5548, 1.6798) at A = 0.571 | (1.5280, 1.6479) | (1.5256, 1.6452), z = 0.3104 + 1.4937 i |
| rho_2 b | (1.2092, 1.5615) | (1.1762, 1.4797) at A = 0.539 | (1.1691, 1.4625) | (1.1686, 1.4607), z = 0.1160 + 1.1628 i |
| rho_2 c | (1.1569, 1.2615) | (1.1339, 1.2252) at A = 0.548 | (1.1286, 1.2172) | (1.1284, 1.2164), z = 0.3968 + 1.0563 i |

Every path is smooth and monotone, with no births, deaths or collisions, and each ends on its own flat partner.

**Conclusion (numerical, strong).** The blind hyperbolic surfaces are continuous deformations, through blind cone
tori, of the zeros of the completed Eisenstein series E*(z, rho/2), which are classical objects. For small k the
deformation is a bijection. For larger k zeros can enter or leave the triangle through the mirror edges, which accounts
for the mismatches in signed count.

**Conjectures.**
1. The flat limit A^{s/2} Z_{B,kappa}(s) -> 2 zeta(s) E(z, s/2) holds locally uniformly in s. This looks provable
   through the Chowla-Selberg expansions.
2. The zero set of Z_{B,kappa}(rho; .) over (kappa, moduli) is a union of smooth curves, transverse to each kappa-slice
   away from the mirror edges, so the number of blind cusped tori equals the number of zeros of E*(., rho/2) up to
   mirror-edge events.
3. Both counts are about gamma^2/150 in the half fundamental domain.

## Theorem: the flat limit (proof; `flat_limit_lemmas.py`, `flat_limit.py`)

**Setting.** Fix z in H and A in (0, A0). Let T_z be the conformal torus C/(Z + zZ) with marked point p, and g_0 its flat
metric of area 1. By McOwen-Troyanov there is a unique conformal metric of curvature -1 on T_z with a cone point of
angle theta = 2 pi - A at p. Its area is A by Gauss-Bonnet. Call it X_{A,z}. Its holonomy traces satisfy the Fricke
relation with kappa = 2 - 2 cos(theta/2), so A = 2 sqrt(4 - kappa) + O((4 - kappa)^{3/2}).

Notation:
- N_{A,z}(v) is the length of the shortest closed curve in the homology class v;
- n_z(v) = |m + n z|/sqrt(Im z) is the flat unit-area length;
- Z_{A,z}(s) = sum_{v != 0} N_{A,z}(v)^-s is the stable-norm zeta;
- Z_flat(s; z) = sum n_z(v)^-s = 2 zeta(s) E(z, s/2).

**Theorem.** As A -> 0, A^{s/2} Z_{A,z}(s) -> Z_flat(s; z) locally uniformly in (s, z) on {Re s > 0, s != 2} x H.
On compact sets the error is O(A |Z_flat(s)| + A^{sigma/4 - eta}) for every eta > 0. In particular, at the zeta zeros,

    A^{rho/2} Z_{A,z}(rho) -> 2 pi^{rho/2} E*(z, rho/2)/Gamma(rho/2).

**Step 0 (trace length = geometric length).** A shortest curve in the class v exists. It avoids p: a geodesic through a
cone point of angle < 2 pi makes an angle < pi on one side and can be shortened. So it is a closed hyperbolic geodesic in
T \ p. It is simple, so it lies in the unique non-peripheral simple class with homology v. Develop it into H^2: its lift
is a geodesic line translated by the holonomy. Hence 2 acosh(|tr rho(v)|/2) = N_{A,z}(v), and the trace-defined Z_B of the
earlier sections is Z_{A,z}.

**Step 1 (uniform length comparison).** Write the rescaled metric as A^{-1} g = e^{2 phi} g_0. It has curvature -A and a
cone point of angle 2 pi - A, so distributionally

    Delta_0 phi = A e^{2 phi} - A delta_p,      int e^{2 phi} dA_0 = 1.

Let G be the Green's function with Delta_0 G = delta_p - 1 and int G = 0; near p, G ~ (1/2pi) log|x - p|.
- Put phi = -A G + psi. Then Delta psi = A(e^{2 phi} - 1).
- e^{-2AG} lies in L^q for every q < infinity, with norm 1 + O(A).
- The Green's operator maps L^q to L^infinity for q > 1. A contraction argument therefore gives
  ||psi - c||_infinity = O(A^2).
- The normalisation, together with int G = 0, gives c = O(A^2).
- So phi = -A G + O(A^2) uniformly, locally uniformly in z.

Consequences:
- **Lower bound.** phi >= -A max G - C A^2, and every curve in class v has flat length >= n(v). So
  N(v)/sqrt(A) >= (1 - c1 A) n(v), with c1 = max_x G_z(x, p) + O(A).
- **Upper bound.** The parallel flat geodesics c_u of class v foliate the torus. By coarea,
  avg_u L(c_u) = n(v) int e^phi dA_0 = n(v)(1 + int phi + O(A^2)) = n(v)(1 + O(A^2)). So
  N(v)/sqrt(A) <= (1 + c2 A^2) n(v).

Both bounds hold uniformly in v.

**Step 1' (first order, explains the data).** Averaging G along the line at transverse position x gives
-(x^2 - x + 1/6)/(2 n(v)^2), from the Fourier series of G over dual vectors orthogonal to v, which have length >= n(v).
The best line has x = 1/2. So for primitive v,

    N(v)/(sqrt(A) n(v)) = 1 - A/(24 n(v)^2) + O(A^2).

Equivalently, N(v)^2 + A^2/12 = A n(v)^2 + O(A^3 n^2) for short curves. The Markoff recursion t_m + t_d = t_u t_w,
expanded with t = 2 + N^2/4 + N^4/192 + ..., gives the same thing algebraically: the parallelogram defect is

    N_m^2 + N_d^2 - 2 N_u^2 - 2 N_w^2 = (A^2/6) (Q_u Q_w - B(u,w)^2) + ... = A^2/6

for every unimodular Farey cell (Q = n^2, B the polar form). The analysis and the algebra agree.

**Step 2 (angular expansion).** N' = N/sqrt(A) is a norm on H_1(T; R) = R^2, identified with the flat period lattice,
so N'(v) = n(v)(1 + eps(theta_v)). Here eps is even, Lipschitz, and sup |eps| <= c1 A by Step 1. Put
F_s(theta) = (1 + eps(theta))^-s = sum_k f_k(s) e^{ik theta}, with k even. For Re s > 2,

    A^{s/2} Z_{A,z}(s) = sum_k f_k(s) Z_k(s),     Z_k(s) = sum_{omega in Lambda \ 0} |omega|^-s (omega/|omega|)^k,

with absolute convergence. The Z_k are Hecke's angular Epstein zeta functions of the unimodular lattice Lambda:
- Z_0 = Z_flat;
- for k != 0, Z_k is entire;
- Lambda_k(s) = pi^{-s/2} Gamma((s + |k|)/2) Z_k(s) satisfies a functional equation s <-> 2 - s, with the dual lattice,
  which is Lambda rotated by 90 degrees.

**Bounds.**
- *Z_k.* On Re s = 2 + eta, |Z_k| <= Z_flat(2 + eta). On Re s = -eta, the functional equation and Stirling give
  |Z_k| <= C (|k| + |t| + 2)^{1 + eta}. Phragmen-Lindelof then gives, uniformly in k,
  |Z_k(sigma + it)| << (|k| + |t| + 2)^{1 - sigma/2 + eta} for -eta <= sigma <= 2 + eta.
- *f_k, first bound.* N' is the support function of the dual ball, so N' + N'' >= 0 as measures on the circle, with
  total mass the perimeter of the dual ball (about 2 pi). So eps'' is a finite measure with TV(eps'') <= C uniformly in
  A, and eps' is bounded. Hence F_s'' = -s(1+eps)^{-s-1} eps'' + s(s+1)(1+eps)^{-s-2} eps'^2 has total variation
  <= C(s), and |f_k(s)| <= C(s)/k^2.
- *f_k, second bound.* sup |F_s - 1| <= C(s) A gives |f_0 - 1| <= C(s) A and |f_k| <= C(s) A for all k.

**Conclusion.**
- For sigma > 0, the series sum_{k != 0} f_k Z_k converges absolutely and locally uniformly, since
  sum k^-2 k^{1 - sigma/2} < infinity. So the right side continues A^{s/2} Z_{A,z} to Re s > 0, with only the pole of
  f_0 Z_flat at s = 2; it agrees with the cell-sum continuation by uniqueness.
- The error is
  sum_k min(A, k^-2) k^{1 - sigma/2 + eta} = O(A^{sigma/4 - eta}), splitting the sum at k = A^{-1/2},
  plus |f_0 - 1| |Z_flat| = O(A).
- Every constant depends continuously on z through max G_z and the lattice. ∎

**Corollary (zeros).** Let z0 be a zero of E*(., rho/2) with nonzero Jacobian. For all small A there is a zero
z_A -> z0 of z -> Z_{A,z}(rho) with the same local degree. This follows from uniform convergence on a small circle
around z0, where |E*| >= eta > 0, and the winding number. Conversely, zeros of Z_{A,.}(rho) in a compact set accumulate
only at zeros of E*. So for small cone area, the blind cone tori are exactly the deformations of the blind flat tori.
The continuation computations above carry the rho_1 and rho_2 families all the way down to the cusp (kappa = 0).

**Numerical checks of the lemmas** (`flat_limit_lemmas.py`; the shape has flat lengths about 1 : 1.2).
- **Parallelogram defect.** D/(A^2/6) for short cells is 0.954 at A = 0.200 and 0.969 at A = 0.063, tending to 1.
  Long cells give D ~ 0, outside the small-N expansion, where D is negligible against N^2.
- **Uniform comparison.** Against the fitted unimodular form, which has det 1 - O(A^2), the worst relative length
  error over all 1.4k-13.6k simple curves up to hyperbolic length 30 is 2.4e-2, 1.6e-2, 8.4e-3 and 2.8e-3 at
  A = 0.64, 0.40, 0.20 and 0.063, about 0.042 A. It does not grow with length.
- **Signs.** All deviations (N/(sqrt(A) n) - 1)/A are <= 0, as the upper bound requires. The minimum is -0.0415, at the
  shortest curve (n about 1), against the predicted -1/24 = -0.0417. The rigorous constant c1 = max G is about
  ln 2/(4 pi) = 0.055 near the square torus.
- **Shape of the error.** Long curves with directions near a short curve inherit its deficit, so eps(theta) has spikes
  at rational directions. These are the vanishing corners of the hyperbolic stable norm.
- **Values.** The values converge faster than the proved A^{sigma/4} (`flat_limit.py`: about A^1.8). The f_k bound
  min(A, k^-2) ignores the cancellation among corners.

## First-order flat limit, and why the Riemann zeros converge fast (`flat_first_order.py`)

**Theorem (Re s > 2).**

    A^{s/2} Z_{A,z}(s) = Z_flat(s; z) + (A/12) s zeta(s) E(z, s/2 + 1) + o(A),

locally uniformly.

*Proof.* Write N'(v) = n(v)(1 + eps(v)).
- **Pointwise first order.** For each primitive w, eps(w)/A -> -1/(24 n_w^2).
  - Upper bound: use the straight line at transverse position 1/2 (Step 1').
  - Lower bound: by Step 1, the minimiser c_A has flat length n + O(A). So it lies within O(sqrt A) of a straight closed
    geodesic. Then L_A(c_A) >= int (1 + phi)|c'| >= n - A int_{c_A} G + O(A^2). Since G is bounded above and upper
    semicontinuous, limsup int_{c_A} G <= n max_u Gbar(u) = n/(24 n^2).
- eps(kw) = eps(w) by homogeneity, and |eps|/A <= c1 uniformly (Step 1).
- (1 + eps)^-s = 1 - s eps + O(A^2) uniformly.
- Dominated convergence for sum n^-sigma, sigma > 2, then gives
  sum_v n_v^-s (-s eps(v))/A -> (s/24) sum_{w prim} sum_k (k n_w)^-s n_w^-2 = (s/24) zeta(s) Z_flat(s+2)/zeta(s+2),
  which equals (s/12) zeta(s) E(z, s/2 + 1). ∎

**Check** (hexagonal and square, z exact):

| s | point | measured / predicted at A = 0.4, 0.2, 0.1, 0.05 |
|---|---|---|
| 3 | hexagonal | 1.112, 1.061, 1.033, 1.018 |
| 3 | square | 1.107, 1.058, 1.031, 1.017 |
| 4 | hexagonal | 1.069, 1.035, 1.017, 1.009 |
| 4 | square | 1.067, 1.033, 1.017, 1.008 |

The coefficients are 0.684 and 0.738 at s = 3, and 0.734 and 0.826 at s = 4.

**At the zeta zeros the first-order term vanishes**, because of the factor zeta(s). The factor comes from summing over
multiples k w, whose deficit equals that of w.
- At s = rho_1, |A^{rho/2} Z_A - Z_flat|/A = 0.77, 0.45, 0.26, 0.14 (hexagonal) and 0.71, 0.42, 0.24, 0.13 (square).
- So the remainder is A^2 log(1/A): divided by A^2 it grows by a constant 0.32 per halving of A.
- This is the "A^1.8" seen earlier.
- The theorem is proved only for Re s > 2. On 0 < Re s < 2 the formal first-order term has a pole at s = 1 from
  s zeta(s), which the true function lacks, so the expansion there must be different. For example, long curves near
  short rational directions follow the short curve's best line ("staircases") and contribute about A^{sigma/2}. Their
  terms also carry the multiples sum zeta(s), consistent with the fast convergence at rho.

**Consequence for blind surfaces.** The zeros of z -> Z_A(rho; z) move only O(A^2 log(1/A)) in the conformal modulus.
The linear-in-A drift of the tracked zeros in shape coordinates (b/a, c/a) should therefore be exactly the length law
N/sqrt(A) = n(1 - A/(24 n^2)). It is. For the rho_1 family, with unit-area lengths of the flat zero
(0.924, 1.120, 1.254), the predicted slopes are 0.0189 for b/a and 0.0303 for c/a. Cone tracking observed 0.0176-0.0184
and 0.0282-0.029.

## The flat limit inside the strip: staircase geodesics and an exact second term (`flat_strip*.py`)

**Staircases.** Fix a primitive w (flat length n) with Farey partner w', and consider v = a w + b w'. Write T = a n for
its extent along w and u for the transverse coordinate, so that lines are spaced 1/n apart.
- Averaged along w, the potential -A G is exactly quadratic: -A Gbar = -A/(24 n^2) + (A/(2 n^2))(u - 1/2)^2, with a
  kink on the line through p (Step 1').
- To first order, the length of a curve in class v minimises int [x'^2/2 - A Gbar(x)] dt, with x = u/n and transverse
  shift b/n. Its Euler-Lagrange equation is u'' = A(u - 1/2): hyperbolic motion, sitting on the best line and crossing
  the cone-point line |b| times.
- The exact solution gives the deficit

      L_A(v) - n_v = (sqrt(A) |b|/(4 n^2)) Psi(sqrt(A) T/(2|b|)),     Psi(y) = coth y - 1/y - y/3.

- Psi interpolates between straight lines (Psi ~ -y^3/45, second order in A) and staircases (Psi ~ 1 - y/3, a deficit
  of -A T/(24 n^2), the full first-order deficit of w).

**Summing.**
- Sum over a coprime to b (density phi(b)/b), over b != 0 (Ramanujan: sum phi(b) b^-s = zeta(s-1)/zeta(s)), over
  primitive w (sum n_w^-3 = Z_flat(3)/(2 zeta(3)) = E(z, 3/2)), and over multiples (zeta(s)).
- The Mellin transform needed is, from coth y - 1/y = sum_k 2y/(y^2 + pi^2 k^2),

      M(s) = int_0^inf y^{-s-1} Psi(y) dy = pi^{-s} zeta(s+1)/cos(pi s/2),

  which agrees with quadrature to 8 digits at s = 1.5 and 2.5.

**Two-term law (derived; numerically exact to the order shown).**

    A^{s/2} Z_{A,z}(s) = Z_flat(s; z) + (A/12) s zeta(s) E(z, s/2 + 1)
                         - 2^{-s} s zeta(s - 1) E(z, 3/2) M(s) A^{(s+1)/2} + O(A^2),     0 < Re s < 3.

**Consistency checks.**
- *s = 1.* zeta(0) = -1/2 and M ~ -1/(3(s-1)) make the staircase residue -(A/24) Z_flat(3)/zeta(3), which cancels the
  pole of the first-order term exactly, as it must, since the true function has no pole at s = 1. What remains is
  (A/48)(Z_flat(3)/zeta(3)) log(1/A).
- *Sizes.* For s < 1 the staircase term dominates, at size A^{(s+1)/2}. For s > 1 the first-order term dominates.
- *s = rho.* The first term vanishes exactly. The second is suppressed by 1/|cos(pi rho/2)| ~ 2 e^{-pi gamma/2}, about
  1e-10 at rho_1. This is why blind surfaces converge like A^2 log(1/A).

**Check** (hexagonal torus, z exact, no fitted constants). Measured diff/A against the two-term prediction:

| s | first-order coeff | staircase coeff | A = 0.4 | A = 0.1 | A = 0.025 |
|---|---|---|---|---|---|
| 0.5 | -0.3433 | 0.5667 | 0.3704 / 0.3692 | 0.6645 / 0.6644 | 1.0818 / 1.0818 |
| 0.8 | -1.2396 | 1.4487 | 0.3495 / 0.3481 | 0.5843 / 0.5842 | 0.8554 / 0.8554 |
| 1.2 | 1.8825 | -1.7316 | 0.3040 / 0.3025 | 0.5072 / 0.5070 | 0.6851 / 0.6851 |
| 1.5 | 0.9885 | -0.9760 | 0.2137 / 0.2122 | 0.4397 / 0.4396 | 0.6003 / 0.6004 |
| 2.5 | 0.6826 | 0.3890 | 0.8566 / 0.8783 | 0.7462 / 0.7518 | 0.7057 / 0.7071 |

The gaps fall like A^2 (0.0012, 0.0004, 0.0001, 0.0000 at s = 0.5). At s = 2.5 the gap is -0.054 A^2, the next order.

**Status.**
- The first-order term is proved for Re s > 2.
- The staircase term is derived from the exact solution of the first-order variational problem. It is not yet proved:
  that needs uniform control of the first-order reduction for curves of length about A^{-1/2}, and of the
  interchange of sums.
- The agreement above, with the pole cancellation built in, is strong evidence that it is correct.

## Counting blind flat tori: N(gamma) ~ 0.0065 gamma^2 (`flat_census2.py`, `flat_kacrice.py`)

**Method.** A fast census of the zeros of E*(z, rho_k/2) on the half fundamental domain.
- For each height y the Fourier coefficients are computed once; all x then follow from cosines.
- Every winding cell is confirmed by Newton on the full series.
- It reproduces the earlier counts 1, 3, 4, 8, 7, 10, 12, 11, 18 for k = 1..9.

| k | gamma | zeros N | N/gamma^2 | N / Berry (t^2/24) | highest zero y | turning point t/(2 pi) |
|---|---|---|---|---|---|---|
| 9 | 48.0 | 18 | 0.0078 | 0.75 | 3.36 | 3.82 |
| 15 | 65.1 | 26 | 0.0061 | 0.59 | 2.70 | 5.18 |
| 20 | 77.1 | 36 | 0.0061 | 0.58 | 5.74 | 6.14 |
| 30 | 101.3 | 61 | 0.0059 | 0.57 | 3.76 | 8.06 |
| 45 | 133.5 | 119 | 0.0067 | 0.64 | 4.15 | 10.62 |
| 60 | 163.0 | 177 | 0.0067 | 0.64 | 3.22 | 12.97 |
| 80 | 201.3 | 264 | 0.0065 | 0.63 | 5.11 | 16.02 |
| 100 | 236.5 | 365 | 0.0065 | 0.63 | 4.57 | 18.82 |

So **N(gamma) = (0.0065 +- 0.0003) gamma^2**, about 0.62 of Berry's isotropic random-wave value t^2/(4 pi) x area(pi/6).
At large k some Newton calls stalled, so these counts may be slight underestimates.

**Where the zeros sit.** No zero lies above the first-mode turning point. At small k the highest zero sits right at it
(k <= 7), as the harmonic-threshold law says. At large k the zeros stay in a bulk region whose top is well below it.

**Gaussian Kac-Rice.** A model with the exact covariance of (f, f_x, f_y) at each height, the true mean C(y), and its
gradient C'(y) gives observed/predicted ratios of 1.26, 1.32, 1.10 and 1.21 at k = 15, 20, 30 and 45.
- The mean's gradient matters. C ~ y^{1-s} turns its phase at rate t/y, as fast as the wave. Leaving the gradient out
  under-predicts by a steady factor of about 2.1.
- The deficit against Berry reflects a constant term that stays comparable to the fluctuations throughout the bulk:
  E* is a random-looking wave plus a deterministic mean of the same size.

**Consequence.** By the flat-limit corollary, nondegenerate blind flat tori persist as blind cone tori for small area.
Blind cone tori of small cone area therefore number about 0.0065 gamma^2 per zeta zero, up to mirror-edge events and
degenerate zeros. This is conjectural for the full count; the persistence is proved.

## Correction: hyperbolic census for k >= 6 was precision-limited; corrected counts (`hyp_census2.py`, `hyp_census5_k*.log`)

**The problem.** The double-precision evaluator on the ray theta = pi/3 loses about (pi/6) gamma/ln 10 digits, roughly
8.4 at gamma = 37. Its absolute error is then about 2e-5, larger than the 1e-7 residual that zeros had to pass. Every
"Newton failure" for k >= 6 was this, not missing zeros. At a test point (k = 6), the rays 0.4 pi, 0.45 pi and 0.48 pi
agree to about 1e-8 while pi/3 is off by 2e-5. The census now uses theta = 0.45 pi.

Blind cusped tori, every count Newton-confirmed:

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| hyperbolic (cusped) | 1 | 3 | 4 | 8 | 7 | 8 | 11 (12 winding cells) | 14 |
| flat (E*) | 1 | 3 | 4 | 8 | 7 | 10 | 12 | 11 |

The counts agree exactly for k <= 5 and stay close for k = 6..8. The totals for k <= 8 are both 56. Beyond k = 5 the
bijection is not exact. That fits the mirror-edge events along the cone deformation, which the signed counts already
showed (k = 5, 7, 8, 9). A grid cell holding a pair of zeros of opposite degree could also hide both, so the hyperbolic
counts for k >= 6 are lower bounds.

The earlier k <= 5 results used theta = pi/3, where the error is about 1e-6 at gamma <= 33. They stand, because those
zeros are nondegenerate (|J| about 10), so the error moves them by only about 1e-7. The X* certificate used
theta = pi/3 and 0.4 pi at gamma = 14.1, where the error is about 1e-9, and also stands.

## Amplitude growth: |Z(rho)|^2 ~ gamma, so sum |c_rho|^2 diverges (flat case; `flat_amplitudes.py`, `flat_amp_theory.py`)

**Derivation.** Epstein's functional equation for a unimodular lattice gives

    Z(rho) = pi^{rho-1} Gamma(1 - rho/2)/Gamma(rho/2) Z(2 - rho),     so     |Z(rho)|^2 ~ (gamma/2 pi) |Z(3/2 - i gamma)|^2.

Z(3/2 + it) = sum_m r(m) m^{-3/4 - it/2}, where r(m) counts lattice vectors of squared length m.
- *Line average.* The Montgomery-Vaughan mean value theorem gives a mean square of M_z = sum_m r(m)^2 m^{-3/2}. For the
  hexagonal lattice M_z = 68.28.
- *Average over zeta zeros.* This is biased. By Landau's formula, the average of x^{i gamma} over zeros is
  -Lambda(x) x^{-1/2}/log(T/2 pi), so every pair with m/n = p^{2k} contributes.
- *Prediction.*

      <|Z(rho)|^2>/gamma ~ (1/2 pi) [M_z - 2 C_z/log(gamma/2 pi)],   C_z = sum_{n, p^k} r(n) r(n p^{2k}) (n^2 p^{2k})^{-3/4} Lambda(p^k) p^{-k/2},

  with C_z = 48.2 for the hexagonal lattice.

**Check** (hexagonal flat torus, first 300 zeros, gamma <= 542):

| gamma band (centre) | 90 | 179 | 277 | 376 | 473 |
|---|---|---|---|---|---|
| Landau-corrected prediction | 5.10 | 6.28 | 6.81 | 7.12 | 7.32 |
| observed <abs(Z)^2>/gamma | 6.37 | 7.16 | 7.42 | 6.69 | 7.50 |

The uncorrected limit is 10.87. Approaching it slowly from below is the Landau bias.

**Consequence.** c_rho = Z(rho)/(2 rho zeta'(rho)), so |c|^2 ~ (<|Z|^2>/gamma)/(4 gamma |zeta'(rho)|^2). Under
Gonek-Hejhal (sum_{gamma <= T} 1/|zeta'|^2 ~ 6T/pi^3), 2 sum_{gamma <= T} |c|^2 diverges like a constant times log T.
Observed: 0.763, 0.944, 1.125, 1.218 and 1.281 at T = 50, 100, 200, 300 and 400, about +0.18 per doubling. At these
heights the effective constant is below 6/pi^3, since <1/|zeta'|^2> per unit gamma is about 0.085 here, and the
asymptote is reached slowly.

**Meaning.**
- The sharp primitive count in an ellipse, and by the flat limit in a stable-norm ball of small-area cone tori, is not
  B^2-almost-periodic with finite variance.
- With the natural truncation T ~ R, the mean square of E_P/sqrt R grows like log R, conditional on RH, simple zeros,
  Gonek-Hejhal and the mean-square law.
- This settles the earlier "is the 20-zero sum the whole sharp error?" question for the flat case. The zero sum is
  complete, but its variance is infinite and grows slowly, so any finite truncation explains a shrinking share. That
  matches the earlier observations: the share explained by 20 zeros was low, and the rms of E_P/sqrt R crept up with R
  on the modular torus (0.77, 1.08, 1.15 at R ~ 1e4, 1e5, 1e6).
- The hyperbolic check needs |Z_B(rho_k)| for many more k. That computation (k = 21-60, mpmath at dps 66-90) is running.

## Hyperbolic vs flat: bounded amplitudes and a finite-variance sharp error (`hyp_amplitudes.py`, `zeros_hi_*.log`)

**Mechanism.** Write Z(s) = s int R^{-s-1} dA(R) = (pole part) + s F(s), with F(s) = int R^{-s-1} E_A(R) dR. By
Mellin-Plancherel in log R,

    int |F(1/2 + it)|^2 dt = 2 pi int R^{-2} |E_A(R)|^2 dR.

- **Flat.** The lattice error E_A ~ R^{1/2} (circle-problem size), so the right side diverges logarithmically. This is
  the |Z(rho)|^2 ~ gamma law above.
- **Hyperbolic.** E_A plateaus, with rms about 250-340 up to R = 2e6 (earlier sections). The integral converges, so the
  mean square of Z_B on the critical line is o(T), and heuristically bounded at a level set by the plateau.
- **Prediction.** <|Z_B(rho)|^2> stays bounded and sum |c_rho|^2 converges (with Gonek-Hejhal,
  sum 1/(gamma^2 |zeta'|^2) < infinity). The sharp error then has a finite-variance limiting distribution, unlike the
  flat case.

**Check** (modular torus, k = 1..34, mpmath at theta = pi/4).

| | gamma < 40 | 40-70 | 70-111 |
|---|---|---|---|
| modular <abs(Z_B)^2> | 164 | 167 | 187 |
| modular <abs(Z_B)^2>/gamma | 5.6 | 3.3 | 2.0 |
| modular 2 sum abs(c)^2 below T = 40, 70, 103 | 0.418 | 0.526 | 0.554 |
| flat hexagonal, same T | 0.720 | 0.862 | 0.947 |

- **Hyperbolic.** A log-log fit gives |Z_B|^2 ~ gamma^0.26, and the increments of the sum shrink (0.108, then 0.028).
  The total is about 0.6.
- **Flat.** The sum keeps growing logarithmically (increments 0.142, 0.085), with <|Z|^2>/gamma about 7 throughout.

**Numerical caveat.** The k = 21-60 run exposed a limitation of the mpmath evaluator. The 40-term Bernoulli series on
|t| < 0.05 has truncation error about (c T0/2 pi)^40 ~ 1e-18, which more working digits do not reduce. The 1/Gamma(rho)
cancellation amplifies it by about e^{0.785 gamma}. Values are therefore invalid above gamma ~ 115 (k >= 39; |Z_B| grows
exponentially to 1e15 at k = 60) and doubtful beyond gamma ~ 105. Only k <= 34 is used. The fix is
KSER ~ 0.75 gamma + 22, or a smaller T0. The validated k <= 20 values are unaffected.

**Interpretation for the modular torus.**
- The long-run mean square of E_P/sqrt R should be 2 sum |c|^2, about 0.6 (the tail beyond gamma = 103 is small).
- The larger finite-R mean square (1.365 on [3e4, 3e5]) is the lattice (Diophantine) component found earlier, entering
  through the first Moebius terms with rms about 225-300. Its normalised size decays like R^{-1/2}.
- This answers the question the section "Is the sharp error the zero sum?" left open. The zero sum is complete with
  finite variance. At accessible R the share explained by any truncation is held down by a non-stationary lattice
  piece that dies out slowly.
- Conditional on RH, simple zeros, Gonek-Hejhal, and the plateau of E_A.

**Cone tori.** For small cone area A the corners of the stable norm are tiny. Z_B then follows the flat sqrt(gamma)
growth up to some gamma*(A) and the hyperbolic bounded behaviour beyond it, so the flat-to-hyperbolic transition in the
variance happens at the scale where the corners are resolved.

## Literature check, round 2 (2026-11-26)

**Risager, "Counting Markov triples and simple geodesics", arXiv 2610.36069 (26 Oct 2026).**
- Proves M(x) = C(log 3x)^2 + O(log x (log log log x)^{1/10}/(log log x)^{3/10}), and O(log x/(log log x)^{1/2}) under
  the quasi-Riemann hypothesis. This is the first o(log x) error.
- Method: the McShane-Rivin ball, Doan-Li-Nguyen normal-turn estimates, Moebius inversion, zero-free regions.
- Quotes the McShane-Rivin conjecture [MR, Conj. 4.3]: the error is O((log x)^{1/2+eps}), i.e. O(R^{1/2+eps}) in
  length, R ~ 2 log 3x.
- Counting identity: S_X(L_T) = 6 M(T) + 4, so E_M/sqrt(log x) is about (sqrt 2/6) E_P/sqrt L = 0.236 E_P/sqrt L.
- Numerics at x = 10^k, k <= 30000 (L up to 1.4e5, nearly uniform in L): the normalised error lies in
  [-1.113, 1.150], i.e. E_P/sqrt L in [-4.7, 4.9]. That fits our rms of about 1.17 at R ~ 1e5, since 30000 samples of a
  sigma ~ 1.2 distribution reach about 4 sigma.
- Not in that paper: no lower bound or Omega result, no meromorphic continuation of the stable-norm zeta, no explicit
  formula with Riemann-zero amplitudes, no blind surfaces.
- So our unconditional Omega_+-(sqrt R) (lim sup >= 1.62, lim inf <= -1.70, i.e. >= 0.38 and <= -0.40 in Risager's
  normalisation) is the matching lower bound to the McShane-Rivin conjecture, and appears to be new.
- The paper also notes announced quasi-RH results (zero-free regions with delta = 1/12, 1/8).

**Doan-Li-Nguyen, "Stable-norm boundary geometry on once-punctured tori", arXiv 2605.14574 v3 (Oct 2026).**
- Rational corners with exponentially small exterior angles: our deficiencies delta ~ 8 e^{-(N_u+N_w)}, Sandwich lemma.
- Explicit irrational flatness orders.
- The dual-area identity Area(B*) = 4 sum l log coth(l/2), already noted and verified in our earlier check.
- New and useful: at most C_X (log L)^2 integer points on each dilated boundary, so at most C (log L)^2 simple geodesics
  of any exact length L. This is the multiplicity bound a truncated Perron formula needs.

**Nowak, "Primitive lattice points inside an ellipse", arXiv math/0307279 (2003).**
- The flat analogue of our Omega result: (1/Y) int_1^Y |R(x)| dx >> Y^{1/4} (x = R^2, so sqrt R).
- Proved through the zeta(2s) denominator plus a zero-density bound for Epstein zeta functions, to exclude the
  possibility that zeta_Q(rho/2) = 0 for all rho, i.e. that every flat torus is blind.
- Explicit blind flat tori and their count do not appear.
- Nowak writes that analogues of the mean-square asymptotic are hopeless at present. Our heuristic law (a log-divergent
  normalised variance for primitive points, against a finite one for all points) is therefore a new conjecture, not a
  known result.
- Upper bounds under RH: Huxley-Nowak O(x^{5/12+eps}), Mueller O(x^{9/22}), Zhai O(x^{221/608+eps}) (rational
  ellipse) and O(x^{0.3968}) (general).

**Not found.**
- Zeros of the non-holomorphic Eisenstein series E(z, s) in the variable z for fixed complex s (searched; only nodal
  lines of real parts, Siegel zeros in s, and holomorphic E_k turned up).
- A Dirichlet series over simple-geodesic lengths with meromorphic continuation, or a Poincare series over simple curves
  on moduli space linked to Eisenstein series. McShane's "Length series on Teichmueller space" (math/0403041) treats
  constant length series, not Dirichlet series.

**Reconciliation with the earlier variance-growth conjecture.** That conjecture rested on a gamma^0.57 fit to 13
coefficients later retracted as corrupted. With validated values, hyperbolic |Z_B(rho)| is bounded and sum |c|^2
converges, so the log-growth conjecture holds for flat tori (Epstein), not hyperbolic ones. The argument that the
Lindelof-type hypothesis (L) is probably false relied on the flat functional equation, which the hyperbolic Z_B lacks.
**Hypothesis (L) is therefore reopened.** Heuristically, |Z_B(1/2 + it)| matches the size of the lattice error E_A at
R ~ t, so (L) is essentially the plateau of E_A, which Theorem 9 gives up to polylog factors for almost every torus.
With Theorem 10 (RH + (L) => O(R^{1/2+eps})), this is a route to the McShane-Rivin conjecture.

## Hypothesis (L) on the critical line: first test, inconclusive above t ~ 80 (`critical_line.py`, `critical_line_*.log`)

|Z_B(1/2 + it)| at 24 generic heights on the modular torus (mpmath, ray pi/4, Bernoulli series of length 0.75 t + 30),
with the flat hexagonal |Z_flat| at the same heights:

| t range | abs(Z_B) values | rms abs(Z_B) | abs(Z_flat)/sqrt(t) |
|---|---|---|---|
| 14.5-16.4 | 5.2, 4.8, 5.3, 7.5, 9.0 | 6.6 | 0.67-1.93 |
| 33-66 | 14.8, 20.6, 12.1, 6.7, 10.4, 7.2, 17.8, 4.7, 19.9, 7.2 | 13.3 | 0.56-4.21 |
| 75-78 | 7.3, 11.0 | 9.3 | 0.36, 3.60 |
| 90-110 (unreliable) | 31.3, 34.4, 15.5, 30.8, 19.1, 26.6, 31.1 | 27.8 | 1.1-7.1 |

**Validation.**
- Recomputing rho_30 with the longer series gives 16.874, against 16.873 before, so the Bernoulli-series length was not
  the limiting factor at gamma ~ 101, and the k <= 34 zero values stand.
- At t = 90.50, though, the pi/3 and pi/4 rays disagree: 34.42 against 31.34. The two rays agreed to 1e-6 at
  gamma ~ 77. So this evaluator is unreliable somewhere between t ~ 80 and 90, probably because the oscillatory
  quadrature has not converged.
- The t >= 90 rows are therefore not evidence either way.

**Status of (L).** For t <= 80, |Z_B| rises from about 6.6 to about 13 and then levels off (7-11 near t ~ 77). The flat
values follow the forced |t|^{1/2} law with large fluctuations. This is consistent with bounded or slowly growing
hyperbolic values but does not decide (L).

**Next.** A robust high-t evaluator would be the hyperbolic Chowla-Selberg expansion: Z_B as constant term plus twist
harmonics. It is fast, needs no 1/Gamma cancellation, and is exact once the deeper Farey deficiencies are included.
