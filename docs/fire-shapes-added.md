# Three source shapes added to the fire grammar, and what they did

F3 (`docs/math-track-f3-results.md`) established that the fire vocabulary,
not the search, was the limit: greedy selection reached 96 percent of an
exhaustive joint fit, the joint fit still left 63 percent relative error,
and two teacher runs differing only in random seed agreed to within 0.003
on forced scenes, so the gap was explainable structure rather than chaos.
It named the cause: every source is one Gaussian column anchored to its
cause, so it cannot split, cannot detach, and cannot hand off to a bed
with its own life cycle.

This is those three shapes. No experiment is frozen here. The
achievability check F3 prescribed runs first, because freezing a bar
before knowing it is reachable is the mistake F3 caught.

## The shapes

| shape | what it models | parameters |
|---|---|---|
| `split` | a shelf over a source divides its lateral profile into two branches at the shelf edges, diverging with height, while the direct column is shadowed behind the shelf | `split_amp`, `split_spread` |
| `puff` | at the cause's switch-off the column detaches, its vertical profile translating upward at its own speed while fading | `puff_amp`, `puff_rise`, `puff_decay` |
| `bed` | a patch source with an ignition time growing with distance from the flame, and an envelope that lights, holds a plateau, then dies as the fuel runs out, over the shorter wider column a pool fire makes | `bed_amp`, `bed_delay`, `bed_speed`, `bed_dur`, `bed_fall` |

The height over which a split develops is tied to the column width rather
than being a free parameter. The bed also depletes the fuel field, which
the older `secondary` class never did; the ignition consumer reads alight
as hot *and* fuelled, so without depletion a lit bed stayed lit forever.

## Achievability: they work, and they are not enough

Joint fit of every parameter of every class, which is the floor the
vocabulary can reach.

| scene | F3 floor | with the three shapes |
|---|---|---|
| obstacle | 0.644 | 0.593 |
| shelf_bed | 0.714 | 0.615 |
| full | 0.608 | 0.590 |
| ignition | 0.626 | 0.633 |
| delayed_ignition | 0.682 | 0.683 |
| windy | 0.496 | 0.496 |
| twin | 0.553 | 0.553 |
| **median** | **0.626** | **0.593** |

**Each shape activates only where its physics applies**, which is the
strongest evidence they are implemented correctly rather than acting as
extra free parameters. `split` switches on near its maximum on all four
scenes with a shelf over the burner and stays off on the rest. `puff`
activates only on the burner-shutoff scene. `bed` only where there are
fuel beds. The two scenes with neither obstacle nor patch nor shutoff,
`windy` and `twin`, are unchanged to four decimals.

**The bed fixes the consumer three experiments could not move.** Ignition
error on `shelf_bed` goes from 1.000, no better than predicting nothing,
to 0.396; on `full` from 0.645 to 0.449. Fuel depletion is what did it.

**The combined floor moves 5 percent and the binding consumers change.**
Median per-consumer at the joint fit is now visual 0.708 and hazard grid
0.758, against heat 0.317 and ignition 0.550. None of the three shapes
addresses the two that now dominate, and both of those depend on the
extent and shape of the hot region rather than on sources appearing and
disappearing.

## Two diagnostics on what is left, one negative

**Travelling structure: tested, not supported, dropped.** The hypothesis
was that the remainder is a train of coherent structures rising up the
column, the same token the wind work found for grass. The residual's
lagged height-to-height correlation peaks at zero lag, 0.87 at one cell
and 0.60 at two, and decays monotonically with lag rather than peaking at
a displaced lag. It is spatially coherent over about 12 cm and it is not
rising. Not carried forward.

**Lateral profile: confirmed, and the direction was the opposite of the
guess.** The column's cross-section is hard-coded Gaussian. The guess was
that it should be closer to exponential, because the corn grammar's own
kernel fitted an exponent of 1.21 rather than 2. That was wrong. Fitting
the exponent shows flatter and squarer helps, not peakier:

| scene | Gaussian, q = 2 | q = 2.4 | q = 3.2 |
|---|---|---|---|
| obstacle | 0.593 | 0.562 | **0.537** |
| twin | 0.553 | 0.546 | **0.540** |
| full | 0.590 | 0.596 | 0.619 |

Two of three improve and both were still improving at 3.2, the edge of
the range tried, so the optimum was not found. The comparison is also
biased against the finding: the Gaussian column is a full 28-parameter
joint fit while each variant only refits three parameters from it, so the
gains are lower bounds.

