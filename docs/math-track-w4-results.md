# Math Track W4 results: event-coordinate conditioning

Preregistration: `docs/math-track-w4-prereg.md` (frozen, unchanged). Raw
outputs: `poc/results/w4.md`, `w4.json`, `w4.png`, `w4.log`. One run; no
scoring code changed after it. One presentation defect in the markdown
writer (two dictionary values printed as source text) was fixed after
the run and the markdown regenerated from the saved JSON; no number
changed.

## Verdict by the frozen rules: coordinate confirmed

| hypothesis | bar | result |
|---|---|---|
| H1 residual direction | `P_t(8) > 0.5`, computed before any shift is fitted | 0.755: **pass** |
| H2 predict the unseen delay | winning law within 15 ms at A = 3, 6, 10 | linear law: misses 0.5, 0.5, 11.4 ms: **pass**; log law misses 5, 13, 36 ms |
| H3 coordinate beats shape | phase below dispersion at every new amplitude | 0.383 < 0.425, 0.522 < 0.657, 0.690 < 0.870: **pass** |
| H4 dispersion disappears after timing | g_eff recovers < 10% of what remains, every new amplitude | 3.1%, 0.0%, 0.5%: **pass** |
| T1 tangent coherence | `chi_g_eff > 0.5` and >= 2x lam, v_max, k_cut | 0.824 against 0.020, 0.092, 0.094: **pass** |

All four scored hypotheses hold on amplitudes the teacher had never been
run at, and the mechanism test holds independently.

## Direct fits (fit subset; scored on the evaluation set)

| A | role | gain only | gain + shift (dt) | gain + g_eff | gain + shift + g_eff | P_t |
|---|---|---|---|---|---|---|
| 1 | floor | 0.343 | 0.343 (-2 ms) | 0.343 | 0.340 | 0.00 |
| 2 | seen | 0.379 | 0.355 (-11 ms) | 0.369 | 0.353 | 0.13 |
| 3 | new | 0.474 | 0.383 (-23 ms) | 0.425 | 0.382 | 0.38 |
| 4 | calibration | 0.598 | 0.424 (-36 ms) | 0.500 | 0.423 | 0.57 |
| 6 | new | 0.825 | 0.522 (-59 ms) | 0.657 | 0.522 | 0.75 |
| 8 | reproduction | 0.955 | 0.614 (-79 ms) | 0.783 | 0.614 | 0.76 |
| 10 | new | 0.997 | 0.690 (-96 ms) | 0.870 | 0.688 | 0.63 |

Reproduction: A = 4 and 8 return the post-hoc values from W3 to the
decimal (-35.7 and -79.0 ms; 0.424 and 0.614). A = 1 fits a shift of
-2 ms, so the base token's time origin is consistent with `dt(1) = 0`.

