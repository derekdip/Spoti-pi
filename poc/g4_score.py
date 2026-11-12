"""G4 frozen scorer. Committed with the preregistration, run once. Compares the two-run path with
G3's one-run path on the same fitting teachers (poc/results/g3.json). The declared pilot case is
excluded from every bar."""
from __future__ import annotations
import json, sys
import numpy as np

BASE = ("rhythm", "legs", "torso", "arms")
PILOT = "nolegs_s1"
G3_CONTROL_IMPAIRMENTS = 5   # vault, weak on intact_s0; stiff, weak, kneel on weak_hip_right_s0


def hit(entry, c):
    cls, side = entry
    return cls == c["designed"] and (c["designed_sign"] == 0 or side == c["designed_sign"])


def main(path, g3_path="poc/results/g3.json"):
    d = json.load(open(path)); C = [c for c in d["cases"] if c["case"] != PILOT]
    g3 = {c["case"]: c for c in json.load(open(g3_path))["cases"]}
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G4 scored: {len(C)} cases ({PILOT} excluded as the declared pilot), {d['STEPS']} steps\n")
    imps = lambda c: [e for e in c["added"] if e[0] not in BASE]
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    damaged = [c for c in C if c["designed"] or c["morph"].startswith("short_shank")]
    controls = [c for c in C if not c["designed"] and not c["morph"].startswith("short_shank")]
    n_dam = len(damaged); bar = 7
    # ---- K1 identity, as G2's and G3's bars
    P("## K1 identity: first impairment repair, within two, and on the mirrors")
    for c in design + mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  two-run {fmt(c['added'])} | G3 one-run {fmt(g3[c['case']]['added'])}")
    k1a = sum(bool(imps(c)) and hit(imps(c)[0], c) for c in design)
    k1b = sum(any(hit(e, c) for e in imps(c)[:2]) for c in design)
    k1c = sum(any(hit(e, c) for e in imps(c)[:2]) for c in mirrors)
    k1 = k1a >= 3 and k1b >= 3 and k1c >= 2
    P(f"-> K1 {'pass' if k1 else 'FAIL'}: first {k1a} of 4 (>= 3), within two {k1b} of 4 (>= 3), mirrors {k1c} of 3 (>= 2)\n")
    # ---- K2 consumers: tolerance clause only
    P("## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance")
    strict = 0; within = 0
    for c in damaged:
        worse = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        beyond = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + c["tolerance"][k]]
        strict += not worse; within += not beyond
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}{'' if not beyond else ' | BEYOND tolerance: ' + ', '.join(beyond)}")
    k2 = within >= bar
    P(f"-> K2 {'pass' if k2 else 'FAIL'}: none beyond tolerance on {within} of {n_dam} (>= {bar}); reported: none worse at all on {strict} of {n_dam} (G3: 3 of 10)\n")
    # ---- K3 controls: impairment repairs in total, against G3's count
    P("## K3 controls: impairment repairs added, in total against G3's")
    total = 0
    for c in controls:
        total += len(imps(c))
        P(f"  {c['case']:<20} two-run {fmt(c['added'])} ({c['e_v0']:.3f} -> {c['e_final']:.3f}, held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f}) | G3 one-run {fmt(g3[c['case']]['added'])}")
    k3 = total <= G3_CONTROL_IMPAIRMENTS
    P(f"-> K3 {'pass' if k3 else 'FAIL'}: {total} impairment repairs on {len(controls)} controls (<= {G3_CONTROL_IMPAIRMENTS})\n")
    # ---- K4 held-out
    P("## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)")
    gen = 0; both = 0
    for c in damaged:
        gen += c["e_final_heldout"] < c["e_v0_heldout"]
        b = sum(a < v for a, v in zip(c["e_final_heldout_runs"], c["e_v0_heldout_runs"])); both += b == 2
        P(f"  {c['case']:<20} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} | held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f}, runs "
          + ", ".join(f"{v:.3f}->{a:.3f}" for v, a in zip(c['e_v0_heldout_runs'], c['e_final_heldout_runs'])) + f" ({b} of 2 lower) | G3 one-run held-out {g3[c['case']]['e_v0_heldout']:.3f} -> {g3[c['case']]['e_final_heldout']:.3f}")
    k4 = gen >= bar
    P(f"-> K4 {'pass' if k4 else 'FAIL'}: {gen} of {n_dam} (>= {bar}); both runs lower on {both} of {n_dam}\n")
    # ---- reported
    steps = [s for c in C for s in c["steps"]]
    reasons = {}
    for s in steps:
        for r in s["rejected"].values():
            key = r.split(":")[0].split(" ")[0]; reasons[key] = reasons.get(key, 0) + 1
    agree = [s["agree"] for s in steps if s.get("pick")]
    P("## Reported")
    P(f"  repairs applied per case, median {np.median([len(c['added']) for c in C]):.0f} (G3: {np.median([len(g3[c['case']]['added']) for c in C]):.0f}); rejections by reason {reasons}")
    P(f"  applied repairs lowering both held-out runs {sum(a == 2 for a in agree)} of {len(agree)}, one run {sum(a == 1 for a in agree)}, neither {sum(a == 0 for a in agree)}")
    P(f"  value of the applied repair against the best fitting drop, median {np.median([s['value'] for s in steps if s.get('pick')]):.2f}")
    for c in mirrors + design:
        where = [i for i, e in enumerate(imps(c)) if hit(e, c)]
        P(f"  {c['case']:<20} designed class arrives as impairment repair {where[0] + 1 if where else 'never'} (G3: {[i for i, e in enumerate([e for e in g3[c['case']]['added'] if e[0] not in BASE]) if hit(e, c)][:1] or ['never']})")
    a, b = k1, k2
    letter = "A" if (a and b) else ("B" if a else ("C" if b else "D"))
    P(f"\n## Outcome (frozen tree): K1 {'pass' if a else 'fail'}, K2 {'pass' if b else 'fail'} -> {letter}; K3 {'pass' if k3 else 'fail'}, K4 {'pass' if k4 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g4.json")
