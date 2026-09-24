# Pond ripples: cheap tokens against the exact linear-wave teacher

Teacher: 256x256 spectral linear waves on a 6.0 m pond, depth 0.4 m, exact per-mode propagation with the full dispersion relation.

## Splash (one impulse), scored on points within 2 m for t >= 0.15 s

| token | height error | slope error | ops per point per live token |
|---|---|---|---|
| ring | 1.076 | 1.338 | 26 |
| chirp | 0.309 | 0.334 | 40 |

Fitted parameters:

```
ring: A=0.006921, lam=0.8488, v=1.072, w=0.3286, kappa=115.6, phi=2.935
chirp: A=0.1, lam=0.1059, m=0.3099, n=1.714, g_eff=9.801, phi=1.621, v_max=1.85, k_cut=54.02
```

## Wake (a 5 cm pressure bump dragged 3 m at 1 m/s), token: chirp

Huygens superposition of the splash-fitted token along the path, one global amplitude fitted.

| emission spacing | tokens | live tokens per point | height error |
|---|---|---|---|
| 0.02 m | 151 | 47.7 | 0.586 |
| 0.05 m | 61 | 19.2 | 0.587 |
| 0.10 m | 31 | 9.7 | 0.606 |
| 0.20 m | 16 | 5.0 | 0.697 |
