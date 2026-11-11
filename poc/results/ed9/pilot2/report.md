# Larger adapters: the knee and the rule

| condition | adapter | matrices | trainable | peak test gain (step) | training gain at the peak | own g* | kept at own g* | kept at the shared g* | kept at the validation minimum | at the last step |
|---|---|---|---|---|---|---|---|---|---|---|
| pilot2-none-8 | r2-one-lr5e-4 | 1 | 7680 | +0.419 (85) | 1.27 | 2.09 | 0.15 | 0.15 | 1.00 | +0.06 |
| pilot2-none-8 | r32-one-lr1e-4 | 1 | 122880 | +0.427 (105) | 1.38 | 1.99 | 0.71 | 0.23 | 0.99 | +0.03 |
| pilot2-none-8 | r8-all-lr1e-4 | 48 | 1179648 | +0.555 (55) | 1.95 | 2.56 | 0.93 | 0.98 | 1.00 | +0.08 |
| pilot2-none-8 | r8-all-lr3e-5 | 48 | 1179648 | +0.525 (140) | 1.80 | 2.72 | 0.81 | 0.94 | 1.00 | +0.13 |
| pilot2-none-8 | r32-all-lr3e-5 | 48 | 4718592 | +0.523 (75) | 1.85 | 2.58 | 0.90 | 0.97 | 1.00 | +0.00 |
| pilot2-none-8 | r32-all-lr1e-5 | 48 | 4718592 | +0.503 (190) | 1.79 | 2.90 | 0.73 | 0.95 | 1.00 | +0.12 |
| pilot2-none-8 | shared g* (median of all half-fits) | | | | | 2.30 | | | | |

## Bars (docs/math-track-ed9-prereg.md)

- pilot2-none-8: knee, one matrix 1.32 (c.v. 0.04); all matrices 1.85 (c.v. 0.03); ratio 1.39
- **R1**, stopped at the own g*: positive in 6 of 6 (needs all), at least 67% of the peak in 5 (needs 5): **holds**
- **R2**, stopped at the shared g*: positive in 6 of 6 (needs all), at least 67% of the peak in 4 (needs 5): **fails**
- **B1**, rank does not move the knee within a reach: largest c.v. 0.04 (needs below 0.2): **holds**
- **B2**, reach moves it: smallest ratio of the all-matrix to the one-matrix knee 1.39 (needs above 1.2): **holds**
- Reported: share of the peak kept, mean, own g* 0.71, shared g* 0.70, validation minimum 1.00; fits that turned 6 of 6.
