# W3 post-hoc residual diagnostic (exploratory, unregistered, not scored)

Single-splash residual `teacher - token` on W1's evaluation set, by model and amplitude. Shares are fractions of the residual energy.

| cell | rel_rmse | axisym_share | gain_phase_global | gain_phase_per_frame | gain_phase_per_radius | gain_only_per_frame | floor_share | near_early_share_residual | near_early_share_teacher | crest_trough_teacher | crest_trough_token |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M0_A1 | 0.344 | 0.950 | 0.009 | 0.108 | 0.103 | 0.060 | 1.000 | 0.412 | 0.415 | 1.075 | 0.999 |
| M2_A1 | 0.344 | 0.950 | 0.009 | 0.108 | 0.103 | 0.060 | 1.000 | 0.412 | 0.415 | 1.075 | 0.999 |
| M4_A1 | 0.344 | 0.950 | 0.009 | 0.108 | 0.103 | 0.060 | 1.000 | 0.412 | 0.415 | 1.075 | 0.999 |
| M0_A4 | 0.688 | 0.967 | 0.677 | 0.706 | 0.701 | 0.256 | 0.238 | 0.509 | 0.443 | 1.052 | 0.999 |
| M2_A4 | 0.500 | 0.963 | 0.092 | 0.393 | 0.367 | 0.037 | 0.490 | 0.605 | 0.443 | 1.052 | 0.998 |
| M4_A4 | 0.497 | 0.960 | 0.099 | 0.411 | 0.352 | 0.039 | 0.485 | 0.597 | 0.443 | 1.052 | 0.997 |
| M0_A8 | 1.546 | 0.964 | 0.907 | 0.915 | 0.922 | 0.622 | 0.004 | 0.447 | 0.494 | 0.989 | 0.999 |
| M2_A8 | 0.930 | 0.964 | 0.564 | 0.734 | 0.756 | 0.244 | 0.017 | 0.602 | 0.494 | 0.989 | 0.999 |
| M4_A8 | 0.931 | 0.960 | 0.575 | 0.745 | 0.743 | 0.243 | 0.014 | 0.619 | 0.494 | 0.989 | 0.999 |

Zero crossings of the azimuthally averaged radial profile (0.2 < r < 2 m) at t = 0.5, 1, 2 s: teacher / token / residual.

| cell | t=0.5 | t=1 | t=2 |
|---|---|---|---|
| M0_A1 | 1 / 0 / 2 | 3 / 3 / 4 | 8 / 12 / 7 |
| M2_A1 | 1 / 0 / 2 | 3 / 3 / 4 | 8 / 12 / 7 |
| M4_A1 | 1 / 0 / 2 | 3 / 3 / 4 | 8 / 12 / 7 |
| M0_A4 | 2 / 0 / 2 | 3 / 3 / 5 | 8 / 12 / 9 |
| M2_A4 | 2 / 0 / 2 | 3 / 3 / 2 | 8 / 11 / 7 |
| M4_A4 | 2 / 0 / 2 | 3 / 3 / 1 | 8 / 13 / 7 |
| M0_A8 | 2 / 0 / 2 | 4 / 3 / 3 | 8 / 12 / 9 |
| M2_A8 | 2 / 0 / 2 | 4 / 3 / 5 | 8 / 13 / 11 |
| M4_A8 | 2 / 0 / 2 | 4 / 3 / 2 | 8 / 13 / 11 |
