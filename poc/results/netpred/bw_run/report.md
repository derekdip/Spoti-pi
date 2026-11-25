# Model-predictive avatar sync (frozen scorer)

Bytes per second per player (streaming every frame: 1980), mean over 24 players; the receiver's error never exceeds the tolerance by construction, checked below.

| receiver | 0.5 cm | 1.0 cm | 2.0 cm |
|---|---|---|---|
| hold | 1131 | 732 | 435 |
| deadreck | 1277 | 994 | 847 |
| deadreck_smooth | 763 | 452 | 316 |
| generic_small | 776 | 478 | 366 |
| generic | 695 | 412 | 316 |
| personal | 704 | 413 | 314 |

- **W1** (the learned receiver sends at least 30% fewer bytes than the best simple receiver at every tolerance): 9%, 9%, 0%: **fails**
- **W2** (the receiver's error never exceeds the tolerance, any receiver, any player): **holds**
- **W3** (personalising saves at least 5% more at 1 cm): -0.3%: **fails**
- **W4** (the larger receiver model sends fewer bytes than the small one at every tolerance): 776 against 695, 478 against 412, 366 against 316: **holds**
