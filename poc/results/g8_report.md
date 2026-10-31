# G8 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 8 steps, base phase at most 6

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G8 ['rhythm', 'arms', 'legs', 'torso', 'limp-1', 'legs', 'hold+1'] | G7 ['stiff-1', 'rhythm', 'arms', 'legs', 'rhythm', 'torso'] | naming step: pick limp drops {'limp': 0.207, 'stiff': 0.195, 'hold': 0.0, 'vault': 0.0, 'weak': 0.0} rejected []
  stump_left_s0        designed limp-1  G8 ['torso', 'arms', 'limp-1', 'legs'] | G7 ['torso', 'arms', 'limp-1', 'legs'] | naming step: pick limp drops {'hold': 0.083, 'stiff': 0.026, 'limp': 0.013, 'weak': 0.008, 'vault': 0.0} rejected ['hold', 'stiff']
  nolegs_s0            designed vault+0  G8 ['arms', 'torso'] | G7 ['arms', 'torso'] | naming step: pick None drops {'vault': 0.0} rejected ['vault']
  locked_knee_right_s0 designed stiff+1  G8 ['rhythm', 'torso', 'legs', 'stiff+1', 'legs', 'hold-1', 'limp+1'] | G7 ['stiff+1', 'torso', 'rhythm', 'hold-1', 'legs'] | naming step: pick stiff drops {'stiff': 0.092, 'limp': 0.013, 'weak': 0.007, 'hold': 0.0, 'vault': 0.0} rejected []
  stump_right_s0       designed limp+1  G8 ['lateral', 'arms', 'vault', 'rhythm', 'hold+1'] | G7 ['lateral', 'arms', 'vault', 'rhythm', 'hold+1'] | naming step: pick vault drops {'vault': 0.044, 'hold': 0.01, 'stiff': 0.008, 'limp': 0.0, 'weak': 0.0} rejected []
-> K1 FAIL: first 1 of 3 (>= 2), within two 1 of 3 (>= 3), mirrors 1 of 2 (>= 2)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.568 -> 0.298 | held-out mean 0.565 -> 0.368, runs 0.584->0.357, 0.545->0.379 (2 of 2 lower)
  stump_left_s0        fit 0.676 -> 0.274 | held-out mean 0.647 -> 0.428, runs 0.630->0.440, 0.663->0.417 (2 of 2 lower)
  nolegs_s0            fit 0.657 -> 0.446 | held-out mean 0.717 -> 0.605, runs 0.761->0.740, 0.672->0.471 (2 of 2 lower)
  noleg_left_s0        fit 0.830 -> 0.654 | held-out mean 0.676 -> 0.345, runs 0.671->0.329, 0.680->0.361 (2 of 2 lower)
  short_shank_left_s0  fit 0.446 -> 0.296 | held-out mean 0.487 -> 0.392, runs 0.554->0.470, 0.421->0.315 (2 of 2 lower)
  short_shank_right_s0 fit 0.484 -> 0.351 | held-out mean 0.534 -> 0.489, runs 0.608->0.552, 0.461->0.427 (2 of 2 lower)
  locked_knee_right_s0 fit 0.612 -> 0.425 | held-out mean 0.681 -> 0.507, runs 0.570->0.348, 0.792->0.665 (2 of 2 lower)
  noleg_right_s0       fit 0.619 -> 0.273 | held-out mean 0.629 -> 0.353, runs 0.618->0.350, 0.640->0.356 (2 of 2 lower)
  stump_right_s0       fit 0.747 -> 0.317 | held-out mean 0.678 -> 0.424, runs 0.652->0.474, 0.705->0.374 (2 of 2 lower)
-> K4 pass: 9 of 9 (>= 7); both runs lower on 9 of 9

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  worse: height, orient, lateral
  stump_left_s0        worse: height
  nolegs_s0            worse: asym_joints
  noleg_left_s0        worse: contact_t, asym_joints
  short_shank_left_s0  worse: height, orient, lateral
  short_shank_right_s0 none worse
  locked_knee_right_s0 worse: height, reach
  noleg_right_s0       worse: contact_t, height
  stump_right_s0       worse: coupling, asym_joints, height, orient
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); none worse at all on 1 of 9

