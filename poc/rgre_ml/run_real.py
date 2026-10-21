"""RGRE-ML-2: grow a dictionary model on real data, one repair per step, and record what the
procedure's own quantities said before each step.

Per case (dataset x split seed): the linear student, then S_MAX growth steps. Before each step the
field residual is diagnosed (poc/rgre/core.py, unchanged) and the pick is the class of the single
tangent direction with the largest squared cosine to the residual, abstention off. The exhaustive
oracle fits every candidate at every step. The abstention quantity is recorded two ways: the joint
version RGRE-ML-1 used (energy left after projecting on every candidate direction at once), which
is degenerate here because the dictionary has more directions than a small dataset has training
rows, and the single-class version (energy left after the best single class), which is the one the
preregistration names. Deferral is ranked at step zero over k-means regions and scored on held-out
points. A permuted-target control gives the same quantities on pure noise.
"""
from __future__ import annotations

import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.rgre import core
from poc.rgre_ml import real as R

S_MAX = 8
DEAD = 0.01
K_REGIONS = 12
DEFER_K = 3
KNN_K = 10


def diagnose(case, s, y=None):
    r = case.residual(s, y)
    signed = case.tangents(s)
    diag = core.diagnose(r, signed, {}, support=())
    sets = {c: [c] for c in signed}
    cls, why, ranked = core.select_projection(diag, 1.01, sets, unrepairable=(), blacklist=[])
    q_single = 1.0 - max(diag["q"].values()) if diag["q"] else 1.0
    return dict(pick=cls, ranked=ranked[:5], q_perp_joint=float(diag["q_perp"]), q_perp=float(q_single),
                q_top=float(max(diag["q"].values())) if diag["q"] else 0.0, n_dirs=int(sum(len(v) for v in signed.values()))), r, signed


def baselines(r, signed, rng):
    rv = r.ravel()
    cand = list(signed)
    return dict(random=str(rng.choice(cand)),
                gradnorm=max(signed, key=lambda c: max(abs(float(rv @ v)) for v in signed[c])))


def pick_anchored(case, s, r):
    """The declared variant: the same rule (largest squared cosine of a single direction) over the
    anchored tangent set. Computed directly, since the coherence table core.diagnose builds is not
    used by the selection rule."""
    rv = r.ravel(); E = float(rv @ rv)
    best, best_c = -1.0, None
    for c, vs in case.tangents(s, anchored=True).items():
        for v in vs:
            n2 = float(v @ v)
            f = float((rv @ v) ** 2 / (n2 * E)) if n2 > 0 and E > 0 else 0.0
            if f > best:
                best, best_c = f, c
    return best_c, best


def value(table, pick, oracle):
    if pick is None:
        return 0.0
    v = table[oracle]["drop"]
    return float(table[pick]["drop"] / v) if v > 1e-12 else (1.0 if table[pick]["drop"] >= v else 0.0)


def defer_rankings(case, r, signed, ranked, cell, ncell):
    """Per-region residual energy at step zero, three ways: its magnitude; what the best single
    class's global projection leaves (RGRE-ML-1b's criterion); and what the joint projection onto
    the top S_MAX ranked classes leaves, the span the growth budget can reach. The pilot showed the
    single-class version reproduces the magnitude ranking on a real dictionary, because no single
    class explains more than a few percent of a real residual; the top-S version is the same
    question sized to the growth budget."""
    rv = r.ravel()
    mag = np.zeros(ncell); og = np.zeros(ncell); ots = np.zeros(ncell)
    rem_by_class = {}
    for c, vs in signed.items():
        Q = core.orth(vs)
        rem_by_class[c] = rv - Q @ (Q.T @ rv) if Q.shape[1] else rv
    top = [c for c in ranked[:S_MAX] if c in signed]
    Qt = core.orth([v for c in top for v in signed[c]]) if top else np.zeros((len(rv), 0))
    rem_top = rv - Qt @ (Qt.T @ rv) if Qt.shape[1] else rv
    for k in range(ncell):
        rows = np.where(cell == k)[0]
        if len(rows) < 8:
            mag[k] = -1.0; og[k] = -1.0; ots[k] = -1.0; continue
        rk = rv[rows]
        mag[k] = float(rk @ rk)
        og[k] = min(float(rem_by_class[c][rows] @ rem_by_class[c][rows]) for c in rem_by_class)
        ots[k] = float(rem_top[rows] @ rem_top[rows])
    return mag, og, ots


