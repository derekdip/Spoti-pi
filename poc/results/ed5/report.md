# ED5 report (frozen scorer)

| condition | matrix | peak test gain (step) | training gain at the peak | turned within the cap | kept: at `g*` | at step 60 | at the validation minimum | at the last step | steps run |
|---|---|---|---|---|---|---|---|---|---|
| none-32 | proj@2 | +0.710 (70) | 1.07 | yes | 1.00 | 0.98 | 1.00 | +0.23 | 160 |
| none-32 | proj@8 | +0.718 (80) | 1.16 | yes | 1.00 | 0.94 | 0.99 | +0.25 | 270 |
| none-32 | v@2 | +0.601 (120) | 0.87 | yes | 0.86 | 0.46 | 1.00 | +0.20 | 320 |
| none-32 | o@8 | +0.736 (160) | 1.20 | yes | 1.00 | 0.45 | 1.00 | +0.25 | 400 |
| leet-32 | proj@2 | +1.316 (110) | 1.69 | yes | 1.00 | 0.72 | 0.99 | +0.10 | 230 |
| leet-32 | proj@8 | +1.410 (140) | 1.81 | yes | 0.98 | 0.77 | 1.00 | +0.23 | 530 |
| leet-32 | v@2 | +1.043 (190) | 1.39 | yes | 0.99 | 0.49 | 0.99 | +0.25 | 540 |
| leet-32 | o@8 | +1.399 (200) | 1.77 | yes | 0.98 | 0.38 | 1.00 | +0.25 | 650 |
| none-64 | proj@2 | +0.576 (80) | 0.98 | yes | 0.98 | 0.95 | 0.98 | +0.24 | 220 |
| none-64 | proj@8 | +0.678 (120) | 1.15 | yes | 1.00 | 0.88 | 1.00 | +0.22 | 590 |
| none-64 | v@2 | +0.517 (180) | 0.88 | yes | 0.89 | 0.70 | 1.00 | +0.23 | 490 |
| none-64 | o@8 | +0.685 (200) | 1.11 | yes | 1.00 | 0.46 | 0.99 | +0.24 | 750 |

| condition | contexts | training gain at the test peak: mean, c.v. over the matrices | the eight half-fit knees | their c.v. | half-fits that turned | `g*` | seconds |
|---|---|---|---|---|---|---|---|
| none-32 | 32 | 1.07, 0.12 | 1.28 1.09 1.21 1.20 0.91 1.07 1.24 1.12 | 0.10 | 8 of 8 | 1.16 | 2494 |
| leet-32 | 32 | 1.67, 0.10 | 1.63 1.53 1.67 1.65 1.07 1.01 1.85 1.78 | 0.19 | 8 of 8 | 1.64 | 3870 |
| none-64 | 64 | 1.03, 0.10 | 1.19 1.15 1.12 1.16 0.73 0.92 1.06 1.21 | 0.14 | 8 of 8 | 1.13 | 7800 |

**E1, the knee is common to the matrices**: the c.v. of the training gain at the test peak is 0.12 (none-32), 0.10 (leet-32), 0.10 (none-64) (needs below 0.35 in every condition). **holds**.

**E2, the rule keeps the gain**: stopped at `g*`, the test gain is positive in 12 of 12 fits (needs all) and at least 67% of the peak in 12 (needs 10, and 3 in every condition: 4 (none-32), 4 (leet-32), 4 (none-64)). **holds**.

**E3, long fits go bad at this size**: the test gain fell to a quarter of its peak within the cap in 12 of 12 fits (needs 10). **holds**.

**E4, the rule is at least as good as the 60-step budget**: mean share of the peak kept 0.972 against 0.681. **holds**.

## Reported

- Share of the peak kept, mean and lowest over the 12 fits: at `g*` 0.97, 0.86; at step 60 0.68, 0.38; at the validation minimum 0.99, 0.98; at the last step +0.22, +0.10.
- Fits whose training gain never reached `g*` before they stopped: 0. Fits below the unadapted model at their last step: 0.
- Test gain over training gain in the first 30 steps: none-32 0.77 0.88 0.63 0.80; leet-32 0.99 1.01 0.95 0.92; none-64 0.74 0.84 0.72 0.78.

## Outcome: **A** (E1 holds, E2 holds, E3 holds, E4 holds)

