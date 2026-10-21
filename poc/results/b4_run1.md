# Math Track B4 results: corner law under the local supremum

Preregistration: `docs/math-track-b4-prereg.md`.

## H0 transfer invariance (sup score; RMS on the same runs as the dilution control)

| threshold | N_corner L=4 | L=8 | L=16 | L=32 | max/min | pass |
|---|---|---|---|---|---|---|
| sup 4.84 mm | None | None | None | None | - | False |
| sup 9.68 mm | None | None | None | None | - | False |
| sup 19.35 mm | None | None | None | None | - | False |
| sup 38.70 mm | None | None | None | None | - | False |
| rms 0.65 mm (control) | None | None | None | None | 32/4 = - | |
| rms 1.30 mm (control) | None | None | None | None | 32/4 = - | |
| rms 2.61 mm (control) | None | None | None | 5 | 32/4 = - | |
| rms 5.21 mm (control) | None | None | None | 5 | 32/4 = - | |

H0 pass: True; dilution control (RMS ratio >= 1.5 at primaries): False.

## Calibration: m_par = 0.0493 (per threshold: 4.84 mm: 0.0024, 9.68 mm: 0.0389, 19.35 mm: 0.1435, 38.70 mm: 0.4496)

| eps (mm) | A | B |
|---|---|---|

## Per trajectory (N at sup thresholds, then RMS thresholds)

| trajectory | N_event | K | turning | sup 4.8 | sup 9.7 | sup 19.3 | sup 38.7 | rms 0.65 | rms 1.30 | rms 2.61 | rms 5.21 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| straight | 4 | 0.00 | 0.00 | 14 | 14 | 10 | 10 | 10 | 8 | 8 | 8 |
| s_curve | 4 | 0.00 | 3.60 | 228 | 107 | 58 | 31 | 78 | 51 | 27 | 23 |
| stop_start | 16 | 0.00 | 0.00 | 54 | 54 | 34 | 34 | 38 | 34 | 26 | 26 |
| slalom | 4 | 0.00 | 11.99 | None | None | 286 | 74 | 286 | 143 | 67 | 67 |
| zigzag | 4 | 6.92 | 7.69 | 223 | 135 | 135 | 58 | 127 | 58 | 28 | 24 |
| wandering | 12 | 1.90 | 4.23 | None | 230 | 92 | 60 | 121 | 64 | 53 | 36 |
| circle | 4 | 0.00 | 4.80 | 259 | 135 | 69 | 37 | 135 | 69 | 37 | 37 |
| tangential_probe | 4 | 0.00 | 0.00 | 34 | 34 | 24 | 17 | 24 | 16 | 12 | 10 |
| corner_L4 | 4 | 1.38 | 1.57 | None | None | None | None | None | None | None | None |
| straight_L4 | 4 | 0.00 | 0.00 | None | None | None | None | None | None | None | None |
| corner_L8 | 4 | 1.38 | 1.57 | None | None | None | None | None | None | None | None |
| straight_L8 | 4 | 0.00 | 0.00 | None | None | None | None | None | None | None | None |
| corner_L16 | 4 | 1.38 | 1.57 | None | None | None | None | None | None | None | None |
| straight_L16 | 4 | 0.00 | 0.00 | None | None | None | None | None | None | None | 8 |
| corner_L32 | 4 | 1.38 | 1.57 | None | 80 | 46 | 31 | 19 | 13 | 13 | 13 |
| straight_L32 | 4 | 0.00 | 0.00 | None | None | None | None | None | None | 8 | 8 |

## Holdout predictions and tests

## H4 at 19.35 mm: corner-bin excess fraction = 1.0, pass True

| trajectory | rho clean | clean bins | corner excess |
|---|---|---|---|
| straight | nan | 10 | None |
| s_curve | 0.76 | 10 | None |
| stop_start | - | 4 | None |
| slalom | 0.2 | 10 | None |
| zigzag | - | 3 | [True, True, True, True, True, True, True] |
| wandering | 0.2 | 6 | [True] |
