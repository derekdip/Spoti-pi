# What the game would decide from the cheap fire, and how often it would be wrong

Every fire experiment in this arc scored relative RMS error in consumer
space, because that is what the fitter minimises and what the frozen bars
were written against. It is not what a game reads. A game asks yes-or-no
questions of a fire: does this hand burn, is this bed alight, may the AI
walk here, and does the glow the player sees look like fire. This scores
the cheap fire at its best-known state on those questions, against the
teacher, so that the decision about what fire is *for* can be made on the
numbers a consumer actually uses.

Script: `poc/fire_decisions.py`. Output: `poc/results/fire_decisions.json`,
`fire_decisions.log`. States: the per-scene Powell floors from
`poc/results/f6_floor.json`, the best any optimiser has reached. Nothing
here was fitted; the states were fixed by the floor measurement before
this script existed, and the thresholds are the teacher's own.

## The decisions

| consumer | decision | threshold |
|---|---|---|
| heat probes | burn / no burn, per probe per frame | `T > 400 K`, the teacher's own hazard temperature |
| ignition | alight / not, per bed per frame | alight fraction `> 0.5` |
| AI hazard grid | impassable / passable, per cell per frame | occupancy `> 0.5` |
| visual glow | none; shape resemblance | relative RMS, and correlation over the second half of the run |

For each decision three rates are reported: the share of all decisions
that disagree with the teacher, the share of the teacher's positives the
cheap fire misses, and the share of the teacher's negatives the cheap fire
raises falsely. The last two matter separately: a missed burn is a hand in
the flame that the game does not punish, a false burn is a hand that is
hurt with nothing visible to blame.

## Results, per scene

| scene | floor RMS | heat wrong | missed burns | false burns | hazard wrong | missed hazards | false hazards | ignition wrong | missed alight | glow corr |
|---|---|---|---|---|---|---|---|---|---|---|
| obstacle | 0.460 | **1.4%** | 14.8% | 0.1% | **1.4%** | 15.5% | 0.7% | no beds | | 0.62 |
| windy | 0.385 | **3.6%** | 5.2% | 3.4% | **1.0%** | 4.4% | 0.8% | no beds | | 0.86 |
| twin | 0.503 | 9.8% | 20.3% | 6.7% | 11.3% | 35.3% | 7.0% | no beds | | 0.86 |
| full | 0.595 | 17.1% | 40.3% | 11.0% | 10.7% | 49.8% | 4.6% | 6.6% | 27.8% | 0.77 |
| delayed_ignition | 0.634 | 18.9% | 29.0% | 14.5% | 14.1% | 40.3% | 7.3% | 8.2% | 55.6% | 0.71 |
| ignition | 0.661 | 18.2% | 29.1% | 14.5% | 14.7% | 44.1% | 8.4% | 24.6% | 66.7% | 0.76 |
| shelf_bed | 0.719 | 15.6% | 36.1% | 9.9% | 10.3% | 46.8% | 4.5% | 0.0% (vacuous) | | 0.72 |
| **median** | 0.595 | **15.6%** | 29.0% | 9.9% | **10.7%** | 40.3% | 4.6% | 7.4% | 41.7% | 0.76 |

The teacher burns 22 percent of probe-frames and marks 14 percent of
cells hazardous, at the median, so "wrong" is measured against a base
rate a do-nothing model would get 78 and 86 percent right. `shelf_bed`'s
ignition row is vacuous: the teacher never lights that bed, so agreeing
with it costs nothing. For reference, the corn representation shipped
with coarse-field error 0.22, late-field correlation 0.98 and trail
overlap 0.95, where trail overlap is the corn analogue of hazard-grid
agreement.

## What the numbers say

**The scenes split in two, and the split follows scene complexity.** On
`obstacle` and `windy` the two decisions the game makes most often, burn
and passable, agree with the teacher 96 to 99 percent of the time. That
is at or above the corn precedent, on the same kind of decision, and it
is the first place in this arc where the cheap fire meets the standard
corn shipped at. Every scene with a fuel bed is wrong 15 to 19 percent of
the time on burn and 10 to 15 percent on passability, and those are the
scenes whose RMS floors were worst too. `twin`, two burners and no bed,
is wrong 10 to 11 percent, nearer the bed scenes than the simple ones, so
beds are not the only thing the grammar struggles with; two interacting
plumes are enough. The RMS
ordering and the decision ordering agree; what changes is the scale.
A 0.46 RMS floor on `obstacle` sounded far from usable. A 1.4 percent
decision error on the same scene does not.

