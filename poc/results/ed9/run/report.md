# Larger adapters: the knee and the rule

| condition | adapter | matrices | trainable | peak test gain (step) | training gain at the peak | own g* | kept at own g* | kept at the shared g* | kept at the validation minimum | at the last step |
|---|---|---|---|---|---|---|---|---|---|---|
| none-8 | r2-one | 1 | 7680 | +0.398 (45) | 1.25 | 1.44 | 0.83 | 0.50 | 1.00 | +0.06 |
| none-8 | r8-one | 1 | 30720 | +0.406 (65) | 1.15 | 1.72 | 0.66 | 0.56 | 1.00 | +0.07 |
| none-8 | r32-one | 1 | 122880 | +0.396 (75) | 1.04 | 1.70 | 0.66 | 0.55 | 0.99 | +0.05 |
| none-8 | r2-all | 48 | 294912 | +0.514 (35) | 1.51 | 2.17 | 0.90 | 0.99 | 1.00 | +0.05 |
| none-8 | r8-all | 48 | 1179648 | +0.487 (55) | 1.79 | 1.94 | 0.98 | 0.99 | 1.00 | -0.03 |
| none-8 | r32-all | 48 | 4718592 | +0.440 (75) | 1.71 | 2.04 | 0.94 | 0.99 | 1.00 | +0.11 |
| none-8 | shared g* (median of all half-fits) | | | | | 1.83 | | | | |
| none-32 | r2-one | 1 | 7680 | +0.590 (80) | 1.22 | 1.25 | 1.00 | 0.72 | 0.99 | +0.12 |
| none-32 | r8-one | 1 | 30720 | +0.596 (105) | 1.16 | 1.34 | 0.98 | 0.80 | 0.99 | +0.12 |
| none-32 | r32-one | 1 | 122880 | +0.587 (145) | 1.12 | 1.42 | 0.93 | 0.77 | 1.00 | +0.14 |
| none-32 | r2-all | 48 | 294912 | +0.808 (60) | 1.91 | 1.91 | 1.00 | 0.99 | 1.00 | -0.10 |
| none-32 | r8-all | 48 | 1179648 | +0.816 (80) | 1.83 | 1.98 | 1.00 | 0.99 | 0.99 | +0.11 |
| none-32 | r32-all | 48 | 4718592 | +0.807 (120) | 1.89 | 1.93 | 1.00 | 0.98 | 1.00 | +0.02 |
| none-32 | shared g* (median of all half-fits) | | | | | 1.67 | | | | |
| leet-32 | r2-one | 1 | 7680 | +1.193 (105) | 1.65 | 1.51 | 0.99 | 1.00 | 1.00 | +0.28 |
| leet-32 | r8-one | 1 | 30720 | +1.155 (140) | 1.52 | 1.52 | 1.00 | 1.00 | 1.00 | +0.26 |
| leet-32 | r32-one | 1 | 122880 | +1.106 (205) | 1.54 | 1.48 | 1.00 | 1.00 | 1.00 | +0.27 |
| leet-32 | r2-all | 48 | 294912 | +1.394 (60) | 1.92 | 1.83 | 0.99 | 0.95 | 1.00 | +0.18 |
| leet-32 | r8-all | 48 | 1179648 | +1.350 (80) | 1.86 | 1.74 | 0.99 | 0.95 | 1.00 | +0.32 |
| leet-32 | r32-all | 48 | 4718592 | +1.259 (120) | 1.94 | 1.72 | 0.99 | 0.96 | 1.00 | +0.08 |
| leet-32 | shared g* (median of all half-fits) | | | | | 1.57 | | | | |

## Bars (docs/math-track-ed9-prereg.md)

- none-8: knee, one matrix 1.15 (c.v. 0.07); all matrices 1.67 (c.v. 0.07); ratio 1.46
- none-32: knee, one matrix 1.17 (c.v. 0.03); all matrices 1.88 (c.v. 0.02); ratio 1.61
- leet-32: knee, one matrix 1.57 (c.v. 0.04); all matrices 1.91 (c.v. 0.02); ratio 1.21
- **R1**, stopped at the own g*: positive in 18 of 18 (needs all), at least 67% of the peak in 16 (needs 15): **holds**
- **R2**, stopped at the shared g*: positive in 18 of 18 (needs all), at least 67% of the peak in 15 (needs 15): **holds**
- **B1**, rank does not move the knee within a reach: largest c.v. 0.07 (needs below 0.2): **holds**
- **B2**, reach moves it: smallest ratio of the all-matrix to the one-matrix knee 1.21 (needs above 1.2): **holds**
- Reported: share of the peak kept, mean, own g* 0.94, shared g* 0.87, validation minimum 1.00; fits that turned 18 of 18.
