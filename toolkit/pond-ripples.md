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
chirp(r, tau) = A * exp(-lam tau) * (tau / 0.5)^m / (1 + r / r0)^n
              * exp(-(r / (v_max tau + 0.02))^4)            (soft causal front)
              * cos(g_eff tau^2 / (4 max(r, 0.02)) + phi)
```

The fixed-wavelength ring from the vegetation grammar (`RingWaveBend` in
the HLSL) is wrong for water: fitted freely it scores worse than drawing
nothing (height error 1.08). Keep it for things that really do travel at
one speed (a shock through grass); use the chirp for water.

**Fitted parameters** (metres, seconds, 0.4 m deep pond, 3 cm impulse):

```
chirp: A=0.0054  lam=0.215  m=-1  n=0.047  g_eff=9.81  phi=1.58  v_max=0.87
```

`g_eff` was searched over 2 to 30 and landed on 9.81: the fit recovered
gravity from the height field, which is the sanity check that the chirp is
the right functional form.

**Teacher.** `poc/water/teacher.py`: spectral linear water waves on a
256x256 grid, full dispersion relation with depth, exact per-mode
propagation, viscous plus bulk damping. Exact for small amplitude.

**Scores** (`poc/results/water.md`):

| case | height error | slope error | live tokens per point |
|---|---|---|---|
| splash, chirp token | 0.49 | 0.65 | 1 |
| wake, Huygens, 2 cm spacing | 0.58 | | 54 |
| wake, Huygens, 5 cm spacing | 0.59 | | 22 |
| wake, Huygens, 10 cm spacing | 0.61 | | 11 |
| wake, Huygens, 20 cm spacing | 0.70 | | 6 |

Cost 34 ops per point per live token. For water the natural runtime is a
baked height/normal texture over the pond, cells at half the shortest
wavelength you want to show, updated once per frame from the live tokens.

**Known limits.** Height error of 0.49 on a splash is a visual match of
the ring pattern, speed and decay, not of every crest; slope (what the
shader actually renders) is worse at 0.65 because the chirp's short
trailing waves are where the residual sits. Linear teacher only: no
breaking, no splash crown, no drops. Real puddles are shallow and
nonlinear, see the puddle-slosh card. Wake tokens per point grow with
path length; cap by killing tokens once `exp(-lam tau)` is below 1e-3.
