"""Figures: predicted moire vs stripe period, and a before/after image."""
import json, math, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from moire import render, lowpass, predict
d = json.load(open("exp_m2.json")); P = np.array(d["P"])
INK, INK2, BLUE, ORANGE = "#191919", "#666666", "#257de0", "#f47230"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#cccccc", "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(9, 3.6), dpi=200)
for key, col, lab in (("point", BLUE, "point sampled"), ("box", ORANGE, "box filtered (area AA)")):
    v = np.maximum(np.array(d[key]), 1e-6); ax.plot(P, v, color=col, lw=1.2, label=lab)
ax.set_yscale("log"); ax.set_ylim(1e-6, 0.5); ax.set_xlim(2.5, 4.5)
ax.axhline(0.003, color="#999999", lw=0.8, ls=(0, (3, 3))); ax.text(4.48, 0.0036, "~visibility threshold (0.3% contrast)", color=INK2, fontsize=8, ha="right")
for x, lab in ((3.0, "3"), (3.5, "7/2"), (2.5, "5/2"), (4.0, "4 (even: no odd harmonic folds)")):
    ax.annotate(lab, (x, 0.3), color=INK2, fontsize=8, ha="center")
ax.set_xlabel("stripe period P (pixels)"); ax.set_ylabel("predicted RMS moire contrast")
ax.grid(axis="y", color="#eeeeee", lw=0.6); ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower left", fontsize=8)
ax.set_title("Moire of 0/1 stripes on a pixel grid (band: periods 16-512 px)", color=INK, fontsize=11, loc="left")
fig.tight_layout(); fig.savefig("moire_vs_period.png")
# before/after: P = 3.01 vs 4.01, point sampled, plus each image's low-pass (the moire itself)
W = 512
fig, axs = plt.subplots(2, 2, figsize=(8, 8), dpi=150)
for j, Pv in enumerate((3.01, 4.01)):
    img = render(Pv, 0.0, W, "point"); comps, rms = predict(Pv, 0.0, "point", f_lo=1/512, f_cut=1/16, nmax=2001)
    axs[0, j].imshow(img[:200, :200], cmap="gray", interpolation="nearest"); axs[0, j].set_title("P = %.2f px, point sampled (200 px crop)" % Pv, fontsize=9)
    lp = lowpass(img, 1/16, win=False)
    axs[1, j].imshow(lp, cmap="gray", vmin=-0.25, vmax=0.25); axs[1, j].set_title("its low-pass (what the eye sees): RMS %.3f" % rms, fontsize=9)
for a in axs.flat: a.set_xticks([]); a.set_yticks([])
fig.tight_layout(); fig.savefig("moire_before_after.png")
