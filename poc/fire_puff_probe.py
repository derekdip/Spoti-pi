"""Four numbers from the teacher, for the puff grammar's declared defaults.

Measured on `plume`, which no experiment scores. Rise speed of the hot front, the puffing
frequency, the height of the visible tongue, and how the width grows with height. These set the
V0 defaults and on-states; they are not fits to any scored scene.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, teacher as TT

p, burners, patches, obstacles = scenes.plume()
rec = TT.run(p, burners, patches, obstacles)
X, Y = TT._grid(p)
b = burners[0]
ex = rec.T - TT.T_AMBIENT                      # (F, ny, nx)
late = rec.times >= 1.0
xi = int(round(b.x / p.dx))
ys = np.arange(p.ny) * p.dx

# 1. mean centreline profile (lateral max per row, late frames)
prof = ex[late].max(axis=2).mean(axis=0)     # (ny,)
vis = ys[prof > (TT.VIS_T0 - TT.T_AMBIENT)]
print(f"tongue: visible (T>{TT.VIS_T0:.0f} K) up to y = {vis.max() if len(vis) else 0:.2f} m; "
      f"T>400 K up to y = {ys[prof > 107].max():.2f} m; peak excess {prof.max():.0f} K at y = {ys[prof.argmax()]:.2f}")
for y in (0.3, 0.6, 0.9, 1.2, 1.5):
    j = int(round(y / p.dx)); print(f"   y={y:.1f}: mean lateral-max excess {prof[j]:6.0f} K")

# 2. width vs height: lateral second moment of the time-mean excess
mean = ex[late].mean(axis=0)
for y in (0.2, 0.4, 0.6, 0.8, 1.0, 1.2):
    j = int(round(y / p.dx)); row = np.maximum(mean[j], 0)
    if row.sum() > 1:
        xc = (row * X[j]).sum() / row.sum(); sig = np.sqrt((row * (X[j] - xc) ** 2).sum() / row.sum())
        print(f"   width: y={y:.1f}  sigma={sig:.3f} m  centre={xc:.2f}")

# 3. puffing frequency: FFT of centreline excess at a few heights
dt = rec.times[1] - rec.times[0]
for y in (0.4, 0.8, 1.2):
    j = int(round(y / p.dx)); s = ex[late, j, :].max(axis=1); s = s - s.mean()
    f = np.fft.rfftfreq(len(s), dt); P = np.abs(np.fft.rfft(s)) ** 2; P[0] = 0
    print(f"   flicker: y={y:.1f} dominant {f[P.argmax()]:.2f} Hz, rms {np.sqrt((s**2).mean()):.0f} K")

# 4. rise speed: lag of maximum cross-correlation between heights
def lagcorr(a, bb, maxlag):
    a = a - a.mean(); bb = bb - bb.mean(); best = (0, -1)
    for L in range(0, maxlag):
        c = (a[:len(a)-L] * bb[L:]).mean() / (a.std() * bb.std() + 1e-9)
        if c > best[1]: best = (L, c)
    return best
for y1, y2 in ((0.3, 0.6), (0.6, 0.9), (0.9, 1.2)):
    j1, j2 = int(round(y1 / p.dx)), int(round(y2 / p.dx))
    s1 = ex[late, j1, :].max(axis=1); s2 = ex[late, j2, :].max(axis=1)
    L, c = lagcorr(s1, s2, 30)
    print(f"   rise: {y1:.1f}->{y2:.1f} m lag {L*dt:.3f} s -> {(y2-y1)/max(L*dt,1e-9):.2f} m/s (corr {c:.2f})")
# 5. soot
print(f"   soot: peak {rec.soot[late].max():.2f}, mean over hot cells {rec.soot[late][ex[late] > 200].mean():.2f}")

# --- second pass: the lateral-max series is too steady to carry a lag, so use the start-up front
# and the lateral centroid instead
print("\nstart-up front (first frame each height exceeds 400 K):")
prev = None
for y in (0.3, 0.6, 0.9, 1.2, 1.5, 1.8):
    j = int(round(y / p.dx)); s = ex[:, j, :].max(axis=1)
    hit = np.where(s > 107)[0]
    ta = rec.times[hit[0]] if len(hit) else np.nan
    v = (y - prev[0]) / (ta - prev[1]) if prev and np.isfinite(ta) and ta > prev[1] else np.nan
    print(f"   y={y:.1f}: arrives t={ta:.2f} s" + (f"  -> {v:.2f} m/s from {prev[0]:.1f}" if prev else ""))
    prev = (y, ta)
print("centroid wobble (late frames):")
for y in (0.6, 1.0, 1.4):
    j = int(round(y / p.dx)); row = np.maximum(ex[late, j, :], 0)
    xc = (row * X[j][None]).sum(1) / np.maximum(row.sum(1), 1e-9); xc = xc - xc.mean()
    f = np.fft.rfftfreq(len(xc), dt); P = np.abs(np.fft.rfft(xc)) ** 2; P[0] = 0
    print(f"   y={y:.1f}: rms {xc.std()*100:.1f} cm, dominant {f[P.argmax()]:.2f} Hz, second {f[np.argsort(P)[-2]]:.2f} Hz")
print("along-column decay of the mean centreline excess, as an age at the front speed:")
for y in (0.3, 0.6, 0.9, 1.2, 1.5, 1.8):
    j = int(round(y / p.dx)); print(f"   y={y:.1f}: {prof[j]:5.0f} K   ln ratio to y=0.3: {np.log(prof[j]/prof[int(round(0.3/p.dx))]):+.2f}")
