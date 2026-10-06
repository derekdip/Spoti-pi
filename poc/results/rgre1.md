# RGRE-1 results

Preregistration: `docs/math-track-rgre1-prereg.md`.

Abstention threshold tau_perp = 0.583 from the calibration cases: old_three_corners 0.08, old_corner_stop_corner 0.10, old_bend_then_corner 0.20, old_reversal 0.00, old_tight_slalom 0.48, old_A4 0.07, old_A6 0.07, old_A8 0.08.

## Per case

| case | classes | E0 | q_perp | chosen (reason) | mu | oracle repair [class] | RGRE pick | V_cap | dE RGRE / oracle | N | 2-step recovery |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smooth_0 | smooth | 0.104 | 0.37 | smooth (ok) | 0.0 | smooth_uniform [smooth] | smooth_uniform | 1.00 | 0.050 / 0.050 | 2/9 | - |
| smooth_1 | smooth | 0.102 | 0.48 | smooth (ok) | 0.0 | smooth_uniform [smooth] | smooth_uniform | 1.00 | 0.043 / 0.043 | 2/9 | - |
| smooth_2 | smooth | 0.101 | 0.37 | smooth (ok) | 0.0 | smooth_uniform [smooth] | smooth_uniform | 1.00 | 0.029 / 0.029 | 2/9 | - |
| smooth_3 | smooth | 0.087 | 0.42 | smooth (ok) | 0.0 | smooth_adaptive [smooth] | smooth_adaptive | 1.00 | 0.038 / 0.038 | 2/9 | - |
| smooth_4 | smooth | 0.111 | 0.36 | smooth (ok) | 0.0 | smooth_uniform [smooth] | smooth_uniform | 1.00 | 0.056 / 0.056 | 2/9 | - |
| smooth_5 | smooth | 0.086 | 0.38 | smooth (ok) | 0.0 | smooth_uniform [smooth] | smooth_uniform | 1.00 | 0.021 / 0.021 | 2/9 | - |
| corner_0 | corner | 0.154 | 0.08 | corner (ok) | 0.0 | smooth_uniform [smooth] | corner_tighten | 0.74 | 0.027 / 0.032 | 2/9 | - |
| corner_1 | corner | 0.069 | 0.07 | corner (ok) | 0.0 | corner_tighten [corner] | corner_tighten | 1.00 | 0.009 / 0.009 | 2/9 | - |
| corner_2 | corner | 0.143 | 0.04 | corner (ok) | 0.0 | smooth_uniform [smooth] | corner_tighten | 0.93 | 0.053 / 0.057 | 2/9 | - |
| corner_3 | corner | 0.157 | 0.03 | corner (ok) | 0.0 | corner_tighten [corner] | corner_tighten | 1.00 | 0.070 / 0.070 | 2/9 | - |
| corner_4 | corner | 0.138 | 0.08 | corner (ok) | 0.0 | smooth_uniform [smooth] | corner_tighten | 0.98 | 0.041 / 0.049 | 2/9 | - |
| corner_5 | corner | 0.158 | 0.07 | corner (ok) | 0.0 | smooth_uniform [smooth] | corner_tighten | 0.85 | 0.071 / 0.083 | 2/9 | - |
| stop_0 | stop | 0.161 | 0.01 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.127 / 0.127 | 1/9 | - |
| stop_1 | stop | 0.231 | 0.02 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.183 / 0.183 | 1/9 | - |
| stop_2 | stop | 0.195 | 0.04 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.112 / 0.112 | 1/9 | - |
| stop_3 | stop | 0.235 | 0.02 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.185 / 0.185 | 1/9 | - |
| stop_4 | stop | 0.115 | 0.02 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.061 / 0.061 | 1/9 | - |
| stop_5 | stop | 0.161 | 0.05 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.100 / 0.100 | 1/9 | - |
| coordinate_0 | coordinate | 0.242 | 0.07 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.165 / 0.165 | 1/9 | - |
| coordinate_1 | coordinate | 0.187 | 0.05 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.145 / 0.145 | 1/9 | - |
| coordinate_2 | coordinate | 0.176 | 0.05 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.122 / 0.122 | 1/9 | - |
| coordinate_3 | coordinate | 0.235 | 0.07 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.184 / 0.184 | 1/9 | - |
| coordinate_4 | coordinate | 0.195 | 0.08 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.134 / 0.134 | 1/9 | - |
| coordinate_5 | coordinate | 0.216 | 0.09 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.159 / 0.159 | 1/9 | - |
| tail_0 | tail | 0.146 | 0.09 | smooth (ok) | 0.0 | decay [tail] | smooth_adaptive | 0.02 | 0.022 / 0.050 | 2/9 | - |
| tail_1 | tail | 0.279 | 0.01 | tail (ok) | 0.71 | decay [tail] | decay | 1.00 | 0.215 / 0.215 | 1/9 | - |
| tail_2 | tail | 0.264 | 0.02 | smooth (ok) | 0.0 | decay [tail] | smooth_uniform | 0.00 | 0.005 / 0.207 | 2/9 | - |
| tail_3 | tail | 0.274 | 0.03 | tail (ok) | 0.68 | decay [tail] | decay | 1.00 | 0.194 / 0.194 | 1/9 | - |
| tail_4 | tail | 0.296 | 0.02 | smooth (ok) | 0.0 | decay [tail] | smooth_uniform | 0.00 | 0.005 / 0.229 | 2/9 | - |
| tail_5 | tail | 0.320 | 0.02 | tail (ok) | 0.67 | decay [tail] | decay | 1.00 | 0.261 / 0.261 | 1/9 | - |
| unary_0 | unary | 0.284 | 0.05 | unary (ok) | 0.77 | width [unary] | width | 1.00 | 0.196 / 0.196 | 2/9 | - |
| unary_1 | unary | 0.333 | 0.03 | unary (ok) | 0.76 | width [unary] | width | 1.00 | 0.262 / 0.262 | 2/9 | - |
| unary_2 | unary | 0.301 | 0.07 | unary (ok) | 0.76 | width [unary] | width | 1.00 | 0.208 / 0.208 | 2/9 | - |
| unary_3 | unary | 0.234 | 0.02 | unary (ok) | 0.76 | width [unary] | width | 1.00 | 0.173 / 0.173 | 2/9 | - |
| unary_4 | unary | 0.401 | 0.11 | unary (ok) | 0.77 | width [unary] | width | 1.00 | 0.324 / 0.324 | 2/9 | - |
| unary_5 | unary | 0.460 | 0.03 | unary (ok) | 0.76 | width [unary] | width | 1.00 | 0.385 / 0.385 | 2/9 | - |
| coordinate_0 | coordinate | 0.677 | 0.11 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.321 / 0.321 | 1/6 | - |
| coordinate_1 | coordinate | 0.821 | 0.13 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.404 / 0.404 | 1/6 | - |
| coordinate_2 | coordinate | 0.958 | 0.15 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.423 / 0.423 | 1/6 | - |
| coordinate_3 | coordinate | 1.083 | 0.17 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.409 / 0.409 | 1/6 | - |
| coordinate_4 | coordinate | 1.195 | 0.19 | unary (ok) | 0.89 | shift [coordinate] | gain | 0.55 | 0.209 / 0.378 | 2/6 | - |
| coordinate_5 | coordinate | 1.292 | 0.21 | unary (ok) | 0.89 | shift [coordinate] | gain | 0.87 | 0.292 / 0.337 | 2/6 | - |
| unary_0 | unary | 0.857 | 0.03 | unary (ok) | 0.89 | gain [unary] | gain | 1.00 | 0.482 / 0.482 | 2/6 | - |
| unary_1 | unary | 0.421 | 0.03 | None (atom) | - | gain [unary] | None | 0.00 | 0.000 / 0.073 | 0/6 | - |
| unary_2 | unary | 0.524 | 0.06 | unary (ok) | 0.89 | gain [unary] | gain | 1.00 | 0.156 / 0.156 | 2/6 | - |
| unary_3 | unary | 0.662 | 0.11 | unary (ok) | 0.89 | gain [unary] | gain | 1.00 | 0.247 / 0.247 | 2/6 | - |
| unary_4 | unary | 0.483 | 0.31 | None (atom) | - | shift [coordinate] | None | 0.00 | 0.000 / 0.006 | 0/6 | - |
| unary_5 | unary | 0.308 | 0.28 | None (atom) | - | gain [unary] | None | 0.00 | 0.000 / 0.007 | 0/6 | - |
| tail_0 | tail | 0.472 | 0.19 | None (atom) | - | lam [tail] | None | 0.00 | 0.000 / 0.059 | 0/6 | - |
| tail_1 | tail | 0.536 | 0.23 | unary (ok) | 0.89 | lam [tail] | gain | 0.64 | 0.060 / 0.094 | 2/6 | - |
| tail_2 | tail | 0.453 | 0.02 | tail (ok) | 0.89 | lam [tail] | lam | 1.00 | 0.108 / 0.108 | 2/6 | - |
| tail_3 | tail | 0.710 | 0.03 | tail (ok) | 0.89 | gain [unary] | lam | 0.99 | 0.231 / 0.233 | 2/6 | - |
| tail_4 | tail | 0.982 | 0.03 | tail (ok) | 0.89 | gain [unary] | m | 0.76 | 0.327 / 0.430 | 2/6 | - |
| tail_5 | tail | 1.499 | 0.02 | tail (ok) | 0.89 | gain [unary] | m | 0.55 | 0.461 / 0.840 | 2/6 | - |
| interaction_0 | interaction | 0.586 | 0.08 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.062 / 0.062 | 1/6 | - |
| interaction_1 | interaction | 0.573 | 0.13 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.052 / 0.052 | 1/6 | - |
| interaction_2 | interaction | 0.755 | 0.12 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.117 / 0.117 | 1/6 | - |
| interaction_3 | interaction | 0.648 | 0.17 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.041 / 0.041 | 1/6 | - |
| interaction_4 | interaction | 0.652 | 0.10 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.086 / 0.086 | 1/6 | - |
| interaction_5 | interaction | 0.525 | 0.10 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.049 / 0.049 | 1/6 | - |
| mix_corner_stop_0 | corner+stop | 0.131 | 0.30 | stop (ok) | 0.3 | events [stop] | events | 1.00 | 0.024 / 0.024 | 1/9 | 1.0 |
| mix_corner_stop_1 | corner+stop | 0.184 | 0.01 | corner (ok) | 0.0 | events [stop] | corner_tighten | 0.47 | 0.020 / 0.064 | 2/9 | 0.52 |
| mix_coordinate_corner_0 | coordinate+corner | 0.249 | 0.04 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.118 / 0.118 | 1/9 | 1.0 |
| mix_coordinate_corner_1 | coordinate+corner | 0.262 | 0.09 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.153 / 0.153 | 1/9 | 1.0 |
| mix_tail_smooth_0 | tail+smooth | 0.314 | 0.01 | tail (ok) | 0.64 | decay [tail] | decay | 1.00 | 0.247 / 0.247 | 1/9 | 0.98 |
| mix_unary_stop_0 | unary+stop | 0.343 | 0.02 | stop (ok) | 0.0 | width [unary] | events | 0.02 | 0.033 / 0.145 | 1/9 | 0.16 |
| mix_coordinate_unary_0 | coordinate+unary | 0.591 | 0.07 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.154 / 0.154 | 1/6 | 0.78 |
| mix_coordinate_unary_1 | coordinate+unary | 0.900 | 0.07 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.323 / 0.323 | 1/6 | 1.0 |
| mix_coordinate_unary_2 | coordinate+unary | 1.339 | 0.08 | unary (ok) | 0.89 | shift [coordinate] | gain | 0.81 | 0.436 / 0.537 | 2/6 | 0.75 |
| mix_interaction_coordinate_0 | interaction+coordinate | 0.841 | 0.04 | interaction (ok) | 0.0 | shift [coordinate] | pair | 0.02 | 0.005 / 0.235 | 1/6 | 0.02 |
| mix_interaction_coordinate_1 | interaction+coordinate | 0.991 | 0.04 | interaction (ok) | 0.0 | shift [coordinate] | pair | 0.03 | 0.006 / 0.181 | 1/6 | 0.02 |
| mix_tail_unary_0 | tail+unary | 0.596 | 0.30 | unary (ok) | 0.89 | gain [unary] | gain | 1.00 | 0.090 / 0.090 | 2/6 | 1.0 |
| unknown_wind_0 | unknown | 0.348 | 0.93 | None (unknown) | - | amp [unary] | None | 0.00 | 0.000 / 0.001 | 0/9 | - |
| unknown_wind_1 | unknown | 0.531 | 0.90 | None (unknown) | - | amp [unary] | None | 0.00 | 0.000 / 0.002 | 0/9 | - |
| unknown_hidden_0 | unknown | 0.710 | 0.99 | None (unknown) | - | width [unary] | None | 0.00 | 0.000 / 0.002 | 0/9 | - |
| unknown_hidden_0 | unknown | 0.533 | 0.63 | None (unknown) | - | gain [unary] | None | 0.00 | 0.000 / 0.003 | 0/6 | - |
| unknown_hidden_1 | unknown | 0.522 | 0.61 | None (unknown) | - | gain [unary] | None | 0.00 | 0.000 / 0.003 | 0/6 | - |
| unknown_moving_0 | unknown | 2.167 | 0.17 | unary (ok) | 0.89 | gain [unary] | gain | 1.00 | 1.197 / 1.197 | 2/6 | - |

