"""Moire prediction for stripe patterns drawn on a pixel grid.

Pattern: square-wave stripes (indicator of frac(k.x) in [0, 1/2)) with wave vector k = (cos t, sin t)/P, P the period in pixels.
Fourier series s(x) = sum_n c_n e^{2 pi i n k.x}, c_0 = 1/2, c_n = 1/(i pi n) (odd n only).
Sampling at integer pixels x in Z^2 folds frequency n k to n k - v, v = nearest point of Z^2, because v.x is an
integer: the sampled image is EXACTLY sum_n c_n H(n k) e^{2 pi i (n k - v_n).x}, where H is the pixel filter
(H = 1 for point sampling, sinc(n kx) sinc(n ky) for box/area sampling). A moire is a harmonic whose folded
frequency b_n = n k - v_n is low (v_n != 0) while n k itself is not.

In 1D (t = 0) |b_n| = ||n/P||, the distance to the nearest integer. Its record lows are at the continued-fraction
denominators of 1/P (best approximations), and min_n n ||n/P|| is the Lagrange/Markoff constant of 1/P: a period
is moire-robust exactly when 1/P is badly approximable, golden-ratio-like."""
import math, numpy as np

def harmonics(P, theta, nmax, filt):
    kx, ky = math.cos(theta) / P, math.sin(theta) / P
    out = []
    for n in range(-nmax, nmax + 1):
        if n % 2 == 0: continue
        c = (1 - complex(math.cos(math.pi * n), -math.sin(math.pi * n))) / (2j * math.pi * n)   # indicator of [0, 1/2)
        fx, fy = n * kx, n * ky
        H = 1.0 if filt == "point" else np.sinc(fx) * np.sinc(fy)
        bx, by = fx - round(fx), fy - round(fy)
        out.append((n, c * H, bx, by, (round(fx), round(fy))))
    return out

def predict(P, theta, filt="box", f_lo=1/1024, f_cut=1/16, nmax=401):
    """Moire components (folded frequency in (f_lo, f_cut], from a harmonic that was folded, v != 0).
    Returns list of (n, amplitude, bx, by) for n > 0 (the -n term is the conjugate) and the RMS moire contrast."""
    comps = []
    for n, a, bx, by, v in harmonics(P, theta, nmax, filt):
        f = math.hypot(bx, by)
        if n > 0 and v != (0, 0) and f_lo < f <= f_cut: comps.append((n, a, bx, by))
    rms = math.sqrt(sum(2 * abs(a) ** 2 for _, a, _, _ in comps))     # the +-n pair is 2|c| cos(...): RMS sqrt(2)|c|
    return comps, rms

def cf(x, depth=12):
    out = []
    for _ in range(depth):
        a = math.floor(x); out.append(a); x -= a
        if x < 1e-12: break
        x = 1 / x
    return out

def _S1(u):
    m = np.floor(u); t = u - m; return m / 2 + np.minimum(t, 0.5)
def _S2(u):
    m = np.floor(u); t = u - m
    g = np.where(t <= 0.5, t * t / 2, 0.125 + (t - 0.5) / 2)
    return m * (m - 1) / 4 + 3 * m / 8 + m / 2 * t + g
def render(P, theta, W, filt="box", ss=None, phase=0.0):
    """Ground truth image: point sample, or box filter by ss x ss supersampling (exact up to the supersampling)."""
    kx, ky = math.cos(theta) / P, math.sin(theta) / P
    if filt == "point":
        y, x = np.mgrid[0:W, 0:W].astype(np.float64)
        return (np.mod(kx * x + ky * y + phase, 1.0) < 0.5).astype(np.float64)
    # exact pixel-area average: u = k.x over the pixel is a sum of two uniforms of widths |kx|, |ky| (a trapezoid),
    # so the average is a second difference of the second antiderivative S2 of the square wave
    y, x = np.mgrid[0:W, 0:W].astype(np.float64)
    u0 = kx * x + ky * y + phase; a, b = abs(kx), abs(ky)
    if a < b: a, b = b, a
    if b < 1e-4: return (_S1(u0 + a / 2) - _S1(u0 - a / 2)) / a
    return (_S2(u0 + a/2 + b/2) - _S2(u0 + a/2 - b/2) - _S2(u0 - a/2 + b/2) + _S2(u0 - a/2 - b/2)) / (a * b)

def lowpass(img, f_cut, win=True):
    W = img.shape[0]
    w = np.hanning(W)[:, None] * np.hanning(W)[None, :] if win else 1.0
    F = np.fft.fft2((img - img.mean()) * w)
    f = np.fft.fftfreq(W); FX, FY = np.meshgrid(f, f)
    F[np.hypot(FX, FY) > f_cut] = 0
    return np.real(np.fft.ifft2(F))

def synth(comps, W, phase=0.0, P=None, theta=None):
    """Predicted low-pass image from the component list (+-n pairs)."""
    y, x = np.mgrid[0:W, 0:W].astype(np.float64)
    img = np.zeros((W, W))
    for n, a, bx, by in comps:
        img += 2 * np.real(a * np.exp(2j * math.pi * (bx * x + by * y + n * phase)))
    return img
