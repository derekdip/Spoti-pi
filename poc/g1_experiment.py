"""G1: growing the gait grammar toward damaged bodies. Prereg: docs/math-track-g1-prereg.md.

Per case (body, teacher seed): from V0 (the walk base fitted once on the intact teacher), three
selection rules grow the grammar along their own paths for STEPS steps with no stopping rule and the
spent rule (a repair worth under one percent is not applied and its class is blacklisted):

  projection  the arc's selector on the signed tangents, one repair fitted per step;
  hybrid      the dictionary check applied (poc/results/gait_dictionary_check.json): classes whose
              gap on the design bodies was over 0.25 are fitted to be ranked, the rest are ranked by
              projection and the top two fitted; the best fitted drop is taken;
  oracle      every repairable class fitted, best drop taken.

At every step of every path the full oracle table is computed, so value is measured against the
same table. The joint floor (every repairable parameter free at once, differential evolution from V0)
is computed once per case. Pictures of the terminal states are saved beside the JSON.
"""
from __future__ import annotations

import argparse, json, sys, time
from dataclasses import replace, asdict
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.gait import biped, grammar as G, rgre_gait as RG
from poc.gait.compare import compare
from poc.rgre.core import diagnose, select_projection

STEPS = 4
DEAD = 0.01
NO_GATE = 1.01
K_SMALL = 2
FITTED = ("kneel_l", "kneel_r", "weak_l", "weak_r")        # gap over 0.25 on the design bodies: fit to rank
PROJECTED = ("stiff_l", "stiff_r", "short_l", "short_r", "hop", "vault")
DESIGN = [(m, 0) for m in biped.MORPHS]
TRANSFER = [(m, 0) for m in biped.MIRRORS] + [("intact", 1), ("nolegs", 1)]
DESIGNED = {"locked_knee": "stiff", "short_shank": "short", "stump": "kneel", "noleg": "hop", "nolegs": "vault"}
VARIANTS = ("projection", "hybrid", "oracle")


def designed_class(morph):
    side, kind = biped.side_of(morph)
    if kind in ("locked_knee", "short_shank", "stump"):
        return f"{DESIGNED[kind]}_{side[0]}"
    if kind == "noleg":
        return "hop"
    if morph == "nolegs":
        return "vault"
    return None


def v0_state():
    return replace(G.GaitState(), **json.load(open("poc/results/gait_v0.json"))["state"])


def step_record(case, st, cand):
    r = case.residual(st); signed = case.tangents(st)
    diag = diagnose(r, signed, {}, support=())
    _, _, ranked = select_projection(diag, NO_GATE, {c: [c] for c in G.CLASSES}, unrepairable=(), blacklist=[])
    ranked = [c for c in ranked if c in cand]
    e0 = case.error(st)
    table = {c: RG.repair_gain(case, st, c) for c in cand}
    return dict(ranked=ranked, e0=e0, table=table, q_top=float(max(diag["q"].values())) if diag and diag["q"] else 0.0)


def choose(variant, rec, blacklist, cand):
    ranked = [c for c in rec["ranked"] if c not in blacklist]
    live = [c for c in cand if c not in blacklist]
    table = rec["table"]
    if variant == "projection":
        return (ranked[0] if ranked else None), 1
    if variant == "oracle":
        return (max(live, key=lambda c: table[c]["drop"]) if live else None), len(live)
    pool = [c for c in live if c in FITTED] + [c for c in ranked if c in PROJECTED][:K_SMALL]
    return (max(pool, key=lambda c: table[c]["drop"]) if pool else None), len(pool)


def run_case(args):
    morph, seed = args
    T0 = time.time()
    case = RG.GaitCase(morph, seed)
    v0 = v0_state()
    cand = case.repairable()
    out = dict(case=case.name, morph=morph, seed=seed, group="design" if (morph, seed) in DESIGN else "transfer",
               designed=designed_class(morph), candidates=cand, e_v0=case.error(v0), per_consumer_v0=case.per_consumer(v0), variants={})
    for variant in VARIANTS:
        st, blacklist, steps = v0, [], []
        for t in range(STEPS):
            rec = step_record(case, st, cand)
            live = [c for c in cand if c not in blacklist]
            oracle = max(live, key=lambda c: rec["table"][c]["drop"]) if live else None
            odrop = rec["table"][oracle]["drop"] if oracle else 0.0
            pick, evaluated = choose(variant, rec, blacklist, cand)
            row = dict(t=t, ranked=rec["ranked"][:5], oracle=oracle, oracle_drop_rel=odrop / rec["e0"], evaluated=evaluated,
                       e_before=rec["e0"], q_top=rec["q_top"], drops={c: rec["table"][c]["drop"] / rec["e0"] for c in cand})
            if pick is None:
                row.update(pick=None, dead=True, e_after=rec["e0"], value=0.0); steps.append(row); continue
            g = rec["table"][pick]; dead = g["drop"] < DEAD * rec["e0"]
            row.update(pick=pick, dead=bool(dead), drop_rel=g["drop"] / rec["e0"],
                       value=(g["drop"] / odrop) if odrop > 1e-12 else (1.0 if g["drop"] >= odrop else 0.0))
            if dead:
                blacklist.append(pick); row["e_after"] = rec["e0"]
            else:
                st = g["state"]; row["e_after"] = g["e1"]
            steps.append(row)
            print(f"   [{case.name}/{variant}] t{t} pick {str(pick):<8} oracle {str(oracle):<8} value {row['value']:.2f} "
                  f"E {rec['e0']:.4f}->{row['e_after']:.4f} ({evaluated} of {len(cand)}) [{time.time()-T0:.0f}s]", flush=True)
        active = [c for c in G.CLASSES if c not in G.V0_CLASSES and G.is_on(st, c)]
        out["variants"][variant] = dict(steps=steps, e_final=case.error(st), active=active, per_consumer=case.per_consumer(st),
                                        state=asdict(st), added=[s["pick"] for s in steps if s.get("pick") and not s["dead"]])
        if variant == "hybrid":
            compare(case, st, f"poc/results/g1_{case.name}_hybrid.png", f"{case.name}: teacher vs hybrid terminal, error {case.error(st):.3f}, classes {active}")
    t1 = time.time()
    fl, e_fl = RG.joint_fit(case, v0, seed=0, maxiter=25, popsize=8)
    out["floor"] = dict(e=e_fl, seconds=round(time.time() - t1), per_consumer=case.per_consumer(fl))
    out["seconds"] = time.time() - T0
    return out


def main(cases, out_path, workers):
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, cases):
            recs.append(rec)
            v = rec["variants"]
            print(f"{rec['case']:<22} [{rec['group']}] designed {rec['designed']} v0 {rec['e_v0']:.3f} | " +
                  " ".join(f"{k} {v[k]['e_final']:.3f} {v[k]['added']}" for k in VARIANTS) +
                  f" | floor {rec['floor']['e']:.3f} [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(STEPS=STEPS, DEAD=DEAD, FITTED=FITTED, PROJECTED=PROJECTED, cases=recs), open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="all", help="all | design | transfer | morph:seed,...")
    ap.add_argument("--out", default="poc/results/g1.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    STEPS = a.steps
    if a.cases == "all": cases = DESIGN + TRANSFER
    elif a.cases == "design": cases = DESIGN
    elif a.cases == "transfer": cases = TRANSFER
    else: cases = [(x.split(":")[0], int(x.split(":")[1])) for x in a.cases.split(",")]
    main(cases, a.out, a.workers)
