# F7 scored: 7 scenes, 10 steps

## K1 value per step against the oracle table
  hybrid, no templates      median 1.000 mean 0.844 (68 steps) repairs/step median 6
  hybrid, no templates, 2   median 1.000 mean 0.927 (68 steps) repairs/step median 7
  F6 hybrid with templates  median 1.000 mean 0.758 (56 steps, 8 per scene)
  steps under 0.9: 18 of 68 (oracle small-gap on 18); F6 hybrid: 19 of 56 (small-gap 19)
-> K1 pass (bar: median >= 0.90 and mean above F6's hybrid on these scenes)

## K2 terminal error against F4's projection greedy (10 steps, the arc's workflow)
  scene                 v0  F4 greedy  F7 hybrid  F7 hyb2  F4 floor  column | glow: F4 floor / F4 look / F7 hybrid | F6 hybrid(8)
  ignition           0.815      0.648      0.561    0.560     0.481   0.580 | 0.73 / 0.39 / 0.58 | 0.561
  delayed_ignition   0.845      0.732      0.631    0.631     0.577   0.626 | 0.75 / 0.61 / 0.66 | 0.631
  full               0.840      0.525      0.591    0.529     0.470   0.590 | 0.75 / 0.76 / 0.59 | 0.586
  twin               0.762      0.412      0.396    0.396     0.454   0.503 | 0.83 / 0.91 / 0.90 | 0.396
  shelf_bed          0.854      0.717      0.689    0.689     0.494   0.615 | 0.68 / 0.54 / 0.79 | 0.702
  split              1.190      0.550      0.436    0.427     0.417   0.411 | 0.77 / 0.91 / 0.79 | 0.519
  shutoff            0.777      0.586      0.582    0.508     0.569   0.551 | nan / nan / nan | 0.582
  hybrid below F4 greedy on 6 of 7 (above on 1); below the column grammar's best known on 2
-> K2 pass (bar: below F4's greedy on >= 6 of 7)

## K3 terminal reduction against F4's global floor (differential evolution, 22 parameters)
  median reduction: F4 greedy 0.246, F7 hybrid 0.297, F4 floor 0.410; hybrid / floor 0.725 (F4 greedy / floor 0.600)
-> K3 FAIL (bar: >= 0.95)

## K4 the look: glow correlation at the hybrid terminal against F4's floor state
  hybrid above F4 floor state on 3 of 7; medians hybrid nan F4 floor nan F4 look fit nan
-> K4 FAIL (bar: above on >= 4 of 7)

## Reported: decisions at the hybrid terminal (heat wrong, ai wrong, ignition missed) against F4's floor
  ignition          heat 14.3% / 12.3%  ai 11.6% / 9.8%  ignition missed 17% / 6%  parcels 31 / 26
  delayed_ignition  heat 21.3% / 16.2%  ai 15.9% / 12.6%  ignition missed 0% / 11%  parcels 17 / 32
  full              heat 14.9% / 9.4%  ai 10.5% / 6.9%  ignition missed 22% / 11%  parcels 17 / 7
  twin              heat 8.5% / 12.0%  ai 6.7% / 7.3%  parcels 20 / 16
  shelf_bed         heat 11.5% / 11.5%  ai 8.4% / 7.6%  ignition missed 0% / 0%  parcels 20 / 30
  split             heat 0.1% / 0.2%  ai 0.9% / 0.9%  parcels 33 / 12
  shutoff           heat 4.6% / 3.3%  ai 3.0% / 2.6%  parcels 15 / 12

## Outcome (frozen tree): K2 pass, K3 fail -> B; K1 pass, K4 fail
