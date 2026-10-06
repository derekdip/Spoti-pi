# G5 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G5 ['legs', 'limp-1', 'torso', 'legs', 'arms'] | G4 ['legs', 'stiff-1', 'limp-1', 'arms']
  nolegs_s0            designed vault+0  G5 ['vault', 'rhythm', 'arms'] | G4 ['vault', 'rhythm', 'arms']
  stump_left_s0        designed kneel-1  G5 ['legs', 'rhythm', 'torso', 'kneel-1', 'kneel-1'] | G4 ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'kneel-1']
  locked_knee_right_s0 designed stiff+1  G5 ['torso', 'legs', 'kneel+1'] | G4 ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1']
  stump_right_s0       designed kneel+1  G5 ['limp+1', 'kneel+1', 'limp+1', 'legs', 'torso'] | G4 ['legs', 'kneel+1']
-> K1 FAIL: first 2 of 3 (>= 2), within two 2 of 3 (>= 3), mirrors 1 of 2 (>= 2)

## K5 one-leg bodies: terminal fitting error against G4's (hop in the grammar), and the right stump's first repair
  noleg_left_s0        G5 0.571 -> 0.496 ['legs', 'torso'] | G4 -> 0.461 ['hop', 'torso', 'legs'] | ABOVE one percent of V0
  noleg_right_s0       G5 0.457 -> 0.258 ['legs', 'torso', 'rhythm', 'arms', 'legs'] | G4 -> 0.245 ['legs', 'torso', 'rhythm', 'arms'] | ABOVE one percent of V0
  stump_right_s0       first impairment repair ['limp+1'], guard rejections [(0, 'legs', 'guard: reach'), (2, 'legs', 'guard: reach'), (2, 'torso', 'guard: reach')] (G4: hop rejected by the guard on reach at step 0)
-> K5 FAIL: 0 of 2 one-leg bodies within one percent of V0 of G4's terminal

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  short_shank_left_s0  worse: joint_stats, asym_joints, height
  locked_knee_left_s0  worse: height, rhythm
  noleg_left_s0        worse: reach
  nolegs_s0            worse: asym_stance, rhythm
  stump_left_s0        worse: joint_stats
  short_shank_right_s0 none worse
  locked_knee_right_s0 worse: height
  stump_right_s0       none worse
  noleg_right_s0       none worse
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); reported: none worse at all on 3 of 9 (G4: 2 of 9)

## K3 controls: impairment repairs added, in total against G4's
  intact_s0            G5 ['torso'] (0.300 -> 0.275, held-out mean 0.495 -> 0.493) | G4 ['torso', 'vault']
  weak_hip_left_s0     G5 ['torso'] (0.508 -> 0.469, held-out mean 0.442 -> 0.423) | G4 ['torso', 'legs']
  weak_hip_right_s0    G5 ['torso', 'weak+1', 'stiff+1'] (0.470 -> 0.385, held-out mean 0.493 -> 0.416) | G4 ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1']
  intact_s1            G5 ['legs', 'rhythm', 'torso'] (0.488 -> 0.405, held-out mean 0.401 -> 0.335) | G4 ['legs', 'rhythm', 'legs', 'torso']
-> K3 pass: 2 impairment repairs on 4 controls (<= 4)

## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)
  short_shank_left_s0  fit 0.334 -> 0.294 | held-out mean 0.400 -> 0.396 (1 of 2 lower) | G4 fit -> 0.294, held-out -> 0.396
  locked_knee_left_s0  fit 0.765 -> 0.398 | held-out mean 0.770 -> 0.465 (2 of 2 lower) | G4 fit -> 0.431, held-out -> 0.482
  noleg_left_s0        fit 0.571 -> 0.496 | held-out mean 0.420 -> 0.317 (2 of 2 lower) | G4 fit -> 0.461, held-out -> 0.279
  nolegs_s0            fit 0.728 -> 0.354 | held-out mean 0.732 -> 0.342 (2 of 2 lower) | G4 fit -> 0.354, held-out -> 0.342
  stump_left_s0        fit 0.494 -> 0.276 | held-out mean 0.495 -> 0.414 (1 of 2 lower) | G4 fit -> 0.226, held-out -> 0.366
  short_shank_right_s0 fit 0.317 -> 0.317 | held-out mean 0.345 -> 0.345 (0 of 2 lower) | G4 fit -> 0.310, held-out -> 0.343
  locked_knee_right_s0 fit 0.769 -> 0.422 | held-out mean 0.714 -> 0.483 (2 of 2 lower) | G4 fit -> 0.397, held-out -> 0.450
  stump_right_s0       fit 0.538 -> 0.343 | held-out mean 0.474 -> 0.331 (2 of 2 lower) | G4 fit -> 0.330, held-out -> 0.320
  noleg_right_s0       fit 0.457 -> 0.258 | held-out mean 0.523 -> 0.384 (2 of 2 lower) | G4 fit -> 0.245, held-out -> 0.380
-> K4 pass: 8 of 9 (>= 7); both runs lower on 6 of 9

## Reported
  repairs applied per case, median 3 (G4: 3); rejections by reason {'spent': 90, 'held-out': 31, 'guard': 5}
  applied repairs lowering both held-out runs 28 of 37, one run 9
  value of the applied repair against the best fitting drop, median 1.00
  terminal fitting error, G5 against G4, every case: intact_s0 0.275/0.268; weak_hip_left_s0 0.469/0.443; short_shank_left_s0 0.294/0.294; locked_knee_left_s0 0.398/0.431; noleg_left_s0 0.496/0.461; nolegs_s0 0.354/0.354; stump_left_s0 0.276/0.226; short_shank_right_s0 0.317/0.310; weak_hip_right_s0 0.385/0.354; locked_knee_right_s0 0.422/0.397; stump_right_s0 0.343/0.330; intact_s1 0.405/0.387; noleg_right_s0 0.258/0.245

## Outcome (frozen tree): K1 fail, K5 fail -> D; K2 pass, K3 pass, K4 pass
