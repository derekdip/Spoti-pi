# ED2 report (frozen scorer)

## F1, the planted cases

| case | truth | got | D | D_held | s | first stage | budget gain | beam (held-out gain) | beam the matched-p score would give | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| refine | REFINE | REFINE | 0.275 | 0.066 | 9.6e-01 | REFINE | nan |  |  | 0 |
| saddle | GLOBALIZE | GLOBALIZE | 0.370 | 0.069 | 0.0e+00 | GLOBALIZE | 0.999 |  |  | 2 |
| extend | EXPAND:fc@7 | GLOBALIZE (miss) | 0.046 | 0.061 | 2.4e-01 | GLOBALIZE | 0.151 |  |  | 2 |
| noise | FALLBACK | FALLBACK | 0.440 | 0.482 | 2.8e-03 | EXHAUSTED | 0.004 | v@7 v@3 v@11 | proj@3 fc@7 proj@7 | 6 |
| adequate | STOP | STOP | 0.008 | 0.029 | 7.0e-02 | STOP | nan |  |  | 0 |

**F1**: 4 of 5 right, the extend case names the planted module: False. **fails**.

## F2, the real-data case against the sweep

| module | D_held | J | in beam |
|---|---|---|---|
| o@3 (sweep best) | 1.0009 | 1.0015 |  |
| proj@3 | 1.0086 | 1.0097 |  |
| v@11 | 1.0147 | 1.0153 | yes |
| v@7 | 1.0177 | 1.0183 |  |
| o@11 | 1.0179 | 1.0185 | yes |
| proj@7 | 1.0185 | 1.0196 |  |
| proj@11 | 1.0207 | 1.0218 |  |
| v@3 | 1.0213 | 1.0219 |  |
| o@7 | 1.0245 | 1.0251 |  |
| fc@11 | 1.0263 | 1.0273 | yes |
| fc@3 | 1.0304 | 1.0315 |  |
| fc@7 | 1.0359 | 1.0370 |  |
| base (the fallback) | 0.9906 | 0.9906 | |
| all modules (reported) | 1.0276 | 1.0343 | |
| current | 0.9903 | 0.9906 | |

Action FALLBACK; the sweep's best is o@3 (J 1.0015); the rule's choice scores J 0.9906. Fits: rule 6 (budget plus beam plus fallback), sweep 12 plus the fallback. Held-out NLL: {'base': 6.124478816986084, 'current': 6.114615440368652}.

**F2**: the rule's choice is within 1 percent of the sweep's best deployment objective: **holds**.

## F3, reported

- noise: tau_sketch 0.000; held-out gain / train gain / eta p12 per module: v@7 -0.005/0.007/0.000, v@3 -0.024/0.006/0.000, v@11 -0.025/0.011/0.000, fc@11 -0.027/0.027/0.000, o@11 -0.027/0.015/0.000, o@7 -0.037/0.008/0.000, proj@11 -0.041/0.019/0.000, o@3 -0.041/0.008/0.000, fc@3 -0.043/0.014/0.000, proj@3 -0.051/0.009/0.000, fc@7 -0.060/0.025/0.000, proj@7 -0.062/0.015/0.000; collapsed []; matched-p collapses 0 of 66
- real: tau_sketch 0.001; held-out gain / train gain / eta p12 per module: v@11 -0.000/0.012/0.001, o@11 -0.002/0.013/0.001, fc@11 -0.004/0.033/0.001, o@3 -0.004/0.024/0.001, v@7 -0.004/0.012/0.000, proj@11 -0.005/0.016/0.001, fc@3 -0.008/0.044/0.000, v@3 -0.009/0.019/0.001, proj@7 -0.016/0.034/0.000, fc@7 -0.017/0.061/0.000, proj@3 -0.021/0.036/0.001, o@7 -0.022/0.032/0.000; collapsed []; matched-p collapses 0 of 66
- noise fits: v@7 held 0.4873 J 0.4879, v@3 held 0.4914 J 0.4920, v@11 held 0.4908 J 0.4914, all_modules held 0.5012 J 0.5080, base held 0.4704 J 0.4704; J_current 0.4819
- real fits: v@11 held 1.0147 J 1.0153, o@11 held 1.0179 J 1.0185, fc@11 held 1.0263 J 1.0273, all_modules held 1.0276 J 1.0343, base held 0.9906 J 0.9906; J_current 0.9906

## Letter: **C** (F1 fails, F2 holds)

