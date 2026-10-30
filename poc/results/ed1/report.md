# ED1 report (frozen scorer)

## Actions per arm

| case | truth | A | B | C | D | E | full |
|---|---|---|---|---|---|---|---|
| refine_early | REFINE | EXPAND:wv@0 (miss) | REFINE | REFINE | REFINE | REFINE | REFINE |
| refine_mid | REFINE | EXPAND:wv@1 (miss) | REFINE | REFINE | REFINE | REFINE | REFINE |
| saddle | GLOBALIZE | EXPAND:wv@0 (miss) | EXPAND:wv@0 (miss) | GLOBALIZE | GLOBALIZE | GLOBALIZE | GLOBALIZE |
| reuse | EXPAND:wv@0 | EXPAND:wv@0 | EXPAND:wv@0 | EXPAND:wv@0 | EXPAND:wv@0 | EXPAND:wv@0 | EXPAND:wv@0 |
| collinear | REPARAMETERIZE | EXPAND:wv@1 (miss) | REFINE (miss) | REFINE (miss) | REPARAMETERIZE | REPARAMETERIZE | REPARAMETERIZE |
| extend | EXPAND:w2@1 | EXPAND:w2@1 | EXPAND:w2@1 | EXPAND:w2@1 | EXPAND:w2@1 | EXPAND:w2@1 | EXPAND:w2@1 |
| noise | FALLBACK | FALLBACK | FALLBACK | FALLBACK | FALLBACK | FALLBACK | FALLBACK |
| adequate | STOP | STOP | STOP | STOP | STOP | STOP | STOP |

**E1**: the full rule gets 8 of 8; EXPAND cases name the planted module: True. **holds**.

## Equivalence (full arm)

| pair | truth | frozen rule | matched-p rule | containment | align | p1 mu/d | p3 mu/d | p12 mu/d |
|---|---|---|---|---|---|---|---|---|
| wv@1|wo@1 | COLLAPSE | COLLAPSE | KEEP DISTINCT | 1.000/1.000 | 1.000 | 0.65/0.76 | 0.84/0.93 | 0.93/1.00 |
| wv@0|w2@1 | KEEP DISTINCT | KEEP DISTINCT | KEEP DISTINCT | 0.802/0.555 | 0.933 | 0.75/0.66 | 0.80/0.99 | 0.87/1.00 |

**E2**: **holds**.

## Ablations

- A misses, among the cases the full rule gets right: refine_early, refine_mid, saddle, collinear
- B misses, among the cases the full rule gets right: saddle, collinear
- C misses, among the cases the full rule gets right: collinear
- redundant fits: full 0, E 2
- D agrees with the full rule on 8 of 8 cases

**E3**: **holds**.

## E4, reported

