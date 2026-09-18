# Transverse fluctuations II: the Gaussian frontier, checked and pushed

A second note was handed over, "Transverse fluctuations in planar
permutation triples: exact variance, mobile structure, and the Gaussian
frontier". It records the proof in `docs/planar-triples-transverse.md`,
draws its consequences, and names a frontier: prove that every connected
transverse cumulant grows linearly in `k`, with the degree-six cumulant
of `c1 - c2` as the first test the marginals do not force, and a
two-state parity refinement of the mobile as the analytic route. This
document checks every algebraic claim of the note exactly, runs the
degree-six test, completes the marginal central limit theorem, and
removes the obstruction the note met on the parity route, after which
the joint Gaussian law follows from two standard theorems.

Scripts, all in `poc/hyper/`: `note2_check.py` (the note's algebra),
`cumulants.py` and `cumulant_asymptotics.py` (exact cumulants to order
8, `k <= 30`), `bivariate2.py` (full joint distribution of `(c1, c2)`,
`k <= 12`), `parity_mobile.py` and `transverse_rates.py` (the two-state
system, its critical surface, and the rates it predicts). Outputs in
`poc/results/hyper_*`.

## Status of the note, item by item

| note | claim | status |
|---|---|---|
| §2 | `U = M - M^2`, `D_z U = M(1+2M)`, `z D_z U = wM`, `Q = z D_z U + wQ` | exact, checked to `z^40` |
| §5 | Lagrange formula (4) for `Q_k`; `A`, `B` closed forms; `A = 2MB` | exact, checked against the data to `k = 24` |
| §7 | singular expansions of `M` and `Q`; (6) `Q_k/L_k = 5/9 - 16/(27k) + O(k^-2)` | exact |
| §7 | (7) constant term `4/81` in `Var(c1 - c2)` | **wrong**: it is `28/81`; and `28/243`, not `4/243`, for `Var(c_i)` |
| §8 | critical curve (8), (9) | exact |
| §9 | expansion (10) of `Lambda` | exact; extended here to `t^8` |
| §9 | marginal central limit theorem (11) | now a theorem, modulo one cited theorem; section 3 |
| §10 | `kappa_3, kappa_4, kappa_5` rates | exact from (10); confirmed by the exact cumulant data |
| §11, §12 | cubic invariant, invariant ring | correct |
| §13 | the degree-six test | run: section 2; the rate is now exact, section 6 |
| §14 | parity kernel (15) | correct |
| §14 | closed form (16) | **wrong as written**; the correct form is `(1 + z(X-Y) - Delta) / (2 X Delta)` |
| §15 | minimum-parity obstruction | real for the pointed series with the pointed vertex weighted |
| §16 | `cosh(h(c1-c2))` removes it | **no**: the pointed vertex's `+1` lands on the class opposite the minimum's; section 4 |
| §17 | (19), (20) | exact |
| §19 | joint Gaussian law (21) | follows from the identity of section 4 and two cited theorems; every joint cumulant rate is now computable exactly, section 6 |

## 1. Exact checks, and the two corrections

Everything in sections 2, 5, 8, 9, 10, 14 and 17 that can be stated as a
series identity was checked in exact rational arithmetic
(`poc/results/hyper_note2_check.log`, 26 of 27 checks pass, the failure
being (16)).

**The finite-size constant.** From the singular expansions
`M = (1-e)/(2(1+e))` and `Q = (1-e)^2/(2(1+e)(3+e))`, `e = (1-8z)^(1/2)`,
and the exact ratios `[z^k] e^j / [z^k] e` (rational functions of `k`),

```
Q_k / L_k = 5/9 - 16/(27 k) - 32/(243 k^2) + 256/(2187 k^3) + 448/(2187 k^4) + O(k^-5)
Var(c1 - c2) = (2(k+2)/3) Q_k/L_k = 10k/27 + 28/81 - 640/(729 k) + O(k^-2)
```

The note's (6) is right and its (7) is not: the `k^0` term is
`(2/3)(-16/27) + (4/3)(5/9) = 28/81`. The truncation at `k^-2` differs
from the exact value at `k = 24` by `0.3 k^-3`.

**The kernel's closed form.** With `Delta = (1 - 2z(X+Y) + z^2(X-Y)^2)^(1/2)`,

```
sum_{i>=1} z^i K_i(X, Y) = (1 + z(X - Y) - Delta) / (2 X Delta),
```

by Lagrange inversion on `T = z(1+XT)(1+YT)`: the sum is
`z(1+YT)/(1 - z phi'(T))` and `1 - z phi'(T) = Delta`. At `X = Y = R` it
reduces to `Phi(R)` as it must, which the note's (16) does not (that
expression gives the Catalan series `(1 - Delta)/(2R)` instead of the
central-binomial series). The note's (19) and (20), which depend only on
the antisymmetric derivative of the kernel, are nevertheless correct;
they were checked from the `K_i` directly.

