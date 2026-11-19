# Reach-aware menus (frozen scorer)

Buttons of 6 (3 per hand) inside the player's true 50% comfort region, mean over the evaluation players; the 80% region in brackets.

| arm | 1 min | 2 min | 5 min |
|---|---|---|---|
| fixed | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| generic | 0.75 (2.75) | 0.75 (2.75) | 0.75 (2.75) |
| rule | 3.50 (4.75) | 3.75 (4.75) | 5.00 (5.75) |
| reuse | 2.50 (4.75) | 3.25 (4.50) | 4.25 (5.50) |
| holdout | 3.50 (5.25) | 3.50 (5.00) | 4.75 (5.50) |
| steps100 | 3.25 (4.50) | 3.00 (4.75) | 5.00 (5.75) |
| steps300 | 2.25 (4.00) | 3.25 (4.50) | 3.75 (4.50) |
| steps1000 | 2.75 (3.50) | 2.75 (5.25) | 3.25 (4.00) |
| oracle | 3.25 (5.00) | 3.75 (4.50) | 4.75 (5.75) |
| last | 2.75 (3.75) | 2.75 (4.75) | 3.25 (4.25) |

- 1 min, **R1** (the rule places at least 0.5 more buttons than the height-scaled default): 3.50 against 0.75: **holds**
- 1 min, **R2** (the rule at least matches training without stopping, 2.75, and is no worse than the default for at least 90% of players: 100%): **holds**
- 1 min, **R3** (one calibrated value reused within 0.3 buttons of the rule): 2.50 against 3.50: **fails**
- 2 min, **R1** (the rule places at least 0.5 more buttons than the height-scaled default): 3.75 against 0.75: **holds**
- 2 min, **R2** (the rule at least matches training without stopping, 2.75, and is no worse than the default for at least 90% of players: 100%): **holds**
- 2 min, **R3** (one calibrated value reused within 0.3 buttons of the rule): 3.25 against 3.75: **fails**
- 5 min, **R1** (the rule places at least 0.5 more buttons than the height-scaled default): 5.00 against 0.75: **holds**
- 5 min, **R2** (the rule at least matches training without stopping, 3.25, and is no worse than the default for at least 90% of players: 100%): **holds**
- 5 min, **R3** (one calibrated value reused within 0.3 buttons of the rule): 4.25 against 5.00: **fails**

**Outcome: B** (A: R1 to R3 at every size; B: R1 everywhere, R2 or R3 fails somewhere; C: R1 fails somewhere).
- Reported, limited reach (below 0.8), 3 players: generic 1.00, 1.00, 1.00; rule 3.67, 4.00, 5.00
- Reported, seated, 1 players: generic 1.00, 1.00, 1.00; rule 5.00, 4.00, 6.00
- Reported, left-leaning (right share below 0.5), 3 players: generic 1.00, 1.00, 1.00; rule 3.67, 3.67, 5.00
