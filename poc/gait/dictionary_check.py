"""The dictionary check for the gait grammar, in two parts.

Gap (docs/linearisation-gap.md): on every design body at V0, fit every repairable class once and
measure how much of its fitted repair lies outside the tangent span the projection would read.

Exclusivity (G2, from docs/math-track-g1-results.md): for every ordered pair of classes (A, B) on a
body, fit A to the teacher, then ask B to reproduce what A did: score B against the consumers of
the A-fitted state, starting from V0. absorption(B | A) = 1 - e(B*) / e(V0) on that target, the
share of A's effect that B can produce. Two classes that absorb each other above about a half
cannot be told apart by any selection rule, whatever the residual says.

Output: poc/results/gait_dictionary_check.{json,log}.
"""
from __future__ import annotations
import json, sys, time
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


def main(bodies=biped.MORPHS, out_path="poc/results/gait_dictionary_check.json"):
    v0 = RG.load_v0()
    out = {}
    T0 = time.time()
    print(f"{'body':<18} {'class':<6} {'q':>6} {'drop/e0':>8} {'gap':>5} {'side':>5}")
    for morph in bodies:
        case = RG.GaitCase(morph, 0)
        e0 = case.error(v0); r0 = case.residual(v0).ravel(); E = float(r0 @ r0)
        signed = case.tangents(v0)
        rows, fitted = {}, {}
        for c in case.repairable():
            if c not in signed: continue
            Q = orth(signed[c]); q = float(((Q.T @ r0) ** 2).sum() / E)
            g = RG.repair_gain(case, v0, c)
            delta = r0 - case.residual(g["state"]).ravel()
            rows[c] = dict(q=q, drop=g["drop"] / e0, gap=gap_of(delta, signed[c]), e1=g["e1"], side=G.side_sign(g["state"], c))
            fitted[c] = g["state"]
            print(f"{morph:<18} {c:<6} {q:6.3f} {g['drop']/e0:8.3f} {rows[c]['gap']:5.2f} {rows[c]['side']:5d}   [{time.time()-T0:.0f}s]", flush=True)
        # exclusivity: what B can do of what A did
        absorb = {}
        for a, sa in fitted.items():
            if a in G.V0_CLASSES or rows[a]["drop"] < 0.01:
                continue                          # base re-fits are not named; a repair that did nothing has nothing to absorb
            ca = case.with_target(case._consumers(sa))
            ea = ca.error(v0)
            absorb[a] = {}
            for b in fitted:
                if b == a or b in ("rhythm", "torso", "arms"): continue     # legs is the base class that can absorb an impairment
                sb, eb = RG.fit_class(ca, v0, b)
                absorb[a][b] = float(max(0.0, 1.0 - eb / ea)) if ea > 1e-9 else 0.0
            print(f"  {morph}: of {a}'s effect, " + ", ".join(f"{b} absorbs {v:.2f}" for b, v in absorb[a].items()) + f"   [{time.time()-T0:.0f}s]", flush=True)
        oracle = max(rows, key=lambda c: rows[c]["drop"]) if rows else None
        pick = max(rows, key=lambda c: rows[c]["q"]) if rows else None
        out[morph] = dict(e0=e0, rows=rows, absorb=absorb, oracle=oracle, pick=pick)
        print(f"  -> {morph}: e0 {e0:.3f}; oracle {oracle} (drop {rows[oracle]['drop']:.3f}, gap {rows[oracle]['gap']:.2f}, side {rows[oracle]['side']}); projection {pick}", flush=True)
        json.dump(out, open(out_path, "w"), indent=1)
    by = {}
    for m in out.values():
        for c, r in m["rows"].items():
            if r["drop"] >= 0.01:
                by.setdefault(c, []).append(r["gap"])
    print("\nmedian gap by class over repairs worth >= 1%:", {c: round(float(np.median(v)), 2) for c, v in sorted(by.items(), key=lambda kv: np.median(kv[1]))})
    pair = {}
    for m in out.values():
        for a, row in m["absorb"].items():
            for b, v in row.items():
                pair.setdefault((a, b), []).append(v)
    print("median absorption over bodies, B of A's effect (pairs over 0.5 are not separable):")
    for (a, b), v in sorted(pair.items(), key=lambda kv: -np.median(kv[1])):
        print(f"  {b:<6} absorbs {a:<6} {np.median(v):.2f}  (n={len(v)})")


if __name__ == "__main__":
    import sys
    main(out_path=sys.argv[1] if len(sys.argv) > 1 else "poc/results/gait_dictionary_check.json")
