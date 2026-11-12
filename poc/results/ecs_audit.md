# Numerical checks for the ECS theory audit

## Section 3: orthonormal states, worst-case rank-n error squared >= 1 - n/M
| n | worst error^2 (PCA basis) | mean error^2 | bound 1 - n/M |
|---|---|---|---|
| 5 | 1.000 | 0.900 | 0.900 |
| 10 | 1.000 | 0.800 | 0.800 |
| 25 | 1.000 | 0.500 | 0.500 |
| 40 | 0.497 | 0.200 | 0.200 |
The mean error squared equals the bound exactly for any basis; the worst case is at or above it, as the theorem says.

## Section 4: coherence mu, bound 1 - n(1 + (M-1) mu)/M
- alpha 0.0: mu 0.000, lambda_max 1.00 <= 1 + (M-1) mu = 1.00; rank-10 worst error^2 1.000, bound 0.800 (holds; loose when mu is not small)
- alpha 0.1: mu 0.029, lambda_max 1.52 <= 1 + (M-1) mu = 2.43; rank-10 worst error^2 0.981, bound 0.515 (holds; loose when mu is not small)
- alpha 0.3: mu 0.130, lambda_max 4.94 <= 1 + (M-1) mu = 7.39; rank-10 worst error^2 0.912, bound -0.478 (holds; loose when mu is not small)

## Sections 8 and 9: block frames, Gershgorin against the summable-overlap bound
- random blocks: mu_B 0.183, rho_B 3.234, lambda_max 1.843; worst-case bound 1 + (M-1) mu_B = 6.29; summable bound 1 + rho_B = 4.23; both hold, the summable one is tighter
- translated local frames (M 30, width 12, s 3): each overlaps d = 2 neighbours, mu_B 0.689, rho_B 1.122, lambda_max 1.735 <= 1 + rho_B = 2.122; rank-20 worst block error 0.800 against bound 0.528; n needed for block error 0.1 by the bound: 38.2 of M s = 90

## Sections 11 and 12: random translation of a periodised Gaussian; PCA eigenvalues against |f^(n)|^2, and the rank law
| sigma | spectrum mismatch, max over the first 40 modes, relative to lambda_0 | rank for eps 0.1 | 0.01 | 0.001 | rank * sigma / sqrt(log 1/eps) at 0.01 |
|---|---|---|---|---|---|
| 0.08 | 7.8e-16 | 8 | 11 | 15 | 0.410 |
| 0.04 | 9.8e-16 | 15 | 23 | 28 | 0.429 |
| 0.02 | 1.3e-15 | 29 | 44 | 55 | 0.410 |
| 0.01 | 2.2e-15 | 59 | 88 | 111 | 0.410 |
The spectrum is |f^(n)|^2 to machine precision; the rank for fixed eps scales as 1/sigma (the last column is constant), and across eps as sqrt(log 1/eps) (ratios 0.1 to 0.001 roughly 1 : 1.4 : 1.7 at fixed sigma). The constant is about 0.5, that is rank ~ (1/2) sigma^-1 sqrt(log 1/eps) when counting positive and negative frequencies together.

## Section 13: random translation of a step; modes needed against eps^-2
| eps | modes m | m * eps^2 |
|---|---|---|
| 0.3 | 5 | 0.45 |
| 0.1 | 41 | 0.41 |
| 0.03 | 308 | 0.28 |
m eps^2 is constant, so m = Theta(eps^-2) as the section says; the translation itself is one coordinate.

## Section 15: bits per state for a Lipschitz one-parameter family
- translation of the width-0.02 Gaussian: Lipschitz constant in the shift 35.4 per unit shift; a shift grid of step eps/K gives state error <= eps with log2(K/eps) bits: 8.5 bits at eps 0.1, 11.8 at 0.01, 15.1 at 0.001, growing by 3.3 bits per decade as k log(1/eps) says with k = 1. The PCA representation of the same family needs the rank in the table above.

## Section 20: the candidate score S(a) equals the exact gain of the linearised augmented model
- ||P_[J,a] r||^2 - ||P_J r||^2 = 0.878733; S(a) = 0.878733; equal to 6.6e-15. The score is exact for the linearised augmented fit, and says nothing about the nonlinear refit (the linearisation gap, docs/linearisation-gap.md).

