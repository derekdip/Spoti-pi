"""V0 for the locomotion case: the walk base fitted once to the intact teacher by differential
evolution over the gait class, as the fire's V0 was calibrated on the bare plume. Saved to
poc/results/gait_v0.json and used as the starting state of every body."""
from __future__ import annotations
import json, sys, time
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import rgre_gait as RG, grammar as G

if __name__ == "__main__":
    case = RG.GaitCase("intact", 0)
    t0 = time.time()
    st, e = RG.fit_base(case, seed=0, maxiter=60, popsize=12)
    print(f"V0 fitted: error {e:.4f} (default state {case.error(G.GaitState()):.4f}) in {time.time()-t0:.0f}s, {case.evals} evaluations")
    print("per consumer", {k: round(v, 3) for k, v in case.per_consumer(st).items()})
    print({k: round(v, 3) for k, v in asdict(st).items() if k in G.BASE_PARAMS})
    json.dump(dict(state=asdict(st), error=e, evals=case.evals, seconds=round(time.time() - t0)), open("poc/results/gait_v0.json", "w"), indent=1)
