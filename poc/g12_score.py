"""G12 frozen scorer. Committed with the preregistration, run once. Bars as G7's; G7's run on the same
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


def main(path, g7_path="poc/results/g11.json"):
    d = json.load(open(path)); C = [c for c in d["cases"] if c["case"] != PILOT]
    g7 = {c["case"]: c for c in json.load(open(g7_path))["cases"]}
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G12 scored: {len(C)} cases ({PILOT} excluded as the declared pilot), {d['STEPS']} steps, \n")
    imps = lambda c: [e for e in c["added"] if e[0] not in BASE]
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    damaged = [c for c in C if c["designed"] or c["morph"].startswith("short_shank") or c["morph"].startswith("noleg")]
    controls = [c for c in C if c["case"] not in [x["case"] for x in damaged]]
    n_dam = len(damaged); bar = 7
    P("## K1 identity: first impairment repair, within two, and on the mirrors")
    for c in design + mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  G12 {fmt(c['added'])} | G11 {fmt(g7[c['case']]['added'])}")
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
        P(f"  {c['case']:<20} G12 {fmt(c['added'])} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} (held-out {c['e_final_heldout']:.3f}) | G11 -> {g7[c['case']]['e_final']:.3f} ({g7[c['case']]['e_final_heldout']:.3f})")
    better = sum(c["e_final"] < g7[c["case"]]["e_final"] for c in C); better_ho = sum(c["e_final_heldout"] < g7[c["case"]]["e_final_heldout"] for c in C)
    P(f"  terminal below G11's on {better} of {len(C)} cases (fitting), {better_ho} of {len(C)} (held-out mean)")
    # ---- K5 reported: the planted part's ground speed while down, terminal state against the teacher's feet
    P("## K5 (reported) ground speed of the part on the floor, m/s: the terminal state's planted part, and the teacher's parts within 2 cm of the floor")
    import sys as _sys; _sys.path.insert(0, ".")
    from poc.gait3d import grammar3d as G, rgre_gait3d as RG
    from poc.gait3d.runtime import state_from_json
    import mujoco                      # (scorer defect fixed after the run: a local numpy import shadowed the module's; bars untouched)
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
    # ---- K6 reported: the round's claim, foot travel. Per case, each foot's swing speed and step length, student against teacher.
    P("## K6 (reported) foot travel at the terminal: forward speed of each foot while off the floor (m/s) and step length between touchdowns (m), student / teacher")
    for c in C:
        case = RG.GaitCase(c["morph"], c["seed"]); st = state_from_json(c["state"]); ps = case._consumers(st)["travel"]; pt = case.target["travel"]
        parts = [g for g in case.body.contact_geoms if g != "pelvis"]
        feet = [(g, i) for i, g in enumerate(parts) if g.startswith("foot") or (g.startswith("hand") and not any(x.startswith("foot") for x in parts))]
        P(f"  {c['case']:<20} " + "; ".join(f"{g} swing {ps[2*i]:.2f}/{pt[2*i]:.2f} step {ps[2*i+1]:.2f}/{pt[2*i+1]:.2f}" for g, i in feet) + f"   (travel block error {c['per_consumer']['travel']:.2f}, V0 {c['per_consumer_v0']['travel']:.2f})")
    # ---- K7 reported: the round's claim, stride against advance. Mean forward foot separation and body speed, student / teacher.
    P("## K7 (reported) stride and advance at the terminal: mean forward separation of the feet (m) and body speed (m/s), student / teacher")
    for c in C:
        case = RG.GaitCase(c["morph"], c["seed"]); st = state_from_json(c["state"]); qs = G.trajectory(st, case.body); qt = case.q_teacher
        feet = [g for g in ("foot_l", "foot_r") if g in case.body.gid]
        def sep(q):
            if len(feet) < 2: return float("nan")
            m_, d_ = case.body.m, case.body.d; out = []
            for row in q:
                d_.qpos[:] = row; mujoco.mj_kinematics(m_, d_); out.append(abs(d_.geom_xpos[case.body.gid["foot_l"]][0] - d_.geom_xpos[case.body.gid["foot_r"]][0]))
            return float(np.mean(out))
        P(f"  {c['case']:<20} separation {sep(qs):.2f}/{sep(qt):.2f}   speed {(qs[-1,0]-qs[0,0])/4:.2f}/{(qt[-1,0]-qt[0,0])/4:.2f}")
    letter = "A" if (k1 and k4) else ("B" if k1 else ("C" if k4 else "D"))
    P(f"\n## Outcome (frozen tree): K1 {'pass' if k1 else 'fail'}, K4 {'pass' if k4 else 'fail'} -> {letter}; K2 {'pass' if k2 else 'fail'}, K3 {'pass' if k3 else 'fail'}; K5, K6, K7 reported")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g12.json")    # (default path fixed after the run; the run was scored with the path given)