| arm | case | D | D_held | s | tau | kappa | lam_min/|H| | stage | glob. gain | beam | collapsed | fits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | refine_early | 0.236 | 0.248 | 1.4e-01 | 0.39 | 1.2e+05 | -1.3e+00/1.3e+01 | EXHAUSTED | nan | w1@1 w2@1 wv@0 | wo@0 wo@1 | 4 |
| A | refine_mid | 0.300 | 0.330 | 1.3e-01 | 0.38 | 2.2e+04 | -1.3e+00/5.1e+01 | EXHAUSTED | nan | w1@1 w2@1 wv@1 | wo@0 wo@1 | 4 |
| A | saddle | 0.439 | 0.447 | 0.0e+00 | 0.00 | inf | -8.0e+00/8.0e+00 | EXHAUSTED | nan | w1@1 w2@1 wv@0 | wo@0 wo@1 | 4 |
| A | reuse | 0.164 | 0.199 | 2.5e-03 | 0.08 | 5.1e+04 | -3.9e-03/3.2e+01 | EXHAUSTED | nan | w1@1 w2@1 wv@0 | wo@0 wo@1 | 4 |
| A | collinear | 0.305 | 0.347 | 9.7e-02 | 0.57 | 9.6e+07 | -1.2e+01/2.5e+02 | EXHAUSTED | nan | w1@1 w2@1 wv@1 | wo@0 wo@1 | 4 |
| A | extend | 0.197 | 0.246 | 4.9e-03 | 0.04 | 1.5e+05 | -4.0e-03/7.9e+01 | EXHAUSTED | nan | w1@1 w2@1 wv@1 | wo@0 wo@1 | 4 |
| A | noise | 0.441 | 0.470 | 1.4e-03 | 0.00 | 1.4e+05 | -1.1e-03/2.1e+01 | EXHAUSTED | nan | w1@1 w2@1 wv@1 | wo@0 wo@1 | 4 |
| A | adequate | 0.006 | 0.007 | 1.6e-02 | 0.99 | 6.0e+04 | -7.8e-04/2.4e+01 | STOP | nan |  |  | 0 |
| B | refine_early | 0.236 | 0.248 | 1.4e-01 | 0.39 | 1.2e+05 | -1.3e+00/1.3e+01 | REFINE | nan |  |  | 0 |
| B | refine_mid | 0.300 | 0.330 | 1.3e-01 | 0.38 | 2.2e+04 | -1.3e+00/5.1e+01 | REFINE | nan |  |  | 0 |
| B | saddle | 0.439 | 0.447 | 0.0e+00 | 0.00 | inf | -8.0e+00/8.0e+00 | EXHAUSTED | nan | wv@0 w1@1 w2@1 | wo@0 wo@1 | 4 |
| B | reuse | 0.164 | 0.199 | 2.5e-03 | 0.08 | 5.1e+04 | -3.9e-03/3.2e+01 | EXHAUSTED | nan | wv@0 wv@1 out_bias | wo@0 wo@1 | 4 |
| B | collinear | 0.305 | 0.347 | 9.7e-02 | 0.57 | 9.6e+07 | -1.2e+01/2.5e+02 | REFINE | nan |  |  | 0 |
| B | extend | 0.197 | 0.246 | 4.9e-03 | 0.04 | 1.5e+05 | -4.0e-03/7.9e+01 | EXHAUSTED | nan | w1@1 out_bias w2@1 | wo@0 wo@1 | 4 |
| B | noise | 0.441 | 0.470 | 1.4e-03 | 0.00 | 1.4e+05 | -1.1e-03/2.1e+01 | EXHAUSTED | nan | wv@0 wv@1 out_bias | wo@0 wo@1 | 4 |
| B | adequate | 0.006 | 0.007 | 1.6e-02 | 0.99 | 6.0e+04 | -7.8e-04/2.4e+01 | STOP | nan |  |  | 0 |
| C | refine_early | 0.236 | 0.248 | 1.4e-01 | 0.39 | 1.2e+05 | -1.3e+00/1.3e+01 | REFINE | nan |  |  | 0 |
| C | refine_mid | 0.300 | 0.330 | 1.3e-01 | 0.38 | 2.2e+04 | -1.3e+00/5.1e+01 | REFINE | nan |  |  | 0 |
| C | saddle | 0.439 | 0.447 | 0.0e+00 | 0.00 | inf | -8.0e+00/8.0e+00 | GLOBALIZE | 1.000 |  |  | 8 |
| C | reuse | 0.164 | 0.199 | 2.5e-03 | 0.08 | 5.1e+04 | -3.9e-03/3.2e+01 | GLOBALIZE | 0.000 | wv@0 wv@1 out_bias | wo@0 wo@1 | 12 |
| C | collinear | 0.305 | 0.347 | 9.7e-02 | 0.57 | 9.6e+07 | -1.2e+01/2.5e+02 | REFINE | nan |  |  | 0 |
| C | extend | 0.197 | 0.246 | 4.9e-03 | 0.04 | 1.5e+05 | -4.0e-03/7.9e+01 | GLOBALIZE | 0.000 | w1@1 out_bias w2@1 | wo@0 wo@1 | 12 |
| C | noise | 0.441 | 0.470 | 1.4e-03 | 0.00 | 1.4e+05 | -1.1e-03/2.1e+01 | GLOBALIZE | 0.000 | wv@0 wv@1 out_bias | wo@0 wo@1 | 12 |
| C | adequate | 0.006 | 0.007 | 1.6e-02 | 0.99 | 6.0e+04 | -7.8e-04/2.4e+01 | STOP | nan |  |  | 0 |
| D | refine_early | 0.236 | 0.248 | 1.4e-01 | 0.39 | 1.2e+05 | -1.3e+00/1.3e+01 | REFINE | nan |  |  | 0 |
| D | refine_mid | 0.300 | 0.330 | 1.3e-01 | 0.38 | 2.2e+04 | -1.3e+00/5.1e+01 | REFINE | nan |  |  | 0 |
| D | saddle | 0.439 | 0.447 | 0.0e+00 | 0.00 | inf | -8.0e+00/8.0e+00 | GLOBALIZE | 1.000 |  |  | 8 |
| D | reuse | 0.164 | 0.199 | 2.5e-03 | 0.08 | 5.1e+04 | -3.9e-03/3.2e+01 | GLOBALIZE | 0.000 | out_bias wv@0 wv@1 | wo@0 wo@1 | 12 |
| D | collinear | 0.305 | 0.347 | 9.7e-02 | 0.57 | 9.6e+07 | -1.2e+01/2.5e+02 | REPARAMETERIZE | nan |  |  | 0 |
| D | extend | 0.197 | 0.246 | 4.9e-03 | 0.04 | 1.5e+05 | -4.0e-03/7.9e+01 | GLOBALIZE | 0.000 | w1@1 out_bias w2@1 | wo@0 wo@1 | 12 |
| D | noise | 0.441 | 0.470 | 1.4e-03 | 0.00 | 1.4e+05 | -1.1e-03/2.1e+01 | GLOBALIZE | 0.000 | w2@1 w1@1 wv@0 | wo@0 wo@1 | 12 |
| D | adequate | 0.006 | 0.007 | 1.6e-02 | 0.99 | 6.0e+04 | -7.8e-04/2.4e+01 | STOP | nan |  |  | 0 |
| E | refine_early | 0.236 | 0.248 | 1.4e-01 | 0.39 | 1.2e+05 | -1.3e+00/1.3e+01 | REFINE | nan |  |  | 0 |
| E | refine_mid | 0.300 | 0.330 | 1.3e-01 | 0.38 | 2.2e+04 | -1.3e+00/5.1e+01 | REFINE | nan |  |  | 0 |
| E | saddle | 0.439 | 0.447 | 0.0e+00 | 0.00 | inf | -8.0e+00/8.0e+00 | GLOBALIZE | 1.000 |  |  | 8 |
| E | reuse | 0.164 | 0.199 | 2.5e-03 | 0.08 | 5.1e+04 | -3.9e-03/3.2e+01 | GLOBALIZE | 0.000 | wo@0 wv@0 wv@1 |  | 12 |
| E | collinear | 0.305 | 0.347 | 9.7e-02 | 0.57 | 9.6e+07 | -1.2e+01/2.5e+02 | REPARAMETERIZE | nan |  |  | 0 |
| E | extend | 0.197 | 0.246 | 4.9e-03 | 0.04 | 1.5e+05 | -4.0e-03/7.9e+01 | GLOBALIZE | 0.000 | w1@1 out_bias w2@1 |  | 12 |
| E | noise | 0.441 | 0.470 | 1.4e-03 | 0.00 | 1.4e+05 | -1.1e-03/2.1e+01 | GLOBALIZE | 0.000 | wv@0 wo@0 wo@1 |  | 12 |
| E | adequate | 0.006 | 0.007 | 1.6e-02 | 0.99 | 6.0e+04 | -7.8e-04/2.4e+01 | STOP | nan |  |  | 0 |
| full | refine_early | 0.236 | 0.248 | 1.4e-01 | 0.39 | 1.2e+05 | -1.3e+00/1.3e+01 | REFINE | nan |  |  | 0 |
| full | refine_mid | 0.300 | 0.330 | 1.3e-01 | 0.38 | 2.2e+04 | -1.3e+00/5.1e+01 | REFINE | nan |  |  | 0 |
| full | saddle | 0.439 | 0.447 | 0.0e+00 | 0.00 | inf | -8.0e+00/8.0e+00 | GLOBALIZE | 1.000 |  |  | 8 |
| full | reuse | 0.164 | 0.199 | 2.5e-03 | 0.08 | 5.1e+04 | -3.9e-03/3.2e+01 | GLOBALIZE | 0.000 | wv@0 wv@1 out_bias | wo@0 wo@1 | 12 |
| full | collinear | 0.305 | 0.347 | 9.7e-02 | 0.57 | 9.6e+07 | -1.2e+01/2.5e+02 | REPARAMETERIZE | nan |  |  | 0 |
| full | extend | 0.197 | 0.246 | 4.9e-03 | 0.04 | 1.5e+05 | -4.0e-03/7.9e+01 | GLOBALIZE | 0.000 | w1@1 out_bias w2@1 | wo@0 wo@1 | 12 |
| full | noise | 0.441 | 0.470 | 1.4e-03 | 0.00 | 1.4e+05 | -1.1e-03/2.1e+01 | GLOBALIZE | 0.000 | wv@0 wv@1 out_bias | wo@0 wo@1 | 12 |
| full | adequate | 0.006 | 0.007 | 1.6e-02 | 0.99 | 6.0e+04 | -7.8e-04/2.4e+01 | STOP | nan |  |  | 0 |

