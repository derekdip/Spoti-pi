"""RGRE-ML-2 frozen scorer. Reads the run's JSON, prints the bars as the preregistration states them.

Nothing in here is tuned after the run: it is committed with the preregistration and run once.
"""
from __future__ import annotations
import json, sys
import numpy as np

DEAD = 0.01


def auc(score, label):
    """AUC of `score` for predicting label == True, by rank comparison with ties at one half."""
    s = np.asarray(score, float); y = np.asarray(label, bool)
    pos, neg = s[y], s[~y]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).mean(); eq = (pos[:, None] == neg[None, :]).mean()
    return float(gt + 0.5 * eq)


def main(path):
    d = json.load(open(path))
    cases = d["cases"]
    datasets = sorted(set(c["dataset"] for c in cases))
    out = []
    P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# RGRE-ML-2 scored: {len(cases)} cases, {len(datasets)} datasets, seeds {sorted(set(c['seed'] for c in cases))}\n")

    # ---- B1 selection value, every growth step taken
    steps = [s for c in cases for s in c["steps"]]
    v = np.array([s["value"] for s in steps]); vr = np.array([s["value_random"] for s in steps]); vg = np.array([s["value_gradnorm"] for s in steps])
    b1 = np.median(v) >= 0.90 and np.median(v) > np.median(vr) and np.median(v) > np.median(vg) and v.mean() > vr.mean() and v.mean() > vg.mean()
    P(f"## B1 selection value over {len(steps)} steps")
    va = np.array([s["value_anchored"] for s in steps])
    P(f"median {np.median(v):.3f} mean {v.mean():.3f} | random {np.median(vr):.3f}/{vr.mean():.3f} | gradient-norm {np.median(vg):.3f}/{vg.mean():.3f} | oracle in top-3 {np.mean([s['oracle_in_top3'] for s in steps]):.0%}")
    P(f"declared variant, anchored tangents (reported, not the bar): median {np.median(va):.3f} mean {va.mean():.3f}; pick = oracle {np.mean([s['pick_anchored'] == s['oracle'] for s in steps]):.0%} vs {np.mean([s['pick'] == s['oracle'] for s in steps]):.0%} single-anchor")
    for n in datasets:
        vv = [s["value"] for c in cases if c["dataset"] == n for s in c["steps"]]
        va_n = [s["value_anchored"] for c in cases if c["dataset"] == n for s in c["steps"]]
        P(f"  {n:<11} median {np.median(vv):.2f} mean {np.mean(vv):.2f} | anchored {np.median(va_n):.2f}/{np.mean(va_n):.2f}")
    P(f"-> B1 {'pass' if b1 else 'FAIL'} (bar: median >= 0.90 and above both baselines on median and mean)\n")

    # ---- B2 stopping signal: q_perp before a step vs whether the step was wasted on held-out data
    wasted = np.array([s["test_drop_rel"] < DEAD for s in steps])
    qp = np.array([s["q_perp"] for s in steps]); qj = np.array([s["q_perp_joint"] for s in steps])
    tidx = np.array([s["t"] for s in steps], float); tdrop = np.array([-s["train_drop_rel"] for s in steps])
    a_q, a_t, a_tr, a_j = auc(qp, wasted), auc(tidx, wasted), auc(tdrop, wasted), auc(qj, wasted)
    b2 = a_q >= 0.75 and a_q > a_t
    P(f"## B2 stopping signal: {wasted.sum()} wasted of {len(steps)} steps (held-out gain < 1%)")
    P(f"AUC q_perp (single-class) {a_q:.3f} | step index {a_t:.3f} | in-sample drop of the pick (needs the fit) {a_tr:.3f} | joint q_perp {a_j:.3f}")
    for n in datasets:
        ss = [s for c in cases if c["dataset"] == n for s in c["steps"]]
        w = np.array([s["test_drop_rel"] < DEAD for s in ss])
        P(f"  {n:<11} wasted {w.sum()}/{len(ss)} AUC q_perp {auc([s['q_perp'] for s in ss], w):.2f} step {auc([s['t'] for s in ss], w):.2f}")
    P(f"-> B2 {'pass' if b2 else 'FAIL'} (bar: AUC >= 0.75 and above the step-index baseline)\n")

    # ---- B3 deferral, scored on the student at the in-sample stop
    def defer_block(label):
        ots = np.array([c["defer"][label]["orth_topS"] for c in cases]); og = np.array([c["defer"][label]["orth_global"] for c in cases])
        mg = np.array([c["defer"][label]["mag"] for c in cases]); rn = np.array([c["defer"][label]["random"] for c in cases])
        no = np.array([c["defer"][label]["none"] for c in cases]); hs = np.array([c["defer"][label]["hindsight"] for c in cases])
        wins = (ots < mg).mean(); ties = np.isclose(ots, mg).mean()
        ok = wins >= 0.60 and np.median(ots) < np.median(mg) and np.median(ots) < np.median(rn)
        P(f"[{label}] top-S orthogonal beats magnitude on {wins:.0%} (ties {ties:.0%}) | medians top-S {np.median(ots):.3f} single-class {np.median(og):.3f} magnitude {np.median(mg):.3f} random {np.median(rn):.3f} none {np.median(no):.3f} hindsight {np.median(hs):.3f}")
        P(f"    single-class beats magnitude on {(og < mg).mean():.0%} (ties {np.isclose(og, mg).mean():.0%})")
        return ok
    P("## B3 deferral at step zero, 3 of 12 regions, held-out error outside the deferred regions")
    b3 = defer_block("dead_stop")
    defer_block("final")
    P(f"-> B3 {'pass' if b3 else 'FAIL'} (bar, on the dead-stop student: top-S wins >= 60% with ties against, median below magnitude and random)\n")

    # ---- B4 noise detection: q_perp at step zero, permuted against real targets
    q_real = [c["steps"][0]["q_perp"] for c in cases]; q_perm = [c["perm"]["q_perp"] for c in cases]
    a4 = auc(q_perm + q_real, [True] * len(q_perm) + [False] * len(q_real))
    paired = float(np.mean([p > r for p, r in zip(q_perm, q_real)]))
    b4 = paired >= 0.90
    P(f"## B4 noise detection at step zero: q_perp permuted vs real, {len(cases)} pairs")
    P(f"paired (permuted > real on the same split) {paired:.0%} | pooled AUC {a4:.3f} | median q_perp real {np.median(q_real):.3f} permuted {np.median(q_perm):.3f} | joint version real {np.median([c['steps'][0]['q_perp_joint'] for c in cases]):.3f} permuted {np.median([c['perm']['q_perp_joint'] for c in cases]):.3f}")
    for n in datasets:
        cc = [c for c in cases if c["dataset"] == n]
        P(f"  {n:<11} real {np.median([c['steps'][0]['q_perp'] for c in cc]):.3f} permuted {np.median([c['perm']['q_perp'] for c in cc]):.3f} paired {np.mean([c['perm']['q_perp'] > c['steps'][0]['q_perp'] for c in cc]):.0%}")
    P(f"-> B4 {'pass' if b4 else 'FAIL'} (bar: permuted above real on >= 90% of splits)\n")

    # ---- reported
    P("## Reported")
    dead_perm = np.mean([c["perm"]["dead"] for c in cases])
    P(f"DEAD rule (1% in-sample) on permuted targets: declined {dead_perm:.0%}; spurious best drop median {np.median([c['perm']['best_train_drop_rel'] for c in cases]):.2%} (max {max(c['perm']['best_train_drop_rel'] for c in cases):.2%})")
    P(f"search: one repair fitted per step of {np.median([c['n_candidates'] for c in cases]):.0f} candidates (median) = {1/np.median([c['n_candidates'] for c in cases]):.3f}")
    P("held-out RMSE in target-sd units, median over splits:")
    P(f"  {'dataset':<11} {'linear':>7} {'dead-stop':>9} {'8 steps':>8} {'best step':>9} {'kNN':>6} {'dead@':>6} {'best@':>6}")
    for n in datasets:
        cc = [c for c in cases if c["dataset"] == n]
        P(f"  {n:<11} {np.median([c['test_err_linear'] for c in cc]):7.3f} {np.median([c['test_err_dead_stop'] for c in cc]):9.3f} "
          f"{np.median([c['test_err_final'] for c in cc]):8.3f} {np.median([c['test_err_best_step'] for c in cc]):9.3f} "
          f"{np.median([c['knn_test_err'] for c in cc]):6.3f} {np.median([c['dead_stop'] for c in cc]):6.1f} {np.median([c['best_step'] for c in cc]):6.1f}")
    P(f"grown model (8 steps) beats linear on held-out in {np.mean([c['test_err_final'] < c['test_err_linear'] for c in cases]):.0%} of cases; beats kNN in {np.mean([c['test_err_final'] < c['knn_test_err'] for c in cases]):.0%}")
    kinds = {}
    for c in cases:
        for m in c["modules_added"]:
            kinds[m.split("_")[0]] = kinds.get(m.split("_")[0], 0) + 1
    P(f"modules grown by kind: {dict(sorted(kinds.items(), key=lambda x: -x[1]))}")
    okind = {}
    for s in steps:
        okind[s["oracle"].split("_")[0]] = okind.get(s["oracle"].split("_")[0], 0) + 1
    P(f"oracle's pick by kind: {dict(sorted(okind.items(), key=lambda x: -x[1]))}")
    P(f"held-out value of the pick (pick's test drop / best candidate's test drop) median {np.median([s['test_drop_rel']/s['best_test_drop_rel'] if s['best_test_drop_rel'] > 1e-9 else 0 for s in steps]):.2f}")

    # ---- outcome
    P("\n## Outcome (frozen tree)")
    letter = "D" if not b1 else ("C" if not b2 else ("A" if b3 else "B"))
    P(f"B1 {'pass' if b1 else 'fail'}, B2 {'pass' if b2 else 'fail'}, B3 {'pass' if b3 else 'fail'}, B4 {'pass' if b4 else 'fail'} -> outcome {letter}")
    text = "\n".join(out)
    print(text)
    return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/rgre_ml2.json")
