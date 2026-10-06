# G9 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps, 

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G9 ['stiff-1', 'legs', 'torso', 'arms', 'limp-1', 'lateral'] | G7 ['stiff-1', 'rhythm', 'arms', 'legs', 'rhythm', 'torso']
  nolegs_s0            designed vault+0  G9 ['arms', 'rhythm'] | G7 ['arms', 'torso']
  stump_left_s0        designed limp-1  G9 ['torso', 'legs', 'rhythm', 'legs', 'torso'] | G7 ['torso', 'arms', 'limp-1', 'legs']
  locked_knee_right_s0 designed stiff+1  G9 ['legs', 'limp+1', 'torso'] | G7 ['stiff+1', 'torso', 'rhythm', 'hold-1', 'legs']
  stump_right_s0       designed limp+1  G9 ['torso', 'lateral', 'torso', 'rhythm', 'arms'] | G7 ['lateral', 'arms', 'vault', 'rhythm', 'hold+1']
-> K1 FAIL: first 1 of 3 (>= 2), within two 1 of 3 (>= 3), mirrors 0 of 2 (>= 2)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.629 -> 0.334 | held-out mean 0.593 -> 0.385, runs 0.600->0.387, 0.586->0.382 (2 of 2 lower)
  short_shank_left_s0  fit 1.039 -> 0.337 | held-out mean 0.922 -> 0.423, runs 0.939->0.460, 0.904->0.385 (2 of 2 lower)
  nolegs_s0            fit 0.769 -> 0.517 | held-out mean 0.781 -> 0.659, runs 0.780->0.776, 0.782->0.542 (2 of 2 lower)
  stump_left_s0        fit 0.687 -> 0.250 | held-out mean 0.651 -> 0.441, runs 0.655->0.474, 0.646->0.407 (2 of 2 lower)
  noleg_left_s0        fit 0.726 -> 0.507 | held-out mean 0.700 -> 0.373, runs 0.690->0.358, 0.709->0.387 (2 of 2 lower)
  locked_knee_right_s0 fit 0.625 -> 0.499 | held-out mean 0.685 -> 0.586, runs 0.593->0.490, 0.777->0.683 (2 of 2 lower)
  short_shank_right_s0 fit 0.970 -> 0.346 | held-out mean 1.094 -> 0.443, runs 1.010->0.526, 1.179->0.360 (2 of 2 lower)
  stump_right_s0       fit 0.730 -> 0.265 | held-out mean 0.713 -> 0.420, runs 0.719->0.447, 0.708->0.394 (2 of 2 lower)
  noleg_right_s0       fit 0.680 -> 0.285 | held-out mean 0.697 -> 0.359, runs 0.674->0.360, 0.720->0.359 (2 of 2 lower)
-> K4 pass: 9 of 9 (>= 7); both runs lower on 9 of 9

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  none worse
  short_shank_left_s0  worse: coupling
  nolegs_s0            worse: asym_joints
  stump_left_s0        worse: height
  noleg_left_s0        worse: contact_t, reach | BEYOND tolerance: contact_t
  locked_knee_right_s0 none worse
  short_shank_right_s0 worse: contact_t, asym_joints, height
  stump_right_s0       none worse
  noleg_right_s0       worse: contact_t, asym_joints, height, reach
-> K2 pass: none beyond tolerance on 8 of 9 (>= 7); none worse at all on 3 of 9

## K3 controls: impairment repairs added, in total
  weak_hip_left_s0     ['torso', 'arms', 'limp+1'] (0.424 -> 0.306, held-out mean 0.429 -> 0.336)
  intact_s0            ['arms', 'torso', 'lateral'] (0.354 -> 0.309, held-out mean 0.409 -> 0.364)
  weak_hip_right_s0    ['rhythm', 'lateral', 'arms'] (0.577 -> 0.376, held-out mean 0.499 -> 0.430)
  intact_s1            ['hold-1', 'rhythm'] (0.378 -> 0.304, held-out mean 0.397 -> 0.378)
-> K3 pass: 2 impairment repairs on 4 controls (<= 4)

