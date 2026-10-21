"""F7: the hybrid selector made the fire workflow's default, and the F4 comparison re-run.
Prereg: docs/math-track-f7-prereg.md.

F6 established the hybrid rule (fit the large-gap classes, project the rest) and found its
remaining losses were the projection's ranking among the small-gap classes, with F1's support
templates the suspect. F7 makes one declared change: the small-gap classes are ranked by the
signed tangents alone, no templates. A second variant that fits the top two small-gap classes is
run beside it and reported. Ten steps, F4's budget, on F4's seven scenes, with the full oracle
table at every step of every path so value is measured against the same table. The terminal
state of each path is scored exactly as F4 scored its states (poc/fire_decisions.decisions), so
the glow correlation and the decision rates compare directly with F4's floor and look fits.
"""
from __future__ import annotations

import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP
from poc.fire_decisions import decisions
from poc.rgre.core import diagnose, select_projection
from poc.f6_experiment import repairable, gap_of, LARGE_GAP, SMALL_GAP, UNMEASURED

STEPS = 10
DEAD = 0.01
NO_GATE = 1.01
UNSEEN = ["ignition", "delayed_ignition", "full", "twin", "shelf_bed", "split", "shutoff"]
VARIANTS = {"hybrid_nt": 1, "hybrid_nt2": 2}     # small-gap classes fitted per step


def step_record(case, st, cand):
    r = case.residual(st)
    signed = case.tangents(st)
    diag = diagnose(r, signed, {}, support=())                     # no templates: the declared change
    _, _, ranked = select_projection(diag, NO_GATE, {c: [c] for c in RP.CLASSES}, unrepairable=(), blacklist=[])
    ranked = [c for c in ranked if c in cand]
    rv = r.ravel(); e0 = case.error(st)
    table, gaps = {}, {}
    for c in cand:
        g = RP.repair_gain(case, st, c)
        table[c] = g
        f = rv - case.residual(g["state"]).ravel()
        gaps[c] = gap_of(f, signed[c]) if c in signed else 1.0
    return dict(ranked=ranked, e0=e0, table=table, gaps=gaps)


def choose(k_small, rec, blacklist, cand):
    ranked = [c for c in rec["ranked"] if c not in blacklist]
    large = [c for c in cand if c in LARGE_GAP and c not in blacklist]
    small = [c for c in ranked if c in SMALL_GAP or c in UNMEASURED][:k_small]
    pool = large + small
    if not pool:
        return None, 0
    return max(pool, key=lambda c: rec["table"][c]["drop"]), len(pool)


def score(case, st):
    dec = decisions(case, st, as_record=puffs.as_record)
    return dict(error=case.error(st), per_consumer=case.per_consumer(st), live=st.live_count(),
                motion=RP.motion_ratio(case, st), decisions=dec,
                state={k: getattr(st, k) for k in st.__dataclass_fields__})


def run_scene(name):
    T0 = time.time()
    case = RP.PuffCase(name, getattr(scenes, name)())
    cand = repairable(case)
    v0 = puffs.PuffState()
    out = dict(scene=name, candidates=cand, e_v0=case.error(v0), variants={})
    for variant, k_small in VARIANTS.items():
        st, blacklist, steps = v0, [], []
        for t in range(STEPS):
            rec = step_record(case, st, cand)
            live = [c for c in cand if c not in blacklist]
            oracle = max(live, key=lambda c: rec["table"][c]["drop"]) if live else None
            odrop = rec["table"][oracle]["drop"] if oracle else 0.0
            pick, evaluated = choose(k_small, rec, blacklist, cand)
            row = dict(t=t, e_in_before=rec["e0"], ranked=rec["ranked"][:5], oracle=oracle, evaluated=evaluated,
                       oracle_drop_rel=odrop / rec["e0"], gaps={c: round(v, 4) for c, v in rec["gaps"].items()})
            if pick is None:
                row.update(pick=None, dead=True, e_in_after=rec["e0"], value=0.0, drop_rel=0.0); steps.append(row); continue
            g = rec["table"][pick]
            dead = g["drop"] < DEAD * rec["e0"]
            row.update(pick=pick, dead=bool(dead), drop_rel=g["drop"] / rec["e0"],
                       value=(g["drop"] / odrop) if odrop > 1e-12 else (1.0 if g["drop"] >= odrop else 0.0),
                       gap_pick=rec["gaps"][pick], gap_oracle=rec["gaps"][oracle] if oracle else 1.0)
            if dead:
                blacklist.append(pick); row["e_in_after"] = rec["e0"]
            else:
                st = g["state"]; row["e_in_after"] = g["e1"]
            steps.append(row)
            print(f"   [{name}/{variant}] t{t} pick {str(pick):<9} oracle {str(oracle):<9} value {row['value']:.2f} "
                  f"E {rec['e0']:.4f}->{row['e_in_after']:.4f} ({evaluated} of {len(cand)}) [{time.time()-T0:.0f}s]", flush=True)
        sc = score(case, st)
        out["variants"][variant] = dict(steps=steps, e_final=sc["error"], terminal=sc)
    out["seconds"] = time.time() - T0
    return out


def main(scene_list, out_path, workers, steps):
    global STEPS
    STEPS = steps
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_scene, scene_list):
            recs.append(rec)
            v = rec["variants"]
            print(f"{rec['scene']:<17} v0 {rec['e_v0']:.3f} | " + " ".join(
                f"{k} {v[k]['e_final']:.3f} (value med {np.median([s['value'] for s in v[k]['steps']]):.2f}, glow {v[k]['terminal']['decisions']['visual']['late_correlation']:.2f})"
                for k in VARIANTS) + f" [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(STEPS=STEPS, DEAD=DEAD, scenes=recs), open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} scenes in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default=",".join(UNSEEN))
    ap.add_argument("--out", default="poc/results/f7.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    main(a.scenes.split(","), a.out, a.workers, a.steps)
