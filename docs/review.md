# Review of the "cause → compressed effect → local reconstruction" write-up

Verdict up front: the core idea is sound and worth building. The event/token
model, superposition of decaying kernels, liveness of tokens, consumers that
interpret one token differently, CPU coarse truth + GPU dense reconstruction,
and fitting a cheap grammar to an expensive offline teacher with a cost-aware
objective are all correct in spirit and match how production games already
handle vegetation trails, snow deformation, and water ripples. What follows
is the list of places where the write-up is wrong or incomplete as written,
with the fix for each. The numbered items are ordered by how much they matter.

## 1. The cost claim is wrong as stated

> "simulation cost can scale approximately with active causes rather than
> the number of affected objects"

What actually scales with the number of active causes `m` is **persistent
state and network bandwidth**. Per-frame **evaluation** of a token
superposition is `O(N × m_local)`: every reconstructed object evaluates every
token in range. On the GPU the `N` is parallel, so the wall-clock cost per
vertex is `O(m_local)`, and that must be bounded (8 to 16 tokens per vertex is
a practical cap). Two ways to bound it:

- Bake tokens into the Level-1 coarse field once per frame, cost
  `O(m × cells_in_radius)`, then have dense objects sample the field, cost
  `O(N)` with one bilinear fetch. This is the right path for wide, smooth
  effects (wind gusts, panic fields, wide wakes).
- Keep a small per-cell token list (a spatial hash of live tokens) and let
  dense objects evaluate only the nearest few tokens. This is the right path
  for narrow features (a 0.3 m trail on a 30 m field) that a coarse grid blurs.

The proof of concept measures the blur: see `poc/results/summary.md`,
section "Coarse-field bake".

## 2. The wave packet formula is non-causal and has no geometric spreading

> `h(x,t) = Σ A_j e^{-λ_j(t-t_j)} cos(k_j‖x-p_j‖ - ω_j(t-t_j) + φ_j)`

As written, `cos(k r - ω τ)` is non-zero everywhere the instant the token is
created, so a splash ripples the entire pond at `τ = 0`. Circular waves in a
2-D surface also lose amplitude roughly as `1/√r`. Use a ring envelope
travelling at the phase speed and a spreading factor:

```
h = Σ A_j e^{-λ_j τ} · exp(-(r - v_j τ)² / 2w_j²) · cos(k_j (r - v_j τ)) / sqrt(1 + r / r0)
```

The same problem applies to the vegetation `b_wave = C e^{-γt} sin(kr - ωt)`.
`RingWave` in `poc/reactive/primitives.py` is the corrected form, with a test
that nothing moves ahead of the front.

## 3. The wake must be one-sided and anchored to the path, not to the mover

> `b_wake = B e^{-d⊥²/2w²} e^{-d∥/ℓ}`

Needs `d∥ ≥ 0` (only behind the mover) and, for a player who turns, `d⊥` and
`d∥` must be measured against the travelled polyline, not the current heading.
That is the snow "track spline" token from later in the write-up; use it for
grass too. In the proof of concept the wake and crush primitives take the
banked polyline with pass times and are zero before the player arrives.

## 4. The capability check is instantaneous, but a capability is about the future

> "simplification is safe if `G_i(X') ≈ G_i(X)`"

If `G_i` is evaluated on the current state, it cannot see what the state will
still cause later. Define each capability on a rollout: `G_i(X) =
observable_i(rollout(X, u_{t:t+H}))` over horizon `H` under the expected
inputs. Because tokens carry their own time envelope, this collapses to a
cheap test: a token is dead for consumer `i` once the remaining integral of
its envelope, weighted by consumer `i`'s sensitivity, is below `ε_i`.

Also, per-token thresholds do not bound the total error. Dropping 200 tokens
that are each just under `ε` can move the field by `200 ε`. Keep a global
budget: drop the smallest tokens until the sum of dropped amplitudes in a
cell hits the budget, then stop.

## 5. "Consumed by the monster ⇒ dead" only holds with one consumer instance

