# Math Track B4 results: the corner law under the local supremum

Preregistration and amendments: `docs/math-track-b4-prereg.md`. Raw outputs:
`poc/results/b4.md`, `b4.json`, `b4.png`, `b4_run3.log`. Runs 1 and 2 are
kept (`b4_run1.*`, `b4_run2_partial.log`); run 3 is the judged run.

## Verdict by the frozen rules: H0 fails by the letter, so the corner law is closed

| test | result |
|---|---|
| H0 transfer invariance (sup, all four lengths within 1.5x) | pass at 4.84 mm (ratio 1.14); fail at 9.68 (1.61), 19.35 (2.33), 38.70 (2.33) |
| H0 dilution control (RMS ratio 32 m / 4 m >= 1.5 at primaries) | fails, and with the *opposite* sign: 0.23 and 0.20 |
| H1 ranking at 19.35 mm | rho model 0.83, turning 0.99: fail |
| H1 at 9.68 mm (other primary) | void: slalom never reaches 9.68 mm in the sweep |
| H2 residuals at 19.35 mm | zigzag 0.10, stop/start 0.29: pass |
| H3 at 38.70 mm | rho 0.77, turning 0.93: fail |
| H4 corner-bin excess at 19.35 mm | 8 of 8 corner bins: pass |

Outcome rule: "H0 fails: stop rescuing the corner theory." Applied.

## What H0 actually shows

The corner's vertex cost is *identical* for 4, 8 and 16 m of surrounding
path at every threshold: 21/21/21 at the two loose thresholds, 45/45/41
at 9.68 mm, 58/62/64 at 4.84 mm. The supremum score is local, as
intended. The 32 m probe is the outlier in both directions (66 where the
others need 45; 9 where the others need 21). Its maximum against
tolerance is non-monotone (a chord that happens to align with the
near-apex tangent at one coarse tolerance), and `N(eps)` takes the
minimum, so a single lucky or unlucky placement moves it. That is
measurement noise of the strict maximum, but the rule was written for all
four lengths and it is failed.

## A correction to B3's diagnosis

B3 attributed its corner over-prediction to RMS dilution: the isolated
probe's corner was said to need *more* vertices because its error was
spread over a long path. The RMS control here shows the sign is the other
way. Under a global RMS score, a longer surrounding path makes an isolated
corner *cheaper* (21 vertices at 4 m, 5 at 32 m), because the same local
error contributes less to the global average. Dilution therefore cannot
explain why B3's 8 m probe needed 27 vertices per corner while the zigzag
needed about 9. That discrepancy is unexplained and is recorded as such.
The "mathematically convincing" dilution argument in the previous track
message was accepted too quickly by both of us.

## What the run found instead, and it is the useful part

Run 1's failure on the slalom and the corner probes led to three checks.
The on-path sign flip was real and is fixed (Amendment 2). The medial-axis
pass-time ambiguity was real but minor (Amendment 3, a few dozen stalks).
The dominant effect was neither: stalks just outside a corner's apex agree
on distance and pass time to a millimetre and 10 ms between tokens, but
their outward normal differs by about 20 degrees, because the wake's
direction is taken from the local tangent of the nearest segment, and a
chord's tangent error is first order in chord length while its position
error is second order.

So the consumer depends on the path's tangent, not only its position. For
a tangent-dependent consumer the vertex count needed to hold the tangent
error below `dtheta` along a curve is

```
N ~ (total turning) / (2 dtheta),     dtheta ~ eps / (B (1 - mix)),
```

so `N ~ turning / eps` at tight tolerance, against `N ~ C_smooth /
sqrt(eps)` for the position term. That is why total turning has ranked
best at tight tolerance in every experiment since B2, and why it is not a
rival heuristic but the derived complexity of the tangent term.

The prediction that separates the two mechanisms is the exponent of the
best achievable sup error against vertex count: -2 where position limits,
-1 where the tangent limits. Post hoc, from run 3's sweeps (best error at
or below each N, upper half of the sweep):

| trajectory | exponent | regime |
|---|---|---|
| straight | -3.2 | position |
| tangential probe | -1.8 | position |
| s_curve | -0.96 | tangent |
| circle | -1.12 | tangent |
| slalom | -0.69 | tangent |
| wandering | -0.92 | tangent |
| zigzag | -1.74 | position |
| corner probe (8 m) | -3.1 | position |

Straight and speed-only paths are position-limited. Continuously curving
paths are tangent-limited. Sharp corners are *position*-limited: a 0.15 s
corner is resolved by a handful of vertices, after which the remaining
error lives on the straight legs. So the expensive object at tight
tolerance is not the corner but sustained curvature, which is exactly the
slalom, under-predicted 3.5 to 1 by a law that had a corner term and no
tangent term.

## Where path complexity stands after B2 to B4

- **Loose tolerance (perceptual, RMS-like):** the anisotropic smooth law
  `integral (m_par a_par^2 + a_perp^2)^(1/4) dt` ranks trajectories at 0.94
  to 0.95 and beats every baseline. Established provisionally, with
  `m_par` small (0.01 to 0.02) and not yet precisely measured.
- **Tight tolerance (certificate, sup-like):** for this consumer the
  representation is governed by total turning with an `eps^-1` law,
  because the consumer reads the tangent. Derived and consistent with the
  measured exponents; the constant has not been calibrated.
- **Stops** are events, not geometry (B2 Amendment 1), and **on-path** and
  **medial-axis** stalks are non-Lipschitz points of this consumer
  (Amendments 2 and 3).
- **Corners** as a separate singular term: closed. Under the certificate
  score they are cheap; under the perceptual score they were mis-diagnosed.
- **The consumer triple** `(G, d, mu)` matters as much as the geometry: the
  same six trajectories rank differently under RMS and sup, and the
  tangent dependence of `G` changes the exponent.

## Recommendation

As agreed before the run: no B5 on corners. The two remaining questions
on this teacher are small and can wait: calibrate the tangent-term
constant, and measure `m_par` with a longer tangential probe. The larger
move is the one the track named: switch teachers. Water is the natural
next one, because the ring token is a wavefront, the third causal geometry
in the taxonomy, and its consumer (surface height and slope) has no
tangent lookup to confound the certificate score.
