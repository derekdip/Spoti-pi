# G13 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G13 ['limp-1'] | G11 ['rhythm', 'arms']
  nolegs_s0            designed vault+0  G13 ['torso'] | G11 ['arms']
  stump_left_s0        designed limp-1  G13 ['rhythm', 'vault'] | G11 ['vault', 'weak-1', 'arms', 'legs']
  locked_knee_right_s0 designed stiff+1  G13 ['stiff+1', 'legs', 'stiff+1'] | G11 ['weak+1', 'stiff+1', 'arms', 'rhythm', 'stiff+1']
  stump_right_s0       designed limp+1  G13 ['lateral', 'rhythm'] | G11 ['vault', 'rhythm', 'arms', 'lateral', 'legs', 'weak-1']
-> K1 FAIL: first 0 of 3 (>= 2), within two 0 of 3 (>= 3), mirrors 1 of 2 (>= 2)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.581 -> 0.420 | held-out mean 0.671 -> 0.555, runs 0.602->0.522, 0.741->0.587 (2 of 2 lower)
  short_shank_left_s0  fit 0.573 -> 0.499 | held-out mean 0.680 -> 0.521, runs 0.698->0.554, 0.662->0.488 (2 of 2 lower)
  nolegs_s0            fit 0.834 -> 0.802 | held-out mean 1.017 -> 1.000, runs 1.028->1.012, 1.006->0.988 (2 of 2 lower)
  stump_left_s0        fit 0.815 -> 0.584 | held-out mean 0.797 -> 0.553, runs 0.537->0.496, 1.057->0.611 (2 of 2 lower)
  noleg_left_s0        fit 0.479 -> 0.319 | held-out mean 0.748 -> 0.580, runs 0.967->0.760, 0.530->0.400 (2 of 2 lower)
  short_shank_right_s0 fit 0.630 -> 0.630 | held-out mean 0.569 -> 0.569, runs 0.615->0.615, 0.523->0.523 (0 of 2 lower)
  locked_knee_right_s0 fit 0.717 -> 0.450 | held-out mean 0.630 -> 0.480, runs 0.657->0.521, 0.603->0.439 (2 of 2 lower)
  stump_right_s0       fit 0.437 -> 0.365 | held-out mean 0.650 -> 0.609, runs 0.403->0.440, 0.897->0.779 (1 of 2 lower)
  noleg_right_s0       fit 0.535 -> 0.337 | held-out mean 0.442 -> 0.414, runs 0.449->0.423, 0.435->0.405 (2 of 2 lower)
-> K4 pass: 8 of 9 (>= 7); both runs lower on 7 of 9

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  worse: contact_t, coupling, speed, height, orient, lateral, reach
  short_shank_left_s0  worse: contact_t, coupling, stance, joint_stats, height, lateral, reach
  nolegs_s0            worse: travel
  stump_left_s0        worse: stance, joint_stats, height, orient, lateral, reach, pose_phase
  noleg_left_s0        worse: joint_stats, height
  short_shank_right_s0 none worse
  locked_knee_right_s0 worse: contact_t, joint_stats, speed, height
  stump_right_s0       worse: travel, joint_stats, asym_joints, orient, reach, pose_phase
  noleg_right_s0       worse: joint_stats
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); none worse at all on 1 of 9

## K3 controls: impairment repairs added, in total
  intact_s0            ['legs', 'rhythm'] (0.443 -> 0.327, held-out mean 0.511 -> 0.394)
  weak_hip_left_s0     ['torso', 'hold+1', 'weak-1', 'lateral'] (0.501 -> 0.262, held-out mean 0.560 -> 0.496)
  weak_hip_right_s0    ['weak-1'] (0.613 -> 0.434, held-out mean 0.426 -> 0.378)
  intact_s1            ['legs', 'lateral'] (0.504 -> 0.352, held-out mean 0.480 -> 0.399)
-> K3 pass: 3 impairment repairs on 4 controls (<= 4)

