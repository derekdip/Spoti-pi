"""Is the hop class a reparametrisation of the walk base? Every hop parameter enters joint_angles
through a base parameter: freq * hop_rate, phase_r * (1 - hop_sync), knee_off + hop_crouch, and
hop_flight * max(0, sin 2phi) inside the same max(0, .) as bob_amp * sin 2phi. So a state with hop on
has an exact base-only twin: freq <- freq * rate, phase_r <- phase_r * (1 - sync), knee_off <-
knee_off + crouch, bob_amp <- bob_amp + flight, hop off. This script builds the twin for the hop
on-state on every body that can hop, and for every terminal state of G3 and G4 that has hop on, and
reports the largest difference between their consumer vectors, at the consumers' own scale.
Ranges are ignored: the twin may lie outside the base's RANGES, which is the range hop adds.
Runs against the grammar with the hop class in it, commit 388686e or earlier; after G5 removed the
class this script is the record of why."""
from __future__ import annotations
import json, sys
from dataclasses import replace
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import biped, grammar as G, rgre_gait as RG


def twin(st: G.GaitState) -> G.GaitState:
    return replace(st, freq=st.freq * st.hop_rate, phase_r=st.phase_r * (1.0 - st.hop_sync), knee_off=st.knee_off + st.hop_crouch,
                   bob_amp=st.bob_amp + st.hop_flight, hop_sync=0.0, hop_crouch=0.0, hop_flight=0.0, hop_rate=1.0)


def diff(case, a, b):
    pa, pb = RG.consumers(case.body, G.trajectory(a, case.body)), RG.consumers(case.body, G.trajectory(b, case.body))
    return max(float(np.abs(pa[k] - pb[k]).max() / case.scale[k]) for k in case.names)


def main():
    v0 = RG.load_v0(); rows = []
    for morph in biped.MORPHS + biped.MIRRORS:
        case = RG.GaitCase(morph, 0)
        if "hop" not in case.repairable(): continue
        on = replace(v0, **G.ON["hop"])
        rows.append((f"{morph} hop on-state", diff(case, on, twin(on)), diff(case, on, v0)))
    for exp in ("g3", "g4"):
        for c in json.load(open(f"poc/results/{exp}.json"))["cases"]:
            st = G.GaitState(**c["state"])
            if G.is_on(st, "hop"):
                case = RG.GaitCase(c["morph"], c["seed"])
                rows.append((f"{exp} terminal {c['case']}", diff(case, st, twin(st)), diff(case, st, v0)))
    print(f"{'state':<36} {'|state - twin|':>15} {'|state - V0|':>14}   (max over consumers, in scale units)")
    for name, d, d0 in rows:
        print(f"{name:<36} {d:>15.2e} {d0:>14.3f}")
    json.dump([dict(state=n, twin_diff=d, v0_diff=d0) for n, d, d0 in rows], open("poc/results/gait_hop_equivalence.json", "w"), indent=1)


if __name__ == "__main__":
    main()