## Reported
  repairs applied per case, median 3; rejections by reason {'guard': 16, 'held-out': 52, 'spent': 69}
  applied repairs lowering both held-out runs 35 of 49, one run 14
  value of the applied repair against the best fitting drop, median 0.82
  weak_hip_left_s0     G9 ['torso', 'arms', 'limp+1'] fit 0.424 -> 0.306 (held-out 0.336) | G7 -> 0.255 (0.383)
  intact_s0            G9 ['arms', 'torso', 'lateral'] fit 0.354 -> 0.309 (held-out 0.364) | G7 -> 0.299 (0.326)
  locked_knee_left_s0  G9 ['stiff-1', 'legs', 'torso', 'arms', 'limp-1', 'lateral'] fit 0.629 -> 0.334 (held-out 0.385) | G7 -> 0.272 (0.384)
  short_shank_left_s0  G9 ['rhythm', 'torso', 'limp+1'] fit 1.039 -> 0.337 (held-out 0.423) | G7 -> 0.308 (0.395)
  nolegs_s0            G9 ['arms', 'rhythm'] fit 0.769 -> 0.517 (held-out 0.659) | G7 -> 0.446 (0.605)
  stump_left_s0        G9 ['torso', 'legs', 'rhythm', 'legs', 'torso'] fit 0.687 -> 0.250 (held-out 0.441) | G7 -> 0.274 (0.428)
  noleg_left_s0        G9 ['vault', 'legs', 'rhythm', 'legs', 'arms', 'limp+1'] fit 0.726 -> 0.507 (held-out 0.373) | G7 -> 0.659 (0.358)
  weak_hip_right_s0    G9 ['rhythm', 'lateral', 'arms'] fit 0.577 -> 0.376 (held-out 0.430) | G7 -> 0.384 (0.431)
  locked_knee_right_s0 G9 ['legs', 'limp+1', 'torso'] fit 0.625 -> 0.499 (held-out 0.586) | G7 -> 0.396 (0.488)
  short_shank_right_s0 G9 ['torso', 'legs'] fit 0.970 -> 0.346 (held-out 0.443) | G7 -> 0.351 (0.489)
  intact_s1            G9 ['hold-1', 'rhythm'] fit 0.378 -> 0.304 (held-out 0.378) | G7 -> 0.274 (0.339)
  stump_right_s0       G9 ['torso', 'lateral', 'torso', 'rhythm', 'arms'] fit 0.730 -> 0.265 (held-out 0.420) | G7 -> 0.317 (0.424)
  noleg_right_s0       G9 ['vault', 'arms', 'lateral', 'torso', 'legs', 'vault'] fit 0.680 -> 0.285 (held-out 0.359) | G7 -> 0.309 (0.349)
  terminal below G7's on 6 of 13 cases (fitting), 4 of 13 (held-out mean)
## K5 (reported) ground speed of the part on the floor, m/s: the terminal state's planted part, and the teacher's parts within 2 cm of the floor
  weak_hip_left_s0     student 0.044   teacher 0.194   (emergent speed 0.38 m/s, teacher 0.38)
  intact_s0            student 0.034   teacher 0.269   (emergent speed 0.37 m/s, teacher 0.36)
  locked_knee_left_s0  student 0.025   teacher 0.191   (emergent speed 0.42 m/s, teacher 0.50)
  short_shank_left_s0  student 0.075   teacher 0.259   (emergent speed 0.45 m/s, teacher 0.44)
  nolegs_s0            student 0.077   teacher 0.196   (emergent speed 0.40 m/s, teacher 0.37)
  stump_left_s0        student 0.371   teacher 0.458   (emergent speed 0.49 m/s, teacher 0.50)
  noleg_left_s0        student 0.517   teacher 0.279   (emergent speed 0.30 m/s, teacher 0.32)
  weak_hip_right_s0    student 0.042   teacher 0.172   (emergent speed 0.29 m/s, teacher 0.29)
  locked_knee_right_s0 student 0.029   teacher 0.157   (emergent speed 0.45 m/s, teacher 0.44)
  short_shank_right_s0 student 0.200   teacher 0.173   (emergent speed 0.31 m/s, teacher 0.29)
  intact_s1            student 0.018   teacher 0.315   (emergent speed 0.39 m/s, teacher 0.38)
  stump_right_s0       student 0.352   teacher 0.289   (emergent speed 0.32 m/s, teacher 0.41)
  noleg_right_s0       student 0.232   teacher 0.286   (emergent speed 0.29 m/s, teacher 0.30)

## Outcome (frozen tree): K1 fail, K4 pass -> C; K2 pass, K3 pass; K5 reported
