# Experiment summary

Teacher: 1600 stalks, 601 frames, ~320 ops/stalk/frame (stateful, neighbour-coupled, substepped).

Banked causes: 18 events + 201-point path = 693 floats (vs 6400 floats of per-stalk state).

## Discovered model

```
  wake(B=0.417, w=0.138, t_lead=0.133, lam=0.1, k=82.6, zeta=0.158, mix=0.831, q=1.25)
  presence(A=0.162, sigma=0.149, mix=0.634, q=1.4)
  radial_impulse(A=0.0863, sigma=0.369, lam=9.53, k=162, zeta=0.733, mix=0.548, q=3.56)
  crush(C=0.0228, w=0.05, t_rise=0.193, t_rec=11.8, mix=5.14e-21, q=2.17)
  ring_wave(A=0.0465, lam=19.9, v=0.69, w=0.467, kappa=6.87)
  saturate(b_max=1.4)
```

Cost ~124 ops/stalk/frame (stateless, no neighbour reads).

## Errors (relative RMS vs teacher, all stalks, all frames)

| metric | value |
|---|---|
| E_all | 0.390 |
| E_walk (player moving) | 0.413 |
| E_late (persistence phase) | 0.346 |
| E_all after 150 ms temporal smoothing | 0.375 |
| E on 16x16 coarse field, all frames | 0.224 |
| E on 16x16 coarse field, persistence phase | 0.224 |
| correlation of late coarse fields (AI trail query) | 0.976 |
| trail IoU on 16x16 query (25% of max threshold) | 0.955 |

## Greedy search path (fit subset)

| terms | E_all | E_late | cost |
|---|---|---|---|
| (none) | 1.000 | 1.000 | 0 |
| wake | 0.424 | 0.402 | 26 |
| wake + presence | 0.404 | 0.350 | 48 |
| wake + presence + radial_impulse | 0.393 | 0.351 | 78 |
| wake + presence + radial_impulse + crush | 0.391 | 0.349 | 101 |
| wake + presence + radial_impulse + crush + saturate | 0.391 | 0.347 | 108 |
| wake + presence + radial_impulse + crush + ring_wave + saturate | 0.390 | 0.346 | 124 |

## Single-primitive baselines

| primitive | E_all | E_late | cost |
|---|---|---|---|
| presence | 0.955 | 0.990 | 22 |
| radial_impulse | 0.529 | 0.434 | 310 |
| ring_wave | 0.984 | 1.000 | 93 |
| wake | 0.428 | 0.404 | 26 |
| crush | 0.507 | 0.400 | 24 |

## Coarse-field bake (Level 1) instead of direct token evaluation

| grid | E_all | E_late | E coarse16 late | ops/stalk/frame |
|---|---|---|---|---|
| 16x16 | 0.609 | 0.577 | 0.369 | 32 |
| 32x32 | 0.444 | 0.436 | 0.245 | 92 |
| 64x64 | 0.415 | 0.405 | 0.229 | 330 |