Physically this is the right direction and the corn analogy was the wrong
one. A hand pressing into grass falls off exponentially from contact; a
buoyant plume has a fairly uniform hot core with sharp edges. A Gaussian
spreads heat too far sideways, which is exactly what a threshold-based
hazard grid and a glow consumer punish.

**A first attempt at this test was invalid and is recorded as such.** It
patched the module at run time and returned byte-identical errors for
every exponent from 1.0 to 3.0, which cannot happen if the parameter is
live. `lat_q` is now a real field on the state, defaulting to zero
meaning the Gaussian exponent of 2, and the numbers above come from that.

## Where this leaves the fire grammar

The three shapes are correct, targeted, and worth keeping. They take the
floor from 0.626 to 0.593 and they make the ignition consumer usable for
the first time. They do not make the representation deployable, and the
0.35 F3 asked for is still far off.

The next thing is not a fourth source shape. It is the profile of the
source that already exists: the lateral exponent above, with its range
extended past 3.2 and fitted rather than swept, and the same question
asked of the vertical profile, which is hard-coded exponential and has
never been tested at all.

## The column's own profile, and what it exposed about the measurement

Both profile exponents were hard-coded since V0 and never questioned: the
lateral one Gaussian, the vertical one exponential. The teacher says the
vertical one is wrong before any fitting is done. Its centreline excess
falls from 907 K to 251 K over 2.26 m while the log-slope steepens from
-0.02 to -1.01, which a pure exponential cannot do because its log-slope
is constant by definition. Fitting `exp(-(y/h)^p)` to that centreline
gives `p = 2.48`, `h = 1.84 m`.

Both are now fittable fields, `lat_q` and `ver_p`, each defaulting to
zero meaning the old hard-coded value, registered as one `profile` class.
A prediction was recorded before the fit ran: `ver_p` above 1 and `lat_q`
above 2.

**Half the prediction held and half did not.** `ver_p` landed above 1 on
all seven scored scenes, median 1.67, so the exponential was genuinely
wrong. `lat_q` ranged from 1.00 to 8.00 across similar scenes, which is a
parameter absorbing whatever slack the fit can give it rather than
recovering a physical shape. The flatter-core reading is not claimed.

**Two scenes got worse, which is impossible, and that is the finding.**
The shapes-only search space is a strict subset of the profile-enabled
one, since `lat_q = 2` and `ver_p = 1` reproduce it exactly, so a true
optimum with the profile enabled can never be worse. Yet `shelf_bed` went
from 0.615 to 0.731 and `windy` from 0.496 to 0.555. Every such
regression is an optimiser failure by construction.

A warm start, beginning from the profile-at-defaults configuration
instead of the all-classes-on one, confirms it and measures the slack:

| scene | shapes only | cold start | warm start | best known |
|---|---|---|---|---|
| shelf_bed | 0.615 | 0.731 | 0.619 | 0.615 |
| windy | 0.496 | 0.555 | **0.482** | 0.482 |
| ignition | 0.633 | 0.640 | **0.580** | 0.580 |
| obstacle | 0.593 | **0.466** | 0.585 | 0.466 |

Neither start dominates. The cold start wins on `obstacle` by 20 percent
and loses on `ignition` by 10. Single-start coordinate descent carries up
to 16 percent slack in either direction.

**With a decent optimiser the profile does help.** Taking the best of the
starts tried, three of four scenes improve on shapes-only and the fourth
is neutral. The floor across the arc, each column the best known at that
stage:

| | V0 | F3 | + three shapes | + profile, best known |
|---|---|---|---|---|
| median | 0.818 | 0.626 | 0.593 | **0.580** |

**This reaches back and weakens every floor number in the arc, including
F3's.** F3's vocabulary-floor bar was a single run of this same
optimiser. The caveat was stated there; the magnitude was not. At 16
percent slack, F3's 0.626 becomes 0.526, still above the 0.35 bar, so its
conclusion survives with considerably less margin than it appeared to
have. Every floor figure in this document should be read as "no worse
than" rather than as a floor.

**Where that leaves it.** The three shapes and the two profile exponents
each help, and each helps by less than the optimiser's own noise on a
bad day. Cumulatively the floor has moved from 0.818 to about 0.580,
which is a 29 percent reduction where roughly 57 percent is needed. The
next thing to fix is not the grammar. It is the measurement: coordinate
descent from one start is not good enough to tell a real floor from an
optimiser artifact, and until it is replaced no further statement about
whether the vocabulary is adequate can be trusted.