### Candidate eta at p = 12 and on the full span, and the fitted candidates (full arm)

- reuse: wv@0 0.09/0.94, wo@0 0.10/0.94, wv@1 0.08/0.91, wo@1 0.06/0.91, w1@1 0.03/0.98, w2@1 0.04/0.95, out_bias 0.07/0.08; fits: wv@0 held 0.007 J 0.010, wv@1 held 0.125 J 0.128, out_bias held 0.174 J 0.174, fallback held 0.023 J 0.042; J_current 0.199
- extend: wv@0 0.02/0.87, wo@0 0.01/0.87, wv@1 0.01/0.93, wo@1 0.01/0.93, w1@1 0.08/1.00, w2@1 0.03/0.98, out_bias 0.03/0.04; fits: w1@1 held 0.196 J 0.202, out_bias held 0.240 J 0.241, w2@1 held 0.024 J 0.029, fallback held 0.048 J 0.068; J_current 0.247
- noise: wv@0 0.00/0.20, wo@0 0.00/0.20, wv@1 0.00/0.23, wo@1 0.00/0.23, w1@1 0.00/0.48, w2@1 0.00/0.29, out_bias 0.00/0.00; fits: wv@0 held 0.491 J 0.494, wv@1 held 0.489 J 0.493, out_bias held 0.471 J 0.473, fallback held 0.570 J 0.590; J_current 0.471

