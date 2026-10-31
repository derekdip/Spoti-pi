"""G3: growth that a teacher's noise cannot pass, and a per-consumer guard. Prereg: docs/math-track-g3-prereg.md.

Every case has two runs of its teacher: the fitting run and a held-out run of the same body with
the seed advanced. Two rules are added to G2's oracle path, both measured rather than chosen:

  held-out acceptance   a repair is applied only if it lowers the error against the held-out run
                        as well as the fitting run; a class fitted to one run's noise does not;
  per-consumer guard    a repair may not worsen any consumer, against the fitting run, by more
                        than that consumer's tolerance, the distance between the two teacher runs
                        on that consumer at V0.

At each step every repairable class is fitted on the fitting run; candidates are taken in order of
fitting drop and the first admissible one is applied; the step is declined when none is. Identity
counts impairment repairs only, with the side sign, as in G2.
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
from poc.g2_experiment import designed, DESIGN, TRANSFER

STEPS = 6
DEAD = 0.01


def run_case(args):
    morph, seed = args
    T0 = time.time()
    fit = RG.GaitCase(morph, seed)
    ho = RG.GaitCase(morph, 1 - seed)
    v0 = RG.load_v0()
    cand = fit.repairable()
    dcls, dsign = designed(morph)
    # tolerance per consumer: how far the two runs of this body are apart on each block, at V0's scale
    p_ho = RG.consumers(fit.body, ho.q_teacher)
    tol = {k: float(np.sqrt(((fit.target[k] - p_ho[k]) ** 2).mean()) / fit.scale[k]) for k in fit.names}
    out = dict(case=fit.name, morph=morph, seed=seed, heldout_seed=1 - seed, group="design" if (morph, seed) in DESIGN else "transfer",
               designed=dcls, designed_sign=dsign, candidates=cand, tolerance=tol,
               e_v0=fit.error(v0), e_v0_heldout=ho.error(v0), per_consumer_v0=fit.per_consumer(v0))
    st, blacklist, steps, added = v0, [], [], []
    for t in range(STEPS):
        e0 = fit.error(st); e0_ho = ho.error(st); pc0 = fit.per_consumer(st)
        live = [c for c in cand if c not in blacklist]
        table = {c: RG.repair_gain(fit, st, c) for c in live}
        order = sorted(live, key=lambda c: -table[c]["drop"])
        row = dict(t=t, e_before=e0, e_before_heldout=e0_ho, drops={c: table[c]["drop"] / e0 for c in live},
                   sides={c: G.side_sign(table[c]["state"], c) for c in live}, rejected={}, pick=None)
        chosen = None
        for c in order:
            g = table[c]
            if g["drop"] < DEAD * e0:
                row["rejected"][c] = "spent"; continue
            e1_ho = ho.error(g["state"])
            if e1_ho >= e0_ho:
                row["rejected"][c] = f"held-out {e1_ho:.4f} >= {e0_ho:.4f}"; continue
            pc1 = fit.per_consumer(g["state"])
            over = [k for k in pc1 if pc1[k] > pc0[k] + tol[k]]
            if over:
                row["rejected"][c] = "guard: " + ", ".join(over); continue
            chosen = c; break
        if chosen is None:
            row.update(dead=True, e_after=e0, e_after_heldout=e0_ho); steps.append(row)
            print(f"   [{fit.name}] t{t} declined: " + "; ".join(f"{c} {r}" for c, r in list(row['rejected'].items())[:4]) + f" [{time.time()-T0:.0f}s]", flush=True)
            break
        g = table[chosen]; st = g["state"]
        row.update(pick=chosen, side=G.side_sign(st, chosen), dead=False, drop_rel=g["drop"] / e0, e_after=g["e1"], e_after_heldout=ho.error(st),
                   oracle=order[0], value=g["drop"] / table[order[0]]["drop"] if table[order[0]]["drop"] > 1e-12 else 1.0)
        added.append((chosen, row["side"]))
        steps.append(row)
        print(f"   [{fit.name}] t{t} pick {chosen:<6} side {row['side']:+d} (oracle {order[0]}, value {row['value']:.2f}) "
              f"fit {e0:.4f}->{g['e1']:.4f} held-out {e0_ho:.4f}->{row['e_after_heldout']:.4f} rejected {list(row['rejected'])} [{time.time()-T0:.0f}s]", flush=True)
    active = [c for c in G.IMPAIRMENTS if G.is_on(st, c)]
    out.update(steps=steps, added=added, active=active, e_final=fit.error(st), e_final_heldout=ho.error(st),
               per_consumer=fit.per_consumer(st), state=asdict(st), seconds=time.time() - T0)
    compare(fit, st, f"poc/results/g3_{fit.name}_checked.png", f"{fit.name}: teacher vs checked terminal, error {fit.error(st):.3f} (held-out {ho.error(st):.3f}), classes {active}")
    return out


def main(cases, out_path, workers):
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, cases):
            recs.append(rec)
            fmt = [f"{a}{s:+d}" if s else a for a, s in rec["added"]]
            print(f"{rec['case']:<22} [{rec['group']}] designed {rec['designed']}{rec['designed_sign']:+d} v0 {rec['e_v0']:.3f}/{rec['e_v0_heldout']:.3f} -> "
                  f"{rec['e_final']:.3f}/{rec['e_final_heldout']:.3f} added {fmt} [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(STEPS=STEPS, DEAD=DEAD, cases=recs), open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="all")
    ap.add_argument("--out", default="poc/results/g3.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    STEPS = a.steps
    if a.cases == "all": cases = DESIGN + TRANSFER
    elif a.cases == "design": cases = DESIGN
    elif a.cases == "transfer": cases = TRANSFER
    else: cases = [(x.split(":")[0], int(x.split(":")[1])) for x in a.cases.split(",")]
    main(cases, a.out, a.workers)
