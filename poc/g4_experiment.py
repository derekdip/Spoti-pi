"""G4: acceptance against two held-out runs of the teacher. Prereg: docs/math-track-g4-prereg.md.

Every body has three teacher runs. One is the fitting run (the same run G2 and G3 fitted); the other
two are held out. G3's two rules are kept with the held-out side widened from one run to the mean of
two, and nothing else changes:

  held-out acceptance   a repair is applied only if it lowers the mean error against the two
                        held-out runs; the number of held-out runs it lowers (0, 1, 2) is recorded;
  per-consumer guard    a repair may not worsen any consumer, against the fitting run, by more
                        than that consumer's tolerance, the mean distance between the fitting run
                        and each held-out run on that consumer at V0.

Candidates are taken in order of fitting drop, as in G2 and G3; the first admissible one is applied;
the step is declined when none is. Identity counts impairment repairs only, with the side sign.
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
SEEDS = (0, 1, 2)


def run_case(args):
    morph, seed = args
    T0 = time.time()
    fit = RG.GaitCase(morph, seed)
    hos = [RG.GaitCase(morph, s) for s in SEEDS if s != seed]
    v0 = RG.load_v0()
    cand = fit.repairable()
    dcls, dsign = designed(morph)
    p_hos = [RG.consumers(fit.body, h.q_teacher) for h in hos]
    tol = {k: float(np.mean([np.sqrt(((fit.target[k] - p[k]) ** 2).mean()) for p in p_hos]) / fit.scale[k]) for k in fit.names}
    e_ho = lambda st: [h.error(st) for h in hos]
    ho_v0 = e_ho(v0)
    out = dict(case=fit.name, morph=morph, seed=seed, heldout_seeds=[h.seed for h in hos], group="design" if (morph, seed) in DESIGN else "transfer",
               designed=dcls, designed_sign=dsign, candidates=cand, tolerance=tol,
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
    compare(fit, st, f"poc/results/g4_{fit.name}_checked.png", f"{fit.name}: teacher vs checked terminal, error {fit.error(st):.3f} (held-out mean {np.mean(ho_f):.3f}), classes {active}")
    return out


def main(cases, out_path, workers):
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, cases):
            recs.append(rec)
            fmt = [f"{a}{s:+d}" if s else a for a, s in rec["added"]]
            print(f"{rec['case']:<22} [{rec['group']}] designed {rec['designed']}{rec['designed_sign']:+d} v0 {rec['e_v0']:.3f}/{rec['e_v0_heldout']:.3f} -> "
                  f"{rec['e_final']:.3f}/{rec['e_final_heldout']:.3f} added {fmt} [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(STEPS=STEPS, DEAD=DEAD, SEEDS=SEEDS, cases=recs), open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="all")
    ap.add_argument("--out", default="poc/results/g4.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    STEPS = a.steps
    if a.cases == "all": cases = DESIGN + TRANSFER
    elif a.cases == "design": cases = DESIGN
    elif a.cases == "transfer": cases = TRANSFER
    else: cases = [(x.split(":")[0], int(x.split(":")[1])) for x in a.cases.split(",")]
    main(cases, a.out, a.workers)
