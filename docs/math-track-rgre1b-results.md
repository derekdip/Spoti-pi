# RGRE-1b results: the simplified selector replicates

Preregistration: `docs/math-track-rgre1b-prereg.md` (frozen at commit
`4b659fb`, unchanged). Raw outputs: `poc/results/rgre1b.md`,
`rgre1b.json`, `rgre1b.png`, `rgre1b.log`. One run, 30 cases, nine
minutes. No calibration stage: RGRE-1's threshold was carried over
verbatim.

## Verdict by the frozen bars: replicated

| bar | target | result |
|---|---|---|
| B1 oracle value captured | median >= 0.90 | 1.000, mean 0.982 over 24 known cases |
| B2 search reduction | median <= 1/3 | 0.167 |
| B3 abstention | unknown >= 80%, known false <= 10% | 5 of 5 and 0 of 24 |
| B4 mixtures | median two-step >= 0.75 | 0.931 over 8 mixtures |

All four hold, so by the frozen outcome the simplified selector is the
version that goes to fire.

## The post-hoc observation held

RGRE-1's coherence-weighted rule was run on the same fresh cases for
comparison. It differs on six of the 24, and on every one of those it is
the worse choice.

| case | projection rule | coherence rule |
|---|---|---|
| corn tail 0 | unary, 0.58 | smooth, 0.01 |
| corn tail 1 | tail, 1.00 | smooth, 0.01 |
| water interaction+coordinate 0 | coordinate, 1.00 | interaction, 0.02 |
| water interaction+coordinate 1 | coordinate, 1.00 | interaction, 0.00 |
| corn unary+stop 0 | unary, 1.00 | stop, 0.01 |
| corn unary+stop 1 | unary, 1.00 | stop, 0.01 |

Those are exactly the two regimes the preregistration targeted, and the
flips run in the direction RGRE-1's diagnosis predicted: a lone template
class was winning on a discounted score while raw ownership already
named the right tangent class. Across all known cases the projection
rule wins six and loses none, the same pattern RGRE-1 measured, with
means 0.982 against 0.752. Identity rose with it: 0.96 against the
injected class and 0.96 against the oracle's class, where RGRE-1 scored
0.86 and 0.69.

## What is still imperfect

**One case below the bar.** `corn_tail_0`, a walk whose kernel
persistence was cut to 0.36, is diagnosed as unary where the oracle
prefers the decay repair; the width repair it tries removes 0.104 of the
0.181 available, so it captures 0.58. This is the corn tail and unary
tangents overlapping, the same pair W4 met in water. Under the
coherence rule the same case scored 0.01, so the simplification improves
it without solving it. Identifying which of two aligned directions owns
a residual remains the open problem, and it is the one thing fire should
be watched for.

**The spent-repair rule never fired.** No first repair on any mixture
fell below the one percent threshold, so the blacklist stayed empty
throughout. The rule is carried forward untested by this benchmark; its
justification is still RGRE-1's observation, not a measurement here.

**One mixture recovered poorly.** `mix_corner_stop_0` reached 0.30 of
the two-step oracle: the corner is diagnosed and repaired first, and the
stop repair afterwards recovers less than the oracle's ordering, which
starts with the events. The median is carried by the other seven.

**The vocabulary-gap case behaved as predicted.** The splash displaced
0.72 m from the token leaves 56 percent of its residual unexplained,
just under the threshold, so the procedure does not abstain; it
diagnoses unary and applies a gain, which the oracle agrees is the best
available move because it turns a misplaced token down. The vocabulary
has a time coordinate and no space coordinate, and nothing in the
residual decomposition can say so. That is the shape of gap fire is
meant to expose, and the case is on record before fire runs.

## Where this leaves the procedure

The version that goes forward is:

1. residual `r = G(F) - G(F_R)`;
2. project onto each tangent direction of the representation and onto
   each class support, one number each, no weighting;
3. if too much is left unexplained, abstain;
4. otherwise take the class of the largest single share and try only its
   repairs, keeping the best error reduction per unit cost;
5. recompute the residual and repeat, without renominating a repair that
   changed nothing.

Two frozen benchmarks, 102 known cases across two teachers, agree that
this captures the median of what an exhaustive search would find while
evaluating a sixth of it. Nothing in it is fitted.
