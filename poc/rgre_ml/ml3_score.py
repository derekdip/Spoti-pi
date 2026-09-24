"""RGRE-ML-3 frozen scorer: the null-calibrated stopping rule against the one percent rule, never
stopping, and not growing, by held-out error at the chosen stop; plus the linearisation gap, reported.
Committed with the preregistration, run once."""
from __future__ import annotations
import json, sys
import numpy as np
from scipy.stats import spearmanr

S_MAX = 8


def stops(rec, M):
    st = rec["steps"]
    return next((s["t"] for s in st if s["q_top"] <= max(s["q_null"][:M])), S_MAX)


def main(path, ml2_path="poc/results/rgre_ml2.json"):
    d = json.load(open(path)); cases = d["cases"]
    datasets = sorted(set(c["dataset"] for c in cases))
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# RGRE-ML-3 scored: {len(cases)} cases, seeds {sorted(set(c['seed'] for c in cases))}, M_PERM {d['M_PERM']}\n")
    # path reproduction against the frozen ML-2 run
    try:
        ml2 = {(c["dataset"], c["seed"]): c for c in json.load(open(ml2_path))["cases"]}
        same = [c["modules_added"] == ml2[(c["dataset"], c["seed"])]["modules_added"] for c in cases]
        P(f"growth path identical to RGRE-ML-2 on {sum(same)} of {len(same)} cases\n")
    except Exception as e:
        P(f"(could not compare with RGRE-ML-2: {e})\n")
    tc = {(c["dataset"], c["seed"]): np.array(c["test_curve"]) for c in cases}
    rules = {}
    for M in (9, 19, 49):
        rules[f"null M={M}"] = {k: stops(c, M) for c in cases for k in [(c["dataset"], c["seed"])]}
    rules["one percent"] = {(c["dataset"], c["seed"]): next((s["t"] for s in c["steps"] if s["dead"]), S_MAX) for c in cases}
    rules["never stop"] = {k: S_MAX for k in tc}
    rules["no growth"] = {k: 0 for k in tc}
    rules["hindsight"] = {k: int(np.argmin(v)) for k, v in tc.items()}
    err = {r: {k: float(tc[k][T]) for k, T in Ts.items()} for r, Ts in rules.items()}
    regret = {r: {k: err[r][k] - float(tc[k].min()) for k in tc} for r in rules}
    P("## Held-out error at the chosen stop, 30 cases")
    P(f"{'rule':<13} {'mean regret':>11} {'median':>8} {'mean err':>9} {'stop=best':>9}  stop step median by dataset")
    for r in rules:
        rg = np.array(list(regret[r].values()))
        by = " ".join(f"{n[:4]} {np.median([rules[r][k] for k in tc if k[0] == n]):.0f}" for n in datasets)
        P(f"{r:<13} {rg.mean():11.4f} {np.median(rg):8.4f} {np.mean(list(err[r].values())):9.4f} {np.mean([rules[r][k] == rules['hindsight'][k] for k in tc]):9.0%}  {by}")
    a, b = "null M=19", "one percent"
    wins = sum(err[a][k] < err[b][k] - 1e-12 for k in tc); losses = sum(err[a][k] > err[b][k] + 1e-12 for k in tc)
    c1 = wins > losses and np.mean(list(regret[a].values())) < np.mean(list(regret[b].values()))
    P(f"\n## C1 null M=19 against the one percent rule: wins {wins} losses {losses} ties {len(tc)-wins-losses}; mean regret {np.mean(list(regret[a].values())):.4f} vs {np.mean(list(regret[b].values())):.4f}")
    P(f"-> C1 {'pass' if c1 else 'FAIL'} (bar: more wins than losses and lower mean regret)")
    c2 = np.mean(list(regret[a].values())) < np.mean(list(regret["never stop"].values())) and np.mean(list(regret[a].values())) < np.mean(list(regret["no growth"].values()))
    P(f"## C2 null M=19 against never stopping ({np.mean(list(regret['never stop'].values())):.4f}) and not growing ({np.mean(list(regret['no growth'].values())):.4f}): mean regret {np.mean(list(regret[a].values())):.4f}")
    P(f"-> C2 {'pass' if c2 else 'FAIL'} (bar: lower mean regret than both)\n")
    for n in datasets:
        ks = [k for k in tc if k[0] == n]
        P(f"  {n:<11} regret null19 {np.mean([regret[a][k] for k in ks]):.4f} one% {np.mean([regret[b][k] for k in ks]):.4f} never {np.mean([regret['never stop'][k] for k in ks]):.4f} none {np.mean([regret['no growth'][k] for k in ks]):.4f} | wins/losses vs one% {sum(err[a][k] < err[b][k]-1e-12 for k in ks)}/{sum(err[a][k] > err[b][k]+1e-12 for k in ks)}")
    # the rule on pure noise
    for M in (9, 19, 49):
        dec = np.mean([c["perm"]["q_top"] <= max(c["perm"]["q_null"][:M]) for c in cases])
        P(f"permuted targets, step zero: null M={M} declines {dec:.0%} (expected about {M/(M+1):.0%})")
    P(f"real targets, step zero: null M=19 declines {np.mean([c['steps'][0]['q_top'] <= max(c['steps'][0]['q_null'][:19]) for c in cases]):.0%}")
    # ---- linearisation gap, reported
    steps = [s for c in cases for s in c["steps"]]
    P("\n## Linearisation gap (post-hoc, no bar)")
    kinds = {}
    for s in steps:
        for k, v in s["gap_by_kind"].items():
            kinds.setdefault(k, []).append(v)
    P("median gap of the fitted contribution outside the tangent span, by module kind: " +
      ", ".join(f"{k} {np.median(v):.2f}" for k, v in sorted(kinds.items(), key=lambda kv: np.median(kv[1]))))
    go = np.array([s["gap_oracle"] for s in steps]); gp = np.array([s["gap_pick"] for s in steps]); v = np.array([s["value"] for s in steps])
    ga = np.array([s["gap_anch_oracle"] for s in steps])
    rho = spearmanr(go, v)
    P(f"gap of the oracle's module vs value captured, {len(steps)} steps: Spearman {rho.statistic:.3f} (p {rho.pvalue:.1e}); gap of the pick's module median {np.median(gp):.2f}; oracle's {np.median(go):.2f}; anchored span {np.median(ga):.2f}")
    lo = v[go < 0.25]; hi = v[go >= 0.25]
    P(f"value when the oracle's gap < 0.25: median {np.median(lo) if len(lo) else float('nan'):.2f} (n={len(lo)}); when >= 0.25: {np.median(hi) if len(hi) else float('nan'):.2f} (n={len(hi)})")
    for n in datasets:
        ss = [s for c in cases if c["dataset"] == n for s in c["steps"]]
        P(f"  {n:<11} oracle gap median {np.median([s['gap_oracle'] for s in ss]):.2f} value {np.median([s['value'] for s in ss]):.2f}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/rgre_ml3.json")
