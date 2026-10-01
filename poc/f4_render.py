"""Teacher / column best-known / puff standard fit / puff look fit, for the F4 scenes, tone-mapped."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, tokens, teacher as TT

GAMMA = 1 / 2.2


def glow(rec):
    return TT.emission(rec.T) * np.exp(-0.5 * rec.soot)


def main(out="poc/results/f4_compare.png"):
    d = json.load(open("poc/results/f4.json")); col = json.load(open("poc/results/f6_floor.json"))
    rows = d["unseen"]
    fig, axes = plt.subplots(4 * len(rows), 4, figsize=(10.4, 8.8 * len(rows)), squeeze=False)
    for si, r in enumerate(rows):
        nm = r["scene"]
        p, burners, patches, obstacles = getattr(scenes, nm)()
        rec = TT.run(p, burners, patches, obstacles)
        idx = np.linspace(0, len(rec.times) - 1, 6)[1:-1].round().astype(int)
        t = rec.times[idx]
        panels = [("teacher", glow(rec)[idx]),
                  ("column", glow(tokens.as_record(tokens.FireState(**col[nm]["state"]), p, t, burners, patches, obstacles)))]
        for lab in ("standard", "look"):
            st = puffs.PuffState(**r["fits"][lab]["state"])
            panels.append((f"puffs {lab}", glow(puffs.as_record(st, p, t, burners, patches, obstacles))))
        vmax = float(panels[0][1].max()) ** GAMMA or 1.0
        for j in range(4):
            for k, (lab, g) in enumerate(panels):
                ax = axes[4 * si + k, j]
                ax.imshow(g[j] ** GAMMA, origin="lower", extent=rec.extent, vmin=0, vmax=vmax, cmap="inferno")
                if obstacles:
                    ax.contour(np.linspace(0, rec.extent[1], p.nx), np.linspace(0, rec.extent[3], p.ny),
                               rec.solid.astype(float), levels=[0.5], colors="w", linewidths=0.6)
                ax.set_xticks([]); ax.set_yticks([])
                if j == 0: ax.set_ylabel(f"{nm}\n{lab}", fontsize=8)
                if k == 0: ax.set_title(f"t = {t[j]:.1f} s", fontsize=8)
        print(nm, "rendered", flush=True)
    fig.suptitle("Soot-obscured emission, tone-mapped (gamma 1/2.2), same scale per scene", fontsize=9)
    fig.tight_layout(); fig.savefig(out, dpi=100); print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
