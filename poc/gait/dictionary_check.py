"""The dictionary check for the gait grammar (docs/linearisation-gap.md): on every design body at
V0, fit every repairable class once and measure how much of its fitted repair lies outside the
tangent span the projection would read. Classes over 0.25 are fitted to be ranked; the rest are
projected. Also records each class's drop, so the table doubles as the step-zero oracle."""
from __future__ import annotations
import json, sys, time
from dataclasses import replace
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import biped, grammar as G, rgre_gait as RG
from poc.rgre.core import orth


def gap_of(f, vs):
    Q = orth(vs); ff = float(f @ f)
    if ff <= 0 or Q.shape[1] == 0: return 1.0
    p = Q.T @ f
    return float(max(0.0, 1.0 - float(p @ p) / ff))


def main(bodies=biped.MORPHS):
    v0 = replace(G.GaitState(), **json.load(open("poc/results/gait_v0.json"))["state"])
    out = {}
    T0 = time.time()
    print(f"{'body':<18} {'class':<8} {'q':>6} {'drop/e0':>8} {'gap':>5}")
    for morph in bodies:
        case = RG.GaitCase(morph, 0)
        e0 = case.error(v0); r0 = case.residual(v0).ravel(); E = float(r0 @ r0)
        signed = case.tangents(v0)
        rows = {}
        for c in case.repairable():
            if c not in signed: continue
            Q = orth(signed[c]); q = float(((Q.T @ r0) ** 2).sum() / E)
            g = RG.repair_gain(case, v0, c)
            delta = r0 - case.residual(g["state"]).ravel()
            rows[c] = dict(q=q, drop=g["drop"] / e0, gap=gap_of(delta, signed[c]), e1=g["e1"])
            print(f"{morph:<18} {c:<8} {q:6.3f} {g['drop']/e0:8.3f} {rows[c]['gap']:5.2f}   [{time.time()-T0:.0f}s]", flush=True)
        oracle = max(rows, key=lambda c: rows[c]["drop"]) if rows else None
        pick = max(rows, key=lambda c: rows[c]["q"]) if rows else None
        out[morph] = dict(e0=e0, rows=rows, oracle=oracle, pick=pick, per_consumer=case.per_consumer(v0))
        print(f"  -> {morph}: e0 {e0:.3f}; oracle {oracle} (drop {rows[oracle]['drop']:.3f}, gap {rows[oracle]['gap']:.2f}); projection {pick}", flush=True)
        json.dump(out, open("poc/results/gait_dictionary_check.json", "w"), indent=1)
    by = {}
    for m in out.values():
        for c, r in m["rows"].items():
            by.setdefault(c, []).append(r["gap"])
    print("\nmedian gap by class:", {c: round(float(np.median(v)), 2) for c, v in sorted(by.items(), key=lambda kv: np.median(kv[1]))})


if __name__ == "__main__":
    main()