### Sweeps

| kind | level | case | truth | got | D | D_held | s | stage |
|---|---|---|---|---|---|---|---|---|
| noise | 0.0 | refine_early | REFINE | REFINE | 0.238 | 0.272 | 1.8e-01 | REFINE |
| noise | 0.0 | reuse | EXPAND:wv@0 | EXPAND:wv@0 | 0.151 | 0.177 | 1.4e-03 | GLOBALIZE |
| noise | 0.0 | extend | EXPAND:w2@1 | EXPAND:w2@1 | 0.119 | 0.157 | 2.2e-03 | GLOBALIZE |
| noise | 0.0 | adequate | STOP | STOP | 0.007 | 0.009 | 1.2e-02 | STOP |
| noise | 0.01 | refine_early | REFINE | REFINE | 0.239 | 0.272 | 1.8e-01 | REFINE |
| noise | 0.01 | reuse | EXPAND:wv@0 | EXPAND:wv@0 | 0.152 | 0.177 | 1.4e-03 | GLOBALIZE |
| noise | 0.01 | extend | EXPAND:w2@1 | EXPAND:w2@1 | 0.119 | 0.157 | 2.2e-03 | GLOBALIZE |
| noise | 0.01 | adequate | STOP | STOP | 0.012 | 0.014 | 6.8e-03 | STOP |
| noise | 0.05 | refine_early | REFINE | REFINE | 0.244 | 0.276 | 1.8e-01 | REFINE |
| noise | 0.05 | reuse | EXPAND:wv@0 | EXPAND:wv@0 | 0.159 | 0.183 | 1.3e-03 | GLOBALIZE |
| noise | 0.05 | extend | EXPAND:w2@1 | EXPAND:w2@1 | 0.128 | 0.166 | 2.1e-03 | GLOBALIZE |
| noise | 0.05 | adequate | STOP | STOP | 0.049 | 0.053 | 1.8e-03 | STOP |
| noise | 0.1 | refine_early | REFINE | REFINE | 0.258 | 0.289 | 1.7e-01 | REFINE |
| noise | 0.1 | reuse | EXPAND:wv@0 | EXPAND:wv@0 | 0.180 | 0.203 | 1.2e-03 | GLOBALIZE |
| noise | 0.1 | extend | EXPAND:w2@1 | EXPAND:w2@1 | 0.151 | 0.190 | 2.0e-03 | GLOBALIZE |
| noise | 0.1 | adequate | STOP | FALLBACK (miss) | 0.097 | 0.104 | 1.0e-03 | GLOBALIZE |
| misspec | 0.01 | extend | STOP | STOP | 0.003 | 0.004 | 3.4e-02 | STOP |
| misspec | 0.03 | extend | STOP | STOP | 0.009 | 0.012 | 1.3e-02 | STOP |
| misspec | 0.1 | extend | STOP | STOP | 0.030 | 0.039 | 1.1e-02 | STOP |
| misspec | 0.3 | extend | EXPAND:w2@1 | EXPAND:w2@1 | 0.088 | 0.114 | 1.2e-02 | GLOBALIZE |
| misspec | 1.0 | extend | EXPAND:w2@1 | EXPAND:w2@1 | 0.265 | 0.325 | 3.0e-03 | GLOBALIZE |

Misspecification: 5 of 5 match the bar-defined truth.

## Letter: **A** (E1 holds, E2 holds, E3 holds)

Seconds per arm: {'A': 1644.8349390029907, 'B': 6636.4711327552795, 'C': 6161.0483202934265, 'D': 1365.4092762470245, 'E': 6145.452792167664, 'full': 6125.934967517853, 'sweeps': 3649.1117312908173}
