# Why a first-order pre-screen can work: the generalising part of a gradient direction

Written 2026-11-11 while ED4's pilot ran. ED2 and ED3 found, as an
empirical fact, that training data alone cannot rank the modules an
adapter might go on while a first-order held-out estimate can. This
note derives what is going on at first order, states one bound that
is proved and one prediction that is borrowed, and checks both on
GPT-2 (`poc/ecsdec/rmt_check.py`, `poc/results/ed4/rmt_check*.log`).
The papers behind the borrowed formula could not be fetched from
this sandbox, so the formula is verified numerically on synthetic
matrices below instead of cited on trust.

## 1. Setting

A module has weights `W` in `R^{a x b}`. On `n` training contexts the
gradient of the loss with respect to `W` is

    G = g + E,

`g` the population gradient and `E` the sampling noise of a mean over
`n` contexts (mean zero, shrinking like `1/sqrt(n)`). A rank-`r`
adapter trained from the base model moves, to first order, along the
rank-`r` truncation of `-G`,

    R = sum_{k<=r} s_k u_k v_k^T,    G = sum_k s_k u_k v_k^T.

Along the unit direction `-R/||R||` the training loss falls at rate

    S_tr = <G, R> / ||R|| = sqrt(sum_{k<=r} s_k^2),

and the population (held-out) loss at rate

    S_pop = <g, R> / ||R|| = S_tr - <E, R> / ||R||.          (1)

`<E, R>/||R||` is the first-order optimism: the part of the direction
that was chosen because the noise happened to point that way. It is
non-negative in expectation, because `R` is selected to align with
`G = g + E`.

## 2. Two elementary consequences

**A measured held-out slope is precise with little data.** With an
independent held-out gradient `G_ho = g + E_ho`, the measured slope
`<G_ho, R>/||R||` is `S_pop` plus the noise projected on one fixed
unit direction. `R` does not depend on the held-out data, so that
projection has mean zero and the variance of a single coordinate of
the noise, not of all `ab` of them. Selecting a direction is an
`ab`-dimensional search; checking one is a one-dimensional
measurement. This is why ED2 and ED3 needed held-out data and why so
little of it sufficed.

