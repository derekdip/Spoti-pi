# G4 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  two-run ['legs', 'stiff-1', 'limp-1', 'arms'] | G3 one-run ['legs', 'stiff-1', 'limp-1', 'arms']
  nolegs_s0            designed vault+0  two-run ['vault', 'rhythm', 'arms'] | G3 one-run ['vault', 'rhythm', 'torso']
  stump_left_s0        designed kneel-1  two-run ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'kneel-1'] | G3 one-run ['legs', 'kneel-1']
  noleg_left_s0        designed hop+0  two-run ['hop', 'torso', 'legs'] | G3 one-run ['hop', 'torso', 'arms']
  stump_right_s0       designed kneel+1  two-run ['legs', 'kneel+1'] | G3 one-run ['hop', 'rhythm', 'torso', 'limp-1', 'stiff+1', 'kneel+1']
  locked_knee_right_s0 designed stiff+1  two-run ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1'] | G3 one-run ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1']
  noleg_right_s0       designed hop+0  two-run ['legs', 'torso', 'rhythm', 'arms'] | G3 one-run ['legs', 'torso', 'rhythm', 'arms']
-> K1 pass: first 4 of 4 (>= 3), within two 4 of 4 (>= 3), mirrors 2 of 3 (>= 2)

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  worse: asym_stance, height, rhythm
  short_shank_left_s0  worse: joint_stats, asym_joints, height
  nolegs_s0            worse: asym_stance, rhythm
  stump_left_s0        none worse
  noleg_left_s0        worse: asym_joints, reach
  short_shank_right_s0 worse: stance, joint_stats, asym_stance, height, reach
  stump_right_s0       worse: reach
  locked_knee_right_s0 worse: stance, height, rhythm
  noleg_right_s0       none worse
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); reported: none worse at all on 2 of 9 (G3: 3 of 10)

## K3 controls: impairment repairs added, in total against G3's
  intact_s0            two-run ['torso', 'vault'] (0.300 -> 0.268, held-out mean 0.495 -> 0.483) | G3 one-run ['torso', 'vault', 'weak-1']
  weak_hip_left_s0     two-run ['torso', 'legs'] (0.508 -> 0.443, held-out mean 0.442 -> 0.387) | G3 one-run ['torso', 'legs']
  weak_hip_right_s0    two-run ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1'] (0.470 -> 0.354, held-out mean 0.493 -> 0.407) | G3 one-run ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1']
  intact_s1            two-run ['legs', 'rhythm', 'legs', 'torso'] (0.488 -> 0.387, held-out mean 0.401 -> 0.344) | G3 one-run ['torso']
-> K3 pass: 4 impairment repairs on 4 controls (<= 5)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  locked_knee_left_s0  fit 0.765 -> 0.431 | held-out mean 0.770 -> 0.482, runs 0.730->0.474, 0.811->0.491 (2 of 2 lower) | G3 one-run held-out 0.730 -> 0.474
  short_shank_left_s0  fit 0.334 -> 0.294 | held-out mean 0.400 -> 0.396, runs 0.404->0.405, 0.396->0.386 (1 of 2 lower) | G3 one-run held-out 0.404 -> 0.348
  nolegs_s0            fit 0.728 -> 0.354 | held-out mean 0.732 -> 0.342, runs 0.724->0.361, 0.739->0.322 (2 of 2 lower) | G3 one-run held-out 0.724 -> 0.357
  stump_left_s0        fit 0.494 -> 0.226 | held-out mean 0.495 -> 0.366, runs 0.475->0.490, 0.515->0.241 (1 of 2 lower) | G3 one-run held-out 0.475 -> 0.470
  noleg_left_s0        fit 0.571 -> 0.461 | held-out mean 0.420 -> 0.279, runs 0.491->0.350, 0.350->0.207 (2 of 2 lower) | G3 one-run held-out 0.491 -> 0.345
  short_shank_right_s0 fit 0.317 -> 0.310 | held-out mean 0.345 -> 0.343, runs 0.342->0.335, 0.349->0.350 (1 of 2 lower) | G3 one-run held-out 0.342 -> 0.335
  stump_right_s0       fit 0.538 -> 0.330 | held-out mean 0.474 -> 0.320, runs 0.482->0.324, 0.465->0.316 (2 of 2 lower) | G3 one-run held-out 0.482 -> 0.354
  locked_knee_right_s0 fit 0.769 -> 0.397 | held-out mean 0.714 -> 0.450, runs 0.831->0.465, 0.597->0.434 (2 of 2 lower) | G3 one-run held-out 0.831 -> 0.465
  noleg_right_s0       fit 0.457 -> 0.245 | held-out mean 0.523 -> 0.380, runs 0.577->0.426, 0.469->0.335 (2 of 2 lower) | G3 one-run held-out 0.577 -> 0.426
-> K4 pass: 9 of 9 (>= 7); both runs lower on 6 of 9

## Reported
  repairs applied per case, median 3 (G3: 3); rejections by reason {'held-out': 32, 'spent': 85, 'guard': 1}
  applied repairs lowering both held-out runs 31 of 43, one run 12, neither 0
  value of the applied repair against the best fitting drop, median 1.00
  stump_right_s0       designed class arrives as impairment repair 1 (G3: [3])
  locked_knee_right_s0 designed class arrives as impairment repair 1 (G3: [0])
  noleg_right_s0       designed class arrives as impairment repair never (G3: ['never'])
  locked_knee_left_s0  designed class arrives as impairment repair 1 (G3: [0])
  nolegs_s0            designed class arrives as impairment repair 1 (G3: [0])
  stump_left_s0        designed class arrives as impairment repair 1 (G3: [0])
  noleg_left_s0        designed class arrives as impairment repair 1 (G3: [0])

## Outcome (frozen tree): K1 pass, K2 pass -> A; K3 pass, K4 pass
