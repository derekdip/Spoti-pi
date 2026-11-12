# Math Track W3 results: unary conditioning before interaction complexity

Preregistration: `docs/math-track-w3-prereg.md` (frozen, unchanged). Raw
outputs: `poc/results/w3.md`, `w3.json`, `w3.png`. One run; no scoring
code was changed after it.

## Verdict by the frozen rules: failure

| hypothesis | bar | result |
|---|---|---|
| H1 unary generalisation | median recovered fraction over A in {2, 8} >= 0.5, no degradation at 0.5 | 0.22 (A = 2: -0.07; A = 8: 0.51); 0.5 degrades by 8.7% (bar 10%): **fail** |
| H2 approach to the interaction floor | median R_cond / R_fixed <= 0.25 | 0.78 (A = 2: 1.07; A = 8: 0.49): **fail** |
| H3 unary beats pair complexity per parameter | eta(M_gain) >= 2 eta(P1), eta(M1) >= 2 eta(P2) | 0.226 vs 0.019 and 0.112 vs 0.012, ratios 12 and 9: **pass** |
| H4 residual becomes interaction-dominated | cross-term share rises on every held-out pair | rises on 3 of 4; D = 0.609, A = 2 falls from 0.0345 to 0.0345 (fourth decimal): **fail** |
| H5 shape beats gain | every M1..M4 below M_gain on median recoverable error | M2, M3, M4 at 0.314 vs 0.418: yes; M1 at 0.420 vs 0.418: no: **fail** |
| knee (reported) | M1 recovers >= 90% of M4's gain over M_gain | M1 recovers 0%; M2 recovers 100% |

Outcome rule: H5 fails, so failure. H1 fails independently.

### A defect in the frozen text, declared

The preregistration says the recoverable error is scored "over the
holdouts where the fixed token has E_rec > 0.05 (A = 2 and 8)". The two
clauses disagree: the fixed token's error at A = 2 was already known from
W1 to be 0.383, which is 0.039 above the floor of 0.344, below the
threshold. The script implements the named set {2, 8}, and that is the
verdict reported above. Under the threshold clause alone (A = 8 only): H1
would pass by 0.012 (0.512), H2 would still fail (0.49), H5 would still
fail (M1 is above M_gain at A = 8 as well). The verdict is failure under
either reading. Every number at A = 2 is a difference of two quantities
within 0.05 of each other and should be read as noise; the A = 8 column
carries the content.

## Single-splash errors (calibration A = 1 and 4; holdout 0.5, 2, 8)

| model | params | A = 0.5 | 1 | 2 | 4 | 8 | conditioned slopes (per unit log A) |
|---|---|---|---|---|---|---|---|
| M0 fixed | 0 | 0.344 | 0.344 | 0.383 | 0.688 | 1.546 | |
| M_gain | 1 | 0.360 | 0.344 | 0.393 | 0.598 | 1.131 | gain -0.248 |
| M1 (+ lam) | 2 | 0.360 | 0.344 | 0.393 | 0.598 | 1.136 | gain -0.276; lam -0.023 |
| M2 (+ g_eff) | 3 | 0.373 | 0.344 | 0.385 | 0.500 | 0.930 | gain -0.231; lam -0.038; g_eff +0.235 |
| M3 (+ v_max) | 4 | 0.374 | 0.344 | 0.385 | 0.499 | 0.932 | + v_max -0.119 |
| M4 (+ k_cut) | 5 | 0.374 | 0.344 | 0.385 | 0.497 | 0.931 | + k_cut +2.9 |

Three things are visible without any hypothesis.

**Gain saturates.** The fitted gain exponent is 0.75 to 0.80: an eight
times larger impulse makes a five times larger wave. This is the
amplitude-dependent damping term of the teacher showing up as amplitude
saturation, not as a change of decay rate. Conditioning the decay rate
(`lam`, M1) does nothing at all: the slope fits to -0.02 and the error is
unchanged at every amplitude. The predeclared order put the damping
nonlinearity in the wrong parameter.

