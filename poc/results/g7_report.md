# G7 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  ['stiff-1', 'rhythm', 'arms', 'legs', 'rhythm', 'torso']
  stump_left_s0        designed limp-1  ['torso', 'arms', 'limp-1', 'legs']
  nolegs_s0            designed vault+0  ['arms', 'torso']
  locked_knee_right_s0 designed stiff+1  ['stiff+1', 'torso', 'rhythm', 'hold-1', 'legs']
  stump_right_s0       designed limp+1  ['lateral', 'arms', 'vault', 'rhythm', 'hold+1']
-> K1 FAIL: first 2 of 3 (>= 2), within two 2 of 3 (>= 3), mirrors 1 of 2 (>= 2)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.568 -> 0.272 | held-out mean 0.565 -> 0.384, runs 0.584->0.368, 0.545->0.400 (2 of 2 lower)
  stump_left_s0        fit 0.676 -> 0.274 | held-out mean 0.647 -> 0.428, runs 0.630->0.440, 0.663->0.417 (2 of 2 lower)
  short_shank_left_s0  fit 0.446 -> 0.308 | held-out mean 0.487 -> 0.395, runs 0.554->0.481, 0.421->0.310 (2 of 2 lower)
  nolegs_s0            fit 0.657 -> 0.446 | held-out mean 0.717 -> 0.605, runs 0.761->0.740, 0.672->0.471 (2 of 2 lower)
  noleg_left_s0        fit 0.830 -> 0.659 | held-out mean 0.676 -> 0.358, runs 0.671->0.362, 0.680->0.355 (2 of 2 lower)
  short_shank_right_s0 fit 0.484 -> 0.351 | held-out mean 0.534 -> 0.489, runs 0.608->0.552, 0.461->0.427 (2 of 2 lower)
  locked_knee_right_s0 fit 0.612 -> 0.396 | held-out mean 0.681 -> 0.488, runs 0.570->0.307, 0.792->0.670 (2 of 2 lower)
  stump_right_s0       fit 0.747 -> 0.317 | held-out mean 0.678 -> 0.424, runs 0.652->0.474, 0.705->0.374 (2 of 2 lower)
  noleg_right_s0       fit 0.619 -> 0.309 | held-out mean 0.629 -> 0.349, runs 0.618->0.351, 0.640->0.347 (2 of 2 lower)
-> K4 pass: 9 of 9 (>= 7); both runs lower on 9 of 9

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  none worse
  stump_left_s0        worse: height
  short_shank_left_s0  worse: asym_joints, height, reach
  nolegs_s0            worse: asym_joints
  noleg_left_s0        worse: contact_t, asym_joints, orient
  short_shank_right_s0 none worse
  locked_knee_right_s0 worse: contact_t
  stump_right_s0       worse: coupling, asym_joints, height, orient
  noleg_right_s0       worse: contact_t, height
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); none worse at all on 2 of 9

## K3 controls: impairment repairs added, in total
  weak_hip_left_s0     ['torso', 'lateral', 'arms'] (0.364 -> 0.255, held-out mean 0.421 -> 0.383)
  intact_s0            ['legs', 'lateral', 'arms', 'torso'] (0.331 -> 0.299, held-out mean 0.392 -> 0.326)
  weak_hip_right_s0    ['lateral', 'torso', 'lateral'] (0.557 -> 0.384, held-out mean 0.473 -> 0.431)
  intact_s1            ['torso', 'arms', 'legs', 'lateral', 'legs'] (0.378 -> 0.274, held-out mean 0.368 -> 0.339)
-> K3 pass: 0 impairment repairs on 4 controls (<= 4)

## Reported
  repairs applied per case, median 4; rejections by reason {'spent': 85, 'held-out': 70, 'guard': 3}
  applied repairs lowering both held-out runs 35 of 50, one run 15
  value of the applied repair against the best fitting drop, median 1.00
  weak_hip_left_s0     ['torso', 'lateral', 'arms'] fit 0.364 -> 0.255
  intact_s0            ['legs', 'lateral', 'arms', 'torso'] fit 0.331 -> 0.299
  locked_knee_left_s0  ['stiff-1', 'rhythm', 'arms', 'legs', 'rhythm', 'torso'] fit 0.568 -> 0.272
  stump_left_s0        ['torso', 'arms', 'limp-1', 'legs'] fit 0.676 -> 0.274
  short_shank_left_s0  ['legs', 'vault', 'torso', 'legs'] fit 0.446 -> 0.308
  nolegs_s0            ['arms', 'torso'] fit 0.657 -> 0.446
  noleg_left_s0        ['stiff+1', 'torso', 'arms', 'rhythm'] fit 0.830 -> 0.659
  short_shank_right_s0 ['legs'] fit 0.484 -> 0.351
  weak_hip_right_s0    ['lateral', 'torso', 'lateral'] fit 0.557 -> 0.384
  locked_knee_right_s0 ['stiff+1', 'torso', 'rhythm', 'hold-1', 'legs'] fit 0.612 -> 0.396
  stump_right_s0       ['lateral', 'arms', 'vault', 'rhythm', 'hold+1'] fit 0.747 -> 0.317
  noleg_right_s0       ['vault', 'rhythm', 'arms', 'torso'] fit 0.619 -> 0.309
  intact_s1            ['torso', 'arms', 'legs', 'lateral', 'legs'] fit 0.378 -> 0.274

## Outcome (frozen tree): K1 fail, K4 pass -> C; K2 pass, K3 pass
