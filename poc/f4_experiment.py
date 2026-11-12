"""F4: can a puff-train grammar express the teacher's fire? Prereg: docs/math-track-f4-prereg.md.

Seven scenes the puff grammar has never been fitted to. For each: the V0 error; the floor by Powell
from three starts under the four standard consumers; the same fit under the tone-mapped look
consumer; both states scored on the standard case (linear error, per-consumer error, decision
rates, glow correlation, motion ratio, parcel count); and a greedy RGRE run with no stopping rule
on the standard case. Every number is saved as it is produced.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poc.fire import scenes, puffs, rgre_puffs as RP
from poc.fire_decisions import decisions
from poc.rgre.core import diagnose, select_projection

NO_GATE = 1.01
DEAD = 0.01
STEPS = 10
UNSEEN = ["ignition", "delayed_ignition", "full", "twin", "shelf_bed", "split", "shutoff"]
OUT = "poc/results/f4.json"


def greedy(case, v0, log):
    st, e0 = v0, case.error(v0)
    rec = dict(steps=[], traj=[e0])
    blacklist, stopped = [], "budget"
    for step in range(STEPS):
        t0 = time.time()
        diag = diagnose(case.residual(st), case.tangents(st), case.templates(), support=RP.SUPPORT_CLASSES)
        if diag is None:
            stopped = "no residual"; break
        pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in RP.CLASSES},
                                              unrepairable=RP.UNREPAIRABLE, blacklist=blacklist)
        evaluated, chosen, g = 0, None, None
        while pick is not None:
            evaluated += 1
            g = RP.repair_gain(case, st, pick)
            if g["drop"] >= DEAD * g["e0"]:
                chosen = pick; break
            blacklist.append(pick)
            pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in RP.CLASSES},
                                                  unrepairable=RP.UNREPAIRABLE, blacklist=blacklist)
        s = dict(step=step, q_perp=diag["q_perp"], ranked=ranked[:4], picked=chosen,
                 evaluated=evaluated, seconds=round(time.time() - t0, 1))
        if chosen is None:
            rec["steps"].append(s); stopped = "exhausted"; break
        s.update(e_before=g["e0"], e_after=g["e1"], dcost=g["dcost"])
        st = g["state"]
        rec["traj"].append(g["e1"]); rec["steps"].append(s)
        log(f"   step {step}: pick {chosen:<8} E {g['e0']:.4f}->{g['e1']:.4f} ({evaluated} tried) {s['seconds']}s")
    rec.update(stopped=stopped, e_final=case.error(st), state={k: getattr(st, k) for k in st.__dataclass_fields__},
               per_consumer=case.per_consumer(st))
    return rec


def score(case, st):
    dec = decisions(case, st, as_record=puffs.as_record)
    return dict(error=case.error(st), per_consumer=case.per_consumer(st), live=st.live_count(),
                motion=RP.motion_ratio(case, st), decisions=dec,
                state={k: getattr(st, k) for k in st.__dataclass_fields__})


def run_scene(nm, log):
    case = RP.PuffCase(nm, getattr(scenes, nm)())
    look = RP.LookCase(case)
    v0 = puffs.PuffState()
    e0 = case.error(v0)
    rec = dict(scene=nm, consumers=case.names, e_v0=e0, per_consumer_v0=case.per_consumer(v0), fits={})
    log(f"{nm}: V0 {e0:.4f}")
    for lab, c in (("standard", case), ("look", look)):
        t0 = time.time()
        st, e, names, spread = RP.floor_fit(c, v0, maxfev_per_dim=40, verbose=False)
        sc = score(case, st)
        sc.update(fit_objective=e, spread=spread, n_params=len(names), seconds=round(time.time() - t0))
        rec["fits"][lab] = sc
        d = sc["decisions"]
        log(f"{nm} {lab:<8} fit {e:.4f} ({', '.join(f'{k} {v:.3f}' for k, v in spread.items())}) -> linear {sc['error']:.4f} "
            f"live {sc['live']} motion {sc['motion']:.2f} {sc['seconds']}s | "
            + ", ".join(f"{k} {v:.3f}" for k, v in sc["per_consumer"].items()))
        log(f"{nm} {lab:<8} heat wrong {100*d['heat']['disagree']:.1f}% ai wrong {100*d['ai']['disagree']:.1f}% "
            + (f"ignition missed {100*d['ignition']['missed_alight']:.1f}% " if "ignition" in d else "")
            + f"glow corr {d['visual']['late_correlation']:.2f}")
    t0 = time.time()
    rec["greedy"] = greedy(case, v0, log)
    rec["greedy"]["seconds"] = round(time.time() - t0)
    g = rec["greedy"]; e = rec["fits"]["standard"]["error"]
    log(f"{nm}: greedy {g['e_final']:.4f} after {len(g['steps'])} steps ({g['stopped']}), "
        f"{(e0 - g['e_final']) / max(e0 - e, 1e-9):.3f} of the floor's reduction")
    rec["evals"] = case.evals
    return rec


def main():
    out = dict(unseen=[], started=time.strftime("%Y-%m-%d %H:%M:%S"))
    T0 = time.time()
    def log(msg):
        print(f"[{time.time()-T0:6.0f}s] {msg}", flush=True)
    for nm in UNSEEN:
        out["unseen"].append(run_scene(nm, log))
        json.dump(out, open(OUT, "w"), indent=1)
    floors = [r["fits"]["standard"]["error"] for r in out["unseen"]]
    corr = [r["fits"]["look"]["decisions"]["visual"]["late_correlation"] for r in out["unseen"]]
    log(f"median standard floor {np.median(floors):.4f}; median glow correlation at the look fit {np.median(corr):.3f}")
    out["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
