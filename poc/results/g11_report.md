# G11 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps, 

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G11 ['rhythm', 'arms'] | G10 ['limp-1', 'legs', 'stiff-1', 'limp-1']
  nolegs_s0            designed vault+0  G11 ['arms'] | G10 []
  stump_left_s0        designed limp-1  G11 ['vault', 'weak-1', 'arms', 'legs'] | G10 ['rhythm', 'weak-1', 'torso']
  locked_knee_right_s0 designed stiff+1  G11 ['weak+1', 'stiff+1', 'arms', 'rhythm', 'stiff+1'] | G10 ['rhythm', 'stiff+1', 'arms']
  stump_right_s0       designed limp+1  G11 ['vault', 'rhythm', 'arms', 'lateral', 'legs', 'weak-1'] | G10 ['rhythm', 'torso', 'lateral', 'torso', 'stiff+1', 'weak+1']
-> K1 FAIL: first 0 of 3 (>= 2), within two 0 of 3 (>= 3), mirrors 1 of 2 (>= 2)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.666 -> 0.594 | held-out mean 0.585 -> 0.484, runs 0.575->0.490, 0.594->0.477 (2 of 2 lower)
  short_shank_left_s0  fit 0.987 -> 0.384 | held-out mean 1.160 -> 0.628, runs 1.208->0.701, 1.113->0.554 (2 of 2 lower)
  nolegs_s0            fit 0.885 -> 0.595 | held-out mean 0.717 -> 0.561, runs 0.726->0.575, 0.709->0.547 (2 of 2 lower)
  stump_left_s0        fit 0.842 -> 0.519 | held-out mean 0.711 -> 0.469, runs 0.725->0.442, 0.697->0.497 (2 of 2 lower)
  noleg_left_s0        fit 0.767 -> 0.388 | held-out mean 0.813 -> 0.636, runs 0.887->0.840, 0.740->0.431 (2 of 2 lower)
  locked_knee_right_s0 fit 0.629 -> 0.416 | held-out mean 0.789 -> 0.635, runs 0.721->0.602, 0.857->0.668 (2 of 2 lower)
  short_shank_right_s0 fit 0.934 -> 0.500 | held-out mean 1.020 -> 0.461, runs 1.007->0.449, 1.033->0.473 (2 of 2 lower)
  stump_right_s0       fit 0.746 -> 0.290 | held-out mean 0.816 -> 0.637, runs 0.822->0.420, 0.810->0.854 (1 of 2 lower)
  noleg_right_s0       fit 0.732 -> 0.590 | held-out mean 0.732 -> 0.677, runs 0.718->0.695, 0.746->0.658 (2 of 2 lower)
-> K4 pass: 9 of 9 (>= 7); both runs lower on 8 of 9

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  worse: contact_t, travel, asym_joints, asym_stance, orient
  short_shank_left_s0  worse: coupling
  nolegs_s0            worse: contact_t, asym_joints, asym_stance, height
  stump_left_s0        worse: height, rhythm
  noleg_left_s0        worse: contact_t, asym_joints, height, orient, reach
  locked_knee_right_s0 worse: speed, height, orient, lateral, rhythm
  short_shank_right_s0 worse: coupling
  stump_right_s0       worse: height, reach
  noleg_right_s0       worse: height, rhythm, reach
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); none worse at all on 0 of 9

## K3 controls: impairment repairs added, in total
  intact_s0            ['arms', 'legs'] (0.340 -> 0.297, held-out mean 0.728 -> 0.715)
  weak_hip_left_s0     ['arms', 'lateral', 'legs', 'torso', 'limp+1'] (0.398 -> 0.329, held-out mean 0.485 -> 0.436)
  weak_hip_right_s0    ['arms', 'lateral'] (0.479 -> 0.417, held-out mean 0.485 -> 0.389)
  intact_s1            ['lateral', 'rhythm', 'arms', 'legs', 'weak+1', 'lateral'] (0.879 -> 0.321, held-out mean 0.458 -> 0.391)
-> K3 pass: 2 impairment repairs on 4 controls (<= 4)

## Reported
  repairs applied per case, median 4; rejections by reason {'held-out': 37, 'spent': 82, 'guard': 15}
  applied repairs lowering both held-out runs 29 of 46, one run 17
  value of the applied repair against the best fitting drop, median 1.00
  intact_s0            G11 ['arms', 'legs'] fit 0.340 -> 0.297 (held-out 0.715) | G10 -> 0.273 (0.624)
  locked_knee_left_s0  G11 ['rhythm', 'arms'] fit 0.666 -> 0.594 (held-out 0.484) | G10 -> 0.540 (0.374)
  weak_hip_left_s0     G11 ['arms', 'lateral', 'legs', 'torso', 'limp+1'] fit 0.398 -> 0.329 (held-out 0.436) | G10 -> 0.300 (0.426)
  short_shank_left_s0  G11 ['limp-1', 'arms'] fit 0.987 -> 0.384 (held-out 0.628) | G10 -> 0.307 (0.484)
  nolegs_s0            G11 ['arms'] fit 0.885 -> 0.595 (held-out 0.561) | G10 -> 0.666 (0.579)
  stump_left_s0        G11 ['vault', 'weak-1', 'arms', 'legs'] fit 0.842 -> 0.519 (held-out 0.469) | G10 -> 0.528 (0.445)
  noleg_left_s0        G11 ['torso', 'arms', 'hold+1'] fit 0.767 -> 0.388 (held-out 0.636) | G10 -> 0.295 (0.501)
  weak_hip_right_s0    G11 ['arms', 'lateral'] fit 0.479 -> 0.417 (held-out 0.389) | G10 -> 0.361 (0.352)
  locked_knee_right_s0 G11 ['weak+1', 'stiff+1', 'arms', 'rhythm', 'stiff+1'] fit 0.629 -> 0.416 (held-out 0.635) | G10 -> 0.406 (0.600)
  short_shank_right_s0 G11 ['limp+1', 'arms', 'lateral', 'weak-1'] fit 0.934 -> 0.500 (held-out 0.461) | G10 -> 0.443 (0.442)
  stump_right_s0       G11 ['vault', 'rhythm', 'arms', 'lateral', 'legs', 'weak-1'] fit 0.746 -> 0.290 (held-out 0.637) | G10 -> 0.263 (0.476)
  noleg_right_s0       G11 ['rhythm', 'torso', 'arms', 'lateral'] fit 0.732 -> 0.590 (held-out 0.677) | G10 -> 0.220 (0.338)
  intact_s1            G11 ['lateral', 'rhythm', 'arms', 'legs', 'weak+1', 'lateral'] fit 0.879 -> 0.321 (held-out 0.391) | G10 -> 0.302 (0.374)
  terminal below G10's on 2 of 13 cases (fitting), 1 of 13 (held-out mean)
