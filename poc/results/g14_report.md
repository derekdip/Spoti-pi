# G14 scored: 4 growth cases, 4 bodies with compositions, 6 steps, grounding clearance

## K8 composition: the composed edit below the raw clip on >= 2 of 3 runs, and its mean over the held-out runs (1, 2) within 1.25 of the fresh growth's held-out terminal, on both combined bodies
  locked_knee_left+weak_hip_right  raw 0.686 0.672 0.691 | composed 0.497 0.528 0.519 (3 of 3 below) | held-out mean 0.524 vs fresh growth 0.416 (x1.25 = 0.520) -> MISS
      locked knee edit alone (G13 locked_knee_left_s0)           0.529 0.509 0.515
      weak hip edit alone (G13 weak_hip_right_s0)                0.502 0.539 0.525
  locked_knee_left+noarm_right     raw 0.518 0.756 0.558 | composed 0.453 0.638 0.475 (3 of 3 below) | held-out mean 0.556 vs fresh growth 0.565 (x1.25 = 0.706) -> ok
-> K8 FAIL

## K9 a removed arm: the raw intact clip with the arm dropped against the one-arm teacher's runs within 1.2 of the intact clip's own run-to-run error (0.511) on >= 2 of 3 runs, and the growth adds no impairment edit
  raw clip errors 0.548 0.549 0.489 (3 of 3 within 0.613); growth added [] (impairments [])
-> K9 pass

## K10 (reported) the one-arm crawl: the legless body's loop with the arm dropped against the one-arm teacher's runs, the crawl's own run-to-run error (0.568), and the growth on the loop
  raw loop errors 2.667 1.852 2.080 (crawl's own runs 0.568); speed 0.42/0.09; growth ['torso', 'arms'] fit 2.667 -> 1.873, held-out 1.966 -> 1.193

## K11 (reported) the growth on each body: held-out error V0 -> terminal per run, edits, speed and airborne against the teacher
  nolegs+noarm_left_s0                 base nolegs  fit 2.667 -> 1.873 | held-out 1.852->1.056, 2.080->1.330 | edits ['torso', 'arms']; rejections 6
  noarm_left_s0                        base intact  fit 0.548 -> 0.548 | held-out 0.549->0.549, 0.489->0.489 | edits []; rejections 10
  locked_knee_left+noarm_right_s0      base intact  fit 0.518 -> 0.417 | held-out 0.756->0.654, 0.558->0.476 | edits ['lateral', 'hold+1', 'arms']; rejections 10
  locked_knee_left+weak_hip_right_s0   base intact  fit 0.686 -> 0.343 | held-out 0.672->0.433, 0.691->0.398 | edits ['limp-1', 'rhythm', 'weak-1', 'stiff-1', 'lateral']; rejections 11
  held-out mean below V0's on 3 of 4
  locked_knee_left+weak_hip_right  raw clip                                                   speed 0.40/0.23 airborne 0.00/0.00
  locked_knee_left+weak_hip_right  locked knee edit alone (G13 locked_knee_left_s0)           speed 0.41/0.23 airborne 0.00/0.00
  locked_knee_left+weak_hip_right  weak hip edit alone (G13 weak_hip_right_s0)                speed 0.41/0.23 airborne 0.00/0.00
  locked_knee_left+weak_hip_right  composed                                                   speed 0.42/0.23 airborne 0.00/0.00
  locked_knee_left+noarm_right     raw clip (arm dropped)                                     speed 0.40/0.41 airborne 0.00/0.04
  locked_knee_left+noarm_right     locked knee edit (G13 locked_knee_left_s0), arm dropped    speed 0.41/0.41 airborne 0.00/0.04
  noarm_left                       raw clip (arm dropped)                                     speed 0.40/0.41 airborne 0.00/0.07
  nolegs+noarm_left                raw crawl loop (arm dropped)                               speed 0.42/0.09 airborne 0.12/0.01

## Outcome (frozen tree): K8 fail, K9 pass -> C; K10, K11 reported
