# G6 scored: 13 cases (nolegs_s1 excluded as the declared pilot), 6 steps

## K6 reproduction of G4 on every case that never used hop
  intact_s0            same: G6 ['torso', 'vault'] 0.267662 | G4 ['torso', 'vault'] 0.267662
  weak_hip_left_s0     same: G6 ['torso', 'legs'] 0.443067 | G4 ['torso', 'legs'] 0.443067
  locked_knee_left_s0  same: G6 ['legs', 'stiff-1', 'limp-1', 'arms'] 0.431373 | G4 ['legs', 'stiff-1', 'limp-1', 'arms'] 0.431373
  short_shank_left_s0  same: G6 ['legs'] 0.294389 | G4 ['legs'] 0.294389
  nolegs_s0            same: G6 ['vault', 'rhythm', 'arms'] 0.354121 | G4 ['vault', 'rhythm', 'arms'] 0.354121
  noleg_left_s0        DIFFERS: G6 ['legs', 'torso'] 0.477345 | G4 ['hop', 'torso', 'legs'] 0.461165  (the hop case, not counted)
  stump_left_s0        same: G6 ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'kneel-1'] 0.225838 | G4 ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'kneel-1'] 0.225838
  short_shank_right_s0 same: G6 ['legs'] 0.309701 | G4 ['legs'] 0.309701
  weak_hip_right_s0    same: G6 ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1'] 0.354137 | G4 ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1'] 0.354137
  stump_right_s0       same: G6 ['legs', 'kneel+1'] 0.330388 | G4 ['legs', 'kneel+1'] 0.330388
  locked_knee_right_s0 same: G6 ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1'] 0.396813 | G4 ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1'] 0.396813
  noleg_right_s0       same: G6 ['legs', 'torso', 'rhythm', 'arms'] 0.244504 | G4 ['legs', 'torso', 'rhythm', 'arms'] 0.244504
  intact_s1            same: G6 ['legs', 'rhythm', 'legs', 'torso'] 0.386704 | G4 ['legs', 'rhythm', 'legs', 'torso'] 0.386704
-> K6 pass: 12 of 12 reproduce G4 (all required)

## K5 the left one-leg body without hop: terminal fitting error against G4's
  noleg_left_s0        G6 0.571 -> 0.477 ['legs', 'torso'] | G4 -> 0.461 ['hop', 'torso', 'legs'] | held-out mean 0.420 -> 0.288 (G4 -> 0.279)
    t0 pick legs top drops [('legs', 0.105), ('kneel', 0.07), ('limp', 0.067), ('rhythm', 0.049)] rejected []
    t1 pick torso top drops [('torso', 0.066), ('vault', 0.056), ('arms', 0.049), ('rhythm', 0.028)] rejected []
    t2 pick None top drops [('arms', 0.054), ('vault', 0.049), ('rhythm', 0.022), ('kneel', 0.002)] rejected [('arms', 'held-out 0.3171 >= 0.287'), ('vault', 'held-out 0.3151 >= 0.287'), ('rhythm', 'held-out 0.2893 >= 0.287')]
-> K5 FAIL: above one percent of V0 of G4's terminal

## K1 identity: first impairment repair, within two, and on the mirrors
  locked_knee_left_s0  designed stiff-1  G6 ['legs', 'stiff-1', 'limp-1', 'arms']
  nolegs_s0            designed vault+0  G6 ['vault', 'rhythm', 'arms']
  stump_left_s0        designed kneel-1  G6 ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'kneel-1']
  stump_right_s0       designed kneel+1  G6 ['legs', 'kneel+1']
  locked_knee_right_s0 designed stiff+1  G6 ['legs', 'stiff+1', 'torso', 'legs', 'limp-1', 'stiff+1']
-> K1 pass: first 3 of 3 (>= 2), within two 3 of 3 (>= 3), mirrors 2 of 2 (>= 2)

## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance
  locked_knee_left_s0  worse: asym_stance, height, rhythm
  short_shank_left_s0  worse: joint_stats, asym_joints, height
  nolegs_s0            worse: asym_stance, rhythm
  noleg_left_s0        worse: reach
  stump_left_s0        none worse
  short_shank_right_s0 worse: stance, joint_stats, asym_stance, height, reach
  stump_right_s0       worse: reach
  locked_knee_right_s0 worse: stance, height, rhythm
  noleg_right_s0       none worse
-> K2 pass: none beyond tolerance on 9 of 9 (>= 7); none worse at all on 2 of 9

## K3 controls: impairment repairs added, in total against G4's
  intact_s0            G6 ['torso', 'vault'] (0.300 -> 0.268, held-out mean 0.495 -> 0.483)
  weak_hip_left_s0     G6 ['torso', 'legs'] (0.508 -> 0.443, held-out mean 0.442 -> 0.387)
  weak_hip_right_s0    G6 ['torso', 'legs', 'stiff+1', 'weak+1', 'kneel-1'] (0.470 -> 0.354, held-out mean 0.493 -> 0.407)
  intact_s1            G6 ['legs', 'rhythm', 'legs', 'torso'] (0.488 -> 0.387, held-out mean 0.401 -> 0.344)
-> K3 pass: 4 impairment repairs on 4 controls (<= 4)

## K4 held-out error at the terminal below V0's, damaged bodies
  locked_knee_left_s0  fit 0.765 -> 0.431 | held-out mean 0.770 -> 0.482 (2 of 2 lower)
  short_shank_left_s0  fit 0.334 -> 0.294 | held-out mean 0.400 -> 0.396 (1 of 2 lower)
  nolegs_s0            fit 0.728 -> 0.354 | held-out mean 0.732 -> 0.342 (2 of 2 lower)
  noleg_left_s0        fit 0.571 -> 0.477 | held-out mean 0.420 -> 0.288 (2 of 2 lower)
  stump_left_s0        fit 0.494 -> 0.226 | held-out mean 0.495 -> 0.366 (1 of 2 lower)
  short_shank_right_s0 fit 0.317 -> 0.310 | held-out mean 0.345 -> 0.343 (1 of 2 lower)
  stump_right_s0       fit 0.538 -> 0.330 | held-out mean 0.474 -> 0.320 (2 of 2 lower)
  locked_knee_right_s0 fit 0.769 -> 0.397 | held-out mean 0.714 -> 0.450 (2 of 2 lower)
  noleg_right_s0       fit 0.457 -> 0.245 | held-out mean 0.523 -> 0.380 (2 of 2 lower)
-> K4 pass: 9 of 9 (>= 7); both runs lower on 6 of 9

## Reported
  repairs applied per case, median 3; rejections by reason {'held-out': 26, 'spent': 78}; value median 1.00

## Outcome (frozen tree): K6 pass, K5 fail -> B; K1 pass, K2 pass, K3 pass, K4 pass
