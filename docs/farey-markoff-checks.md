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
