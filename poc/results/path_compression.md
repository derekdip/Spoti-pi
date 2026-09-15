# Path compression: spatial vs spacetime vs behaviour-weighted (preregistered)

Prediction stated before the run: E_behaviour(N) < E_spacetime(N) < E_spatial(N) on held-out, strongest at the wake front; exponent toward -0.5.

Fitted wake kernel slopes: L_x = 3.231 per m, L_t = 4.617 per s, so the behaviour-weighted time scale is c_t = L_t / L_x = 1.43 m/s (mean walking speed 1.63 m/s). Excess error is relative to the dense 200 Hz path as token.

## Equal point counts, held-out walk (excess visual error, all frames / wake front)

| N | spatial | spacetime | behaviour |
|---|---|---|---|
| 5 | 0.3006 / 0.3320 | 0.1518 / 0.1624 | 0.1482 / 0.1605 |
| 6 | 0.1343 / 0.1582 | 0.1255 / 0.1076 | 0.1218 / 0.1053 |
| 8 | 0.0668 / 0.0819 | 0.0240 / 0.0371 | 0.0226 / 0.0362 |
| 10 | 0.0650 / 0.0779 | 0.0067 / 0.0162 | 0.0061 / 0.0158 |
| 12 | 0.0463 / 0.0500 | 0.0048 / 0.0107 | 0.0046 / 0.0106 |
| 16 | 0.0313 / 0.0274 | 0.0045 / 0.0072 | 0.0046 / 0.0075 |
| 20 | 0.0254 / 0.0209 | 0.0001 / 0.0001 | 0.0001 / 0.0015 |
| 24 | 0.0207 / 0.0165 | 0.0000 / 0.0000 | 0.0000 / 0.0010 |
| 32 | 0.0181 / 0.0138 | 0.0000 / 0.0027 | 0.0000 / 0.0032 |
| 48 | - | 0.0000 / 0.0029 | 0.0000 / 0.0031 |

## Equal point counts, training walk (excess visual error, all frames / wake front)

| N | spatial | spacetime | behaviour |
|---|---|---|---|
| 5 | 0.1850 / 0.1800 | 0.2783 / 0.2376 | 0.2762 / 0.2353 |
| 6 | 0.1286 / 0.1369 | 0.2283 / 0.1900 | 0.2233 / 0.1865 |
| 8 | 0.0673 / 0.0844 | 0.1329 / 0.1110 | 0.1281 / 0.1091 |
| 10 | 0.0582 / 0.0761 | 0.0486 / 0.0425 | 0.0468 / 0.0428 |
| 12 | 0.0445 / 0.0636 | 0.0151 / 0.0138 | 0.0145 / 0.0143 |
| 16 | 0.0353 / 0.0408 | 0.0000 / 0.0046 | 0.0063 / 0.0094 |
| 20 | 0.0296 / 0.0352 | 0.0000 / 0.0013 | 0.0000 / 0.0018 |
| 24 | 0.0256 / 0.0312 | 0.0000 / 0.0008 | 0.0000 / 0.0009 |
| 32 | 0.0195 / 0.0179 | 0.0000 / 0.0007 | 0.0000 / 0.0007 |
| 48 | 0.0057 / 0.0143 | 0.0000 / 0.0004 | 0.0000 / 0.0003 |

Held-out ordering behaviour < spacetime < spatial held at 5 of 9 point counts on all frames and 5 of 9 at the wake front.

## Exponents: points against excess error (log-log, both walks)

| method | all frames | wake front |
|---|---|---|
| spatial | -0.68 | -0.74 |
| spacetime | -0.33 | -0.34 |
| behaviour | -0.30 | -0.32 |

Prediction was -0.5; the earlier spatial-only estimate was -0.73.

## Corrected liveness bound (monotone future envelope)

beta = min(lam, c/2) = 9.33 1/s, C_s = 10.59.

| eps | live tokens (future envelope) | bound (R/beta) log(C_s/eps) |
|---|---|---|
| 1e-01 | 1.05 | 1.50 |
| 1e-02 | 1.33 | 2.24 |
| 1e-03 | 1.46 | 2.98 |
| 1e-04 | 2.69 | 3.72 |
| 1e-05 | 2.95 | 4.46 |
