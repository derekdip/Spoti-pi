# Does "diagnose on the field, score on the consumers" hold in fire? No difference to find: the consumer residual diagnoses as well as the field there

RGRE-ML-1 found that diagnosing on the consumer-space residual halved
the identification rate against the raw field, and named the binary
decision consumer as the likely cause. Every fire experiment diagnosed
on the consumer residual, so if the finding were general, the fire arc
had been picking repairs on a degraded signal from F1 onward. This is
the cross-check. Not preregistered, no bar, no verdict letter: the
question is whether the picks change, and the answer is reported as it
came out. Script `poc/fire_diag_space.py`, raw output
`poc/results/fire_diag_space.{log,json}`.

## What was run

Nine fire scenes, the puff grammar's default state, step zero. The
step-0 diagnosis was run three ways and each pick compared with the
oracle, which fits every repairable class once and takes the largest
raw error reduction on the consumers:

- **consumer + templates**: the residual every fire run used, with the
  support templates F1 declared for the bed and deflection classes;
- **consumer**: the same residual, no templates, which is what
  RGRE-ML-1 ran;
- **field**: the coarse excess-temperature field, no thresholds, no
  emission, no soot. Scoring stays on the consumers, so the oracle is
  the same for all three.

Value is the pick's raw drop over the oracle's. Where a scene was built
around one mechanism (wind, an obstacle, twin attraction, a fuel bed)
the pick is also compared with that.

## Result

| scene | oracle | mechanism | consumer + templates | consumer | field | value: templates / consumer / field |
|---|---|---|---|---|---|---|
| windy | rise | wind | width | width | cool | 0.48 / 0.48 / 0.75 |
| obstacle | rise | deflect | deflect | deflect | cool | 0.90 / 0.90 / 0.86 |
| twin | rise | attract | profile | profile | attract | 0.85 / 0.85 / 0.68 |
| split | rise | deflect | width | width | cool | 0.66 / 0.66 / 0.88 |
| shutoff | cool | none | width | width | base | 0.72 / 0.72 / 0.22 |
| ignition | wind | bed | bed | wind | wind | 0.09 / 1.00 / 1.00 |
| delayed_ignition | wind | bed | bed | wind | wind | 0.07 / 1.00 / 1.00 |
| full | wind | bed | bed | deflect | wind | 0.02 / 0.67 / 1.00 |
| shelf_bed | rise | bed | bed | deflect | wind | 0.05 / 0.91 / 0.60 |

| diagnosis space | value median | value mean | pick = oracle | oracle in top 3 | pick = mechanism |
|---|---|---|---|---|---|
| consumer + templates | 0.48 | 0.43 | 0 of 9 | 4 of 9 | 5 of 8 |
| consumer | 0.85 | 0.80 | 2 of 9 | 4 of 9 | 1 of 8 |
| field | 0.86 | 0.78 | 3 of 9 | 4 of 9 | 1 of 8 |

**Consumer against field.** Medians 0.85 and 0.86, means 0.80 and
0.78, the oracle in the top three on the same four scenes, and the
exact oracle found on two scenes against three. Scene by scene the
field wins three (windy, split, full), the consumer wins four
(obstacle, twin, shutoff, shelf_bed) and two tie. That is no
difference on nine scenes. The RGRE-ML-1 effect does not appear in
fire, and the fire arc's diagnoses were not on a degraded signal.

**Why it does not appear.** Fire's consumers are the glow (smooth),
probe temperatures (smooth), bed ignition fractions (a threshold
averaged over each patch) and hazard occupancy (a threshold averaged
over 16 by 16 cells). The two thresholded consumers are fractions
after averaging, not per-sample bits, and the two smooth consumers
carry most of the residual's energy. RGRE-ML-1's decision consumer was
a single bit per sample with no averaging, and that is the consumer
the identification rate halved on. So the general statement narrows
again, in the direction the RGRE-ML-1 document already pointed: a
per-sample binary consumer degrades the residual as a diagnostic;
smooth consumers and averaged thresholds do not, and the field is not
better than them. "Diagnose on the field" is the safe default when a
consumer is a bare decision. It is not a correction to the fire arc.

**The templates, an unexpected reading.** With F1's support templates
the pick is the scene's mechanism on five of eight scenes and the
oracle on none, with a third of the value. On the four bed scenes the
templates pick the bed at step zero and that repair is worth 2 to 9
percent of the best single step, because the bed cannot light until
the plume reaches it; the oracle takes the wind or the plume first.
Without templates both residuals take the wind or the plume first and
reach full value on three of the four. The templates were declared in
F1 to make the support classes findable at all, and they do that; the
price, visible here for the first time, is that they put the mechanism
ahead of the value at step zero. Sequencing (F3, RGRE-ML-1) is what
recovers the bed afterwards. This is an observation on nine scenes,
not a finding, and it is not acted on.

**What the oracle says about step zero in fire.** The best single
repair is the plume's rise on six of nine scenes and the wind on
three, never the mechanism the scene was built around. Every
diagnosis space agrees the first step is the plume; the disagreement
is over which plume parameter. That is F3's finding restated: the
search is not the limit at step zero, the vocabulary is.

## What this closes

RGRE-ML-1's second establishment, "diagnose on the field residual,
score on the consumers", is now: diagnose on the field where a
consumer is a per-sample decision; elsewhere the consumer residual is
as good, and scoring stays on the consumers in every case. The fire
arc stands as diagnosed. Nothing in the fire documents needs
re-reading.
