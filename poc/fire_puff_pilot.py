"""Design pilot for the puff grammar on two SEEN scenes, `windy` and `obstacle`. Declared, not scored.

Two fits per scene: the floor under the four standard consumers (comparable with every earlier
floor), and the floor under the tone-mapped `LookCase` (what a player sees). Every state is then
scored on the standard case: linear error, per-consumer error, decision rates, glow correlation,
motion ratio, parcel count. Draws teacher / best column / puff (standard fit) / puff (look fit).
Anything learned here may change the grammar before it is frozen; nothing here is a result, and
F4's unseen scenes are never run by this script.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, tokens, teacher as TT, rgre_puffs as RP
from poc.fire_decisions import decisions

SEEN = ("windy", "obstacle")


def glow(rec):
    return TT.emission(rec.T) * np.exp(-0.5 * rec.soot)


def score(case, st):
    dec = decisions(case, st, as_record=puffs.as_record)
    return dict(error=case.error(st), per_consumer=case.per_consumer(st), live=st.live_count(),
                motion=RP.motion_ratio(case, st), decisions=dec,
                state={k: getattr(st, k) for k in st.__dataclass_fields__})


def main(maxfev=40):
    old = json.load(open("poc/results/f6_floor.json"))
    out = {}
    fig, axes = plt.subplots(4 * len(SEEN), 4, figsize=(10.4, 8.8 * len(SEEN)), squeeze=False)
    T0 = time.time()
    for si, nm in enumerate(SEEN):
        case = RP.PuffCase(nm, getattr(scenes, nm)())
        look = RP.LookCase(case)
        v0 = puffs.PuffState()
        out[nm] = dict(e_v0=case.error(v0), old_floor=old[nm]["floor"], old_per_consumer=old[nm]["per_consumer"], fits={})
        print(f"[{time.time()-T0:5.0f}s] {nm}: V0 {out[nm]['e_v0']:.4f}", flush=True)
        states = {}
        for lab, c in (("standard", case), ("look", look)):
            st, e, names, spread = RP.floor_fit(c, v0, maxfev_per_dim=maxfev, verbose=True)
            sc = score(case, st); sc.update(fit_objective=e, spread=spread, n_params=len(names))
            out[nm]["fits"][lab] = sc; states[lab] = st
            d = sc["decisions"]
            print(f"[{time.time()-T0:5.0f}s] {nm} {lab:<8} fit {e:.4f} ({', '.join(f'{k} {v:.3f}' for k, v in spread.items())}) -> "
                  f"linear {sc['error']:.4f} (old column {old[nm]['floor']:.4f}) live {sc['live']} motion {sc['motion']:.2f}", flush=True)
            print(f"        per consumer " + ", ".join(f"{k} {v:.3f}" for k, v in sc["per_consumer"].items()), flush=True)
            print(f"        heat wrong {100*d['heat']['disagree']:.1f}% (missed {100*d['heat']['missed_burn']:.1f}%)  "
                  f"ai wrong {100*d['ai']['disagree']:.1f}% (missed {100*d['ai']['missed_hazard']:.1f}%)  "
                  f"glow corr {d['visual']['late_correlation']:.2f}", flush=True)
            json.dump(out, open("poc/results/puff_pilot.json", "w"), indent=1)
        p, burners, patches, obstacles = getattr(scenes, nm)()
        rec = TT.run(p, burners, patches, obstacles)
        idx = np.linspace(0, len(rec.times) - 1, 6)[1:-1].round().astype(int)
        col = tokens.as_record(tokens.FireState(**old[nm]["state"]), p, rec.times[idx], burners, patches, obstacles)
        rows = [("teacher", glow(rec)[idx]), ("column", glow(col))]
        for lab in ("standard", "look"):
            rows.append((f"puffs {lab}", glow(puffs.as_record(states[lab], p, rec.times[idx], burners, patches, obstacles))))
        vmax = float(rows[0][1].max()) or 1.0
        for j in range(4):
            for r, (lab, g) in enumerate(rows):
                ax = axes[4 * si + r, j]
                ax.imshow(g[j], origin="lower", extent=col.extent, vmin=0, vmax=vmax, cmap="inferno")
                if obstacles:
                    ax.contour(np.linspace(0, col.extent[1], p.nx), np.linspace(0, col.extent[3], p.ny),
                               col.solid.astype(float), levels=[0.5], colors="w", linewidths=0.6)
                ax.set_xticks([]); ax.set_yticks([])
                if j == 0: ax.set_ylabel(f"{nm}\n{lab}", fontsize=8)
                if r == 0: ax.set_title(f"t = {rec.times[idx[j]]:.1f} s", fontsize=8)
        fig.tight_layout(); fig.savefig("poc/results/puff_pilot.png", dpi=110)
    print("done", flush=True)


if __name__ == "__main__":
    main(maxfev=int(sys.argv[1]) if len(sys.argv) > 1 else 40)
