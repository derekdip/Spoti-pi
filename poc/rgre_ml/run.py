"""RGRE as a model-growing and deferral procedure: the loop, the oracle, the baselines, the deferral test.

Selection and diagnosis are `poc/rgre/core.py`, unchanged: the code that ran on corn, water and
fire. Only the representation is new. TAU is RGRE-1's calibrated abstention threshold, carried
over verbatim into a fourth domain, as it was into fire.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.rgre import core
from poc.rgre_ml import cases as C
from poc.rgre_ml.dictionary import MODULES, CLASSES

TAU = 0.5834212065969504
DEAD = 0.01
REPAIR_SETS = {c: [c] for c in CLASSES}
DEFER_GRID = 4
DEFER_K = 4


def candidates(s):
    """Model growing asks which module to ADD. Refitting a module the student already has at the
    teacher's values can only absorb residual by miscalibrating it, and the pilot's oracle did
    exactly that on a third of the cases; those are compensation, not identification."""
    return [c for c in CLASSES if c not in s.active()]


def rgre_pick(case, s, blacklist=(), tau=TAU, value_only=False):
    r = case.residual(s)
    signed = C.tangents(case, s)
    signed = {c: v for c, v in signed.items() if c in candidates(s)}
    if value_only:
        a, b = case.blocks()[0]["value"]
        r = r[:, a:b]
        signed = {c: [v[a:b] for v in vs] for c, vs in signed.items()}
    diag = core.diagnose(r, signed, {}, support=())
    sets = {c: [c] for c in candidates(s)}
    cls, why, ranked = core.select_projection(diag, tau, sets, unrepairable=(), blacklist=list(blacklist))
    return cls, why, ranked, diag, signed, r


def oracle_table(case, s):
    """Fit every class once: the exhaustive search RGRE is measured against."""
    e0 = case.error(s)
    out = {}
    for c in candidates(s):
        new, e1 = C.fit_module(case, s, c)
        dc = MODULES[c].cost
        out[c] = dict(state=new, e1=e1, drop=e0 - e1, value=(e0 - e1) / dc, dc=dc)
    return e0, out


def baselines(case, s, r, signed, rng):
    """Pickers an ML practitioner would reach for, all given the same tangents RGRE gets."""
    rv = r.ravel(); E = float(rv @ rv)
    blocks, _ = case.blocks()
    a, b = blocks["value"]
    picks = {}
    cand = list(signed)
    picks["random"] = str(rng.choice(cand))
    picks["cheapest"] = min(cand, key=lambda c: (MODULES[c].cost, c))
    # gradient norm: |r . v| unnormalised, max over a class's directions; large-tangent classes win
    picks["gradnorm"] = max(signed, key=lambda c: max(abs(float(rv @ v)) for v in signed[c]))
    # matching pursuit on the prediction alone: cos^2 in the value consumer, ignoring the decisions
    def mp(c):
        best = 0.0
        for v in signed[c]:
            vv = v[a:b]; rr = rv[a:b]
            n2 = float(vv @ vv) * float(rr @ rr)
            best = max(best, float(rv[a:b] @ vv) ** 2 / n2 if n2 > 0 else 0.0)
        return best
    picks["mp_value"] = max(signed, key=mp)
    return picks


def value_captured(table, pick, oracle, key="drop"):
    """Share of the oracle's gain the pick achieves. `drop` is raw error reduction, the question
    'which module is missing'; `value` divides by parameter count, RGRE-1's definition, reported too."""
    if pick is None:
        return 0.0
    v_or = table[oracle][key]
    return float(table[pick][key] / v_or) if v_or > 1e-12 else (1.0 if table[pick][key] >= v_or else 0.0)


