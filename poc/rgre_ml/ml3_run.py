"""RGRE-ML-3: a stopping rule with no constant, and the linearisation gap, on the RGRE-ML-2 splits.

The growth path is RGRE-ML-2's, re-grown deterministically (same data, same seeds, same picks; the
scorer checks the modules added against the frozen run). At every step two new things are recorded.

The null. The statistic the abstention quantity is built on, q_top = max over classes of the share
of residual energy the class's tangent subspace explains, is recomputed M_PERM times with the
residual shuffled across samples. Shuffling keeps the residual's values and breaks its relation to
the inputs, which is the hypothesis "nothing here is structure a candidate can find". A rule that
declines a step when any of the first M shuffles reaches the observed value is a permutation test
at level 1/(M+1) with M a budget rather than a tuned constant; M = 9, 19 and 49 are all recorded.

The linearisation gap. For every candidate the oracle fits, the fraction of its fitted contribution
that lies outside the tangent span the ranking used: 1 - cos^2(f*, span T_c). Zero by construction
for a one-parameter linear module; the number that says how far a free-shape module's fit ends
from where its tangent pointed. Post-hoc, no bar.
"""
from __future__ import annotations

import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.rgre import core
from poc.rgre_ml import real as R
from poc.rgre_ml.run_real import S_MAX, DEAD, diagnose

M_PERM = 49


def class_bases(signed):
    """One orthonormal basis per class, stacked, with the class index of each column."""
    cols, idx, names = [], [], []
    for i, (c, vs) in enumerate(signed.items()):
        Q = core.orth(vs)
        if Q.shape[1] == 0:
            continue
        cols.append(Q); idx += [len(names)] * Q.shape[1]; names.append(c)
    B = np.concatenate(cols, 1)
    return B, np.array(idx), names


def q_top_many(B, idx, ncls, Rm):
    """q_top for every column of Rm (n, m): the largest per-class explained share."""
    P = (B.T @ Rm) ** 2                                   # (K, m)
    E = (Rm ** 2).sum(0)                                  # (m,)
    G = np.zeros((ncls, B.shape[1])); G[idx, np.arange(B.shape[1])] = 1.0
    q = G @ P / np.maximum(E, 1e-300)                     # (ncls, m)
    return q.max(0)


def gap(f, vs):
    Q = core.orth(vs)
    ff = float(f @ f)
    if ff <= 0 or Q.shape[1] == 0:
        return 1.0
    p = Q.T @ f
    return float(max(0.0, 1.0 - float(p @ p) / ff))


def run_case(args):
    name, seed = args
    T0 = time.time()
    case = R.RCase(name, seed)
    rng = np.random.default_rng(seed * 104729 + len(name))
    s = case.student0()
    rec = dict(dataset=name, seed=seed, n_train=int(case.n), d=int(case.d), n_candidates=len(case.mods),
               test_err_linear=case.test_error(s))
    steps, states = [], [s]
    for t in range(S_MAX):
        d, r, signed = diagnose(case, s)
        rv = r.ravel()
        B, idx, names = class_bases(signed)
        obs = float(q_top_many(B, idx, len(names), rv[:, None])[0])
        Rm = np.stack([rng.permutation(rv) for _ in range(M_PERM)], 1)
        null = q_top_many(B, idx, len(names), Rm)
        e0, table = case.oracle_table(s)
        oracle = max(table, key=lambda c: table[c]["drop"])
        pick = d["pick"]
        p0 = case.predict(s, case.Xtr)
        signed_anch = case.tangents(s, anchored=True)
        gaps, gaps_anch = {}, {}
        for c, row in table.items():
            f = case.predict(row["state"], case.Xtr) - p0
            gaps[c] = gap(f, signed[c]) if c in signed else 1.0
            gaps_anch[c] = gap(f, signed_anch[c]) if c in signed_anch else 1.0
        kinds = {}
        for c in table:
            kinds.setdefault(c.split("_")[0], []).append(gaps[c])
        new = table[pick]["state"]
        step = dict(t=t, pick=pick, oracle=oracle, q_top=obs, q_perp=1.0 - obs, q_null=[float(x) for x in null],
                    train_err_before=e0, train_err_after=table[pick]["e1"], train_drop_rel=(e0 - table[pick]["e1"]) / e0,
                    test_err_before=case.test_error(s), test_err_after=table[pick]["test"],
                    value=float(table[pick]["drop"] / table[oracle]["drop"]) if table[oracle]["drop"] > 1e-12 else 1.0,
                    gap_oracle=gaps[oracle], gap_pick=gaps[pick], gap_anch_oracle=gaps_anch[oracle],
                    gap_by_kind={k: float(np.median(v)) for k, v in kinds.items()},
                    drop_by_kind={k: float(max(table[c]["drop"] for c in table if c.split("_")[0] == k)) / e0 for k in kinds},
                    dead=(e0 - table[pick]["e1"]) < DEAD * e0)
        steps.append(step)
        s = new; states.append(s)
    rec["steps"] = steps
    rec["test_curve"] = [case.test_error(x) for x in states]
    rec["modules_added"] = [st["pick"] for st in steps]
    # the same statistic and null on permuted targets at step zero: what the rule does on pure noise
    yp = rng.permutation(case.ytr)
    sp = case.student0(yp)
    dp, rp, sgp = diagnose(case, sp, yp)
    rvp = rp.ravel()
    B, idx, names = class_bases(sgp)
    obs_p = float(q_top_many(B, idx, len(names), rvp[:, None])[0])
    null_p = q_top_many(B, idx, len(names), np.stack([rng.permutation(rvp) for _ in range(M_PERM)], 1))
    rec["perm"] = dict(q_top=obs_p, q_null=[float(x) for x in null_p])
    rec["seconds"] = time.time() - T0
    return rec


def line(rec):
    st = rec["steps"]
    def stop(M):
        return next((s["t"] for s in st if s["q_top"] <= max(s["q_null"][:M])), S_MAX)
    tc = rec["test_curve"]
    return (f"{rec['dataset']:<11} seed {rec['seed']}  lin {tc[0]:.3f} best {min(tc):.3f}@{int(np.argmin(tc))} | "
            f"stop M9 {stop(9)} M19 {stop(19)} M49 {stop(49)} dead {next((s['t'] for s in st if s['dead']), S_MAX)} | "
            f"q_top0 {st[0]['q_top']:.3f} null max {max(st[0]['q_null'][:19]):.3f} | "
            f"gap oracle med {np.median([s['gap_oracle'] for s in st]):.2f} pick {np.median([s['gap_pick'] for s in st]):.2f} | "
            f"perm q_top {rec['perm']['q_top']:.3f} null max {max(rec['perm']['q_null'][:19]):.3f} [{rec['seconds']:.0f}s]")


def main(datasets, seeds, out, workers):
    jobs = [(n, s) for n in datasets for s in seeds]
    recs, T0 = [], time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, jobs):
            recs.append(rec)
            print(line(rec), flush=True)
            json.dump(dict(M_PERM=M_PERM, S_MAX=S_MAX, cases=recs), open(out, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default=",".join(R.DATASETS))
    ap.add_argument("--seeds", default="1,2,3,4,5")
    ap.add_argument("--out", default="poc/results/rgre_ml3.json")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    main(a.datasets.split(","), [int(x) for x in a.seeds.split(",")], a.out, a.workers)
