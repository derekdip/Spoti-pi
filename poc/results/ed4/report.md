# ED4 report (frozen scorer)

Placement selector `line`, beam of 3; the fixed choice is `proj@8`, `proj@2`, `proj@5`. Losses are on the test contexts.

## Placement

| condition | base loss | sweep's best module, gain | line: best gain in beam | the fixed choice: best gain in beam | rgn: best gain in beam | gradnorm: best gain in beam | random: best gain in beam | `line` beam |
|---|---|---|---|---|---|---|---|---|
| leet-32 | 6.266 | proj@8 +1.049 | +1.049 | +1.049 | +0.573 | +0.573 | +0.887 | v@11, proj@8, o@8 |
| devowel-32 | 6.460 | proj@8 +0.880 | +0.687 | +0.880 | +0.476 | +0.476 | +0.741 | v@11, proj@11, fc@11 |
| reverse-32 | 7.413 | proj@8 +0.922 | +0.641 | +0.922 | +0.847 | +0.847 | +0.755 | v@11, proj@11, fc@11 |
| none-32 | 6.169 | proj@5 +0.656 | +0.362 | +0.656 | +0.479 | +0.479 | +0.555 | v@11, o@8, v@8 |

**H1, the pre-screen picks well**: the `line` beam reaches at least 90% of the sweep's best gain on 1 of 4 conditions (needs 3, and at least 3 conditions); its mean best test loss is 5.892 against random 5.843, rgn 5.983, gradnorm 5.983 (needs to be below all three). **fails**.

**H1p, it is no worse than a fixed choice**: mean best test loss 5.892 against the fixed choice's 5.700 (needs to be within 0.01 nats above it, or below). **fails**.

## Stopping

| condition | module | `rho` | cross-fitted share | peak test gain (step) | test gain at the end | kept | gain when stopped at the validation minimum (step) | share of the peak | training gain at the end |
|---|---|---|---|---|---|---|---|---|---|
| stop-leet-8 | v@2 | +0.57 | +0.46 | +0.479 (100) | -1.771 | -3.70 | +0.479 (100) | 1.00 | +4.12 |
| stop-leet-8 | o@2 | +0.57 | +0.40 | +0.614 (100) | -2.031 | -3.31 | +0.599 (90) | 0.98 | +5.32 |
| stop-leet-8 | fc@2 | +0.57 | +0.53 | +0.591 (70) | -2.260 | -3.82 | +0.591 (70) | 1.00 | +5.76 |
| stop-leet-8 | proj@2 | +0.57 | +0.64 | +0.592 (60) | -3.072 | -5.18 | +0.592 (60) | 1.00 | +5.71 |
| stop-leet-8 | v@8 | +0.53 | +0.60 | +0.799 (140) | -0.684 | -0.86 | +0.799 (140) | 1.00 | +3.93 |
| stop-leet-8 | o@8 | +0.43 | +0.44 | +0.640 (130) | -1.443 | -2.25 | +0.638 (120) | 1.00 | +4.88 |
| stop-leet-8 | fc@8 | +0.44 | +0.59 | +0.750 (70) | -1.635 | -2.18 | +0.750 (70) | 1.00 | +5.64 |
| stop-leet-8 | proj@8 | +0.58 | +0.63 | +0.931 (90) | -1.279 | -1.37 | +0.931 (90) | 1.00 | +5.10 |
| stop-none-8 | v@2 | +0.31 | +0.11 | +0.332 (90) | -1.414 | -4.26 | +0.332 (90) | 1.00 | +3.08 |
| stop-none-8 | o@2 | +0.29 | +0.13 | +0.441 (90) | -2.800 | -6.36 | +0.441 (90) | 1.00 | +4.71 |
| stop-none-8 | fc@2 | +0.31 | +0.33 | +0.429 (70) | -2.660 | -6.19 | +0.429 (70) | 1.00 | +5.79 |
| stop-none-8 | proj@2 | +0.29 | +0.32 | +0.422 (50) | -4.342 | -10.28 | +0.422 (50) | 1.00 | +5.78 |
| stop-none-8 | v@8 | +0.44 | +0.42 | +0.436 (100) | -1.907 | -4.38 | +0.436 (100) | 1.00 | +4.04 |
| stop-none-8 | o@8 | +0.34 | +0.22 | +0.477 (100) | -2.168 | -4.54 | +0.477 (100) | 1.00 | +4.05 |
| stop-none-8 | fc@8 | +0.35 | +0.57 | +0.374 (70) | -3.263 | -8.72 | +0.374 (70) | 1.00 | +5.70 |
| stop-none-8 | proj@8 | +0.44 | +0.50 | +0.502 (50) | -2.433 | -4.85 | +0.502 (50) | 1.00 | +4.80 |