## Reported
  repairs applied per case, median 2; rejections by reason {'spent': 89, 'held-out': 62, 'guard': 6}
  applied repairs lowering both held-out runs 18 of 27, one run 9
  value of the applied repair against the best fitting drop, median 0.78
  locked_knee_left_s0  G13 ['limp-1'] fit 0.581 -> 0.420 (held-out 0.555) | G11 -> 0.594 (0.484)
  intact_s0            G13 ['legs', 'rhythm'] fit 0.443 -> 0.327 (held-out 0.394) | G11 -> 0.297 (0.715)
  short_shank_left_s0  G13 ['weak+1'] fit 0.573 -> 0.499 (held-out 0.521) | G11 -> 0.384 (0.628)
  weak_hip_left_s0     G13 ['torso', 'hold+1', 'weak-1', 'lateral'] fit 0.501 -> 0.262 (held-out 0.496) | G11 -> 0.329 (0.436)
  nolegs_s0            G13 ['torso'] fit 0.834 -> 0.802 (held-out 1.000) | G11 -> 0.595 (0.561)
  stump_left_s0        G13 ['rhythm', 'vault'] fit 0.815 -> 0.584 (held-out 0.553) | G11 -> 0.519 (0.469)
  weak_hip_right_s0    G13 ['weak-1'] fit 0.613 -> 0.434 (held-out 0.378) | G11 -> 0.417 (0.389)
  noleg_left_s0        G13 ['lateral', 'weak+1', 'arms'] fit 0.479 -> 0.319 (held-out 0.580) | G11 -> 0.388 (0.636)
  short_shank_right_s0 G13 [] fit 0.630 -> 0.630 (held-out 0.569) | G11 -> 0.500 (0.461)
  locked_knee_right_s0 G13 ['stiff+1', 'legs', 'stiff+1'] fit 0.717 -> 0.450 (held-out 0.480) | G11 -> 0.416 (0.635)
  stump_right_s0       G13 ['lateral', 'rhythm'] fit 0.437 -> 0.365 (held-out 0.609) | G11 -> 0.290 (0.637)
  intact_s1            G13 ['legs', 'lateral'] fit 0.504 -> 0.352 (held-out 0.399) | G11 -> 0.321 (0.391)
  noleg_right_s0       G13 ['lateral', 'weak+1', 'weak+1', 'legs', 'weak+1'] fit 0.535 -> 0.337 (held-out 0.414) | G11 -> 0.590 (0.677)
  terminal below G11's on 4 of 13 cases (fitting), 7 of 13 (held-out mean)
## K5 (reported) ground speed of the part on the floor, m/s: the terminal state's planted part, and the teacher's parts within 2 cm of the floor
  locked_knee_left_s0  student 0.424   teacher 0.166   (emergent speed 0.41 m/s, teacher 0.34)
  intact_s0            student 0.678   teacher 0.238   (emergent speed 0.37 m/s, teacher 0.42)
  short_shank_left_s0  student 0.870   teacher 0.284   (emergent speed 0.37 m/s, teacher 0.33)
  weak_hip_left_s0     student 0.844   teacher 0.182   (emergent speed 0.46 m/s, teacher 0.41)
  nolegs_s0            student nan   teacher 0.250   (emergent speed 0.40 m/s, teacher 0.44)
  stump_left_s0        student 0.494   teacher 0.226   (emergent speed 0.21 m/s, teacher 0.16)
  weak_hip_right_s0    student 0.298   teacher 0.202   (emergent speed 0.41 m/s, teacher 0.36)
  noleg_left_s0        student 0.825   teacher 0.272   (emergent speed 0.39 m/s, teacher 0.34)
  short_shank_right_s0 student 0.360   teacher 0.202   (emergent speed 0.40 m/s, teacher 0.29)
  locked_knee_right_s0 student 0.859   teacher 0.170   (emergent speed 0.44 m/s, teacher 0.39)
  stump_right_s0       student 0.278   teacher 0.176   (emergent speed 0.31 m/s, teacher 0.24)
  intact_s1            student 0.606   teacher 0.223   (emergent speed 0.36 m/s, teacher 0.32)
  noleg_right_s0       student 0.673   teacher 0.313   (emergent speed 0.35 m/s, teacher 0.29)
