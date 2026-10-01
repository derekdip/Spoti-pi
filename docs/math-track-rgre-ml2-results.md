# RGRE-ML-2 results: outcome D. On real data the projection cannot rank modules whose shape must be fitted; the abstention quantity tells structure from noise on every split and is a stopping signal above the step index; deferral by orthogonality ties magnitude

Preregistration: `docs/math-track-rgre-ml2-prereg.md`, frozen at commit
`4e33531`, unchanged. Raw output: `poc/results/rgre_ml2.json`, `.log`,
`rgre_ml2_report.md` (the frozen scorer's output, `poc/rgre_ml/score_real.py`,
committed before the scored splits ran). Six datasets, split seeds 1 to
5, 30 cases, 240 growth steps, 308 seconds on four workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| B1 selection value | median `>= 0.90` of the oracle's in-sample drop; above random and gradient-norm | **0.475** (mean 0.53); random 0.12, gradient-norm 0.35 | **fail, as predicted** |
| B2 stopping signal | AUC of `q_perp` for a wasted step `>= 0.75`, above the step index | **0.840**; step index 0.618; in-sample drop of the fitted pick 0.886 | pass |
| B3 deferral | top-S orthogonal beats magnitude on `>= 60%`, ties against; median below magnitude and random | **17%** wins, 77% ties; medians 0.613 / 0.613 / 0.633 | **fail, as predicted** |
| B4 noise detection | permuted above real on `>= 90%` of splits | **100%** (30 of 30); pooled AUC 0.99 | pass |

B1 fails, so the letter is **D**: the projection does not select well
on real data with free-shape modules. B2 holds, so the write-up says
what the tree said it would say in that case: the quantity can be a
stopping signal for a growth procedure whose selection is done some
other way.

## What each bar means

**Selection fails for the reason stated in advance, and exactly
there.** The oracle's best single step was a two-dimensional Gaussian
bump on 201 of 240 steps and a sinusoid on 28: modules whose centre,
width, frequency or phase must be fitted. On those 233 steps the pick
captured 0.46 of the oracle's drop in median and was the oracle on 9
percent. On the 7 steps where the oracle was a fixed-shape module (a
product, a square, a cube, an absolute value at the canonical
threshold), the pick was the oracle on all 7 with value 1.00. So the
identity with matching pursuit holds where matching pursuit's premise
holds, a fixed atom, and the on-state tangent of a free-shape module
does not say where its fit will end. Concrete, the dataset with the
most structure to find, reached 0.73; abalone, the least, 0.38. The
declared anchored-tangent variant, several fixed on-states per module,
lifts the median to 0.60 and is still far from the bar; on the pilot it
had been worse, and across 240 steps it is better on five datasets of
six. Neither version is a way to rank fitted shapes by projection.

**The abstention quantity is a stopping signal, with a qualification
the pooled number hides.** Read before a step and without any fit, the
single-class `q_perp` predicts whether the step's held-out gain will be
under one percent with AUC 0.84, against 0.62 for the step index. The
in-sample drop of the fitted pick, which costs the fit, reaches 0.89.
The qualification is where the signal lives: at step zero the median
`q_perp` is 0.61 on concrete, 0.77 on auto mpg and 0.96 to 0.97 on the
other four, and the held-out gain of eight steps on those datasets is
27, 15 and 0.6 to 4 percent. Much of the pooled AUC is the quantity
telling the six datasets apart by how much explainable structure they
hold, which is a legitimate use and the one a practitioner would make
of it first. Within a dataset the AUC is 0.62 to 0.88, above the step
index on four datasets and below it on diabetes and red wine, where
the step index alone reaches 0.81 and 0.95 because nearly every step
is wasted. The bar passes as frozen; the within-dataset signal is
real and modest.

**Deferral ties.** Top-S orthogonal and magnitude deferral chose the
same three regions on 23 of 30 cases and the scores tie there; where
they differed, orthogonal won 5 and lost 2. The reason is in the
numbers above: with `q_perp` at 0.96 on four datasets, projecting
the residual onto the eight top-ranked classes removes almost nothing
from any region, so "unexplainable energy" is energy. Hindsight
deferral, the best three regions chosen on the held-out residual
itself, scores 0.607 against magnitude's 0.613 and no deferral's
0.631, so on these datasets deferring a quarter of the input space
moves the error by three percent and no ranking rule has much room.
The claim RGRE-ML-1b established by a two percent margin does not
reach real data, as predicted, and is dropped for it.

**Noise detection holds without exception.** On every one of 30 splits
the step-zero `q_perp` on shuffled targets is above the value on the
real targets, 0.995 against 0.963 in median, with the closest pair on
diabetes (0.975 against 0.968). The joint version RGRE-ML-1 used
reads 0.35 against 0.66 and would have failed on the small datasets
for the reason the preregistration gave.

## Reported

**The one percent dead rule sits at the noise floor.** On permuted
targets the best spurious in-sample drop among 66 to 176 candidates
has median 0.49 percent and maximum 1.59 percent, so the rule declines
93 percent of pure-noise steps. On real targets it stops abalone and
California at step zero, where eight steps still gain 2 and 4 percent
held-out, and diabetes and red wine at step one, where the best step
is two or three. It never lets growth run on a dataset with structure
and stops it early on the ones without much; a rule on held-out data
would do better and costs data.

**The grown model is worth having where there is structure.** Eight
steps beat the linear model on held-out error in 83 percent of cases
and ten-nearest-neighbours in 83 percent. Concrete falls from 0.63 to
0.45 of a standard deviation, auto mpg from 0.43 to 0.37; abalone,
California and red wine move by one to four percent; diabetes gets
worse by step eight. The modules grown were products (71), bumps
(64), cubes (33) and sinusoids (27); the oracle would have grown bumps
almost every time.

**One blow-up.** California seed 5 goes from 0.602 to 1.454 held-out
at step six, when an exponential module of the bedrooms feature,
fitted within its bounds on the training range, is evaluated on a
test outlier several training standard deviations out. The dead-stop
student for that case is the linear one and no bar is touched. It is
the extrapolation hazard of an unbounded basis function, and a bound on
the module's *output* rather than its parameters is the fix, not run.

**Held-out value of the pick** (its held-out drop over the best
candidate's held-out drop) is 0.31 in median and negative on diabetes:
on a noisy small dataset the projection's pick tends to hurt out of
sample, where the oracle's would have helped.

## What RGRE-ML-2 establishes

1. RGRE's selection rule is matching pursuit and inherits its premise:
   an atom with a fixed shape. On six real datasets the useful atoms
   were free-shape modules on 233 of 240 steps, and the projection
   ranked them at half the oracle's value. A growth procedure for real
   data needs to fit before it ranks, or restrict itself to fixed
   atoms, and the second choice would have thrown away most of the
   gain here.
2. The abstention quantity separates structure from noise on every
   real split and is a stopping signal above the trivial baseline;
   most of its signal is between datasets, some is within.
3. Deferral by orthogonality is dropped for real data. It needs a
   residual that the dictionary can partly explain, and on four of six
   datasets it could not.
4. No constant transferred again: the one percent rule stops too early
   on the datasets with something to find.

No rescue, no second run on the scored splits. Nothing above is edited
after the run.
