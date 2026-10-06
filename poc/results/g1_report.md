# G1 scored: 14 cases, 4 steps

## I1 first pick = designed class, design bodies (hybrid); I2 designed class added within two steps
  locked_knee_left_s0  designed stiff_l  first kneel_l  added ['kneel_l', 'weak_l', 'weak_r'] | projection first hop      oracle first stiff_l
  noleg_left_s0        designed hop      first hop      added ['hop', 'vault', 'stiff_r', 'short_r'] | projection first hop      oracle first hop
  short_shank_left_s0  designed short_l  first short_r  added ['short_r', 'weak_l'] | projection first short_l  oracle first short_r
  stump_left_s0        designed kneel_l  first hop      added ['hop', 'kneel_l'] | projection first kneel_l  oracle first hop
  nolegs_s0            designed vault    first vault    added ['vault'] | projection first vault    oracle first vault
-> I1 FAIL: 2 of 5 (bar >= 3 of 5)
-> I2 FAIL: 3 of 5 (bar >= 4 of 5)

## I3 designed class within two steps on the mirrored bodies (hybrid)
  short_shank_right_s0 designed short_r  added ['kneel_r', 'weak_r'] | projection ['hop', 'kneel_l', 'weak_r'] oracle ['kneel_r', 'weak_r']
  locked_knee_right_s0 designed stiff_r  added ['kneel_r', 'weak_r', 'stiff_r'] | projection ['hop'] oracle ['stiff_r', 'weak_r', 'stiff_l', 'hop']
  noleg_right_s0       designed hop      added ['hop', 'vault', 'kneel_l', 'weak_l'] | projection ['hop', 'vault', 'stiff_l', 'weak_l'] oracle ['hop', 'vault', 'kneel_l', 'weak_l']
  stump_right_s0       designed kneel_r  added ['hop', 'short_l', 'hop'] | projection ['kneel_r', 'hop'] oracle ['hop', 'short_l', 'hop']
  nolegs_s1            designed vault    added ['vault'] | projection ['vault'] oracle ['vault']
-> I3 FAIL: 2 of 5 (bar >= 3 of 4)

## I4 value per step against the oracle table, all cases, steps with positive oracle gain
  projection  median 0.768 mean 0.541 over 50 steps; repairs/step median 1
  hybrid      median 1.000 mean 0.827 over 49 steps; repairs/step median 6
  oracle      median 1.000 mean 1.000 over 48 steps; repairs/step median 10
-> I4 pass (bar: hybrid median >= 0.90)

## I5 terminal reduction against the joint floor (differential evolution from V0), impaired cases
  locked_knee_left_s0  v0 0.666 hybrid 0.615 projection 0.573 oracle 0.520 floor 0.666 | hybrid/floor 51820769.36
  noleg_left_s0        v0 0.689 hybrid 0.321 projection 0.320 oracle 0.321 floor 0.405 | hybrid/floor 1.30
  short_shank_left_s0  v0 0.352 hybrid 0.307 projection 0.318 oracle 0.307 floor 0.352 | hybrid/floor 45771422.73
  stump_left_s0        v0 0.679 hybrid 0.310 projection 0.334 oracle 0.310 floor 0.354 | hybrid/floor 1.13
  nolegs_s0            v0 0.796 hybrid 0.421 projection 0.421 oracle 0.421 floor 0.388 | hybrid/floor 0.92
  short_shank_right_s0 v0 0.379 hybrid 0.328 projection 0.342 oracle 0.328 floor 0.379 | hybrid/floor 51292938.75
  locked_knee_right_s0 v0 0.678 hybrid 0.577 projection 0.671 oracle 0.565 floor 0.678 | hybrid/floor 100516456.60
  noleg_right_s0       v0 0.683 hybrid 0.240 projection 0.243 oracle 0.240 floor 0.371 | hybrid/floor 1.42
  stump_right_s0       v0 0.708 hybrid 0.331 projection 0.342 oracle 0.331 floor 0.393 | hybrid/floor 1.19
  nolegs_s1            v0 0.777 hybrid 0.408 projection 0.408 oracle 0.408 floor 0.360 | hybrid/floor 0.89
-> I5 pass: median 1.358 (bar >= 0.80)

## I6 no consumer worse than V0 at the hybrid terminal, impaired cases
  locked_knee_left_s0  worse: contact_t, rhythm
  noleg_left_s0        none worse
  short_shank_left_s0  none worse
  stump_left_s0        worse: reach
  nolegs_s0            none worse
  short_shank_right_s0 worse: joint_stats, reach
  locked_knee_right_s0 worse: stance, height
  noleg_right_s0       none worse
  stump_right_s0       worse: pitch, reach
  nolegs_s1            worse: pitch
-> I6 FAIL: 4 of 10 (bar >= 10 of 12)

## Reported: controls (nothing designed to be missing)
  intact_s0            first pick weak_l drop 0.008 dead True | added [] | v0 0.265 -> 0.265
  weak_hip_left_s0     first pick hop drop 0.072 dead False | added ['hop', 'vault'] | v0 0.450 -> 0.399
  weak_hip_right_s0    first pick vault drop 0.099 dead False | added ['vault', 'weak_r'] | v0 0.435 -> 0.376
  intact_s1            first pick vault drop 0.061 dead False | added ['vault', 'stiff_l', 'weak_r', 'weak_l'] | v0 0.475 -> 0.413

## Outcome (frozen tree): I2 fail, I4 pass -> A; I1 2/5, I3 2/4, I5 pass, I6 fail
