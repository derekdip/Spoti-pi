# Behavioural tolerance sweep (Math Track B0, item 18)

Convention: expectation over recorded inputs (training + held-out walks, averaged). Cost is ops per stalk per frame; the teacher is 320 plus neighbour reads.

## A. Representations

| representation | cost | visual | AI field | gameplay | visual (held-out) |
|---|---|---|---|---|---|
| field only, 8x8 (wake+presence baked) | 14 | 0.843 | 0.702 | 0.277 | 0.871 |
| field only, 10x10 (wake+presence baked) | 15 | 0.762 | 0.613 | 0.195 | 0.750 |
| field only, 16x16 (wake+presence baked) | 20 | 0.609 | 0.371 | 0.036 | 0.598 |
| field only, 20x20 (wake+presence baked) | 24 | 0.539 | 0.337 | 0.041 | 0.527 |
| field only, 25x25 (wake+presence baked) | 31 | 0.496 | 0.296 | 0.026 | 0.489 |
| field only, 32x32 (wake+presence baked) | 43 | 0.453 | 0.273 | 0.020 | 0.448 |
| field only, 40x40 (wake+presence baked) | 60 | 0.402 | 0.251 | 0.020 | 0.399 |
| field only, 64x64 (wake+presence baked) | 135 | 0.420 | 0.256 | 0.020 | 0.415 |
| path only (wake) | 26 | 0.422 | 0.260 | 0.017 | 0.420 |
| path + local kernels (wake + presence) | 48 | 0.402 | 0.251 | 0.020 | 0.399 |
| path + local + event residuals (subset of six) | 76 | 0.387 | 0.222 | 0.018 | 0.383 |
| full grammar (six terms) | 124 | 0.386 | 0.221 | 0.018 | 0.382 |
| teacher itself | 320 | 0.000 | 0.000 | 0.000 | 0.000 |

Lower envelope (cheapest representation reaching each error level):

- **visual**: field only, 8x8 (wake+presence baked) (14 ops, 0.843) -> field only, 10x10 (wake+presence baked) (15 ops, 0.762) -> field only, 16x16 (wake+presence baked) (20 ops, 0.609) -> field only, 20x20 (wake+presence baked) (24 ops, 0.539) -> path only (wake) (26 ops, 0.422) -> path + local kernels (wake + presence) (48 ops, 0.402) -> path + local + event residuals (subset of six) (76 ops, 0.387) -> full grammar (six terms) (124 ops, 0.386) -> teacher itself (320 ops, 0.000)
- **ai**: field only, 8x8 (wake+presence baked) (14 ops, 0.702) -> field only, 10x10 (wake+presence baked) (15 ops, 0.613) -> field only, 16x16 (wake+presence baked) (20 ops, 0.371) -> field only, 20x20 (wake+presence baked) (24 ops, 0.337) -> path only (wake) (26 ops, 0.260) -> path + local kernels (wake + presence) (48 ops, 0.251) -> path + local + event residuals (subset of six) (76 ops, 0.222) -> full grammar (six terms) (124 ops, 0.221) -> teacher itself (320 ops, 0.000)
- **gameplay**: field only, 8x8 (wake+presence baked) (14 ops, 0.277) -> field only, 10x10 (wake+presence baked) (15 ops, 0.195) -> field only, 16x16 (wake+presence baked) (20 ops, 0.036) -> path only (wake) (26 ops, 0.017) -> teacher itself (320 ops, 0.000)

## B. Liveness threshold

Radial-impulse token of the six-term fit: lam=9.53, k=162, zeta=0.73, slower decay rate lambda' = 9.33 1/s.

| eps | live tokens per frame (measured) | predicted (R/lambda') log(1/eps) | visual error with pruning |
|---|---|---|---|
| 3e-01 | 0.80 | 0.39 | 0.3860 |
| 1e-01 | 1.07 | 0.74 | 0.3862 |
| 3e-02 | 1.28 | 1.13 | 0.3864 |
| 1e-02 | 1.41 | 1.48 | 0.3864 |
| 3e-03 | 1.50 | 1.87 | 0.3864 |
| 1e-03 | 1.56 | 2.22 | 0.3864 |
| 3e-04 | 2.55 | 2.61 | 0.3864 |
| 1e-04 | 2.84 | 2.96 | 0.3864 |
| 1e-05 | 3.15 | 3.70 | 0.3864 |

Measured slope of live count against log(1/eps): 0.237; predicted R/lambda' = 0.322.

## C. Path tolerance

| tolerance (m) | points kept | excess visual error | excess AI error |
|---|---|---|---|
| 1.000 | 3.5 | +0.3212 | +0.2822 |
| 0.500 | 3.5 | +0.3212 | +0.2822 |
| 0.200 | 5.0 | +0.2243 | +0.2215 |
| 0.100 | 6.5 | +0.1841 | +0.1963 |
| 0.050 | 9.5 | +0.0564 | +0.0453 |
| 0.020 | 14.5 | +0.0350 | +0.0189 |
| 0.010 | 21.0 | +0.0278 | +0.0126 |
| 0.005 | 29.0 | +0.0200 | +0.0042 |
| 0.002 | 48.5 | +0.0110 | +0.0038 |

Log-log slope of points against tolerance: -0.44 (prediction -0.5). Log-log slope of excess visual error against tolerance: 0.60 (Lipschitz prediction +1).

