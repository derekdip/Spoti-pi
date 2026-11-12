# Math Track W4: event-coordinate conditioning. Preregistration (frozen before any run)

Question: is the dominant missing degree of freedom in the large-amplitude
splash *where the atom sits in time* (an event coordinate) rather than
the atom's shape (a parameter)? W3 found, post hoc, that an onset advance
of the base token beat a dispersion slope at equal parameter count and
made the dispersion slope vanish. That was seen at A = 4 and A = 8, so
those amplitudes are reproduction targets here, not tests. Teacher, base
token `theta_0`, fit subset, evaluation set and metric are W1's and W3's
(`docs/math-track-w3-prereg.md`); nothing about them changes.

## Definitions

Base token `K(x, t; theta_0)`, `theta_0` frozen from W1 (`poc/results/
w1.json`). Time derivative `dK/dt` by central difference with step
1/240 s. Fixed-token residual at amplitude A: `r_A = eta_A - s_A K`, where
`s_A = <eta_A, K> / ||K||^2` is the least-squares gain (the gain the fixed
family can always apply; no other parameter is fitted before H1 is
scored). Recoverable error `E_rec = max(E - E_floor, 0)` with
`E_floor = E_fixed(1)`, as in W3.

Models, each fitted directly at one amplitude on the fit subset with the
gain profiled out analytically (the least-squares gain given the other
parameter), scored on the evaluation set:

| model | free scalars besides gain | search |
|---|---|---|
| M_gain | none | closed form |
| M_phase | onset shift `dt` in `K(x, t - dt)` | grid -200..+20 ms step 2 ms, then bounded refinement around the best grid point |
| M_disp | `g_eff` | grid 8..14 step 0.05, then bounded refinement |
| M_phase+g | `dt` and `g_eff` | Powell from the best of the two 1-D fits |

`dt_hat(A)` is M_phase's fitted shift; `g_hat(A)` is M_phase+g's fitted
`g_eff`. Delay laws, with `dt(1) = 0` because `theta_0` was fitted at
A = 1 and absorbs any base offset:

- log law `dt(A) = c_log log A`, `c_log = dt_hat(4) / log 4`;
- linear law `dt(A) = c_lin (A - 1)`, `c_lin = dt_hat(4) / 3`.

Gain law for extrapolation: `s(A) = A^(1 + s1)`, `s1` from M_phase's
least-squares gain at A = 4 (reported, not scored; W3 already measured a
saturating gain).

Tangent coherence of parameter `theta_j` with time, at `theta_0`, A = 1,
on the evaluation set: `chi_j = |<dK/dtheta_j, dK/dt>| / (||dK/dtheta_j||
||dK/dt||)`, with `dK/dtheta_j` by central difference (relative step
1e-3 of `|theta_j|`, or 1e-4 absolute when `theta_j = 0`). Computed for
every chirp parameter (A, lam, m, n, g_eff, phi, v_max, k_cut). The full
Gram matrix of normalised tangents is reported.

## Amplitudes (frozen)

| A | role |
|---|---|
| 1 | floor (`E_floor`) |
| 4 | calibration of `c_log`, `c_lin`, `s1` |
| 2, 8 | seen in W3 (8 also post hoc); reproduction only |
| 3, 6, 10 | new holdouts; every scored hypothesis is scored on these |

If the teacher produces a non-finite field at any amplitude, that
amplitude is dropped and reported; the hypotheses are scored on the
remaining new holdouts, with the drop stated.

## Hypotheses and bars (frozen)

- **H1 residual direction.** `P_t(A) = <r_A, dK/dt>^2 / (||r_A||^2
  ||dK/dt||^2)`, computed before any shift is fitted. Bar, as set by the
  track owner: `P_t(8) > 0.5`. Reported: `P_t` at every amplitude and
  whether it is non-decreasing over {3, 4, 6, 8, 10}. (The linearisation
  `r ~ -dt dK/dt` degrades as the shift approaches a wave period, so a
  drop at A = 10 is not counted against H1 but is reported.)
- **H2 predict the unseen delay.** Both laws predict `dt(A)` at A in
  {3, 6, 10} from A = 4 alone. The winning law is the one with the smaller
  sum of `|dt_law(A) - dt_hat(A)|` over the three. Bar: the winning law is
  within 15 ms of `dt_hat(A)` at every new amplitude. Reported: whether
  the winning law's error `E_law(A)` (token with the law's `dt` and gain)
  is within 0.05 of M_phase's direct-fit error at every new amplitude;
  and the reproduction of `dt_hat(8)` against the post-hoc -75 to -79 ms.
- **H3 coordinate beats shape.** Direct fits, one added scalar each. Bar:
  `E(M_phase) < E(M_disp)` at every new amplitude (not pooled). Reported:
  the same comparison under extrapolation from A = 4 with the log law for
  both (`g_eff` log-linear as in W3).
- **H4 dispersion disappears after timing.** Bar: at every new amplitude,
  `(E(M_phase) - E(M_phase+g)) / (E(M_phase) - E_floor) < 0.10`, i.e.
  conditioning `g_eff` on top of the shift recovers less than a tenth of
  what remains. Reported: `g_hat(A) - g_0` per unit log A, against W3's
  +0.24.
- **T1 tangent coherence** (prediction stated with its reason). Because
  `dK/dg_eff` and `dK/dt` are both dominated by `-A env sin(Phi)` with
  positive weights (`tau^2 / 4r` and `g tau / 2r`), while the envelope
  parameters' tangents follow `cos(Phi)`, `chi_g_eff` should be high and
  the others low. Bar: `chi_g_eff > 0.5` and at least twice the largest
  of `chi_lam`, `chi_v_max`, `chi_k_cut` (the other W3-conditioned
  parameters). `chi_phi` is expected to be high as well and is reported.

## Reported diagnostics (not scored)

- Ordered tangent decomposition of `r_A` at each amplitude: share along
  `dK/dt` (coordinate), then share of the remainder along the span of the
  shape tangents (lam, g_eff, v_max, k_cut, m, n, phi), then the
  orthogonal rest; and the joint least-squares share of the full span, to
  show how much the overlap inflates any single attribution.
- Per-frame linearised shift `b(tau)` from `r_A ~ a K + b dK/dt` per
  frame at A = 6 and 10: whether the shift drifts with `tau` (the
  `dt(A, tau)` alternative named in the outcome rules).

## Outcome rules (frozen)

- **Coordinate confirmed:** H1, H2, H3, H4 all hold. Amplitude-dependent
  event coordinates are the missing representation; the runtime fix is
  one banked number per token and no extra operations.
- **Proxy:** H1 and H3 hold, H2 fails. The shift is the local mechanism
  but no cause-amplitude law extrapolates; the per-frame drift diagnostic
  decides whether `dt` depends on propagation state (`dt(A, tau)`).
- **Neither:** H1 or H3 fails. Scalar corrections stop here; the next
  representation is a small unary basis, not another scalar.
- H4 and T1 are scored independently of the above and establish, or do
  not, the explanatory ordering "phase error -> apparent dispersion
  error".

After W4, water pauses regardless of outcome, per the track owner; the
next track returns to the corn path branch (B3's defect class: smooth
approximation plus singular geometry plus explicit events).

Results go in `poc/results/w4.md`; nothing above is edited after the run.
