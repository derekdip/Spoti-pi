# Reach-aware menus (frozen scorer)

Buttons of 6 (3 per hand) inside the player's true 50% comfort region, mean over the evaluation players; the 80% region in brackets.

| arm | 1 min | 2 min | 5 min |
|---|---|---|---|
| fixed | 0.12 (0.42) | 0.12 (0.42) | 0.12 (0.42) |
| generic | 1.12 (2.29) | 1.12 (2.29) | 1.12 (2.29) |
| rule | 3.00 (4.42) | 3.33 (4.83) | 4.17 (5.42) |
| reuse | 2.83 (4.04) | 3.12 (4.71) | 3.42 (4.79) |
| holdout | 2.67 (4.38) | 3.54 (4.88) | 4.12 (5.29) |
| steps100 | 3.29 (4.67) | 3.75 (5.04) | 4.46 (5.54) |
| steps300 | 2.79 (4.17) | 2.92 (4.33) | 3.83 (5.08) |
| steps1000 | 2.12 (3.75) | 2.71 (4.25) | 3.50 (4.88) |
| oracle | 3.12 (4.42) | 3.58 (4.62) | 4.21 (5.33) |
| last | 2.25 (3.75) | 2.67 (4.46) | 3.46 (4.75) |

- 1 min, **R1** (the rule places at least 0.5 more buttons than the height-scaled default): 3.00 against 1.12: **holds**
- 1 min, **R2** (the rule at least matches training without stopping, 2.25, and is no worse than the default for at least 90% of players: 96%): **holds**
- 1 min, **R3** (one calibrated value reused within 0.3 buttons of the rule): 2.83 against 3.00: **holds**
- 2 min, **R1** (the rule places at least 0.5 more buttons than the height-scaled default): 3.33 against 1.12: **holds**
- 2 min, **R2** (the rule at least matches training without stopping, 2.67, and is no worse than the default for at least 90% of players: 100%): **holds**
- 2 min, **R3** (one calibrated value reused within 0.3 buttons of the rule): 3.12 against 3.33: **holds**
- 5 min, **R1** (the rule places at least 0.5 more buttons than the height-scaled default): 4.17 against 1.12: **holds**
- 5 min, **R2** (the rule at least matches training without stopping, 3.46, and is no worse than the default for at least 90% of players: 100%): **holds**
- 5 min, **R3** (one calibrated value reused within 0.3 buttons of the rule): 3.42 against 4.17: **fails**

**Outcome: B** (A: R1 to R3 at every size; B: R1 everywhere, R2 or R3 fails somewhere; C: R1 fails somewhere).
- Reported, limited reach (below 0.8), 12 players: generic 1.83, 1.83, 1.83; rule 2.92, 3.75, 4.17
- Reported, seated, 7 players: generic 0.86, 0.86, 0.86; rule 2.86, 3.29, 4.00
- Reported, left-leaning (right share below 0.5), 8 players: generic 1.12, 1.12, 1.12; rule 3.00, 3.25, 4.25