## K3 controls: impairment repairs added, in total
  weak_hip_left_s0     ['torso', 'lateral', 'arms'] (0.364 -> 0.255, held-out mean 0.421 -> 0.383)
  intact_s0            ['legs', 'lateral', 'arms', 'torso'] (0.331 -> 0.299, held-out mean 0.392 -> 0.326)
  weak_hip_right_s0    ['lateral', 'torso', 'lateral'] (0.557 -> 0.384, held-out mean 0.473 -> 0.431)
  intact_s1            ['torso', 'arms', 'legs', 'lateral', 'legs'] (0.378 -> 0.274, held-out mean 0.368 -> 0.339)
-> K3 pass: 0 impairment repairs on 4 controls (<= 4)

## Reported
  repairs applied per case, median 4; rejections by reason {'spent': 130, 'held-out': 80, 'guard': 4}
  applied repairs lowering both held-out runs 44 of 60, one run 16
  value of the applied repair against the best fitting drop, median 1.00
  weak_hip_left_s0     G8 ['torso', 'lateral', 'arms'] fit 0.364 -> 0.255 (held-out 0.383) | G7 -> 0.255 (0.383)
  intact_s0            G8 ['legs', 'lateral', 'arms', 'torso'] fit 0.331 -> 0.299 (held-out 0.326) | G7 -> 0.299 (0.326)
  locked_knee_left_s0  G8 ['rhythm', 'arms', 'legs', 'torso', 'limp-1', 'legs', 'hold+1'] fit 0.568 -> 0.298 (held-out 0.368) | G7 -> 0.272 (0.384)
  stump_left_s0        G8 ['torso', 'arms', 'limp-1', 'legs'] fit 0.676 -> 0.274 (held-out 0.428) | G7 -> 0.274 (0.428)
  nolegs_s0            G8 ['arms', 'torso'] fit 0.657 -> 0.446 (held-out 0.605) | G7 -> 0.446 (0.605)
  noleg_left_s0        G8 ['rhythm', 'torso', 'legs', 'arms'] fit 0.830 -> 0.654 (held-out 0.345) | G7 -> 0.659 (0.358)
  short_shank_left_s0  G8 ['legs', 'legs', 'rhythm', 'torso', 'stiff+1', 'torso', 'legs'] fit 0.446 -> 0.296 (held-out 0.392) | G7 -> 0.308 (0.395)
  weak_hip_right_s0    G8 ['lateral', 'torso', 'lateral'] fit 0.557 -> 0.384 (held-out 0.431) | G7 -> 0.384 (0.431)
  short_shank_right_s0 G8 ['legs'] fit 0.484 -> 0.351 (held-out 0.489) | G7 -> 0.351 (0.489)
  locked_knee_right_s0 G8 ['rhythm', 'torso', 'legs', 'stiff+1', 'legs', 'hold-1', 'limp+1'] fit 0.612 -> 0.425 (held-out 0.507) | G7 -> 0.396 (0.488)
  noleg_right_s0       G8 ['rhythm', 'legs', 'rhythm', 'arms', 'lateral', 'legs', 'vault', 'weak-1'] fit 0.619 -> 0.273 (held-out 0.353) | G7 -> 0.309 (0.349)
  stump_right_s0       G8 ['lateral', 'arms', 'vault', 'rhythm', 'hold+1'] fit 0.747 -> 0.317 (held-out 0.424) | G7 -> 0.317 (0.424)
  intact_s1            G8 ['torso', 'arms', 'legs', 'lateral', 'legs'] fit 0.378 -> 0.274 (held-out 0.339) | G7 -> 0.274 (0.339)
  terminal below G7's on 3 of 13 cases (fitting), 3 of 13 (held-out mean)

## Outcome (frozen tree): K1 fail, K4 pass -> C; K2 pass, K3 pass
