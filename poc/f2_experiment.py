"""F2: F1's fire search with the stopping rule replaced. Preregistration: docs/math-track-f2-prereg.md.

Only the stopping rule differs from poc/f1_experiment.py, which is frozen and untouched:

  - q_perp no longer gates anything. The frozen select_projection is called with its threshold at
    1.01, above the largest value the quantity can take, so the function is unchanged.
  - Abstention is a step-zero test on realised gain: if the top-ranked class removes 10 percent or
    less of the V0 error, the case is out of vocabulary and the search stops with no expansions.
    Ten percent is RGRE-1b's out-of-vocabulary constant, not a new one.
  - Termination from step one on is repair exhaustion at the unchanged 1 percent spent rule, or the
    step budget.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poc.fire import scenes, rgre_fire as R, tokens
from poc.rgre.core import diagnose, select, select_projection

NO_GATE = 1.01          # q_perp is a fraction of energy, so this disables the threshold
OOV = 0.10              # RGRE-1b's out-of-vocabulary constant, now the step-zero abstention rule
DEAD = 0.01             # RGRE-1b's spent-repair constant, unchanged
STEPS = 10

SCORED = [("obstacle", True), ("ignition", True), ("delayed_ignition", False), ("full", False),
          ("windy", False), ("twin", False), ("shelf_bed", False)]
REPORTED = ["split", "shutoff"]


def run_scene(name, seen, v0, verbose=True):
    case = R.FireCase(name, getattr(scenes, name)())
    st = tokens.FireState(**v0)
    e0 = case.error(st)
    rec = dict(scene=name, seen=seen, e_v0=e0, consumers=case.names,
               per_consumer_v0=case.per_consumer(st), steps=[], e_at_6=None)
    blacklist, stopped = [], None
    for step in range(STEPS):
        t0 = time.time()
        tg = case.tangents(st)
        diag = diagnose(case.residual(st), tg, case.templates(), support=R.SUPPORT_CLASSES)
        if diag is None:
            stopped = "no residual"; break
        table = {cls: R.repair_gain(case, st, cls) for cls in R.CLASSES}
        best = max(table.values(), key=lambda g: g["gain"])
        pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in R.CLASSES},
                                              unrepairable=R.UNREPAIRABLE, blacklist=blacklist)
        coh_pick = select(diag, NO_GATE, unrepairable=R.UNREPAIRABLE)[0]
        evaluated, chosen, gain_r = 0, None, None
        while pick is not None:
            evaluated += 1
            g = table[pick]
            if step == 0:
                # out of vocabulary: the top-ranked repair does not meaningfully help
                if g["drop"] <= OOV * g["e0"]:
                    why = "unknown"; blacklist.append(pick); pick = None; break
                chosen, gain_r = pick, g; break
            if g["drop"] >= DEAD * g["e0"]:
                chosen, gain_r = pick, g; break
            blacklist.append(pick)
            pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in R.CLASSES},
                                                  unrepairable=R.UNREPAIRABLE, blacklist=blacklist)
        s = dict(step=step, q_perp=diag["q_perp"], ranked=ranked[:4], picked=chosen, why=why,
                 evaluated=evaluated, oracle=best["cls"], oracle_gain=best["gain"],
                 coherence_pick=coh_pick, seconds=round(time.time() - t0, 1))
        if chosen is None:
            s["e_before"] = s["e_after"] = case.error(st)
            rec["steps"].append(s); stopped = why or "exhausted"; break
        s.update(e_before=gain_r["e0"], e_after=gain_r["e1"], rgre_gain=gain_r["gain"],
                 dcost=gain_r["dcost"],
                 v_cap=(gain_r["gain"] / best["gain"]) if best["gain"] > 0 else None)
        st = gain_r["state"]
        rec["steps"].append(s)
        if step == 5:
            rec["e_at_6"] = gain_r["e1"]
        if verbose:
            print(f"   [{name}] step {step}: q_perp {diag['q_perp']:.3f}  pick {chosen:<9} "
                  f"oracle {best['cls']:<9} E {gain_r['e0']:.4f}->{gain_r['e1']:.4f} "
                  f"V {round(s['v_cap'],3) if s['v_cap'] is not None else None}  {s['seconds']}s", flush=True)
    rec["stopped"] = stopped or "budget"
    rec["e_final"] = case.error(st)
    rec["steps_used"] = sum(1 for s in rec["steps"] if s["picked"] is not None)
    rec["per_consumer_final"] = case.per_consumer(st)
    rec["state_final"] = {k: getattr(st, k) for k in st.__dataclass_fields__ if getattr(st, k) != 0.0}
    rec["cost_final"] = st.cost()
    if rec["e_at_6"] is None:
        rec["e_at_6"] = rec["e_final"]
    return rec, case, st


def score(out):
    vs, evs, reds, reds6, transfer, steps = [], [], [], [], [], []
    for rec in out["scored"]:
        for s in rec["steps"]:
            if s.get("v_cap") is not None:
                vs.append(s["v_cap"])
            if s.get("picked") is not None:
                evs.append(s["evaluated"])
        reds.append((rec["e_v0"] - rec["e_final"]) / rec["e_v0"])
        reds6.append((rec["e_v0"] - rec["e_at_6"]) / rec["e_v0"])
        transfer.append(all(rec["per_consumer_final"][c] <= rec["per_consumer_v0"][c] + 1e-9
                            for c in rec["consumers"]))
        steps.append(rec["steps_used"])
    out["bars"] = {
        "B1_median_value_captured": {"value": float(np.median(vs)) if vs else None, "target": 0.75,
                                     "pass": bool(vs and np.median(vs) >= 0.75)},
        "B2_median_repairs_per_step": {"value": float(np.median(evs)) if evs else None,
                                       "target": len(R.CLASSES) / 3.0,
                                       "pass": bool(evs and np.median(evs) <= len(R.CLASSES) / 3.0)},
        "B3_median_terminal_reduction": {"value": float(np.median(reds)), "target": 0.40,
                                         "pass": bool(np.median(reds) >= 0.40)},
        "B4_consumer_transfer": {"value": int(sum(transfer)), "target": 6, "pass": bool(sum(transfer) >= 6)},
        "B5_median_steps_used": {"value": float(np.median(steps)), "target": 4.0,
                                 "pass": bool(np.median(steps) >= 4.0)},
        "reported_median_reduction_at_6": float(np.median(reds6)),
    }
    print("\nBARS")
    for k, v in out["bars"].items():
        print("  ", k, v)


def main():
    v0 = json.load(open("poc/results/f1_v0.json"))
    out = {"no_gate": NO_GATE, "oov": OOV, "dead": DEAD, "steps": STEPS, "v0": v0,
           "scored": [], "reported": []}
    t0 = time.time()
    for name, seen in SCORED:
        print(f"[{time.time()-t0:6.0f}s] {name} (seen={seen})", flush=True)
        rec, _, _ = run_scene(name, seen, v0)
        out["scored"].append(rec)
        json.dump(out, open("poc/results/f2.json", "w"), indent=1)
    for name in REPORTED:
        print(f"[{time.time()-t0:6.0f}s] {name} (out of vocabulary, reported)", flush=True)
        rec, case, st = run_scene(name, False, v0)
        rows = {cls: round(100 * (g["e0"] - g["e1"]) / max(g["e0"], 1e-12), 2)
                for cls in R.CLASSES for g in [R.repair_gain(case, st, cls)]}
        rec["terminal_construct_check"] = rows
        rec["terminal_max_single_class"] = max(rows.values())
        print(f"   terminal construct check: max single class removes {max(rows.values()):.1f}%", flush=True)
        out["reported"].append(rec)
        json.dump(out, open("poc/results/f2.json", "w"), indent=1)
    print(f"[{time.time()-t0:6.0f}s] done", flush=True)
    score(out)
    json.dump(out, open("poc/results/f2.json", "w"), indent=1)


if __name__ == "__main__":
    main()