def run_case(args):
    name, seed = args
    T0 = time.time()
    case = R.RCase(name, seed)
    rng = np.random.default_rng(seed * 7919 + len(name))
    s = case.student0()
    rec = dict(dataset=name, seed=seed, n_train=int(case.n), n_test=int(len(case.yte)), d=int(case.d),
               n_candidates=len(case.mods), test_err_linear=case.test_error(s), train_err_linear=case.error(s))
    # k-means regions on the training inputs, fixed before any growth
    C = R.kmeans(case.Xtr, K_REGIONS, seed)
    cell_tr, cell_te = R.assign(case.Xtr, C), R.assign(case.Xte, C)
    steps = []
    states = [s]
    defer_rank = None
    for t in range(S_MAX):
        d, r, signed = diagnose(case, s)
        if t == 0:
            # the full ranking of classes by projection, for the top-S span
            full_ranked = []
            for c, _, _ in sorted(core.diagnose(r, signed, {}, support=())["items"], key=lambda x: -x[2]):
                if c not in full_ranked:
                    full_ranked.append(c)
            mag, og, ots = defer_rankings(case, r, signed, full_ranked, cell_tr, K_REGIONS)
            defer_rank = dict(mag=[int(i) for i in np.argsort(-mag)], orth_global=[int(i) for i in np.argsort(-og)],
                              orth_topS=[int(i) for i in np.argsort(-ots)],
                              random=[int(i) for i in np.random.default_rng(seed).permutation(K_REGIONS)])
        e0, table = case.oracle_table(s)
        oracle = max(table, key=lambda c: table[c]["drop"])
        oracle_test = min(table, key=lambda c: table[c]["test"])
        te0 = case.test_error(s)
        bl = baselines(r, signed, rng)
        anc, anc_f = pick_anchored(case, s, r)
        pick = d["pick"]
        new = table[pick]["state"]
        e1, te1 = table[pick]["e1"], table[pick]["test"]
        step = dict(t=t, pick=pick, oracle=oracle, oracle_test=oracle_test, ranked=d["ranked"],
                    q_perp=d["q_perp"], q_perp_joint=d["q_perp_joint"], q_top=d["q_top"], n_dirs=d["n_dirs"],
                    train_err_before=e0, train_err_after=e1, test_err_before=te0, test_err_after=te1,
                    train_drop_rel=(e0 - e1) / e0, test_drop_rel=(te0 - te1) / te0,
                    best_test_drop_rel=(te0 - table[oracle_test]["test"]) / te0,
                    value=value(table, pick, oracle), value_random=value(table, bl["random"], oracle),
                    value_gradnorm=value(table, bl["gradnorm"], oracle),
                    pick_anchored=anc, value_anchored=value(table, anc, oracle), anchored_cos2=anc_f,
                    oracle_in_top3=oracle in d["ranked"][:3],
                    dead=(e0 - e1) < DEAD * e0, cost=int(case.mods[pick].cost))
        steps.append(step)
        s = new
        states.append(s)
    rec["steps"] = steps
    dead_stop = next((st["t"] for st in steps if st["dead"]), S_MAX)
    rec["dead_stop"] = int(dead_stop)
    s_dead, s_final = states[dead_stop], states[S_MAX]
    test_curve = [case.test_error(x) for x in states]
    rec["test_curve"] = test_curve
    rec["test_err_dead_stop"] = test_curve[dead_stop]
    rec["test_err_final"] = test_curve[S_MAX]
    rec["test_err_best_step"] = float(min(test_curve))
    rec["best_step"] = int(np.argmin(test_curve))
    rec["knn_test_err"] = float(np.sqrt(np.mean((case.yte - R.knn_predict(case.Xtr, case.ytr, case.Xte, KNN_K)) ** 2)))
    rec["modules_added"] = [st["pick"] for st in steps]
    # deferral: rankings from step zero, scored on the held-out points outside the deferred regions
    def score(order, st):
        deferred = set(order[:DEFER_K])
        keep = np.array([c not in deferred for c in cell_te])
        res = case.yte - case.predict(st, case.Xte)
        return float(np.sqrt(np.mean(res[keep] ** 2))) if keep.any() else float("nan")
    res_final = case.yte - case.predict(s_dead, case.Xte)
    hind = np.zeros(K_REGIONS)
    for k in range(K_REGIONS):
        hind[k] = float((res_final[cell_te == k] ** 2).sum())
    hind_order = [int(i) for i in np.argsort(-hind)]
    rec["defer"] = {}
    for label, st in (("dead_stop", s_dead), ("final", s_final)):
        rec["defer"][label] = dict(mag=score(defer_rank["mag"], st), orth_global=score(defer_rank["orth_global"], st),
                                   orth_topS=score(defer_rank["orth_topS"], st),
                                   random=score(defer_rank["random"], st), none=case.test_error(st),
                                   hindsight=score(hind_order, st))
    rec["defer_rank"] = defer_rank
    # permuted-target control at step zero: the same quantities on pure noise
    yp = rng.permutation(case.ytr)
    sp = case.student0(yp)
    dp, rp, sgp = diagnose(case, sp, yp)
    e0p, tp = case.oracle_table(sp, yp)
    op = max(tp, key=lambda c: tp[c]["drop"])
    rec["perm"] = dict(q_perp=dp["q_perp"], q_perp_joint=dp["q_perp_joint"], q_top=dp["q_top"],
                       best_train_drop_rel=(e0p - tp[op]["e1"]) / e0p, pick_train_drop_rel=(e0p - tp[dp["pick"]]["e1"]) / e0p,
                       dead=(e0p - tp[dp["pick"]]["e1"]) < DEAD * e0p, pick=dp["pick"], oracle=op)
    rec["seconds"] = time.time() - T0
    return rec


