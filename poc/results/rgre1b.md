# RGRE-1b results: replication of the simplified selector

Preregistration: `docs/math-track-rgre1b-prereg.md`.

Threshold carried over unchanged from RGRE-1: tau = 0.583. Seed 20260916.

## Per case

| case | injected | E0 | q_perp | chosen (reason) | oracle repair [class] | pick | V_cap | S-rule class | S-rule V | 2-step |
|---|---|---|---|---|---|---|---|---|---|---|
| corn_tail_0 | tail | 0.251 | 0.03 | unary (ok) | decay [tail] | amp | 0.58 | smooth | 0.01 | - |
| corn_tail_1 | tail | 0.204 | 0.10 | tail (ok) | decay [tail] | decay | 1.00 | smooth | 0.01 | - |
| corn_tail_2 | tail | 0.213 | 0.01 | tail (ok) | decay [tail] | decay | 1.00 | tail | 1.00 | - |
| corn_coordinate_0 | coordinate | 0.161 | 0.08 | coordinate (ok) | shift [coordinate] | shift | 1.00 | coordinate | 1.00 | - |
| corn_coordinate_1 | coordinate | 0.216 | 0.07 | coordinate (ok) | shift [coordinate] | shift | 1.00 | coordinate | 1.00 | - |
| corn_unary_0 | unary | 0.285 | 0.05 | unary (ok) | width [unary] | width | 1.00 | unary | 1.00 | - |
| water_coordinate_0 | coordinate | 0.533 | 0.08 | coordinate (ok) | shift [coordinate] | shift | 1.00 | coordinate | 1.00 | - |
| water_coordinate_1 | coordinate | 0.958 | 0.15 | coordinate (ok) | shift [coordinate] | shift | 1.00 | coordinate | 1.00 | - |
| water_unary_0 | unary | 0.630 | 0.03 | unary (ok) | gain [unary] | gain | 1.00 | unary | 1.00 | - |
| water_tail_0 | tail | 0.550 | 0.03 | tail (ok) | lam [tail] | lam | 1.00 | tail | 1.00 | - |
| corn_stop_0 | stop | 0.243 | 0.00 | stop (ok) | events [stop] | events | 1.00 | stop | 1.00 | - |
| corn_stop_1 | stop | 0.105 | 0.11 | stop (ok) | events [stop] | events | 1.00 | stop | 1.00 | - |
| corn_corner_0 | corner | 0.151 | 0.02 | corner (ok) | corner_tighten [corner] | corner_tighten | 1.00 | corner | 1.00 | - |
| corn_corner_1 | corner | 0.202 | 0.05 | corner (ok) | corner_tighten [corner] | corner_tighten | 1.00 | corner | 1.00 | - |
| water_interaction_0 | interaction | 0.580 | 0.10 | interaction (ok) | pair [interaction] | pair | 1.00 | interaction | 1.00 | - |
| water_interaction_1 | interaction | 0.593 | 0.17 | interaction (ok) | pair [interaction] | pair | 1.00 | interaction | 1.00 | - |
| mix_interaction_coordinate_0 | interaction+coordinate | 0.900 | 0.04 | coordinate (ok) | shift [coordinate] | shift | 1.00 | interaction | 0.02 | 0.83 |
| mix_interaction_coordinate_1 | interaction+coordinate | 0.935 | 0.05 | coordinate (ok) | shift [coordinate] | shift | 1.00 | interaction | 0.00 | 0.62 |
| mix_unary_stop_0 | unary+stop | 0.421 | 0.04 | unary (ok) | width [unary] | width | 1.00 | stop | 0.01 | 1.0 |
| mix_unary_stop_1 | unary+stop | 0.321 | 0.01 | unary (ok) | width [unary] | width | 1.00 | stop | 0.01 | 1.0 |
| mix_coordinate_corner_0 | coordinate+corner | 0.210 | 0.04 | coordinate (ok) | shift [coordinate] | shift | 1.00 | coordinate | 1.00 | 1.0 |
| mix_tail_smooth_0 | tail+smooth | 0.351 | 0.04 | tail (ok) | decay [tail] | decay | 1.00 | tail | 1.00 | 0.86 |
| mix_corner_stop_0 | corner+stop | 0.214 | 0.01 | corner (ok) | corner_tighten [corner] | corner_tighten | 1.00 | corner | 1.00 | 0.3 |
| mix_coordinate_unary_0 | coordinate+unary | 0.792 | 0.07 | coordinate (ok) | shift [coordinate] | shift | 1.00 | coordinate | 1.00 | 1.0 |
| unknown_wind_0 | unknown | 0.372 | 0.92 | None (unknown) | smooth_uniform [smooth] | None | 0.00 | None | 0.00 | - |
| unknown_wind_1 | unknown | 0.396 | 0.92 | None (unknown) | amp [unary] | None | 0.00 | None | 0.00 | - |
| unknown_hidden_walker_0 | unknown | 0.699 | 0.99 | None (unknown) | width [unary] | None | 0.00 | None | 0.00 | - |
| unknown_hidden_splash_0 | unknown | 0.586 | 0.70 | None (unknown) | gain [unary] | None | 0.00 | None | 0.00 | - |
| unknown_hidden_splash_1 | unknown | 0.574 | 0.70 | None (unknown) | gain [unary] | None | 0.00 | None | 0.00 | - |
| gap_offcentre_0 | space_coordinate | 1.322 | 0.56 | unary (ok) | gain [unary] | gain | 1.00 | unary | 1.00 | - |

## Frozen bars

| bar | target | result | pass |
|---|---|---|---|
| B1 oracle value captured | median >= 0.90 | 1.000 (mean 0.982, n 24) | True |
| B2 search reduction | median <= 1/3 | 0.167 | True |
| B3 abstention | unknown >= 80%, known false <= 10% | 5/5 and 0/24 | True |
| B4 mixtures | median two-step >= 0.75 | 0.931 (n 8) | True |

## Reported, not scored

RGRE-1's coherence-weighted rule on the same cases: median 1.000, mean 0.752; the projection rule wins 6 cases and loses 0.

Identity: 0.96 against the injected class, 0.96 against the oracle's.

Vocabulary-gap case (unscored): gap_offcentre_0 q_perp 0.56, chose unary, oracle gain removing 24% of the error

Median value captured by injected class: tail 1.00, coordinate 1.00, unary 1.00, stop 1.00, corner 1.00, interaction 1.00

## Verdict: replicated: the simplified selector holds on fresh cases

