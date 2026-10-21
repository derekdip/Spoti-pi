"""V0 for the 3D locomotion case: the walk base (five base classes) fitted once to the intact
teacher's seed-0 run by differential evolution. Saved to poc/results/gait3d_v0.json."""
from __future__ import annotations
import json, sys, time
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import rgre_gait3d as RG, grammar3d as G

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    out_path = sys.argv[2] if len(sys.argv) > 2 else RG.V0_PATH
    case = RG.GaitCase("intact", 0)
    t0 = time.time()
    st, e = RG.fit_base(case, seed=seed, maxiter=80, popsize=12)
    print(f"V0 fitted: error {e:.4f} (default state {case.error(G.GaitState()):.4f}) in {time.time()-t0:.0f}s, {case.evals} evaluations")
    print("per consumer", {k: round(v, 3) for k, v in case.per_consumer(st).items()})
    print({k: round(v, 3) for k, v in asdict(st).items() if k in G.BASE_PARAMS})
    json.dump(dict(state=asdict(st), error=e, evals=case.evals, seconds=round(time.time() - t0)), open(out_path, "w"), indent=1)