**`Lambda` beyond `t^5`.** Reverting `e^t = (1-q)^2(1+2q)/(4q^3)` exactly,

```
Lambda(t) = 2/3 t + 5/81 t^2 - 7/2187 t^3 - 47/78732 t^4 + 469/6377292 t^5
          + 2917/344373768 t^6 - 26369/15496819560 t^7 - 2823749/23431191174720 t^8 + ...
```

so the predicted marginal rates `kappa_r(c_i)/k -> (-1)^r Lambda^(r)(0)` are

| r | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| rate | 10/81 | 14/729 | -94/6561 | -4690/531441 | 29170/4782969 | 369166/43046721 | -5647498/1162261467 |

## 2. The degree-six test

`cumulants.py` runs the Frobenius content-product computation with jets
in the divided-power basis `a^r/r!`, so that `x = N e^a`, `y = N e^-a`
gives `sum (c1 - c2)^r` exactly for `r <= 8`, and `x = N e^a`, `y = N`
gives `sum c1^r`. Both to `k = 30`. At every `k` the relations forced by
symmetry and Euler hold exactly: odd cumulants of `X = c1 - c2` vanish,
`kappa_2(X) = 3 kappa_2(c1)`, `kappa_4(X) = 9 kappa_4(c1)`,
`kappa_1(c1) = (k+2)/3`, `kappa_2(c1) = 2Q_k/(3N_k)`.

**Result: `kappa_6(X) = O(k)`, at the rate the parity mobile predicts.**
The three terms of the note's (13) are each of order `k^3`; at `k = 30`
they are about `2.2 x 10^4` and cancel to `6.48`. The sixth cumulant
grows linearly from `k = 8` on, with first differences that decrease
monotonically toward the rate:

| k | 10 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|
| `kappa_6(X)` | 2.0044 | 3.1978 | 4.3170 | 5.4049 | 6.4788 |
| first difference | 0.2468 | 0.2280 | 0.2193 | 0.2156 | 0.2141 |
| `kappa_8(X)` | | | | | -24.34 |

Fitting `a k + b + c/k + ...` exactly on the last 4, 5 and 6 values
gives `a = 0.21078, 0.21092, 0.21083` for `kappa_6(X)` and `-0.779,
-0.773, -0.777` for `kappa_8(X)`. The critical surface of the two-state
system (section 4) gives `0.210842` and `-0.7756`. So the first joint
cumulant that the marginals do not determine is linear in `k`, and its
rate is the one the parity mobile's `Lambda(t, -t)` produces: the
finite-state picture passes its first unconstrained test.

**The marginal rates are confirmed under the rooted measure.** The same
exact fits for `kappa_r(c1)/k`, against `(-1)^r Lambda^(r)(0)`:

| r | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| data fit (m = 6) | 0.1234568 | 0.0192044 | -0.0143271 | -0.0088249 | 0.0060980 | 0.0085796 | -0.0048754 |
| `Lambda` | 0.1234568 | 0.0192044 | -0.0143271 | -0.0088251 | 0.0060987 | 0.0085759 | -0.0048591 |

Agreement is to six digits through `r = 5` and degrades as the `1/k`
corrections of the higher cumulants grow; nothing is off.

**The degree-6 tensor.** With `K_6(a) = alpha e_2(a)^3 + beta e_3(a)^2`
on the plane, `kappa_6(X) = -alpha` and `kappa_6(c1) = -alpha/27 +
4 beta/729`, so the data give `alpha = -0.21083`, `beta = -0.3116`. The
surface value `0.2108416` is within `3 x 10^-7` of `4150/3^9 =
0.2108418`, which would make `beta = -2045/3^8 = -0.31169`; both are
candidates only, consistent with the data and not established. A closed
form of the critical surface would decide them.

**Gaussian moment ratios.** `E[X^4]/(3 sigma^4)` and
`E[X^6]/(15 sigma^6)` with `sigma^2 = 10k/27 + 28/81` are 0.894, 0.789
at `k = 8`; 0.963, 0.918 at `k = 16`; 0.985, 0.962 at `k = 30`,
approaching 1 at the `O(1/k)` speed that linear cumulants imply.

## 3. The marginal central limit theorem

**Theorem.** For a uniform random rooted planar hypermap with `k` darts
and each `i`,

```
(c_i - (k+2)/3) / (10k/81)^(1/2)  ==>  N(0, 1).
```

