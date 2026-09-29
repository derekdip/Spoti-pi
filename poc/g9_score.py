"""G9 frozen scorer. Committed with the preregistration, run once. Bars as G7's; G7's run on the same
teachers (poc/results/g7.json) is the comparison. The declared pilot case is excluded from every bar."""
from __future__ import annotations
import json, sys
import numpy as np

BASE = ("rhythm", "legs", "lateral", "torso", "arms")
PILOT = "nolegs_s1"
CONTROL_BAR = 4


def hit(entry, c):
    cls, side = entry
    return cls == c["designed"] and (c["designed_sign"] == 0 or side == c["designed_sign"])


def main(path, g7_path="poc/results/g7.json"):
    d = json.load(open(path)); C = [c for c in d["cases"] if c["case"] != PILOT]
    g7 = {c["case"]: c for c in json.load(open(g7_path))["cases"]}
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G9 scored: {len(C)} cases ({PILOT} excluded as the declared pilot), {d['STEPS']} steps, \n")
    imps = lambda c: [e for e in c["added"] if e[0] not in BASE]
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    damaged = [c for c in C if c["designed"] or c["morph"].startswith("short_shank") or c["morph"].startswith("noleg")]
    controls = [c for c in C if c["case"] not in [x["case"] for x in damaged]]
    n_dam = len(damaged); bar = 7
    P("## K1 identity: first impairment repair, within two, and on the mirrors")
    for c in design + mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  G9 {fmt(c['added'])} | G7 {fmt(g7[c['case']]['added'])}")
    k1a = sum(bool(imps(c)) and hit(imps(c)[0], c) for c in design)
    k1b = sum(any(hit(e, c) for e in imps(c)[:2]) for c in design)
    k1c = sum(any(hit(e, c) for e in imps(c)[:2]) for c in mirrors)
    k1 = k1a >= 2 and k1b >= 3 and k1c >= 2
    P(f"-> K1 {'pass' if k1 else 'FAIL'}: first {k1a} of {len(design)} (>= 2), within two {k1b} of {len(design)} (>= 3), mirrors {k1c} of {len(mirrors)} (>= 2)\n")
    P("## K4 held-out error at the terminal below V0's, damaged bodies (mean of two runs; both runs reported)")
    gen = 0; both = 0
    for c in damaged:
        gen += c["e_final_heldout"] < c["e_v0_heldout"]
        b = sum(a < v for a, v in zip(c["e_final_heldout_runs"], c["e_v0_heldout_runs"])); both += b == 2
        P(f"  {c['case']:<20} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} | held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f}, runs "
          + ", ".join(f"{v:.3f}->{a:.3f}" for v, a in zip(c['e_v0_heldout_runs'], c['e_final_heldout_runs'])) + f" ({b} of 2 lower)")
    k4 = gen >= bar
    P(f"-> K4 {'pass' if k4 else 'FAIL'}: {gen} of {n_dam} (>= {bar}); both runs lower on {both} of {n_dam}\n")
    P("## K2 consumers at the terminal against V0, damaged bodies: none beyond its tolerance")
    strict = 0; within = 0
    for c in damaged:
        worse = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        beyond = [k for k, v in c["per_consumer"].items() if v > c["per_consumer_v0"][k] + c["tolerance"][k]]
        strict += not worse; within += not beyond
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}{'' if not beyond else ' | BEYOND tolerance: ' + ', '.join(beyond)}")
    k2 = within >= bar
    P(f"-> K2 {'pass' if k2 else 'FAIL'}: none beyond tolerance on {within} of {n_dam} (>= {bar}); none worse at all on {strict} of {n_dam}\n")
    P("## K3 controls: impairment repairs added, in total")
    total = 0
    for c in controls:
        total += len(imps(c))
        P(f"  {c['case']:<20} {fmt(c['added'])} ({c['e_v0']:.3f} -> {c['e_final']:.3f}, held-out mean {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f})")
    k3 = total <= CONTROL_BAR
    P(f"-> K3 {'pass' if k3 else 'FAIL'}: {total} impairment repairs on {len(controls)} controls (<= {CONTROL_BAR})\n")
    steps = [s for c in C for s in c["steps"]]
    reasons = {}
    for s in steps:
        for r in s["rejected"].values():
            key = r.split(":")[0].split(" ")[0]; reasons[key] = reasons.get(key, 0) + 1
    agree = [s["agree"] for s in steps if s.get("pick")]
    P("## Reported")
    P(f"  repairs applied per case, median {np.median([len(c['added']) for c in C]):.0f}; rejections by reason {reasons}")
    P(f"  applied repairs lowering both held-out runs {sum(a == 2 for a in agree)} of {len(agree)}, one run {sum(a == 1 for a in agree)}")
    P(f"  value of the applied repair against the best fitting drop, median {np.median([s['value'] for s in steps if s.get('pick')]):.2f}")
    for c in C:
        P(f"  {c['case']:<20} G9 {fmt(c['added'])} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} (held-out {c['e_final_heldout']:.3f}) | G7 -> {g7[c['case']]['e_final']:.3f} ({g7[c['case']]['e_final_heldout']:.3f})")
    better = sum(c["e_final"] < g7[c["case"]]["e_final"] for c in C); better_ho = sum(c["e_final_heldout"] < g7[c["case"]]["e_final_heldout"] for c in C)
    P(f"  terminal below G7's on {better} of {len(C)} cases (fitting), {better_ho} of {len(C)} (held-out mean)")
    # ---- K5 reported: the planted part's ground speed while down, terminal state against the teacher's feet
    P("## K5 (reported) ground speed of the part on the floor, m/s: the terminal state's planted part, and the teacher's parts within 2 cm of the floor")
    import sys as _sys; _sys.path.insert(0, ".")
    from poc.gait3d import grammar3d as G, rgre_gait3d as RG
    from poc.gait3d.runtime import state_from_json
    import numpy as np, mujoco
    def ground_speed(body, qs, eps=0.02):
        m, d = body.m, body.d; out = []
        for k in range(1, len(qs)):
            d.qpos[:] = qs[k - 1]; mujoco.mj_kinematics(m, d); lows0 = body.lowest(body.all_gids); x0 = d.geom_xpos[body.all_gids].copy() if False else np.array([d.geom_xpos[g][0] for g in body.all_gids])
            d.qpos[:] = qs[k]; mujoco.mj_kinematics(m, d); lows1 = body.lowest(body.all_gids); x1 = np.array([d.geom_xpos[g][0] for g in body.all_gids])
            down = (lows0 <= eps) & (lows1 <= eps)
            if down.any(): out.append(float(np.abs(x1[down] - x0[down]).min() * RG.FPS))
        return float(np.mean(out)) if out else float("nan")
    for c in C:
        case = RG.GaitCase(c["morph"], c["seed"]); st = state_from_json(c["state"])
        P(f"  {c['case']:<20} student {ground_speed(case.body, G.trajectory(st, case.body)):.3f}   teacher {ground_speed(case.body, case.q_teacher):.3f}   (emergent speed {float(case._consumers(st)['speed'][0]):.2f} m/s, teacher {float(case.target['speed'][0]):.2f})")
    letter = "A" if (k1 and k4) else ("B" if k1 else ("C" if k4 else "D"))
    P(f"\n## Outcome (frozen tree): K1 {'pass' if k1 else 'fail'}, K4 {'pass' if k4 else 'fail'} -> {letter}; K2 {'pass' if k2 else 'fail'}, K3 {'pass' if k3 else 'fail'}; K5 reported")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g8.json")