With several monsters, late-spawned consumers, or a consumer that was out of
range, consumption is not death. Kill tokens by time envelope and amplitude,
and treat consumption as a per-consumer-class counter that can shorten but
never extend the lifetime. This matters for determinism too: if death depends
on who happened to query, two clients disagree on the live set.

## 6. The per-stalk integrated spring breaks determinism and replay

> "the stalk itself only needs `(b_x, b_z, v_x, v_z)`"

Integrating a spring per frame on the GPU is frame-rate dependent: a Quest at
72 Hz and a PC at 120 Hz diverge, and a replay from tokens does not reproduce
the recording. The fix is to make dense reconstruction **stateless**: the
response of a damped spring to an exponentially decaying push has a closed
form,

```
c = 2ζ√k,  ω = √k·√(1-ζ²),  a = λ - c/2,  P = k / (a² + ω²)
b(τ) = A · P · [ e^{-λτ} - e^{-cτ/2} ( cos ωτ - (a/ω) sin ωτ ) ]      (τ ≥ 0)
```

which is about 12 operations, keeps the overshoot and ring-down that make a
spring look like a spring, and makes `b_i(t)` a pure function of
`(tokens, p_i, t, seed)`. `spring_response` in the proof of concept
implements this and is tested against an RK4 integration. Keep integrated
per-object state only where genuine history matters (a hand actively holding
a stalk), and keep that state off the gameplay-truth path.

A consequence: the "rollout error" worry (`E_60`, `E_600`) in the second half
of the write-up only applies if you choose the recursive `x̂_{t+1} =
F̂(x̂_t, u_t)` form. The stateless token form has zero drift by construction.
Its failure mode is different: token count growth, which liveness bounds.

## 7. A linear coupled-spring teacher is too easy a test

> `m ẍ_i + c ẋ_i + k x_i + Σ_j k_ij (x_i - x_j) = F_i(t)`

That system is linear, so its response to any input is exactly a sum of
Green's functions. A search over decaying kernels will succeed on it almost
by definition and tell you little. The teacher in the proof of concept adds
the nonlinear parts that matter in a game: penalty contact between the stalk
tip and a moving cylinder, stiffening at large bend, drag along the mover's
velocity, and plastic crush with hysteresis. Those are exactly the effects
that superposition cannot represent, so they are the fair test.

## 8. Superposition needs at least one nonlinear op in the grammar

Crush, saturation, and "the blade cannot bend past 90°" are not additive.
The grammar needs unary post-ops (soft clamp, max, hysteresis-as-token).
`Saturate` is included as a compositional wrapper.

## 9. State-space RMS is the wrong visual metric

Fitting on raw per-stalk RMS makes the search chase a 0.3-second pulse on the
few dozen stalks under the player's feet, where a 50 ms timing error is a
large numerical error and an invisible visual one. The proof of concept
reports both the raw error and a time-smoothed one. For the real thing, use a
screen-space, distance-weighted metric (project bend to the headset view,
weight by 1/distance², compare after a short temporal blur), and a separate
gameplay metric per consumer (the trail IoU in the proof of concept is the
"monster can find the trail" capability).

## 10. Runtime cost is not additive across primitives, and flops are not ms

On Quest the real costs are register pressure and branching in the vegetation
shader, uniform/structured buffer size per draw, and CPU time for the
token→field bake, not summed flops. Use summed primitive costs only as the
search heuristic (that is what the proof of concept does), then profile the
composed shader on device with OVR Metrics Tool / RenderDoc for Quest, and
feed the measured ms back as the cost term. Benchmark compositions, not
primitives.

## 11. Coarse field resolution versus feature size

A 32×32 field over a 30 m patch is a ~1 m cell. A 0.3 m trail is sub-cell,
so a field-only path blurs it. The proof of concept quantifies this; the
answer is: AI and audio queries are fine from the coarse field, visuals of
narrow features must sample tokens directly or use a small high-resolution
window that follows the player (a 2-level clip map).

