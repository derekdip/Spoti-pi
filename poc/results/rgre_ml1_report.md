114 cases pooled from seeds [101, 102, 103]

| bar | target | result | |
|---|---|---|---|
| B1 abstention AUC (field) | >= 0.90 | 0.964 | pass |
| B2 two-step recovery (field) | >= 0.85 | 1.000 | pass |
| B3 field beats consumer | identity and AUC both higher | identity 0.85 vs 0.46; AUC 0.96 vs 0.80 | pass |
| B4 selection value (field = MP) | >= 0.90 and above baselines | median 1.00 mean 0.83 | random 0.16/0.31 cheapest 0.13/0.27 gradnorm 0.97/0.68 | pass |
| B5 tau transfers (predicted fail) | oov >= 80%, known <= 10% | 67%, 27% | FAIL |
| B6 controls decline | >= 75% | 83% | pass |
| B7 orthogonal deferral (predicted fail) | >= 60% of oov cases | 8% | FAIL |
| B8 search fraction | <= 1/3 | 0.10 | pass |

Outcome by the frozen tree (B1 x B2): **A**

per seed:
  seed 101: AUC field 0.99 consumer 0.84 | two-step field 0.98 consumer 0.66 | identity field 0.83 consumer 0.50 | value field 1.00
  seed 102: AUC field 0.88 consumer 0.78 | two-step field 1.00 consumer 1.00 | identity field 0.83 consumer 0.28 | value field 1.00
  seed 103: AUC field 1.00 consumer 0.81 | two-step field 1.00 consumer 0.89 | identity field 0.89 consumer 0.61 | value field 1.00

other reported quantities:
  value_rgre                 0.394
  value_rgre_notabstained    0.941
  identity                   0.352
  oracle_identity            0.815
  two_step_found_field       1.375
  q_perp_known               0.444
  q_perp_oov                 0.682
  defer_oov_mag              0.349
  defer_oov_orth_global      0.352
  defer_oov_random           0.379
  defer_iso_orthg_wins       0.352
  ctrl_abstain               0.417