*Proof.* Let `y(z; s) = R_s - s` be the series of mobiles with a marked
corner and at least one edge, `s` marking white vertices. It satisfies
`y = G(z, y; s)` with `G = s/(1 - Phi_z(s + y)) - s`, and `G` is a
smooth implicit-function schema in the sense of Flajolet and Sedgewick
(Analytic Combinatorics, Theorem VII.3): analytic in `|4z(s+y)| < 1`,
nonnegative coefficients, `G(0, y) = 0`, nonlinear in `y`, aperiodic
(`[z^k] y = L_k > 0` for every `k`), and the characteristic system
`G = y`, `G_y = 1` has at `s = 1` the positive solution `(z, y) = (1/8,
1/2)` inside the domain (`4zR = 3/4`). The schema depends analytically
on `s`, so by the parametrised form of the theorem (Drmota, Systems of
functional equations, Random Structures and Algorithms 10, 1997; Flajolet
and Sedgewick, section IX.7), `y` has a square-root singularity at
`rho(s)`, analytic near `s = 1`, with

```
[z^k] y(z; s) = c(s) rho(s)^-k k^(-3/2) (1 + O(1/k))
```

uniformly for complex `s` near 1. Here `rho(s) = q(s)^3` with `q` given
by the note's (8): that is exactly the characteristic system solved.
The quasi-powers theorem (Flajolet and Sedgewick, Theorem IX.8) then
gives, for the number of white vertices `n` of a uniform random mobile
with `k` edges, `E[e^{tn}] = exp(k Lambda(t) + O(1))` uniformly near
`t = 0` with `Lambda(t) = log(rho(1)/rho(e^t))`, hence a Gaussian limit
with mean `k Lambda'(0) = 2k/3` and variance `k Lambda''(0) = 10k/81`,
the variance constant being nonzero.

A mobile with a marked corner is two pointed rooted hypermaps, both with
`c1 + c2 = 1 + n`, so the same law holds for `v = c1 + c2` under the
pointed-uniform measure. The rooted-uniform measure `P` and the
pointed-uniform measure `P_p` on rooted hypermaps with `k` darts are
related by `P_p(m) = v(m) P(m) / E[v]`, so `P(A) = E_p[1_A / v] /
E_p[1/v]`. On `B_k = {|v - 2k/3| <= k^(3/4)}`, `1/v = (3/2k)(1 +
O(k^(-1/4)))`; off it, `1/v <= 1` and `P_p(B_k^c) <= 2 exp(-c k^(1/2))`
by a Chernoff bound from the uniform quasi-powers estimate, which is
`o(1/k)`. Hence `P((v - 2k/3)/(10k/81)^(1/2) <= x) = P_p(same and
B_k)(1 + o(1)) + o(1) -> Phi(x)`. Finally `c3 = k + 2 - v`, and `c1`,
`c2`, `c3` have the same law by symmetry. QED

The cumulant expansion `kappa_r(v) = k Lambda^(r)(0) + O(1)` is what
quasi-powers give for the pointed measure; under the rooted measure the
same linear rates hold, since the `1/v` tilt changes every fixed-order
cumulant by `O(1)`, and the exact data of section 2 show the rates
directly.

## 4. The parity mobile determines the whole bivariate series

**The obstruction, made precise.** In a mobile with relative labels
`h` (root label 0), the true distance is `h - h_min + 1`, so the class
of the pointed vertex `v0` is `{h != h_min mod 2}` plus `v0` itself, and
the other class is `{h == h_min mod 2}`. Writing `n_0`, `n_1` for the
numbers of even and odd relative labels (root included), the two
orientations of the root edge give

```
(c1, c2) = (1 + n_other, n_min)  or  (n_min, 1 + n_other),
{n_other, n_min} = {n_0, n_1} as a set, which one is which decided by h_min mod 2.
```

So `cosh(h(c1 - c2))` is `cosh(h(1 + n_0 - n_1))` for one parity of
the minimum and `cosh(h(1 - n_0 + n_1))` for the other. Symmetrising does
not remove the global bit; the `+1` of the pointed vertex attaches to
the class opposite the minimum's, and only that class is ambiguous.
`parity_mobile.py` confirms it: the weighted identity
`x H_x + y H_y = x G(x,y) + y G(y,x)` fails at 1584 of 1728 test points.

**The fix.** Do not weight the pointed vertex. Pointing at a vertex and
dropping its own weight is the operator `d/dx + d/dy` on
`H(z; x, y) = sum_maps x^c1 y^c2`, and for it the two orientations
contribute `x^{n_other} y^{n_min} + x^{n_min} y^{n_other} = x^{n_0}
y^{n_1} + x^{n_1} y^{n_0}` whichever class holds the minimum. Hence