def defer_test(case, s_before, s_after, signed, r_before):
    """Per-region deferral: defer the cells whose residual no single class can explain, versus the
    cells where the residual is merely large. Scored by what is left un-handled after one growth step.

    A cell's orthogonal fraction uses each class's subspace restricted to the cell's own rows, and
    takes the best single class, mirroring select_projection: 'no one class explains this cell'.
    """
    X = case.X
    blocks, _ = case.blocks()
    a, b = blocks["value"]
    rv = r_before.ravel()[a:b]
    ix = np.clip(((X[:, 0] + 1) / 2 * DEFER_GRID).astype(int), 0, DEFER_GRID - 1)
    iy = np.clip(((X[:, 1] + 1) / 2 * DEFER_GRID).astype(int), 0, DEFER_GRID - 1)
    cell = iy * DEFER_GRID + ix
    ncell = DEFER_GRID * DEFER_GRID
    mag = np.zeros(ncell); orth = np.zeros(ncell); orth_g = np.zeros(ncell)
    # global: project the whole value residual onto each class's subspace once; a cell's unexplained
    # energy is what the best single GLOBAL fit leaves in it. Local subspaces on 32 samples explain
    # anything, which the pilot showed; this is the well-posed version of the same question.
    rem_by_class = {}
    for c, vs in signed.items():
        Q = core.orth([v[a:b] for v in vs])
        rem_by_class[c] = rv - (Q @ (Q.T @ rv)) if Q.shape[1] else rv
    for k in range(ncell):
        rows = np.where(cell == k)[0]
        if len(rows) < 4:
            mag[k] = 0; orth[k] = 0; continue
        rk = rv[rows]; Ek = float(rk @ rk)
        mag[k] = Ek
        best = 0.0
        for c, vs in signed.items():
            Q = core.orth([v[a:b][rows] for v in vs])
            if Q.shape[1] == 0: continue
            p = Q @ (Q.T @ rk)
            best = max(best, float(p @ p) / Ek if Ek > 0 else 0.0)
        orth[k] = Ek * (1.0 - best)          # unexplainable energy in this cell, local subspaces
        orth_g[k] = min(float(rem_by_class[c][rows] @ rem_by_class[c][rows]) for c in rem_by_class) if rem_by_class else Ek
    # the residual that remains after the growth step, per sample, in the value consumer
    t, sc = case.targets()
    rem = (t["value"] - s_after.predict(X)) / sc["value"]
    def score(order):
        deferred = set(order[:DEFER_K])
        keep = np.array([cell[i] not in deferred for i in range(len(X))])
        return float(np.sqrt((rem[keep] ** 2).mean())) if keep.any() else 0.0
    by_mag = list(np.argsort(-mag)); by_orth = list(np.argsort(-orth)); by_og = list(np.argsort(-orth_g))
    rng = np.random.default_rng(len(X))
    by_rand = list(rng.permutation(ncell))
    return dict(mag=score(by_mag), orth=score(by_orth), orth_global=score(by_og), random=score(by_rand),
                none=float(np.sqrt((rem ** 2).mean())))