## K5 (reported) ground speed of the part on the floor, m/s: the terminal state's planted part, and the teacher's parts within 2 cm of the floor
  intact_s0            student 0.062   teacher 0.238   (emergent speed 0.37 m/s, teacher 0.42)
  locked_knee_left_s0  student 0.024   teacher 0.166   (emergent speed 0.33 m/s, teacher 0.34)
  weak_hip_left_s0     student 0.277   teacher 0.182   (emergent speed 0.43 m/s, teacher 0.41)
  short_shank_left_s0  student 0.025   teacher 0.284   (emergent speed 0.34 m/s, teacher 0.33)
  nolegs_s0            student 0.010   teacher 0.250   (emergent speed 0.41 m/s, teacher 0.44)
  stump_left_s0        student 0.069   teacher 0.226   (emergent speed 0.15 m/s, teacher 0.16)
  noleg_left_s0        student 0.421   teacher 0.272   (emergent speed 0.30 m/s, teacher 0.34)
  weak_hip_right_s0    student 0.043   teacher 0.202   (emergent speed 0.35 m/s, teacher 0.36)
  locked_knee_right_s0 student 0.069   teacher 0.170   (emergent speed 0.29 m/s, teacher 0.39)
  short_shank_right_s0 student 0.024   teacher 0.202   (emergent speed 0.25 m/s, teacher 0.29)
  stump_right_s0       student 0.344   teacher 0.176   (emergent speed 0.23 m/s, teacher 0.24)
  noleg_right_s0       student 0.000   teacher 0.313   (emergent speed 0.27 m/s, teacher 0.29)
  intact_s1            student 0.011   teacher 0.223   (emergent speed 0.32 m/s, teacher 0.32)
## K6 (reported) foot travel at the terminal: forward speed of each foot while off the floor (m/s) and step length between touchdowns (m), student / teacher
  intact_s0            foot_l swing 1.61/1.65 step 0.30/0.15; foot_r swing 1.26/1.00 step 0.20/0.12   (travel block error 0.15, V0 0.24)
  locked_knee_left_s0  foot_l swing 1.13/1.90 step 0.17/0.26; foot_r swing 0.99/0.99 step 0.21/0.21   (travel block error 0.35, V0 0.26)
  weak_hip_left_s0     foot_l swing 1.43/1.07 step 0.32/0.27; foot_r swing 1.45/1.55 step 0.34/0.30   (travel block error 0.20, V0 0.25)
  short_shank_left_s0  foot_l swing 0.71/0.96 step 0.43/0.22; foot_r swing 0.93/0.88 step 0.42/0.21   (travel block error 0.26, V0 1.07)
  nolegs_s0            hand_l swing 0.67/1.67 step 0.45/0.34; hand_r swing 0.59/0.58 step 0.49/0.86   (travel block error 0.54, V0 0.72)
  stump_left_s0        foot_r swing 0.80/0.69 step 0.28/0.14   (travel block error 0.34, V0 1.09)
  noleg_left_s0        foot_r swing 0.86/1.33 step 0.14/0.31   (travel block error 0.34, V0 1.03)
  weak_hip_right_s0    foot_l swing 1.59/1.59 step 0.29/0.25; foot_r swing 1.44/1.24 step 0.22/0.17   (travel block error 0.12, V0 0.10)
  locked_knee_right_s0 foot_l swing 0.73/1.25 step 0.20/0.24; foot_r swing 1.77/3.17 step 0.40/1.30   (travel block error 0.47, V0 0.55)
  short_shank_right_s0 foot_l swing 0.79/0.36 step 0.36/0.07; foot_r swing 1.03/0.91 step 0.38/0.21   (travel block error 0.50, V0 0.96)
  stump_right_s0       foot_l swing 1.48/1.77 step 0.64/0.24   (travel block error 0.28, V0 1.00)
  noleg_right_s0       foot_l swing 0.00/0.69 step 0.00/0.16   (travel block error 0.84, V0 1.01)
  intact_s1            foot_l swing 1.04/0.84 step 0.57/0.22; foot_r swing 1.01/1.16 step 0.24/0.16   (travel block error 0.29, V0 0.53)

## Outcome (frozen tree): K1 fail, K4 pass -> C; K2 pass, K3 pass; K5, K6 reported
