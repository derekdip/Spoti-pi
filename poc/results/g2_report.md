# G2 scored: 14 cases, 6 steps

## J1 first IMPAIRMENT repair names the damage (class and side), oracle path, design bodies; J2 within the first two impairment repairs (base re-fits do not count)
  locked_knee_left_s0  designed stiff-1  oracle ['legs', 'stiff-1', 'limp-1', 'arms', 'kneel+1', 'torso'] | safe [] | projection ['hop', 'stiff-1', 'legs', 'kneel+1', 'vault']
  nolegs_s0            designed vault+0  oracle ['vault', 'rhythm', 'torso'] | safe ['rhythm'] | projection ['vault', 'torso', 'arms', 'rhythm']
  noleg_left_s0        designed hop+0  oracle ['hop', 'torso', 'arms'] | safe [] | projection ['hop', 'vault', 'torso', 'hop']
  stump_left_s0        designed kneel-1  oracle ['legs', 'kneel-1', 'torso', 'legs', 'rhythm', 'legs'] | safe ['hop'] | projection ['hop', 'torso', 'kneel-1', 'limp+1']
-> J1 pass: 4 of 4 (bar >= 3 of 4)
-> J2 pass: 4 of 4 (bar >= 3 of 4)

## J3 within two repairs on the mirrored bodies, oracle path
  locked_knee_right_s0 designed stiff+1  oracle ['legs', 'stiff+1', 'torso', 'rhythm', 'stiff+1', 'arms'] | safe []
  stump_right_s0       designed kneel+1  oracle ['hop', 'kneel+1', 'legs', 'kneel+1', 'torso', 'vault'] | safe []
  noleg_right_s0       designed hop+0  oracle ['legs', 'torso', 'rhythm', 'arms'] | safe ['legs', 'arms']
-> J3 pass: 2 of 3 (bar >= 2 of 3)

## J4 terminal reduction against the local floor (Powell from V0 and from the oracle terminal), impaired cases
  locked_knee_left_s0  v0 0.765 oracle 0.379 safe 0.765 projection 0.417 floor 0.372 (v0 0.474, terminal 0.372) | 0.98
  short_shank_left_s0  v0 0.334 oracle 0.294 safe 0.334 projection 0.295 floor 0.291 (v0 0.302, terminal 0.291) | 0.92
  nolegs_s0            v0 0.728 oracle 0.338 safe 0.678 projection 0.343 floor 0.326 (v0 0.326, terminal 0.331) | 0.97
  noleg_left_s0        v0 0.571 oracle 0.446 safe 0.571 projection 0.443 floor 0.426 (v0 0.435, terminal 0.426) | 0.87
  stump_left_s0        v0 0.494 oracle 0.224 safe 0.334 projection 0.307 floor 0.224 (v0 0.277, terminal 0.224) | 1.00
  short_shank_right_s0 v0 0.317 oracle 0.295 safe 0.317 projection 0.298 floor 0.295 (v0 0.304, terminal 0.295) | 1.00
  locked_knee_right_s0 v0 0.769 oracle 0.349 safe 0.769 projection 0.462 floor 0.348 (v0 0.348, terminal 0.348) | 1.00
  stump_right_s0       v0 0.538 oracle 0.298 safe 0.538 projection 0.317 floor 0.279 (v0 0.318, terminal 0.279) | 0.92
  noleg_right_s0       v0 0.457 oracle 0.245 safe 0.345 projection 0.251 floor 0.233 (v0 0.233, terminal 0.234) | 0.95
  nolegs_s1            v0 0.724 oracle 0.307 safe 0.422 projection 0.307 floor 0.306 (v0 0.310, terminal 0.306) | 1.00
-> J4 pass: median 0.976 (bar >= 0.80, ratios capped at 2)

## J5 no consumer worse than V0 at the oracle terminal, impaired cases
  locked_knee_left_s0  worse: asym_stance, height, rhythm, reach
  short_shank_left_s0  worse: joint_stats, asym_joints, height
  nolegs_s0            worse: asym_stance, rhythm
  noleg_left_s0        worse: asym_joints
  stump_left_s0        none worse
  short_shank_right_s0 worse: joint_stats, speed, pitch, rhythm, reach
  locked_knee_right_s0 worse: stance, height
  stump_right_s0       none worse
  noleg_right_s0       none worse
  nolegs_s1            none worse
-> J5 FAIL: 4 of 10 (bar >= 6 of 10)

## Reported: the short-shank bodies (no designed class), the safe path's identity, and the controls
  short_shank_left_s0  oracle added ['legs'] (0.334 -> 0.294); impairment repairs []
  short_shank_right_s0 oracle added ['rhythm', 'weak+1'] (0.317 -> 0.295); impairment repairs ['weak+1']
  safe path: designed within two on 0 of 4 design, 0 of 3 mirrors; declined at step zero on 6 of 10 impaired
  intact_s0            oracle added ['torso', 'vault', 'weak-1'] (0.300 -> 0.258); safe []
  weak_hip_left_s0     oracle added ['torso', 'legs', 'arms'] (0.508 -> 0.433); safe []
  weak_hip_right_s0    oracle added ['torso', 'legs', 'stiff+1', 'arms', 'weak+1', 'kneel-1'] (0.470 -> 0.337); safe ['arms']
  intact_s1            oracle added ['legs', 'rhythm', 'legs', 'vault'] (0.488 -> 0.381); safe ['arms']
  projection value per step: median 0.31 mean 0.06 (83 steps)

## Outcome (frozen tree): J2 pass, J3 pass -> A; J1 4/4, J4 pass, J5 fail