def run_case(case, rng, log):
    s0 = case.student0
    rec = dict(name=case.name, kind=case.kind, missing=list(case.missing), oov=case.oov, e0=case.error(s0))
    cls, why, ranked, diag, signed, r = rgre_pick(case, s0)
    cls_ng, _, _, _, _, _ = rgre_pick(case, s0, tau=1.01)                     # abstention off
    cls_v, _, _, diag_v, _, _ = rgre_pick(case, s0, tau=1.01, value_only=True)  # field residual only
    e0, table = oracle_table(case, s0)
    oracle = max(table, key=lambda c: table[c]["drop"])
    oracle_cost = max(table, key=lambda c: table[c]["value"])
    rec.update(q_perp=diag["q_perp"], q_perp_value=diag_v["q_perp"], rgre=cls, reason=why, ranked=ranked[:4],
               oracle=oracle, oracle_cost=oracle_cost, oracle_drop=table[oracle]["drop"], abstained=cls is None)
    picks = baselines(case, s0, r, signed, rng)
    picks["rgre"] = cls
    picks["rgre_nogate"] = cls_ng
    picks["rgre_value"] = cls_v
    picks["oracle"] = oracle
    # a pick whose fitted gain is under DEAD of the error is declined: the grower does nothing
    def declined(p):
        return p is not None and table[p]["drop"] < DEAD * e0
    rec["declined"] = declined(cls)
    rec["value"] = {k: value_captured(table, p, oracle) for k, p in picks.items()}
    rec["value_per_cost"] = {k: value_captured(table, p, oracle_cost, "value") for k, p in picks.items()}
    rec["picks"] = picks
    rec["repairs_evaluated"] = 0 if cls is None else 1
    if case.kind == "isolated":
        rec["identity"] = (cls == case.missing[0])
        rec["identity_nogate"] = (cls_ng == case.missing[0])
        rec["identity_value"] = (cls_v == case.missing[0])
        rec["identity_mp"] = (picks["mp_value"] == case.missing[0])
        rec["oracle_identity"] = (oracle == case.missing[0])
    # the state after RGRE's single growth step (or unchanged if it abstained or declined)
    s1 = table[cls]["state"] if (cls is not None and not rec["declined"]) else s0
    rec["e_after"] = case.error(s1)
    rec["defer"] = defer_test(case, s0, s1, signed, r)
    # two-step sequencing on the mixture cases, with each residual space; abstention off so the
    # sequencing is tested on its own, the way F3 tested the search without a stopping rule
    if case.kind == "two":
        best2 = None
        for order in ((case.missing[0], case.missing[1]), (case.missing[1], case.missing[0])):
            st = s0
            for c in order:
                st, _ = C.fit_module(case, st, c)
            e2 = case.error(st)
            best2 = e2 if best2 is None else min(best2, e2)
        rec["two"] = {}
        for lab, vo in (("consumer", False), ("field", True)):
            black = []
            s, e = s0, e0
            steps = []
            for step in range(3):                 # a spent pick costs a step; three tries for two modules
                if len([x for x in steps if "e_after" in x]) == 2:
                    break
                c2, why2, _, d2, _, _ = rgre_pick(case, s, black, tau=1.01, value_only=vo)
                if c2 is None:
                    steps.append(dict(pick=None, why=why2)); break
                new, e1 = C.fit_module(case, s, c2)
                if e - e1 < DEAD * e:
                    black.append(c2); steps.append(dict(pick=c2, spent=True)); continue
                steps.append(dict(pick=c2, e_before=e, e_after=e1, q_perp=d2["q_perp"]))
                s, e = new, e1
            found = sum(1 for x in steps if x.get("pick") in case.missing and "e_after" in x)
            rec["two"][lab] = dict(steps=steps, e_final=e, e_oracle2=best2, found=found,
                                   recovery=float((e0 - e) / max(e0 - best2, 1e-9)))
    log(f"{case.name:<22} E0 {rec['e0']:.3f}  q_perp {rec['q_perp']:.2f}  rgre {str(cls):<8} oracle {oracle:<8} "
        f"value {rec['value']['rgre']:.2f}" + (f"  identity {'Y' if rec.get('identity') else 'n'}" if case.kind == "isolated" else "")
        + (f"  2-step field {rec['two']['field']['recovery']:.2f} consumer {rec['two']['consumer']['recovery']:.2f}" if case.kind == "two" else "")
        + f"  defer og {rec['defer']['orth_global']:.3f} mag {rec['defer']['mag']:.3f}" + ("  DECLINED" if rec["declined"] else ""))
    return rec


