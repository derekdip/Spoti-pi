# RGRE-ML-2 scored: 30 cases, 6 datasets, seeds [1, 2, 3, 4, 5]

## B1 selection value over 240 steps
median 0.475 mean 0.533 | random 0.123/0.202 | gradient-norm 0.345/0.406 | oracle in top-3 22%
declared variant, anchored tangents (reported, not the bar): median 0.601 mean 0.583; pick = oracle 12% vs 12% single-anchor
  abalone     median 0.38 mean 0.47 | anchored 0.65/0.64
  california  median 0.44 mean 0.47 | anchored 0.49/0.50
  concrete    median 0.73 mean 0.68 | anchored 0.75/0.74
  diabetes    median 0.47 mean 0.56 | anchored 0.62/0.61
  mpg         median 0.51 mean 0.54 | anchored 0.60/0.49
  winered     median 0.41 mean 0.48 | anchored 0.52/0.51
-> B1 FAIL (bar: median >= 0.90 and above both baselines on median and mean)

## B2 stopping signal: 164 wasted of 240 steps (held-out gain < 1%)
AUC q_perp (single-class) 0.840 | step index 0.618 | in-sample drop of the pick (needs the fit) 0.886 | joint q_perp 0.705
  abalone     wasted 39/40 AUC q_perp 0.62 step 0.44
  california  wasted 33/40 AUC q_perp 0.65 step 0.53
  concrete    wasted 10/40 AUC q_perp 0.71 step 0.58
  diabetes    wasted 33/40 AUC q_perp 0.65 step 0.81
  mpg         wasted 13/40 AUC q_perp 0.66 step 0.72
  winered     wasted 36/40 AUC q_perp 0.88 step 0.95
-> B2 pass (bar: AUC >= 0.75 and above the step-index baseline)

## B3 deferral at step zero, 3 of 12 regions, held-out error outside the deferred regions
[dead_stop] top-S orthogonal beats magnitude on 17% (ties 77%) | medians top-S 0.613 single-class 0.617 magnitude 0.613 random 0.633 none 0.631 hindsight 0.607
    single-class beats magnitude on 27% (ties 70%)
[final] top-S orthogonal beats magnitude on 17% (ties 77%) | medians top-S 0.606 single-class 0.606 magnitude 0.606 random 0.653 none 0.644 hindsight 0.608
    single-class beats magnitude on 27% (ties 70%)
-> B3 FAIL (bar, on the dead-stop student: top-S wins >= 60% with ties against, median below magnitude and random)

## B4 noise detection at step zero: q_perp permuted vs real, 30 pairs
paired (permuted > real on the same split) 100% | pooled AUC 0.992 | median q_perp real 0.963 permuted 0.995 | joint version real 0.354 permuted 0.657
  abalone     real 0.959 permuted 0.999 paired 100%
  california  real 0.972 permuted 0.998 paired 100%
  concrete    real 0.610 permuted 0.995 paired 100%
  diabetes    real 0.968 permuted 0.975 paired 100%
  mpg         real 0.773 permuted 0.989 paired 100%
  winered     real 0.970 permuted 0.995 paired 100%
-> B4 pass (bar: permuted above real on >= 90% of splits)

## Reported
DEAD rule (1% in-sample) on permuted targets: declined 93%; spurious best drop median 0.49% (max 1.59%)
search: one repair fitted per step of 104 candidates (median) = 0.010
held-out RMSE in target-sd units, median over splits:
  dataset      linear dead-stop  8 steps best step    kNN  dead@  best@
  abalone       0.675     0.675    0.662     0.661  0.679    0.0    6.0
  california    0.602     0.602    0.577     0.577  0.610    0.0    8.0
  concrete      0.633     0.460    0.449     0.449  0.573    6.0    8.0
  diabetes      0.746     0.765    0.764     0.741  0.827    1.0    2.0
  mpg           0.431     0.378    0.371     0.363  0.389    5.0    8.0
  winered       0.790     0.779    0.789     0.778  0.825    1.0    3.0
grown model (8 steps) beats linear on held-out in 83% of cases; beats kNN in 83%
modules grown by kind: {'pair': 71, 'bump': 64, 'cubic': 33, 'sin': 27, 'abs': 15, 'quad': 14, 'step': 13, 'exp': 3}
oracle's pick by kind: {'bump': 201, 'sin': 28, 'pair': 4, 'abs': 4, 'quad': 2, 'cubic': 1}
held-out value of the pick (pick's test drop / best candidate's test drop) median 0.31

## Outcome (frozen tree)
B1 fail, B2 pass, B3 fail, B4 pass -> outcome D
