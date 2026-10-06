# RGRE-ML-3 results: Half. The self-calibrated stop beats the constant on 15 cases to 9 and in median regret, and loses the mean-regret bar to one case where an exponential module extrapolated

Preregistration: `docs/math-track-rgre-ml3-prereg.md`, frozen at commit
`29f7f59`, unchanged. Raw output: `poc/results/rgre_ml3.json`, `.log`,
`rgre_ml3_report.md` (the frozen scorer's output, `poc/rgre_ml/ml3_score.py`).
Thirty cases, the RGRE-ML-2 growth path re-grown and identical on 30 of
30, 49 shuffles per step, 395 seconds on three workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| C1 against the constant | more wins than losses in held-out error at the stop, and lower mean regret | wins **15**, losses 9, ties 6; mean regret **0.0351 vs 0.0143** | **fail** |
| C2 a stopping rule, not a rename | mean regret below never stopping and below not growing | 0.0351 vs 0.0360 and 0.0522 | pass, by 0.0009 |

Exactly one holds, so the outcome is **Half**: C2 holds, C1 fails.

## What decided it

| rule | mean regret | median regret | stop = hindsight best | stop step, median by dataset |
|---|---|---|---|---|
| null, M = 9 / 19 / 49 | 0.0351 / 0.0351 / 0.0348 | 0.0022 | 33% | abalone 8, California 8, concrete 8, diabetes 0, mpg 5, wine 4 |
| one percent | 0.0143 | 0.0114 | 13% | 0, 0, 6, 1, 5, 1 |
| never stop | 0.0360 | 0.0020 | 40% | 8 everywhere |
| no growth | 0.0522 | 0.0249 | 3% | 0 everywhere |
| hindsight | 0 | 0 | 100% | 6, 8, 8, 2, 8, 3 |

**The mean bar was decided by one case.** California seed 5 is the
case RGRE-ML-2 reported: an exponential module of the bedrooms
feature, fitted within its parameter bounds, evaluated on a test
outlier several training standard deviations out, taking held-out
error from 0.60 to 1.45. The null rule, reading a statistic still
three times its shuffled maximum at every step on that split, kept
growing and took the blow-up; so did never stopping. That single
regret of 0.85 is 81 percent of the null rule's summed regret over
30 cases. On the other 29 cases the null rule's mean regret is 0.0069
against the constant's 0.0142, which is the direction the wins and
the medians already show. That comparison is post-hoc and does not
change the verdict; the bar was the mean, the preregistration did not
exclude anything, and the case is real: a stopping rule that reads the
training residual cannot see a module that will extrapolate on test
inputs it never met. The defect is the module's, an unbounded basis
function, and the fix RGRE-ML-2 named, a bound on its output, is not
run here.

**Where the rule is right.** On abalone, California and concrete the
statistic never falls below twice its null in eight steps, the rule
never stops, and the held-out curve keeps falling to step five or
beyond on all 15 cases; the constant had stopped ten of them at step
zero and two more at step four. On diabetes the rule stops at step
zero on four of five splits, where the hindsight best is step zero to
three and the gains are under three percent; never stopping costs
0.03 there. On red wine it stops between steps two and six with mean
regret 0.004, against 0.009 for the constant.

**Where it is wrong.** Auto mpg: the rule stops at step four or five
on every split, the held-out best is step seven or eight on four of
five, and it loses to the constant 0 to 3. The statistic there falls
to its null by step five while the fitted picks were still worth one
to two percent held-out each; a single direction's explained share
underestimates what a four-parameter bump will find, which is the
linearisation gap of the companion document, on auto mpg the largest
of the six datasets (0.62). The rule reads the tangent, and where the
tangent is not the repair it stops before the repair is exhausted.

**The budget does not matter.** M = 9, 19 and 49 choose the same step
on 29 of 30 cases. On shuffled targets the rule declines at step zero
on 30 of 30 for every M; on real targets it declines at step zero on
4 of 30, all diabetes. There is no constant to transfer and nothing to
tune.

**Against never stopping, the pass is narrow and honest about it.**
The two rules coincide on the three datasets with structure and on
the blow-up; they differ only on diabetes, auto mpg and red wine,
where the null rule saves 0.03 on diabetes and loses 0.012 on auto
mpg. The mean difference is 0.0009. On these six datasets "grow eight
steps" is nearly as good a rule as any, and the null rule's real
content is that it knows when not to start (diabetes) and when not to
stop (abalone, California), which the constant got wrong in both
directions.

## What RGRE-ML-3 establishes

1. The one percent constant can be replaced by a permutation test on
   the procedure's own statistic, with no number to carry between
   settings, and the replacement is better where the constant was
   wrong: it grows where there is structure to find and declines where
   there is not, on shuffled targets every time.
2. It does not beat the constant by the frozen mean-regret bar, because
   a rule that reads training residual cannot foresee extrapolation on
   test inputs. That is a dictionary defect and stays on record as
   one.
3. It stops early where the tangent under-reads the repair, which is
   the same limitation RGRE-ML-2 found in selection and the companion
   document measures.

No rescue, no second run on the scored splits. Nothing above is edited
after the run.
