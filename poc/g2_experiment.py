"""G2: growing the gait grammar with exclusive classes. Prereg: docs/math-track-g2-prereg.md.

Same fourteen teachers as G1. Per case, from V0, three selection rules grow the grammar along their
own paths for STEPS steps with the spent rule and no stopping rule:

  projection   the arc's selector on the signed tangents, one repair fitted per step (record);
  oracle       every repairable class fitted, best drop taken: the workflow's rule where a fit
               costs three seconds (docs/math-track-g1-results.md);
  oracle_safe  the best drop among the fitted classes that make no consumer worse than the
               current state; declined when none qualifies.

The oracle table is computed once per step and shared by the rules at a common state, and each
path keeps its own state. The floor is Powell over every repairable parameter from V0 and from the
oracle terminal, the better of the two, with an explicit budget. Identity is a class and, for sided
classes, the sign of its side.
"""
from __future__ import annotations

import argparse, json, sys, time
from dataclasses import asdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.gait import biped, grammar as G, rgre_gait as RG
from poc.gait.compare import compare
from poc.rgre.core import diagnose, select_projection

STEPS = 6          # room for base re-fits and two impairment repairs
DEAD = 0.01
NO_GATE = 1.01
DESIGN = [(m, 0) for m in biped.MORPHS]
TRANSFER = [(m, 0) for m in biped.MIRRORS] + [("intact", 1), ("nolegs", 1)]
VARIANTS = ("projection", "oracle", "oracle_safe")


def designed(morph):
    """(class, side sign) the damage should be named by; (None, 0) for bodies with none."""
    side, kind = biped.side_of(morph)
    sign = {"left": -1, "right": 1}.get(side, 0)
    # The short shank has no designed class (pilot, docs/math-track-g2-prereg.md): the student's
    # grounding on the shorter leg reproduces the teacher's stance asymmetry by itself, and what is
    # left after a base re-fit is under one percent for every impairment class. Reported, not barred.
    if kind in ("locked_knee", "stump"):
        return {"locked_knee": "stiff", "stump": "kneel"}[kind], sign
    if kind == "noleg":
        return "hop", 0
    if morph == "nolegs":
        return "vault", 0
    return None, 0


def step_record(case, st, cand):
    r = case.residual(st); signed = case.tangents(st)
    diag = diagnose(r, signed, {}, support=())
    _, _, ranked = select_projection(diag, NO_GATE, {c: [c] for c in G.CLASSES}, unrepairable=(), blacklist=[])
    ranked = [c for c in ranked if c in cand]
    e0 = case.error(st); pc0 = case.per_consumer(st)
    table = {c: RG.repair_gain(case, st, c) for c in cand}
    for c in table:
        pc = case.per_consumer(table[c]["state"])
        table[c]["worse"] = [k for k in pc if pc[k] > pc0[k] + 1e-9]
    return dict(ranked=ranked, e0=e0, table=table)


def choose(variant, rec, blacklist, cand):
    ranked = [c for c in rec["ranked"] if c not in blacklist]
    live = [c for c in cand if c not in blacklist]
    table = rec["table"]
    if variant == "projection":
        return ranked[0] if ranked else None
    if variant == "oracle":
        return max(live, key=lambda c: table[c]["drop"]) if live else None
    safe = [c for c in live if not table[c]["worse"]]
    return max(safe, key=lambda c: table[c]["drop"]) if safe else None


def run_case(args):
    morph, seed = args
    T0 = time.time()
    case = RG.GaitCase(morph, seed)
    v0 = RG.load_v0()
    cand = case.repairable()
    dcls, dsign = designed(morph)
    out = dict(case=case.name, morph=morph, seed=seed, group="design" if (morph, seed) in DESIGN else "transfer",
               designed=dcls, designed_sign=dsign, candidates=cand, e_v0=case.error(v0), per_consumer_v0=case.per_consumer(v0), variants={})
    for variant in VARIANTS:
        st, blacklist, steps, added = v0, [], [], []
        for t in range(STEPS):
            rec = step_record(case, st, cand)
            live = [c for c in cand if c not in blacklist]
            oracle = max(live, key=lambda c: rec["table"][c]["drop"]) if live else None
            odrop = rec["table"][oracle]["drop"] if oracle else 0.0
            pick = choose(variant, rec, blacklist, cand)
            row = dict(t=t, ranked=rec["ranked"][:4], oracle=oracle, oracle_drop_rel=odrop / rec["e0"], e_before=rec["e0"],
                       drops={c: rec["table"][c]["drop"] / rec["e0"] for c in cand},
                       sides={c: G.side_sign(rec["table"][c]["state"], c) for c in cand},
                       worse={c: rec["table"][c]["worse"] for c in cand})
            if pick is None:
                row.update(pick=None, dead=True, e_after=rec["e0"], value=0.0); steps.append(row); continue
            g = rec["table"][pick]; dead = g["drop"] < DEAD * rec["e0"]
            row.update(pick=pick, side=G.side_sign(g["state"], pick), dead=bool(dead), drop_rel=g["drop"] / rec["e0"],
                       value=(g["drop"] / odrop) if odrop > 1e-12 else (1.0 if g["drop"] >= odrop else 0.0))
            if dead:
                blacklist.append(pick); row["e_after"] = rec["e0"]
            else:
                st = g["state"]; row["e_after"] = g["e1"]; added.append((pick, row["side"]))
            steps.append(row)
            print(f"   [{case.name}/{variant}] t{t} pick {str(pick):<6} side {row.get('side', 0):+d} oracle {str(oracle):<6} value {row['value']:.2f} "
                  f"E {rec['e0']:.4f}->{row['e_after']:.4f} [{time.time()-T0:.0f}s]", flush=True)
        active = [c for c in G.IMPAIRMENTS if G.is_on(st, c)]
        out["variants"][variant] = dict(steps=steps, e_final=case.error(st), active=active, per_consumer=case.per_consumer(st),
                                        state=asdict(st), added=added)
        if variant == "oracle":
            compare(case, st, f"poc/results/g2_{case.name}_oracle.png", f"{case.name}: teacher vs oracle terminal, error {case.error(st):.3f}, classes {active}")
            s_or = st
    t1 = time.time()
    fa, ea = RG.local_floor(case, v0, maxfev=4000)
    fb, eb = RG.local_floor(case, s_or, maxfev=4000)
    out["floor"] = dict(e=min(ea, eb), from_v0=ea, from_oracle=eb, seconds=round(time.time() - t1))
    out["seconds"] = time.time() - T0
    return out


def main(cases, out_path, workers):
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, cases):
            recs.append(rec)
            v = rec["variants"]
            print(f"{rec['case']:<22} [{rec['group']}] designed {rec['designed']}{rec['designed_sign']:+d} v0 {rec['e_v0']:.3f} | " +
                  " ".join(f"{k} {v[k]['e_final']:.3f} {v[k]['added']}" for k in VARIANTS) +
                  f" | floor {rec['floor']['e']:.3f} [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(STEPS=STEPS, DEAD=DEAD, cases=recs), open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="all")
    ap.add_argument("--out", default="poc/results/g2.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    STEPS = a.steps
    if a.cases == "all": cases = DESIGN + TRANSFER
    elif a.cases == "design": cases = DESIGN
    elif a.cases == "transfer": cases = TRANSFER
    else: cases = [(x.split(":")[0], int(x.split(":")[1])) for x in a.cases.split(",")]
    main(cases, a.out, a.workers)