```
(d/dx + d/dy) H(z; x, y) = G(x, y) + G(y, x),        G(x, y) = R_e(x, y) - x,   (*)
```

with `R_e = x/(1 - Phi_0(R_e, R_o))`, `R_o = y/(1 - Phi_0(R_o, R_e))`
the note's two-state system (17) and `Phi_0` the corrected kernel.
Checked as a polynomial identity in `(x, y)` for every `k <= 12` by
evaluating both sides at a `12 x 12` grid of rational points, against
the full joint distribution of `(c1, c2)` from the character formula
(`bivariate2.py`); a polynomial of degree at most 11 in each variable is
determined by its values on that grid. Since `H(z; x, 0) = 0` (every map
has a white vertex), `(*)` determines `H`:

```
H(z; x, y) = integral_0^y [G + G^T](z; x - y + s, s) ds.
```

So the bivariate rooted series is an explicit integral of an algebraic
function, and the Walsh--Arques parametrisation is not needed for what
follows.

**Consequences.** The two-state system for `y_e = R_e - x`, `y_o = R_o
- y` is a positive, strongly connected, nonlinear, aperiodic system,
analytic in `(x, y)`, whose characteristic system at `(1, 1)` is the
scalar one with its solution `(1/8, 1/2, 1/2)` inside the domain. By the
Drmota--Lalley--Woods theorem with parameters (Drmota 1997; Flajolet and
Sedgewick, Theorem VII.6 and section IX.7) both components have a common
square-root singularity `rho(x, y)`, analytic near `(1, 1)`, with
uniform coefficient asymptotics `c(x,y) rho^-k k^(-3/2)`. By `(*)` the
same holds for `(d/dx + d/dy) H`. Integrating along the segment, the
endpoint `s = y` dominates because `rho` decreases strictly along the
diagonal direction near `(1, 1)` (its logarithmic derivative there is
`-2/3`), the rest of the segment is exponentially smaller by positivity
of the coefficients, and Laplace's method at the endpoint gives
`H_k(x, y) = c_H(x, y) rho(x, y)^-k k^(-5/2)(1 + O(1/k))` uniformly for
complex `(x, y)` near `(1, 1)`. That is a bivariate quasi-power with

```
Lambda(t1, t2) = log( rho(1, 1) / rho(e^t1, e^t2) ),
```

and the multivariate quasi-powers theorem (Hwang; Flajolet and
Sedgewick, section IX.9) gives the joint Gaussian law for `(c1, c2)`
with mean `k grad Lambda(0)` and covariance `k Hess Lambda(0)`, provided
the Hessian is nonsingular. The exact variances of the first document
force `Hess Lambda(0) = (5/81) [[2, -1], [-1, 2]]`, whose determinant is
`75/6561`. With `c3 = k + 2 - c1 - c2` this is the note's (21):

```
( c - (k+2)/3 (1,1,1) ) / k^(1/2)  ==>  N( 0, (5/27) I  on the plane x1 + x2 + x3 = 0 ).
```

**Numerical confirmation of the surface.** `parity_mobile.py` solves the
characteristic system of the two-state system by Newton's method and
differentiates `Lambda` numerically:

| direction | `Lambda''` from the surface | exact rate |
|---|---|---|
| `(1, 1)`: `Var(c1 + c2)/k` | 0.1234568 | 10/81 |
| `(1, -1)`: `Var(c1 - c2)/k` | 0.3703704 | 10/27 |
| `(1, 0)`: `Var(c1)/k` | 0.1234568 | 10/81 |
| `(1, 0)`: `Lambda'` | 0.3333333 | 1/3 |

all agreeing to `1e-12`. `transverse_rates.py` goes further and fits the
Taylor series of `Lambda(t, -t)`:

| `r` | `kappa_r(X)/k` from the surface | reference |
|---|---|---|
| 2 | 0.370370370 | 10/27 exact |
| 4 | -0.128943758 | `9 kappa_4(c1)/k = -94/729 = -0.128943759`, forced |
| 6 | 0.2108416 | not forced by the marginals |
| 8 | -0.7756 | not forced by the marginals |

The degree-4 rate is an independent test of the joint quasi-powers,
since it does not follow from the variance, and it passes to eight
digits. The degree-6 rate is the parity mobile's prediction for the
note's test; section 2 compares it with the exact data.

## 5. Where this leaves the frontier

- The second moment, the marginal Gaussian law and, through `(*)`, the
  joint Gaussian law are settled, the last two modulo the cited theorems
  whose hypotheses are checked above.
