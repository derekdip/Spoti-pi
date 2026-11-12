"""G6 frozen scorer. Committed with the preregistration, run once. Compares the hop-less grammar's
path, ranges as G4's, with G4 on the same fitting teachers (poc/results/g4.json). The declared
pilot case is excluded from every bar. The one-leg bodies have no designed class."""
from __future__ import annotations
import json, sys
import numpy as np

BASE = ("rhythm", "legs", "torso", "arms")
PILOT = "nolegs_s1"
G4_CONTROL_IMPAIRMENTS = 4
HOP_CASE = "noleg_left_s0"        # the one G4 case whose path used hop; every other scored case must reproduce G4
REPRO_TOL = 1e-6


def hit(entry, c):
    cls, side = entry
    return cls == c["designed"] and (c["designed_sign"] == 0 or side == c["designed_sign"])


def main(path, g4_path="poc/results/g4.json"):
    d = json.load(open(path)); C = [c for c in d["cases"] if c["case"] != PILOT]
    g4 = {c["case"]: c for c in json.load(open(g4_path))["cases"]}
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G6 scored: {len(C)} cases ({PILOT} excluded as the declared pilot), {d['STEPS']} steps\n")
    imps = lambda c: [e for e in c["added"] if e[0] not in BASE]
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    damaged = [c for c in C if c["designed"] or c["morph"].startswith("short_shank") or c["morph"].startswith("noleg")]
    controls = [c for c in C if c["case"] not in [x["case"] for x in damaged]]
    n_dam = len(damaged); bar = 7
    # ---- K6 reproduction: every case but the hop case reproduces G4's repairs and terminal error
    P("## K6 reproduction of G4 on every case that never used hop")
    rep = 0
    for c in C:
        same = [tuple(e) for e in c["added"]] == [tuple(e) for e in g4[c["case"]]["added"]] and abs(c["e_final"] - g4[c["case"]]["e_final"]) < REPRO_TOL
        if c["case"] != HOP_CASE: rep += same
        P(f"  {c['case']:<20} {'same' if same else 'DIFFERS'}: G6 {fmt(c['added'])} {c['e_final']:.6f} | G4 {fmt(g4[c['case']]['added'])} {g4[c['case']]['e_final']:.6f}{'  (the hop case, not counted)' if c['case'] == HOP_CASE else ''}")
    k6 = rep == len(C) - 1
    P(f"-> K6 {'pass' if k6 else 'FAIL'}: {rep} of {len(C) - 1} reproduce G4 (all required)\n")
    # ---- K5 the hop case
    P("## K5 the left one-leg body without hop: terminal fitting error against G4's")
    hc = [c for c in C if c["case"] == HOP_CASE][0]
    k5 = hc["e_final"] <= g4[HOP_CASE]["e_final"] + 0.01 * hc["e_v0"]
    P(f"  {HOP_CASE:<20} G6 {hc['e_v0']:.3f} -> {hc['e_final']:.3f} {fmt(hc['added'])} | G4 -> {g4[HOP_CASE]['e_final']:.3f} {fmt(g4[HOP_CASE]['added'])} | held-out mean {hc['e_v0_heldout']:.3f} -> {hc['e_final_heldout']:.3f} (G4 -> {g4[HOP_CASE]['e_final_heldout']:.3f})")
    for s in hc["steps"]:
        top = sorted(s["drops"].items(), key=lambda kv: -kv[1])[:4]
        P(f"    t{s['t']} pick {s.get('pick')} top drops {[(k, round(v, 3)) for k, v in top]} rejected {[(k, v[:24]) for k, v in s['rejected'].items() if v != 'spent']}")
    P(f"-> K5 {'pass' if k5 else 'FAIL'}: {'within' if k5 else 'above'} one percent of V0 of G4's terminal\n")
    # ---- K1 identity
    P("## K1 identity: first impairment repair, within two, and on the mirrors")
    for c in design + mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  G6 {fmt(c['added'])}")
    k1a = sum(bool(imps(c)) and hit(imps(c)[0], c) for c in design)
    k1b = sum(any(hit(e, c) for e in imps(c)[:2]) for c in design)
    k1c = sum(any(hit(e, c) for e in imps(c)[:2]) for c in mirrors)
    k1 = k1a >= 2 and k1b >= 3 and k1c >= 2
    P(f"-> K1 {'pass' if k1 else 'FAIL'}: first {k1a} of {len(design)} (>= 2), within two {k1b} of {len(design)} (>= 3), mirrors {k1c} of {len(mirrors)} (>= 2)\n")
    # ---- K2, K3, K4 as G5
    P("## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance")
    strict = 0; within = 0
    for c in damaged:
        worse = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        beyond = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + c["tolerance"][k]]
        strict += not worse; within += not beyond
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}{'' if not beyond else ' | BEYOND tolerance: ' + ', '.join(beyond)}")
    k2 = within >= bar
    P(f"-> K2 {'pass' if k2 else 'FAIL'}: none beyond tolerance on {within} of {n_dam} (>= {bar}); none worse at all on {strict} of {n_dam}\n")
    P("## K3 controls: impairment repairs added, in total against G4's")
    total = 0
    for c in controls:
        total += len(imps(c))
        P(f"  {c['case']:<20} G6 {fmt(c['added'])} ({c['e_v0']:.3f} -> {c['e_final']:.3f}, held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f})")
    k3 = total <= G4_CONTROL_IMPAIRMENTS
    P(f"-> K3 {'pass' if k3 else 'FAIL'}: {total} impairment repairs on {len(controls)} controls (<= {G4_CONTROL_IMPAIRMENTS})\n")
    P("## K4 held-out error at the terminal below V0's, damaged bodies")
    gen = 0; both = 0
    for c in damaged:
        gen += c["e_final_heldout"] < c["e_v0_heldout"]
        b = sum(a < v for a, v in zip(c["e_final_heldout_runs"], c["e_v0_heldout_runs"])); both += b == 2
        P(f"  {c['case']:<20} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} | held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f} ({b} of 2 lower)")
    k4 = gen >= bar
    P(f"-> K4 {'pass' if k4 else 'FAIL'}: {gen} of {n_dam} (>= {bar}); both runs lower on {both} of {n_dam}\n")
    steps = [s for c in C for s in c["steps"]]
    reasons = {}
    for s in steps:
        for r in s["rejected"].values():
            key = r.split(":")[0].split(" ")[0]; reasons[key] = reasons.get(key, 0) + 1
    P("## Reported")
    P(f"  repairs applied per case, median {np.median([len(c['added']) for c in C]):.0f}; rejections by reason {reasons}; value median {np.median([s['value'] for s in steps if s.get('pick')]):.2f}")
    letter = "A" if (k6 and k5) else ("B" if k6 else ("C" if k5 else "D"))
    P(f"\n## Outcome (frozen tree): K6 {'pass' if k6 else 'fail'}, K5 {'pass' if k5 else 'fail'} -> {letter}; K1 {'pass' if k1 else 'fail'}, K2 {'pass' if k2 else 'fail'}, K3 {'pass' if k3 else 'fail'}, K4 {'pass' if k4 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g6.json")
