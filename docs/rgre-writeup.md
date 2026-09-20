# Residual-guided representation expansion: the procedure, the evidence, and the failures

This consolidates seven frozen experiments and one unfrozen arc into one
account of what RGRE is, what it has been shown to do, and where it has
failed. Each claim below points to the document that measured it; nothing
here is new data. The results documents are the record and are unchanged.

## 1. The problem it addresses

The runtime this repository is about replaces an expensive, stateful
simulation with a cheap, stateless representation: a small vocabulary of
closed-form tokens, anchored to causes, evaluated on demand. That
representation is never right the first time. The question RGRE answers
is: given a teacher, a cheap representation, and a set of consumers that
read it, which part of the representation should be changed next, and
can the answer be read off the error rather than searched for.

A consumer is a function `G` from a field to what a game uses: a coarse
grid an AI queries, a set of probes, a threshold decision. The residual
is `r = G(F) - G(F_R)`, teacher minus representation, in consumer space.
The claim under test throughout is that the geometry of `r` names the
repair.

## 2. The procedure, as it stands after RGRE-1b

`poc/rgre/core.py`. Nothing in it is fitted to the domains it was run on
except one threshold, discussed under failures.

1. **Residual.** `r = G(F) - G(F_R)`, for every consumer, stacked.
2. **Tangents.** For each parameter of the representation, the finite
   difference of `G(F_R)` in that parameter; for a parameter that is
   currently off, the secant from its declared on-state, so a switched-off
   class is visible to the diagnosis. Classes group parameters; a class
   may also carry templates (fixed shapes that are not derivatives) and a
   support (where in consumer space it can act).
3. **Diagnosis** (`diagnose`). Project `r` onto each tangent direction and
   each template, one number each: the fraction of the residual's energy
   that direction alone explains. Also record `q_perp`, the fraction
   orthogonal to the span of every direction of every class.
4. **Selection** (`select_projection`). Rank individual directions by
   their own fraction and take the class of the top one. No coherence
   weighting, no class-level aggregation. Abstain if `q_perp` exceeds
   `tau = 0.5834`. Skip a class whose every repair has been spent.
5. **Repair.** Fit only the selected class's parameters, from the class's
   on-state if it is off (`fit_class`). Keep the best error reduction per
   unit cost. A repair that reduces error by under one percent is
   blacklisted and cannot be nominated again.
6. **Repeat** from the moved residual.

The design decisions that were tested and lost are not in that list: a
coherence multiplier on the class score, class-level aggregation of
ownership, abstention on partially explained known cases, and a
fixed-percentage stopping rule.

## 3. The evidence

Seven frozen experiments, three domains, two teachers of the corn and
water kind and one fluid teacher for fire. All results are by the frozen
rules; the label each tree returned is given as returned.

| experiment | domain | cases | value captured (median) | search fraction | other bars | outcome |
|---|---|---|---|---|---|---|
| RGRE-1 | corn, water | 78 | 1.00 (mean 0.82) | 0.17 | mixtures 0.88; abstain 5/6 unknown, 4/72 known | A; H3, H6, H7 fail |
| RGRE-1b | corn, water | 30 fresh | 1.00 (mean 0.98) | 0.17 | mixtures 0.93; abstain 5/5 and 0/24 | replicated, 4/4 |
| F1 | fire | 9 scenes, 13 steps | 1.00 | 0.10 | terminal reduction 0.10 vs 0.40 bar; consumers 6/7 | B |
| F2 | fire, new stop rule | 9 scenes | 0.64 | 0.10 | stop decisions 1/9 correct | C and D both fire |
| F3 | fire, no stop rule | 9 scenes | greedy 0.96 of joint | 1 repair/step | floor 0.63 vs 0.35 bar; consumers 7/7 | C |
| post-F3 | fire, unfrozen | 9 scenes | | | floor 0.63 to 0.58 across shapes, profile, Powell | vocabulary is the limit |
| decisions | fire, unfrozen | 7 scenes | | | burn/passable wrong 1 to 4% on the two simplest scenes, 10 to 19% on the rest | owner's call |
| F4 | fire, parcel grammar | 7 unseen | greedy 0.83 of a global floor | 1 repair/step | floor below column 5/7; glow corr 0.64 median; parcels up to 32 | D |

