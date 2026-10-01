"""G3 frozen scorer. Committed with the preregistration, run once. Compares the checked path with
G2's oracle path on the same teachers (poc/results/g2.json)."""
from __future__ import annotations
import json, sys
import numpy as np

BASE = ("rhythm", "legs", "torso", "arms")


def hit(entry, c):
    cls, side = entry
    return cls == c["designed"] and (c["designed_sign"] == 0 or side == c["designed_sign"])


def main(path, g2_path="poc/results/g2.json"):
    d = json.load(open(path)); C = d["cases"]
    g2 = {c["case"]: c for c in json.load(open(g2_path))["cases"]}
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G3 scored: {len(C)} cases, {d['STEPS']} steps\n")
    imps = lambda c: [e for e in c["added"] if e[0] not in BASE]
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    damaged = [c for c in C if c["designed"] or c["morph"].startswith("short_shank")]
    controls = [c for c in C if not c["designed"] and not c["morph"].startswith("short_shank")]
    # ---- K1 identity, as G2's bars
    P("## K1 identity on the checked path: first impairment repair, within two, and on the mirrors")
    for c in design + mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  checked {fmt(c['added'])} | G2 oracle {fmt(g2[c['case']]['variants']['oracle']['added'])}")
    k1a = sum(bool(imps(c)) and hit(imps(c)[0], c) for c in design)
    k1b = sum(any(hit(e, c) for e in imps(c)[:2]) for c in design)
    k1c = sum(any(hit(e, c) for e in imps(c)[:2]) for c in mirrors)
    k1 = k1a >= 3 and k1b >= 3 and k1c >= 2
    P(f"-> K1 {'pass' if k1 else 'FAIL'}: first {k1a} of 4 (>= 3), within two {k1b} of 4 (>= 3), mirrors {k1c} of 3 (>= 2)\n")
    # ---- K2 consumers
    P("## K2 consumers at the checked terminal against V0, damaged bodies")
    strict = 0; within = 0
    for c in damaged:
        worse = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        beyond = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + c["tolerance"][k]]
        strict += not worse; within += not beyond
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}{'' if not beyond else ' | beyond tolerance: ' + ', '.join(beyond)}")
    k2 = strict >= 6 and within >= 8
    P(f"-> K2 {'pass' if k2 else 'FAIL'}: none worse on {strict} of {len(damaged)} (>= 6), none beyond tolerance on {within} of {len(damaged)} (>= 8)\n")
    # ---- K3 controls
    P("## K3 controls: impairment classes added")
    bad = 0
    for c in controls:
        bad += bool(imps(c))
        P(f"  {c['case']:<20} checked {fmt(c['added'])} ({c['e_v0']:.3f} -> {c['e_final']:.3f}, held-out {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f}) | G2 oracle {fmt(g2[c['case']]['variants']['oracle']['added'])}")
    k3 = bad <= 1
    P(f"-> K3 {'pass' if k3 else 'FAIL'}: impairment classes on {bad} of {len(controls)} controls (<= 1)\n")
    # ---- K4 held-out
    P("## K4 held-out error at the terminal below V0's, damaged bodies")
    gen = 0
    for c in damaged:
        gen += c["e_final_heldout"] < c["e_v0_heldout"]
        P(f"  {c['case']:<20} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} | held-out {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f} | G2 oracle fit {g2[c['case']]['variants']['oracle']['e_final']:.3f}")
    k4 = gen >= 8
    P(f"-> K4 {'pass' if k4 else 'FAIL'}: {gen} of {len(damaged)} (>= 8)\n")
    # ---- reported
    steps = [s for c in C for s in c["steps"]]
    reasons = {}
    for s in steps:
        for r in s["rejected"].values():
            reasons[r.split(":")[0].split(" ")[0]] = reasons.get(r.split(":")[0].split(" ")[0], 0) + 1
    P("## Reported")
    P(f"  repairs applied per case, median {np.median([len(c['added']) for c in C]):.0f} (G2 oracle: {np.median([len(g2[c['case']]['variants']['oracle']['added']) for c in C]):.0f}); rejections by reason {reasons}")
    P(f"  value of the applied repair against the best fitting drop, median {np.median([s['value'] for s in steps if s.get('pick')]):.2f}")
    a, b = k1, k2
    letter = "A" if (a and b) else ("B" if a else ("C" if b else "D"))
    P(f"\n## Outcome (frozen tree): K1 {'pass' if a else 'fail'}, K2 {'pass' if b else 'fail'} -> {letter}; K3 {'pass' if k3 else 'fail'}, K4 {'pass' if k4 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g3.json")
