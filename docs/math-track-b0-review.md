# Review of Math Track B0: the behavioural pseudometric and what is built on it

Each item is tagged **Definition**, **Result** (proved as stated),
**Conditional** (true under stated extra conditions), **Claim** (asserted,
not proved), or **Prediction** (testable). The two changes that matter most
are at the top.

## The two things to fix before building on it

### A. The pseudometric must live on behaviours, not on states of one system

Items 10, 12 and 15 compare a teacher state with a state of a *different*
system (the token model, the grid, the shader). `D_H` as defined takes two
states of the same `F`. Fix: define the behaviour of a (system, state,
consumer-set) triple as the map

```
B(x) : u -> ( G_i(Phi_t(x, u)) )_{i, t <= H}
```

and put the pseudometric on behaviours:

```
D_H(B, B') = sup_u  sum_t gamma^t  sum_i w_i  d_i( B(u)_{i,t}, B'(u)_{i,t} ).
```

Everything in the track then goes through verbatim, and a shader
approximation (a change of `G_i`, not of state) is comparable in the same
space. Items 10 to 16 are correct once read this way; as written they are
not well-typed.

### B. The supremum over inputs makes the quotient nearly trivial for a renderer

With `sup` over all input sequences and a renderer consumer that can look
anywhere, two states that differ in one stalk are distinguishable: walk up
and look. So `D_H > 0` for almost every pair, `Q_H` is barely smaller than
`X`, `N_H(eps)` is enormous, and the "knee" in item 17 sits at microscopic
resolution for every representation. This is exactly what the proof of
concept measured: per-stalk error floors at 0.39 for all six grammars
while the coarse consumer error was 0.22 with correlation 0.98.

Two consistent ways out, and the track should pick one explicitly:

1. **Expectation version.** `D_H^pi = E_{u ~ pi}[...]` with `pi` the
   recorded player-input distribution. Still a pseudometric (expectation of
   pseudometrics). The proof of concept's numbers are estimates of this
   object, on one training and one held-out trajectory.
2. **Sup version with honest consumers.** Keep `sup`, but make `G_visual`
   the actual perceptual channel: screen-space projection at headset
   resolution, distance-weighted, with a short temporal blur. Then a
   differing stalk 15 m away genuinely is not distinguishable, and the
   quotient is non-trivial.

The certificates in items 4 to 6 are `sup`-type bounds on single tokens and
are fine either way. The covering-number and knee statements are only
meaningful under one of the two choices above.

## Item by item

**B0, definition of `D_H`.** Definition. Needs one condition to be
real-valued: bounded consumer outputs or a compact input set, otherwise the
`sup` can be infinite. With `gamma < 1` and bounded per-step differences,
`H = infinity` is also finite.

**B0, "D_H is a pseudometric".** Result, given finiteness. Non-negativity
and symmetry are immediate; the triangle inequality follows from the
pointwise one plus `sup(a + b) <= sup a + sup b`. Correct.

**1, exact equivalence and quotient.** Result: the kernel of a pseudometric
is an equivalence relation and `X / ~_H` is a metric space. Two caveats
the track should state. First, `~_H` depends on `H`, on the consumer set,
and on the input set. Second, with finite `H`, `~_H` is **not a
congruence for `F`**: `x ~_H x'` only gives `F(x,u) ~_{H-1} F(x',u)`. So
`F` does not descend to `Q_H` and "the game operates on `Q_H`" is not
justified for finite `H`. It is justified for `H = infinity` with
`gamma < 1`, where `D` satisfies the fixed-point recursion

```
D(x, x') = max_u [ sum_i w_i d_i(G_i x, G_i x') + gamma D(F(x,u), F(x',u)) ]
```

and is a bisimulation pseudometric. This object already exists under that
name (Ferns, Panangaden and Precup, 2004, for MDPs); the recursion is what
makes it computable on finite abstractions. Worth citing and using.

**2, approximate equivalence is not transitive.** Result. Correct, and the
notation `approx_{eps,H}` is the right one.

**3, coverings and the bit bound.** Definition plus Result. `B >= log2
N_H(eps)` is correct *provided* the codewords are reconstructions in the
same behaviour space and `N_H` is the minimal cover size: any code whose
decodings are within `eps` of every state is itself an `eps`-cover. Note
this bounds *state encoding*, not runtime cost, and is only informative
under fix B.