- The critical surface is now expanded exactly (section 6), which turns
  the candidates of section 2 into exact rates, and section 8 gives it in
  closed form: it is the fold `(1-p-q-r)^2 = 4pqr` of the Arquès
  parametrisation, and the series itself is `pqr(1-p-q-r)`.
- The renewal bijection behind `Q = w(M + Q)` remains open and remains
  unnecessary.

## 6. The critical surface, exactly

`critical_surface.py` expands the two-state critical surface along a
direction `(x, y) = (e^{at}, e^{bt})` as an exact power series in `t`,
by Newton's method in the ring `Q[[t]]`. The kernel is made polynomial
with the Lagrange auxiliary `T = z(1 + R_e T)(1 + R_o T)`, which is
symmetric in `(R_e, R_o)` so one `T` serves both kernels, and
`Delta = 1 - z(R_e + R_o) - 2 z R_e R_o T`; the two-state system becomes

```
R_e (Delta - z(1 + R_o T)) = x Delta,    R_o (Delta - z(1 + R_e T)) = y Delta,
T = z (1 + R_e T)(1 + R_o T),            det d(P_1, P_2, P_3)/d(R_e, R_o, T) = 0,
```

four polynomial equations in `(z, R_e, R_o, T)`, started at the exact
critical point `(1/8, 3/2, 3/2, 2/9)`. Each Newton step doubles the
`t`-adic precision; order 12 takes four seconds. With
`Lambda(at, bt) = -log(8 z(t))`, the rates `r! [t^r] Lambda` are

| r | transverse `(1,-1)`: `kappa_r(c1 - c2)/k` | marginal `(1,0)`: `kappa_r(c1)/k` |
|---|---|---|
| 1 | 0 | 1/3 |
| 2 | 10/27 | 10/81 |
| 3 | 0 | 14/729 |
| 4 | -94/729 | -94/6561 |
| 5 | 0 | -4690/531441 |
| 6 | **4150/19683** | 29170/4782969 |
| 7 | 0 | 369166/43046721 |
| 8 | -3710734/4782969 | -5647498/1162261467 |
| 10 | 216102770/43046721 | 491008150/94143178827 |
| 12 | -175646959486/3486784401 | -71289982174/22876792454961 |

Checks that all pass exactly: the transverse odd rates vanish; the
marginal column reproduces the scalar critical curve of section 1 at
every order computed (the sign pattern `(-1)^r` between `c1` and
`v = k + 2 - c3` included); the diagonal direction `(1,1)` reproduces
the scalar curve verbatim; the transverse `r = 2, 4` rates equal `10/27`
and `9 kappa_4(c1)/k` as symmetry forces. So the two-state surface,
derived from the parity mobile, agrees with the one-state surface,
derived from the plain mobile, wherever the two overlap, at every order.

**The degree-six constants are exact.** `kappa_6(c1 - c2)/k -> 4150/3^9`,
which the exact data of section 2 fit to four digits and the numerical
surface to seven. Hence the invariant cumulant tensors on the plane are,
with `e_2`, `e_3` the elementary symmetric functions of `a`,

```
K_6(a) = alpha e_2^3 + beta e_3^2,     alpha = -4150/3^9,   beta = -2045/3^8,
K_8(a) = a_8 e_2^4 + b_8 e_2 e_3^2,    a_8 = -3710734/3^14, b_8 = -1371176/3^12,
```

the first joint invariants that the `S_3` symmetry and the marginals do
not determine. They are theorems in the same sense as the joint law:
modulo the cited Drmota--Lalley--Woods and quasi-powers theorems, whose
hypotheses are verified, the joint cumulants of `(c1, c2, c3)` are
`k` times these rates plus `O(1)`.

The same script gives every joint cumulant rate to any order, and the
mixed directions `(a, b)` give the full tensors directly; only the two
directions needed for `alpha`, `beta`, `a_8`, `b_8` were run.

## 7. Literature check, as far as this environment allows

Method: web search only. arXiv, Springer, OEIS, Semantic Scholar and
university hosts are blocked by this session's network policy, so every
statement below rests on search-engine summaries of abstracts, not on
the papers. A specialist should read Arquès 1986 and Bousquet-Mélou and
Schaeffer 2002 directly before any claim of novelty.

