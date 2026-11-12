# Quest notes: getting the bend cost off the GPU

Numbers below come from `poc/results/gpu_sweep.md` (trail model) and
`poc/results/wind.md` (wind). The reference shader code is in `unity/`.

## 1. Ship two terms

| model | per-stalk error | coarse-field error | late-field correlation | ops per evaluation |
|---|---|---|---|---|
| six terms as discovered | 0.39 | 0.22 | 0.98 | 124 |
| wake + presence | 0.40 | 0.25 | 0.98 | 48 |
| wake only | 0.42 | 0.26 | 0.98 | 26 |

Held-out walk gives the same picture. The path wake with the closed-form
spring envelope is the whole trail; presence is the live push under the
walker's feet. Crush, radial impulse, ring wave and saturate add nothing
you can see for a walking player. Keep the per-event tokens for things that
actually are events (a stomp, a thrown object, the scarecrow's arm hitting a
row).

Fitted starting values, in metres and seconds, for a 0.35 m radius walker
in stalks spaced 0.25 m (refit against your own teacher before trusting
them):

```
wake:     B=0.43  w=0.131  t_lead=0.142  lam=0.1  k=78.4  zeta=0.154  mix=0.81  q=1.21
presence: A=0.187 sigma=0.136 mix=0.65 q=1.23
```

`q` near 1 means the spatial falloff is closer to `exp(-d/w)` than to a
Gaussian. Fix `q = 1` at ship time and the `pow` disappears.

## 2. Evaluate per instance, not per vertex

The reconstruction is a pure function of tokens and time, so nothing forces
it into the vertex shader. Two patterns, both trivial in cost:

- **Per-instance buffer.** A compute pass writes one `float2` bend per
  stalk into a `StructuredBuffer`, at 36 or 72 Hz. The vertex shader reads
  `_Bend[instanceID]` and calls `ApplyBend` (height-squared scaling, a
  handful of ops). Arithmetic for 15,000 stalks at 48 ops: about 0.7 M ops
  per frame, versus 72 M if every one of ~100 vertices per stalk did it.
- **Bend texture.** Bake the same two terms into an `RG16F` texture over
  the field once per frame and sample it once per instance (or per vertex
  for the near ring). At 0.25 m cells a 30 m field is 120×120 texels,
  57 KB. The sweep says cells at or below stalk spacing match direct
  evaluation; 0.3 m cells cost 0.46 error, 0.5 m cells 0.55, because the
  fitted trail is only 0.13 m wide. The texture wins as soon as anything
  else reads it: particles, the scarecrow, rustle audio, the monster's
  trail query all sample the same 57 KB instead of re-evaluating tokens.

The nearest-point-on-polyline query for the wake (`NearestOnPath` in
`ReactiveKernels.cs`) runs once per stalk when the path token changes, not
per frame. For 15,000 stalks and a 200-point path that is 3 M ops, once.

## 3. LOD is a mesh problem; bend stays

A 0.4 m tip displacement is visible at every distance a 30 m field can
offer, so far stalks still need bend. What they do not need is a mesh.
Beyond the distance where individual stalks merge (roughly 15 to 20 m at
Quest 2 pixel density) draw impostor cards or merged row meshes and skew
them with the bend texture. The bend evaluation stays per instance from the
texture at every LOD; only vertex count changes.

## 4. Measured

**Done, on a phone: `docs/bendbench-results.md`.** All six terms cost
37%, 36% and 7% over a no-bend baseline on three load shapes, at 400,000 to
575,000 stalks. Scaled to the 15,000 stalks this field actually uses, that is
0.12 ms, under 1% of a 13.9 ms budget, so the claim below holds for the
reason it gives. Baking to a bend texture (section 2) costs nothing
measurable on any of the three. One caution the run added: the same
arithmetic costs eight times more per vertex invocation in one preset than
another, so the op counts this write-up quotes do not predict milliseconds.
A phone is not a Quest 2, and none of this ran on a headset.

**To close the question on the headset itself.** The same page runs in the
Quest browser with no changes: open
`https://claude.ai/artifact/QVrzUYuoUtMpZLjhbNbKpt` in the headset's
browser, pick the **Q2 eyes** resolution (2880×1584, two default eye buffers
side by side, so the fill cost is what a stereo render pays), press **All
three loads**, and paste the "Results as JSON" block into a message. The
page is a flat panel, not a WebXR session, so it measures the GPU's cost
of the arithmetic and the fill at the right pixel count, not the
compositor or the timewarp. That is the number this section needs. The
Unity path in `unity/` remains uncompiled and unmeasured on device; the
browser run bounds it, it does not replace it.

## 4b. Measure before optimising the math further

A cornfield on Quest 2 is usually fill-bound (alpha-tested leaves disable
early-Z on Adreno) or vertex-count bound. The bend ALU is a small slice of
either. OVR Metrics Tool and Snapdragon Profiler will say which. If
fragment-bound: leaf cards cut tighter to the alpha shape, opaque stalk
geometry with clipping only on leaves, front-to-back draw order, fixed
foveated rendering. If vertex-bound: sections 2 and 3.

## 5. Wind as tokens

`poc/wind_experiment.py` drives 4096 stalks with synthetic frozen
turbulence advected at 4 m/s and asks what a sparse representation can
recover. Results in `poc/results/wind.md`, picture in `wind.png`.

| representation, K = 32 terms | bend error | evaluations per vertex |
|---|---|---|
| 32 global Fourier modes | 0.76 | 32 |
| 32 travelling Gaussian gusts | 0.76 | 2.3 |
| 32 gusts + travelling wave packets | 0.77 | 2.4 |

Three things fall out:

- **Locality is the win, not fidelity.** Gusts and Fourier modes capture
  the same energy per term. A gust only touches the vertices under its
  footprint, so 32 tokens cost 2.3 evaluations per vertex versus 32. At
  128 terms it is 4 versus 128.
- **A resonant canopy shows stripes, not blobs.** The bend field of 1 Hz
  stalks under 4 m/s wind is striped across the wind at U/f0 = 4 m (the
  honami effect). The token for that is a travelling wave packet: an
  across-wind envelope carrying a cosine at that wavelength, moving at U.
  The pursuit starts picking packets over blobs once the big gusts are
  taken (29% of tokens by K = 128). Same closed form as the ring wave
  with a straight front.
- **Everything below about 1.5 m should be seeded noise.** After 32
  tokens the residual still holds 59% of the bend energy but its
  correlation length is 1.25 m along wind and 1.5 m across. That is a few
  stalks. Represent it as per-stalk (or per-cluster) seeded noise with the
  residual's variance and a ~1 s time scale, not as more tokens. Coherent
  structure as tokens, incoherent remainder as seed: the write-up's own
  rule.

To ship: emit gusts and packets upwind on a random schedule from a wind
state (mean speed, direction, gustiness), advect them at U, kill them past
the field; evaluate per instance from the same bend texture as the trail.
Real parameters for gust size, packet wavelength and speed come from field
video (Py, de Langre and Moulia 2006; Finnigan 1979) or your own phone
footage through optical flow. The synthetic teacher here only shows the
shape of the answer.

## 6. Multiplayer and replay for free

Tokens are idempotent and tiny. Send the path polyline and stride events
with times on a shared clock, snapshot the live token set for late joiners,
and let one authority decide token death. Every client reconstructs the
same field with no state to synchronise.