def summarise_line(rec):
    st = rec["steps"]
    vals = [s["value"] for s in st]
    return (f"{rec['dataset']:<11} seed {rec['seed']}  n={rec['n_train']:<5} cand={rec['n_candidates']:<4} "
            f"lin {rec['test_err_linear']:.3f} -> dead@{rec['dead_stop']} {rec['test_err_dead_stop']:.3f} "
            f"final {rec['test_err_final']:.3f} best {rec['test_err_best_step']:.3f}@{rec['best_step']} knn {rec['knn_test_err']:.3f} | "
            f"value med {np.median(vals):.2f} anchored {np.median([s['value_anchored'] for s in st]):.2f} | q_perp step0 {st[0]['q_perp']:.3f} perm {rec['perm']['q_perp']:.3f} "
            f"(joint {st[0]['q_perp_joint']:.2f}/{rec['perm']['q_perp_joint']:.2f}) | "
            f"defer topS {rec['defer']['dead_stop']['orth_topS']:.3f} og {rec['defer']['dead_stop']['orth_global']:.3f} mag {rec['defer']['dead_stop']['mag']:.3f} "
            f"rand {rec['defer']['dead_stop']['random']:.3f} | perm best drop {rec['perm']['best_train_drop_rel']:.3%} "
            f"[{rec['seconds']:.0f}s]")


def main(datasets, seeds, out, workers):
    jobs = [(n, s) for n in datasets for s in seeds]
    recs = []
    T0 = time.time()
    with Pool(workers) as pool:
        for rec in pool.imap_unordered(run_case, jobs):
            recs.append(rec)
            print(summarise_line(rec), flush=True)
            json.dump(dict(datasets=list(datasets), seeds=list(seeds), S_MAX=S_MAX, DEAD=DEAD, K_REGIONS=K_REGIONS,
                           DEFER_K=DEFER_K, cases=recs), open(out, "w"), indent=1)
    print(f"done: {len(recs)} cases in {time.time()-T0:.0f}s -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default=",".join(R.DATASETS))
    ap.add_argument("--seeds", default="1,2,3,4,5")
    ap.add_argument("--out", default="poc/results/rgre_ml2.json")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    main(a.datasets.split(","), [int(x) for x in a.seeds.split(",")], a.out, a.workers)