## K6 (reported) foot travel at the terminal: forward speed of each foot while off the floor (m/s) and step length between touchdowns (m), student / teacher
  locked_knee_left_s0  foot_l swing 1.44/1.90 step 0.23/0.26; foot_r swing 0.32/0.99 step 0.21/0.21   (travel block error 0.37, V0 0.45)
  intact_s0            foot_l swing 1.13/1.65 step 0.18/0.15; foot_r swing 0.63/1.00 step 0.15/0.12   (travel block error 0.31, V0 0.44)
  short_shank_left_s0  foot_l swing 0.36/0.96 step 0.00/0.22; foot_r swing 0.34/0.88 step 0.26/0.21   (travel block error 0.56, V0 0.68)
  weak_hip_left_s0     foot_l swing 1.06/1.07 step 0.44/0.27; foot_r swing 1.24/1.55 step 0.32/0.30   (travel block error 0.18, V0 0.70)
  nolegs_s0            hand_l swing 0.37/1.67 step 0.00/0.34; hand_r swing 0.25/0.58 step 0.00/0.86   (travel block error 0.82, V0 0.78)
  stump_left_s0        foot_r swing 0.51/0.69 step 0.16/0.14   (travel block error 0.32, V0 0.95)
  weak_hip_right_s0    foot_l swing 1.62/1.59 step 0.39/0.25; foot_r swing 0.35/1.24 step 0.22/0.17   (travel block error 0.42, V0 0.52)
  noleg_left_s0        foot_r swing 1.08/1.33 step 0.37/0.31   (travel block error 0.17, V0 0.85)
  short_shank_right_s0 foot_l swing 1.62/0.36 step 0.38/0.07; foot_r swing 0.39/0.91 step 0.00/0.21   (travel block error 1.26, V0 1.26)
  locked_knee_right_s0 foot_l swing 0.59/1.25 step 0.23/0.24; foot_r swing 0.58/3.17 step 0.42/1.30   (travel block error 0.75, V0 0.87)
  stump_right_s0       foot_l swing 1.36/1.77 step 0.36/0.24   (travel block error 0.25, V0 0.21)
  intact_s1            foot_l swing 0.87/0.84 step 0.18/0.22; foot_r swing 0.85/1.16 step 0.19/0.16   (travel block error 0.23, V0 0.75)
  noleg_right_s0       foot_l swing 0.81/0.69 step 0.21/0.16   (travel block error 0.20, V0 1.14)
## K7 (reported) reach of the edits: held-out error raw clip -> terminal per run, G11's parametric terminal, and the terminal's speed and airborne fraction against the teacher's
  locked_knee_left_s0  walking      held-out raw 0.671 -> terminal 0.555 (runs 0.602->0.522, 0.741->0.587) | G11 parametric 0.484 | speed 0.41 / 0.34 m/s, airborne 0.00 / 0.00; edits ['limp-1']
  short_shank_left_s0  walking      held-out raw 0.680 -> terminal 0.521 (runs 0.698->0.554, 0.662->0.488) | G11 parametric 0.628 | speed 0.37 / 0.33 m/s, airborne 0.14 / 0.07; edits ['weak+1']
  nolegs_s0            gait switch  held-out raw 1.017 -> terminal 1.000 (runs 1.028->1.012, 1.006->0.988) | G11 parametric 0.561 | speed 0.40 / 0.44 m/s, airborne 1.00 / 0.05; edits ['torso']
  stump_left_s0        gait switch  held-out raw 0.797 -> terminal 0.553 (runs 0.537->0.496, 1.057->0.611) | G11 parametric 0.469 | speed 0.21 / 0.16 m/s, airborne 0.39 / 0.03; edits ['rhythm', 'vault']
  noleg_left_s0        gait switch  held-out raw 0.748 -> terminal 0.580 (runs 0.967->0.760, 0.530->0.400) | G11 parametric 0.636 | speed 0.39 / 0.34 m/s, airborne 0.09 / 0.06; edits ['lateral', 'weak+1', 'arms']
  short_shank_right_s0 walking      held-out raw 0.569 -> terminal 0.569 (runs 0.615->0.615, 0.523->0.523) | G11 parametric 0.461 | speed 0.40 / 0.29 m/s, airborne 0.14 / 0.10; edits []
  locked_knee_right_s0 walking      held-out raw 0.630 -> terminal 0.480 (runs 0.657->0.521, 0.603->0.439) | G11 parametric 0.635 | speed 0.44 / 0.39 m/s, airborne 0.10 / 0.00; edits ['stiff+1', 'legs', 'stiff+1']
  stump_right_s0       gait switch  held-out raw 0.650 -> terminal 0.609 (runs 0.403->0.440, 0.897->0.779) | G11 parametric 0.637 | speed 0.31 / 0.24 m/s, airborne 0.12 / 0.07; edits ['lateral', 'rhythm']
  noleg_right_s0       gait switch  held-out raw 0.442 -> terminal 0.414 (runs 0.449->0.423, 0.435->0.405) | G11 parametric 0.677 | speed 0.35 / 0.29 m/s, airborne 0.14 / 0.12; edits ['lateral', 'weak+1', 'weak+1', 'legs', 'weak+1']


## Outcome (frozen tree): K1 fail, K4 pass -> C; K2 pass, K3 pass; K5, K6, K7 reported
