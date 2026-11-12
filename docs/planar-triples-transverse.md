# Transverse fluctuations in planar permutation triples: Q = M^2/(1+M) is a theorem

A note was handed over, "A tagged first-return program for transverse
fluctuations in planar permutation triples", whose central conjecture is

```
Q = w (M + Q),      equivalently      Q = M^2 / (1 + M),      V = 2 M^2 / (1 + M)
```

for the second moment of the colour imbalance `c1 - c2` over genus-zero
transitive permutation triples. The note reduces the conjecture to a
local orientation/colour involution identity, its (18), and leaves that
open. This document proves the conjecture by a different route, one that
needs no signed decomposition at all, and verifies every step exactly.
Scripts: `poc/hyper/moments.py`, `poc/hyper/bivariate.py`,
`poc/hyper/proof_check.py`, `poc/hyper/mobile_sampler.py`. Outputs:
`poc/results/hyper_*`.

## Objects and notation (the note's)

`T_k` is the set of triples `(s1, s2, s3)` in `S_k^3` with `s1 s2 s3 = 1`,
`<s1, s2>` transitive, and `c1 + c2 + c3 = k + 2`, where `c_i` is the
number of cycles of `s_i`. Every sum below is divided by `(k-1)!`, which
turns it into a sum over rooted planar hypermaps with `k` darts: a
transitive triple with a marked point has trivial stabiliser under
simultaneous conjugation, so `|T_k| / (k-1)!` is the number of such
hypermaps, and any function of the `c_i` is constant on conjugacy
classes. Write

```
N_k = |T_k| / (k-1)!                        rooted planar hypermaps with k darts
L_k = sum c1 / (k-1)!                       M(z) = sum_k L_k z^k
V_k = sum (c1 - c2)^2 / (k-1)!              Q = V / 2
D_k = sum (c1 + c2)^2 / (2 (k-1)!)          the vertex second moment (new here)
w   = z (1 + 2M)
```

**Theorem.** `M = z (1 + 2M)^2`, so `L_k = 2^(k-1) Cat_k`, and
`Q = M^2 / (1 + M)`. Equivalently `Q = w (M + Q)`, and the note's
recurrence (20) holds for every `k`.

## Why no signed decomposition is needed

Up to the symmetry of the triple there are only two second moments,
`sum c1^2` and `sum c1 c2`. Euler's relation fixes
`sum (c1 + c2 + c3)^2`. So one more scalar second moment determines all
of them, the signed one included. The natural scalar is the second
moment of the total number of vertices of the bipartite map, `c1 + c2`,
and that is exactly what a vertex-pointed bijection computes, because a
mobile carries one labelled vertex per map vertex. The colour difference
never has to be tracked, and no sign ever appears.

## Proof

**Step 1, symmetry.** The maps `(s1, s2, s3) -> (s2, s3, s1)` and
`(s1, s2, s3) -> (s2^-1, s1^-1, s3^-1)` preserve the product condition
(`s2^-1 s1^-1 s3^-1 = (s3 s1 s2)^-1 = 1`), transitivity, and the multiset
of cycle counts up to permutation. They generate `S_3` acting on `T_k`,
so every moment sum is symmetric in `(c1, c2, c3)`. Write
`s2 = sum c1^2 / (k-1)!` and `s11 = sum c1 c2 / (k-1)!`; by symmetry
these are the moments of any index and any index pair.

**Step 2, Euler.** `sum (c1 + c2 + c3) / (k-1)! = (k+2) N_k` and
`sum (c1 + c2 + c3)^2 / (k-1)! = (k+2)^2 N_k`. By symmetry

```
3 L_k = (k+2) N_k,              3 s2 + 6 s11 = (k+2)^2 N_k.
```

Also `Q_k = s2 - s11` and `D_k = s2 + s11`, so
`s11 = (k+2)^2 N_k / 3 - D_k` and

```
Q_k = 3 D_k - (2/3) (k+2)^2 N_k = 3 D_k - 2 (k+2) L_k.               (A)
```

In series, `(k+2) L_k` is the coefficient of `z M' + 2M`. Everything now
rests on `D`.

**Step 3, the vertex second moment by mobiles.** A hypermap with `k`
darts is a planar bipartite map with `k` edges: black vertices are the
cycles of `s1`, white vertices the cycles of `s2`, faces the cycles of
`s3`. A rooted hypermap is a bipartite map with a marked oriented edge,
the orientation fixing which colour class is `s1`. So `N_k` counts rooted
planar bipartite maps with `k` edges, and the sum over rooted hypermaps
pointed at a vertex of either colour, with weight `s` per vertex, is

```
P(z; s) = sum_maps (c1 + c2) s^(c1 + c2) z^k,      d/ds P at s = 1  =  2 sum_k D_k z^k.
```