**Dispersion stiffens.** The effective gravity slope is +0.24 per unit
log A, so g_eff is 10.16 at A = 4 and 10.32 at A = 8 against 9.83 at
base: the cubic restoring term makes the waves 3 to 5 percent faster on
average. Within the frozen family this is the one shape parameter that
matters: it cuts the A = 8 error from 1.13 to 0.93 and the A = 4 error
from 0.60 to 0.50. The post-hoc check at the end of this document shows
it is a proxy for something the family could not express, an
amplitude-dependent onset time.

**Then nothing.** Front speed and viscous cutoff slopes change no error
by more than 0.002. The knee is at two conditioned quantities, but they
are gain and dispersion, not the frozen pair gain and damping. The
reported knee statistic is therefore 0% at M1 and 100% at M2.

## Why H1 fails: the family cannot reach the floor even at its own calibration point

At A = 4, where the slopes are fitted, the best conditioned token scores
0.497 on the evaluation set and 0.490 on the fit subset, against the
floor of 0.344. A log-linear shift of these five quantities does not
contain the A = 4 splash. At A = 8 (extrapolation), conditioning recovers
51% of the amplitude-shaped error and leaves 0.59 above the floor. So the
missing representation is not "the same parameters, depending on A";
roughly half of the nonlinear error is that, and the other half is a
shape the chirp family does not produce at any parameter setting. The
post-hoc diagnostic below asks which shape.

The mild degradation at A = 0.5 (0.374 vs 0.344) is also informative: the
teacher at half amplitude is linear (same error as at A = 1), but
`log(A / A0)` is antisymmetric about A0 and pushes the parameters the
wrong way. The true dependence saturates at low amplitude, so the family
should be `theta_0 + theta_1 log(1 + A / A_nl)`, not `log(A / A0)`. That
is a diagnosis, not a rescue; it was not run.

## Why H2 and H4 fail: the residual did not transition

The prediction was that after conditioning the unary atom, the pair
residual would turn from "bad unary + small interaction" into "small
unary + actual interaction". It moved a fraction of the way. On the
nearest pair at A = 8 the true cross-term's share of the remaining
residual rises from 11% to 19%; at the wider separation from 4% to 6%;
at A = 2 it does not move, because there is nothing to recover. After
the best unary conditioning the pair residual is still 80 to 95 percent
single-cause error. The ratio of recoverable unary error to interaction
strength falls from 6.4 to 3.1 at A = 8, not to below 1.6 as H2 needed.

The hierarchy's next step, "now add an interaction atom", is not yet
justified by these residuals. The unary atom is still the bottleneck.

## H3 passes, and P1 and P2 show why the order matters

Per parameter, amplitude conditioning of the unary token buys 9 to 12
times more held-out pair error reduction than a pair term. More telling
is what the pair terms do: fitted on the A = 4 nearest-pair residual of
the *fixed* unary model, P1 and P2 make the A = 8 wide pair worse (1.65
against 1.54) and barely help the near one (1.50 against 1.64). The pair
residual they were fitted to was 90% unary error, so the "interaction"
atom absorbed unary misfit and does not transfer. This is the expected
behaviour of a representation learner that adds interaction order before
its unary order is adequate, and it is the strongest positive content of
W3: fitting the wrong axis first produces a term that generalises
negatively.

## What W3 establishes

1. **Condition unary first** holds as an efficiency statement (H3, by an
   order of magnitude) and fails as a sufficiency statement (H1, H2): the
   conditioned unary atom recovers half of the nonlinear error and stops.
2. **Which parameters carry the nonlinearity** is now measured within
   the frozen family: gain (saturation, exponent 0.75 to 0.8) and
   dispersion (g_eff +2.4% per doubling). Damping, front speed and cutoff
   carry none of it. A deployed amplitude-aware splash token needs two
   extra numbers, but not the two the physical ordering predicted; and
   the post-hoc check below says the second number should be an onset
   advance, not a dispersion shift.
