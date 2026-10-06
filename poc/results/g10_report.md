# G10 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps, 

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G10 ['limp-1', 'legs', 'stiff-1', 'limp-1'] | G9 ['stiff-1', 'legs', 'torso', 'arms', 'limp-1', 'lateral']
  stump_left_s0        designed limp-1  G10 ['rhythm', 'weak-1', 'torso'] | G9 ['torso', 'legs', 'rhythm', 'legs', 'torso']
  nolegs_s0            designed vault+0  G10 [] | G9 ['arms', 'rhythm']
  locked_knee_right_s0 designed stiff+1  G10 ['rhythm', 'stiff+1', 'arms'] | G9 ['legs', 'limp+1', 'torso']
  stump_right_s0       designed limp+1  G10 ['rhythm', 'torso', 'lateral', 'torso', 'stiff+1', 'weak+1'] | G9 ['torso', 'lateral', 'torso', 'rhythm', 'arms']
-> K1 FAIL: first 0 of 3 (>= 2), within two 1 of 3 (>= 3), mirrors 1 of 2 (>= 2)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.600 -> 0.540 | held-out mean 0.461 -> 0.374, runs 0.470->0.372, 0.452->0.376 (2 of 2 lower)
  stump_left_s0        fit 0.623 -> 0.528 | held-out mean 0.483 -> 0.445, runs 0.388->0.401, 0.578->0.489 (1 of 2 lower)
  noleg_left_s0        fit 0.354 -> 0.295 | held-out mean 0.527 -> 0.501, runs 0.665->0.651, 0.390->0.351 (2 of 2 lower)
  nolegs_s0            fit 0.666 -> 0.666 | held-out mean 0.579 -> 0.579, runs 0.580->0.580, 0.578->0.578 (0 of 2 lower)
  short_shank_left_s0  fit 0.494 -> 0.307 | held-out mean 0.561 -> 0.484, runs 0.558->0.510, 0.564->0.457 (2 of 2 lower)
  locked_knee_right_s0 fit 0.580 -> 0.406 | held-out mean 0.686 -> 0.600, runs 0.635->0.574, 0.737->0.626 (2 of 2 lower)
  short_shank_right_s0 fit 0.547 -> 0.443 | held-out mean 0.471 -> 0.442, runs 0.501->0.388, 0.441->0.496 (1 of 2 lower)
  stump_right_s0       fit 0.422 -> 0.263 | held-out mean 0.529 -> 0.476, runs 0.442->0.385, 0.615->0.568 (2 of 2 lower)
  noleg_right_s0       fit 0.376 -> 0.220 | held-out mean 0.376 -> 0.338, runs 0.367->0.308, 0.384->0.368 (2 of 2 lower)
-> K4 pass: 8 of 9 (>= 7); both runs lower on 6 of 9

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  worse: asym_stance, height, reach
  stump_left_s0        worse: contact_t, stance, joint_stats, lateral
  noleg_left_s0        worse: height
  nolegs_s0            none worse
  short_shank_left_s0  worse: coupling
  locked_knee_right_s0 worse: lateral, pose_phase
  short_shank_right_s0 worse: coupling, reach
  stump_right_s0       worse: height
  noleg_right_s0       worse: asym_joints, height, rhythm
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); none worse at all on 1 of 9

## K3 controls: impairment repairs added, in total
  weak_hip_left_s0     ['torso', 'torso', 'stiff+1'] (0.356 -> 0.300, held-out mean 0.448 -> 0.426)
  intact_s0            ['torso', 'rhythm', 'weak-1', 'arms'] (0.322 -> 0.273, held-out mean 0.632 -> 0.624)
  weak_hip_right_s0    ['lateral'] (0.390 -> 0.361, held-out mean 0.421 -> 0.352)
  intact_s1            ['lateral', 'rhythm', 'arms'] (0.783 -> 0.302, held-out mean 0.402 -> 0.374)
-> K3 pass: 2 impairment repairs on 4 controls (<= 4)

