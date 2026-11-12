"""The linearisation gap in fire: how far each class's fitted repair ends from where its tangent
pointed, on the nine scenes at step zero. The contrast case for RGRE-ML-3's diagnostic: projection
selected well in fire (F3: 96 percent of the joint fit at one repair per step), so its gaps should
be small where it did. Post-hoc, no bar. Output poc/results/fire_lin_gap.{log,json}."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP
from poc.rgre.core import orth

SC = ["windy", "obstacle", "twin", "split", "shutoff", "ignition", "delayed_ignition", "full", "shelf_bed"]


def main():
    T0 = time.time(); out = []
    print(f"{'scene':<17} {'class':<9} {'q_c':>6} {'drop/e0':>8} {'gap':>6}")
    for nm in SC:
        case = RP.PuffCase(nm, getattr(scenes, nm)())
        v0 = puffs.PuffState()
        r0 = case.residual(v0).ravel(); E = float(r0 @ r0); e0 = case.error(v0)
        signed = case.tangents(v0)
        rows = {}
        for c in RP.CLASSES:
            if c == "bed" and not case.patches: continue
            if c == "deflect" and not case.obstacles: continue
            if c == "attract" and len(case.burners) < 2: continue
            if c not in signed: continue
            Q = orth(signed[c])
            q_c = float(((Q.T @ r0) ** 2).sum() / E)
            g = RP.repair_gain(case, v0, c)
            delta = r0 - case.residual(g["state"]).ravel()
            dd = float(delta @ delta)
            gp = float(max(0.0, 1.0 - float(((Q.T @ delta) ** 2).sum()) / dd)) if dd > 0 else 1.0
            rows[c] = dict(q=q_c, drop=g["drop"] / e0, gap=gp)
            print(f"{nm:<17} {c:<9} {q_c:6.3f} {g['drop']/e0:8.3f} {gp:6.2f}", flush=True)
        oracle = max(rows, key=lambda c: rows[c]["drop"]); pick = max(rows, key=lambda c: rows[c]["q"])
        out.append(dict(scene=nm, rows=rows, oracle=oracle, pick=pick, value=rows[pick]["drop"] / rows[oracle]["drop"] if rows[oracle]["drop"] > 0 else 1.0))
        print(f"  -> oracle {oracle} (gap {rows[oracle]['gap']:.2f}) pick {pick} (gap {rows[pick]['gap']:.2f}) value {out[-1]['value']:.2f}  [{time.time()-T0:.0f}s]", flush=True)
        json.dump(out, open("poc/results/fire_lin_gap.json", "w"), indent=1)
    by = {}
    for o in out:
        for c, r in o["rows"].items():
            by.setdefault(c, []).append(r["gap"])
    print("\nmedian gap by class:", {c: round(float(np.median(v)), 2) for c, v in by.items()})
    go = [o["rows"][o["oracle"]]["gap"] for o in out]
    print(f"gap of the oracle's class: median {np.median(go):.2f}; value captured median {np.median([o['value'] for o in out]):.2f}")


if __name__ == "__main__":
    main()
