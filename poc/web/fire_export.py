"""Export teacher glow frames and fitted model states for the browser harness.

The teacher is a fluid solver and cannot run in a browser, so its glow is precomputed and shipped
as a PNG atlas, one frame per tile. The cheap model IS closed-form and stateless, so it is
reimplemented in the page and evaluated live; that is the whole point of the comparison.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.fire import scenes, teacher as TT

OUT = Path("poc/web/firebench")
SC = ["plume", "gusty", "strong_gust", "gust_shelf", "bed_chain"]
STRIDE = 4                      # the stride every experiment scored at


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    states = {}
    try:
        f5 = json.load(open("poc/results/f5.json"))
        for r in f5["fresh"] + [f5["pilot"]]:
            states[r["scene"]] = r["fits"][r["best"]]["state"]
    except Exception as e:
        print("no f5:", e)
    try:
        po = json.load(open("poc/results/pin_one.json"))
        states["plume"] = po["runs"]["cheap four + soot"]["state"]
    except Exception as e:
        print("no pin_one:", e)
    for nm in SC:
        p, burners, patches, obstacles = getattr(scenes, nm)()
        rec = TT.run(p, burners, patches, obstacles)
        keep = np.arange(0, len(rec.times), STRIDE)
        glow = TT.emission(rec.T[keep]) * np.exp(-0.5 * rec.soot[keep])
        F, ny, nx = glow.shape
        vmax = float(glow.max()) or 1.0
        atlas = (np.clip(glow / vmax, 0, 1) * 255).astype(np.uint8)
        # tile frames vertically; within a tile, row j is grid row j with y increasing upward,
        # so the page draws grid row j at canvas row ny-1-j
        img = Image.fromarray(atlas.reshape(F * ny, nx))
        img.save(OUT / f"teacher_{nm}.png", optimize=True)
        meta[nm] = dict(nx=nx, ny=ny, frames=int(F), dx=float(p.dx), vmax=vmax,
                        times=[float(t) for t in rec.times[keep]],
                        gust_amp=float(p.gust_amp), gust_hz=float(p.gust_hz),
                        burners=[dict(x=b.x, y=b.y, radius=b.radius, t_on=b.t_on,
                                      t_off=min(b.t_off, 1e6)) for b in burners],
                        patches=[dict(x=q.x, y=q.y, radius=q.radius) for q in patches],
                        obstacles=[dict(x=o.x, y=o.y, hw=o.half_w, hh=o.half_h) for o in obstacles],
                        state=states.get(nm))
        sz = (OUT / f"teacher_{nm}.png").stat().st_size
        print(f"{nm:<13} {F} frames {nx}x{ny}  peak glow {vmax:.2f}  png {sz/1024:.0f} KB"
              f"  state {'yes' if states.get(nm) else 'MISSING'}", flush=True)
    json.dump(meta, open(OUT / "scenes.json", "w"))
    print("wrote", OUT / "scenes.json", f"{(OUT/'scenes.json').stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
