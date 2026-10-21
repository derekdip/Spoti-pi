# F1: RGRE end to end on fire. Preregistration (frozen before any scored scene is run)

RGRE-1 and RGRE-1b ran on corn and water, where the cheap vocabulary was
built alongside the teacher and each case carried one injected defect
whose owner was known. Fire is the first domain where neither is true.
The starting representation is deliberately underpowered, it is wrong in
many ways at once on every scene, and nothing about it was chosen by
hand. The question is whether the same procedure, with the same frozen
threshold, still finds what is missing.

## What is frozen from before

Diagnosis is `poc/rgre/core.py::diagnose`, unchanged. Selection is
`poc/rgre/core.py::select_projection`, unchanged, the rule RGRE-1b
confirmed. The abstention threshold is `tau = 0.5834212065969504`,
RGRE-1's calibrated value, carried over verbatim into a third domain
with no recalibration stage. The spent-repair rule is unchanged: a
repair that reduced the error by less than one percent of its starting
value cannot be chosen again.

## The cheap representation

`poc/fire/tokens.py`. V0 is a buoyant column per burner: Gaussian
across, exponential decay with height, width growing linearly. Four
parameters. No flicker, no wind, no soot, no obstacle, no rise time, and
a fuel patch does nothing. The consumers are the teacher's own
(`poc/fire/teacher.py`), not the representation's: coarse glow with soot
obscuration, temperature at 24 probe points, per-patch ignition, and a
coarse hazard grid.

The residual lives in the consumers' joint space. Each consumer block is
divided by its own target scale and by the square root of its own width,
so the four contribute equally and the norm the selector sees is exactly
the objective being minimised.

Ten classes, whose structure was written from physical reasoning before
any residual was computed: `amp`, `height`, `width`, `soot`, `flicker`,
`tilt`, `rise`, `deflect`, `secondary`, `floor`. Two are support-type
(`deflect` owns the obstacle neighbourhood, `secondary` owns the fuel
beds and the ignition consumer). Parameter ranges and the canonical
on-state used for an off class's tangent are declared in
`poc/fire/rgre_fire.py` and are mid-range guesses, not fits.

`floor`, a uniform excess temperature, is a legal parameter and a
physically wrong model of a flame. It is kept as a repairable distractor
rather than an abstention trigger, so that the question "does the
procedure waste a step on it" can be answered. Nothing in this
vocabulary is unrepairable.

## Calibration, and what was seen

**Calibration scene: `plume`, and only that.** V0's four parameters were
fitted there by the same automatic coordinate descent every repair uses.
Result, frozen: `amp = 605.56`, `height = 1.20`, `width = 0.07`,
`spread = 0.0`, error 0.679 down from 1.234. Worth noting before the
run: the fit chose an excess of 606 K where the teacher's column reaches
907 K, because the consumers see soot-obscured glow rather than
temperature.

**Declared pilot on seen cases.** The step-one rankings at V0 on
`obstacle` and `ignition` were inspected. That inspection is what
prompted making `floor` a distractor instead of an abstention trigger,
because it topped the ranking on `obstacle`. Those two scenes are
therefore seen, and are flagged as such in the results. The other five
scored scenes were never run before this freeze.

**Out-of-vocabulary construct check, and why one bar is conditional.**
RGRE-1b required that no single repair remove more than 10 percent of an
unknown case's error. Two candidates were built and both fail that rule
at V0: a burner that shuts off and leaves a detached puff (12.8 percent,
via `rise`) and a wide shelf directly over the burner that splits the
plume in two (33.2 percent, via `height`). The reason is structural and
is a finding in itself: when the starting model is deliberately
underpowered, generic parameters mop up so much error that nothing looks
out of vocabulary. The rule only bites near a good model. So the
abstention bar below is conditional on re-running that check at the
terminal state, and the condition is declared here rather than decided
afterwards.

## Scenes

| role | scenes |
|---|---|
| calibration | `plume` |
| scored, seen during the pilot | `obstacle`, `ignition` |
| scored, unseen | `delayed_ignition`, `full`, `windy`, `twin`, `shelf_bed` |
| out of vocabulary, reported | `split`, `shutoff` |

## Procedure

Six expansion steps per scene. At each step: compute the tangent
directions and support templates at the current state, diagnose, and if
`q_perp > tau` abstain and stop. Otherwise the frozen selector names one
class; fit its parameters; keep the result if it reduces the error,
otherwise blacklist that class and re-select. In parallel and only for
scoring, an oracle fits every class and takes the best error reduction
per unit added cost. Cost is one per parameter left non-zero.

## Bars (frozen)

- **F1-B1** median oracle value captured `>= 0.75`, over every step of
  every scored scene, where value is the ratio of RGRE's error reduction
  per unit cost to the oracle's. Steps where the oracle's own gain is
  not positive are excluded. The bar is below RGRE-1b's 0.90 because
  this is a six-step end-to-end search with no injected defect, and that
  is declared here, not after the fact.
- **F1-B2** median repairs evaluated per step `<= 1/3` of the ten
  classes.
- **F1-B3** median terminal error reduction over the scored scenes
  `>= 0.40` of the V0 error.
- **F1-B4** at the terminal state, no consumer is worse than it was at
  V0, in at least 6 of the 7 scored scenes.
- **F1-B5, conditional.** Re-run the single-class construct check on
  `split` at that scene's terminal state. If no class then removes more
  than 10 percent, the scene is properly out of vocabulary and the
  procedure must abstain on it. If some class still does, B5 is
  unscorable and is reported as such with the number.

## Reported without bars

The class chosen at each step of each scene; how often `floor` is
chosen and whether the oracle agrees; the `q_perp` trajectory; the
per-consumer error trajectory, including any consumer a repair helps at
another's expense; and what RGRE-1's coherence-weighted rule would have
chosen on the same diagnoses.

## Outcome (frozen)

- **A**: B1 through B4 hold. The procedure transfers to a third domain
  with no recalibration, and the fire representation it built is the one
  to carry forward.
- **B**: B1 and B2 hold, B3 or B4 fails. Selection transfers but the
  vocabulary is too weak; the results name which expansion is missing.
- **C**: B1 fails. The procedure does not transfer end to end, and the
  step where it first diverges from the oracle is the finding.
- **D**: the procedure abstains at step one on most scored scenes. The
  threshold does not transfer out of its calibration domain; report and
  stop rather than recalibrate.

No further hypotheses, no rescue, no second run on these scenes.
Results go in `docs/math-track-f1-results.md`; nothing above is edited
after the run.