*The one imported result.* Bouttier, Di Francesco and Guitter, "Planar
maps as labeled mobiles", Electron. J. Combin. 11 (2004) R69, bipartite
case: planar bipartite maps with `n` edges pointed at a vertex `v0` are
in bijection with mobiles with `n` edges. Label every vertex by its
distance from `v0`; put a black node in each face and join it to every
corner of that face whose clockwise-following edge leads to a vertex of
label one lower; delete the map's edges and `v0`. What remains is a
plane tree whose white vertices are the map's vertices other than `v0`,
carrying their labels, and whose black nodes of degree `i` are the faces
of degree `2i`; around a black node, clockwise-consecutive labels
satisfy `l' >= l - 1`, all labels are at least 1 and the minimum is 1.
Three consequences are used.

(a) *Edges correspond.* An edge of the map from a vertex of label `l` to
one of label `l - 1` is the clockwise-following edge of exactly one
corner of its upper endpoint, and that corner is attached; conversely an
attached corner determines its edge. So a pointed map with a marked edge
is a mobile with a marked edge, equivalently a mobile with a marked
white corner. The marked map edge has two orientations, so pointed
rooted bipartite maps with `n` edges are twice the mobiles with `n`
edges and a marked white corner.

(b) *Labels can be shifted.* Subtracting the root corner's label gives a
mobile with root label 0 and integer labels; the true labels are
recovered as `label - min + 1`. So mobiles with a marked white corner are
exactly plane trees with integer labels, root label 0, and the local
condition at black nodes, with no positivity constraint. This is the
shift that makes Chassaing and Schaeffer's labelled trees count pointed
quadrangulations.

(c) *The local structure at a black node is free.* Around a black node
of degree `i`, a face of degree `2i`, the labels of the `2i` corners form
a cyclic walk of `i` up-steps and `i` down-steps, and the attached
corners are those followed by a down-step. Rooting at the parent corner,
whose step is down, the other `i - 1` down-steps can sit at any `i - 1`
of the remaining `2i - 1` positions, and their positions determine the
children's labels. So a black node with a parent contributes
`z^i C(2i-1, i-1)` and has `i - 1` independent white children.

Hence, with `s` marking white vertices, the series `R_s` of mobiles with
a marked white corner (the root white vertex, then its sequence of black
children, each with its `i - 1` white children) satisfies

```
R_s = s / (1 - Phi(R_s)),        Phi(u) = sum_{i >= 1} C(2i-1, i) z^i u^(i-1),
```

and, counting `v0` with weight `s` and the two root orientations,

```
P(z; s) = 2 s (R_s - s).                                                 (B)
```

**Step 4, algebra.** Write `R = R_1` and `R'` for `d/ds R_s` at `s = 1`.
Since `sum_{i>=1} C(2i-1, i) x^i = ((1 - 4x)^(-1/2) - 1) / 2`, the
equation at `s = 1` reads `(2R - 1)^2 (1 - 4zR) = 1`, and with
`R = 1 + M` this is `M = z (1 + 2M)^2`. Lagrange inversion gives
`L_k = 2^(k-1) Cat_k`, the note's starting point. Differentiating
`R_s (1 - Phi(R_s)) = s` at `s = 1`,

```
R' = 1 / (1 - Phi(R) - R Phi'(R))
   = 1 / (1 - z (1 - 4zR)^(-3/2))
   = 1 / (1 - M (1 + 2M))
   = 1 / ((1 - 2M)(1 + M)),
```

using `(1 - 4zR)^(-1/2) = 2R - 1 = 1 + 2M` and `z = M / (1 + 2M)^2`. From
(B), `sum_k D_k z^k = (1/2) d/ds P |_{s=1} = M + R' - 1`. From
`M = z (1 + 2M)^2`, `z M' = M (1 + 2M) / (1 - 2M)`. Substituting into (A):

```
Q = 3 (M + R' - 1) - 2 (zM' + 2M)
  = -M + [ M (1 + 2M) / (1 - 2M) ] [ 3 / (1 + M) - 2 ]
  = -M + M (1 + 2M) / (1 + M)
  = M^2 / (1 + M).
```

With `w = z (1 + 2M) = M / (1 + 2M)` one has `1 - w = (1 + M) / (1 + 2M)`,
so `Q = w M / (1 - w) = w (M + Q)`. That is the note's (1), and its
(20)-(23) and (26) follow as the note shows. QED.

The only imported statement is the bijection. Everything else is
symmetry, Euler's relation and one differentiation.

## Exact verification