**4, causal cones.** Conditional. The algebra is right given the exponential
bounds. Three conditions from the kernels we actually fitted:
- The spring envelope is not monotone in `tau` (it rises, overshoots,
  rings). A bound `|K_t| <= C e^{-lambda' tau}` holds with `lambda' = min(lam,
  c/2)` and `C >= 1`, so the death time uses the slower rate.
- The generalised Gaussian satisfies an exponential bound only for
  `q >= 1`. Our fits gave `q` of 1.2 to 1.4. If a fit ever wants `q < 1`
  the cone is polynomial, not exponential.
- The water chirp decays only polynomially in `r` and its front *expands*:
  a point can be outside a token's influence now and inside it later. The
  bound as written still holds, but "dead at this point now" is not "dead
  at this point". Liveness must be taken as a sup over the remaining
  horizon at the consumer's location, which is the future-not-instant
  caveat from the first review, now in the math.

**5, consumer sensitivity.** Conditional on Lipschitz consumers. Correct.
`r_i` must be the distance from the token to the *nearest* point the
consumer observes, and the norm in the Lipschitz condition must match the
norm the kernel bound is in.

**6, accumulation certificate.** Result. Correct and conservative (it sums
magnitudes; cancellation can only help). A `tanh` saturation is 1-Lipschitz
so the certificate survives the post-op. This is deployable as written.

**7, live-token scaling `M_eps ~ (R / lambda) log(A / eps)`.** Conditional.
Correct for emission at bounded rate and exponential temporal decay. Two
refinements. The quantity that costs GPU time is evaluations per vertex,
which is `M_eps` times the footprint fraction; with a Gaussian footprint
that fraction also grows like `log(A/eps)`, so evaluations per vertex grow
roughly like `log^2(1/eps)`. With the chirp's polynomial spatial decay the
footprint grows polynomially in `1/eps`. Both are cheap to measure: the
proof of concept already counts live tokens against a threshold.

**8, path compression.** Result for uniform sampling of a bounded-curvature
curve: the sagitta bound `delta <= kappa l^2 / 8` and `N = O(L
sqrt(kappa/delta))` are standard, and the optimal adaptive version has
segment density proportional to `sqrt(kappa(s))`. Conditional on the
consumer being Lipschitz in geometric deviation, `N ~ eps^{-1/2}`. One
omission: the path token also carries pass times, and the wake envelope is
sharp in time (fitted lead 0.14 s), so timing interpolation error needs its
own term in the budget when the walker's speed varies.

**9, sensitivity-adaptive resolution.** Claim, plausible. For `q -> 1` the
kernel's gradient at `d = 0` is finite rather than zero, so near-trail
geometry matters more. `delta(s) ~ eps / |grad K|` is the usual error
equidistribution heuristic; note the gradient depends on the consumer's
distance from the path, not on `s` alone.

