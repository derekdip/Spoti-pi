# Toolkit: cheap fitted representations

One card per effect. Each card says what the token is, which closed-form
kernel reconstructs it, the fitted parameters, what teacher they were fitted
to, the measured error and cost, and what is still unverified. A card is
only added once the fit has been run and scored, so every number here has a
script behind it in `poc/`.

| card | effect | token | kernel | teacher | status |
|---|---|---|---|---|---|
| [corn-trail](corn-trail.md) | walker's trail through stalks | banked path polyline + live presence | wake (spring envelope) + presence | synthetic coupled nonlinear stalk lattice | fitted, held-out walk verified, shipped by the user |
| [wind-gusts](wind-gusts.md) | field sway and honami stripes | travelling gusts + wave packets + seeded residual | Gaussian / Gabor envelopes advected at U | synthetic frozen turbulence | shape verified, parameters need real footage |
| [pond-ripples](pond-ripples.md) | splash rings and wakes on open water | impulse events, Huygens along a path | dispersive chirp ring | exact linear-wave spectral solver | fitted; chirp recovers g = 9.81; fixed-wavelength ring rejected |
| [puddle-slosh](puddle-slosh.md) | confined shallow water after an impact | impact event + box geometry | standing modes / bouncing pulse | real MPM data (DeepMind WaterDrop) | negative result: fits in-window, does not extrapolate; use period + decay only |

Reference shader/C# for the kernels: `unity/ReactiveKernels.hlsl`,
`unity/ReactiveKernels.cs`.

## How a card gets added

1. Pick a teacher you trust: your own heavy sim, an exact solver for a
   known equation, or public simulation data (`docs/data-sources.md`).
2. Record `(causes u(t), state x(t))`, and a second run with different
   causes for a held-out check.
3. Write the candidate kernels as pure functions of (token, point, time).
4. Fit on a subset, score on everything, score on the held-out run, and
   score in the consumer's space (coarse field, slope, screen space), not
   just raw state.
5. Record error, cost, live tokens per point, and what was not tested.
