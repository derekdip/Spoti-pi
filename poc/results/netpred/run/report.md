# Personalising a VR motion predictor: when to stop (frozen scorer)

Share of the possible personalisation gain kept, (generic - arm) / (generic - best along the fit); negative = worse than the generic model.


## 1 minute of motion (16 players; calibrated relative drop r* = 0.147 from 8 players)

Error 100 ms ahead, mean over players (cm^2): constant velocity 5.653, generic 1.271, best personalised 1.215.

| stop | mean share kept | lowest | players worse than generic | mean error (cm^2) |
|---|---|---|---|---|
| rule | +0.47 | -3.04 | 1 of 16 | 1.235 |
| reuse | +0.61 | -2.34 | 1 of 16 | 1.228 |
| holdout | +0.07 | -7.39 | 1 of 16 | 1.246 |
| holdout_refit | +0.30 | -6.33 | 1 of 16 | 1.234 |
| steps100 | -1.68 | -11.25 | 10 of 16 | 1.302 |
| steps300 | -1.75 | -11.25 | 11 of 16 | 1.309 |
| steps1000 | -1.75 | -11.25 | 11 of 16 | 1.309 |
| last | -1.75 | -11.25 | 11 of 16 | 1.309 |

- **N1** (the rule keeps at least 67% on average and does not end below the generic model for at least 90% of players): 0.47, 94%: **fails**
- **N2** (the rule keeps at least what the best fixed step budget keeps, chosen with the test data in hand: steps100): 0.47 against -1.68: **holds**
- **N3** (reuse of one calibrated relative drop is within 0.1 of the rule, with no extra fits): 0.61 against 0.47: **holds**

## 2 minutes of motion (16 players; calibrated relative drop r* = 0.212 from 8 players)

Error 100 ms ahead, mean over players (cm^2): constant velocity 5.653, generic 1.271, best personalised 1.170.

| stop | mean share kept | lowest | players worse than generic | mean error (cm^2) |
|---|---|---|---|---|
| rule | +0.82 | +0.41 | 0 of 16 | 1.185 |
| reuse | +0.76 | +0.32 | 0 of 16 | 1.191 |
| holdout | +0.68 | +0.32 | 0 of 16 | 1.199 |
| holdout_refit | +0.80 | +0.31 | 0 of 16 | 1.189 |
| steps100 | +0.50 | -1.36 | 3 of 16 | 1.202 |
| steps300 | +0.18 | -1.36 | 3 of 16 | 1.234 |
| steps1000 | +0.09 | -1.36 | 3 of 16 | 1.250 |
| last | +0.08 | -1.36 | 3 of 16 | 1.251 |

- **N1** (the rule keeps at least 67% on average and does not end below the generic model for at least 90% of players): 0.82, 100%: **holds**
- **N2** (the rule keeps at least what the best fixed step budget keeps, chosen with the test data in hand: steps100): 0.82 against 0.50: **holds**
- **N3** (reuse of one calibrated relative drop is within 0.1 of the rule, with no extra fits): 0.76 against 0.82: **holds**

## 5 minutes of motion (16 players; calibrated relative drop r* = 0.312 from 8 players)

Error 100 ms ahead, mean over players (cm^2): constant velocity 5.653, generic 1.271, best personalised 1.069.

| stop | mean share kept | lowest | players worse than generic | mean error (cm^2) |
|---|---|---|---|---|
| rule | +0.90 | +0.76 | 0 of 16 | 1.091 |
| reuse | +0.87 | +0.50 | 0 of 16 | 1.088 |
| holdout | +0.71 | +0.44 | 0 of 16 | 1.123 |
| holdout_refit | +0.90 | +0.73 | 0 of 16 | 1.086 |
| steps100 | +0.84 | +0.69 | 0 of 16 | 1.106 |
| steps300 | +0.88 | +0.25 | 0 of 16 | 1.085 |
| steps1000 | +0.66 | +0.21 | 0 of 16 | 1.124 |
| last | +0.59 | +0.15 | 0 of 16 | 1.141 |

- **N1** (the rule keeps at least 67% on average and does not end below the generic model for at least 90% of players): 0.90, 100%: **holds**
- **N2** (the rule keeps at least what the best fixed step budget keeps, chosen with the test data in hand: steps300): 0.90 against 0.88: **holds**
- **N3** (reuse of one calibrated relative drop is within 0.1 of the rule, with no extra fits): 0.87 against 0.90: **holds**

**Outcome: C** (A: N1 to N3 hold at every size; B: N1 holds everywhere, N2 or N3 fails somewhere; C: N1 fails somewhere).
