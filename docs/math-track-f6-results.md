# F6 results: outcome B by the frozen tree, and the tree's description of B is wrong. The dictionary check takes the fire workflow from 0.45 of the oracle's value to 1.00 at half the oracle's cost and beats the arc's selector on 14 scenes of 15; the constant-free stop never stops in fire, as predicted

Preregistration: `docs/math-track-f6-prereg.md`, frozen at commit
`e03a1d7`, unchanged. Raw output: `poc/results/f6.json`, `f6.log`,
`f6_report.md` (the frozen scorer's output, `poc/f6_score.py`). Fifteen
scenes, three selection rules, eight steps each, 2006 seconds on three
workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| G1 value | hybrid median `>= 0.90`, above projection | hybrid **1.000** (mean 0.75); projection 0.452 (mean 0.44) | pass |
| G2 terminal | hybrid median `>=` projection's, and `>= 0.95` of the oracle's | hybrid 0.289 vs projection 0.241, wins **14 of 15**; hybrid / oracle **0.902** | **fail** on the second clause |
| G3 the check transfers | `>= 80%` of scene-class pairs on the six unseen scenes on the same side of 0.25 | **86%** (44 of 51) | pass |
| S1 the stop | lower held-out regret than the one percent rule, and stops on at least half the exhausted scenes | regret 0.0126 vs 0.0088; stopped on 1 of 6 | **fail, as predicted** |

G1 holds and G2 fails, so the letter is **B**. The frozen text for B
reads "the check fixes the picks and the terminal state was already at
the vocabulary's floor, as F3 said". That is not what happened. The
terminal state moved: median reduction 0.241 under the arc's selector,
0.289 under the hybrid, 0.320 under the oracle, and the hybrid beat
the arc's selector on fourteen scenes of fifteen. G2 failed its second
clause only, the hybrid reaching 0.90 of the oracle's terminal gain
against a bar of 0.95. The tree assumed that a better first step could
not move the terminal error, and it did. This is a defect in a frozen
tree, the fourth in the fire freezes, and it is recorded as the
earlier ones were: the letter is B, the numbers say the hybrid sits
between the selector and the oracle, closer to the oracle.

## What each bar means

**The check fixes the picks (G1).** With the six large-gap classes
fitted to be ranked and the rest left to projection, the rule takes
the oracle's own repair on the median step, at six repairs per step
against the oracle's twelve. The arc's selector captured 0.45 in
median, 0.62 on the design scenes and 0.35 on the unseen ones. Where
it lost, the oracle's class was `rise` on 53 of 89 steps, the class
the linearisation-gap document showed the projection cannot see, then
`width` (18) and `wind` (12). Where the hybrid still lost, on 43 of 120
steps, the oracle's class was a small-gap class every time: `width`
(29), `profile` (9), `base` (4), `jitter` (1). The classification was
right and the projection's ranking *among* the small-gap classes was
wrong: on `split` the oracle wanted `profile` then `width` on six
consecutive steps and the projection's top small-gap pick was
`deflect`, after which the hybrid fell back to a fitted large-gap
class worth less. F1's support templates, which the fire cross-check
found put the mechanism ahead of the value, are the likely cause; the
hybrid inherited them with the selector. Ranking the small-gap classes
without templates, or fitting the top two, is the obvious next change
and is not run here.

**The terminal state moves (G2).** Fourteen wins of fifteen against the
arc's selector, by 0.01 to 0.14 of the V0 error, with `windy` the one
loss by 0.007. Against the oracle the hybrid ties on five scenes
(`twin`, `delayed_ignition`, `gusty`, `strong_gust`, `gust_twin`) and
trails by 0.04 to 0.10 on five (`split`, `shutoff`, `gust_shelf`,
`full`, `windy`), the scenes where the small-gap ranking failed above.
Held-out errors track in-sample errors to within the noise floor on
every scene; the reseeded teacher differs from the original by 0.001
to 0.013 on the forced scenes and by 0.12 to 0.28 on `obstacle`,
`shutoff` and `twin`, whose plumes are chaotic, and even there the
ranking of the three rules is the same on both teachers.

**The check transfers, with two classes that depend on the state
(G3).** On the six unseen gusted scenes, 44 of 51 classifications hold.
The seven misses are `amp` on five scenes (gap 0.03 to 0.05 against
0.48 on the design scenes), `deflect` on `gust_shelf` (0.66 against
0.13) and `width` on `gust_twin` (0.27). Along the 360 recorded path
states the median gap is 0.05 for `amp`, 0.42 for `deflect`, 0.33 for
`cool` and 0.25 for `attract`, against 0.96 for `rise`, 0.73 for
`rate`, 0.70 for `wind` and 0.08 to 0.12 for `profile`, `base` and
`width`. So the check is a property of the grammar for the classes at
either end and a property of the state for the four in the middle;
`amp` was misclassified by the step-zero table and cost nothing here
because fitting it is cheap, and `deflect` was misclassified the other
way and cost the `gust_shelf` and `split` steps above.

**The stop never stops (S1), as predicted.** The statistic sits 11 to
24 times above its shuffled maximum at every step in median, and the
null rule ran to the budget on twelve scenes of fifteen. It stopped at
step 3 on `delayed_ignition` (hindsight 5), at 7 on `full` (hindsight
8) and at step 0 on `shelf_bed`, a false stop: there the shuffled
maximum reached 0.137 against an observed 0.134, because the scene's
ignition consumer is a block of one column per frame and a tangent
correlates with almost any permutation of it. The one percent rule
stopped earlier everywhere and had lower regret; never stopping had
none, because in fire a repair that helps in-sample helps against the
reseeded teacher too. The result is the one RGRE-ML-3's auto mpg case
showed from the other side: the shuffle null detects structure, and
fire's residual is structured everywhere and reachable almost nowhere.
A stop for this domain has to read what a fit did, not what a tangent
could see, which is what the one percent rule does and what its
constant was calibrated for.

## What F6 establishes

1. The linearisation gap is usable as a dictionary check in the domain
   the procedure was built for. Fitting the classes it names and
   projecting the rest takes the fire workflow from 0.45 to 1.00 of the
   oracle's per-step value and from 0.24 to 0.29 median terminal
   reduction, at half the oracle's cost, on fifteen scenes including
   six the check never saw.
2. What it does not fix is the projection's ranking among the classes
   it leaves to projection, and the support templates are the suspect.
3. Two classes, `amp` and `deflect`, change sides along a path. The
   check should be taken at the state where it is used, or the middle
   classes fitted as well; either costs one or two repairs per step.
4. The constant-free stop is not a fire stop. In a domain where the
   vocabulary is the limit, structure in the residual says nothing
   about whether a repair can reach it.

No rescue, no second run on the scored scenes. Nothing above is edited
after the run.
