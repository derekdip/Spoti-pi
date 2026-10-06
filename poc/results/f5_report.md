5 of 5 fresh scenes present

### Fresh scenes, at the cross-evaluated best state

| scene | gust | V0 | floor (de, two-stage) | best fit | sway: model / teacher | ratio | phase err | glow corr | burn wrong | passable wrong | missed alight | parcels | greedy / floor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gust_shelf | 1.8 m/s @ 0.7 Hz | 0.787 | 0.519 (0.551, 0.519) | standard | 6.3 / 10.1 cm | 63% | 31 deg | 0.80 | 11.1% | 7.4% |  | 12 | 0.71 |
| fast_gust | 1.6 m/s @ 1.4 Hz | 0.624 | 0.461 (0.461, 0.484) | standard | 3.5 / 4.7 cm | 73% | 54 deg | 0.66 | 4.6% | 4.1% |  | 16 | 0.26 |
| strong_gust | 2.6 m/s @ 0.7 Hz | 0.795 | 0.496 (0.581, 0.496) | standard | 11.3 / 16.8 cm | 68% | 34 deg | 0.80 | 11.4% | 9.4% |  | 11 | 0.55 |
| gust_twin | 1.5 m/s @ 0.7 Hz | 1.219 | 0.402 (0.402, 0.445) | standard | 3.9 / 5.1 cm | 76% | 109 deg | 0.85 | 1.9% | 2.0% |  | 4 | 0.84 |
| bed_chain | 2.0 m/s @ 0.7 Hz | 0.833 | 0.532 (0.560, 0.532) | standard | 9.6 / 12.5 cm | 77% | 26 deg | 0.81 | 15.0% | 12.7% | 20% | 12 | 0.70 |

### Bars

| bar | target | result | |
|---|---|---|---|
| B1 motion | median ratio in [0.5,1.5], median phase err <= 45 deg | 0.73, 34 deg | pass |
| B2 shape | median glow correlation >= 0.70 | 0.800 (a static blob reaches 0.85) | pass |
| B3 decisions | burn <=5%, passable <=5%, alight missed <=25% | 11.1%, 7.4%, 20% | FAIL |
| B4 cost | <= 20 parcels on every fresh scene | max 16 | pass |
| B5 transfer | ratio in [0.5,1.5] and phase err <= 60 deg on both | fast_gust 140%/31deg; strong_gust 38%/34deg | FAIL |
| (reported) search | median greedy / floor | 0.70 | |

Outcome by the frozen tree (B1 motion x B2 shape): **A**

### Paired re-measurement (declared seen; F4 numbers are its frozen standard floors)

| scene | F4 error | F5 error | change | F5 sway ratio | phase err | parcels | F4 parcels |
|---|---|---|---|---|---|---|---|
| ignition | 0.481 | 0.538 | +11.8% | 103% | 30 deg | 13 | 26 |
| full | 0.470 | 0.475 | +1.1% | 86% | 22 deg | 11 | 7 |
| windy | 0.329 | 0.367 | +11.5% | 437% | 40 deg | 6 | 6 |

pilot `gusty` (seen): error 0.464, sway 67% at 37 deg, 11 parcels

look-fit versus standard-fit sway ratio, every scene that has both:
  gusty         standard   67% ( 37 deg, E 0.464)   look  103% ( 30 deg, E 0.502)   best: standard
  gust_shelf    standard   63% ( 31 deg, E 0.519)   look   93% ( 26 deg, E 0.538)   best: standard
  fast_gust     standard   73% ( 54 deg, E 0.461)   look   91% ( 58 deg, E 0.517)   best: standard
  strong_gust   standard   68% ( 34 deg, E 0.496)   look   89% ( 25 deg, E 0.498)   best: standard
  gust_twin     standard   76% (109 deg, E 0.402)   look   13% ( 71 deg, E 0.408)   best: standard
  bed_chain     standard   77% ( 26 deg, E 0.532)   look   87% ( 17 deg, E 0.572)   best: standard
  ignition      standard  103% ( 30 deg, E 0.538)   look   66% ( 10 deg, E 0.544)   best: standard
  full          standard   86% ( 22 deg, E 0.475)   look   99% ( 34 deg, E 0.501)   best: standard
  windy         standard   90% ( 70 deg, E 0.372)   look  437% ( 40 deg, E 0.367)   best: look

v_rise at the best state, against F4's 0.37 to 0.56 on gusted scenes (P1):
  gust_shelf    v_rise 0.57 m/s
  fast_gust     v_rise 1.73 m/s
  strong_gust   v_rise 0.59 m/s
  gust_twin     v_rise 1.37 m/s
  bed_chain     v_rise 0.51 m/s
  ignition      v_rise 0.61 m/s
  full          v_rise 0.43 m/s
  windy         v_rise 0.93 m/s