**10, exact capability banking.** Definition presented as a theorem. Once
`D_H` lives on behaviours (fix A), "outputs match exactly for all `u`, `t
<= H`" *is* `D_H = 0`; there is nothing to prove. The content is in
constructing `tau`, and the conclusion holds only relative to `H`, the
consumer set, and the input set.

**11, approximate banking.** Result. Summing uniform per-step bounds is
valid. Correct.

**12, composition.** Result by the triangle inequality, on behaviours.
Correct and useful. Conservative: stage errors need not add.

**13 and 14, budget allocation.** Result for convex differentiable cost
curves; the equal-marginal-cost condition is the KKT condition. Real cost
curves are discrete and non-convex (a grid goes 32 to 64), so in practice
this is a knapsack solved greedily on measured curves, which is what the
sweep in `poc/gpu_sweep.py` already produces for two of the stages.

**15, executable complexity `C*(eps)`.** Definition. Needs the behaviour
pseudometric, a stated initial-state set, and a stated cost model
(operation counts now, milliseconds later). It is a rate-distortion curve
with computation in place of rate. For the *linear* part of any teacher
this curve is already known: balanced truncation gives model order versus
error with the certificate `error <= 2 sum of discarded Hankel singular
values`. So for the vegetation lattice, existence is settled in closed form
and the interesting part of `C*` is entirely the nonlinear contact and
crush. That supports prediction 17 directly.

**16, search regret.** Definition. The probe in the proof of concept
(differential evolution reached the same floor as Powell) is an empirical
estimate that regret was small and the family was the limit, which is the
distinction this item makes formal.

**17, three regimes and a knee.** Prediction. Consistent with what was
measured: at loose tolerance the wake alone (26 ops, 0.42) is as good as
six terms (124 ops, 0.39), so cost is flat there; below 0.39 per-stalk,
nothing in the grammar helps and the next step up is the teacher itself,
which is the knee. The 576-stalk runs floored at 0.6, so the knee's
position depends on stalk density relative to contact radius, and it is a
different knee per consumer: the coarse AI consumer reaches its tolerance
far cheaper than the visual one. `C*` is really a vector of curves, one
per consumer, or one curve per weighting `w_i`.

**18, the experiment.** Well posed and almost entirely runnable with the
existing code, once the sup-versus-expectation choice is made (fix B). The
six representations map onto existing paths: field-only is the bake at
grid `G`, path-only is the wake, path plus local kernels is wake plus
presence, path plus event residuals adds the radial impulse, the field
sweep exists, the full grammar exists. The three predictions map to three
sweeps: live-token count against the liveness threshold (prediction 1),
path point count against a polyline tolerance (prediction 2), and the
lower envelope of cost against error across representations, per consumer
(prediction 3). Add the held-out walk to every point. Estimated compute is
under an hour on the current teacher.

## Summary of status

| item | status |
|---|---|
| D_H is a pseudometric | result (needs finiteness) |
| quotient Q_H | result; not a dynamical system for finite H |
| approximate relation not transitive | result |
| bit lower bound via covering number | result; informative only under fix B |
| causal cones, consumer death, global certificate | results under exponential kernel bounds; expanding-front kernels need the sup over remaining horizon |
| log(1/eps) live tokens, eps^{-1/2} path points | conditional scaling laws, testable now |
| exact banking theorem | definition once D_H is on behaviours |
| approximate banking, composition, budget | results on behaviours |
| C*(eps), regret | definitions; linear part already solved by balanced truncation |
| knee | prediction, partially supported by existing runs |

## Results of the item-18 sweep (`poc/knee_experiment.py`, `poc/results/knee.md`, `knee.png`)

Convention used: expectation over recorded inputs (training and held-out
walks averaged). Held-out numbers track training within 0.01 everywhere,
so nothing below is a fit to one walk.

**Prediction 3, the knee: confirmed, and it is consumer-specific.** The
visual envelope runs 14 ops at 0.84, 26 ops at 0.42 (wake only), 48 ops at
0.40 (wake + presence), 76 ops at 0.39, 124 ops at 0.39 (six terms), then
the teacher at 320 ops and 0. Between 26 and 124 ops the error moves by
0.04 while cost rises almost fivefold; the grammar is exhausted there and
the next available point is the microscopic simulation. That flat stretch
followed by the jump is the knee, at roughly 26 to 48 ops. The AI-field
consumer has the same shape with its knee at the same cost. The gameplay
consumer (can the trail be found) saturates at the 16x16 field, 20 ops,
error 0.04; everything above that is indistinguishable to it. So `C*(eps)`
is a different curve per consumer, as the review argued, and the cheapest
representation that satisfies all three is the wake alone at 26 ops
unless the visual tolerance is tighter than 0.42, in which case nothing
short of the teacher helps.

One detail worth keeping: the baked field at 64x64 is worse than at 40x40
(0.42 versus 0.40) and three times the cost, because bilinear sampling of
a kernel with `q` near 1 is not monotone in resolution. Cost curves are
not convex, which is why the budget allocation of items 13 and 14 has to
be run as a discrete greedy on measured points, not as a derivative
condition.

**Prediction 1, live tokens grow like log(1/eps): confirmed in shape, with
the deviation the review predicted.** Live radial-impulse tokens per frame
rise linearly in `log(1/eps)` from 0.8 at `eps = 0.3` to 3.2 at `eps =
1e-5`. Measured slope 0.24 against the predicted `R / lambda'` of 0.32.
The shortfall and the visible step between `eps = 1e-3` and `3e-4` are
the ring-down lobes of the spring envelope: a non-monotone kernel crosses
`eps` several times, so whole lobes switch on at once as `eps` drops. The
bound in item 4 is an upper bound and holds; the equality-style scaling
law needs a monotone envelope constant `C` in front. Pruning at any of
these thresholds changed visual error by under 0.001, consistent with
part A: for a walking player the radial tokens carry almost nothing.

