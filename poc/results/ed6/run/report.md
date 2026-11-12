# ED6 report (frozen scorer)

## distilgpt2

| condition | matrix | base test loss | peak test gain (step) | training gain at the peak | turned | kept: at `g*` | at step 60 | at the validation minimum | at the last step | steps run |
|---|---|---|---|---|---|---|---|---|---|---|
| distilgpt2-none-8 | 1.mlp.c_proj | 6.320 | +0.297 (40) | 1.13 | yes | 1.00 | 0.19 | 0.99 | -2.60 | 90 |
| distilgpt2-none-8 | 4.mlp.c_proj | 6.320 | +0.382 (60) | 1.23 | yes | 0.97 | 1.00 | 1.00 | -0.17 | 110 |
| distilgpt2-none-8 | 1.attn.c_attn[1536:2304] | 6.320 | +0.264 (70) | 0.81 | yes | 0.90 | 0.94 | 1.00 | +0.07 | 130 |
| distilgpt2-none-8 | 4.attn.c_proj | 6.320 | +0.279 (120) | 1.21 | yes | 0.98 | 0.51 | 0.99 | -0.05 | 210 |
| distilgpt2-leet-8 | 1.mlp.c_proj | 6.368 | +0.738 (50) | 1.59 | yes | 0.98 | 0.96 | 0.94 | -0.81 | 100 |
| distilgpt2-leet-8 | 4.mlp.c_proj | 6.368 | +1.008 (70) | 1.72 | yes | 0.97 | 0.99 | 0.99 | +0.21 | 140 |
| distilgpt2-leet-8 | 1.attn.c_attn[1536:2304] | 6.368 | +0.416 (90) | 1.25 | yes | 0.98 | 0.74 | 0.95 | +0.03 | 150 |
| distilgpt2-leet-8 | 4.attn.c_proj | 6.368 | +0.737 (120) | 1.58 | yes | 0.99 | 0.57 | 0.99 | +0.14 | 210 |
| distilgpt2-none-32 | 1.mlp.c_proj | 6.357 | +0.459 (50) | 0.90 | yes | 0.99 | 1.00 | 1.00 | +0.21 | 150 |
| distilgpt2-none-32 | 4.mlp.c_proj | 6.357 | +0.581 (90) | 1.18 | yes | 0.98 | 0.89 | 0.99 | +0.23 | 320 |
| distilgpt2-none-32 | 1.attn.c_attn[1536:2304] | 6.357 | +0.418 (160) | 0.99 | yes | 0.99 | 0.74 | 0.96 | +0.21 | 310 |
| distilgpt2-none-32 | 4.attn.c_proj | 6.357 | +0.478 (190) | 1.08 | yes | 1.00 | 0.39 | 1.00 | +0.20 | 450 |

| condition | text, contexts | training gain at the test peak: mean, c.v. | half-fit knees: c.v., turned | `g*` | seconds |
|---|---|---|---|---|---|
| distilgpt2-none-8 | none, 8 | 1.09, 0.15 | 0.16, 8 of 8 | 1.03 | 204 |
| distilgpt2-leet-8 | leet, 8 | 1.53, 0.11 | 0.42, 8 of 8 | 1.42 | 205 |
| distilgpt2-none-32 | none, 32 | 1.04, 0.10 | 0.18, 8 of 8 | 1.05 | 894 |

**E1, the knee is common to the matrices**: c.v. 0.15, 0.11, 0.10 (needs below 0.35 in every condition). **holds**.

**E2, the rule keeps the gain**: positive in 12 of 12 (needs all); at least 67% of the peak in 12 (needs 10, and 3 in every condition: 4, 4, 4). **holds**.

**E3, long fits go bad**: 12 of 12 fell to a quarter of their peak within the cap (needs 10). **holds**.

**E4, the rule is at least as good as the 60-step budget**: mean share of the peak 0.976 against 0.743. **holds**.

Reported: share of the peak kept, mean and lowest: at `g*` 0.98, 0.90; at step 60 0.74, 0.19; at the validation minimum 0.98, 0.94; at the last step -0.19, -2.60. Fits that never reached `g*`: 0. Fits below the unadapted model at their last step: 4.

**distilgpt2: A** (E1 holds, E2 holds, E3 holds, E4 holds)