| what | how | reach |
|---|---|---|
| `N_k, L_k, s2, s11, Q_k, D_k` from the Frobenius content-product formula: order-2 jets in `(a, b)`, connected part by the logarithm, genus 0 as the top degree in `N` | `moments.py`, integers only | `k <= 24` (19 s) |
| the full distribution of `c1` from the same formula equals Tutte's slicings formula in its dual form (A census of slicings, 1962): an independent classical input | `bivariate.py` | `k <= 14`, every `(k, c1)` |
| `M = z(1+2M)^2`; `R_1 = 1 + M`; `R' = 1/((1-2M)(1+M))`; `D = M + R' - 1` against the data; `Q = 3D - 2(zM' + 2M)` equals `M^2/(1+M)` and the data; `Q = w(M+Q)`; recurrence (20); `E = 4w(M+E)` | `proof_check.py`, exact rationals | series to `z^96`, data to `k = 24` |

Both classical inputs were recalled without access to the literature,
and each is confirmed against the exact data where it is used: the
mobile equation through `D` at every `k <= 24`, Tutte's formula through
the full `c1` distribution at every `k <= 14`. If either had been
misremembered the data would have said so.

Extract of the data (`poc/results/hyper_moments.json` has `k <= 24`):

| k | N_k | L_k | Q_k | D_k |
|---|---|---|---|---|
| 1 | 1 | 1 | 0 | 2 |
| 2 | 3 | 4 | 1 | 11 |
| 3 | 12 | 20 | 7 | 69 |
| 4 | 56 | 112 | 45 | 463 |
| 5 | 288 | 672 | 291 | 3233 |
| 6 | 1584 | 4224 | 1917 | 23167 |
| 8 | 54912 | 183040 | 87805 | 1249535 |
| 12 | 91287552 | 426008576 | 215277565 | 4047839231 |
| 16 | 193100021760 | 1158600130560 | 600196448253 | 14103267049471 |

## What this settles in the note, and what it does not

- (1), (2), (20), (21)-(23) and (26) are theorems. (25), `E = 4w(M+E)`
  with `E = zM' - M = 4M^2/(1-2M)`, is an identity and is checked.
- (18), the local orientation/colour identity, is neither proved nor
  needed. The proof never opens a Jucys-Murphy factor, never peels a
  maximal label and carries no sign. Whether the note's tagged
  first-return process exists as a combinatorial object is untouched.
  What is now known is that its predicted loop equation is true, so (18)
  cannot be refuted by coefficients; it can only be settled by
  constructing the involution.
- The renewal reading of `1/(1-w)`. Here `1/(1-w) = (1+2M)/(1+M)` comes
  from the factor `1/(1+M)` in `R'` once Euler's relation cancels the
  pole `1/(1-2M)`. Nothing renewal-like was used. Whether the geometric
  series has a bijective meaning is open.
- The note's guessed multiplier-2 channel. The equation `X = 2w(M+X)`
  has the unique solution `X = 2M^2`, with coefficients
  `2^(k-1) (Cat_(k+1) - 2 Cat_k)`. Whether any natural statistic has that
  series was not examined.
- Section 5's finding that endpoint pointing retains cycle-length
  information is consistent with all of this: the proof needs only
  vertex counts, which is why it can afford to ignore cycle lengths.

## The result as statistics

For a uniform random rooted planar hypermap with `k` darts, equivalently
a uniform rooted planar bipartite map with `k` edges or a uniform
genus-zero transitive triple:

```
E[c1]            = (k+2)/3
Var(c1 - c2)     = 2 Q_k / N_k = (2 (k+2) / 3) Q_k / L_k
Var(c1)          = Var(c1 - c2) / 3 = 2 Q_k / (3 N_k)
Cov(c1, c2)      = -Var(c1) / 2
```

The last two use `Var(c1 + c2 + c3) = 0` and symmetry. Near `z = 1/8`
one has `M = 1/2 - a (1 - 8z)^(1/2) + ...` and `Q = M^2/(1+M)` has
derivative `5/9` at `M = 1/2`, so `Q_k / L_k -> 5/9` and

```
Var(c1 - c2) ~ (10/27) k,          Var(c1) ~ (10/81) k.
```

| k | Var(c1 - c2) | / (k+2) | Var(c1) | / (k+2) |
|---|---|---|---|---|
| 8 | 3.198 | 0.320 | 1.066 | 0.107 |
| 16 | 6.216 | 0.345 | 2.072 | 0.115 |
| 32 | 12.170 | 0.358 | 4.057 | 0.119 |
| 64 | 24.036 | 0.364 | 8.012 | 0.121 |
| 96 | 35.892 | 0.366 | 11.964 | 0.122 |

`10/27 = 0.3704`, `10/81 = 0.1235`. Each colour class holds a third of
`k + 2` vertices give or take `0.35 sqrt(k)`, and the imbalance between
two classes has standard deviation `0.61 sqrt(k)`.

## Computer-science uses

