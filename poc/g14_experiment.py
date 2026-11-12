"""G14: composition of edits, a removed arm, and a one-arm crawl. Prereg: docs/math-track-g14-prereg.md.

Four new teacher bodies, three seeds each. Two things are measured on each:
  1. the growth of G13 (the grammar's classes as edits of a base clip, held-out acceptance, the guard,
     the spent rule, six steps), fit on seed 0 with seeds 1 and 2 held out, on the intact clip for the
     bodies with legs and on the legless body's own loop for the one-arm crawl, with clearance grounding;
  2. compositions that fit nothing: the edits G13 fitted to the single damages, composed
     (clip_edit.compose) and played on the combined body with the missing parts dropped, scored against
     all three runs; beside them the raw clip and each single edit alone.
"""
from __future__ import annotations
import argparse, json, sys, time
from dataclasses import asdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.gait3d import biped3d as biped, grammar3d as G, rgre_gait3d as RG, clip_edit as CE
from poc.gait3d.compare3d import compare
from poc.gait3d.runtime import state_from_json

STEPS = 6
DEAD = 0.01
SEEDS = (0, 1, 2)
GROUNDING = "clearance"
BODIES = list(biped.COMBINED)
CASES = [(m, 0) for m in BODIES]
PILOT = ("noarm_left", 2)
G13 = "poc/results/g13.json"


def base_for(morph):
    return CE.base_clip(morph="nolegs") if biped.legless(morph) else CE.base_clip()


def make_case(morph, seed, ref):
    return CE.EditedGaitCase(morph, seed, ref, base_for(morph), GROUNDING)


def designed(morph):
    side, kind = biped.side_of(morph)
    sign = {"left": -1, "right": 1}.get(side, 0)
    if kind in ("locked_knee", "stump"):
        return {"locked_knee": "stiff", "stump": "limp"}[kind], sign
    return None, 0


def run_case(args):
    morph, seed = args
    T0 = time.time()
    v0 = RG.load_v0()
    fit = make_case(morph, seed, v0)
    hos = [make_case(morph, s, v0) for s in SEEDS if s != seed]
    cand = fit.repairable()
    dcls, dsign = designed(morph)
    p_hos = [RG.consumers(fit.body, h.q_teacher) for h in hos]
    tol = {k: float(np.mean([np.sqrt(((fit.target[k] - p[k]) ** 2).mean()) for p in p_hos]) / fit.scale[k]) for k in fit.names}
    e_ho = lambda st: [h.error(st) for h in hos]
    ho_v0 = e_ho(v0)
    out = dict(case=fit.name, morph=morph, seed=seed, heldout_seeds=[h.seed for h in hos], group="pilot" if (morph, seed) == PILOT else "design",
               base=base_for(morph).morph, designed=dcls, designed_sign=dsign, candidates=cand, tolerance=tol,
               e_v0=fit.error(v0), e_v0_heldout=float(np.mean(ho_v0)), e_v0_heldout_runs=ho_v0, per_consumer_v0=fit.per_consumer(v0))
    st, blacklist, steps, added = v0, [], [], []
    for t in range(STEPS):
        e0 = fit.error(st); ho0 = e_ho(st); m0 = float(np.mean(ho0)); pc0 = fit.per_consumer(st)
        live = [c for c in cand if c not in blacklist]
        table = {c: RG.repair_gain(fit, st, c) for c in live}
        order = sorted(live, key=lambda c: -table[c]["drop"])
        row = dict(t=t, e_before=e0, e_before_heldout=m0, e_before_heldout_runs=ho0, drops={c: table[c]["drop"] / e0 for c in live},
                   sides={c: G.side_sign(table[c]["state"], c) for c in live}, rejected={}, pick=None)
        chosen = None
        for c in order:
            g = table[c]
            if g["drop"] < DEAD * e0:
                row["rejected"][c] = "spent"; continue
            ho1 = e_ho(g["state"]); m1 = float(np.mean(ho1)); agree = sum(a < b for a, b in zip(ho1, ho0))
            if m1 >= m0:
                row["rejected"][c] = f"held-out {m1:.4f} >= {m0:.4f} ({agree} of 2 runs lower)"; continue
            pc1 = fit.per_consumer(g["state"])
            over = [k for k in pc1 if pc1[k] > pc0[k] + tol[k]]
            if over:
                row["rejected"][c] = "guard: " + ", ".join(over); continue
            chosen = c; row.update(agree=agree, e_after_heldout_runs=ho1); break
        if chosen is None:
            row.update(dead=True, e_after=e0, e_after_heldout=m0); steps.append(row)
            print(f"   [{fit.name}] t{t} declined: " + "; ".join(f"{c} {r}" for c, r in list(row['rejected'].items())[:4]) + f" [{time.time()-T0:.0f}s]", flush=True)
            break
        g = table[chosen]; st = g["state"]
        row.update(pick=chosen, side=G.side_sign(st, chosen), dead=False, drop_rel=g["drop"] / e0, e_after=g["e1"], e_after_heldout=float(np.mean(row["e_after_heldout_runs"])),
                   oracle=order[0], value=g["drop"] / table[order[0]]["drop"] if table[order[0]]["drop"] > 1e-12 else 1.0)
        added.append((chosen, row["side"]))
        steps.append(row)
        print(f"   [{fit.name}] t{t} pick {chosen:<6} side {row['side']:+d} (oracle {order[0]}, value {row['value']:.2f}) "
              f"fit {e0:.4f}->{g['e1']:.4f} held-out {m0:.4f}->{row['e_after_heldout']:.4f} ({row['agree']} of 2) rejected {list(row['rejected'])} [{time.time()-T0:.0f}s]", flush=True)
    active = [c for c in G.IMPAIRMENTS if G.is_on(st, c)]
    ho_f = e_ho(st)
    out.update(steps=steps, added=added, active=active, e_final=fit.error(st), e_final_heldout=float(np.mean(ho_f)), e_final_heldout_runs=ho_f,
               per_consumer=fit.per_consumer(st), state=asdict(st), seconds=time.time() - T0)
    compare(fit, st, f"poc/results/g14_{fit.name}_checked.png", f"{fit.name}: teacher vs checked terminal, error {fit.error(st):.3f} (held-out mean {np.mean(ho_f):.3f}), classes {active}")
    return out


