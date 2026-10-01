"""F6: the two changes from the ML track folded into the fire workflow. Prereg: docs/math-track-f6-prereg.md.

Three selection rules grow the puff grammar on each scene, each along its own path, to a budget of
S_MAX steps with no stopping rule, so that every stopping rule can be scored afterwards from the
same recorded curves:

  projection  the arc's selector (poc/rgre/core.select_projection with F1's support templates),
              one repair fitted per step;
  hybrid      the dictionary check applied: classes whose step-zero linearisation gap was over
              0.25 on the design scenes are fitted to be ranked, the rest are ranked by projection
              and the top one fitted; the best fitted drop is taken;
  oracle      every repairable class fitted, best drop taken.

At every step of every path the full oracle table is computed (every class fitted from the current
state), so the value each rule captures is measured against the same table, and the count of
repairs each rule would have needed is recorded rather than the compute actually spent. Also
recorded: the abstention statistic q_top and its shuffle null (residual permuted within each
consumer block, M_PERM times), the linearisation gap of every fitted class, the in-sample error
and the error against a second teacher run of the same scene with a different seed (held-out).
"""
from __future__ import annotations

import argparse, json, sys, time
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP
from poc.rgre.core import diagnose, select_projection, orth

S_MAX = 8
DEAD = 0.01
M_PERM = 49
NO_GATE = 1.01
DESIGN = ["windy", "obstacle", "twin", "split", "shutoff", "ignition", "delayed_ignition", "full", "shelf_bed"]
TRANSFER = ["gusty", "gust_shelf", "fast_gust", "strong_gust", "gust_twin", "bed_chain"]
# the dictionary check, from poc/results/fire_lin_gap.json (step-zero medians over the design scenes)
LARGE_GAP = ("amp", "cool", "wind", "rate", "bed", "rise")          # gap >= 0.25: fit to rank
SMALL_GAP = ("width", "deflect", "profile", "base", "attract")      # gap < 0.25: projection ranks
UNMEASURED = ("jitter", "soot", "floor")                            # inert at step zero: projection ranks
VARIANTS = ("projection", "hybrid", "oracle")


def repairable(case):
    out = []
    for c in RP.CLASSES:
        if c == "bed" and not case.patches: continue
        if c == "deflect" and not case.obstacles: continue
        if c == "attract" and len(case.burners) < 2: continue
        out.append(c)
    return out


def class_bases(signed):
    cols, idx, names = [], [], []
    for c, vs in signed.items():
        Q = orth(vs)
        if Q.shape[1] == 0: continue
        cols.append(Q); idx += [len(names)] * Q.shape[1]; names.append(c)
    if not cols:
        return None, None, []
    return np.concatenate(cols, 1), np.array(idx), names


def q_top_many(B, idx, ncls, Rm):
    P = (B.T @ Rm) ** 2
    E = (Rm ** 2).sum(0)
    G = np.zeros((ncls, B.shape[1])); G[idx, np.arange(B.shape[1])] = 1.0
    return (G @ P / np.maximum(E, 1e-300)).max(0)


def shuffled(case, r, rng, m):
    """m copies of the residual with entries permuted within each consumer block."""
    blocks, _ = case.blocks()
    F = r.shape[0]
    out = np.empty((r.size, m))
    for j in range(m):
        rr = r.copy()
        for c, (a, b) in blocks.items():
            blk = rr[:, a:b].ravel()
            rr[:, a:b] = rng.permutation(blk).reshape(F, b - a)
        out[:, j] = rr.ravel()
    return out


def gap_of(f, vs):
    Q = orth(vs); ff = float(f @ f)
    if ff <= 0 or Q.shape[1] == 0: return 1.0
    p = Q.T @ f
    return float(max(0.0, 1.0 - float(p @ p) / ff))


def step_record(case, case_ho, st, blacklist, rng, cand):
    """Everything measured at one state: diagnosis, null, oracle table, gaps."""
    r = case.residual(st)
    signed = case.tangents(st)
    diag = diagnose(r, signed, case.templates(), support=RP.SUPPORT_CLASSES)
    sets = {c: [c] for c in RP.CLASSES}
    _, _, ranked = select_projection(diag, NO_GATE, sets, unrepairable=(), blacklist=[])
    ranked = [c for c in ranked if c in cand]
    rv = r.ravel()
    B, idx, names = class_bases({c: v for c, v in signed.items() if c in cand})
    if B is not None:
        obs = float(q_top_many(B, idx, len(names), rv[:, None])[0])
        null = q_top_many(B, idx, len(names), shuffled(case, r, rng, M_PERM))
    else:
        obs, null = 0.0, np.zeros(M_PERM)
    e0 = case.error(st)
    table, gaps = {}, {}
    for c in cand:
        g = RP.repair_gain(case, st, c)
        table[c] = g
        f = rv - case.residual(g["state"]).ravel()
        gaps[c] = gap_of(f, signed[c]) if c in signed else 1.0
    live = [c for c in cand if c not in blacklist]
    oracle = max(live, key=lambda c: table[c]["drop"]) if live else None
    return dict(r=r, ranked=ranked, q_top=obs, null=[float(x) for x in null], e0=e0, table=table, gaps=gaps,
                oracle=oracle, ho0=case_ho.error(st))