**Prediction 2, path points grow like eps^{-1/2}: half confirmed.** Points
kept by Douglas-Peucker scale as `tol^-0.44` against the predicted
`tol^-0.5`. Excess visual error scales as `tol^0.60`, not the `tol^1` a
Lipschitz consumer would give. So in terms of error the point count grows
like `eps^-0.73`, steeper than predicted. The cause is the timing term the
track omitted: the simplified polyline interpolates pass times linearly
between kept vertices, the walker's speed varies, and the wake envelope
has a 0.14 s lead and a sharp rise, so timing error decays more slowly
than geometric error as the tolerance shrinks. Item 8 needs a time
tolerance alongside the geometric one; with it, the geometric law should
recover its exponent. Practical note: 48 Douglas-Peucker points are
within 0.011 of the 201-point uniform 20 Hz path, so the banked path can
be a quarter of its current size.

**Status after the sweep.**

| prediction | outcome |
|---|---|
| knee where microscopic contact becomes distinguishable | confirmed, at 26 to 48 ops for visual, 20 ops for gameplay |
| live tokens ~ log(1/eps) | confirmed in form; slope 25% under prediction due to ring-down lobes |
| path points ~ eps^{-1/2} | geometric half confirmed (exponent -0.44); error half sub-linear (0.60) because of pass-time interpolation |
| held-out generalisation of the envelope | confirmed, within 0.01 |

## Review of the follow-up track (expectation metric, spacetime path law, knees)

**1, expectation pseudometric `D_{H,mu}`.** Definition, and a Result that it
is a pseudometric (expectation of pseudometrics, given integrability). Two
notions, expected and worst-case, is the right split. Still to be stated:
it lives on behaviours (fix A above), and `mu` must be a distribution over
input *sequences* of length `H`, so it is a distribution over player
trajectories, not over single inputs.

**2, liveness with the monotone future envelope.** Result. `K-bar(tau) =
sup_{s >= tau} |K(s)|` is monotone by construction, and for the closed-form
spring `|K| <= P (e^{-lam tau} + sqrt(1 + (a/omega)^2) e^{-c tau / 2})`,
so `K-bar <= C_s e^{-beta tau}` with `beta = min(lam, c/2)`. There is no
resonant case for real `lam`: the denominator `a^2 + omega^2` is always
positive. `C_s` is computable as `max_tau K-bar(tau) e^{beta tau}`; the
experiment below measures it. One caution: the count the earlier sweep
reported used instantaneous magnitude, which *undercounts* relative to
`K-bar`; the theorem bounds the `K-bar` count, so the comparison in the
earlier sweep was between a lower quantity and an upper bound. The rerun
below counts with `K-bar`.

**3 and 4, spacetime path and `E <= L_x delta_x + L_t delta_t`.** Result,
given the kernel is Lipschitz in both arguments. It is: the spring envelope
starts with zero slope (`b'(0) = 0`), so the causal onset is `C^1`, and the
generalised Gaussian with `q > 1` is `C^1` at `d = 0`. With `q = 1` there
is a kink with finite one-sided slope, still Lipschitz. `q < 1` would not
be, which the fits never asked for.

**5, corrected compression law.** Conditional, and the condition fails
where it matters. `t''(s)` with arc-length `s` is `-v'(s) / v(s)^3`, which
is unbounded wherever the walker stops, and both walks end in a stop. The
fix is to parametrise by time: with vertices `(p_k, t_k)` and `p` linear in
`t` on each segment, the nearest-point fraction along the chord equals the
time fraction exactly, so timing is exact for the polyline's own motion and
the only chord error is `|p''(t)| Delta t^2 / 8`, bounded by acceleration.
Then `N = O(eps^{-1/2})` returns with `K_t` replaced by acceleration and no
blow-up. This is what the 3-D Douglas-Peucker on `(x, y, c_t t)` computes.