def summarise(recs):
    def med(xs): return float(np.median(xs)) if xs else float("nan")
    known = [r for r in recs if r["kind"] in ("isolated", "two")]
    iso = [r for r in recs if r["kind"] == "isolated"]
    two = [r for r in recs if r["kind"] == "two"]
    oov = [r for r in recs if r["kind"] == "oov"]
    ctrl = [r for r in recs if r["kind"] == "control"]
    out = {}
    out["value_rgre"] = med([r["value"]["rgre"] for r in known])
    out["value_mean_rgre"] = float(np.mean([r["value"]["rgre"] for r in known])) if known else float("nan")
    for b in ("random", "cheapest", "gradnorm", "mp_value", "rgre_nogate", "rgre_value"):
        out[f"value_{b}"] = med([r["value"][b] for r in known])
    out["value_rgre_notabstained"] = med([r["value"]["rgre"] for r in known if not r["abstained"]])
    out["identity_nogate"] = float(np.mean([r["identity_nogate"] for r in iso])) if iso else float("nan")
    out["identity_value"] = float(np.mean([r["identity_value"] for r in iso])) if iso else float("nan")
    out["identity_mp"] = float(np.mean([r["identity_mp"] for r in iso])) if iso else float("nan")
    out["ctrl_declined_or_abstained"] = float(np.mean([r["abstained"] or r["declined"] for r in ctrl])) if ctrl else float("nan")
    # how separable are OOV and known by q_perp at all, whatever the threshold
    qk = [r["q_perp"] for r in known]; qo = [r["q_perp"] for r in oov]
    if qk and qo:
        out["q_perp_auc"] = float(np.mean([[o > k for k in qk] for o in qo]))
        qkv = [r["q_perp_value"] for r in known]; qov = [r["q_perp_value"] for r in oov]
        out["q_perp_value_auc"] = float(np.mean([[o > k for k in qkv] for o in qov]))
    out["search_fraction"] = med([r["repairs_evaluated"] / len(CLASSES) for r in known])
    out["identity"] = float(np.mean([r["identity"] for r in iso])) if iso else float("nan")
    out["oracle_identity"] = float(np.mean([r["oracle_identity"] for r in iso])) if iso else float("nan")
    out["two_step_recovery_consumer"] = med([r["two"]["consumer"]["recovery"] for r in two])
    out["two_step_recovery_field"] = med([r["two"]["field"]["recovery"] for r in two])
    out["two_step_found_field"] = float(np.mean([r["two"]["field"]["found"] for r in two])) if two else float("nan")
    out["oov_abstain"] = float(np.mean([r["abstained"] for r in oov])) if oov else float("nan")
    out["known_false_abstain"] = float(np.mean([r["abstained"] for r in known])) if known else float("nan")
    out["ctrl_abstain"] = float(np.mean([r["abstained"] for r in ctrl])) if ctrl else float("nan")
    out["q_perp_known"] = med([r["q_perp"] for r in known]); out["q_perp_oov"] = med([r["q_perp"] for r in oov])
    for grp, name in ((oov, "oov"), (iso, "iso")):
        if grp:
            out[f"defer_{name}_orth"] = med([r["defer"]["orth"] for r in grp])
            out[f"defer_{name}_mag"] = med([r["defer"]["mag"] for r in grp])
            out[f"defer_{name}_random"] = med([r["defer"]["random"] for r in grp])
            out[f"defer_{name}_orth_global"] = med([r["defer"]["orth_global"] for r in grp])
            out[f"defer_{name}_orth_wins"] = float(np.mean([r["defer"]["orth"] < r["defer"]["mag"] for r in grp]))
            out[f"defer_{name}_orthg_wins"] = float(np.mean([r["defer"]["orth_global"] < r["defer"]["mag"] for r in grp]))
    return out


def main(seed, out_path, pilot=False, n=(18, 8, 8, 4)):
    T0 = time.time()
    def log(m): print(f"[{time.time()-T0:5.1f}s] {m}", flush=True)
    rng = np.random.default_rng(seed + 7)
    cs = C.build_cases(seed, *n, log=log)
    recs = [run_case(c, rng, log) for c in cs]
    summ = summarise(recs)
    print("\nsummary:")
    for k, v in summ.items():
        print(f"  {k:<24} {v:.3f}")
    json.dump(dict(seed=seed, pilot=pilot, tau=TAU, cases=recs, summary=summ), open(out_path, "w"), indent=1)
    log(f"wrote {out_path}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="poc/results/rgre_ml_pilot.json")
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    main(a.seed, a.out, a.pilot)
