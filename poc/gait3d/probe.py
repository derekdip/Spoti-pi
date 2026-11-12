"""Feasibility probes: run the 3D harness with planner constants overridden from the command line,
so that each iteration is one line in the run log.  python3 poc/gait3d/probe.py TAG morph[,morph] DURATION KEY=VALUE ..."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import mpc3d, biped3d, feasibility3d

tag, morphs, dur = sys.argv[1], sys.argv[2].split(","), float(sys.argv[3])
for kv in sys.argv[4:]:
    k, v = kv.split("=")
    target = mpc3d if hasattr(mpc3d, k) else biped3d
    assert hasattr(target, k), k
    setattr(target, k, type(getattr(target, k))(float(v)) if not isinstance(getattr(target, k), bool) else v == "1")
    if target is biped3d and k == "SPEED_TARGET": mpc3d.SPEED_TARGET = getattr(target, k)
print("overrides:", sys.argv[4:], flush=True)
feasibility3d.main(morphs, tag=tag, duration=dur)