**6, density proportional to `sqrt(q(s))`.** Result (standard error
equidistribution). Douglas-Peucker on the spacetime curve realises it
implicitly; `L_x` and `L_t` enter only through the ratio `c_t = L_t / L_x`
that scales the time axis. That ratio is the whole content of "behaviour
weighting" when the consumer's sensitivity is uniform along the path,
which it is for a uniform field. It becomes a genuinely different
compressor only when sensitivity varies along the path (stalks near the
player's view, a consumer that only looks at part of the field).

**7 and 8, the knee as marginal efficiency, discrete allocation.**
Definitions, both right. The multiple-choice knapsack is solvable by
enumeration at game scale.

**9 to 11, per-consumer representations, the DAG, compressibility ratios.**
Definitions. The "architecture theorem" is a tautology as stated (separate
is optimal when it is cheaper), but the quotient framing gives it content:
the minimal object is a shared causal core plus consumer-specific
sufficient statistics, and the sweep shows the gameplay statistic saturates
at a fifth of the visual one's cost. `chi` depends on the cost model; state
which one.

**12.** Agreed, including the caveat: two walks from one teacher.

## Results of the preregistered path-compression experiment (`poc/path_compression.py`, `poc/results/path_compression.md`, `.png`)

Prediction stated before the run: at equal point counts on the held-out
walk, behaviour-weighted < spacetime < spatial, most clearly at the wake
front, and the points-versus-error exponent moves from -0.73 toward -0.5.
Reference for "excess error" is the dense 200 Hz path used directly as the
token. Kernel slopes from the fitted wake: `L_x = 3.23` per m, `L_t = 4.62`
per s, so `c_t = L_t / L_x = 1.43` m/s; mean walking speed 1.63 m/s.

**Spacetime versus spatial: confirmed, strongly.** On the held-out walk the
spacetime compressor is below the spatial one at every point count, by
about tenfold from 10 points up (excess 0.0067 against 0.065 at 10 points,
all frames; 0.016 against 0.078 at the wake front). It reaches the dense
reference at about 20 points, where the spatial one still carries 0.025
and has not reached it at 48. The 201-point banked path can therefore be
about 20 spacetime vertices with no measurable loss. This is the timing
term made visible: the same geometric budget spent on where the walker
slows and turns, not only on where the path bends.

**Behaviour-weighted versus spacetime: not established.** The two curves
overlap. The strict ordering held at 5 of 9 point counts on all frames and
5 of 9 at the front, which is chance. The reason is structural, not a
failure of the idea: with uniform consumer sensitivity along the path, the
only difference between the two methods is the time scale, and the
kernel-derived `c_t` of 1.43 m/s is within 15% of the walking speed. A
real test needs either a walk whose speed is far from `L_t / L_x` or a
consumer whose sensitivity varies along the path (a view frustum, a
partial field). Until then, item 6 stays a Result about density but the
*named* compressor is not yet distinguishable from spacetime DP.

**The exponent: overshoot, and the measurement is floor-limited.** Points
against excess error now fit -0.33 (spacetime) and -0.30 (behaviour),
against -0.68 for spatial. The correction therefore moved the exponent
past -0.5, but the fit is not trustworthy: the spacetime compressor
reaches the reference floor at about 20 points, so between "too coarse"
(5 points) and "at the floor" there are only three or four usable points,
and several of them sit within noise of zero excess. There is no
asymptotic range in this data. Verdict: inconclusive rather than failed.
To measure the exponent, the walk needs more curvature and speed
variation (a longer, wandering walk with several stops), or the reference
needs to be the true continuous motion rather than a 200 Hz polyline.

**Caveat found on the training walk.** At very coarse budgets (5 to 8
points) the spatial compressor beats the spacetime one on the training
S-curve, because the spacetime method spends scarce points on the start
and stop ramps while the S-curve's error is mostly geometric. From 10
points up the ordering is the predicted one on both walks. So the
allocation between geometry and timing at tiny budgets is walk-dependent,
which is exactly what a walk-dependent `q(s)` in item 6 says.

**Corrected liveness bound: holds.** Counting live tokens with the
monotone future envelope `sup_{s >= tau} |K(s)|` and comparing with
`(R / beta) log(C_s / eps)` at `beta = 9.33` and the measured `C_s =
10.6`: the count is below the bound at every threshold, by a factor of
about 1.5, and the log form is visible across four decades. The steps
remain, because the future envelope is flat across each ring-down lobe.
Theorem as restated in item 2 is consistent with the data.

**Status after this experiment.**

| claim | outcome |
|---|---|
| spacetime path compression beats spatial at equal N (held-out) | confirmed, about tenfold from 10 points up |
| behaviour weighting beats plain spacetime | not established; the two time scales nearly coincide here |
| corrected exponent returns to -1/2 | inconclusive; compressor reaches the floor before an asymptotic range exists |
| monotone-envelope liveness bound | holds with a 1.5x margin, log form confirmed |
| practical: banked path size | 201 uniform points can be about 20 spacetime vertices |
