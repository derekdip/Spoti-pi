# Online stopping signals against the cross-fitted knee and held-out stopping

Share of each fit's peak test gain kept (stop step in brackets; `none` = the signal never fired, the fit's last step is used).

| condition | matrix | peak (step) | g* (rule) | share | disparity | eb | validation minimum |
|---|---|---|---|---|---|---|---|
| pilot-none-8 | transformer.h.2.mlp.c_proj | +0.463 (40) | 0.96 (60) | 1.00 (40) | 0.05 (10) | -0.20 (100) | 1.00 (40) |
| pilot-none-8 | transformer.h.8.mlp.c_proj | +0.523 (50) | 0.99 (60) | 1.00 (50) | 0.05 (10) | -0.01 (none) | 0.99 (60) |
| pilot-none-8 | transformer.h.2.attn.c_attn[1536:2304] | +0.287 (110) | 1.00 (110) | 0.71 (90) | 0.02 (10) | 0.56 (130) | 1.00 (110) |
| pilot-none-8 | transformer.h.8.attn.c_proj | +0.455 (110) | 1.00 (110) | 0.99 (100) | 0.01 (10) | 0.09 (none) | 0.98 (120) |
| pilot-none-32 | transformer.h.2.mlp.c_proj | +0.587 (60) | 0.96 (70) | 1.00 (60) | 0.05 (10) | 0.56 (110) | 1.00 (60) |
| pilot-none-32 | transformer.h.8.mlp.c_proj | +0.776 (80) | 1.00 (80) | 0.99 (70) | 0.04 (10) | 0.51 (180) | 0.99 (70) |
| pilot-none-32 | transformer.h.2.attn.c_attn[1536:2304] | +0.553 (120) | 0.93 (180) | 0.97 (100) | 0.01 (10) | 0.97 (100) | 1.00 (120) |
| pilot-none-32 | transformer.h.8.attn.c_proj | +0.723 (140) | 1.00 (140) | 1.00 (130) | 0.00 (10) | 0.46 (320) | 1.00 (130) |

| stop | mean share kept | lowest | at least 2/3 of the peak |
|---|---|---|---|
| rule | 0.98 | 0.93 | 8 of 8 |
| share | 0.96 | 0.71 | 8 of 8 |
| disparity | 0.03 | 0.00 | 0 of 8 |
| eb | 0.37 | -0.20 | 1 of 8 |
| val | 1.00 | 0.98 | 8 of 8 |
