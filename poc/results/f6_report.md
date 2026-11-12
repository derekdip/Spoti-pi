# F6 scored: 9 design scenes, 6 transfer scenes

## G1 value captured per step (oracle gain > 0), median / mean, and repairs needed per step
  projection  median 0.452 mean 0.444 over 120 steps | repairs/step median 1 of 12
  hybrid      median 1.000 mean 0.750 over 120 steps | repairs/step median 6 of 12
  oracle      median 1.000 mean 1.000 over 120 steps | repairs/step median 12 of 12
  [design] projection 0.62 hybrid 1.00
  [transfer] projection 0.35 hybrid 1.00
-> G1 pass (bar: hybrid median >= 0.90 and above projection)

## G2 terminal in-sample reduction after 8 steps, (e_v0 - e_8)/e_v0
  projection  median 0.241 mean 0.286
  hybrid      median 0.289 mean 0.345
  oracle      median 0.320 mean 0.369
  hybrid vs projection: wins 14 losses 1 ties 0; hybrid / oracle median 0.902
    obstacle          v0 0.929 -> proj 0.559 hyb 0.511 orc 0.506 | held-out 0.551/0.500/0.491 floor 0.121
    windy             v0 0.962 -> proj 0.411 hyb 0.418 orc 0.385 | held-out 0.410/0.418/0.384 floor 0.004
    twin              v0 0.762 -> proj 0.440 hyb 0.396 orc 0.396 | held-out 0.526/0.488/0.488 floor 0.280
    shutoff           v0 0.777 -> proj 0.589 hyb 0.582 orc 0.528 | held-out 0.594/0.577/0.523 floor 0.125
    split             v0 1.190 -> proj 0.550 hyb 0.519 orc 0.417 | held-out 0.555/0.503/0.399 floor 0.095
    ignition          v0 0.815 -> proj 0.698 hyb 0.561 orc 0.542 | held-out 0.698/0.561/0.542 floor 0.001
    delayed_ignition  v0 0.845 -> proj 0.641 hyb 0.631 orc 0.631 | held-out 0.641/0.631/0.631 floor 0.002
    full              v0 0.840 -> proj 0.622 hyb 0.586 orc 0.551 | held-out 0.622/0.586/0.551 floor 0.001
    shelf_bed         v0 0.854 -> proj 0.778 hyb 0.702 orc 0.689 | held-out 0.778/0.702/0.689 floor 0.013
    gusty             v0 0.743 -> proj 0.604 hyb 0.565 orc 0.565 | held-out 0.604/0.565/0.565 floor 0.001
    gust_shelf        v0 0.787 -> proj 0.649 hyb 0.603 orc 0.559 | held-out 0.649/0.604/0.559 floor 0.002
    fast_gust         v0 0.624 -> proj 0.595 hyb 0.521 orc 0.515 | held-out 0.595/0.521/0.515 floor 0.002
    strong_gust       v0 0.795 -> proj 0.627 hyb 0.595 orc 0.595 | held-out 0.627/0.595/0.595 floor 0.002
    gust_twin         v0 1.219 -> proj 0.557 hyb 0.438 orc 0.437 | held-out 0.557/0.438/0.437 floor 0.003
    bed_chain         v0 0.833 -> proj 0.654 hyb 0.592 orc 0.576 | held-out 0.654/0.592/0.576 floor 0.002
-> G2 FAIL (bar: hybrid median >= projection median and >= 0.95 x oracle median)

## G3 dictionary check on the transfer scenes: step-zero gap on the same side of 0.25 as the design classification
  gusty:amp=0.03! gusty:rate=0.68 gusty:rise=0.97 gusty:cool=0.43 gusty:width=0.06 gusty:wind=0.45 gusty:base=0.00 gusty:profile=0.00 gust_shelf:amp=0.04! gust_shelf:rate=0.81 gust_shelf:rise=0.98 gust_shelf:cool=0.47 gust_shelf:width=0.07 gust_shelf:wind=0.68 gust_shelf:deflect=0.66! gust_shelf:base=0.00 gust_shelf:profile=0.00 fast_gust:amp=0.05! fast_gust:rate=0.81 fast_gust:rise=0.90 fast_gust:cool=0.39 fast_gust:width=0.10 fast_gust:wind=0.92 fast_gust:base=0.00 fast_gust:profile=0.09 strong_gust:amp=0.04! strong_gust:rate=0.74 strong_gust:rise=0.98 strong_gust:cool=0.47 strong_gust:width=0.06 strong_gust:wind=0.35 strong_gust:base=0.00 strong_gust:profile=0.00 gust_twin:amp=0.53 gust_twin:rate=1.00 gust_twin:rise=0.99 gust_twin:cool=0.72 gust_twin:width=0.27! gust_twin:wind=0.75 gust_twin:base=0.00 gust_twin:attract=0.25 gust_twin:profile=0.04 bed_chain:amp=0.03! bed_chain:rate=0.74 bed_chain:rise=0.97 bed_chain:cool=0.48 bed_chain:width=0.06 bed_chain:wind=0.54 bed_chain:base=0.00 bed_chain:bed=0.99 bed_chain:profile=0.00
-> G3 pass: 44/51 = 86% (bar >= 80%)

## S1 stopping rules on the hybrid path, scored by held-out error at the stop
  null M=19    mean regret 0.0126 median 0.0000 | stops: obstac 8 windy 8 twin 8 shutof 8 split 8 igniti 8 delaye 3 full 7 shelf_ 0 gusty 8 gust_s 8 fast_g 8 strong 8 gust_t 8 bed_ch 8
  null M=49    mean regret 0.0126 median 0.0000 | stops: obstac 8 windy 8 twin 8 shutof 8 split 8 igniti 8 delaye 3 full 7 shelf_ 0 gusty 8 gust_s 8 fast_g 8 strong 8 gust_t 8 bed_ch 8
  one percent  mean regret 0.0088 median 0.0000 | stops: obstac 2 windy 8 twin 7 shutof 7 split 3 igniti 6 delaye 5 full 4 shelf_ 3 gusty 3 gust_s 4 fast_g 8 strong 4 gust_t 8 bed_ch 5
  never stop   mean regret 0.0000 median 0.0000 | stops: obstac 8 windy 8 twin 8 shutof 8 split 8 igniti 8 delaye 8 full 8 shelf_ 8 gusty 8 gust_s 8 fast_g 8 strong 8 gust_t 8 bed_ch 8
  no growth    mean regret 0.3149 median 0.2408 | stops: obstac 0 windy 0 twin 0 shutof 0 split 0 igniti 0 delaye 0 full 0 shelf_ 0 gusty 0 gust_s 0 fast_g 0 strong 0 gust_t 0 bed_ch 0
  hindsight    mean regret 0.0000 median 0.0000 | stops: obstac 8 windy 8 twin 7 shutof 7 split 3 igniti 6 delaye 5 full 8 shelf_ 6 gusty 3 gust_s 4 fast_g 8 strong 4 gust_t 8 bed_ch 5
  scenes whose last three hybrid steps each gained under 1% held-out: 6; the null rule stopped before the budget on 1 of them
  q_top / null max, median over scenes by step: 15.3 19.9 16.0 20.6 16.9 20.8 23.9 11.5
-> S1 FAIL (bar: lower mean held-out regret than the one percent rule, and stops before the budget on at least half the exhausted scenes)

## Outcome (frozen tree): G1 pass, G2 fail -> B; G3 pass, S1 fail
