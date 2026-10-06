# Pond ripples

**Effect.** Splash rings from an impact and the wake of something dragged
through open water. Consumers: water surface shader (height and normal),
audio, AI ("something disturbed the pond").

**Token.** An impulse event: position, time, amplitude. A wake is the
Huygens superposition of impulse tokens emitted along the path.

**Kernel.** The dispersive ring. Deep-water waves disperse: long waves run
ahead, short waves trail, so the phase is the Cauchy-Poisson chirp
`g t^2 / (4 r)`, not `k r - w t`:

```
k_loc         = g_eff tau^2 / (4 r^2)                       (local wavenumber of the chirp)
chirp(r, tau) = A * exp(-lam tau) * (tau / 0.5)^m / (1 + r / r0)^n
              * exp(-(r / (v_max tau + 0.02))^4)            (soft causal front)
              * exp(-(k_loc / k_cut)^2)                     (viscous cutoff of short waves)
              * cos(g_eff tau^2 / (4 max(r, 0.02)) + phi)
```

The viscous cutoff matters: without it the chirp fills the inside of the
ring with ever-shorter waves that a real pond damps away, and the slope
error doubles (0.65 versus 0.33).

The fixed-wavelength ring from the vegetation grammar (`RingWaveBend` in
the HLSL) is wrong for water: fitted freely it scores worse than drawing
nothing (height error 1.08). Keep it for things that really do travel at
one speed (a shock through grass); use the chirp for water.

**Fitted parameters** (metres, seconds, 0.4 m deep pond, 3 cm impulse):

```
chirp: A=0.1  lam=0.106  m=0.31  n=1.71  g_eff=9.8  phi=1.62  v_max=1.85  k_cut=54
```

`g_eff` was searched over 2 to 30 and landed on 9.80: the fit recovered
gravity from the height field, which is the sanity check that the chirp is
the right functional form. `k_cut` of 54 rad/m means waves shorter than
about 12 cm are damped, a plausible viscous scale for a pond.

**Teacher.** `poc/water/teacher.py`: spectral linear water waves on a
256x256 grid, full dispersion relation with depth, exact per-mode
propagation, viscous plus bulk damping. Exact for small amplitude.

**Scores** (`poc/results/water.md`):

| case | height error | slope error | live tokens per point |
|---|---|---|---|
| splash, fixed-wavelength ring | 1.08 | 1.34 | 1 |
| splash, chirp token | 0.31 | 0.33 | 1 |
| wake, Huygens, 2 cm spacing | 0.59 | | 48 |
| wake, Huygens, 5 cm spacing | 0.59 | | 19 |
| wake, Huygens, 10 cm spacing | 0.61 | | 10 |
| wake, Huygens, 20 cm spacing | 0.70 | | 5 |

Cost 40 ops per point per live token. Refitting the token's shape on the
wake itself (17 minutes of differential evolution) did not beat the
transferred splash token, so the wake residual is the difference between an
impulse and a moving pressure source, not the token's shape. For water the natural runtime is a
baked height/normal texture over the pond, cells at half the shortest
wavelength you want to show, updated once per frame from the live tokens.

**Known limits.** Height error of 0.31 on a splash is a visual match of
the ring pattern, speed, decay and wavelength trend, not of every crest.
The wake at 0.6 keeps the V pattern and its spacing but not the amplitude
distribution along the arms. Linear teacher only: no
breaking, no splash crown, no drops. Real puddles are shallow and
nonlinear, see the puddle-slosh card. Wake tokens per point grow with
path length; cap by killing tokens once `exp(-lam tau)` is below 1e-3.
