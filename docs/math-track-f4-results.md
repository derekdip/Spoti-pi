# F4 results: outcome D by the frozen tree, and the better grammar on five scenes of seven

Preregistration: `docs/math-track-f4-prereg.md`, frozen at commit
`bf8fd16`, unchanged. Raw output: `poc/results/f4.json`, `f4_run.log`,
`f4_report.md` (the frozen-bar scorer's output, `poc/f4_report.py`,
written before any result existed), `f4_compare.png` and the two
readable crops `f4_compare_a.png`, `f4_compare_b.png`. Run 1 crashed on
the first bed scene from a shadowed variable in the bed path, which
neither seen scene exercised (`f4_run1_crash.log`, fixed at `22bd9f7`
with a test, no change to the frozen grammar or protocol). Run 2 is the
judged run: seven scenes, 2 h 18 min, roughly 11 minutes per global fit.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| B1 glow | median correlation at the look fit `>= 0.80` | **0.644** (2 of 7 at `>= 0.90`) | **fail** |
| B2 floor against the column | below the column's best-known on `>= 6` of 7 | **5 of 7** | **fail** |
| B3 decisions | burn `<= 5%`, passable `<= 5%`, missed alight `<= 25%` | 11.5%, 7.3%, **11%** | **fail** (alight passes) |
| B4 cost | `<= 24` parcels per source everywhere | max **32** | **fail** |
| B5 search | median greedy `>= 0.80` of the floor | 0.828 | pass |

The tree is exclusive on B1 and B2 and both fail, so the letter is
**D: the puff train is not enough either.** That is the verdict and it
stands. The rest of this document is what the numbers say underneath
it, which is more than the letter.

## Per scene

| scene | V0 | puff floor (de, two-stage) | column best-known | look fit, scored linear | glow corr, standard / look | burn wrong | passable wrong | missed alight | parcels | greedy / floor |
|---|---|---|---|---|---|---|---|---|---|---|
| ignition | 0.815 | **0.481** (0.481, 0.594) | 0.580 | 0.589 | 0.73 / 0.39 | 12.3% | 9.8% | 6% | 26 | 0.50 |
| delayed_ignition | 0.845 | **0.577** (0.675, 0.577) | 0.626 | 0.585 | 0.75 / 0.61 | 16.2% | 12.6% | 11% | 32 | 0.42 |
| full | 0.840 | **0.470** (0.470, 0.529) | 0.590 | 0.483 | 0.75 / 0.76 | 9.4% | 6.9% | 11% | 7 | 0.85 |
| twin | 0.762 | **0.454** (0.454, 0.524) | 0.503 | **0.402** | 0.83 / **0.91** | 12.0% | 7.3% | | 16 | 1.14 |
| shelf_bed | 0.854 | **0.494** (0.564, 0.494) | 0.615 | 0.583 | 0.68 / 0.54 | 11.5% | 7.6% | vacuous | 30 | 0.38 |
| split | 1.190 | 0.417 (0.417, 0.488) | **0.411** | 0.413 | 0.77 / **0.91** | 0.2% | 0.9% | | 12 | 0.83 |
| shutoff | 0.777 | 0.569 (0.569, 0.588) | **0.551** | 0.599 | 0.71 / 0.64 | 3.3% | 2.6% | | 12 | 0.92 |

Column decision rates on the same scenes, for reference: burn wrong
18.2, 18.9, 17.1, 9.8, 15.6, 0.2, 3.6 percent; passable wrong 14.7,
14.1, 10.7, 11.3, 10.3, 0.9, 2.6; missed alight 67, 56, 28 percent.

## What the numbers say

**The puff grammar is the better representation on five of seven
unseen scenes, by 8 to 20 percent, and on every consumer where there
is a bed.** Median floor 0.481 against the column's 0.580. Ignition
misses fall from 67, 56 and 28 percent to 6, 11 and 11; burn and
passable disagreement fall on every bed scene; the hazard grid improves
on six of seven. This is the first fire representation in the arc that
gets a bed to light on its own clock at the decision level.

**The two misses are exactly the two scenes the design said it would
win, and both are inside the optimiser's own disagreement.** P1
predicted `split` and `shutoff` in vocabulary; they lost to the column
by 1.5 and 3 percent. On the same run the two optimisers disagreed by
15 and 12 percent on `delayed_ignition` and `shelf_bed`, and on `twin`
and `split` the look-objective run landed on a state that scores better
on the standard objective than the standard run's own answer (0.402
against 0.454, 0.413 against 0.417). A 1.5 percent margin is not a
measurement here. What is a measurement is that the column's
hand-built `split` class, made for that one scene, is hard to beat, and
that the detached parcel on `shutoff` is too small and dies too soon
(the hazard grid error is 0.66, the worst consumer on that scene).

**B1 failed for two reasons and the frozen scoring choice was one of
them.** B1 was frozen on the look-fit state. On the three gusted bed
scenes the tone-mapped objective buys a dim wide glow and the
correlation collapses: 0.39, 0.61 and 0.54 against 0.73, 0.75 and 0.68
at the standard fit. Scored at the standard fit instead, the median is
0.748, still below 0.80, so the letter does not change; but the
tone-mapped fit is not a safe way to get glow on scenes with a gust and
a bed, and it was adopted on the strength of two seen scenes without
either. Where it does work it works well: `twin` and `split` reach 0.91
at the look fit, and the `twin` picture is the first cheap fire in the
arc that looks like the teacher's, two tall tapering tongues leaning
into each other.

**The gusted scenes are fitted as the mean of a swaying flame.** The
teacher's plume on `ignition`, `delayed_ignition`, `full` and
`shelf_bed` sways with the 0.7 Hz gust and leans onto the bed; the
fitted puff fire is a static block on the burner (`f4_compare_b.png`).
The grammar has the gust drift; the motion ratios say the fit captured
0.44 to 0.80 of the teacher's motion on those scenes, so it used the
drift and still averaged. A frame-wise objective on a deterministic
sway should be able to lock phase, and this one did not; whether that
is the optimiser or the drift law is not resolved here.

**The cost bar failed because the objective has no cost in it.** All
three bed scenes fitted 26 to 32 parcels per source; the four others 7
to 16. Without a cost term the floor fit buys accuracy with parcels.
The column grammar's greedy search charged cost per unit error; its
floor did not, and neither does this one. A deployable state needs the
budget inside the objective or the grammar.

**Search adequacy fell where the floor got better.** F3's 0.96 was
greedy against a coordinate-descent floor. Against a global floor,
greedy reaches 0.38 to 0.50 on the three bed scenes and beats the floor
outright on `twin`. The ratio was always a statement about the floor's
quality as much as the search's. P2 held in part: greedy chose
`deflect` on two of three shelf scenes, `attract` on `twin`, and `bed`
on one of four bed scenes rather than the predicted two.

## What this run establishes

1. A stateless parcel train is a better cheap fire than an anchored
   column on scenes with beds, gusts, shelves and two sources, on every
   consumer, and it is the first to serve the ignition consumer.
2. It is not fire to look at on gusted bed scenes, and the tone-mapped
   objective does not fix that; it makes it worse there.
3. The floor is still not measured reliably. Two global-ish optimisers
   disagree by up to 15 percent, and the run's own cross-evaluation
   found better standard states in the look run twice. Both B2 misses
   are inside that band.
4. Parcel count must be part of the objective before any floor is
   called deployable.

By the frozen rules, no rescue and no second run on these scenes.
Nothing above is edited after the run.