## openai-gpt

| condition | matrix | base test loss | peak test gain (step) | training gain at the peak | turned | kept: at `g*` | at step 60 | at the validation minimum | at the last step | steps run |
|---|---|---|---|---|---|---|---|---|---|---|
| openai-gpt-none-8 | 2.mlp.c_proj | 6.401 | +0.256 (50) | 0.96 | yes | 0.96 | 0.92 | 1.00 | -0.98 | 100 |
| openai-gpt-none-8 | 8.mlp.c_proj | 6.401 | +0.264 (30) | 1.00 | yes | 0.92 | -0.59 | 1.00 | -2.29 | 80 |
| openai-gpt-none-8 | 2.attn.c_attn[1536:2304] | 6.401 | +0.232 (110) | 1.09 | yes | 0.77 | 0.76 | 0.97 | +0.23 | 180 |
| openai-gpt-none-8 | 8.attn.c_proj | 6.401 | +0.118 (80) | 1.02 | yes | 0.94 | 0.84 | 1.00 | -0.07 | 140 |
| openai-gpt-leet-8 | 2.mlp.c_proj | 6.220 | +0.904 (80) | 1.84 | yes | 0.99 | 0.94 | 0.99 | +0.24 | 180 |
| openai-gpt-leet-8 | 8.mlp.c_proj | 6.220 | +1.092 (60) | 2.22 | yes | 0.98 | 1.00 | 1.00 | +0.23 | 290 |
| openai-gpt-leet-8 | 2.attn.c_attn[1536:2304] | 6.220 | +1.004 (360) | 2.03 | yes | 1.00 | 0.67 | 1.00 | +0.22 | 680 |
| openai-gpt-leet-8 | 8.attn.c_proj | 6.220 | +1.015 (150) | 2.54 | yes | 0.96 | 0.71 | 1.00 | +0.24 | 550 |
| openai-gpt-none-32 | 2.mlp.c_proj | 6.324 | +0.378 (70) | 0.91 | yes | 1.00 | 0.95 | 1.00 | +0.24 | 160 |
| openai-gpt-none-32 | 8.mlp.c_proj | 6.324 | +0.427 (50) | 1.11 | yes | 1.00 | 0.98 | 0.98 | +0.21 | 150 |
| openai-gpt-none-32 | 2.attn.c_attn[1536:2304] | 6.324 | +0.380 (110) | 0.81 | yes | 0.86 | 0.72 | 0.89 | +0.08 | 590 |
| openai-gpt-none-32 | 8.attn.c_proj | 6.324 | +0.400 (110) | 1.00 | yes | 1.00 | 0.73 | 0.98 | +0.21 | 280 |

| condition | text, contexts | training gain at the test peak: mean, c.v. | half-fit knees: c.v., turned | `g*` | seconds |
|---|---|---|---|---|---|
| openai-gpt-none-8 | none, 8 | 1.02, 0.05 | 0.73, 8 of 8 | 0.81 | 254 |
| openai-gpt-leet-8 | leet, 8 | 2.16, 0.12 | 0.21, 8 of 8 | 2.04 | 669 |
| openai-gpt-none-32 | none, 32 | 0.96, 0.12 | 0.21, 8 of 8 | 1.01 | 1245 |

**E1, the knee is common to the matrices**: c.v. 0.05, 0.12, 0.12 (needs below 0.35 in every condition). **holds**.

**E2, the rule keeps the gain**: positive in 12 of 12 (needs all); at least 67% of the peak in 12 (needs 10, and 3 in every condition: 4, 4, 4). **holds**.

**E3, long fits go bad**: 12 of 12 fell to a quarter of their peak within the cap (needs 10). **holds**.

**E4, the rule is at least as good as the 60-step budget**: mean share of the peak 0.949 against 0.720. **holds**.

Reported: share of the peak kept, mean and lowest: at `g*` 0.95, 0.77; at step 60 0.72, -0.59; at the validation minimum 0.98, 0.89; at the last step -0.12, -2.29. Fits that never reached `g*`: 0. Fits below the unadapted model at their last step: 3.

**openai-gpt: A** (E1 holds, E2 holds, E3 holds, E4 holds)

## gpt2-medium