Scope first: this is enumerative combinatorics. Nothing in it bears on
the reactive-field runtime, which stays paused where RGRE-1b left it.

**A validated linear-time uniform generator.** The bijection in the
proof is also a sampler. `mobile_sampler.py` draws a uniform mobile with
`k` edges by the cycle lemma (i.i.d. out-degrees weighted
`C(2i-1, i) y^i` at the critical `y = 3/16`, conditioned on the total,
rotated once), attaches a uniform label pattern to each black node, and
reads the colour of every vertex off the parity of its distance to the
pointed vertex, which is the label minus the minimum plus one. No map
closure is needed for the statistics; the closure to the three
permutations is the BDG inverse construction, linear time, and is not
written here. Rooted expectations come from pointed samples by the
weight `1/v`. Four exact values act as oracles; two of them test the
sampler alone and two test the theorem.

| k | samples | statistic | tests | Monte Carlo | exact | z |
|---|---|---|---|---|---|---|
| 20 | 60000 | `E_pointed[1/v]` | sampler | 0.06814 +- 0.00003 | 0.06818 | -1.24 |
| 20 | 60000 | `E[c3]` | sampler | 7.325 +- 0.007 | 7.333 | -1.22 |
| 20 | 60000 | `E[c3^2]` | theorem | 56.239 +- 0.104 | 56.347 | -1.04 |
| 20 | 60000 | `E[(c1-c2)^2]` | theorem | 7.851 +- 0.049 | 7.709 | +2.92 |
| 50 | 60000 | `E_pointed[1/v]` | sampler | 0.02886 +- 0.00001 | 0.02885 | +1.65 |
| 50 | 60000 | `E[c3]` | sampler | 17.350 +- 0.010 | 17.333 | +1.65 |
| 50 | 60000 | `E[c3^2]` | theorem | 307.330 +- 0.377 | 306.727 | +1.60 |
| 50 | 60000 | `E[(c1-c2)^2]` | theorem | 18.723 +- 0.110 | 18.847 | -1.12 |
| 100 | 60000 | `E_pointed[1/v]` | sampler | 0.01470 +- 0.00000 | 0.01471 | -0.42 |
| 100 | 60000 | `E[c3]` | sampler | 33.994 +- 0.015 | 34.000 | -0.40 |
| 100 | 60000 | `E[c3^2]` | theorem | 1167.978 +- 1.003 | 1168.458 | -0.48 |
| 100 | 60000 | `E[(c1-c2)^2]` | theorem | 37.579 +- 0.216 | 37.374 | +0.95 |
| 200 | 30000 | `E_pointed[1/v]` | sampler | 0.00743 +- 0.00000 | 0.00743 | +1.63 |
| 200 | 30000 | `E[c3]` | sampler | 67.380 +- 0.029 | 67.333 | +1.62 |
| 200 | 30000 | `E[c3^2]` | theorem | 4564.481 +- 3.754 | 4558.583 | +1.57 |
| 200 | 30000 | `E[(c1-c2)^2]` | theorem | 74.446 +- 0.601 | 74.415 | +0.05 |

Seed `20260918 + k`, run in `poc/results/hyper_sampler.log`. Sixteen z-scores, one at
`+2.9` (`k = 20`, the imbalance). Two independent reruns of that size with
250 000 samples each (`hyper_sampler_k20_recheck.log`) give `-0.84` and
`+1.09`, so it was a fluctuation. Every other entry is within two standard
errors. Cost is linear: 30 000 maps with 200 edges in 26 s, most of it the
rejection step of the cycle lemma, which accepts about one sequence in 75
at that size.

**Exact oracles for any other sampler.** Markov chains on maps,
Boltzmann samplers and rejection schemes for planar bipartite maps,
hypermaps or 2-constellations can be checked against
`E[1/v] = 3/(2(k+2))` under pointing, `E[c3] = (k+2)/3`, and the two
second moments above, all in closed form for every `k`. Before this the
second moment of the imbalance was an unproved fit.

**Sizing on random planar bipartite structures.** In a random planar
bipartite map with `k` edges the two vertex classes are each
`(k+2)/3 +- 0.35 sqrt(k)` and differ by `0.61 sqrt(k)` in standard
deviation, with the exact finite-`k` values above. That is the number to
use when a data structure is provisioned per class.

**The pipeline as a tool.** The exact-jet character computation
(`moments.py`) gives every second moment of cycle counts for planar
factorisations in a second, and the proof pattern, symmetry plus Euler
plus one vertex-pointed bijection, is not specific to this statistic. It
applies as it stands to covariances of vertex and face counts in other
map classes that mobiles cover, and the character side extends to
constellations with more than three factors.

## Addendum

A second note built on this proof; its claims are checked and its frontier
is pushed in `docs/planar-triples-gaussian-frontier.md`.
