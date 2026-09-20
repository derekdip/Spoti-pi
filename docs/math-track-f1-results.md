# F1 results: selection transfers, the stopping rule does not

Preregistration: `docs/math-track-f1-prereg.md`, frozen at commit
`3442624`, unchanged. Raw output: `poc/results/f1.json`,
`f1_run.log`, `f1_v0.json`, `f1_oov_check.json`. One run, nine scenes,
281 seconds. No recalibration: RGRE-1's threshold was used verbatim in a
third domain.

## Verdict by the frozen bars: outcome B

| bar | target | result | |
|---|---|---|---|
| B1 oracle value captured | median >= 0.75 | **1.000** over 13 steps | pass |
| B2 repairs evaluated per step | median <= 3.33 of 10 | **1.0** | pass |
| B3 terminal error reduction | median >= 0.40 | **0.098** | **fail** |
| B4 consumer transfer | >= 6 of 7 scenes | **6** | pass |
| B5 abstention, conditional | see below | scorable, and it abstained | pass |

The frozen tree calls that outcome B: selection transfers, the
vocabulary is too weak. The bars are right and the label is wrong, and
the reason is in the stop column.

## What actually stopped the search

| scene | seen | steps | stopped because | E, V0 to final | picks |
|---|---|---|---|---|---|
| obstacle | yes | 1 | threshold | 0.732 to 0.706, 3.5% | width |
| ignition | yes | 3 | threshold | 0.816 to 0.623, 23.6% | rise, width, tilt |
| delayed_ignition | no | 2 | repairs spent | 0.840 to 0.757, 9.8% | rise, width |
| full | no | 4 | threshold | 0.818 to 0.625, 23.5% | rise, width, tilt, height |
| windy | no | 0 | threshold | 0.834 to 0.834, 0.0% | none |
| twin | no | 1 | threshold | 0.725 to 0.664, 8.4% | rise |
| shelf_bed | no | 2 | repairs spent | 0.830 to 0.741, 10.8% | rise, width |

Not one scene reached the six steps it was allowed. Seven of nine
stopped because the unexplained fraction `q_perp` crossed the
carried-over threshold, and only two ran out of usable repairs. So the
binding constraint is the stopping rule, not the vocabulary, and B3
failed for a reason B3 was not measuring.

**The threshold cannot work this way, and the mechanism is structural.**
`q_perp` is the share of residual energy orthogonal to the span of every
class direction. Greedy fitting removes in-span energy by construction,
so `q_perp` is pushed upward by the procedure's own success. Thresholding
it is therefore a rule that fires after a roughly fixed number of steps
rather than when the vocabulary runs out. It is not monotone, because a
good repair also removes some out-of-span energy, and two scenes show it
falling, but on net it crossed within four steps everywhere.

That also explains why RGRE-1 and RGRE-1b never saw this. Both were one
and two step problems on near-complete models, where `q_perp` had no room
to climb. The threshold transferred as a number and not as a meaning.

**The sharpest single case is `windy`.** It is the one scene whose defect
the vocabulary explicitly contains, a steady crosswind against a `tilt`
class built for exactly that. The procedure abstained at step zero with
`q_perp = 0.593` against a threshold of 0.583, did nothing at all, and
left the hazard grid at 1.111, worse than predicting an empty field. A
miss of one part in sixty cost the entire scene.

## What did pass, and it is not nothing

**Selection is exact.** Over 13 scored steps the selector matched the
oracle's choice on 11 and captured the full available value per unit
cost. It evaluated one repair per step where the oracle evaluated ten.
The two disagreements were the first step on `obstacle`, taking `width`
where the oracle wanted `height` and capturing 0.232, and the fourth
step on `full`, capturing 0.967. The distractor was never taken:
`floor`, a uniform excess temperature that is a physically wrong model of
a flame, was picked zero times in twenty steps.

**The conditional abstention bar resolved, and in favour.** At its
terminal state the split-plume scene's best single class removed 9.1
percent, inside the 10 percent rule, so the scene is properly out of
vocabulary there even though it was not at V0. The procedure abstained
on it. That is the RGRE-1b abstention behaviour reproducing in a third
domain, and it is the one place the threshold did the job it was built
for. The detached-puff scene stayed at 12.8 percent and remains
unscored, as declared.

## The finding that matters more than the bars

**Greedy error-per-cost picked an unphysical mechanism over the right
one, and the oracle agreed.** Three scenes carry a fuel bed that lights
and burns out. The vocabulary has a `secondary` class for exactly that:
a second source at the bed, with a delay that grows with distance from
the flame, which is W4's onset-time coordinate transferred to fire.
`secondary` was never chosen, by the selector or by the oracle, in
twenty steps. Instead the ignition consumer improved from 1.000 to 0.441
on one scene and 0.496 on another by way of `tilt`, which leans the
column over until it permanently overlaps the bed. The bed then reads as
alight for the whole scene and never burns out. It is cheaper than
adding a class and it scores better, and nothing in the objective can
tell that it is wrong.

The pick histogram over all twenty steps is `width` six, `rise` five,
`tilt` two, `deflect` one, `height` one. Never chosen: `soot`,
`flicker`, `secondary`, `amp`, `floor`. Soot is absent from V0 entirely
and the visual consumer multiplies by `exp(-0.5 s)`, so its omission is
a real defect the residual never cashed in.

**The rule RGRE-1b retired would have chosen better here.** RGRE-1's
coherence-weighted score differs on 14 of 20 steps, and on 13 of those
it names `secondary`, the class that actually models the mechanism. It
would have scored worse on the frozen metric, because the metric prefers
leaning the flame. RGRE-1b was right that projection captures more
measured value and this run does not overturn it. What this run adds is
that the measured value and the physics came apart, and the rule that
tracked the physics is the one that was retired for tracking less value.

**One cost-model defect, reported not fixed.** Re-fitting a parameter
that is already on is charged one unit of cost even though it adds no
complexity, because the cost delta is floored at one. That biases the
ranking toward re-fitting `width` over switching on `soot`, which costs
two. It is frozen and stays as it is.

## Consumer conflict

B4 asked whether the terminal model is worse for any consumer than V0
was. Six of seven scenes: no. The exception is `obstacle`, the shortest
run, where the single `width` repair improved the hazard grid from 0.838
to 0.727 while making the visual worse, 0.912 to 0.937, and the heat
probes worse, 0.269 to 0.297. One repair, three consumers, two of them
paying for the third. The objective is their mean, so the trade was
correct by the rules and is still the thing to watch.

## Where this leaves the procedure

Frozen rules, so no rescue and no second run on these scenes. What the
run establishes:

1. Residual projection and the per-direction selection rule transfer to
   a third domain with no recalibration, at full value and a tenth of
   the search.
2. The abstention threshold does not transfer to a multi-step search,
   and cannot, because it thresholds a quantity that greedy fitting
   drives upward. A stopping rule for this setting has to look at
   something else: the oracle's own remaining gain, or `q_perp` relative
   to its own trajectory rather than to a fixed constant.
3. Error per unit cost is not a safe objective on its own. It bought a
   flame permanently leaning on a fuel bed rather than a bed that
   lights and burns out, and no consumer in the set could object.

The fire representation this produced is not worth carrying forward.
The three points above are.
