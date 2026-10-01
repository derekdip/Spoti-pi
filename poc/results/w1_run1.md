# Math Track W1 results: transfer to water

Preregistration: `docs/math-track-w1-prereg.md`.

Token fitted to the nonlinear single splash: height error 0.344; A=0.0427, lam=0.05, m=-0.0975, n=1.32, g_eff=9.83, phi=1.63, v_max=1.52, k_cut=68.8

## Q1 liveness: beta = 0.396 1/s, C = 0.0022; slope measured 2.363 vs predicted R/beta = 5.048; Spearman 0.991; H1 pass False

| eps / K(0) | live tokens M | predicted (R/beta) log(C/eps) | pruned-vs-full error |
|---|---|---|---|
| 3e-02 | 6.02 | 6.95 | 0.399 |
| 1e-02 | 11.71 | 12.49 | 0.185 |
| 3e-03 | 18.78 | 18.57 | 0.040 |
| 1e-03 | 21.62 | 24.12 | 0.010 |
| 3e-04 | 22.70 | 30.19 | 0.001 |
| 1e-04 | 22.77 | 35.74 | 0.000 |
| 3e-05 | 22.77 | 41.82 | 0.000 |

Full token field against the teacher rain: 0.511.

## Q2 observation order

| n | N | bilinear height | bilinear slope | bicubic height | bicubic slope |
|---|---|---|---|---|---|
| 12 | 144 | 1.0647 | 0.9985 | 1.1491 | 1.0074 |
| 16 | 256 | 0.9417 | 0.9948 | 1.0210 | 1.0074 |
| 24 | 576 | 0.8259 | 0.9661 | 0.8758 | 0.9856 |
| 32 | 1024 | 0.7505 | 0.9355 | 0.7657 | 0.9390 |
| 48 | 2304 | 0.5487 | 0.8240 | 0.5362 | 0.8009 |
| 64 | 4096 | 0.3934 | 0.6930 | 0.3397 | 0.6222 |
| 96 | 9216 | 0.2102 | 0.4472 | 0.1117 | 0.2747 |
| 128 | 16384 | 0.1299 | 0.3229 | 0.0382 | 0.1153 |
| 192 | 36864 | 0.0683 | 0.1586 | 0.0122 | 0.0291 |
| 256 | 65536 | 0.0333 | 0.0692 | 0.0013 | 0.0278 |

| quantity | measured exponent | predicted |
|---|---|---|
| bilinear_E_height | -0.87 | -1.0 |
| bilinear_E_slope | -0.81 | -0.5 |
| bicubic_E_height | -1.91 | -2.0 |
| bicubic_E_slope | -1.23 | -1.5 |

Slope minus height exponent: bilinear +0.06, bicubic +0.68 (prediction +0.5, bar [0.3, 0.7]). H2 pass False; H3 (bicubic height steeper by >= 0.5) pass True.

## Q3 interaction

| D (m) | a | I12 height | I12 slope | token pair error | single vs token |
|---|---|---|---|---|---|
| 0.281 | 0.5 | 1.0014 | 1.0011 | 0.383 | 0.344 |
| 0.281 | 1.0 | 1.0025 | 1.0023 | 0.383 | 0.344 |
| 0.281 | 2.0 | 1.0026 | 1.0044 | 0.428 | 0.383 |
| 0.281 | 4.0 | 0.9980 | 1.0080 | 0.761 | 0.688 |
| 0.281 | 8.0 | 1.0075 | 1.0124 | 1.644 | 1.546 |
| 0.609 | 0.5 | 1.0006 | 1.0004 | 0.376 | 0.344 |
| 0.609 | 1.0 | 1.0011 | 1.0008 | 0.374 | 0.344 |
| 0.609 | 2.0 | 1.0020 | 1.0016 | 0.404 | 0.383 |
| 0.609 | 4.0 | 1.0038 | 1.0028 | 0.693 | 0.688 |
| 0.609 | 8.0 | 1.0069 | 1.0038 | 1.543 | 1.546 |
| 1.219 | 0.5 | 1.0002 | 1.0002 | 0.363 | 0.344 |
| 1.219 | 1.0 | 1.0005 | 1.0003 | 0.362 | 0.344 |
| 1.219 | 2.0 | 1.0009 | 1.0005 | 0.397 | 0.383 |
| 1.219 | 4.0 | 1.0014 | 1.0007 | 0.692 | 0.688 |
| 1.219 | 8.0 | 1.0005 | 1.0006 | 1.543 | 1.546 |
| 2.391 | 0.5 | 1.0000 | 1.0000 | 0.366 | 0.344 |
| 2.391 | 1.0 | 1.0001 | 1.0000 | 0.367 | 0.344 |
| 2.391 | 2.0 | 1.0002 | 1.0001 | 0.407 | 0.383 |
| 2.391 | 4.0 | 1.0003 | 1.0001 | 0.702 | 0.688 |
| 2.391 | 8.0 | 1.0002 | 1.0001 | 1.536 | 1.546 |

H4 (monotone in a, non-increasing in D): False. H5 (base < 5% everywhere, 8x > 5% at smallest D): False. H6 (cross-term below single-splash token deviation everywhere): False.

## Transfer success (H1 and H2): False

