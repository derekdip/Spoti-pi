"""G5 frozen scorer. Committed with the preregistration, run once. Compares the hop-less grammar's
path with G4's on the same fitting teachers (poc/results/g4.json). The declared pilot case is
excluded from every bar. The one-leg bodies have no designed class."""
from __future__ import annotations
import json, sys
import numpy as np

BASE = ("rhythm", "legs", "torso", "arms")
PILOT = "nolegs_s1"
G4_CONTROL_IMPAIRMENTS = 4   # vault on intact_s0; stiff, weak, kneel on weak_hip_right_s0
ONE_LEG = ("noleg_left_s0", "noleg_right_s0")


def hit(entry, c):
    cls, side = entry
    return cls == c["designed"] and (c["designed_sign"] == 0 or side == c["designed_sign"])


def main(path, g4_path="poc/results/g4.json"):
    d = json.load(open(path)); C = [c for c in d["cases"] if c["case"] != PILOT]
    g4 = {c["case"]: c for c in json.load(open(g4_path))["cases"]}
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G5 scored: {len(C)} cases ({PILOT} excluded as the declared pilot), {d['STEPS']} steps\n")
    imps = lambda c: [e for e in c["added"] if e[0] not in BASE]
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    damaged = [c for c in C if c["designed"] or c["morph"].startswith("short_shank") or c["morph"].startswith("noleg")]
    controls = [c for c in C if c["case"] not in [x["case"] for x in damaged]]
    n_dam = len(damaged); bar = 7
    # ---- K1 identity
    P("## K1 identity: first impairment repair, within two, and on the mirrors")
    for c in design + mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  G5 {fmt(c['added'])} | G4 {fmt(g4[c['case']]['added'])}")
    k1a = sum(bool(imps(c)) and hit(imps(c)[0], c) for c in design)
    k1b = sum(any(hit(e, c) for e in imps(c)[:2]) for c in design)
    k1c = sum(any(hit(e, c) for e in imps(c)[:2]) for c in mirrors)
    k1 = k1a >= 2 and k1b >= 3 and k1c >= 2
    P(f"-> K1 {'pass' if k1 else 'FAIL'}: first {k1a} of {len(design)} (>= 2), within two {k1b} of {len(design)} (>= 3), mirrors {k1c} of {len(mirrors)} (>= 2)\n")
    # ---- K5 the round's claim: the one-leg bodies lose nothing without hop, and the right stump needs no guard
    P("## K5 one-leg bodies: terminal fitting error against G4's (hop in the grammar), and the right stump's first repair")
    k5n = 0
    for c in C:
        if c["case"] in ONE_LEG:
            ok = c["e_final"] <= g4[c["case"]]["e_final"] + 0.01 * c["e_v0"]; k5n += ok
            P(f"  {c['case']:<20} G5 {c['e_v0']:.3f} -> {c['e_final']:.3f} {fmt(c['added'])} | G4 -> {g4[c['case']]['e_final']:.3f} {fmt(g4[c['case']]['added'])} | {'within' if ok else 'ABOVE'} one percent of V0")
    sr = [c for c in C if c["case"] == "stump_right_s0"][0]
    guard_hits = [(s["t"], k, r) for s in sr["steps"] for k, r in s["rejected"].items() if r.startswith("guard")]
    P(f"  stump_right_s0       first impairment repair {fmt(imps(sr)[:1])}, guard rejections {guard_hits or 'none'} (G4: hop rejected by the guard on reach at step 0)")
    k5 = k5n == 2
    P(f"-> K5 {'pass' if k5 else 'FAIL'}: {k5n} of 2 one-leg bodies within one percent of V0 of G4's terminal\n")
    # ---- K2 consumers: tolerance clause
    P("## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance")
    strict = 0; within = 0
    for c in damaged:
        worse = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        beyond = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + c["tolerance"][k]]
        strict += not worse; within += not beyond
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}{'' if not beyond else ' | BEYOND tolerance: ' + ', '.join(beyond)}")
    k2 = within >= bar
    P(f"-> K2 {'pass' if k2 else 'FAIL'}: none beyond tolerance on {within} of {n_dam} (>= {bar}); reported: none worse at all on {strict} of {n_dam} (G4: 2 of 9)\n")
    # ---- K3 controls
    P("## K3 controls: impairment repairs added, in total against G4's")
    total = 0
    for c in controls:
        total += len(imps(c))
        P(f"  {c['case']:<20} G5 {fmt(c['added'])} ({c['e_v0']:.3f} -> {c['e_final']:.3f}, held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f}) | G4 {fmt(g4[c['case']]['added'])}")
    k3 = total <= G4_CONTROL_IMPAIRMENTS
    P(f"-> K3 {'pass' if k3 else 'FAIL'}: {total} impairment repairs on {len(controls)} controls (<= {G4_CONTROL_IMPAIRMENTS})\n")
    # ---- K4 held-out
    P("## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)")
    gen = 0; both = 0
    for c in damaged:
        gen += c["e_final_heldout"] < c["e_v0_heldout"]
        b = sum(a < v for a, v in zip(c["e_final_heldout_runs"], c["e_v0_heldout_runs"])); both += b == 2
        P(f"  {c['case']:<20} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} | held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f} ({b} of 2 lower) | G4 fit -> {g4[c['case']]['e_final']:.3f}, held-out -> {g4[c['case']]['e_final_heldout']:.3f}")
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
    P(f"  repairs applied per case, median {np.median([len(c['added']) for c in C]):.0f} (G4: {np.median([len(g4[c['case']]['added']) for c in C]):.0f}); rejections by reason {reasons}")
    P(f"  applied repairs lowering both held-out runs {sum(a == 2 for a in agree)} of {len(agree)}, one run {sum(a == 1 for a in agree)}")
    P(f"  value of the applied repair against the best fitting drop, median {np.median([s['value'] for s in steps if s.get('pick')]):.2f}")
    P(f"  terminal fitting error, G5 against G4, every case: " + "; ".join(f"{c['case']} {c['e_final']:.3f}/{g4[c['case']]['e_final']:.3f}" for c in C))
    letter = "A" if (k1 and k5) else ("B" if k1 else ("C" if k5 else "D"))
    P(f"\n## Outcome (frozen tree): K1 {'pass' if k1 else 'fail'}, K5 {'pass' if k5 else 'fail'} -> {letter}; K2 {'pass' if k2 else 'fail'}, K3 {'pass' if k3 else 'fail'}, K4 {'pass' if k4 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g5.json")
