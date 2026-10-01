# RGRE-1 results

Preregistration: `docs/math-track-rgre1-prereg.md`.

Abstention threshold tau_perp = 0.583 from the calibration cases: old_three_corners 0.08, old_corner_stop_corner 0.10, old_bend_then_corner 0.20, old_reversal 0.00, old_tight_slalom 0.48, old_A4 0.07, old_A6 0.07, old_A8 0.08.

## Per case

| case | classes | E0 | q_perp | chosen (reason) | mu | oracle repair [class] | RGRE pick | V_cap | dE RGRE / oracle | N | 2-step recovery |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smooth_0 | smooth | 0.100 | 0.31 | smooth (ok) | 0.0 | smooth_uniform [smooth] | smooth_uniform | 1.00 | 0.037 / 0.037 | 2/9 | - |
| corner_0 | corner | 0.163 | 0.06 | corner (ok) | 0.0 | corner_tighten [corner] | corner_tighten | 1.00 | 0.080 / 0.080 | 2/9 | - |
| stop_0 | stop | 0.173 | 0.00 | stop (ok) | 0.0 | events [stop] | events | 1.00 | 0.150 / 0.150 | 1/9 | - |
| coordinate_0 | coordinate | 0.221 | 0.10 | coordinate (ok) | 0.05 | shift [coordinate] | shift | 1.00 | 0.127 / 0.127 | 1/9 | - |
| tail_0 | tail | 0.266 | 0.01 | smooth (ok) | 0.0 | decay [tail] | smooth_adaptive | 0.00 | 0.002 / 0.209 | 2/9 | - |
| unary_0 | unary | 0.310 | 0.06 | unary (ok) | 0.76 | width [unary] | width | 1.00 | 0.247 / 0.247 | 2/9 | - |
| coordinate_0 | coordinate | 0.677 | 0.11 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.321 / 0.321 | 1/6 | - |
| unary_0 | unary | 0.857 | 0.03 | unary (ok) | 0.89 | gain [unary] | gain | 1.00 | 0.482 / 0.482 | 2/6 | - |
| tail_0 | tail | 0.472 | 0.19 | None (atom) | - | lam [tail] | None | 0.00 | 0.000 / 0.059 | 0/6 | - |
| interaction_0 | interaction | 0.586 | 0.08 | interaction (ok) | 0.0 | pair [interaction] | pair | 1.00 | 0.062 / 0.062 | 1/6 | - |
| mix_corner_stop_0 | corner+stop | 0.193 | 0.48 | stop (ok) | 0.16 | events [stop] | events | 1.00 | 0.060 / 0.060 | 1/9 | 1.0 |
| mix_coordinate_unary_0 | coordinate+unary | 0.591 | 0.07 | coordinate (ok) | 0.83 | shift [coordinate] | shift | 1.00 | 0.154 / 0.154 | 1/6 | 0.78 |
| unknown_wind_0 | unknown | 0.710 | 0.89 | None (unknown) | - | amp [unary] | None | 0.00 | 0.000 / 0.000 | 0/9 | - |
| unknown_hidden_0 | unknown | 0.533 | 0.63 | None (unknown) | - | gain [unary] | None | 0.00 | 0.000 / 0.003 | 0/6 | - |

## Tests

| test | result | pass |
|---|---|---|
| H1 | {"median_V_cap": 1.0, "mean_V_cap": 0.8334445850713087, "median_dE_rgre": 0.1031078885684712, "median_dE_oracle": 0.13816896971904952, "by_domain": {"corn": 1.0, "water": 1.0}} | True |
| H2 | {"median_N_ratio": 0.16666666666666666} | True |
| H3 | {"baseline_median_V_cap": {"cheapest_first": 0.0, "largest_opportunity": 1.0, "best_local_projection": 1.0, "random": 0.3277603487635246}, "rgre_median_V_cap": 1.0} | False |
| H4 | {"median_recovery2": 0.8894926932733433, "ownership_shift_count": 1, "n_mixtures": 2} | True |
| H5 | {"tau_perp": 0.5834212065969504, "unknown_abstained": 2, "n_unknown": 2, "known_false_abstain": 1, "n_known": 12, "q_perp_unknown": [0.8895925339257941, 0.6254938179408474]} | True |
| H6 | {"identity_low_mu": 0.8571428571428571, "identity_high_mu": 1.0, "n_low": 7, "n_high": 4, "oracle_value_low_mu": 0.07950096397765599, "oracle_value_high_mu": 0.2841725481894153} | False |
| H7 | {"rediagnosis_wins": 1, "ties": 0, "n": 2, "median_dE_rediag": 0.1542546742094938, "median_dE_ablation": 0.14151301001976785} | False |

Identity: vs injected 0.83; vs oracle 0.83; oracle class in top-2 0.92.

V_cap by injected class: smooth 1.00, corner 1.00, stop 1.00, coordinate 1.00, tail 0.00, unary 1.00, interaction 1.00

## Verdict: A: procedure supported