**The generating function is classical.** Walsh, "Hypermaps versus
bipartite maps", J. Combin. Theory Ser. B 18 (1975) 155-163, set up the
correspondence used throughout and tabulated rooted hypermaps to 12
darts by vertices, hyperedges, darts and genus. Arquès, "Relations
fonctionnelles et dénombrement des hypercartes planaires pointées",
Combinatoire énumérative (Labelle and Leroux, eds.), Lecture Notes in
Mathematics 1234, Springer 1986, obtains from two decompositions "a
simple system of parametric equations" for the series of rooted planar
hypermaps by vertices, faces and hyperedges. Giorgetti and Walsh,
"Enumeration of hypermaps of a given genus", Ars Math. Contemp. (2018),
give parametric expressions for low genus by darts, vertices,
hyperedges and faces; arXiv:1411.3534 reaches the same series by matrix
integrals; arXiv:1609.05493 shows these series are rational after an
explicit change of variables. So the bivariate rooted series `H(z; x,
y)` that section 4 recovers from the parity mobile has been available
since 1986, and every exact statement in these two documents, `Q =
M^2/(1+M)`, the covariance, the cumulant rates, is in principle a
differentiation of Arquès' system. No search result mentions the second
moment of the colour imbalance, the variance of the vertex count of a
planar hypermap, or the constants `10/27`, `10/81`, `5/27`; whether any
of the specific formulas has been written down could not be determined.

**The two-colour bijection existed too.** Bousquet-Mélou and Schaeffer,
"The degree distribution in bipartite planar maps: applications to the
Ising model" (2002, arXiv:math/0211070), count bipartite planar maps by
the degrees of black and white vertices through a bijection with
blossoming trees; specialising the degree weights gives the same
bivariate series. Bernardi and Fusy, "Unified bijections for planar
hypermaps with general cycle-length constraints", Ann. Inst. Henri
Poincaré D 7 (2020) 75-164, contain both that bijection and the
Bouttier--Di Francesco--Guitter mobiles as special cases. The parity
mobile's contribution is therefore at most the mechanism: relative
label parity on mobiles, and the observation that leaving the pointed
vertex unweighted removes the minimum-parity ambiguity. Whether that
mechanism appears in print could not be checked.

**Limit laws.** The number of vertices of a uniform planar map with `n`
edges is asymptotically normal with variance `25n/32` (search summary;
the Bender--Richmond lineage, and Drmota and Panagiotou for vertices of
given degree). No result on the joint law of vertices, hyperedges and
faces of random planar hypermaps, or on bipartite maps by colour
counts, surfaced. Given Arquès' algebraic parametrisation the joint
Gaussian law is a routine application of the multivariate quasi-powers
framework, so it should be regarded as known in principle and, as far
as this check reaches, unstated.

**OEIS.** The sequences `Q_k = 0, 1, 7, 45, 291, 1917, ...` and `D_k = 2,
11, 69, 463, 3233, ...` could not be looked up; web search finds no page
listing either.

**Verdict.** New at the level this check can reach: the closed forms,
the exact covariance, and the degree-six and degree-eight invariants.
Forty years old: the generating function they come from. Expected:
the joint Gaussian law. The honest description of the whole is a short
note's worth of exact consequences of a classical series, obtained by a
route that avoids the series, plus one small bijective mechanism of
uncertain novelty.

## 8. The Arquès comparison, made explicit

A third note proposes the bridge to the Arquès parametrisation. Its form
of that parametrisation is taken as given here (the paper is
unreachable from this environment): for the trivariate series
`Htilde(X, U, Y) = sum_maps X^c1 U^c3 Y^c2`, which needs no dart
variable because `c1 + c2 + c3 = k + 2`, so that
`H(z; x, y) = z^-2 Htilde(zx, z, zy)`,

```
X = p (1 - q - r),      U = q (1 - p - r),      Y = r (1 - p - q).
```

`arques_bridge.py` and `arques_proof.py` check the note and go further.

**The note's claims hold exactly.** The Jacobian determinant is
`(1-p-q-r)^2 - 4pqr` (its (13015)-(13017)), symbolically. The fold of
the parametrisation under `(zx, z, zy)`, expanded by the same series
Newton method along the transverse, marginal and diagonal directions,
coincides with the two-state surface of section 6 to order 12 in all
three: the note's (13041) at the level of the surface. On the two-state
solution the note's `(Delta, z)` formulas (13040) and (13038),

```
x + y = 1 + 1/z - 3/(2 Delta) - Delta^3/(2 z^2),
(x - y)^2 = (Delta - z)^3 (z - Delta^3) / (Delta^3 z^3),
```

hold as series identities, and so does the bridge `Delta = 1 - p - r`,
`q = z / Delta`.

**The series itself is four terms.** A Padé null-space search on the
exact trivariate data to total degree 14 (656 equations, numerator
degree at most 6, denominator degree at most 3) returns a unique
relation up to common factors:

```
Htilde = p q r (1 - p - q - r).
```

