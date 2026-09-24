"""F1: RGRE end to end on fire. Preregistration: docs/math-track-f1-prereg.md (frozen at 3442624).

Six expansion steps per scene from a deliberately underpowered V0. The frozen projection selector
names one class per step; an oracle fits every class only so the step can be scored. Nothing is
chosen by hand and no threshold is recalibrated.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poc.fire import scenes, rgre_fire as R, tokens
from poc.rgre.core import diagnose, select, select_projection

TAU = 0.5834212065969504          # RGRE-1's value, carried over verbatim
STEPS = 6
DEAD = 0.01                       # a repair removing less than this fraction is spent

SCORED = [("obstacle", True), ("ignition", True), ("delayed_ignition", False), ("full", False),
          ("windy", False), ("twin", False), ("shelf_bed", False)]
REPORTED = ["split", "shutoff"]


def run_scene(name, seen, v0, verbose=True):
    case = R.FireCase(name, getattr(scenes, name)())
    st = tokens.FireState(**v0)
    e0 = case.error(st)
    rec = dict(scene=name, seen=seen, e_v0=e0, consumers=case.names,
               per_consumer_v0=case.per_consumer(st), steps=[])
    blacklist, stopped = [], None
    for step in range(STEPS):
        t0 = time.time()
        tg = case.tangents(st)
        tmpl = case.templates()
        diag = diagnose(case.residual(st), tg, tmpl, support=R.SUPPORT_CLASSES)
        if diag is None:
            stopped = "no residual"; break
        # the oracle fits every class from this state; RGRE's choice is looked up in the same table
        table = {cls: R.repair_gain(case, st, cls) for cls in R.CLASSES}
        best = max(table.values(), key=lambda g: g["gain"])
        pick, why, ranked = select_projection(diag, TAU, {c: [c] for c in R.CLASSES},
                                              unrepairable=R.UNREPAIRABLE, blacklist=blacklist)
        coh_pick = select(diag, TAU, unrepairable=R.UNREPAIRABLE)[0]
        evaluated = 0
        chosen, gain_r = None, None
        while pick is not None:
            evaluated += 1
            g = table[pick]
            if g["drop"] >= DEAD * g["e0"]:
                chosen, gain_r = pick, g
                break
            blacklist.append(pick)
            pick, why, ranked = select_projection(diag, TAU, {c: [c] for c in R.CLASSES},
                                                  unrepairable=R.UNREPAIRABLE, blacklist=blacklist)
        s = dict(step=step, q_perp=diag["q_perp"], ranked=ranked[:4],
                 picked=chosen, why=why, evaluated=evaluated,
                 oracle=best["cls"], oracle_gain=best["gain"], coherence_pick=coh_pick,
                 seconds=round(time.time() - t0, 1))
        if chosen is None:
            s["e_before"] = case.error(st); s["e_after"] = case.error(st)
            rec["steps"].append(s); stopped = why; break
        s.update(e_before=gain_r["e0"], e_after=gain_r["e1"], rgre_gain=gain_r["gain"],
                 dcost=gain_r["dcost"],
                 v_cap=(gain_r["gain"] / best["gain"]) if best["gain"] > 0 else None)
        st = gain_r["state"]
        rec["steps"].append(s)
        if verbose:
            print(f"   [{name}] step {step}: q_perp {diag['q_perp']:.3f}  pick {chosen:<9} "
                  f"oracle {best['cls']:<9} E {gain_r['e0']:.4f}->{gain_r['e1']:.4f} "
                  f"V {s['v_cap'] if s['v_cap'] is None else round(s['v_cap'],3)}  {s['seconds']}s", flush=True)
    rec["stopped"] = stopped
    rec["e_final"] = case.error(st)
    rec["per_consumer_final"] = case.per_consumer(st)
    rec["state_final"] = {k: getattr(st, k) for k in st.__dataclass_fields__ if getattr(st, k) != 0.0}
    rec["cost_final"] = st.cost()
    rec["total_evals"] = case.evals
    return rec, case, st


def main():
    v0 = json.load(open("poc/results/f1_v0.json"))
    out = {"tau": TAU, "steps": STEPS, "v0": v0, "scored": [], "reported": []}
    t0 = time.time()
    for name, seen in SCORED:
        print(f"[{time.time()-t0:6.0f}s] {name} (seen={seen})", flush=True)
        rec, _, _ = run_scene(name, seen, v0)
        out["scored"].append(rec)
        json.dump(out, open("poc/results/f1.json", "w"), indent=1)
    for name in REPORTED:
        print(f"[{time.time()-t0:6.0f}s] {name} (out of vocabulary, reported)", flush=True)
        rec, case, st = run_scene(name, False, v0)
        # B5's condition: does the terminal state make this scene properly out of vocabulary?
        rows = {cls: round(100 * (g["e0"] - g["e1"]) / max(g["e0"], 1e-12), 2)
                for cls in R.CLASSES for g in [R.repair_gain(case, st, cls)]}
        rec["terminal_construct_check"] = rows
        rec["terminal_max_single_class"] = max(rows.values())
        print(f"   terminal construct check: max single class removes "
              f"{max(rows.values()):.1f}%", flush=True)
        out["reported"].append(rec)
        json.dump(out, open("poc/results/f1.json", "w"), indent=1)
    print(f"[{time.time()-t0:6.0f}s] done", flush=True)
    score(out)
    json.dump(out, open("poc/results/f1.json", "w"), indent=1)


def score(out):
    vs, evs, reds, transfer = [], [], [], []
    for rec in out["scored"]:
        for s in rec["steps"]:
            if s.get("v_cap") is not None:
                vs.append(s["v_cap"])
            if s.get("picked") is not None:
                evs.append(s["evaluated"])
        reds.append((rec["e_v0"] - rec["e_final"]) / rec["e_v0"])
        ok = all(rec["per_consumer_final"][c] <= rec["per_consumer_v0"][c] + 1e-9 for c in rec["consumers"])
        transfer.append(ok)
    split = [r for r in out["reported"] if r["scene"] == "split"]
    b5_ok = split and split[0]["terminal_max_single_class"] <= 10.0
    bars = {
        "B1_median_value_captured": {"value": float(np.median(vs)) if vs else None,
                                     "target": 0.75, "pass": bool(vs and np.median(vs) >= 0.75)},
        "B2_median_repairs_per_step": {"value": float(np.median(evs)) if evs else None,
                                       "target": len(R.CLASSES) / 3.0,
                                       "pass": bool(evs and np.median(evs) <= len(R.CLASSES) / 3.0)},
        "B3_median_terminal_reduction": {"value": float(np.median(reds)), "target": 0.40,
                                         "pass": bool(np.median(reds) >= 0.40)},
        "B4_consumer_transfer": {"value": int(sum(transfer)), "target": 6,
                                 "pass": bool(sum(transfer) >= 6)},
        "B5_abstention": {"scorable": bool(b5_ok),
                          "terminal_max_single_class": split[0]["terminal_max_single_class"] if split else None,
                          "abstained": (split[0]["stopped"] == "unknown") if split else None},
    }
    out["bars"] = bars
    print("\nBARS")
    for k, v in bars.items():
        print("  ", k, v)
    return bars


if __name__ == "__main__":
    main()
