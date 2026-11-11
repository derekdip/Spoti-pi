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
| (4), the half rule and `2 rho - 1` | elementary (a quadratic along one direction); its predictions were written before the data and checked in section 8: it orders the modules (correlation 0.96 over 64) and is biased cautious, by 0.19 at 8 contexts and 0.05 at 96 |
| the hard threshold as "worth fitting to convergence" | a reading of a known threshold (Gavish and Donoho's 4 / sqrt(3)), in the isotropic model |
| early stopping as a spectral filter with optimum `rho` per mode | known for least squares; used, not claimed |
| the edge-level formula calibrating under low-rank noise | an empirical regularity on one model, three text conditions, rank 2; no proof, and the model it comes from is false for this noise |

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
