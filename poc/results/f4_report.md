7 of 7 unseen scenes present

| scene | V0 | standard floor (de, two-stage) | column best-known | beats column | look fit -> linear | glow corr (look) | burn wrong | passable wrong | missed alight | parcels | greedy / floor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ignition | 0.815 | **0.481** (0.481, 0.594) | 0.580 | yes | 0.542 -> 0.589 | 0.39 | 12.3% | 9.8% | 6% | 26 | 0.50 |
| delayed_ignition | 0.845 | **0.577** (0.675, 0.577) | 0.626 | yes | 0.577 -> 0.585 | 0.61 | 16.2% | 12.6% | 11% | 32 | 0.42 |
| full | 0.840 | **0.470** (0.470, 0.529) | 0.590 | yes | 0.462 -> 0.483 | 0.76 | 9.4% | 6.9% | 11% | 7 | 0.85 |
| twin | 0.762 | **0.454** (0.454, 0.524) | 0.503 | yes | 0.374 -> 0.402 | 0.91 | 12.0% | 7.3% |  | 16 | 1.14 |
| shelf_bed | 0.854 | **0.494** (0.564, 0.494) | 0.615 | yes | 0.527 -> 0.583 | 0.54 | 11.5% | 7.6% |  | 30 | 0.38 |
| split | 1.190 | **0.417** (0.417, 0.488) | 0.411 | no | 0.302 -> 0.413 | 0.91 | 0.2% | 0.9% |  | 12 | 0.83 |
| shutoff | 0.777 | **0.569** (0.569, 0.588) | 0.551 | no | 0.508 -> 0.599 | 0.64 | 3.3% | 2.6% |  | 12 | 0.92 |

| bar | target | result | |
|---|---|---|---|
| B1 glow | median corr >= 0.80 | 0.644 (2 of 7 at >= 0.90) | FAIL |
| B2 floor vs column | >= 6 of 7 | 5 of 7 | FAIL |
| B3 decisions | burn <= 5%, passable <= 5%, alight missed <= 25% | 11.5%, 7.3%, 11% | FAIL |
| B4 cost | parcels <= 24 everywhere | max 32 | FAIL |
| B5 search | median greedy/floor >= 0.80 | 0.828 | pass |

Outcome by the frozen tree (B1 x B2): **D**

P1 split/shutoff below column: {'split': (0.417, 0.411), 'shutoff': (0.569, 0.551)}
P2 greedy picks: {'ignition': ['bed', 'bed', 'wind', 'base', 'cool', 'width', 'rise', 'width'], 'delayed_ignition': ['wind', 'base', 'cool', 'width', 'rise', 'cool'], 'full': ['deflect', 'wind', 'base', 'width', 'soot', 'rise', 'width', 'cool', 'width'], 'twin': ['profile', 'attract', 'width', 'amp', 'base', 'width', 'rise', 'rate'], 'shelf_bed': ['deflect', 'wind', 'base', 'width', 'rise'], 'split': ['width', 'base', 'wind', 'wind', 'amp', 'cool', 'width', 'rise'], 'shutoff': ['wind', 'width', 'base', 'jitter', 'rate', 'cool', 'width']}

per consumer at the standard floor:
  ignition          visual 0.628  heat 0.263  ignition 0.325  ai 0.597   | column: visual 0.675  heat 0.340  ignition 0.729  ai 0.804
  delayed_ignition  visual 0.595  heat 0.269  ignition 0.650  ai 0.694   | column: visual 0.684  heat 0.325  ignition 0.719  ai 0.721
  full              visual 0.632  heat 0.261  ignition 0.253  ai 0.592   | column: visual 0.699  heat 0.311  ignition 0.486  ai 0.773
  twin              visual 0.540  heat 0.260  ai 0.510   | column: visual 0.494  heat 0.273  ai 0.665
  shelf_bed         visual 0.685  heat 0.282  ignition 0.276  ai 0.594   | column: visual 0.674  heat 0.288  ignition 1.000  ai 0.726
  split             visual 0.655  heat 0.151  ai 0.265   | column: visual 0.658  heat 0.131  ai 0.238
  shutoff           visual 0.704  heat 0.194  ai 0.661   | column: visual 0.696  heat 0.183  ai 0.627
