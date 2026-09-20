# F2: the same fire search with the stopping rule replaced. Preregistration (frozen before the run)

F1 is frozen and stands. It found that residual projection selects
exactly, matching the oracle on 11 of 13 steps at a tenth of the search,
while the terminal model barely improved on V0 because seven of nine
scenes stopped early. They stopped because `q_perp`, the share of
residual energy orthogonal to every class direction, crossed a threshold
carried over from RGRE-1. That quantity is pushed upward by greedy
fitting itself, so thresholding it fires after a roughly fixed number of
steps rather than when the vocabulary is spent.

F2 changes the stopping rule and nothing else. Same teacher, same
scenes, same calibrated V0, same classes, same ranges, same objective,
same selector, same oracle, same scoring.

## The change, and why it needs no new constant

**`q_perp` no longer stops anything.** It is still computed and
reported. The frozen `select_projection` is called with its threshold
set to 1.01, above the largest value the quantity can take, so the
function itself is untouched and only its argument differs.

**Abstention moves to step zero and to realised gain.** A case is out of
vocabulary when no single repair meaningfully helps it. RGRE-1b already
fixed what "meaningfully" means, at 10 percent of the case's error, and
F1 used that same number for its construct checks. F2 promotes it to the
decision rule: at step zero, fit the top-ranked class, and if it removes
10 percent or less of the V0 error, abstain and stop with no expansions.

**Termination moves to repair exhaustion.** From step one onward the
search stops only when every class has been blacklisted by the spent
rule, which is unchanged at 1 percent, or when the step budget runs out.

So F2 uses two constants and both were frozen before F1: 10 percent for
out of vocabulary, 1 percent for spent. Nothing is calibrated here.

**The step budget rises from 6 to 10.** It was never binding in F1,
where the longest run used 4 steps, so this cannot explain F1's failure
and it gives the new rule room to show what it does. Terminal reduction
is scored at termination; the reduction after 6 steps is also reported
so the comparison with F1 is exact.

## Bars (frozen)

The first four are F1's, unchanged, so the two runs compare directly.

- **F2-B1** median oracle value captured `>= 0.75`, over every step of
  every scored scene, steps with non-positive oracle gain excluded.
- **F2-B2** median repairs evaluated per step `<= 1/3` of the ten
  classes.
- **F2-B3** median terminal error reduction `>= 0.40` of the V0 error.
  This is the bar F1 failed at 0.098 and it is the point of the change.
- **F2-B4** at the terminal state, no consumer is worse than at V0, in
  at least 6 of the 7 scored scenes.
- **F2-B5** median steps used `>= 4` of the 10 allowed, across the
  scored scenes. F1's median was 2. This asks directly whether the
  search now runs instead of stopping.

## Predictions, stated in advance

These are not bars. They are written down so the fix can be wrong in a
way that is visible.

1. `windy` will select `tilt` at step zero and end with a substantial
   reduction. In F1 it abstained at step zero with `q_perp = 0.593`
   against a threshold of 0.583 and did nothing at all, on the one scene
   whose defect the vocabulary explicitly contains.
2. Median steps used will rise from 2 to at least 4.
3. `soot` and `secondary`, never chosen once in F1's twenty steps, will
   be chosen at least once now that the cheap classes can be spent.
4. B3 will pass if and only if the stopping rule really was the binding
   constraint. If B3 still fails with the search running to exhaustion,
   the vocabulary was the limit after all and F1's outcome label was
   right for the wrong reason.

## What is deliberately not changed

F1's larger finding was that error per unit cost bought an unphysical
mechanism: the flame was leaned permanently over a fuel bed rather than
the bed being given the class that models it lighting and burning out,
because leaning is cheaper and scores better. The objective is not
touched here. Changing the stopping rule and the objective at once would
make neither attributable. Whether `secondary` is now chosen is reported
under prediction 3, and whether the leaning persists is reported without
a bar.

The cost-model defect F1 reported, that re-fitting an already-enabled
parameter is charged one unit although it adds no complexity, is also
left as it is.

## Outcome (frozen)

- **A**: B1 through B5 hold. The stopping rule was the binding
  constraint, the fix is correct, and the fire representation it builds
  is worth carrying forward.
- **B**: B5 holds and B3 fails. The search now runs and the vocabulary
  is genuinely the limit; the results name which expansion is missing.
- **C**: B1 or B2 fails. Removing the threshold cost selection quality
  or search economy, which would mean `q_perp` was doing useful work
  that this rule does not replace.
- **D**: B5 fails. The search still does not run, and the diagnosis in
  F1 was wrong about the cause.

No rescue, no third run on these scenes. Results go in
`docs/math-track-f2-results.md`; nothing above is edited after the run.
