# Reading the token's parameters off the teacher makes the fire worse on every scene

Three places in this arc showed the consumer-space RMS objective
selecting against appearance, and the height control added a fourth:
pinning one measured parameter on `plume` reached a glow correlation of
0.84, the best in the arc, on 7 parcels, at a total error the fitter
scored 14 percent worse and would never have chosen. The obvious next
question was whether the objective, not the grammar, is the binding
constraint on how the fire looks.

`poc/fire_physics_first.py` tests it the direct way. Seven constants are
measured **once** on `plume`, the reference scene, and applied unchanged
to every other scene: peak flame temperature, terminal rise speed, its
acceleration, parcel width at birth and its growth rate, the cooling
time and the soot load. Nothing is measured per scene; nothing is fitted
to a consumer error. The remaining seventeen parameters are fitted as
before, by identical code and settings. The prediction was recorded in
the script's docstring and committed before the run: the correlation
rises on a majority of scenes, or the objective is not the constraint.

## Result: it fails on every scene, by a wide margin

Constants measured on the reference teacher: `amp` 906.5 K, `v_rise`
3.47 m/s, `accel` 0.66 /s, `width` 0.055 m, `grow` 0.140 m/s, `cool`
0.775 s, `soot_amp` 10.09.

| scene | free error | physics error | free visual | physics visual | free corr | physics corr |
|---|---|---|---|---|---|---|
| plume | **0.475** | 0.524 | **0.705** | 0.759 | **0.75** | 0.65 |
| gusty | **0.464** | 0.573 | **0.583** | 0.735 | **0.82** | 0.60 |
| gust_shelf | **0.519** | 0.614 | **0.582** | 0.773 | **0.80** | 0.56 |
| strong_gust | **0.496** | 0.628 | **0.595** | 0.774 | **0.80** | 0.56 |
| bed_chain | **0.532** | 0.599 | **0.616** | 0.790 | **0.81** | 0.56 |

Correlation rose on **0 of 5**. Median visual error **+28.3 percent**,
median total error +18.3 percent. By the recorded rule the verdict
reads "the objective is not the binding constraint; the grammar is".

## Why that verdict over-claims, and what the run actually establishes

The rule was written before the run and it is reported as written. It
over-claims, and the evidence against it is in this repository: the
height control pinned **one** of these same seven constants, `v_rise`
at 2.25 m/s, and `plume` improved, visual error 0.705 to 0.662 and
correlation 0.75 to 0.84. Here `plume` with seven pinned, `v_rise`
among them at 3.47, lands at 0.759 and 0.65. One measured constant
helped and seven hurt, so the experiment cannot separate "measured
physics does not help" from "my identification of measured quantity
with model parameter is wrong".

There is a concrete reason to suspect the identification. **The
teacher's observable quantities are ensemble properties; the model's
parameters are per-parcel properties**, and they share names without
sharing meaning:

- `cool` was measured from the decay of the plume's centreline peak.
  That is the decay of a *superposition* of parcels passing a point,
  not the cooling of one parcel.
- `grow` was measured from the lateral spread of the *time-mean* field,
  which contains the scatter of parcel positions as well as the growth
  of each parcel, so it overstates the per-parcel growth.
- `v_rise` was fitted as the asymptotic speed of the *leading edge* of
  the start-up front, which is the fastest part of a growing structure
  rather than the terminal speed of a typical parcel, and at 3.47 m/s
  it is half again the 2.25 the height control used successfully.

All three errors push the same way: parcels too fast, too wide and too
short-lived, which is what the pictures of the degradation show.

So what this run establishes firmly is narrower than its verdict line
and more useful than either reading:

**Substituting seven ensemble measurements of the teacher for the
token's per-parcel parameters makes the representation worse on every
scene tried, by 28 percent of visual error.** For a project whose thesis
is causes rather than effects, that is worth stating plainly: reading
the *cause* off the world is right and has worked throughout this
repository, but a token's internal parameters are not observables of
the teacher even when they carry the same name and the same units. The
map from one to the other is itself a thing that needs calibrating, and
this is the first experiment in the arc to test it.

## What would settle the open question

The objective-versus-grammar question remains open, and the way to
close it is one parameter at a time rather than seven at once: pin each
of the seven alone, on one scene, and see which individually improve
the correlation. The height control already did this for `v_rise` at
2.25 and got the best visual result in the arc. Seven fits on one scene
is about thirty-five minutes and would say which identifications are
sound, which is a precondition for any further claim that the objective
is what limits appearance.

Until that is done, no claim should be made in either direction. The
single best-looking state produced anywhere in this arc remains `plume`
with `v_rise` pinned at 2.25 and everything else fitted: correlation
0.84 against a static-blob ceiling of 0.85, on 7 parcels.
