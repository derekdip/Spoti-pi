# The linearisation gap: when a tangent can stand in for a repair, measured in two domains

Post-hoc, unregistered, no bar. Recorded in the RGRE-ML-3 run
(`poc/rgre_ml/ml3_run.py`, 240 growth steps on six real datasets) and
by `poc/fire_lin_gap.py` on the nine fire scenes at step zero. Raw
output `poc/results/rgre_ml3.json`, `poc/results/fire_lin_gap.{json,log}`.

## The quantity

RGRE ranks candidate repairs by projecting the residual onto each
candidate's tangent directions before any repair is fitted. That is
only a proxy for what the repair will do. For a candidate `c`, let
`f*` be the change the fitted repair actually makes and `T_c` the
tangent span the ranking used. The linearisation gap is

    gap_c = 1 - cos^2(f*, span T_c),

the fraction of the fitted change that the tangent could not have
pointed at. It is zero by construction for a module with one linear
parameter. It is what RGRE-ML-1's preregistration meant by "a
candidate must have a direction before it is fitted", as a number.

## Real data: the projection captures value where the gap is small, and only there

Over 240 steps, binned by the gap of the module the oracle would have
chosen:

| oracle's gap | steps | value captured, median | pick = oracle |
|---|---|---|---|
| under 0.10 | 19 | 1.00 | 89% |
| 0.10 to 0.25 | 45 | 0.51 | 13% |
| 0.25 to 0.50 | 70 | 0.41 | 3% |
| 0.50 to 0.75 | 56 | 0.44 | 5% |
| over 0.75 | 50 | 0.42 | 2% |

Spearman correlation between the oracle's gap and the value captured,
minus 0.31 over 240 steps. The module the projection picks has a gap
of 0.00 in median and under 0.10 on 72 percent of steps: the rule
picks what it can see. By module kind the median gap is 0.00 for the
square, cube, product and exponential, 0.01 for the step, 0.02 for the
absolute value, 0.09 for the sinusoid and 0.30 for the two-dimensional
bump, and the bump was the oracle's choice on 201 of 240 steps. By
dataset the oracle's median gap runs from 0.15 (concrete, where the
projection captured 0.73) to 0.62 and 0.70 (auto mpg and red wine,
0.51 and 0.41).

The anchored-tangent variant of RGRE-ML-2 brings the gap of the
oracle's module down to 0.05 in median, and its value was 0.60: a span
that contains the fit is not enough, because the rule reads one
direction at a time and among many directions noise finds one to
correlate with. The gap says whether the tangent could have found the
repair; it does not by itself say that the rule will.

## Fire: the same, and it re-reads step zero of the whole arc

At step zero on nine scenes, for every repairable class: the
projection's reading `q_c` (the share of residual energy the class's
tangents explain), the fitted repair's drop as a fraction of the
error, and the gap.

| class | median gap | note |
|---|---|---|
| base, profile, attract | 0.00 | |
| width, deflect | 0.09, 0.13 | the classes the projection picked on seven of nine scenes |
| amp, cool, shutoff's cool | 0.48 | |
| wind | 0.73 | picked, and the oracle, on the two ignition scenes |
| bed | 0.92 | |
| rise | 0.98 | the oracle on five of nine scenes; `q` 0.003 to 0.012 on all nine |

Among the 69 repairs worth more than half a percent of the error, the
projection's reading predicts the fitted drop with Spearman 0.92
where the gap is under 0.2 and 0.18 where it is over 0.5. Repairs with
a small gap have median reading 0.079 and median drop 0.030; repairs
with a large gap have reading 0.012 and drop 0.105. The largest
repairs in fire are the ones the tangent cannot see.

The `rise` class, plume velocity and acceleration, is the oracle's
first step on windy, obstacle, twin, split and shelf_bed with drops of
13 to 55 percent of the error, and its tangent at the initial state
explains one percent of the residual or less on every scene, because
changing the rise translates the whole plume and a translation's
derivative decorrelates from the translation as soon as it is larger
than the plume's width. The projection picked width, deflect or
profile instead, classes with gaps under 0.15, and captured 0.35 to
0.90 of the oracle's step. F3's finding that greedy selection reached
96 percent of the joint fit stands as measured; what this adds is that
at step zero the projection was choosing among the classes it could
read, and the class with the most value was not one of them on five
scenes of nine. The fire arc's "the plume first" was the oracle's
verdict, never the projection's.

## What the gap is for

A dictionary check before a run. Fit each candidate once on a
reference residual, compute its gap, and the table above says what to
expect: classes under 0.1 will be ranked at full value by projection
and need no search; classes over 0.25 must be fitted to be ranked, and
if the repair is cheap the oracle is the method for them. In fire
that would have said, before F1, that width, deflect, profile, base
and attract were projection's to rank and rise, bed and wind were
not; on the real datasets it would have said that everything but the
bump and the sinusoid was fine and those two were most of the value.
Neither run had that table. The next one can.