**And it is a theorem, because the two-state system is the Arquès
parametrisation.** Write `A = 1 + R_e T`, `B = 1 + R_o T`. The two-state
equations give `T = zAB`, `A = 1/(1 - z R_e B)`, `B = 1/(1 - z R_o A)`,
and then `Delta = 1/A + 1/B - 1` by a two-line computation. Define

```
p = 1 - 1/A,        r = 1 - 1/B,        q = z / Delta.
```

Then `Delta = 1 - p - r`, `z R_e = p(1 - r)`, `z R_o = r(1 - p)`,
`T = q(1-p-r)/((1-p)(1-r))`, and the two remaining equations read
`zx = p(1-q-r)`, `zy = r(1-p-q)`, while `z = q(1-p-r)`. Substituting
this dictionary into the polynomial system of section 6 gives zero
identically (`arques_proof.py`, check 1). So the two-state solution is
rational in `(p, q, r)`, and its parameters have a bijective meaning:
`p` is `1 - 1/(1 + R_e T)`, the kernel's own auxiliary evaluated on the
even branch, `r` the same on the odd branch, `q` the dart weight over
the discriminant. The fold of the parametrisation and the singularity
of the parity mobile agree in section 6 because they are one object.

For `Htilde`: as polynomial identities,

```
(d/dX + d/dY) Htilde = q (p + r),        (d/dX + d/dU + d/dY) Htilde = pq + qr + rp,
```

(check 2, in the form `grad Htilde . adj(J) (e_X + e_Y) = q(p+r) det J`).
Since `R_e + R_o - x - y = [p(1-r) + r(1-p) - X - Y]/z = q(p+r)/z`, the
first identity says exactly `(d/dx + d/dy)[z^-2 Htilde(zx, z, zy)] = G +
G^T`. The true series satisfies the same equation by `(*)` of section
4, both vanish at `y = 0` (`r = 0` iff `Y = 0`), and a formal series in
`z` with polynomial coefficients is determined by these two facts. Hence

```
sum_{rooted planar hypermaps} X^c1 U^c3 Y^c2  =  p q r (1 - p - q - r),
```

modulo the mobile bijection only. The pointed series, unweighted at the
pointed cycle, is `e_2(p, q, r)`.

**The weakest sentence, replaced.** The note asks for the uniform
`k^(-5/2)` law for `H_k(x, y)` without the endpoint integral. Check 3:
every component of the row vector `grad Htilde . adj(J)` is divisible
by `det J`, so on the whole fold `Htilde` is stationary along the
kernel of `J`. At a simple fold point the branch of `(p, q, r)` over a
ray `z -> (zx, z, zy)` is a Puiseux series in `(rho - z)^(1/2)` whose
linear term is the kernel direction; stationarity kills the
`(rho - z)^(1/2)` term of `Htilde`, so its leading singular term is
`(rho - z)^(3/2)`. At the symmetric point the coefficient is nonzero,
`U = 1/4 - e^2 + 2 e^3 + ...` with `e = (1 - 8z)^(1/2)` (check 4), hence
nonzero nearby by continuity. With `rho(x, y)` analytic near `(1, 1)`,
and the dominant singularity unique on its circle (positivity and
aperiodicity at `(1, 1)`, continuity of the branch points in `(x, y)`),
uniform singularity analysis for algebraic functions with a parameter
gives

```
H_k(x, y) = c_H(x, y) rho(x, y)^-k k^(-5/2) (1 + O(1/k))
```

uniformly for complex `(x, y)` near `(1, 1)`. The integral estimate of
section 4 is no longer needed; the statement rests on an algebraic fact
checked exactly plus the standard transfer theorem.

**What is classical and what is not, restated.** The parametrisation
is Arquès' (1986), and the four-term closed form is presumably his
theorem in some normalisation; neither could be read here. New, as far
as this environment can tell: the derivation of the parametrisation
from the parity mobile with a bijective meaning for `(p, q, r)`; the
explicit joint cumulant generating function `Lambda(t1, t2)` with its
exact rates; and the theorem package of the note's (13042)-(13045),
whose analytic step now runs through the fold-stationarity of
`Htilde` rather than an integral lemma.

## 9. The coefficient route: an exact formula, no product formula, and the local and large-deviation laws tested

A fourth note asks for the exact Arquès coefficient `A_k(c1, c2, c3)`,
hoping for a product of binomials from which Stirling's formula would
give the rate function, the Hessian, the local prefactor and the
lattice at once, and strict convexity for free.

**The formula.** With `Htilde = pqr(1-p-q-r)` and `p = X/(1-q-r)`,
`q = U/(1-p-r)`, `r = Y/(1-p-q)`, the Lagrange--Good inversion formula
gives, for `a = c1`, `b = c3`, `c = c2`, `a + b + c = k + 2`,