Documents: `docs/math-track-rgre1-results.md`, `rgre1b-results.md`,
`f1-results.md`, `f2-results.md`, `f3-results.md`, `fire-shapes-added.md`,
`fire-decisions.md`.

### What transfers, with no recalibration

**Selection.** On two benchmarks totalling 108 cases in corn and water
and 13 greedy steps in fire, the class named by the largest single projection is the class
whose repair an exhaustive search would have bought, in the median case,
while evaluating a sixth to a tenth of the repair space. Fire is the
strongest evidence because it is the cleanest: with every stopping rule
removed and every parameter of every class free, greedy selection by
projection reaches 96 percent of a full joint fit while evaluating one
repair per step, and beats the joint fit outright on three of seven
scenes (F3). Selection is not the bottleneck in any domain tried.

**Sequencing.** After a correct first repair the first class's ownership
collapses and the second's rises, and the second repair is found. Median
two-step recovery 0.88 and 0.93 on two benchmarks.

**Consumer safety.** A repair chosen on the mean over consumers made no
consumer worse on 7 of 7 fire scenes in F3 and 6 of 7 in F1. The one
exception, `obstacle` in F1, is on record: one repair improved the hazard
grid and worsened the glow and the probes.

**Abstention on genuinely foreign residual.** Ten of eleven
out-of-vocabulary cases in corn and water abstained. The eleventh was a
case the vocabulary could partly absorb with a gain, and the oracle agreed
that was the best available move.

**Simplicity.** The rule that survives has no weighting and one constant.
Every refinement tried on top of it lost value on the cases where they
disagreed: RGRE-1's coherence rule lost 12 and won 0 against plain
projection; RGRE-1b measured the same, 6 and 0.

## 4. The failures, in full

These are the content. Each is a thing the procedure got wrong or a thing
I got wrong running it, and where it is recorded.

1. **The abstention threshold does not survive a multi-step search.**
   `tau = 0.5834` was calibrated on RGRE-1's development cases, one- and
   two-defect problems on near-complete models. In fire, `q_perp` is driven upward by the
   procedure's own success, because greedy fitting removes in-span energy
   by construction, so a fixed threshold fires after a roughly fixed
   number of steps rather than when the vocabulary is exhausted. Seven of
   nine fire scenes stopped this way inside four steps; `windy`, the one
   scene whose defect the vocabulary explicitly contained, abstained at
   step zero by one part in sixty and did nothing (F1).
2. **The replacement stopping rule was worse.** A ten-percent step-zero
   gain test, borrowed from RGRE-1b's constant for whether any class can
   explain a whole case, got eight of nine decisions wrong and wrong in
   both directions: it blocked six in-vocabulary scenes and ran both
   out-of-vocabulary ones. Same structural reason: a constant calibrated
   where one thing is missing reused where many are (F2).
3. **The measured value and the physics came apart.** The rule RGRE-1b
   retired, coherence weighting, would have named `secondary`, the class
   that models the burning bed, on 13 of the 14 fire steps where the two
   rules disagreed. It was retired for capturing less value, and it does
   capture less value; the value metric preferred leaning the flame over
   lighting the bed (F1). Per-unit-cost error is not a safe objective on
   its own.
4. **Three classes were unreachable by the fitter, and a claim was built
   on their silence.** Classes gated by more than one parameter (`soot`,
   `flicker`, `secondary`) started every parameter at zero, so coordinate
   descent selected zero for the first and gated off the rest. Their gain
   was exactly 0.00 percent, everywhere. F1's reading that the objective
   preferred an unphysical mechanism over `secondary` was therefore
   unsupported: `secondary` was top-ranked at step zero on four of seven
   scenes and was rejected because fitting it could not act, not because
   the objective preferred something else. Fixed by fitting from the
   on-state; an amendment is appended to F1 and F1 is not edited (F2).
5. **A bar was frozen above the achievable.** F1's terminal-reduction
   target of 40 percent had a ceiling of about 23 percent, measurable in
   under a minute a scene by fitting everything jointly. Two experiments
   were spent repairing a search whose target was out of reach. The
   check is cheap and is now part of the method: fit jointly, then freeze
   (F3).