3. **The residual after conditioning is still unary**, so the expansion
   table's row "changes with cause amplitude -> condition unary atom" is
   necessary but not sufficient here; what remains changes with amplitude
   and is not reachable by conditioning the frozen parameters. The table
   needs a row that distinguishes "same atom, wrong parameter law" from
   "wrong atom", and only a residual diagnostic can tell them apart.
4. **The frozen text had an internal inconsistency** (threshold clause
   vs named set) that did not affect the verdict but is recorded.

## Post-hoc residual diagnostic (exploratory, unregistered, not scored)

`poc/w3_residual_diagnostic.py`, outputs `poc/results/w3_residual.md`,
`w3_residual.json`, `w3_residual.png`. It re-runs the teacher at A = 1, 4,
8 and decomposes the single-splash residual of the fixed (M0) and
conditioned (M2, M4) tokens on W1's evaluation set. Nothing here was
predeclared; it exists to make the next preregistration specific.

| share of residual energy | M0, A=1 (floor) | M0, A=4 | M2, A=4 | M0, A=8 | M2, A=8 |
|---|---|---|---|---|---|
| relative RMS error | 0.344 | 0.688 | 0.500 | 1.546 | 0.930 |
| axisymmetric | 0.95 | 0.97 | 0.96 | 0.96 | 0.96 |
| one gain + one time shift, whole field (linearised) | 0.01 | 0.68 | 0.09 | 0.91 | 0.56 |
| gain + time shift per frame | 0.11 | 0.71 | 0.39 | 0.92 | 0.73 |
| gain + time shift per radius bin | 0.10 | 0.70 | 0.37 | 0.92 | 0.76 |
| along the A = 1 floor residual | 1.00 | 0.24 | 0.49 | 0.00 | 0.02 |
| in the near-field early box (r < 0.5 m, t < 1 s) | 0.41 | 0.51 | 0.61 | 0.45 | 0.60 |
| teacher energy in that box | 0.42 | 0.44 | 0.44 | 0.49 | 0.49 |

Reading, in the order of the expansion table:

1. **The residual is single-cause.** 95 to 97 percent of its energy is
   axisymmetric at every amplitude and for every model. It is not grid
   noise and, on a single splash, cannot be interaction. The table's
   "condition unary atom" row was the right row.
2. **The floor is a shape misfit, not a gain or phase error.** At A = 1
   the linear family's own residual (0.344) is only 1% explainable by a
   global gain and time shift, and 11% even with a free gain and shift
   in every frame. Its radial profile at t = 2 s has 12 zero crossings
   against the teacher's 8: the chirp puts too many short waves near the
   source late on. That misfit is what W1's fit left, and conditioning on
   amplitude was never going to touch it.
3. **The fixed token's nonlinear error is almost entirely gain and
   phase.** At A = 8, one gain and one time shift for the whole field
   explain 91% of M0's residual (linearised, so an upper bound). The
   log-linear conditioning captured the constant part of this: after M2,
   a whole-field gain and shift still explain 56% at A = 8 (the slopes
   fitted at A = 4 under-extrapolate) but only 9% at A = 4, where they
   were fitted.
