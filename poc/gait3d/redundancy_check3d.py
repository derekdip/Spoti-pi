"""Parameter redundancy for the 3D grammar (poc/gait/redundancy_check.py on the 3D modules): does an impairment parameter move the consumers in a direction the walk base
already has? For each impairment class at its canonical on-state on top of V0, the finite-difference
tangent of every parameter is taken (the residual's direction per unit of the parameter, as
GaitCase.tangents does), and each class parameter's tangent is regressed on the span of the twenty
base-parameter tangents. redundancy(p) = 1 - |t_p - P_base t_p|^2 / |t_p|^2: 1.0 means the base can
move the consumers exactly as p does, at first order; 0 means p's direction is new. The class's own
step (on-state minus V0) is regressed the same way. Run on the seven design bodies at V0; a
pre-run check, no teacher fit involved beyond the consumer scales."""
from __future__ import annotations
import json, sys, time
from dataclasses import replace
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d as biped, grammar3d as G, rgre_gait3d as RG


def tangent(case, st, p):
    lo, hi = G.RANGES[p]; cur = getattr(st, p); h = RG.EPS[p]
    nxt = cur + h if cur + h <= hi else cur - h
    base = case.residual(st).ravel()
    return (case.residual(replace(st, **{p: nxt})).ravel() - base) / (nxt - cur)


def r2(t, B):
    if float(t @ t) == 0.0 or B.shape[1] == 0:
        return float("nan")
    beta, *_ = np.linalg.lstsq(B, t, rcond=None)
    return float(1.0 - ((t - B @ beta) ** 2).sum() / (t ** 2).sum())


def main(bodies=biped.MORPHS, out_path="poc/results/gait3d_redundancy_check.json"):
    v0 = RG.load_v0(); out = {}; T0 = time.time()
    for morph in bodies:
        case = RG.GaitCase(morph, 0); rep = case.repairable()
        out[morph] = {}
        for cls in G.IMPAIRMENTS:
            if cls not in rep: continue
            on = replace(v0, **G.ON[cls])
            cols = [tangent(case, on, p) for p in G.BASE_PARAMS if not (p in G.CLASSES["legs"] and "legs" not in rep)]
            B = np.stack([c for c in cols if float(c @ c) > 0], 1)
            row = {p: r2(tangent(case, on, p), B) for p in G.CLASSES[cls]}
            row["class step"] = r2(case.residual(on).ravel() - case.residual(v0).ravel(), B)
            out[morph][cls] = row
        print(f"{morph:<18} " + "  ".join(f"{cls} " + " ".join(f"{p.split('_',1)[1]} {v:.2f}" for p, v in row.items() if p != 'class step') + f" step {row['class step']:.2f}" for cls, row in out[morph].items()), flush=True)
    json.dump(out, open(out_path, "w"), indent=1)
    print(f"\nmedian redundancy over bodies (1.0 = the base has this direction; parameters over 0.9 add range, not direction):")
    for cls in G.IMPAIRMENTS:
        rows = [out[m][cls] for m in bodies if cls in out[m]]
        if not rows: continue
        print(f"  {cls:<6} " + "  ".join(f"{p:<12} {np.nanmedian([r[p] for r in rows]):.2f} (min {np.nanmin([r[p] for r in rows]):.2f})" for p in G.CLASSES[cls] + ["class step"]) + f"  n={len(rows)}")
    print(f"[{time.time()-T0:.0f}s]")


if __name__ == "__main__":
    main()
