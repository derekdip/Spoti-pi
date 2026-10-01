# Math Track W1 results: transfer to a wavefront teacher

Preregistration and scoring corrections: `docs/math-track-w1-prereg.md`.
Raw outputs: `poc/results/w1.md`, `w1.json`, `w1.png`, `w1.log`; run 1
(two scoring-code defects, both declared before run 2) is kept as
`w1_run1.*`.

## Verdict by the frozen rules: transfer fails on H1, succeeds on H2, and Q3 holds throughout

| question | hypothesis | result |
|---|---|---|
| Q1 liveness | H1: live count linear in log(1/eps), slope within 50% of R/beta | Spearman 0.99, slope 2.36 vs predicted 5.05: fail |
| Q2 observation order | H2: slope loses one order of h for both interpolants | bilinear +0.47, bicubic +0.68 (bar 0.3 to 0.7): pass |
| Q2 | H3: bicubic height steeper than bilinear by >= 0.5 | -1.91 vs -0.87: pass |
| Q3 interaction | H4: monotone in amplitude, non-increasing in separation | pass, every row and column |
| Q3 | H5: below 5% at base amplitude, above 5% at 8x for the nearest pair | 1.3% max at base; 18.7% at 8x: pass |
| Q3 | H6: cross-term below single-splash token deviation everywhere | pass (0.19 vs 1.55 at the extreme) |

"Transfer success" was defined as H1 and H2 together, so by the letter it
fails. The substance is one law that transferred as predicted, one that
found its boundary, and one new result.

## Q2: the observation-order law transferred, with four exponents

Predicted `E = O(N^{-(r+1-k)/d})` with `d = 2`: bilinear height -1,
bilinear slope -1/2, bicubic height -2, bicubic slope -3/2. Measured over
the five finest grids: -0.87, -0.40, -1.91, -1.23. Every one within 0.3
of prediction, the lost order between height and slope 0.47 and 0.68, and
the gain from cubic over linear representation 1.04 in height. This was
predicted from vegetation worldlines and interpolation theory before any
water result was seen. It also answers the design question directly: a
water shader that reads normals needs roughly the square of the texture
resolution that a height-only consumer needs at the same tolerance under a
bilinear representation, and a bicubic (or higher-order) representation
buys back more for the normal consumer than for the height consumer.

A note on method: run 1 measured the bilinear slope by central differences
on the fine grid, which smooths the representation's derivative back to
second order and hid the effect entirely (no lost order at all). The
consumer must observe the representation's own derivative, or the test
measures the smoother, not the representation. That is the fourth
theorem-measurement mismatch in this programme, and the second time it was
the derivative operator.

## Q1: the liveness law found its boundary

The count of live splash tokens is monotone in `log(1/eps)` (Spearman
0.99) and matches the exponential prediction at the three loosest
thresholds (6.0 vs 7.0, 11.7 vs 12.5, 18.8 vs 18.6), then saturates near
23 while the prediction keeps climbing to 42. Two things are happening.

First, the fitted water token's envelope is not exponential. The chirp's
amplitude falls with the ring's spreading term `(1 + r / r0)^{-1.32}` at
`r = v tau` and a fitted damping of only 0.05 per second, so its future
envelope decays as a power of time, about `tau^{-1.4}`, and the
"exponential rate" `beta = 0.40` fitted over 1 to 8 s is a local
approximation that under-estimates lifetimes beyond it. A power-law
envelope gives a power-law live count, `M ~ eps^{-1/1.4}`, not a
logarithm. The first review (item 4) flagged exactly this for
polynomially decaying kernels; here it is measured.

Second, the saturation is the finite 20 s window: once tokens outlive the
window, `M` is capped by the number emitted. That is a limit of the
experiment, but it is also the physical statement: with geometric
spreading and weak damping, ripples on a pond effectively never die
within a game-relevant horizon, so token death must come from the
consumer's threshold on amplitude, and that threshold prunes far fewer
tokens than exponential intuition suggests. Pruning at each threshold
behaves as the certificate says (error against the full field falls from
0.40 at the loosest threshold to below 0.001 at the tightest).

Status: the liveness *machinery* transfers (future envelope, threshold,
certificate); the *logarithmic law* belongs to exponentially decaying
tokens and does not transfer to wavefronts with geometric spreading. The
general statement is `M(eps) = R * T(eps)` with `T` the envelope's
inverse; `log` is the exponential case, a power is the spreading case.

## Q3: superposition suffices at game amplitudes, and the nonlinearity is single-cause

Interaction strength `I12` rises monotonically with amplitude at every
separation and falls monotonically with separation at every amplitude.
At base amplitude it is at most 1.3 percent (nearest pair); it crosses 5
percent at four times base for the nearest pair (10 percent) and reaches
19 percent at eight times. Slope interaction is consistently smaller than
height interaction, so the cross-term is long-wave. And in every cell the
cross-term is far below the single splash's own deviation from the
base-scaled token (0.34 to 1.55), which means the nonlinearity mostly
reshapes each splash rather than coupling them: an amplitude-dependent
token shape would recover most of the loss without any pair token, and a
pair token or local simulation is needed only above about four times
base amplitude within about 0.3 m. That is the first quantitative answer
to "when does cause superposition stop being a sufficient representation"
on this teacher.

## Where the programme stands after W1

| law | vegetation | water | status |
|---|---|---|---|
| observation-order exponent `-(r+1-k)/d` | derived from the tangent finding (B4) | confirmed, four exponents | transferred |
| liveness `M ~ log(1/eps)` | confirmed (exponential envelope) | fails; power-law envelope gives a power law | boundary found: decay class of the token |
| superposition of independent causes | not tested | sufficient at game amplitudes; nonlinearity single-cause | new result |
| stops as events; singular structure preserved | confirmed | not applicable | |
| consumer triple (G, d, mu) sets the exponent | B4 | Q2 (k) | reinforced |

Two of three laws behaved as predicted in a different dynamical system,
and the third failed in a way the theory had already flagged and can
state precisely. Four of the five failures in this programme were
theorem-measurement mismatches; two of those were the derivative
operator. The rule for the next teacher is simple: the consumer in the
score must be the exact operator applied to the representation, never a
smoothed proxy.