**H2a, a long fit goes bad whatever the share**: the test gain at the end is below 50% of its peak in 16 of 16 fits (needs all). **holds**. Of the 6 fits with `rho` above one half, 6 are among them; 16 of 16 end below the unadapted model.

**H2b, stopping on validation keeps the gain**: stopping at the validation minimum keeps at least 90% of the peak test gain in 16 of 16 fits (needs 14). **holds**.

## Reported

Rank correlation of each score with the fitted test gain; * marks a beam that holds the sweep's best module.

| condition | slope | line | step | trainslope | trainline | cfslope | rgn | gradnorm | the fixed choice |
|---|---|---|---|---|---|---|---|---|---|
| leet-32 | -0.16 | +0.15 * | +0.17 * | -0.05 | +0.23 * | -0.11 | -0.36 | -0.37 | * |
| devowel-32 | +0.04 | +0.21 | +0.46 | -0.02 | +0.16 | +0.06 | -0.45 | -0.44 | * |
| reverse-32 | -0.06 | +0.03 | +0.22 * | -0.11 | -0.06 | -0.04 | -0.31 | -0.27 | * |
| none-32 | +0.28 | -0.10 | +0.16 * | +0.27 | +0.18 | +0.45 | +0.03 | +0.03 | * |

- leet-32: fitted test gains proj@8 +1.049, proj@5 +1.017, fc@8 +0.906, proj@2 +0.869, fc@11 +0.860, fc@5 +0.849, fc@2 +0.820, o@5 +0.627, proj@11 +0.627, o@11 +0.616, o@2 +0.573, v@8 +0.530, v@11 +0.499, o@8 +0.498, v@2 +0.464, v@5 +0.421; seconds: scores 83, fits 1591

- devowel-32: fitted test gains proj@8 +0.880, proj@5 +0.795, proj@2 +0.774, fc@8 +0.732, fc@2 +0.695, fc@5 +0.693, fc@11 +0.687, proj@11 +0.609, o@11 +0.585, o@5 +0.568, v@11 +0.493, o@2 +0.476, v@8 +0.446, o@8 +0.439, v@5 +0.377, v@2 +0.349; seconds: scores 90, fits 1630

- reverse-32: fitted test gains proj@8 +0.922, proj@2 +0.847, proj@5 +0.782, fc@8 +0.723, fc@5 +0.705, fc@2 +0.686, fc@11 +0.641, o@2 +0.624, proj@11 +0.560, o@5 +0.549, o@11 +0.533, v@8 +0.478, o@8 +0.443, v@11 +0.434, v@2 +0.406, v@5 +0.377; seconds: scores 468, fits 1818

- none-32: fitted test gains proj@5 +0.656, proj@8 +0.650, proj@2 +0.570, fc@5 +0.534, o@5 +0.512, fc@2 +0.502, o@2 +0.479, fc@8 +0.444, fc@11 +0.422, v@2 +0.409, proj@11 +0.390, v@8 +0.362, o@8 +0.362, o@11 +0.321, v@5 +0.277, v@11 +0.265; seconds: scores 468, fits 1649

- stop-leet-8: rank correlation with the test gain at the end: `rho` -0.21, cross-fitted share +0.07; seconds 1743

- stop-none-8: rank correlation with the test gain at the end: `rho` +0.48, cross-fitted share -0.31; seconds 1755

## Outcome: placement **C** (H1 fails, H1p fails); stopping **confirmed** (H2a holds, H2b holds)

