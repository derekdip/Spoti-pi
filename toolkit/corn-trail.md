# Corn trail

**Effect.** A walker pushes through stalks; a trail stays, leans along the
walking direction, and slowly recovers. Consumers: vegetation shader,
monster trail query, rustle audio.

**Token.** The walked path as a polyline with pass times (20 Hz is enough),
plus the live walker position and heading. About 700 floats for a 10 s
walk versus 6400 floats of per-stalk state.

**Kernel.** Per stalk, precompute perpendicular distance to the path, pass
time, outward normal and tangent (once, when the path changes). Then:

```
wake:     B * SpringEnvelope(t - (tPass - tLead)) * GKern(dPerp, w, q) * normalize(lerp(nOut, tan, mix))
presence: A * GKern(|p - walker|, sigma, q) * normalize(lerp(outward, walkerDir, mix))
```

`SpringEnvelope` is the closed-form response of a damped spring to an
exponentially decaying push (`unity/ReactiveKernels.hlsl`). Stateless.

**Fitted parameters** (metres, seconds; walker radius 0.35 m, stalks 0.25 m apart):

```
wake:     B=0.43  w=0.131  t_lead=0.142  lam=0.1  k=78.4  zeta=0.154  mix=0.81  q=1.21
presence: A=0.187 sigma=0.136 mix=0.65 q=1.23
```

**Teacher.** `poc/reactive/teacher.py`: 1600 stalks, damped springs with
stiffening, 4-neighbour coupling, tip contact with a cylinder, drag, plastic
crush with 20 s recovery. Synthetic.

**Scores** (`poc/results/gpu_sweep.md`, `holdout.md`):

| | training walk | held-out walk |
|---|---|---|
| per-stalk relative RMS | 0.40 | 0.40 |
| 16x16 coarse-field error | 0.25 | 0.25 |
| late coarse-field correlation | 0.98 | 0.99 |

Cost 48 ops per stalk per frame (26 with wake only), evaluated per instance
or baked to a bend texture with cells no larger than the stalk spacing.

**Known limits.** Per-stalk residual (0.4) is threshold-contact scatter;
regenerate it from a seed, do not fit it. Per-event stomp tokens add nothing
for walking. Hands and crouching were not in the teacher. Parameters were
fitted to synthetic physics; refit against your own heavy sim before
trusting the numbers.