The shift recovers 70%, 63% and 47% of the recoverable error at A = 3, 6
and 10 with one number. The dispersion parameter, given the same one
number, recovers 31%, 35% and 19%. Given both, the fitted `g_eff` returns
to base (9.79 to 9.93 against 9.83; slope per unit log A between -0.04
and +0.04, against W3's +0.24). The dispersion stiffening W3 measured was
a time shift wearing a parameter's clothes.

## H2: the delay is predictable from one calibration amplitude

| A | fitted shift | log law | linear law |
|---|---|---|---|
| 2 | -11.4 ms | -17.8 (miss 6.4) | -11.9 (miss 0.5) |
| 3 | -23.3 | -28.3 (5.0) | -23.8 (0.5) |
| 6 | -59.0 | -46.1 (12.9) | -59.5 (0.5) |
| 8 | -79.0 | -53.5 (25.4) | -83.3 (4.3) |
| 10 | -95.6 | -59.3 (36.4) | -107.0 (11.4) |

Calibrated on A = 4 alone, the linear law lands within half a
millisecond at A = 2, 3 and 6 and starts to bend below linear at A = 8
and 10 (the shift saturates, as the gain does). The log law, which is the
functional form W3 used for every conditioned parameter, is wrong for
this coordinate by a factor of 1.6 at A = 10.

**Reported and not met: error within 0.05 of the direct fit.** Under the
linear law the error is within 0.02 at A = 3 and 6 but 0.07 above the
direct fit at A = 8 and 0.15 above at A = 10. See the attribution below
for whether the delay miss or the gain law is responsible.

## H1 and the tangent decomposition: the residual points at time

`P_t`, the fraction of the gain-corrected residual lying along the time
tangent, rises from 0.00 at A = 1 through 0.38, 0.57, 0.75 to 0.76 at
A = 8, then falls to 0.63 at A = 10 where the shift (96 ms) is a large
fraction of the near-source wave period and the first-order relation
`r ~ -dt dK/dt` no longer holds (anticipated in the preregistration; not
counted). The ordered decomposition:

| A | along dK/dt | shape tangents, after | orthogonal rest | joint span |
|---|---|---|---|---|
| 1 | 0.00 | 0.02 | 0.98 | 0.09 |
| 3 | 0.38 | 0.03 | 0.59 | 0.44 |
| 6 | 0.75 | 0.01 | 0.24 | 0.79 |
| 10 | 0.63 | 0.09 | 0.28 | 0.78 |

Two readings. The linear family's own floor (A = 1) is 98% orthogonal to
every tangent of the token, time and shape alike: it is a shape the
family does not contain in any direction, and no scalar conditioning
will reach it. And the amplitude-dependent part is coordinate, not
shape: the seven shape tangents together explain 1 to 9 percent after
the time direction is removed.

## T1: why W3 picked the wrong parameter

| parameter | coherence with dK/dt |
|---|---|
| g_eff | 0.824 |
| phi | 0.906 |
| v_max | 0.092 |
| k_cut | 0.094 |
| m | 0.029 |
| lam | 0.020 |
| A | 0.019 |
| n | 0.004 |

The prediction and its reason were stated before computing: `dK/dg_eff`
and `dK/dt` are both the quadrature pattern `-A env sin(Phi)` with
positive weights, so they are nearly parallel; the envelope parameters'
tangents follow `cos(Phi)` and are nearly orthogonal to time. The
coherence of `g_eff` is 0.82, of the phase offset 0.91, of everything
else below 0.1. A local optimiser given `g_eff` but not `dt` will use
`g_eff` to counterfeit a time shift, reduce the error, and identify the
wrong degree of freedom. That is what W3 did. Fit improvement did not
imply representation identity; the intervention (change the amplitude,
see which parameterisation keeps predicting) did.

## Drift diagnostic (reported)

The per-frame linearised shift is only meaningful while the shift is
small against the local wave period, which holds to about A = 4. There
the early third of the event needs a larger shift than the late third
(A = 3: -30 vs -18 ms; A = 4: -51 vs -33 ms, global -36 ms). So the
coordinate is not exactly one number per event; the advance is larger
while the wave is large. The global shift captured enough of it to pass
every bar, and because the proxy outcome did not occur, the
`dt(A, tau)` alternative is not pursued here. At A >= 6 the per-frame
estimator leaves its linear range and its values are not interpretable.

## Post-hoc observations (seen after the run; candidates, not results)

1. The shift's saturation at A = 8 and 10 has the same shape as the
   gain's. With the gain law calibrated at A = 4 (`s(A) = A^0.852`), the
   law `dt(A) = c (s(A) - 1)` with `c = -15.8 ms` reproduces every fitted
   shift within 2.1 ms (A = 2: 1.3, 3: 1.2, 6: 2.1, 8: 1.8, 10: 1.0),
   against 11.4 ms for the linear law at A = 10. If it survives a
   confirmatory test on fresh amplitudes it collapses the two conditioned
   numbers into one: the wave starts earlier in proportion to how much
   larger than base it is. This is stated here so that it is on record
   as post hoc.
2. The fitted gain exponent falls with amplitude (0.96 at A = 2, 0.85 at
   4, 0.66 at 10): the gain law is itself a first-order description, and
   its miss grows with A.

### Attribution of the law's error gap (post hoc, `poc/w4_attribution.py`)

| A | direct dt, direct gain | law dt, direct gain | direct dt, law gain | law dt, law gain |
|---|---|---|---|---|
| 8 | 0.614 | 0.617 | 0.681 | 0.683 |
| 10 | 0.690 | 0.703 | 0.823 | 0.838 |

The delay miss costs 0.003 at A = 8 and 0.013 at A = 10. The gain law
costs 0.07 and 0.13: `A^0.852` calibrated at A = 4 predicts a gain of
5.9 and 7.1 where the fitted gains are 4.4 and 4.5, because the response
saturates harder than a power law from one point can say. The reported
"error within 0.05" miss is the gain law's, not the coordinate's. The
delay law as frozen is good enough for deployment across the whole range;
the gain law wants its own calibration nearer the top of it.

## What W4 establishes

1. **Event coordinates are a level of the hierarchy.** The largest
   nonlinear degree of freedom in this teacher is where the atom sits in
   time, not what shape it has. It was invisible to W3 because W3 only
   allowed shape to vary.
2. **The residual named it before the fit did.** `P_t` was computed from
   the fixed token's residual with no shift fitted, and it grew with
   amplitude exactly where the shift was needed. The decomposition
   `r = r_coordinate + r_shape + r_perp` is now a working procedure, with
   the caveat that overlapping tangents (T1) make single attributions
   ambiguous and only an intervention across amplitude resolves them.
3. **The runtime fix is free.** One banked number per token
   (`t_event - dt(A)`), no extra operations, and a law with one constant
   calibrated at one amplitude predicts the delay within 12 ms up to ten
   times base amplitude.
4. **The remaining extrapolation error is the gain's, not the
   coordinate's.** Under the linear delay law the error at A = 10 is
   0.15 above the direct fit, and the attribution puts 0.13 of that on
   the gain law and 0.01 on the delay. The delay law transfers; the
   saturating gain needs a calibration point nearer the top of the
   range, or the post-hoc law that ties the two together.
5. **The floor is out of family.** 98% of the base-amplitude residual is
   orthogonal to every tangent of the chirp. Reaching below 0.34 needs
   a different atom, not a conditioned one; that is a separate question
   and water pauses here per the track plan.

## Next, per the track owner

Water pauses. The next track returns to the corn path branch and asks
whether the same procedure (decompose the residual onto known tangent
spaces, add the coordinate it lives in) works on B3's defect class:
smooth approximation plus singular geometry plus explicit events.