**Misses outnumber false alarms three to one, everywhere.** Median missed
burns 29 percent against false burns 10 percent; missed hazards 40
percent against false hazards 5 percent; missed alight 42 percent against
false alight 1 percent. The cheap fire is systematically cooler and
smaller than the teacher. That is consistent with what the RMS residual
already said, that the anchored column spreads its heat too thin and
cannot fill the hot region's true extent, and it means the errors are not
symmetric noise. They are a bias, and a bias in the direction that
under-punishes the player.

**The ignition consumer is the worst at the decision level, not the
best.** Its 7.4 percent median disagreement looks fine and is misleading,
because beds are unlit most of the time and agreeing on "not alight" is
free. Of the frames where the teacher's bed is alight, the cheap fire
misses 28 to 67 percent. On `ignition` it misses two thirds: the bed
lights late or not at all. The finding in `docs/fire-shapes-added.md` that the bed shape made the
ignition consumer usable was about RMS; on the decision the bed actually
feeds, it is not.

**The glow is the one consumer with no decision, and it is the one
furthest from the precedent.** Late correlation runs 0.62 to 0.86 against
corn's 0.98. That is the shape of the hot region, which every RMS
analysis in the arc named as the thing an anchored column cannot express.
The number is here for completeness; it does not change under any
threshold.

## Proposed acceptance bars, for the owner to set

These are proposals grounded in the corn precedent, not frozen rules, and
the decision on which consumers fire must serve is not mine to make.
The corn trail shipped at 0.95 overlap; the equivalent here is 5 percent
disagreement. The miss and false-alarm bars are stricter than the
disagreement bar because they are measured against the positives alone,
where the game's attention is.

| consumer | proposed bar | passes now | fails now |
|---|---|---|---|
| heat: burn / no burn | wrong `<= 5%`, missed burns `<= 15%` | obstacle, windy | twin, full, delayed_ignition, ignition, shelf_bed |
| AI: passable | wrong `<= 5%`, missed hazards `<= 15%` | windy; obstacle passes on disagreement and misses the miss bar by half a point, 15.5% | the other five |
| ignition: alight | missed alight `<= 25%` | none scorable | full, delayed_ignition, ignition |
| visual: glow | late correlation `>= 0.9` | none | all seven |

Read as a decision table:

- **If fire is a hazard the player and the AI avoid, on open ground or
  around an obstacle, and beds are set dressing:** the current grammar
  is deployable at the decision level on the scenes that describe that
  use, and nothing further needs building. The bias toward misses is the
  thing to watch; a fixed offset on the burn threshold would trade misses
  for false alarms, but that offset would be tuned on these same scenes
  and is not applied here.
- **If beds must light, spread and burn out on their own clock:** the
  ignition consumer fails on every scorable scene, by a margin no
  threshold hides, and the bed shape is not enough. That is the grammar
  rebuild F3 named, advected sources that are not anchored to a cause,
  and it is the only thing in this arc that would move that row.
- **If the glow must look like the teacher's fire:** same answer, with
  less hope, because the visual consumer sits at 0.76 correlation against
  a precedent of 0.98 and no decision threshold makes that number better.

## What it looks like

`poc/fire_render.py` draws the two side by side, `poc/results/fire_compare.png`:
soot-obscured emission at full resolution, four times per scene, one
colour scale per scene set by the teacher's brightest frame.

The picture says what the glow correlation said, and more bluntly. The
teacher's plume is a tall tapering tongue with a bright core and a dark
tip that flickers, leans, and on `obstacle` splits into two thin
streams that reach the shelf. The cheap fire is a short, dim, flat-topped
block that does not reach the shelf, does not taper, does not flicker and
barely moves. On `twin` the teacher's two plumes lean into each other and
grow to three times their starting height; the cheap two stand still.
The fitter chose a stubby dim column because a taller, brighter one that
is wrong about where the tongue is costs more RMS than one that stays
inside the region the teacher always fills. That is the correct answer to
the question the fitter was asked and the wrong shape for a player to
look at.

At the decision level the same block is a fair hazard: the hot region a
hand or an AI cell tests is near the base, which the block covers. At
the visual level it is not fire. Nothing in the anchored-column grammar,
with any parameter values, produces the tongue, and that is the rebuild
the next section's last two rows point at.

## Caveats

The states were fitted to relative RMS, not to these decisions, so a
fitter that targeted the decisions directly could land elsewhere; that
was not tried because it would be tuning on the scenes being scored. The
Powell states carry the up-to-20-percent optimiser slack documented in
`docs/fire-shapes-added.md`, so a decision rate here is "no worse than"
in the same sense the RMS floors are. Two of the seven scenes have no
beds and two of the bed scenes are near-duplicates, so the medians are
over a small and uneven set; the per-scene rows are the result, the
medians are a summary.