| condition | matrix | base test loss | peak test gain (step) | training gain at the peak | turned | kept: at `g*` | at step 60 | at the validation minimum | at the last step | steps run |
|---|---|---|---|---|---|---|---|---|---|---|
| gpt2-medium-none-8 | 4.mlp.c_proj | 6.293 | +0.560 (50) | 1.42 | yes | 0.71 | 0.97 | 0.97 | -1.18 | 100 |
| gpt2-medium-none-8 | 16.mlp.c_proj | 6.293 | +0.620 (60) | 1.58 | yes | 0.89 | 1.00 | 1.00 | -0.68 | 110 |
| gpt2-medium-none-8 | 4.attn.c_attn[2048:3072] | 6.293 | +0.446 (120) | 1.40 | yes | 0.82 | 0.52 | 0.99 | +0.17 | 210 |
| gpt2-medium-none-8 | 16.attn.c_proj | 6.293 | +0.585 (150) | 1.62 | yes | 0.91 | 0.33 | 1.00 | +0.11 | 230 |
| gpt2-medium-leet-8 | 4.mlp.c_proj | 6.279 | +1.012 (70) | 1.96 | yes | 0.99 | 0.97 | 0.97 | -0.70 | 120 |
| gpt2-medium-leet-8 | 16.mlp.c_proj | 6.279 | +1.078 (70) | 1.97 | yes | 0.99 | 0.94 | 1.00 | +0.04 | 120 |
| gpt2-medium-leet-8 | 4.attn.c_attn[2048:3072] | 6.279 | +0.453 (100) | 1.19 | yes | 0.48 | 0.83 | 1.00 | +0.25 | 150 |
| gpt2-medium-leet-8 | 16.attn.c_proj | 6.279 | +0.950 (150) | 2.06 | yes | 1.00 | 0.37 | 1.00 | +0.04 | 230 |
| gpt2-medium-none-32 | 4.mlp.c_proj | 6.052 | +0.736 (80) | 1.38 | yes | 1.00 | 0.94 | 0.99 | +0.20 | 160 |
| gpt2-medium-none-32 | 16.mlp.c_proj | 6.052 | +0.769 (90) | 1.37 | yes | 1.00 | 0.88 | 1.00 | +0.24 | 210 |
| gpt2-medium-none-32 | 4.attn.c_attn[2048:3072] | 6.052 | +0.621 (210) | 1.29 | yes | 0.99 | 0.62 | 1.00 | +0.22 | 400 |
| gpt2-medium-none-32 | 16.attn.c_proj | 6.052 | +0.768 (230) | 1.43 | yes | 0.99 | 0.32 | 1.00 | +0.23 | 470 |

| condition | text, contexts | training gain at the test peak: mean, c.v. | half-fit knees: c.v., turned | `g*` | seconds |
|---|---|---|---|---|---|
| gpt2-medium-none-8 | none, 8 | 1.51, 0.07 | 0.32, 8 of 8 | 2.00 | 1127 |
| gpt2-medium-leet-8 | leet, 8 | 1.80, 0.20 | 0.29, 8 of 8 | 2.21 | 991 |
| gpt2-medium-none-32 | none, 32 | 1.37, 0.04 | 0.18, 8 of 8 | 1.37 | 4286 |

**E1, the knee is common to the matrices**: c.v. 0.07, 0.20, 0.04 (needs below 0.35 in every condition). **holds**.

**E2, the rule keeps the gain**: positive in 12 of 12 (needs all); at least 67% of the peak in 11 (needs 10, and 3 in every condition: 4, 3, 4). **holds**.

**E3, long fits go bad**: 12 of 12 fell to a quarter of their peak within the cap (needs 10). **holds**.

**E4, the rule is at least as good as the 60-step budget**: mean share of the peak 0.898 against 0.726. **holds**.

Reported: share of the peak kept, mean and lowest: at `g*` 0.90, 0.48; at step 60 0.73, 0.32; at the validation minimum 0.99, 0.97; at the last step -0.09, -1.18. Fits that never reached `g*`: 0. Fits below the unadapted model at their last step: 3.

**gpt2-medium: A** (E1 holds, E2 holds, E3 holds, E4 holds)

## Outcome: distilgpt2 **A**, openai-gpt **A**, gpt2-medium **A**; A on 3 of 3 models, the rule keeps the gain (A or B) on 3

