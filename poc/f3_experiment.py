"""F3: does the vocabulary or the search limit the cheap fire model? Prereg: docs/math-track-f3-prereg.md.

No stopping rule, no borrowed constant, no per-step oracle. Greedy expansion to a budget, and a
joint fit of every parameter of every class as the floor the vocabulary can reach.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poc.fire import scenes, rgre_fire as R, tokens
from poc.rgre.core import diagnose, select_projection

NO_GATE = 1.01
DEAD = 0.01
STEPS = 12

SCORED = [("obstacle", True), ("ignition", True), ("delayed_ignition", False), ("full", False),
          ("windy", False), ("twin", False), ("shelf_bed", False)]
REPORTED = ["split", "shutoff"]


def run_scene(name, seen, v0):
    case = R.FireCase(name, getattr(scenes, name)())
    st = tokens.FireState(**v0)
    e0 = case.error(st)
    rec = dict(scene=name, seen=seen, e_v0=e0, consumers=case.names,
               per_consumer_v0=case.per_consumer(st), steps=[], traj=[e0])
    blacklist, stopped = [], "budget"
    for step in range(STEPS):
        t0 = time.time()
        diag = diagnose(case.residual(st), case.tangents(st), case.templates(),
                        support=R.SUPPORT_CLASSES)
        if diag is None:
            stopped = "no residual"; break
        pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in R.CLASSES},
                                              unrepairable=R.UNREPAIRABLE, blacklist=blacklist)
        evaluated, chosen, g = 0, None, None
        while pick is not None:
            evaluated += 1
            g = R.repair_gain(case, st, pick)
            if g["drop"] >= DEAD * g["e0"]:
                chosen = pick; break
            blacklist.append(pick)
            pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in R.CLASSES},
                                                  unrepairable=R.UNREPAIRABLE, blacklist=blacklist)
        s = dict(step=step, q_perp=diag["q_perp"], ranked=ranked[:4], picked=chosen,
                 evaluated=evaluated, seconds=round(time.time() - t0, 1))
        if chosen is None:
            rec["steps"].append(s); stopped = "exhausted"; break
        s.update(e_before=g["e0"], e_after=g["e1"], dcost=g["dcost"])
        st = g["state"]
        rec["traj"].append(g["e1"])
        rec["steps"].append(s)
        print(f"   [{name}] step {step}: pick {chosen:<9} E {g['e0']:.4f}->{g['e1']:.4f} "
              f"({evaluated} tried) {s['seconds']}s", flush=True)
    rec["stopped"] = stopped
    rec["e_greedy"] = case.error(st)
    rec["steps_used"] = sum(1 for s in rec["steps"] if s["picked"])
    rec["per_consumer_greedy"] = case.per_consumer(st)
    rec["state_greedy"] = {k: getattr(st, k) for k in st.__dataclass_fields__ if getattr(st, k) != 0.0}
    t0 = time.time()
    jst, je = R.joint_fit(case, tokens.FireState(**v0))
    rec["e_joint"] = je
    rec["per_consumer_joint"] = case.per_consumer(jst)
    rec["state_joint"] = {k: getattr(jst, k) for k in jst.__dataclass_fields__ if getattr(jst, k) != 0.0}
    rec["joint_seconds"] = round(time.time() - t0, 1)
    print(f"   [{name}] greedy {rec['e_greedy']:.4f} ({rec['steps_used']} steps)  "
          f"joint {je:.4f} ({rec['joint_seconds']}s)  V0 {e0:.4f}", flush=True)
    return rec, case, st


def score(out):
    joints, ratios, reds, transfer, picks = [], [], [], [], []
    for r in out["scored"]:
        joints.append(r["e_joint"])
        gj = r["e_v0"] - r["e_joint"]
        gg = r["e_v0"] - r["e_greedy"]
        if gj > 1e-9:
            ratios.append(gg / gj)
        reds.append(gg / r["e_v0"])
        if r["steps_used"] > 0:
            transfer.append(all(r["per_consumer_greedy"][c] <= r["per_consumer_v0"][c] + 1e-9
                                for c in r["consumers"]))
        picks += [s["picked"] for s in r["steps"] if s["picked"]]
    picks += [s["picked"] for r in out["reported"] for s in r["steps"] if s["picked"]]
    gated = {c for c in ("soot", "flicker", "secondary") if c in picks}
    out["bars"] = {
        "B1_vocabulary_floor": {"value": float(np.median(joints)), "target": 0.35,
                                "pass": bool(np.median(joints) <= 0.35)},
        "B2_search_adequacy": {"value": float(np.median(ratios)) if ratios else None, "target": 0.80,
                               "pass": bool(ratios and np.median(ratios) >= 0.80)},
        "B3_gated_reachable": {"value": sorted(gated), "target": ">=1 of soot/flicker/secondary",
                               "pass": bool(gated)},
        "B4_terminal_reduction": {"value": float(np.median(reds)), "target": 0.40,
                                  "pass": bool(np.median(reds) >= 0.40)},
        "B5_consumer_transfer": {"value": int(sum(transfer)), "of": len(transfer), "target": 6,
                                 "pass": bool(sum(transfer) >= 6)},
        "pick_histogram": {k: picks.count(k) for k in sorted(set(picks))},
    }
    print("\nBARS")
    for k, v in out["bars"].items():
        print("  ", k, v)


def main():
    v0 = json.load(open("poc/results/f1_v0.json"))
    out = {"steps": STEPS, "dead": DEAD, "v0": v0, "scored": [], "reported": []}
    t0 = time.time()
    for name, seen in SCORED:
        print(f"[{time.time()-t0:6.0f}s] {name}", flush=True)
        rec, _, _ = run_scene(name, seen, v0)
        out["scored"].append(rec); json.dump(out, open("poc/results/f3.json", "w"), indent=1)
    for name in REPORTED:
        print(f"[{time.time()-t0:6.0f}s] {name} (out of vocabulary, reported)", flush=True)
        rec, case, st = run_scene(name, False, v0)
        rows = {cls: round(100 * (g["e0"] - g["e1"]) / max(g["e0"], 1e-12), 2)
                for cls in R.CLASSES for g in [R.repair_gain(case, st, cls)]}
        rec["terminal_construct_check"] = rows
        rec["terminal_max_single_class"] = max(rows.values())
        out["reported"].append(rec); json.dump(out, open("poc/results/f3.json", "w"), indent=1)
    print(f"[{time.time()-t0:6.0f}s] done", flush=True)
    score(out)
    json.dump(out, open("poc/results/f3.json", "w"), indent=1)


if __name__ == "__main__":
    main()
