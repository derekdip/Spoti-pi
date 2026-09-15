# Pond ripples: cheap tokens against the exact linear-wave teacher

Teacher: 256x256 spectral linear waves on a 6.0 m pond, depth 0.4 m, exact per-mode propagation with the full dispersion relation.

## Splash (one impulse), scored on points within 2 m for t >= 0.15 s

| token | height error | slope error | ops per point per live token |
|---|---|---|---|
| ring | 1.076 | 1.338 | 26 |
| chirp | 0.494 | 0.647 | 34 |

Fitted parameters:

```
ring: A=0.006921, lam=0.8488, v=1.072, w=0.3286, kappa=115.6, phi=2.935
chirp: A=0.005378, lam=0.2149, m=-1, n=0.04654, g_eff=9.807, phi=1.579, v_max=0.8732
```

## Wake (a 5 cm pressure bump dragged 3 m at 1 m/s), token: chirp

Huygens superposition of the splash-fitted token along the path, one global amplitude fitted.

| emission spacing | tokens | live tokens per point | height error |
|---|---|---|---|
| 0.02 m | 151 | 54.3 | 0.582 |
| 0.05 m | 61 | 21.9 | 0.588 |
| 0.10 m | 31 | 11.1 | 0.612 |
| 0.20 m | 16 | 5.7 | 0.696 |

Token shape refitted on the wake itself at 5 cm spacing: height error 1.019, 2.6 live tokens per point.

