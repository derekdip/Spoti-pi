# Numerical check of the alternating spectral ladder for the xi Hankel kernel

A draft was handed over claiming that the moving-tail Hankel operators
`(H_a f)(x) = int_0^inf Phi(2a+x+y) f(y) dy`, built from the kernel in
the Fourier representation of the completed Riemann xi function, develop
an alternating eigenvalue ladder whose successive scales differ by
`eps_a = h'(2a)/h(2a)^2 ~ e^{-4a}/pi`. This is a check of that draft, not
a contribution to it. Scripts: `poc/xi/ladder.py`, `poc/xi/checks.py`.

## Why it can be checked exactly

Writing `ell = log Phi` and `H = h(2a)`, the hazard-rescaled kernel is
`k(s) = Phi(2a + s/H) / Phi(2a)`. Keeping the dominant theta shell,

```
log k(s) = -(e^{eps s} - 1) / eps,     eps = 2 / H
```

exactly, not just to the order the draft writes out. So the rescaled
operator is a one-parameter Gumbel-type kernel, and in the monic Laguerre
basis for the weight `e^{-2u}` every matrix element is

```
A_mn = int_0^inf e^{-2s} G(s, eps) R_mn(s) ds,
R_mn(s) = int_0^s p_m(u) p_n(s-u) du,   int_0^inf e^{-2s} s^j ds = j!/2^{j+1}
```

with `G = exp(log k + s)` expanded in `eps`. Every coefficient is
rational, and `1/(||p_m|| ||p_n||) = 2 * 2^{m+n} / (m! n!)` is rational
too, so with a rational `eps` the normalised matrix and its LDL pivots
are computed in exact arithmetic with no floating point anywhere.

## What holds

**Every claim that can be checked, checks.** Signs alternate, branches
are simple and separated, and the constants converge to the draft's
conjecture `C_n = n!/2^{2n+1}` with an O(eps) relative error, which is
the rate the draft predicts.

Constants from exact rational arithmetic at `eps = 10^-4`, theta jets:

| n | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| computed | 0.499963 | 0.124959 | 0.062455 | 0.046815 | 0.046782 | 0.058428 | 0.087555 |
| `n!/2^{2n+1}` | 0.5 | 0.125 | 0.0625 | 0.046875 | 0.046875 | 0.058594 | 0.087891 |

The draft establishes `C_0`, `C_1`, `C_2` and predicts `C_3 = 3/64`. The
prediction holds, and so do `C_4`, `C_5`, `C_6`.

The supporting links hold too:

- higher theta shells are negligible at the moving boundary, `phi_2/phi_1`
  being 1e-30 at `a = 0.5` and 1e-223 at `a = 1`;
- `h(2a)` matches `2 pi e^{4a} - 9/2` to six digits by `a = 1`, and
  `eps_a / (e^{-4a}/pi)` runs 1.238, 1.027, 1.0036 at `a = 0.5, 1, 1.5`;
- the reduction of the true kernel to `exp(-(e^{eps s}-1)/eps)` holds to
  9e-4 at `a = 1` and 5e-6 at `a = 1.5`, uniformly over `s <= 20`;
- the LDL pivots the draft uses in place of eigenvalues agree with the
  true eigenvalues of the same matrix to a relative error that falls like
  `eps^2`, 6e-7 on the leading branch at `eps = 10^-3`.

## Two things the draft does not say

**The constants depend only on the quadratic jet.** Three kernels with
different higher jets give the same `C_n`: the theta family
(`s^r/r!`), the draft's own comparison family `T_alpha`
(`s^r/r`), and a pure quadratic perturbation `exp(-s - eps s^2/2)` with
no higher jets at all. The degree-selection rule explains it: the `(n,n)`
matrix element needs degree `2n`, and at order `eps^n` only the `n`-th
power of the quadratic term reaches that degree, so every higher jet
enters the `n`-th branch at relative order `eps`.

This matters for section 13. The draft treats the comparison family as
motivation and is careful to say the theorem does not transfer a result
from it. In fact the two families provably share the constants, so the
conjecture can be proved wherever it is easiest, and the easiest place is
the pure Gaussian perturbation of `e^{-u-v}`. That turns an all-order
Schur-complement identity for the theta kernel into a statement about one
elementary kernel, which is a much smaller target.

**The embedding in Corollary 2 is off by a factor of two.** With
`(J_a f)(x) = f(x - 2a)`, a change of variables gives

```
<H_0 J_a f, J_a f> = <H_{2a} f, f>,   not <H_a f, f>
```

because the kernel becomes `Phi(4a + xi + eta)`. Checked numerically as
well as algebraically. The corollary is unaffected, since one relabels
`a` or shifts by `a` instead, but equation (45) as written is wrong.

## What was not checked

Novelty. Whether the alternating ladder or the two-sided infinite
signature of `H_0` is already known is a literature question, and this
environment has no access to the literature. Nothing here bears on the
Riemann hypothesis, and the draft is careful to say so in section 14.

## Standing of the draft's own checklist

Section 15 lists four items to be written out in full. Items 1, 2 and 4
are now supported numerically at the level of the quantities they
concern. Item 3, the explicit Schur-complement induction fixing the sign
and the constant at each level, is the one that matters, and it is the
one the universality observation makes easier.
