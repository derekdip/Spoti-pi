# Is plume height the visual defect? One of two, and the answer points elsewhere

F5's control overturned F5's own premise and left a new suspect: the
visual defect is plume height, because fitted rise speeds sit near
0.5 m/s against a measured front speed of 2.25 and the pictures show a
leaning stub. That is the same class of evidence the sway claim had
before a control killed it, so it got the same test before another
round was built on it.

Script: `poc/fire_height_control.py`, whose docstring records the
prediction **before** the run and was committed before it: pinning
`v_rise` to the measured 2.25 m/s and refitting everything else should
lower the **visual** consumer error by more than 2 percent if height is
the defect. Output: `poc/results/height_control.log`, `.json`. Scenes:
`gusty` (F5's declared-seen pilot) and `plume` (never scored anywhere).
Fit settings are F5's verbatim.

## Result

| scene | fit | total error | visual error | glow correlation | plume height | teacher height | parcels |
|---|---|---|---|---|---|---|---|
| gusty | free (`v_rise` 0.52) | **0.465** | 0.602 | 0.77 | 0.48 m | 0.70 m | 14 |
| gusty | pinned 2.25 | 0.518 | 0.602 | 0.77 | **0.44 m** | 0.70 m | 16 |
| plume | free (`v_rise` 1.70) | **0.475** | 0.705 | 0.75 | **0.53 m** | 0.53 m | 14 |
| plume | pinned 2.25 | 0.541 | **0.662** | **0.84** | 0.58 m | 0.53 m | **7** |

By the recorded rule: `gusty` **fails** at -0.1 percent, `plume`
**passes** at -6.1 percent. One of two, so **height is not the general
explanation of the visual gap**, and the strongest single fact against
it needs no pinning at all: on `plume` the free fit already matches the
teacher's visible height to the centimetre, 0.53 against 0.53, and has
the **worst** visual error in the table. Perfect height, worst looks.

On `gusty` the pinned fit made the plume *shorter*, 0.48 to 0.44 m,
while rising four times faster. Visible height is rise speed times
time-to-cool, and the fitter simply shortened the cooling to pay for
the speed, which is why the visual error did not move by a thousandth.

## What the passing case actually shows

`plume` pinned is the best-looking state produced anywhere in this arc:
glow correlation **0.84**, against a static-blob ceiling of 0.85 that
nothing else in five fire experiments has approached, on **7 parcels**,
the cheapest state in the arc. It was reached by **removing** a degree
of freedom and setting it from a measurement of the teacher rather than
by fitting.

And the objective scored it worse: total error 0.541 against the free
fit's 0.475. The fitter had that state available and would never choose
it.

That is the same pattern three independent places in this arc now show:

- F5's look objective tracked the teacher's sway better than the
  standard objective on seven of nine scenes and lost on total error on
  eight of nine, often by under one percent.
- F4's gusted fits filled the swept envelope with slow cold parcels,
  which looks wrong and scores well.
- Here, a physically measured rise speed improves appearance by 6
  percent and correlation by 0.09 while costing 14 percent of total
  error.

## What this changes

The working conclusion after F5 was that the grammar is at its visual
limit. This control does not support that. On `plume` the grammar
reached the static-blob ceiling once one parameter was taken away from
the fitter, so the grammar can express a fire that looks right; the
consumer-space RMS objective does not select it.

The next question is therefore not a sixth source shape or a seventh
law. It is whether fitting the parameters the teacher can measure
directly, and fitting only the rest, produces a fire that both looks
right and decides right. Every quantity needed is already measured in
`poc/results/puff_probe.log`: rise speed, cooling time, width growth,
flicker rate. That is a cheap experiment and a different kind of claim
from anything tried so far.

One caveat stated plainly: the improvement is one scene of two, and
`plume` is the simplest scene in the set. This is a diagnostic on two
unscored scenes, not a frozen result, and it establishes a direction
rather than a number.
