# ED3 report (frozen scorer)

## G1, the planted module under a format shift

Truth EXPAND:fc@7; got EXPAND:fc@7; first stage GLOBALIZE; budget gain 0.006; restarts beating the first fit 0 of 2.
The planted module in the held-out-gain beam: True; in the matched-p beam: False; in the Auto-RGN beam: False.
| selector | modules fitted | best J among them |
|---|---|---|
| held_gain | fc@7 fc@11 proj@7 | 0.3182 |
| matched_p | proj@11 o@7 v@11 | 0.4278 |
| rgn | v@3 o@3 v@11 | 0.4451 |
| random | v@3 fc@3 o@11 | 0.4169 |
| random, expected over draws | | 0.3912 |
| the full sweep | all | 0.3182 |
| the base | | 0.6866 |
| the current | | 0.5939 |

**G1**: the rule returns EXPAND on the planted module: **holds**.

## G2, the format shift itself: selectors against the sweep

| selector | modules fitted | best J among them |
|---|---|---|
| held_gain | fc@11 fc@7 proj@7 | 6.0800 |
| matched_p | proj@11 o@7 v@7 | 6.1702 |
| rgn | v@3 o@3 v@7 | 6.2345 |
| random | o@3 v@3 o@7 | 6.2345 |
| random, expected over draws | | 6.1720 |
| the full sweep | all | 6.0800 |
| the base | | 6.5848 |
| the current | | 6.4253 |

Action EXPAND:fc@11; held-out NLL base 6.585, current 6.425; restarts beating the first fit 0.

**G2**: the held-out gain's beam does at least as well as Auto-RGN's and as random placement's expectation, and within 1 percent of the sweep: **holds**.

## G3, reported

- extend: first-order held-out gain against the fitted held-out distortion gain, Pearson 0.69, Spearman 0.59; per module (predicted / fitted distortion gain): fc@7 +0.411/+0.466, fc@11 +0.364/+0.311, proj@7 +0.351/+0.327, proj@11 +0.283/+0.240, o@7 +0.275/+0.280, o@11 +0.275/+0.242, v@11 +0.261/+0.232, proj@3 +0.224/+0.296, o@3 +0.212/+0.251, v@7 +0.198/+0.208, fc@3 +0.164/+0.300, v@3 +0.140/+0.240
- extend: D 0.6295 D_held 0.5936 s 2.27e-01 first stage GLOBALIZE tau_sketch 0.038 fits 15; sweep (J): fc@7 0.3182, proj@7 0.4006, fc@11 0.4103, fc@3 0.4169, proj@3 0.4192, o@7 0.4278, o@3 0.4451, o@11 0.4506, v@3 0.4519, proj@11 0.4524, v@11 0.4567, v@7 0.4707
- real: first-order held-out gain against the fitted held-out distortion gain, Pearson 0.74, Spearman 0.70, against the fitted cross-entropy gain Pearson 0.41, Spearman 0.22; per module (predicted / fitted distortion gain / fitted cross-entropy gain): fc@11 +0.009/+0.007/+0.346, fc@7 +0.009/+0.003/+0.158, proj@7 +0.005/+0.003/+0.089, o@7 +0.005/+0.000/-0.037, o@3 +0.005/+0.002/+0.170, proj@11 +0.004/+0.003/+0.256, o@11 +0.004/+0.002/+0.243, fc@3 +0.004/+0.002/+0.220, v@3 +0.003/+0.002/+0.191, v@11 +0.003/+0.002/+0.212, v@7 +0.002/+0.001/+0.076, proj@3 +0.001/+0.001/+0.057
- real: D 0.9986 D_held 0.9992 s 3.73e-02 first stage GLOBALIZE tau_sketch 0.002 fits 15; sweep (J): fc@11 6.0800, proj@11 6.1702, o@11 6.1824, fc@3 6.2059, v@11 6.2135, v@3 6.2345, o@3 6.2561, fc@7 6.2678, proj@7 6.3373, v@7 6.3501, proj@3 6.3688, o@7 6.4626

## Letter: **A** (G1 holds, G2 holds)

