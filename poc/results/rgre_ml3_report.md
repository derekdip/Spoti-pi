# RGRE-ML-3 scored: 30 cases, seeds [1, 2, 3, 4, 5], M_PERM 49

growth path identical to RGRE-ML-2 on 30 of 30 cases

## Held-out error at the chosen stop, 30 cases
rule          mean regret   median  mean err stop=best  stop step median by dataset
null M=9           0.0351   0.0022    0.6332       33%  abal 8 cali 8 conc 8 diab 0 mpg 5 wine 4
null M=19          0.0351   0.0022    0.6332       33%  abal 8 cali 8 conc 8 diab 0 mpg 5 wine 4
null M=49          0.0348   0.0022    0.6329       33%  abal 8 cali 8 conc 8 diab 0 mpg 5 wine 4
one percent        0.0143   0.0114    0.6124       13%  abal 0 cali 0 conc 6 diab 1 mpg 5 wine 1
never stop         0.0360   0.0020    0.6341       40%  abal 8 cali 8 conc 8 diab 8 mpg 8 wine 8
no growth          0.0522   0.0249    0.6503        3%  abal 0 cali 0 conc 0 diab 0 mpg 0 wine 0
hindsight          0.0000   0.0000    0.5981      100%  abal 6 cali 8 conc 8 diab 2 mpg 8 wine 3

## C1 null M=19 against the one percent rule: wins 15 losses 9 ties 6; mean regret 0.0351 vs 0.0143
-> C1 FAIL (bar: more wins than losses and lower mean regret)
## C2 null M=19 against never stopping (0.0360) and not growing (0.0522): mean regret 0.0351
-> C2 pass (bar: lower mean regret than both)

  abalone     regret null19 0.0012 one% 0.0125 never 0.0012 none 0.0125 | wins/losses vs one% 5/0
  california  regret null19 0.1713 one% 0.0241 never 0.1713 none 0.0241 | wins/losses vs one% 4/1
  concrete    regret null19 0.0000 one% 0.0171 never 0.0000 none 0.1750 | wins/losses vs one% 3/0
  diabetes    regret null19 0.0172 one% 0.0111 never 0.0314 none 0.0133 | wins/losses vs one% 1/3
  mpg         regret null19 0.0167 one% 0.0121 never 0.0051 none 0.0713 | wins/losses vs one% 0/3
  winered     regret null19 0.0043 one% 0.0090 never 0.0070 none 0.0172 | wins/losses vs one% 2/2
permuted targets, step zero: null M=9 declines 100% (expected about 90%)
permuted targets, step zero: null M=19 declines 100% (expected about 95%)
permuted targets, step zero: null M=49 declines 100% (expected about 98%)
real targets, step zero: null M=19 declines 13%

## Linearisation gap (post-hoc, no bar)
median gap of the fitted contribution outside the tangent span, by module kind: quad 0.00, cubic 0.00, pair 0.00, exp 0.00, step 0.01, abs 0.02, sin 0.09, bump 0.30
gap of the oracle's module vs value captured, 240 steps: Spearman -0.314 (p 6.7e-07); gap of the pick's module median 0.00; oracle's 0.38; anchored span 0.05
value when the oracle's gap < 0.25: median 0.79 (n=64); when >= 0.25: 0.43 (n=176)
  abalone     oracle gap median 0.35 value 0.38
  california  oracle gap median 0.29 value 0.44
  concrete    oracle gap median 0.15 value 0.73
  diabetes    oracle gap median 0.35 value 0.47
  mpg         oracle gap median 0.62 value 0.51
  winered     oracle gap median 0.70 value 0.41
