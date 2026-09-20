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