6. **Three outcome-tree defects in three fire freezes.** F1's B3 as
   above; F2's C and D were written as exclusive and both fired; F3's C
   versus D boundary was written as "a wide margin" and never quantified.
   Each is named in its own results document rather than resolved in
   whichever direction flatters the run.
7. **The floor is not being measured reliably.** Single-start coordinate
   descent carries up to 16 percent slack in either direction; Powell
   from three starts is better on five of nine scenes and worse on four,
   spanning -17 to +20 percent, and is itself multi-modal by 8 percent
   across its own starts. A monotonicity guarantee I claimed for the
   Powell fit was not implemented, because the starts never included a
   previously found best state. Every floor number in the fire arc is
   "no worse than", and the conclusion that the vocabulary is the limit
   rests on the spread across independent optimisers, not on any single
   number (`fire-shapes-added.md`).
8. **A cost-model bias.** Re-fitting a parameter that is already on costs
   one unit even though it adds no complexity, which favours re-fitting
   `width` over switching on `soot`. Frozen, reported, not fixed (F1).
9. **Overlapping tangents remain unresolved.** When two directions are
   nearly aligned, corn's tail and unary, water's dispersion and time
   shift, the projection names the wrong owner and the identity score
   pays for it. Simplification raised identity from 0.69 to 0.96 without
   solving this; it is the same problem W4 met and the one fire was told
   to watch for (RGRE-1b).
10. **RGRE does not design vocabularies, and fire needed one designed.**
    The fire representation's gap was shapes, not parameters: a column
    that cannot split around a shelf, detach when its burner stops, or
    hand off to a bed with its own life cycle. No repair reaches a shape
    the grammar does not contain, and F3 showed that switching on more
    of the existing vocabulary does not help. The three shapes were
    designed by hand from F3's diagnosis and each activated only where
    its physics applies, which is what a correct implementation looks
    like; together with two fitted profile exponents they moved the
    floor from 0.63 to 0.58, where about 0.35 was asked for. At the
    decision level the same grammar is 1 to 4 percent wrong on burn and
    passability on the two simplest scenes and 10 to 19 percent wrong on
    the rest, and misses the lit bed on 28 to 67 percent of
    alight frames (`fire-decisions.md`).

11. **The grammar rebuild was better and still failed its bars.** F4
    replaced the anchored column with a stateless parcel train after a
    declared three-round pilot on two seen scenes. On seven unseen
    scenes it beat the column's best-known floor on five, by 8 to 20
    percent, and cut ignition misses from 28 to 67 percent to 6 to 11;
    the two misses were the two scenes the design predicted it would
    win, by margins inside the optimiser's own 15 percent disagreement.
    The glow bar failed, partly because it was frozen on a tone-mapped
    fit that collapses on gusted bed scenes, and the cost bar failed
    because the floor objective has no cost in it
    (`math-track-f4-results.md`).

## 5. What the whole arc says

Reduced to the claims that have survived every test:

- The residual's projection onto a representation's tangent directions
  names the next repair, at full value and a tenth of the search, in
  three domains, with no fitted weighting.
- It also says when it cannot help: the gap between greedy and joint
  fitting is the diagnostic, and in fire that gap was 4 percent, so the
  remaining 60 percent of error was the vocabulary's and nothing about
  the search would move it.
- Any constant carried from one setting to another failed: two stopping
  rules, both borrowed, both wrong for the same structural reason. The
  procedure that works has no constant that needs to transfer except
  the abstention threshold, and that one should be replaced by something
  relative to the search's own trajectory before it is used again in a
  multi-step setting.
- Relative RMS is the fitter's objective and not the consumer's
  question. The fire grammar that looked far from usable at 0.46 RMS is
  1.4 percent wrong on the decision a game would actually make from it,
  on that scene. Whether the fire is deployable is a question about which
  decisions it must serve, and that is the owner's, not the procedure's.

What RGRE is good for is choosing between repairs the representation
already contains, and saying when none of them is the answer. What it
does not do is invent the shape that is missing. In every domain here
that step was done by a person reading the residual RGRE produced, and it
was the step that mattered most.