4. **What conditioning missed is time-varying.** At the calibration point
   A = 4, M2's residual is half the floor shape (49% along the A = 1
   residual) and most of the rest is a gain and phase correction that
   changes from frame to frame (39% per-frame against 9% global). The
   wave's amplitude decays during the event, so the nonlinearity weakens
   as it goes; a parameter law conditioned on cause amplitude gives one
   value for the whole event, and the residual is the drift. The
   representation this points at is conditioning on *local* amplitude
   (the token's own decaying envelope) rather than on the cause's
   amplitude: the same two axes, gain and dispersion, but read from state
   the token already computes, at no extra runtime cost and one extra
   parameter (the conditioning's decay).
5. **A smaller part is a new shape.** Even per-frame gain and phase
   freedom leaves 0.39 at A = 4 and 0.47 at A = 8 against the floor of
   0.344. This part grows with amplitude and concentrates in the
   near-field early box (60% of the residual against 44 to 49% of the
   teacher's energy): the nonlinear source region. Crest/trough asymmetry
   is absent (teacher 1.05 to 0.99, token 1.00), consistent with the
   teacher's odd nonlinearities producing only odd harmonics. Whether this
   is harmonic steepening or the cavity's own dynamics is not determined.

The ceiling this sets for the next track is quantitative: a conditioning
law that follows the local amplitude can at best reach about 0.39 at A =
4 and 0.47 at A = 8 (the per-frame numbers), and the frozen family's
floor stays at 0.344 unless the atom itself changes.

### Direct check: onset time is the missing conditioned parameter

`poc/w3_shift_check.py`, output `poc/results/w3_shift_check.json`. The
linearised time-shift basis above is only a first-order proxy, so this
fits an actual shift: the token evaluated at `t - t_event - dt0`, with
`dt0` free, directly at A = 4 and A = 8 (fit subset; scored on the
evaluation set). Same protocol as W3's fits otherwise.

| fitted at | gain + dt0 (2 params) | gain + g_eff (2 params) | gain + g_eff + dt0 (3 params) |
|---|---|---|---|
| A = 4 | **0.424**, dt0 = -36 ms | 0.500, g_eff slope +0.24 | 0.423, dt0 = -38 ms, g_eff slope -0.02 |
| A = 8 | **0.614**, dt0 = -79 ms | 0.783, g_eff slope +0.39 | 0.614, dt0 = -75 ms, g_eff slope +0.03 |

(The A = 8 column fits directly at A = 8, so "gain + g_eff" here is
0.78, not W3's extrapolated 0.93.)

Three consequences. First, with the same two parameters, an onset advance
beats the dispersion slope at both amplitudes, and once the delay is free
the g_eff slope collapses to zero: **the dispersion stiffening W3 measured
was the frozen family's best log-linear imitation of a time shift.** The
physical reading "cubic restoring term raises the effective gravity" was
wrong; the large-amplitude wave train is the base wave train started
earlier. Second, the event's effective time was not among the five
parameters the preregistration allowed to depend on amplitude, which is
why H1 could not pass: the family was conditioned on the wrong axes.
Third, the cost of the fix at runtime is zero operations (`tau = t -
t_event - dt0(A)`) and one banked number per token; the delay is not
log-linear in A (-36 ms at 4, -77 ms at 8; a log law from A = 4 would
predict -54 ms, a linear law -72 ms), and choosing that law is exactly
what the next preregistration must do before seeing A = 8.

What this leaves: 0.42 at A = 4 and 0.61 at A = 8 against the floor of
0.344, with the residual's per-frame decomposition suggesting a further
time-varying component at A = 8 and a near-field shape at both.

## Suggested next: W4, conditioned event time, predicted before observation

The residual has now named the axis (onset time) and set the ceiling. A
preregistration that follows from it, without further fitting:

1. Family: the frozen W1 token with gain exponent and onset advance
   conditioned on amplitude; no shape parameter conditioned.
2. Two candidate laws for `dt0(A)`, declared in advance: log-linear in A
   (W3's family form) and linear in A. Calibrate both on A = 1 and 4
   only, predict dt0 and the error at A = 8 and A = 2 for each, and score
   the prediction, not the fit.
3. Bars: the winning law predicts dt0(8) within 15 ms (one fifth of a
   wave period at r = 0.5 m) and E(8) within 0.05 of the direct fit
   (0.61); E(4) <= 0.45 with two parameters.
4. Residual transition re-scored (W3's H4) with the onset-conditioned
   unary model, since the unary bottleneck is now smaller.
5. The A = 0.5 saturation is scored as a third holdout, predicting no
   degradation under the linear law and degradation under the log law.

If both laws miss at A = 8, the delay is not a function of cause
amplitude alone and the row to add to the expansion table is "residual is
a phase drift within the event -> condition on local state, not on the
cause".

