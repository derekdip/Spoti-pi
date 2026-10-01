# F2 results: the replacement rule is worse, and the run exposed a defect that undercuts both

Preregistration: `docs/math-track-f2-prereg.md`, frozen at commit
`14fbe1e`, unchanged. Raw output: `poc/results/f2.json`, `f2_run.log`.
One run, nine scenes, 268 seconds.

## Verdict by the frozen bars

| bar | target | F2 | F1 | |
|---|---|---|---|---|
| B1 value captured | median >= 0.75 | **0.636** | 1.000 | **fail** |
| B2 repairs per step | median <= 3.33 | 1.0 | 1.0 | pass |
| B3 terminal reduction | median >= 0.40 | **0.000** | 0.098 | **fail** |
| B4 consumer transfer | >= 6 of 7 | 7 | 6 | pass, but see below |
| B5 steps used | median >= 4 | **0.0** | 2 | **fail** |

**The frozen outcome tree does not resolve.** C fires because B1
failed; D fires because B5 failed. They were written as if exclusive and
they are not. That is a defect in the tree, named rather than resolved
in whichever direction flatters the run. Both readings are reported
below and both are partly right.

B4's pass is vacuous. Six of seven scored scenes performed zero
expansions, so their consumers are unchanged by definition. A bar that
a do-nothing run passes is not measuring anything, and it passed 7 of 7
precisely because the run did nothing.

## The replacement rule discriminates backwards

The new rule abstains at step zero when the top-ranked class's fitted
repair removes 10 percent or less of the V0 error.

| scene | in vocabulary | step-zero decision | correct? |
|---|---|---|---|
| obstacle | yes | abstained | no |
| ignition | yes | abstained | no |
| delayed_ignition | yes | abstained | no |
| full | yes | abstained | no |
| windy | yes | proceeded | yes |
| twin | yes | abstained | no |
| shelf_bed | yes | abstained | no |
| split | no | proceeded, 5 steps | no |
| shutoff | no | proceeded, 2 steps | no |

Eight of nine decisions wrong, and wrong in both directions at once: it
blocked six of seven scenes it should have run and ran both scenes it
should have blocked. That is worse than the threshold it replaced and
worse than deciding at random.

The cause is the same one F1 identified for `q_perp`, in a second
disguise. Ten percent is RGRE-1b's constant for whether *any* class can
explain a *whole case* with one piece missing. Applied to the *first
step* of a model missing many pieces, the error is spread thin enough
that no single repair clears it, while an out-of-vocabulary scene whose
V0 column is simply the wrong shape clears it easily on a generic
parameter. Both borrowed constants fail for the same structural reason:
they were calibrated where one thing was absent and reused where many
are.

## What the run got right

**Prediction 1 was confirmed, and emphatically.** `windy` selected
`tilt` at step zero, exactly as written down in advance, then ran eight
steps to a 40.7 percent reduction, the largest anywhere in F1 or F2. Its
hazard grid went from 1.111, worse than predicting an empty field, to
0.422. In F1 that scene abstained at step zero by one part in sixty and
achieved nothing. On the one scene where the new rule let the search
run, the search worked.

**Selection decays with depth, which F1 could never see.** Median value
captured by step index: 1.00, 0.98, 0.81, 0.69, 0.73, 0.51, 0.36, 0.18.
F1 always stopped by step four, so its perfect B1 was measured only over
the shallow steps where selection is easy. Depth is not free.

**The distractor is taken once the search runs long.** `floor`, a
uniform excess temperature that is a physically wrong model of a flame,
was never picked in F1's twenty steps. In F2 it was picked twice, at
`windy` step seven and `split` step three, both deep. A long greedy
search degenerates toward whatever cheaply reduces error.

**Both out-of-vocabulary scenes now end properly out of vocabulary.**
Terminal construct checks fell to 1.5 percent for `split` and 1.6
percent for `shutoff`, from 9.1 and 12.8 in F1. Expansion does drive a
case toward genuinely unexplainable residual. Nothing in either rule
detected it at the time.

## The defect, which undercuts a headline claim in both runs

Predictions 3 said `soot` and `secondary` would be chosen once the
cheap classes were spent. They were not, in either run, at any depth.
Investigating that produced the finding that matters most here.

**Three classes were unreachable by the fitter.** `soot`, `flicker` and
`secondary` are each gated by more than one parameter at once: a soot
amplitude does nothing without a soot height, a flicker amplitude
nothing without a frequency, a secondary source nothing without a burn
duration. `fit_class` runs coordinate descent from the current state,
where every one of those parameters is zero, so the first parameter it
sweeps changes nothing or makes things worse, it correctly selects zero,
and every later parameter is then gated off. Measured on `ignition` at
V0: sweeping `sec_amp` alone gives 0.8163, 0.8181, 0.8283, 0.8338, so
zero wins and the class is inert. From the class's declared on-state it
gives 0.8115, a real improvement. The gain of `secondary` was recorded
as exactly 0.00 percent, never approximately, on every scene and at
every depth, which is the signature of a term that is switched off
rather than one that is weak.

The same blind spot was anticipated and fixed for the *tangent*
directions before F1 was frozen, which is why an `ON` dictionary of
canonical on-states exists in the code and is declared in F1's
preregistration. It was never applied to *fitting*. So the diagnosis
could see these classes and the repair could not reach them.

**What this invalidates.** F1's results say `secondary` "was never
chosen, by the selector or by the oracle, in twenty steps", and reads
that as greedy error-per-cost preferring an unphysical mechanism. The
first half is accurate as a fact about choices. The reading is not
supported: `secondary` was the *top-ranked* class at step zero on four
of seven scored scenes, and was rejected only because fitting it was
structurally incapable of producing a gain. The residual geometry named
the right class and the repair machinery could not act on it. That is a
better and less flattering explanation than the one F1 offered, and it
is corrected here rather than by editing F1, which stays as it was
written. An amendment is appended to F1's results pointing here.

What survives from F1 unaffected: the `q_perp` stopping analysis, the
value-captured and search-economy results, the consumer conflict on
`obstacle`, and the observation that the flame leaning over the bed is
what produced the ignition improvement. What no longer stands is the
claim that the objective chose leaning *over* the secondary class. It
chose leaning over nothing, because the alternative was inert.

## Where this leaves it

Two stopping rules tried, both borrowed constants, both failed for the
same reason. The rule that would not have this problem takes no constant
from another domain at all: compare a step's gain to the previous step's
and stop when the sequence flattens.

But that is not the next thing to do. The next thing is to make the
three gated classes reachable and rerun, because until then no statement
about whether the vocabulary is adequate means anything. That is F3.
