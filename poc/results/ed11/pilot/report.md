# ED11: the online share on Adam's step

Share of each fit's peak test gain kept (stopping step; `none`: never fired, the last step is used).

| condition | adapter | peak (step) | rule | share_adam | share | share_single | disparity_rel | validation minimum |
|---|---|---|---|---|---|---|---|---|
| pilot-none-16 | proj@2 | +0.501 (70) | 0.48 (40) | 0.39 (30) | 1.00 (70) | 0.92 (60) | 0.03 (10) | 1.00 (70) |
| pilot-none-16 | v@2 | +0.193 (100) | 0.88 (70) | 0.16 (20) | 0.96 (90) | 0.88 (80) | 0.03 (10) | 0.96 (90) |
| pilot-none-16 | r2-all | +0.655 (50) | 0.99 (45) | 0.07 (10) | 0.03 (70) | 0.42 (65) | 0.07 (10) | 1.00 (45) |
| pilot-none-16 | r8-all | +0.651 (65) | 0.97 (60) | 0.05 (10) | 0.05 (none) | 0.05 (none) | 0.26 (25) | 1.00 (65) |

| stop | mean share kept | lowest | at least 2/3 of the peak | positive |
|---|---|---|---|---|
| rule | 0.83 | 0.48 | 3 of 4 | 4 of 4 |
| share_adam | 0.17 | 0.05 | 0 of 4 | 4 of 4 |
| share | 0.51 | 0.03 | 2 of 4 | 4 of 4 |
| share_single | 0.57 | 0.05 | 2 of 4 | 4 of 4 |
| disparity_rel | 0.10 | 0.03 | 0 of 4 | 4 of 4 |
| val | 0.99 | 0.96 | 4 of 4 | 4 of 4 |

| condition | reach | rule | share_adam | share | share_single | disparity_rel | val |
|---|---|---|---|---|---|---|---|
| pilot-none-16 | one | 0.68 | 0.27 | 0.98 | 0.90 | 0.03 | 0.98 |
| pilot-none-16 | all | 0.98 | 0.06 | 0.04 | 0.23 | 0.16 | 1.00 |