**A lower bound from training data alone.** For any matrix `E` and
any `R` of rank at most `r`, `<E, R> <= ||E||_(r) ||R||_F`, where
`||E||_(r)` is the root of the sum of the `r` largest squared
singular values of `E` (the pairing of the Ky Fan 2-`r` norm with
rank-`r` matrices: write `<E, R> = <P E Q, R>` with `P, Q` the
projectors on `R`'s column and row spaces, and `||P E Q||_F <=
||E||_(r)`). With (1):

    S_pop >= S_tr - ||E||_(r).                                 (2)

`E` is not observed, but its law is: if the training set is split
into halves `A` and `B`, then `(G_A - G_B)/2` has the same
distribution as the noise of the full-sample mean (the signal
cancels, the noise variance is `(1/4)(2 sigma^2/(n/2)) = sigma^2/n`).
The split-half difference is an empirical null for the gradient
noise, with whatever structure the real noise has.

## 3. The borrowed prediction: singular-value shrinkage

For a rank-one signal `theta u v^T` in noise with independent
entries of standard deviation `tau`, the classical results on spiked
rectangular matrices give a threshold `theta_c = tau (ab)^{1/4}`:
below it the top singular vectors of the noisy matrix carry no
information about `u, v`; above it the top singular value is
`s = sqrt((theta^2 + tau^2 a)(theta^2 + tau^2 b))/theta` and the
product `theta <u, u_hat><v, v_hat>`, which is exactly the
population slope of the empirical direction, equals the
Frobenius-optimal shrinkage of `s`:

    eta(s) = tau sqrt(B) sqrt((y^2 - c - 1)^2 - 4c) / y,   y = s/(tau sqrt(B)),

with `B = max(a, b)`, `c = min(a, b)/B`, and `eta = 0` for
`y <= 1 + sqrt(c)`, that is for `s` at or below the noise's largest
singular value `tau (sqrt(a) + sqrt(b))`. For rank `r` the predicted
population slope is

    S_pred = sum_{k<=r} s_k eta(s_k) / sqrt(sum_{k<=r} s_k^2).        (3)

Numerical verification on synthetic matrices (three draws each;
`poc/ecsdec/rmt_check.py: shrink`):

| a x b | theta/theta_c | s1 / noise edge | measured `<g, u_hat v_hat^T>` | predicted `eta(s1)` |
|---|---|---|---|---|
| 768 x 768 | 0.5 | 0.99 | 0.02 | 0.00 |
| 768 x 768 | 1.5 | 1.08 | 23.1 | 22.9 |
| 768 x 768 | 2.0 | 1.26 | 41.4 | 42.0 |
| 768 x 768 | 4.0 | 2.13 | 104.0 | 104.3 |
| 768 x 3072 | 0.5 | 1.00 | 0.00 | 0.71 |
| 768 x 3072 | 1.5 | 1.07 | 31.3 | 30.3 |
| 768 x 3072 | 2.0 | 1.24 | 57.0 | 58.1 |
| 768 x 3072 | 4.0 | 2.03 | 145.2 | 144.6 |

The formula needs `tau`. Two estimates from the split-half null: the
Frobenius level `||E_null||_F / sqrt(ab)`, right if the noise is
isotropic, and the edge level `s_max(E_null)/(sqrt(a) + sqrt(b))`,
which places the formula's noise edge at the null's measured largest
singular value.

## 4. What GPT-2's gradients look like

**The noise is not isotropic.** On GPT-2 base, next-token
cross-entropy, 16 modules, the split-half null has effective rank
`||E||_F^2 / s_max^2` between 1.2 and 4.6: the sampling noise of a
module's gradient lives in a handful of directions, as a sum of a
few dominant outer products would. The independent-entry model of
section 3 is false as a description, the Frobenius level puts the
edge far too low (its prediction equals the raw training slope to
three digits), and no sharp threshold is to be expected.

**The edge-level shrinkage nevertheless predicts the population
slope.** Training sets of 8 to 128 contexts against one held-out set
of 192 contexts, three text conditions, rank 2
(`rmt_check2.log`). Mean absolute log error of the predictor against
the measured held-out slope, over the 16 modules:

| condition | n | s1 / edge (median) | held / train | held / shrunk | error, raw training slope | error, shrunk |
|---|---|---|---|---|---|---|
| plain | 8 | 1.17 | 0.44 | 1.07 | 0.870 | 0.232 |
| plain | 16 | 1.56 | 0.62 | 0.93 | 0.534 | 0.142 |
| plain | 32 | 2.36 | 0.69 | 0.82 | 0.399 | 0.220 |
| plain | 64 | 2.84 | 0.82 | 0.92 | 0.225 | 0.104 |
| plain | 128 | 4.00 | 0.88 | 0.93 | 0.141 | 0.076 |
| alternating caps | 8 | 1.47 | 0.66 | 1.06 | 0.448 | 0.112 |
| alternating caps | 16 | 2.08 | 0.87 | 1.11 | 0.128 | 0.126 |
| alternating caps | 32 | 2.74 | 0.90 | 1.01 | 0.117 | 0.033 |
| alternating caps | 64 | 4.26 | 0.95 | 1.00 | 0.049 | 0.033 |
| alternating caps | 128 | 5.95 | 0.96 | 0.99 | 0.058 | 0.017 |
| leet | 8 | 1.76 | 0.66 | 0.93 | 0.428 | 0.130 |
| leet | 16 | 2.04 | 0.88 | 1.15 | 0.134 | 0.187 |
| leet | 32 | 3.58 | 0.97 | 1.08 | 0.040 | 0.080 |
| leet | 64 | 4.66 | 0.98 | 1.04 | 0.024 | 0.037 |
| leet | 128 | 3.71 | 0.89 | 0.96 | 0.112 | 0.046 |

Over the fifteen rows the raw training slope is off by 0.247 on
average and the shrunk one by 0.105; the shrunk one is better in
twelve rows, and by a factor of three to four where it matters most
(8 contexts: 0.87 to 0.23, 0.45 to 0.11, 0.43 to 0.13). Where the
training slope is already within a few percent (leet at 16 to 64
contexts) the shrinkage over-corrects by 4 to 15 percent. The lower
bound (2), with `||E||_(r)` read off the split-half null, holds on
238 of the 240 module-conditions.

**How fast the first-order direction becomes real.** The fraction of
the training slope that generalises rises from 0.44 to 0.88 on plain
text and from 0.66 to 0.96 on a format shift as the contexts go from
8 to 128, tracking the ratio of the top singular value to the noise
edge (about 1.2 to 4 and 1.5 to 6). At 8 contexts a median of one of
a module's top eight singular values clears the edge; at 32 and
above, two.

## 5. What this does and does not explain

- **Mimicry is not a first-order effect of the first direction.**
  By 24 to 32 contexts on a format shift the top two gradient
  directions of every module generalise almost fully. The mimicry
  ED2 and ED3 measured (65 to 88 percent of the training residual
  removed by any module, far less held-out) is produced along the
  fit, as later steps follow directions under the noise edge. The
  number of singular values above the edge (one or two here) is a
  first-order reading of how much rank the data can support.
- **Why matrix size matters.** The edge grows like
  `sqrt(a) + sqrt(b)`: 55 for a 768 x 768 attention matrix, 83 for a
  768 x 3072 MLP matrix. At equal signal an MLP module needs about
  2.3 times the data to clear it, which is the direction of ED3's
  upper-casing pilot (MLP modules overfitting on a weak shift) and
  of the format shifts where they lead once the signal is strong.
- **A pre-screen without held-out data.** `S_pred` uses the training
  set only (the full gradient and two half gradients, three backward
  passes for every module at once). Where held-out data is scarce it
  is a substitute for the held-out slope, good to about ten percent
  here.
- **What it does not give.** The slope is an infinitesimal rate. It
  is positive for every module even on plain text at 8 contexts,
  where a 60-step fit overfits, so it cannot be the go or no-go
  gate; and it says nothing about how far a module can usefully
  move, which is what separates modules once all their slopes are
  real. Both are questions about the fit's length, and ED4's pilot
  compares the slope against estimates that take a finite step.

## 6. From the rate to the gain: the half rule

Added 2026-11-11, 00:41 UTC, before the ED4 pilot printed any number.

The slope is a rate at step zero. To second order along the unit
direction `d = -R/||R||`, with step `eta`,

    L_tr(eta)  = L_tr(0)  - eta S_tr  + kappa eta^2 / 2,
    L_pop(eta) = L_pop(0) - eta S_pop + kappa eta^2 / 2,

`kappa` the curvature of the loss along `d` (its sampling noise is
of higher order than the slope's, so one `kappa` serves both). The
training loss is lowest at `eta_tr = S_tr / kappa`, where it has
fallen by `S_tr^2 / (2 kappa)`. With `rho = S_pop / S_tr`, the
fraction of the training slope that is real, the population loss at
that step has fallen by

    eta_tr S_pop - kappa eta_tr^2 / 2 = (S_tr^2 / (2 kappa)) (2 rho - 1).      (4)

Three consequences.

- **Fitting a direction to its training optimum helps if and only
  if more than half of its slope is real.** Below `rho = 1/2` the
  fit makes the population loss worse than not fitting at all.
- **The share of the training gain that survives is `2 rho - 1`.**
- **Stopping at the fraction `rho` of the way is optimal** and
  always helps: the population gain there is `rho^2` times the
  training-optimal gain, `S_pop^2 / (2 kappa)`.

For a rank-`r` adapter the components differ: component `k` has
`rho_k = eta(s_k) / s_k`, which falls toward zero as `s_k` nears the
noise edge. In the isotropic model `rho_k > 1/2` is the condition
`s_k > (4 / sqrt(3)) tau sqrt(n)` for a square matrix, that is 1.155
times the noise edge (1.172 times for a 1-to-4 rectangle): the
classical optimal hard threshold for singular values, recovered here
as the statement that a component is worth fitting to convergence.
The rank the data supports is the number of components with
`rho_k > 1/2`, a little stricter than the count above the edge.

Gradient flow on a quadratic makes the same point mode by mode: at
time `t` a mode of curvature `lambda` has been fitted to the
fraction `1 - exp(-lambda t)`, and the population gain of that mode
is greatest when the fraction equals its `rho`. Early stopping is a
spectral filter, which is known for least squares; what is used here
is only that the filter's optimum is the quantity the pre-screen
already estimates.

**What (4) predicts for the ED4 pilot, stated before its data.** The
pilot computes, per module, `slope` and `trainslope` (so `rho`), and
`line` and `trainline`, the held-out and training gains at the
training line-search step with logits linearised.

1. Per module, `line / trainline` is close to `2 rho - 1`.
2. Alternating capitals at 96 contexts: `rho` was measured at about
   1.0 for every module (section 4), so every `line` is positive and
   close to its `trainline`.
3. Plain text at 96 contexts: `rho` about 0.9, so `line` about 0.8
   of `trainline`, positive for every module.
4. Plain text at 8 contexts: `rho` has median 0.44 to 0.45, below
   one half, so `line` is negative for about half the modules or
   more and near zero in the median: the look-ahead estimate reads
   no-go where the slope reads go.

The real fit is 60 Adam steps of a LoRA pair, not a line search to
convergence; a short fit is an early-stopped one, so its gain can be
positive where (4) is negative. How the fitted gain sits between the
slope and (4) is what the pilot's sweep shows.

## 7. Status of each statement

| statement | status |
|---|---|
| (1), the one-direction argument, the split-half null | elementary |
| (2), the lower bound | elementary (Ky Fan norm duality), checked: 238 of 240 |
| the spiked-matrix threshold, singular-value map and optimal shrinkage | known results (Baik, Ben Arous and Peche; Benaych-Georges and Nadakuditi; Gavish and Donoho), reproduced numerically here, not re-derived and not fetched |
| reading the shrunk training slope as the generalising part of an adapter's first-order direction, with the edge set by a split-half null | an application; whether it is in the literature was not checkable from this sandbox |
| (4), the half rule and `2 rho - 1` | elementary (a quadratic along one direction); its predictions were written before the data and checked in section 8: it orders the modules (correlation 0.96 over 64) and is biased cautious, by 0.19 at 8 contexts and 0.05 at 96; it is a statement about a line search along one direction and did not carry to a real LoRA fit run long (section 11, pilot) |
| the hard threshold as "worth fitting to convergence" | a reading of a known threshold (Gavish and Donoho's 4 / sqrt(3)), in the isotropic model; checked per component in section 9: safe from 32 contexts up, a floor on the rank and not an estimate of it, unreliable at 8 contexts of plain text |
| early stopping as a spectral filter with optimum `rho` per mode | known for least squares; used, not claimed |
| the edge-level formula calibrating under low-rank noise | an empirical regularity on one model, three text conditions, rank 2; no proof, and the model it comes from is false for this noise |
| the share as the rate at which test gain accrues at the start of a fit; a knee at a training gain common to the matrices; stopping at the cross-fitted knee | the first is an identity for gradient flow, checked on 16 fits; the other two are empirical: 24 long fits at 8 contexts (section 12) and 12 at 32 and 64 under a preregistration, outcome A (section 13); no derivation of why the knee is where it is |

## 8. The half rule checked

Added 01:01 UTC 2026-11-11, after section 6 was committed (72314e6)
and before the pilot reached its plain-text conditions.
`poc/ecsdec/halfrule_check.py` computes the pilot's own quantities
(`slope`, `trainslope`, `line`, `trainline`) for the 16 modules on
separately drawn contexts (seed 5), at 8 and at 96 training contexts,
plain text and alternating capitals; log in
`poc/results/ed4/halfrule_check.log`, every row in
`halfrule_check.json`. It is a check on a second sample, not the
pilot: the pilot's own numbers are set against the same four
predictions in the ED4 preregistration.

| condition | n | `rho` median | `2 rho - 1` median | measured `line / trainline` median | negative: measured, predicted | correlation | mean abs. error |
|---|---|---|---|---|---|---|---|
| plain | 8 | 0.525 | +0.051 | +0.378 | 4, 7 of 16 | 0.96 | 0.221 |
| alternating caps | 8 | 0.737 | +0.474 | +0.645 | 0, 0 of 16 | 0.61 | 0.176 |
| plain | 96 | 0.931 | +0.862 | +0.884 | 0, 0 of 16 | 0.90 | 0.066 |
| alternating caps | 96 | 1.004 | +1.008 | +1.091 | 0, 0 of 16 | 0.64 | 0.075 |

Over the 64 module-condition pairs: correlation 0.96, mean absolute
error 0.134, mean of measured minus predicted +0.116, the sign of the
look-ahead gain right on 61. By size: at 8 contexts the measured
ratio exceeds `2 rho - 1` by 0.185 on average, at 96 by 0.046. The
two alternating-capitals rows have low correlations because `rho`
barely varies across modules there; their errors are no larger.

**The four predictions of section 6, on this sample.**

1. `line / trainline` close to `2 rho - 1`: holds as an ordering and
   at 96 contexts (error 0.07); at 8 contexts it is biased low by
   about 0.2. Partly holds.
2. Alternating capitals at 96: every `line` positive and close to its
   `trainline`. Holds (16 of 16 positive, median ratio 1.09).
3. Plain text at 96: `line` about 0.8 of `trainline`, all positive.
   Holds (median 0.88, 16 of 16 positive).
4. Plain text at 8: `line` negative for about half the modules or
   more and near zero in the median. Fails: 4 of 16 negative, median
   +0.38. Two things went against it. This sample's `rho` has median
   0.525, not the 0.44 to 0.45 of section 4's sample (eight contexts
   is a small sample and the split moves with it); and three modules
   with `rho` between 0.35 and 0.46 came out positive where (4) says
   negative.

**Why the rule reads cautious.** (4) took one curvature `h` for the
training loss and the population loss along the direction. With two,
`h_tr` and `h_pop`, the same algebra gives

    gain_pop / gain_tr at the training optimum = 2 rho - kappa,   kappa = h_pop / h_tr,

so the break-even is `rho > kappa / 2` and the half rule is the case
`kappa = 1`. The measured ratios imply a median `kappa` of 0.85 at 8
contexts and 0.95 at 96. A `kappa` below one is what a direction
fitted to the training contexts would give: it moves the logits most
where the training tokens are, so the second-order cost falls more on
the training loss than on fresh text, and less so as the sample grows.
That reading is not established here: the two curvatures were not
measured separately, and the line search takes steps up to 15 on a
loss that is not quadratic at that range, which is the other
candidate for the gap.

**What stands.** `rho > 1/2` is a sufficient condition for fitting to
the training optimum to help, not a necessary one: on these 64 pairs
no module with `rho` above one half had a negative look-ahead gain,
and three with `rho` between 0.35 and 0.46 had a positive one. As a
screen it errs toward reading no-go.

## 9. The rank question, one component at a time

Added 01:19 UTC 2026-11-11. `poc/ecsdec/rank_check.py`, with
three predictions in its docstring, was committed (f897ce7) before
it ran. For each of the first eight singular components of each
module's training gradient it records `s_k / edge` and the
component's real share `rho_k = u_k^T G_pop v_k / s_k`, `G_pop`
taken on 192 held-out contexts: 1920 components over three text
conditions, five training sizes and 16 modules
(`poc/results/ed4/rank_check.json`). By the half rule a component is
worth fitting to the training optimum when `rho_k > 1/2`; the
isotropic model puts that boundary at `2 / sqrt(3) = 1.155` times
the noise edge.

**A defect in the run.** The script's constant was `4 / sqrt(3) =
2.309` times the edge: the threshold in noise units, used as if it
were in units of the edge. The `P1` and `P2` lines of
`rank_check.log` are therefore at 2.31, not at the 1.155 the
predictions name. The log is kept as it ran. The constant is
corrected and `rank_check rescore` recomputes the predictions at
1.155 from the saved rows, with no new data
(`rank_check_rescored.log`). Both sets of figures are below.

| prediction | at 1.155 x edge | as run, at 2.31 x edge | verdict |
|---|---|---|---|
| P1: above the threshold, `rho_k > 1/2` in at least 90% | 355 of 368, 96.5% | 168 of 168 | holds |
| P2: below it, more than a quarter have `rho_k > 1/2` | 662 of 1552, 42.7% | 849 of 1752, 48.5% | holds |
| P3: above the edge, the shrinker's share correlates with `rho_k` above 0.5 | 0.508 over 400 | the same | holds, by 0.008 |

**Where P1 fails.** All 13 failures at 1.155 are plain text at 8
contexts (11) and 16 contexts (2), and 11 of them are a module's
leading component. At 8 contexts of plain text the leading component
clears the threshold in all 16 modules and is more than half real in
5. From 32 contexts up no component above the threshold failed (257
of 257). The split-half null at 8 contexts is two halves of four,
and its edge is itself a noisy number.

**The threshold is a floor on the rank, not the rank.** Per module,
of the first eight components:

| condition | n | worth fitting (`rho_k > 1/2`) | above 1.155 x edge |
|---|---|---|---|
| plain | 8 | 0.6 | 1.0 |
| plain | 16 | 1.5 | 1.1 |
| plain | 32 | 2.4 | 1.5 |
| plain | 64 | 3.6 | 1.8 |
| plain | 128 | 5.9 | 1.9 |
| alternating caps | 8 | 1.8 | 1.0 |
| alternating caps | 16 | 2.4 | 1.3 |
| alternating caps | 32 | 4.1 | 1.5 |
| alternating caps | 64 | 6.1 | 1.8 |
| alternating caps | 128 | 7.2 | 2.0 |
| leet | 8 | 1.9 | 1.2 |
| leet | 16 | 3.9 | 1.3 |
| leet | 32 | 6.4 | 1.8 |
| leet | 64 | 7.6 | 1.9 |
| leet | 128 | 8.0 | 2.0 |

At 128 contexts six to eight of the first eight components are more
than half real and two clear the threshold. Components between 0.5
and 1.0 times the edge, inside the noise by the isotropic reading,
have a median `rho_k` of 0.74 to 0.78 and are above one half in 82
to 89% of cases; only below 0.5 times the edge does the median fall
under one half (0.35).

**Reading.** The edge is the noise's largest singular value, and the
noise is close to low rank (section 4), so the edge overstates the
noise a component in a generic direction meets. That is the same
fact that made the model false in section 4, seen from the other
side: it left the rank-2 slope well calibrated and it makes the
edge useless as a rank selector beyond "at least this many". A rank
estimate needs a `rho_k` that does not go through a noise model.
The direct candidate is cross-fitting: take the directions from one
half of the training contexts and measure their slope on the other
half. `rho_k` here is also measured against a finite held-out set,
so for the smallest components it carries noise of its own.

## 10. Cross-fitting: the real share without a noise model

Added 01:35 UTC 2026-11-11. `poc/ecsdec/crossfit_check.py`,
with three predictions in its docstring, was committed (f063540)
before it ran; log in `poc/results/ed4/crossfit_check.log`, rows in
`crossfit_check.json`.

Split the `n` training contexts into halves A and B. A direction
taken from A is independent of B, so `<G_B, R_A> / ||R_A||^2` is an
unbiased estimate of the real share of a direction fitted on `n / 2`
contexts; average it with the same from B to A. It uses no held-out
text and no model of the noise. It estimates a smaller sample than
the one in hand, so it should read low. To first order in the noise
the optimism `<E, R> / ||R||` is quadratic in `E`, so `1 - rho` is
proportional to `1 / n` and the corrected estimate is
`(1 + rho_cf) / 2`.

| condition | n | share, measured | cross-fitted | corrected | error: raw slope | shrunk | cross-fit | corrected |
|---|---|---|---|---|---|---|---|---|
| plain | 8 | 0.434 | 0.329 | 0.664 | 0.840 | 0.293 | 0.278 | 0.447 |
| plain | 16 | 0.615 | 0.374 | 0.687 | 0.542 | 0.151 | 0.362 | 0.195 |
| plain | 32 | 0.733 | 0.654 | 0.827 | 0.337 | 0.169 | 0.178 | 0.137 |
| plain | 64 | 0.850 | 0.790 | 0.895 | 0.187 | 0.069 | 0.088 | 0.068 |
| plain | 128 | 0.883 | 0.870 | 0.935 | 0.128 | 0.065 | 0.059 | 0.054 |
| alternating caps | 8 | 0.665 | 0.409 | 0.705 | 0.421 | 0.168 | 0.517 | 0.077 |
| alternating caps | 16 | 0.831 | 0.604 | 0.802 | 0.225 | 0.073 | 0.282 | 0.056 |
| alternating caps | 32 | 0.896 | 0.780 | 0.890 | 0.124 | 0.043 | 0.139 | 0.027 |
| alternating caps | 64 | 0.941 | 0.882 | 0.941 | 0.061 | 0.029 | 0.070 | 0.025 |
| alternating caps | 128 | 0.893 | 0.947 | 0.973 | 0.113 | 0.070 | 0.055 | 0.084 |
| leet | 8 | 0.755 | 0.534 | 0.767 | 0.261 | 0.087 | 0.375 | 0.082 |
| leet | 16 | 0.891 | 0.673 | 0.837 | 0.138 | 0.085 | 0.299 | 0.064 |
| leet | 32 | 0.948 | 0.827 | 0.913 | 0.060 | 0.051 | 0.165 | 0.060 |
| leet | 64 | 0.975 | 0.905 | 0.952 | 0.029 | 0.044 | 0.101 | 0.041 |
| leet | 128 | 0.895 | 0.945 | 0.973 | 0.111 | 0.056 | 0.062 | 0.084 |

Shares are medians over the 16 modules for the rank-2 direction;
errors are mean absolute log errors of each predictor of the
held-out slope.

| prediction | result | verdict |
|---|---|---|
| C1: uncorrected, the cross-fitted share reads low in at least 12 of 15 rows | 13 of 15 | holds |
| C2: corrected, its error is below the raw training slope's | 0.100 against 0.238 | holds |
| C3: as a rank estimate it beats the count above 1.155 x edge in at least 12 of 15 rows | 12 of 15; mean absolute error per module 1.41 against 2.76 | holds, at the bar |

**Against the shrunk slope.** Not predicted either way: the corrected
cross-fit and the shrunk slope tie, 0.100 against 0.097. They fail in
different places. The correction overshoots where the share is low
(plain text at 8 contexts: 0.664 against a measured 0.434, error
0.447 against the shrunk slope's 0.293), which is where a first-order
expansion in the noise has no standing. On a format shift at 8 to 32
contexts it is the better of the two (0.027 to 0.077 against 0.043 to
0.168).

**As a rank estimate.** The number of the first eight components
whose uncorrected cross-fitted share exceeds one half, per module,
against the number worth fitting and the count above the threshold of
section 9:

| condition | n | worth fitting | cross-fit | above 1.155 x edge |
|---|---|---|---|---|
| plain | 8 | 0.6 | 0.6 | 1.0 |
| plain | 16 | 1.5 | 0.5 | 1.1 |
| plain | 32 | 2.4 | 1.7 | 1.5 |
| plain | 64 | 3.5 | 2.2 | 1.8 |
| plain | 128 | 5.6 | 3.4 | 1.9 |
| alternating caps | 8 | 1.8 | 0.5 | 1.0 |
| alternating caps | 16 | 2.4 | 1.4 | 1.3 |
| alternating caps | 32 | 4.1 | 2.5 | 1.5 |
| alternating caps | 64 | 6.2 | 3.9 | 1.8 |
| alternating caps | 128 | 7.2 | 5.8 | 2.0 |
| leet | 8 | 1.9 | 1.0 | 1.2 |
| leet | 16 | 4.0 | 1.5 | 1.3 |
| leet | 32 | 6.4 | 3.5 | 1.8 |
| leet | 64 | 7.6 | 6.2 | 1.9 |
| leet | 128 | 8.0 | 7.8 | 2.0 |

The cross-fitted count is at or below the number worth fitting in all
15 rows, so it stays a cautious estimate, and from 32 contexts up it
follows the true number where the edge count stays near 2. The three
rows where the edge count is closer are at 8 and 16 contexts; there
neither is good.

**What cross-fitting cannot see.** At 128 contexts on the two format
shifts the measured share falls back to 0.89 while the cross-fitted
share reads 0.95. The training and held-out contexts come from
different files; once the sampling noise is small, what is left is
the difference between the two sets of files, and a split inside the
training set carries no information about that. Cross-fitting
estimates how a direction holds on more text like the training text.

**A defect in how these runs draw text.** The contexts are drawn
from this repository's `docs/*.md` as they stand when a process
reads them, alternate files to training and to held-out. This note
is one of those files, and every section added to it changes the
pool; a new file in `docs/` also shifts which files fall on which
side. No docs commit fell inside any run's window (rmt 00:02 to
00:06 and 00:09 to 00:17, half rule 00:46 to 01:00, rank 01:10 to
01:17, cross-fit 01:22 to 01:32), so each run is internally
consistent, but sections 4, 8, 9 and 10 are on slightly different
pools although their seeds agree: section 9 has 3.6 components
worth fitting on plain text at 64 contexts and this section 3.5,
section 4 has a share of 0.69 on plain text at 32 contexts and this
section 0.733. The comparisons inside each table are unaffected;
numbers should not be compared across sections to the second
decimal. ED2's and ED3's scored runs are not affected: no docs
commit lies between either freeze and its run. For ED4 the corpus is
to be pinned to a named commit before the freeze.

## 11. The half rule does not carry to a full fit (pilot)

Added 02:47 UTC 2026-11-11. Pilot data for ED4
(`poc/results/ed4/pilot3.json`, `pilot3.log`), not a scored result
and not preceded by a written prediction; ED4's preregistration
turns it into one.

Sections 6 and 8 concern a step along one fixed direction, with the
logits linearised. A LoRA fit is not that: it moves far beyond the
first-order direction. To see what a real fit does, a rank-2 LoRA
was trained on each of eight modules alone for 300 Adam steps (five
times the sweep's budget, same start and learning rate) on 8
contexts of plain text, with its loss on 96 test contexts and on 96
separate validation contexts recorded every 10 steps. `rho` is the
slope on the validation contexts over the training slope.

| module | `rho` | cross-fitted share | test gain: peak (step) | step 60 | step 150 | step 300 | training gain, step 300 | stopped at the validation minimum |
|---|---|---|---|---|---|---|---|---|
| `v@2` | 0.22 | 0.15 | +0.31 (110) | +0.28 | +0.28 | -1.13 | 3.31 | +0.31 |
| `o@2` | 0.28 | 0.10 | +0.44 (110) | +0.38 | +0.36 | -2.04 | 4.91 | +0.44 |
| `proj@2` | 0.37 | 0.20 | +0.47 (50) | +0.46 | -2.40 | -4.09 | 6.27 | +0.47 |
| `o@8` | 0.37 | 0.16 | +0.49 (110) | +0.20 | +0.38 | -1.68 | 4.19 | +0.49 |
| `fc@2` | 0.38 | 0.19 | +0.40 (50) | +0.38 | -1.68 | -2.49 | 6.30 | +0.38 |
| `v@8` | 0.46 | 0.30 | +0.47 (110) | +0.21 | +0.32 | -1.59 | 4.08 | +0.47 |
| `proj@8` | 0.57 | 0.38 | +0.56 (50) | +0.56 | -1.16 | -2.11 | 5.11 | +0.56 |
| `fc@8` | 0.59 | 0.44 | +0.48 (80) | +0.44 | -1.63 | -2.71 | 6.21 | +0.48 |

Every fit peaks within 110 steps, crosses zero between steps 100 and
200 and ends 1.1 to 4.1 nats below the unadapted model, with its
training loss driven almost to zero on the MLP matrices (the base
training loss is 6.40). The two modules with `rho` above one half
fall as far as the rest. Across the eight, `rho` does not order the
outcome in the direction the rule needs: its rank correlation with
the test gain at steps 150, 200 and 300 is -0.24, -0.38 and -0.38.
What orders the time course is the kind of matrix: the MLP matrices
peak at 50 to 80 steps and are negative by 120, the attention
matrices peak at 110 and are negative by 200.

**What this takes away.** `rho > 1/2` was read in section 8 as
sufficient for fitting to the training optimum to help. That is
true of the line search it was derived for and false of a LoRA fit
run long, on the only eight cases tried. The share describes the
first step of a fit. It is evidence about a ranking and about how
much of an initial rate is real; it is not a stopping rule, and the
tool's text has been changed to say so.

**What worked.** Stopping each fit at the minimum of its validation
loss kept 95 to 100% of its peak test gain. The sweep's 60-step
budget sits near that point for the MLP matrices and before it for
the attention matrices, which is why the 60-step sweeps of the pilot
show gains everywhere.

**Limits.** One sample of 8 contexts, one text condition, one
learning rate, eight modules. At 8 contexts `rho` only reaches 0.59,
so the pilot says nothing about fits whose share is near one.

## 12. What the share does describe: the rate at the start, and a knee

Added 06:06 UTC 2026-11-11. Exploratory, beside ED4:
`poc/ecsdec/knee_check.py`, logs `knee_check.log` and
`knee_check_scored.log` in `poc/results/ed4/`. Its predictions K1 to
K3 were committed before its first run (1488b8c) and K4 before the
second (420e643). The long fits it reads are the pilot's eight
(section 11) and the sixteen of ED4's scored run; ED4's own bars on
those sixteen are scored separately by its frozen scorer.

**An identity.** Under gradient flow on the training loss,

    d L_pop / d L_tr = <grad L_pop, grad L_tr> / ||grad L_tr||^2,

so at every moment of a fit the test gain accrues, per unit of
training gain, at the real share of the step then being taken. The
pre-screen's `rho` is this ratio at the start, for the leading part
of the gradient. Section 6 assumed the ratio falls linearly along
one direction; section 11 showed a real fit does not behave so. What
the long fits show instead:

**The rate at the start is the share.** Over the first 30 steps the
test gain over the training gain, against `rho` measured before
training on validation contexts: rank correlation 0.83 over the 16
scored fits (K3 asked for more than 0.5), mean absolute difference
0.05, largest 0.15.

**Then a knee, at a training gain that belongs to the sample.** The
ratio stays near its starting value and then drops below zero within
a few tens of steps. The training gain at the test peak:

| sample | mean | c.v. over the eight matrices | step of the peak, c.v. |
|---|---|---|---|
| pilot, plain text | 1.29 | 0.22 | 0.33 |
| scored, leet | 1.82 | 0.18 | 0.28 |
| scored, plain text | 1.15 | 0.10 | 0.25 |

K3 asked for a c.v. below 0.35 in each scored condition. The MLP
matrices reach the knee in 50 to 90 steps and the attention matrices
in 90 to 140; in training gain they reach it together.

**A stopping rule from the training contexts alone.** Fit on one
half of the training contexts and watch the loss on the other half;
note the training gain at which that loss is lowest; do this for
four matrices, both ways round, and take the median `g*` of the
eight values. Then stop any fit on the full sample when its training
gain reaches `g*`.

| sample | the eight cross-fitted values, c.v. | `g*` | mean training gain at the test peak | test gain positive | at least 2/3 of the peak | median share of the peak, lowest |
|---|---|---|---|---|---|---|
| pilot, plain text (K1, K2) | 0.37 | 1.31 | 1.29 | 8 of 8 | 8 of 8 | 0.99, 0.94 |
| scored, leet (K4) | 0.31 | 1.76 | 1.82 | 8 of 8 | 8 of 8 | 0.96, 0.79 |
| scored, plain text (K4) | 0.18 | 1.43 | 1.15 | 8 of 8 | 7 of 8 | 0.89, 0.49 |

| prediction | verdict |
|---|---|
| K1: the cross-fitted values have a c.v. below 0.35; the step of the turn differs by 2 or more between MLP and attention | fails on the first part (0.37); the second holds (2.2) |
| K2: on the pilot sample, stopping at `g*` keeps a positive gain in 8 of 8 and two thirds of the peak in at least 6 | holds |
| K3: the knee's training gain has a c.v. below 0.35 in each scored condition; the early ratio tracks `rho` above 0.5 | holds |
| K4: the rule found and applied on each scored sample: positive in 8 of 8, two thirds of the peak in at least 6 | holds in both |

A single cross-fitted value is too noisy to use (0.61 to 2.23 on the
pilot sample); the median of eight is what the rule rests on. My
expectation that a half sample would turn earlier was wrong: `g*`
fell within 4% of the full sample's knee twice and 24% above it
once, and that overshoot is where the one fit below two thirds
(`v@2`, 0.49 of its peak) comes from.

**Against the alternatives**, share of each fit's peak test gain
kept, over the 24 long fits:

| rule | needs | median | lowest | at least 2/3 | positive |
|---|---|---|---|---|---|
| stop at the validation minimum | 96 held-out contexts | 1.00 | 0.95 | 24 | 24 |
| stop at the cross-fitted knee | nothing beyond the 8 training contexts | 0.96 | 0.48 | 23 | 24 |
| stop at step 60 | a budget chosen in advance | 0.90 | 0.39 | 18 | 24 |
| train to step 300 | | -4.32 | -10.28 | 0 | 0 |

The step-60 budget is the one the pilot happened to use and suits
the MLP matrices; it leaves the attention matrices of layer 8 at 40
to 45% of their peak. A budget in steps does not transfer between
matrices and a budget in training gain does.

**Limits.** Three samples of 8 contexts, two kinds of text, one
model, one learning rate, rank 2; the cross-fit costs eight half-size
fits. The rows of the comparison table other than the knee's are
descriptive, with no prediction behind them. Nothing here has been
tried at 32 or more contexts, where a 60-step fit does not reach a
knee at all.

## 13. The knee at 32 and 64 contexts (ED5)

Added 11:07 UTC 2026-11-11. Section 12's limits said nothing
had been tried above 8 contexts. ED5 preregistered the test
(`docs/math-track-ed5-prereg.md`) and its outcome is A
(`docs/math-track-ed5-results.md`): twelve long fits, plain and leet
text at 32 contexts and plain text at 64, four matrices each.

| kind of text | contexts | training gain at the test peak, mean over the matrices | c.v. | step of the peak |
|---|---|---|---|---|
| plain | 8 (ED4 pilot) | 1.29 | 0.22 | 50 to 110 |
| plain | 8 (ED4) | 1.15 | 0.10 | 50 to 100 |
| plain | 32 | 1.07 | 0.12 | 70 to 160 |
| plain | 64 | 1.03 | 0.10 | 80 to 200 |
| leet | 8 (ED4) | 1.82 | 0.18 | 60 to 140 |
| leet | 32 | 1.67 | 0.10 | 110 to 200 |

The knee's training gain falls by a tenth to a fifth from 8 to 64
contexts and differs by half as much again between the two kinds of
text. More contexts make more of the early training gain real (the
test gain over the training gain in the first 30 steps is 0.25 to
0.61 at 8 contexts and 0.72 to 0.84 at 64 on plain text) and push
the knee later in steps, and do not move it much in training gain.
Why the turn should sit at a fixed training gain for a kind of text
is not explained here; it is the regularity the stopping rule uses,
and over the 36 long fits of sections 12 and 13 the rule kept a
positive test gain in every one and two thirds of the peak in 35.

## 14. Re-reading the long fits: a collapse, a reason for it, and what the rule has not yet been tested against

Added 2026-11-11, in a new session, after the scored ED6 run was lost
with the machine it ran on (its results were never committed; only
its frozen config is in `poc/results/ed6/run/`). Everything below is
exploratory and after the fact: it reads curves already recorded
(ED4, ED4's pilot, ED5, ED5's pilot, ED6's pilot, the PyTorch
cross-check), trains nothing, and was not predicted before it was
computed. Script `poc/ecsdec/knee_reanalysis.py`, output
`poc/results/ed6/knee_reanalysis.log`.

**A collapse, stronger than a shared knee.** Plot each fit's test gain
against its training gain instead of against the step. Across the
matrices of one condition the curves nearly coincide: the spread of
test gain between matrices, averaged along the curve and divided by
the mean peak, is 2 to 5 times smaller at matched training gain than
at matched step (0.08 against 0.16 to 0.18 at 32 and 64 contexts;
0.26 to 0.35 against 0.85 to 1.67 at 8). The shared knee of
sections 12 and 13 is a consequence: if the curves are one curve,
their maxima are at one training gain. Two corollaries the logs show:

- the mean real share up to the knee, peak test gain over the
  training gain there, is even more nearly common than the knee
  itself at 32 and 64 contexts (c.v. 0.02 to 0.05 across matrices,
  against 0.10 to 0.12 for the knee): 0.65 plain at 32, 0.77 leet at
  32, 0.60 plain at 64; at 8 contexts 0.36 to 0.37 with c.v. 0.10 to
  0.21;
- the gap between training and test gain at the knee is 0.37 to 0.41
  nats in all four 32- and 64-context conditions, plain or leet, and
  0.73 to 1.15 at 8 contexts.

**A sufficient condition for the collapse (argument, not proof).**
Write `f` for the model's outputs on all contexts. Gradient flow on
the training loss through matrix `m` moves them, to first order, as

    df/dt = -K_m(f) grad_f L_tr(f),

`K_m` the tangent kernel of that matrix (for a weight matrix, the
product of the Gram matrix of its inputs and that of the gradients
arriving at its outputs). If the kernels of two matrices are
proportional, `K_m = c_m K`, the two flows trace one path in output
space at speeds `c_m`: `f_m(t) = f(c_m t)`. Training loss and test
loss are both functions of `f`, so test gain as a function of
training gain is the same curve for every such matrix, and its
maximum sits at the same training gain however many steps each
matrix needs to get there. A step budget cannot have this property
and a training-gain budget does. Departures from proportionality
predict departures from the common curve. This is an idealisation
three ways (LoRA starts at `B = 0` and is not lazy, the optimiser is
Adam, rank 2 truncates), so it is a candidate mechanism, not an
explanation, and it says nothing yet about why the curve turns where
it does.

**Testable from here, given weights:** (K5) the centred alignment
between `K_m` and the mean kernel over the four matrices, computed
on the training contexts before training, ranks the matrices by how
far each one's own knee sits from the condition's mean knee. `v@2`,
whose knee is the lowest in every condition, should be the least
aligned. (K6) For a matrix with fast speed `c_m`, the curve against
training gain should not change if the learning rate is halved
(steps double, the curve stays).

**A cheaper cross-fit (after the fact, not a rule).** The rule's
cost is eight half-fits. Taking `g*` from the two half-fits of a
single MLP matrix, `proj@2` (the fastest to turn), keeps on average
0.958, 0.978 and 0.958 of the peak at 32 and 64 contexts against
0.964, 0.986 and 0.967 for the median of eight, for about a fifth of
the half-fit steps, and 0.935 and 0.886 at 8 contexts against 0.937
and 0.856. A single attention matrix is worse (`v@2` alone, whose own
knee is low, stops the others early: 0.72 to 0.77 on leet). The best
single training gain for all matrices of a condition, chosen with
the test curves in hand, keeps 0.94 to 0.99; the median of eight is
within 0.02 of it at 32 and 64 contexts and 0.12 below it on ED4's
plain-text sample at 8, the loss coming from the overshoot named in
section 12.

**A guess at that overshoot.** The half-fits measure the knee of a
sample of `n/2` contexts, not `n`. On plain text the knee is 1.15 to
1.29 at 8, 1.07 at 32 and 1.03 at 64, close to `k(n) = 1.0 + 1.7/n`;
that law puts the knee at 4 contexts at 1.43, which is exactly the
`g*` of ED4's plain-text sample, and its bias, `k(n/2) - k(n) =
1.7/n`, is 0.22 at 8 and 0.05 at 32, matching where the rule lost
and where it did not. Leet at 8 shows no such overshoot (`g*` 1.76,
knee 1.82), so this is three points of one kind of text, not a law.
If it holds, a cross-fit on folds of `3n/4` cuts the bias to a third
at the cost of noisier held-out quarters.

**What the rule has not been tested against.** The use case is that
the rule spends all `n` contexts on training while early stopping on
held-out data spends some on validation. Every comparison so far
holds the training set fixed and gives validation its own 32 to 96
extra contexts, which is not that trade. ED4's half-fits allow one
look at the real trade at 8 contexts: train on all 8 and stop at
`g*`, against train on 4 and stop at the minimum on the other 4, in
nats on the same test contexts. On leet the rule is ahead on all
four matrices with half-fits (0.38 to 0.85 against 0.29 to 0.74). On
plain text the two are level (means 0.35 and 0.34). A 4+4 split is
the worst way to hold out; 6+2 and 7+1 have not been tried.

**ED6.** Its interim readings (three of nine conditions) were
reported in the session that ran it and are not a verdict. The
preregistration lets a lost process be relaunched with the same
command; the config names model directories in that session's
scratch space, so a relaunch also needs the three models at those
paths (or a config edit, which would be a departure to name), and
the models cannot be downloaded from this session's network.
