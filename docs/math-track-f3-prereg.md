# F3: is the vocabulary or the search the limit? Preregistration (frozen before the run)

F1 and F2 both stand and both failed their terminal-error bar. F1 blamed
the stopping rule, F2 replaced it and did worse, and F2 then found that
three classes were unreachable by the repair fitter, which withdraws the
most interesting reading either run offered. After two failed stopping
rules it is no longer sensible to tune a search without knowing whether
its target is reachable at all.

F3 measures the target. It takes no constant from another domain.

## Changes from F2

**The fitter is fixed.** A class whose parameters are all zero now
starts its coordinate descent from the same canonical on-state its
tangent direction already used, which was declared in F1's
preregistration and never applied to fitting. Measured effect on
`ignition` at V0: `secondary` goes from exactly 0.00 percent gain to
0.37, `flicker` from 0.00 to 0.03, `soot` stays at 0.00 because a fitted
column amplitude has already absorbed the obscuration, which is a
correct answer rather than a defect.

**No stopping rule.** Both borrowed constants failed, so F3 carries
neither. The search runs to a 12-step budget or until every class is
spent at the unchanged 1 percent accept floor, whichever comes first,
and the full error trajectory is reported. Where to stop is then a
question the trajectory answers rather than one a constant decides.

**No per-step oracle.** Scoring is against a joint fit instead, which is
both cheaper and the more informative comparison.

**A joint fit is added.** Every parameter of every class, fitted
together by the same coordinate descent, no greed and no selection. That
is the floor the vocabulary can reach on each scene and it is the number
neither earlier run ever measured.

Everything else is unchanged: teacher, scenes, calibrated V0, classes,
ranges, objective, consumers, and the projection selector.

## Bars (frozen)

- **F3-B1, the vocabulary floor.** Median relative error of the joint
  fit across the 7 scored scenes `<= 0.35`. V0 sits near 0.80, so this
  asks whether the grammar can more than halve the consumer error when
  nothing is withheld from it.
- **F3-B2, search adequacy.** Median greedy error reduction `>= 0.80`
  of the joint fit's reduction on the same scene. This asks whether
  greedy selection reaches what joint fitting reaches.
- **F3-B3, reachability.** At least one of `soot`, `flicker`,
  `secondary` is chosen at least once across all scenes. All three were
  chosen zero times in F1 and F2 while inert.
- **F3-B4, terminal reduction.** Median `>= 0.40` of the V0 error,
  which is F1-B3 and F2-B3 verbatim so the three runs compare.
- **F3-B5, consumer transfer.** At the terminal state no consumer is
  worse than at V0, in at least 6 of the 7 scored scenes, counting only
  scenes that performed at least one expansion, so a do-nothing run
  cannot pass it the way F2's did.

## Outcome (frozen)

- **A**: B1 and B2 hold. The vocabulary is adequate and greedy search
  reaches it. Whatever terminal error remains is the stopping rule's,
  and a rule with no borrowed constant is the next thing to build.
- **B**: B1 holds and B2 fails. The vocabulary can express the scenes
  and greedy selection cannot find it. The search is the limit, and the
  step where greedy and joint diverge is the finding.
- **C**: B1 fails but the joint fit still beats V0 by a wide margin.
  The vocabulary is the limit. No search repair helps and the results
  name which terms are missing.
- **D**: B1 fails and the joint fit is close to V0. The grammar is
  nearly useless for fire and needs rebuilding rather than extending.

Reported without bars: the per-step error trajectory of every scene,
which classes the joint fit switches on that greedy never reaches, the
per-consumer breakdown at the joint fit, whether the flame still leans
over the fuel bed once `secondary` is reachable, and the two
out-of-vocabulary scenes' terminal construct checks.

No rescue, no second run on these scenes. Results go in
`docs/math-track-f3-results.md`; nothing above is edited after the run.