def compositions():
    """The no-fit compositions on the combined bodies, scored against every run. Each entry: the state
    played, its error on runs 0, 1, 2, and the physical readouts."""
    v0 = RG.load_v0(); g13 = {c["case"]: state_from_json(c["state"]) for c in json.load(open(G13))["cases"]}
    plan = {
        "locked_knee_left+weak_hip_right": {"raw clip": v0, "locked knee edit alone (G13 locked_knee_left_s0)": g13["locked_knee_left_s0"],
                                            "weak hip edit alone (G13 weak_hip_right_s0)": g13["weak_hip_right_s0"],
                                            "composed": CE.compose(g13["locked_knee_left_s0"], g13["weak_hip_right_s0"], v0)},
        "locked_knee_left+noarm_right": {"raw clip (arm dropped)": v0, "locked knee edit (G13 locked_knee_left_s0), arm dropped": g13["locked_knee_left_s0"]},
        "noarm_left": {"raw clip (arm dropped)": v0},
        "nolegs+noarm_left": {"raw crawl loop (arm dropped)": v0},
    }
    out = {}
    for morph, entries in plan.items():
        cases = [make_case(morph, s, v0) for s in SEEDS]; out[morph] = {}
        for label, st in entries.items():
            errs = [c.error(st) for c in cases]; ps = cases[0]._consumers(st); pt = cases[0].target
            out[morph][label] = dict(errors=errs, state=asdict(st), speed=float(ps["speed"][0]), speed_teacher=float(pt["speed"][0]),
                                     airborne=float(ps["stance"][-3]), airborne_teacher=float(pt["stance"][-3]))
            print(f"{morph:<32} {label:<58} errors " + " ".join(f"{e:.3f}" for e in errs) + f"  speed {out[morph][label]['speed']:.2f}/{out[morph][label]['speed_teacher']:.2f}", flush=True)
    return out


def main(cases, out_path, workers):
    recs, T0 = [], time.time()
    comp = compositions() if cases else {}
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, cases):
            recs.append(rec)
            fmt = [f"{a}{s:+d}" if s else a for a, s in rec["added"]]
            print(f"{rec['case']:<36} [{rec['group']}] base {rec['base']} v0 {rec['e_v0']:.3f}/{rec['e_v0_heldout']:.3f} -> "
                  f"{rec['e_final']:.3f}/{rec['e_final_heldout']:.3f} added {fmt} [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(STEPS=STEPS, DEAD=DEAD, SEEDS=SEEDS, GROUNDING=GROUNDING, cases=recs, compositions=comp), open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="all")
    ap.add_argument("--out", default="poc/results/g14.json")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    STEPS = a.steps
    if a.cases == "all": cases = CASES
    elif a.cases == "pilot": cases = [PILOT]
    else: cases = [(x.split(":")[0], int(x.split(":")[1])) for x in a.cases.split(",")]
    main(cases, a.out, a.workers)
