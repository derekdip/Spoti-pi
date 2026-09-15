# Wind: gust tokens versus Fourier modes

Synthetic frozen turbulence (128 m x 32 m at 0.25 m, outer scale 8.0 m, U = 4.0 m/s, sigma_u = 1.2 m/s) advected over 4096 stalks at 1.0 Hz, zeta 0.15.
Errors are relative RMS. 'wind' scores the wind field itself; 'bend' scores the stalk bend on frames after the
start-up transient (t >= 3 s). 'fit to wind' representations were chosen to match the wind field; 'fit to bend'
representations were chosen to match the steady-state bend field (the wind field passed through the stalk's
transfer function, which reproduces the integrated teacher to 0.012).
Evals per vertex: terms a vertex must evaluate. Fourier modes are global; a gust only touches vertices within 3 sigma.

Wave packets: the dictionary also holds across-wind-elongated envelopes carrying cos/sin at the resonant
wavelength U/f0 = 4.0 m (a travelling wave packet); the pursuit picks gusts or packets freely.

| K | wind: Fourier | wind: gusts | bend, fit to wind: Fourier | bend, fit to wind: gusts | bend, fit to bend: Fourier | bend, fit to bend: gusts | bend, fit to bend: gusts + wave packets | evals/vertex: Fourier | evals/vertex: gusts | evals/vertex: packets |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 0.851 | 0.843 | 0.910 | 0.905 | 0.910 | 0.904 | 0.904 (0% packets) | 4 | 0.9 | 0.9 |
| 8 | 0.797 | 0.786 | 0.874 | 0.854 | 0.874 | 0.854 | 0.854 (0% packets) | 8 | 1.3 | 1.3 |
| 16 | 0.729 | 0.723 | 0.820 | 0.822 | 0.820 | 0.821 | 0.821 (0% packets) | 16 | 1.9 | 1.9 |
| 32 | 0.654 | 0.662 | 0.770 | 0.768 | 0.764 | 0.764 | 0.767 (12% packets) | 32 | 2.3 | 2.4 |
| 64 | 0.578 | 0.600 | 0.710 | 0.713 | 0.693 | 0.701 | 0.703 (23% packets) | 64 | 2.9 | 3.1 |
| 128 | 0.503 | 0.530 | 0.643 | 0.662 | 0.606 | 0.649 | 0.631 (29% packets) | 128 | 3.7 | 4.2 |

Gust radii chosen by the pursuit (first 128 tokens), fit to wind: 1.0 m: 60, 2.0 m: 53, 4.0 m: 13, 8.0 m: 2

Fit to bend: 1.0 m: 78, 2.0 m: 34, 4.0 m: 14, 8.0 m: 2

