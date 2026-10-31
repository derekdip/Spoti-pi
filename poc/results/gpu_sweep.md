# GPU sweep

## How few terms to ship

Scored on all 1600 stalks and all frames. Cost is ops per stalk per frame for direct token evaluation.

| model | walk | E_all | E_late | E_coarse16_all | E_coarse16_late | coarse16_late_corr | cost |
|---|---|---|---|---|---|---|---|
| six terms (as discovered) | training | 0.390 | 0.346 | 0.223 | 0.223 | 0.976 | 124.343 |
| six terms (as discovered) | held-out | 0.382 | 0.313 | 0.220 | 0.209 | 0.987 | 124.097 |
| wake + presence | training | 0.404 | 0.348 | 0.249 | 0.223 | 0.976 | 48.000 |
| wake + presence | held-out | 0.399 | 0.316 | 0.251 | 0.208 | 0.985 | 48.000 |
| wake only | training | 0.424 | 0.402 | 0.263 | 0.212 | 0.977 | 26.000 |
| wake only | held-out | 0.420 | 0.368 | 0.258 | 0.189 | 0.988 | 26.000 |

```
wake + presence:
  wake(B=0.43, w=0.131, t_lead=0.142, lam=0.1, k=78.4, zeta=0.154, mix=0.808, q=1.21)
  presence(A=0.187, sigma=0.136, mix=0.648, q=1.23)
wake only:
  wake(B=0.438, w=0.143, t_lead=0.243, lam=0.1, k=56.7, zeta=0.154, mix=0.792, q=1.26)
```

## Baked bend texture: cell size versus error

Two-term model baked to a grid over the 10 m field each frame, then bilinearly sampled per stalk.
Bake cost is per cell per frame; divide by your stalk count for the per-stalk share. Sampling adds ~12 ops per vertex (or per instance).

| grid | cell (m) | E_all | E_late | E coarse16 late | bake ops per cell |
|---|---|---|---|---|---|
| direct tokens | - | 0.404 | 0.348 | 0.223 | 48 per stalk |
| 10x10 | 1.00 | 0.773 | 0.757 | 0.593 | 48 |
| 16x16 | 0.62 | 0.620 | 0.574 | 0.367 | 48 |
| 20x20 | 0.50 | 0.550 | 0.528 | 0.345 | 48 |
| 25x25 | 0.40 | 0.503 | 0.473 | 0.271 | 48 |
| 32x32 | 0.31 | 0.458 | 0.432 | 0.243 | 48 |
| 40x40 | 0.25 | 0.404 | 0.348 | 0.223 | 48 |
| 50x50 | 0.20 | 0.424 | 0.389 | 0.234 | 48 |
| 64x64 | 0.16 | 0.425 | 0.396 | 0.227 | 48 |
| 80x80 | 0.12 | 0.416 | 0.378 | 0.229 | 48 |