## Tests

| test | result | pass |
|---|---|---|
| H1 | {"median_V_cap": 1.0, "mean_V_cap": 0.822794526534827, "median_dE_rgre": 0.11747688966225939, "median_dE_oracle": 0.1451333693354241, "by_domain": {"corn": 1.0, "water": 1.0}} | True |
| H2 | {"median_N_ratio": 0.16666666666666666} | True |
| H3 | {"baseline_median_V_cap": {"cheapest_first": 0.0006585203314059296, "largest_opportunity": 1.0, "best_local_projection": 1.0, "random": 0.3229882350409228}, "rgre_median_V_cap": 1.0} | False |
| H4 | {"median_recovery2": 0.8803509384220773, "ownership_shift_count": 7, "n_mixtures": 12} | True |
| H5 | {"tau_perp": 0.5834212065969504, "unknown_abstained": 5, "n_unknown": 6, "known_false_abstain": 4, "n_known": 72, "q_perp_unknown": [0.9322365702015045, 0.8960100105277025, 0.990650414138492, 0.6254938179408474, 0.6131596109602468, 0.17493283688741185]} | True |
| H6 | {"identity_low_mu": 0.725, "identity_high_mu": 0.75, "n_low": 40, "n_high": 28, "oracle_value_low_mu": 0.08444071079981513, "oracle_value_high_mu": 0.2618265380856534} | False |
| H7 | {"rediagnosis_wins": 4, "ties": 3, "n": 12, "median_dE_rediag": 0.164492355631724, "median_dE_ablation": 0.19069914456502718} | False |

Identity: vs injected 0.86; vs oracle 0.69; oracle class in top-2 0.93.

V_cap by injected class: smooth 1.00, corner 0.99, stop 1.00, coordinate 1.00, tail 0.88, unary 1.00, interaction 1.00

## Verdict: A: procedure supported