def choose(variant, rec, blacklist, cand):
    ranked = [c for c in rec["ranked"] if c not in blacklist]
    table = rec["table"]
    if variant == "projection":
        return (ranked[0] if ranked else None), 1
    if variant == "oracle":
        live = [c for c in cand if c not in blacklist]
        return rec["oracle"], len(live)
    # hybrid: fitted large-gap classes plus projection's top small-gap class
    large = [c for c in cand if c in LARGE_GAP and c not in blacklist]
    small_top = next((c for c in ranked if c in SMALL_GAP or c in UNMEASURED), None)
    pool = large + ([small_top] if small_top else [])
    if not pool:
        return None, 0
    return max(pool, key=lambda c: table[c]["drop"]), len(pool)


def run_scene(name):
    T0 = time.time()
    scene = getattr(scenes, name)()
    case = RP.PuffCase(name, scene)
    p, burners, patches, obstacles = scene
    case_ho = RP.PuffCase(name, (replace(p, seed=p.seed + 1), burners, patches, obstacles))
    cand = repairable(case)
    v0 = puffs.PuffState()
    out = dict(scene=name, group="design" if name in DESIGN else "transfer", candidates=cand,
               e_v0=case.error(v0), ho_v0=case_ho.error(v0), noise_floor=None, variants={})
    # the noise floor: the two teacher runs against each other, in the case's own units
    out["noise_floor"] = float(np.sqrt(sum((((case.target[c] - case_ho.target[c]) / case.scale[c]) ** 2).mean() for c in case.names) / len(case.names)))
    rng = np.random.default_rng(len(name) * 7 + 1)
    shared0 = None
    for variant in VARIANTS:
        st, blacklist, steps = v0, [], []
        for t in range(S_MAX):
            if t == 0 and shared0 is not None:
                rec = shared0
            else:
                rec = step_record(case, case_ho, st, blacklist, rng, cand)
                if t == 0: shared0 = rec
            pick, evaluated = choose(variant, rec, blacklist, cand)
            row = dict(t=t, q_top=rec["q_top"], null=rec["null"], e_in_before=rec["e0"], e_ho_before=rec["ho0"],
                       ranked=rec["ranked"][:5], oracle=rec["oracle"], evaluated=evaluated,
                       gaps={c: round(v, 4) for c, v in rec["gaps"].items()},
                       oracle_drop_rel=(rec["table"][rec["oracle"]]["drop"] / rec["e0"]) if rec["oracle"] else 0.0)
            if pick is None:
                row.update(pick=None, dead=True, e_in_after=rec["e0"], e_ho_after=rec["ho0"], value=0.0, drop_rel=0.0)
                steps.append(row); continue
            g = rec["table"][pick]
            dead = g["drop"] < DEAD * rec["e0"]
            odrop = rec["table"][rec["oracle"]]["drop"] if rec["oracle"] else 0.0
            row.update(pick=pick, dead=bool(dead), drop_rel=g["drop"] / rec["e0"],
                       value=(g["drop"] / odrop) if odrop > 1e-12 else (1.0 if g["drop"] >= odrop else 0.0),
                       gap_pick=rec["gaps"][pick], gap_oracle=rec["gaps"][rec["oracle"]] if rec["oracle"] else 1.0)
            if dead:
                blacklist.append(pick)
                row.update(e_in_after=rec["e0"], e_ho_after=rec["ho0"])   # a dead repair is not applied
            else:
                st = g["state"]
                row.update(e_in_after=g["e1"], e_ho_after=case_ho.error(st))
            steps.append(row)
            print(f"   [{name}/{variant}] t{t} pick {str(pick):<9} oracle {str(rec['oracle']):<9} value {row['value']:.2f} "
                  f"in {rec['e0']:.4f}->{row['e_in_after']:.4f} ho {row['e_ho_after']:.4f} q_top {rec['q_top']:.3f} null {max(rec['null'][:19]):.3f} "
                  f"[{time.time()-T0:.0f}s]", flush=True)
        out["variants"][variant] = dict(steps=steps, e_in_final=steps[-1]["e_in_after"], e_ho_final=steps[-1]["e_ho_after"],
                                        state=st.__dict__ if hasattr(st, "__dict__") else None)
    out["seconds"] = time.time() - T0
    return out


def main(scene_list, out_path, workers):
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_scene, scene_list):
            recs.append(rec)
            v = rec["variants"]
            print(f"{rec['scene']:<17} [{rec['group']}] v0 {rec['e_v0']:.3f} floor {rec['noise_floor']:.3f} | final in/ho: "
                  + " ".join(f"{k} {v[k]['e_in_final']:.3f}/{v[k]['e_ho_final']:.3f}" for k in VARIANTS)
                  + f" | value med proj {np.median([s['value'] for s in v['projection']['steps']]):.2f} hyb {np.median([s['value'] for s in v['hybrid']['steps']]):.2f}"
                  + f" [{rec['seconds']:.0f}s]", flush=True)
            json.dump(dict(S_MAX=S_MAX, DEAD=DEAD, M_PERM=M_PERM, LARGE_GAP=LARGE_GAP, SMALL_GAP=SMALL_GAP, scenes=recs),
                      open(out_path, "w"), indent=1)
    print(f"done: {len(recs)} scenes in {time.time()-T0:.0f}s -> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default=",".join(DESIGN + TRANSFER))
    ap.add_argument("--out", default="poc/results/f6.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--steps", type=int, default=None)
    a = ap.parse_args()
    if a.steps: S_MAX = a.steps
    main(a.scenes.split(","), a.out, a.workers)
