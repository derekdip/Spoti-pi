"""M1: does the predicted component list reproduce the measured low-frequency content of rendered stripes?
Measured: render, Hann-window, ideal low-pass at f_cut. Predicted: synthesise the listed components, same window and
low-pass. Report the relative L2 error and the RMS moire contrast both ways."""
import math, numpy as np, random
from moire import predict, render, lowpass, synth
W = 1024; FC = 1/16
rng = random.Random(3)
cases = [(3.3, 0.0), (2.9, 0.0), (3.618, 0.0), (4.1, 0.31), (2.5 + 1e-3, 0.0), (3.05, 0.12), (5.27, 0.78), (2.71, 1.1)] + \
        [(rng.uniform(2.2, 6), rng.uniform(0, math.pi / 2)) for _ in range(8)]
for filt in ("box", "point"):
    print("filter:", filt)
    for P, th in cases:
        comps, rms = predict(P, th, filt, f_lo=0, f_cut=FC, nmax=(2001 if filt == "point" else 401))
        meas = lowpass(render(P, th, W, filt), FC)
        pred = lowpass(synth(comps, W), FC)
        win = np.hanning(W)[:, None] * np.hanning(W)[None, :]
        e = np.linalg.norm(meas - pred) / max(np.linalg.norm(meas), 1e-12)
        mrms = np.sqrt(np.mean(meas ** 2) / np.mean(win ** 2))
        top = sorted(comps, key=lambda c: -abs(c[1]))[:2]
        print("  P %6.3f theta %5.2f: predicted RMS moire %.4f, measured %.4f, rel. L2 error of predicted image %.3f, %3d components, strongest: %s" % (
            P, th, rms, mrms, e, len(comps), ", ".join("n=%d amp %.4f period %.0f px" % (n, abs(a), 1 / math.hypot(bx, by)) for n, a, bx, by in top)), flush=True)