## 12. Networking details that the write-up skips

Tokens are idempotent and tiny, which is the good part. You still need a
shared clock for `t_0` (otherwise envelopes are out of phase between
clients), a "live token set" snapshot for late joiners, and a rule that the
server decides token death (or every client applies the same deterministic
rule) so the live sets do not diverge.

## 13. The "extract τ_AI and keep X' + τ_AI" rule is right

That is a sufficient statistic for the consumer. Two notes: it must be
computed once, at the moment of simplification, from the detailed state you
are about to discard; and the token type should be owned by the consumer
that needs it (the AI system defines `τ_AI`, not the vegetation system).

## What the proof of concept says about the central claim

Numbers from the last full run are in `poc/results/summary.md`; the picture
is `poc/results/comparison.png`. The qualitative findings held across three
runs (two at 576 stalks, one at 1600) and a separate probe that swapped the
Powell optimiser for differential evolution:

1. **The grammar reproduces what a consumer sees, not what the simulator
   stores.** Raw per-stalk state error bottoms out at 0.39 relative RMS on
   the 1600-stalk run (0.6 on the coarser 576-stalk runs) no matter how the
   parameters are searched: differential evolution found the same floor as
   Powell, so the model family is the limit, not the search. Meanwhile the
   16×16 coarse field an AI would query has 0.22 error with 0.98
   correlation in the persistence phase, and the mean trail profile versus
   distance from the path matches within about 10% in every band. The residual is per-stalk scatter from the teacher's
   threshold-based contact and crush (which stalk got clipped by the
   cylinder's edge, whether it crossed the crush threshold). That scatter is
   exactly what the write-up says to regenerate from a seed rather than
   store, and it is not something a smooth kernel can or should fit.

2. **The error metric decides what the search discovers.** Fit on raw
   state RMS and the search hedges: it widens the pulse in time to cover
   per-stalk timing differences, and lowers its peak. A 150 ms temporal
   smoothing barely helps because the mismatch is spatial as much as
   temporal. The metric has to be the consumer's metric (see item 9).

3. **Where the energy is.** 84% of all bend energy is in stalks within
   0.25 m of the path and 99% within 1 m. Neighbour coupling in this
   teacher spreads very little. That is why the banked-path primitives
   (wake, crush) win the greedy search and the per-event ones (radial
   impulse, ring wave) add almost nothing: for a walking player the path
   *is* the cause, and 0.5 m stride events are a worse description of it.
   The write-up's `c_stomp` tokens are the right shape for discrete
   impacts, not for locomotion.

4. **A sharper-than-Gaussian kernel fits contact better.** Letting the
   spatial kernel shape vary (generalised Gaussian `exp(-½(d/w)^q)`), the
   fit pushes `q` toward 1 (exponential), meaning a narrow peak with a
   heavier tail than a Gaussian. Cheap to add (one `pow`), worth having in
   the grammar.

5. **The coarse field blurs narrow features as predicted.** Baking the
   model to a 16×16 field over 10 m (0.6 m cells) and sampling back raises
   the error from 0.39 to 0.61; 32×32 (0.3 m cells) gives 0.44 at lower
   cost than direct evaluation for 1600 stalks; 64×64 gives 0.42 at nearly
   three times the direct cost. The two-level plan (coarse field for
   AI/audio, direct tokens or a local clip map for visuals) is the right
   one, and the crossover depends on stalk density versus token count.

6. **The compression is real.** Banked causes are a few hundred floats;
   the equivalent per-stalk state is thousands, and the teacher needs
   substepped, neighbour-coupled integration that has no stateless GPU
   form at all. The cheap model is roughly 124 ops per stalk per frame with
   no neighbour reads and no state, versus roughly 320 for the teacher plus
   four neighbour reads per substep. Six hundred and ninety-three banked
   floats stand in for 6400 floats of per-stalk state.

What this does *not* show yet: generalisation to a held-out walk, real
player inputs, or any measured Quest cost. Those are the next three steps
in the README.
