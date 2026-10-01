# G3 scored: 14 cases, 6 steps

## K1 identity on the checked path: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  checked ['legs', 'stiff-1', 'limp-1', 'arms'] | G2 oracle ['legs', 'stiff-1', 'limp-1', 'arms', 'kneel+1', 'torso']
  stump_left_s0        designed kneel-1  checked ['legs', 'kneel-1'] | G2 oracle ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'legs']
  nolegs_s0            designed vault+0  checked ['vault', 'rhythm', 'torso'] | G2 oracle ['vault', 'rhythm', 'torso']
  noleg_left_s0        designed hop+0  checked ['hop', 'torso', 'arms'] | G2 oracle ['hop', 'torso', 'arms']
  locked_knee_right_s0 designed stiff+1  checked ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1'] | G2 oracle ['legs', 'stiff+1', 'torso', 'rhythm', 'stiff+1', 'arms']
  stump_right_s0       designed kneel+1  checked ['hop', 'rhythm', 'torso', 'limp-1', 'stiff+1', 'kneel+1'] | G2 oracle ['hop', 'kneel+1', 'legs', 'kneel+1', 'torso', 'vault']
  noleg_right_s0       designed hop+0  checked ['legs', 'torso', 'rhythm', 'arms'] | G2 oracle ['legs', 'torso', 'rhythm', 'arms']
-> K1 FAIL: first 4 of 4 (>= 3), within two 4 of 4 (>= 3), mirrors 1 of 3 (>= 2)

## K2 consumers at the checked terminal against V0, damaged bodies
  locked_knee_left_s0  worse: asym_stance, height, rhythm
  stump_left_s0        none worse
  nolegs_s0            worse: asym_stance, rhythm
  noleg_left_s0        worse: asym_joints
  short_shank_left_s0  worse: asym_stance, pitch, reach
  short_shank_right_s0 worse: stance, joint_stats, asym_stance, height, reach
  locked_knee_right_s0 worse: stance, height, rhythm
  stump_right_s0       worse: reach
  nolegs_s1            none worse
  noleg_right_s0       none worse
-> K2 FAIL: none worse on 3 of 10 (>= 6), none beyond tolerance on 10 of 10 (>= 8)

## K3 controls: impairment classes added
  weak_hip_left_s0     checked ['torso', 'legs'] (0.508 -> 0.443, held-out 0.481 -> 0.386) | G2 oracle ['torso', 'legs', 'arms']
  intact_s0            checked ['torso', 'vault', 'weak-1'] (0.300 -> 0.258, held-out 0.488 -> 0.479) | G2 oracle ['torso', 'vault', 'weak-1']
  weak_hip_right_s0    checked ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1'] (0.470 -> 0.354, held-out 0.539 -> 0.380) | G2 oracle ['torso', 'legs', 'stiff+1', 'arms', 'weak+1', 'kneel-1']
  intact_s1            checked ['torso'] (0.488 -> 0.454, held-out 0.300 -> 0.282) | G2 oracle ['legs', 'rhythm', 'legs', 'vault']
-> K3 FAIL: impairment classes on 2 of 4 controls (<= 1)

## K4 held-out error at the terminal below V0's, damaged bodies
  locked_knee_left_s0  fit 0.765 -> 0.431 | held-out 0.730 -> 0.474 | G2 oracle fit 0.379
  stump_left_s0        fit 0.494 -> 0.274 | held-out 0.475 -> 0.470 | G2 oracle fit 0.224
  nolegs_s0            fit 0.728 -> 0.338 | held-out 0.724 -> 0.357 | G2 oracle fit 0.338
  noleg_left_s0        fit 0.571 -> 0.446 | held-out 0.491 -> 0.345 | G2 oracle fit 0.446
  short_shank_left_s0  fit 0.334 -> 0.283 | held-out 0.404 -> 0.348 | G2 oracle fit 0.294
  short_shank_right_s0 fit 0.317 -> 0.310 | held-out 0.342 -> 0.335 | G2 oracle fit 0.295
  locked_knee_right_s0 fit 0.769 -> 0.397 | held-out 0.831 -> 0.465 | G2 oracle fit 0.349
  stump_right_s0       fit 0.538 -> 0.298 | held-out 0.482 -> 0.354 | G2 oracle fit 0.298
  nolegs_s1            fit 0.724 -> 0.307 | held-out 0.728 -> 0.359 | G2 oracle fit 0.307
  noleg_right_s0       fit 0.457 -> 0.245 | held-out 0.577 -> 0.426 | G2 oracle fit 0.245
-> K4 pass: 10 of 10 (>= 8)

## Reported
  repairs applied per case, median 3 (G2 oracle: 4); rejections by reason {'held-out': 35, 'spent': 90}
  value of the applied repair against the best fitting drop, median 1.00

## Outcome (frozen tree): K1 fail, K2 fail -> D; K3 fail, K4 pass