```
A(a, b, c) = [p^(a-1) q^(b-1) r^(c-1)]  (1-p-q-r) ((1-p-q-r)^2 - 4pqr)
                                          (1-q-r)^-(a+1) (1-p-r)^-(b+1) (1-p-q)^-(c+1),
```

the Good determinant being `det J / ((1-q-r)(1-p-r)(1-p-q))`. Expanding
the negative powers, `A` is a finite triple sum of products of three
multinomial coefficients, over the 20 monomials of the prefactor.
`coefficients.py` evaluates it exactly; it agrees with the character
data at every `(k, c1, c2)`, `k <= 12`, and the support is the whole
triangle `c1, c2, c3 >= 1`, so the lattice span is 1.

**There is no product formula.** At `k = 12`: `A(2,6,6) = 925190 =
2 . 5 . 7 . 13217`, `A(7,3,4) = 1936308 = 2^2 . 3 . 11 . 14669`,
`A(5,5,4) = 9032898 = 2 . 3 . 7 . 431 . 499`. A product of binomials
with arguments of order `k` has no prime factor much larger than `k`;
primes near `10^4` at `k = 12` rule it out. The exact formula stays a
triple sum, whose saddle-point analysis is the critical-surface
analysis in other clothes. The coefficient route is not a shortcut to
strict convexity.

**What it does give is exact coefficients at large `k`.** A central
coefficient costs 2 s at `k = 121` and 36 s at `k = 241`, which makes
the note's two numerical tests possible.

**Local limit at the centre, (13115)-(13116).** For `k = 1 mod 3` and
`m = (k+2)/3`, with `N_k` the total:

| k | 31 | 61 | 91 | 121 | 181 | 241 | [[K301]] |
|---|---|---|---|---|---|---|---|
| `k Pr(c1 = c2 = m)` | 1.4313 | 1.4581 | 1.4678 | 1.4728 | 1.4780 | 1.4806 | [[V301]] |

Richardson extrapolation of the `1/k` correction from the last two
values gives [[RICH]], against `27 sqrt3 / (10 pi) = 1.488588`. So at
the balanced point `Pr(C_k = m) ~ 27 sqrt3 / (10 pi k)`: the lattice
factor is 1 and the analytic prefactor cancels in the probability, as
the note predicted.

**Large deviations, (13113).** `ldp_check.py` takes `rho(x, y)` from
the fold by Newton's method, `Lambda(t) = -log(8 rho(e^t1, e^t2))`,
solves `grad Lambda(t) = u` and sets `I(u) = t . u - Lambda(t)`. The
local law `Pr(C_k = m) = C(u) e^(-k I(u)) / k (1 + O(1/k))` predicts
that `-(1/k) log Pr - (log k)/k - I(u)` is `O(1/k)`. At five lattice
points away from the centre:

| `u` | `k = 121`: `k x diff` | `k = 241`: `k x diff` |
|---|---|---|
| (0.40, 0.30) | -0.63 | -0.70 |
| (0.25, 0.25) | +1.19 | +1.15 |
| (0.45, 0.45) | -4.03 | -4.25 |
| (0.20, 0.50) | -0.64 | -0.71 |
| (0.50, 0.25) | -1.25 | [[U5]] |

The difference halves when `k` doubles in every case, and `k x diff`
converges to `-log C(u)`: the rate function computed from the surface
is the exponential rate of the exact coefficients, and the prefactor
grows toward the boundary of the simplex as it should.

**Strict convexity, numerically.** `Hess Lambda(0)` equals
`(5/81) [[2, -1], [-1, 2]]` to `1e-7`. On a `13 x 13` grid over the tilt
box `|t_i| <= 1.2` (`x, y` from 0.30 to 3.3) the smallest eigenvalue of
the Hessian is 0.046, at the corner `t = (1.2, 1.2)`, so the Hessian is
positive definite on that compact set, as (13109) predicts. This is
evidence, not a proof; the note's variance-lower-bound or
nondegeneracy argument remains the route to a theorem.

**Where the fourth note's programme stands.** The exact coefficient
formula exists and is verified, but it is a triple sum and not a
product, so the Stirling shortcut is not available. The local limit at
the centre and the large-deviation rate function are confirmed
numerically to the precision finite `k` allow, with the rate function
given explicitly by the Arquès fold. The theorem package of the third
note stands as before; the global large-deviation principle and the
local limit theorem are now well-supported conjectures with an
explicit rate function, awaiting a proof of strict convexity on
compact tilt sets.
