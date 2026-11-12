"""Post-hoc, unregistered: the frozen joint floor (differential evolution from V0, 25 generations)
returned V0 itself on seven of fourteen cases, so I5 is vacuous. This computes a local floor by
Powell from V0 and from the hybrid terminal state, per case, and reports the better."""
from __future__ import annotations
import json, sys, time
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import grammar as G, rgre_gait as RG


def powell(case, st, maxfev):
    names = list(G.CLASSES["gait"]) + [p for c in case.repairable() for p in G.CLASSES[c]]
    lo = np.array([G.RANGES[p][0] for p in names]); hi = np.array([G.RANGES[p][1] for p in names])
    x0 = np.clip([getattr(st, p) for p in names], lo, hi)
    f = lambda x: case.error(replace(st, **{n: float(v) for n, v in zip(names, np.clip(x, lo, hi))}))
    r = minimize(f, x0, method="Powell", bounds=list(zip(lo, hi)), options=dict(maxfev=maxfev, xtol=1e-3, ftol=1e-5))
    return float(r.fun)


def one(rec):
    case = RG.GaitCase(rec["morph"], rec["seed"])
    v0 = replace(G.GaitState(), **json.load(open("poc/results/gait_v0.json"))["state"])
    hy = replace(G.GaitState(), **rec["variants"]["hybrid"]["state"])
    t0 = time.time()
    a = powell(case, v0, 3000); b = powell(case, hy, 3000)
    return dict(case=rec["case"], from_v0=a, from_hybrid=b, floor=min(a, b), seconds=round(time.time() - t0))


if __name__ == "__main__":
    d = json.load(open("poc/results/g1.json"))
    recs = [c for c in d["cases"] if c["designed"]]
    out = []
    with Pool(3) as pool:
        for r in pool.imap_unordered(one, recs):
            out.append(r); print(r, flush=True)
            json.dump(out, open("poc/results/g1_posthoc_floor.json", "w"), indent=1)
