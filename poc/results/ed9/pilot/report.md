# Larger adapters: the knee and the rule

| condition | adapter | matrices | trainable | peak test gain (step) | training gain at the peak | own g* | kept at own g* | kept at the shared g* | kept at the validation minimum | at the last step |
|---|---|---|---|---|---|---|---|---|---|---|
| pilot-none-8 | r2-one | 1 | 7680 | +0.419 (50) | 1.26 | 2.16 | -0.38 | -0.62 | 1.00 | -0.92 |
| pilot-none-8 | r32-one | 1 | 122880 | +0.410 (20) | 1.65 | 1.53 | 0.94 | 0.40 | 1.00 | -3.50 |
| pilot-none-8 | r8-all | 48 | 1179648 | +0.540 (10) | 2.47 | 2.24 | 0.95 | 0.96 | 1.00 | -4.05 |
| pilot-none-8 | r32-all | 48 | 4718592 | +0.520 (5) | 2.54 | 3.30 | -0.11 | 0.91 | 1.00 | -4.58 |
| pilot-none-8 | shared g* (median of all half-fits) | | | | | 2.30 | | | | |