## Reported
  repairs applied per case, median 3; rejections by reason {'held-out': 66, 'spent': 91, 'guard': 4}
  applied repairs lowering both held-out runs 25 of 42, one run 17
  value of the applied repair against the best fitting drop, median 0.70
  weak_hip_left_s0     G10 ['torso', 'torso', 'stiff+1'] fit 0.356 -> 0.300 (held-out 0.426) | G9 -> 0.306 (0.336)
  intact_s0            G10 ['torso', 'rhythm', 'weak-1', 'arms'] fit 0.322 -> 0.273 (held-out 0.624) | G9 -> 0.309 (0.364)
  locked_knee_left_s0  G10 ['limp-1', 'legs', 'stiff-1', 'limp-1'] fit 0.600 -> 0.540 (held-out 0.374) | G9 -> 0.334 (0.385)
  stump_left_s0        G10 ['rhythm', 'weak-1', 'torso'] fit 0.623 -> 0.528 (held-out 0.445) | G9 -> 0.250 (0.441)
  noleg_left_s0        G10 ['torso', 'legs', 'arms'] fit 0.354 -> 0.295 (held-out 0.501) | G9 -> 0.507 (0.373)
  nolegs_s0            G10 [] fit 0.666 -> 0.666 (held-out 0.579) | G9 -> 0.517 (0.659)
  short_shank_left_s0  G10 ['limp-1', 'torso', 'arms', 'legs'] fit 0.494 -> 0.307 (held-out 0.484) | G9 -> 0.337 (0.423)
  weak_hip_right_s0    G10 ['lateral'] fit 0.390 -> 0.361 (held-out 0.352) | G9 -> 0.376 (0.430)
  locked_knee_right_s0 G10 ['rhythm', 'stiff+1', 'arms'] fit 0.580 -> 0.406 (held-out 0.600) | G9 -> 0.499 (0.586)
  short_shank_right_s0 G10 ['legs', 'stiff+1', 'limp+1'] fit 0.547 -> 0.443 (held-out 0.442) | G9 -> 0.346 (0.443)
  stump_right_s0       G10 ['rhythm', 'torso', 'lateral', 'torso', 'stiff+1', 'weak+1'] fit 0.422 -> 0.263 (held-out 0.476) | G9 -> 0.265 (0.420)
  noleg_right_s0       G10 ['rhythm', 'torso', 'legs', 'lateral', 'arms'] fit 0.376 -> 0.220 (held-out 0.338) | G9 -> 0.285 (0.359)
  intact_s1            G10 ['lateral', 'rhythm', 'arms'] fit 0.783 -> 0.302 (held-out 0.374) | G9 -> 0.304 (0.378)
  terminal below G9's on 9 of 13 cases (fitting), 6 of 13 (held-out mean)
## K5 (reported) ground speed of the part on the floor, m/s: the terminal state's planted part, and the teacher's parts within 2 cm of the floor
  weak_hip_left_s0     student 0.283   teacher 0.182   (emergent speed 0.36 m/s, teacher 0.41)
  intact_s0            student 0.502   teacher 0.238   (emergent speed 0.46 m/s, teacher 0.42)
  locked_knee_left_s0  student 0.365   teacher 0.166   (emergent speed 0.33 m/s, teacher 0.34)
  stump_left_s0        student 0.332   teacher 0.226   (emergent speed 0.16 m/s, teacher 0.16)
  noleg_left_s0        student 0.331   teacher 0.272   (emergent speed 0.35 m/s, teacher 0.34)
  nolegs_s0            student 0.158   teacher 0.250   (emergent speed 0.18 m/s, teacher 0.44)
  short_shank_left_s0  student 0.390   teacher 0.284   (emergent speed 0.34 m/s, teacher 0.33)
  weak_hip_right_s0    student 0.351   teacher 0.202   (emergent speed 0.33 m/s, teacher 0.36)
  locked_knee_right_s0 student 0.348   teacher 0.170   (emergent speed 0.34 m/s, teacher 0.39)
  short_shank_right_s0 student 0.410   teacher 0.202   (emergent speed 0.29 m/s, teacher 0.29)
  stump_right_s0       student 0.322   teacher 0.176   (emergent speed 0.25 m/s, teacher 0.24)
  noleg_right_s0       student 0.412   teacher 0.313   (emergent speed 0.28 m/s, teacher 0.29)
  intact_s1            student 0.358   teacher 0.223   (emergent speed 0.28 m/s, teacher 0.32)

## Outcome (frozen tree): K1 fail, K4 pass -> C; K2 pass, K3 pass; K5 reported
