"""M2: avoidance. Sweep the stripe period P in [2.5, 4.5] px (theta = 0) and the angle at P = 3.3, predicting the RMS
moire contrast in the visible band (period 16..512 px). Validate predictions by measurement on a subsample, find the
spikes (small-denominator rationals n/m with n odd), and pick the most robust period."""
import math, numpy as np, json
from fractions import Fraction
from moire import predict, render, lowpass, cf
W = 1024; FC = 1/16; FLO = 1/512
def pred(P, th, filt): return predict(P, th, filt, f_lo=FLO, f_cut=FC, nmax=2001 if filt == "point" else 401)[1]
def meas(P, th, filt):
    m = lowpass(render(P, th, W, filt), FC); win = np.hanning(W)[:, None] * np.hanning(W)[None, :]
    # remove the band below FLO the same way the predictor does
    F = np.fft.fft2(m); f = np.fft.fftfreq(W); FX, FY = np.meshgrid(f, f); F[np.hypot(FX, FY) <= FLO] = 0
    m = np.real(np.fft.ifft2(F)); return math.sqrt(np.mean(m ** 2) / np.mean(win ** 2))
Ps = np.linspace(2.5, 4.5, 2001)
out = {}
for filt in ("point", "box"):
    v = np.array([pred(P, 0.0, filt) for P in Ps]); out[filt] = v.tolist()
    # validation on 25 evenly spaced periods
    idx = np.linspace(0, len(Ps) - 1, 25).astype(int)
    pm = [(v[i], meas(Ps[i], 0.0, filt)) for i in idx]
    rel = [abs(a - b) / max(b, 1e-12) for a, b in pm if b > 1e-4]
    print("%s: validation on 25 periods: median |pred - meas|/meas %.3f, max %.3f (cases above 1e-4: %d)" % (filt, np.median(rel), max(rel), len(rel)))
    order = np.argsort(-v)
    peaks = []
    for i in order:
        if all(abs(Ps[i] - Ps[j]) > 0.03 for j in peaks): peaks.append(i)
        if len(peaks) == 6: break
    print("  worst periods:", ", ".join("P=%.3f (~%s) rms %.3f" % (Ps[i], Fraction(Ps[i]).limit_denominator(9), v[i]) for i in peaks))
    # most robust: minimise the worst prediction over a +-0.01 px tolerance window (designs are not exact)
    k = 10; robust = np.array([v[max(0, i-k):i+k+1].max() for i in range(len(Ps))])
    b = int(np.argmin(robust[k:-k])) + k
    print("  most robust period (worst over +-0.01 px): P=%.4f, rms <= %.5f; 1/P continued fraction %s; median over the range %.4f" % (
        Ps[b], robust[b], cf(1 / Ps[b], 8), np.median(v)))
    out[filt + "_best"] = float(Ps[b])
# P exactly 4 vs 3: duty 1/2 kills even harmonics, so n/m with n even cannot fold
for P in (3.0, 3.01, 4.0, 4.01, 3.5, 3.51):
    print("  P=%.2f: point-sampled rms %.4f, box %.6f" % (P, pred(P, 0, "point"), pred(P, 0, "box")))
# angle sweep at P = 3.3
th = np.linspace(0, math.pi / 4, 901)
va = np.array([pred(3.3, t, "point") for t in th]); out["theta"] = th.tolist(); out["theta_point"] = va.tolist()
print("angle sweep P=3.3 (point): worst theta %.2f deg rms %.3f; best theta %.2f deg rms %.4f; theta=0 rms %.4f" % (
    math.degrees(th[va.argmax()]), va.max(), math.degrees(th[va.argmin()]), va.min(), va[0]))
out["P"] = Ps.tolist(); json.dump(out, open("exp_m2.json", "w"))
