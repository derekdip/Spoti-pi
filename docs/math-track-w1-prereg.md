# Math Track W1: transfer to a wavefront teacher. Preregistration (frozen before any run)

Three laws found on the vegetation/worldline teacher are tested on water
before observing water's results. Nothing here is tuned after the run.

## Teacher (frozen)

`poc/water/teacher.py` with the mild nonlinearity: exact per-mode linear
propagation (full dispersion, depth 0.4 m, damping `0.25 + 1e-4 k^2`) plus,
in physical space after each substep, amplitude-dependent damping
`0.25 |eta| / 0.02` per second and a cubic restoring term `1e4 eta^3`.
Design-time check: a single base-amplitude splash deviates 6.3 percent
from the linear teacher, 53 percent at four times the amplitude; the pair
cross-term at 0.6 m separation is 0.5 and 3.4 percent. 6 m periodic pond,
256 x 256 (512 x 512 for question 2), splash = 3 cm Gaussian impulse of
downward velocity, base amplitude 1.0 m/s.

## Consumers (frozen)

`G0` = surface height. `G1` = surface slope (gradient by central
differences on the fine grid). Errors are RMS over points within 2 m of
the splash (or the pair midpoint) and frames from 0.15 s on, relative to
the reference field's RMS.

## Token (frozen after one fit)

The dispersive chirp with viscous cutoff (`poc/water/tokens.py`), fitted
once to the nonlinear teacher's single base-amplitude splash under `G0`
with the same procedure as before (differential evolution then Powell on
a subset). Other amplitudes scale the token amplitude linearly; the
nonlinearity is expected to break that, which question 3 measures.

## Question 1: does the liveness law transfer?

Rain: 40 splashes at 2 per second over 20 s at uniform random positions in
the central 4 x 4 m (seed 0), base amplitude. The token's monotone future
envelope `K-bar(tau) = sup_{s >= tau} max_r |h_token(r, s)|` is computed
from the fitted parameters; its tail on `tau` in [1, 8] s gives the decay
rate `beta` and constant `C`. `M(eps)` = time-averaged number of tokens
with `K-bar(t - t_j) > eps` over `t` in [5, 20] s, for `eps` in {3e-2, 1e-2,
3e-3, 1e-3, 3e-4, 1e-4, 3e-5} times `K-bar(0)`.

- **W1-H1.** `M(eps)` is monotone in `log(1/eps)` (Spearman > 0.95) and
  its slope against `log(1/eps)` is within 50 percent of `R / beta` with
  `R = 2` per second.
- Reported: the reconstruction error of the pruned token field against the
  full token field, and the full token field against the teacher rain.

## Question 2: does the observation-order law transfer?

Single base splash on the 512 grid, frames at 0.5, 1, 1.5, 2, 3 s. The
reference field is re-represented on coarse grids of `n` cells per side,
`n` in {12, 16, 24, 32, 48, 64, 96, 128, 192, 256} (cells 50 cm to 2.3 cm),
by sampling at the coarse nodes and interpolating back with (a) bilinear
and (b) bicubic splines. Height error from the interpolant; slope error
from the interpolant's gradient. `N = n^2`. Exponents are the slopes of
`log E` against `log N` over `n` in {64, 96, 128, 192, 256}.

Theory: piecewise polynomial of degree `r`, consumer observing derivative
order `k`, domain dimension `d`: `E = O(N^{-(r+1-k)/d})`. With `d = 2`:
bilinear height -1, bilinear slope -1/2, bicubic height -2, bicubic slope
-3/2.

- **W1-H2 (primary).** Slope exponent minus height exponent is in
  [+0.3, +0.7] for both interpolants (one lost order of `h`), so slope is
  systematically harder to compress than height.
- **W1-H3.** Bicubic height exponent is steeper than bilinear height
  exponent by at least 0.5.
- Reported: the absolute exponents against the four predicted values, with
  the caveat that the field's viscous cutoff wavelength (about 12 cm) puts
  the coarser half of the sweep outside the asymptotic regime.

## Question 3: when does cause superposition stop sufficing?

Pairs of simultaneous splashes at separations `D` in {0.281, 0.609,
1.219, 2.391} m (grid-exact) and amplitudes `a` in {0.5, 1, 2, 4, 8} times
base. Teacher runs: single at each amplitude (the second single is its
translate), pair at each `(D, a)`. Interaction strength
`I12 = ||h(1+2) - h(1) - h(2)|| / ||h(1+2)||` for height and for slope,
over points within 2 m of the midpoint, frames from 0.15 s. Also the
error of the base-fitted token pair scaled by `a` against the teacher pair
(the representation the runtime would use).

- **W1-H4.** `I12(height)` is monotone increasing in `a` at every `D`
  (Spearman = 1) and non-increasing in `D` at every `a` (Spearman <= 0).
- **W1-H5.** At base amplitude `I12(height) < 5` percent at every `D`;
  at 8 times base `I12(height) > 5` percent at the smallest `D`.
- **W1-H6 (from the design-time observation).** At every `(D, a)` the
  cross-term `I12` is smaller than the single-splash deviation from the
  base-scaled token, so the nonlinearity is mostly single-cause and an
  amplitude-dependent token would outlast raw superposition.

## Outcome rules (frozen)

Transfer succeeds if H1 and H2 hold. H3 to H6 are reported as supporting
or not. Results go in `poc/results/w1.md`; nothing above is edited after
the run.

## Scoring-code correction (declared after run 1, before run 2; protocol unchanged)

Run 1 (`poc/results/w1_run1.*`) reported `I12 = 1.00` in every Q3 cell.
The scoring code passed the residual `pair - s1 - s2` to the relative-error
function as if it were a prediction, computing `||R - pair|| / ||pair||`
instead of `||R|| / ||pair||`. The replicated cell (D = 0.61 m, base
amplitude) has a true interaction of 0.4 percent. The two calls are
corrected; nothing else changes. Q1 and Q2 are deterministic and
unaffected. Run 2 is the run Q3 is judged on.
