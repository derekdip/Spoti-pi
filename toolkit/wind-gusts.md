# Wind gusts

**Effect.** Coherent gusts crossing a field, with the striped "honami"
pattern a resonant canopy shows. Consumers: vegetation, audio, particles.

**Token.** A gust: position, across/along-wind widths, amplitude, emission
time; advected at the mean wind speed U; killed once past the field. A wave
packet: the same envelope carrying a cosine at wavelength U / f0 (f0 the
stalk's natural frequency), with amplitude and phase.

**Kernel.**

```
gust:   A * exp(-(dx^2 / 2 sx^2 + dy^2 / 2 sy^2))                  with dx = x - (x0 + U (t - t0))
packet: same envelope * cos(k0 * dx + phi),   k0 = 2 pi f0 / U
```

Bend follows through the same closed-form spring as the trail, or, cheaper,
quasi-statically with a resonant gain.

**Teacher.** `poc/wind_experiment.py`: synthetic frozen turbulence
(von Karman-like spectrum, 8 m outer scale, U = 4 m/s, 1.2 m/s turbulence)
advected over 4096 stalks at 1 Hz, damping ratio 0.15. Synthetic.

**Scores** (`poc/results/wind.md`), bend error after the transient:

| K terms | Fourier modes | gust tokens | gusts + packets | evals per vertex (tokens) |
|---|---|---|---|---|
| 32 | 0.76 | 0.76 | 0.77 | 2.4 |
| 128 | 0.61 | 0.65 | 0.63 | 4.2 |

Tokens and Fourier modes carry the same energy per term; tokens cost 2 to 4
evaluations per vertex instead of K. After 32 tokens the residual still
holds 59% of the bend energy but its correlation length is 1.25 m: seed it
per stalk with the residual's variance and a ~1 s time scale instead of
adding tokens.

**Known limits.** Gust sizes, packet wavelength and speed came from
synthetic turbulence. Real values: Finnigan 1979 (waving wheat), Py, de
Langre and Moulia 2006 (crop canopy video), or phone footage of a field
through optical flow. The seeded residual's spectrum has not been matched
to anything real.
