# moire: predicting and avoiding moire of stripe patterns on a pixel grid

| file | what |
|---|---|
| `moire.py` | `predict(P, theta, filt)`: the list of moire components (harmonic, amplitude, folded frequency) and the RMS moire contrast; exact renderers (point sampling, analytic box filter); low-pass measurement |
| `exp_m1.py` -> `exp_m1.log` | prediction vs measurement on 16 (period, angle) cases, point and box filtered |
| `exp_m2.py` -> `exp_m2.log`, `exp_m2.json` | avoidance: sweep of the period P in [2.5, 4.5] px and of the angle |
| `figures.py` -> `moire_vs_period.png`, `moire_before_after.png` | |

## The model (exact, not a heuristic)

Stripes are the indicator of frac(k.x) < 1/2, with k = (cos t, sin t)/P. Their Fourier series is
sum_n c_n e^{2 pi i n k.x}, where c_n = 1/(i pi n) for odd n and 0 for even n != 0. At integer pixels
e^{2 pi i v.x} = 1 for every v in Z^2, so the sampled image is *exactly*

    sum_n c_n H(n k) e^{2 pi i (n k - v_n).x},     v_n = nearest lattice point to n k,

where H is the pixel filter: 1 for point sampling, sinc(n kx) sinc(n ky) for area (box) antialiasing. A moire is a
harmonic whose folded frequency n k - v_n is low (here, periods of 16 to 512 px) while v_n != 0. In 1D that folded
frequency is ||n/P||, the distance to the nearest integer. Its record lows come from the continued-fraction
(Stern-Brocot) approximations of 1/P, which is where the Farey machinery enters.

## Results

**Prediction** (`exp_m1.log`). Across 16 cases the predicted RMS moire matches the measurement to 1-3% for both
filters, and the predicted component list names each moire's period and harmonic. Point-sampled images are
reproduced to 2-20% L2. The worst cases are exact rationals such as P = 33/10, where infinitely many harmonics fold onto
one beat and the harmonic cutoff (2001) shows. With box filtering most moires fall below the measurement floor of a
1024 px window (about 1e-4).

**Avoidance** (`exp_m2.log`, `moire_vs_period.png`):
- **Point sampling** (no AA, nearest-texel minification, 1-bit masks): the median RMS moire over the range is 4.7%.
  The worst periods are near P = n/m with **n odd and small**: around 3 (n = 3) it reaches 16.6%, and also around
  20/7 and 16/5.
- **Even periods are immune**, because a duty-1/2 square wave has no even harmonics, so P = 4 cannot fold anything
  into the band. Robustness is what matters, because a design is never exact: allowing +-0.01 px, the most robust
  period in [2.5, 4.5] is P = 4, with RMS at most 0.9%. P = 3.01 gives 16.5% (see `moire_before_after.png`).
- **Box filtering** (area AA) lowers moire 30-1000x. The median is 0.03% and the worst is 1.0%, from the n = 3 fold
  in the window P in [2.82, 3.2].
- **Angle** (P = 3.3, point sampled): 0 degrees gives 4.4%, and the predictor finds angles near 6.45 degrees that
  measure 0.09%.

**What did not hold up.** I expected the golden-ratio-like ("badly approximable") periods to be the most robust, by
analogy with Hurwitz/Markoff. They are not: P = 2 + phi = 3.618 is at the median, 4.7%. Diophantine quality governs
the tail of high harmonics, but the visible band is wide (1/512 to 1/16), so a low harmonic always lands in it, and
those dominate. The continued fractions explain *where* the spikes are (n/m with small odd n). They do not make
irrational periods the best choice.

## Use

`predict()` is a microsecond-scale moire checker for any (period, angle, filter). Possible uses:
- a lint for UI hatch patterns, scanline and stripe shaders, halftone screens, or VR textures without mips;
- choosing a pattern scale that is moire-robust within a tolerance;
- explaining a reported moire as "harmonic n folded by lattice vector v".

It does not model gamma, display subpixels or a contrast-sensitivity curve. The band edges are a modelling choice.
