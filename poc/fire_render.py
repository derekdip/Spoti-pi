"""Side-by-side frames of the teacher and the cheap fire at its best-known state.

Every number in the arc is an error; this is what the two actually look like. Rows are the
soot-obscured emission the visual consumer coarsens, at full resolution, on a colour scale fixed
per scene by the teacher's brightest frame. Nothing is fitted here.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, tokens, teacher as TT

SC = ("windy", "obstacle", "twin", "full")
NT = 4


def glow(rec):
    return TT.emission(rec.T) * np.exp(-0.5 * rec.soot)


def main():
    floor = json.load(open("poc/results/f6_floor.json"))
    fig, axes = plt.subplots(2 * len(SC), NT, figsize=(2.6 * NT, 2.2 * 2 * len(SC)), squeeze=False)
    for si, nm in enumerate(SC):
        p, burners, patches, obstacles = getattr(scenes, nm)()
        rec = TT.run(p, burners, patches, obstacles)
        idx = np.linspace(0, len(rec.times) - 1, NT + 2)[1:-1].round().astype(int)
        st = tokens.FireState(**floor[nm]["state"])
        cheap = tokens.as_record(st, p, rec.times[idx], burners, patches, obstacles)
        ext = cheap.extent
        gt, gc = glow(rec)[idx], glow(cheap)
        vmax = float(gt.max()) or 1.0
        times = rec.times[idx]; idx = np.arange(NT)
        for j, f in enumerate(idx):
            for r, (g, lab) in enumerate(((gt, "teacher"), (gc, "cheap"))):
                ax = axes[2 * si + r, j]
                ax.imshow(g[f], origin="lower", extent=ext, vmin=0, vmax=vmax, cmap="inferno", aspect="equal")
                if obstacles:
                    ax.contour(np.linspace(ext[0], ext[1], p.nx), np.linspace(ext[2], ext[3], p.ny),
                               cheap.solid.astype(float), levels=[0.5], colors="w", linewidths=0.6)
                ax.set_xticks([]); ax.set_yticks([])
                if j == 0:
                    ax.set_ylabel(f"{nm}\n{lab}", fontsize=8)
                if r == 0:
                    ax.set_title(f"t = {times[f]:.1f} s", fontsize=8)
        print(f"{nm}: rendered, floor {floor[nm]['floor']:.3f}, teacher peak glow {vmax:.2f}", flush=True)
    fig.suptitle("Soot-obscured emission, full resolution, same colour scale per scene", fontsize=9)
    fig.tight_layout()
    fig.savefig("poc/results/fire_compare.png", dpi=110)
    print("wrote poc/results/fire_compare.png")


if __name__ == "__main__":
    main()
