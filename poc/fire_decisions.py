"""What would the game decide from the cheap fire, and how often would it be wrong?

Relative RMS is the fitting objective; it is not what a game reads. Each consumer feeds a decision:
a hand near a probe burns or does not, a fuel bed is alight or is not, a hazard cell is passable or
is not, and the player sees a glow whose shape either resembles the real one or does not. This
scores the cheap fire at its best-known state on those decisions, against the teacher, and sets
them beside the standard corn shipped with: coarse-field error 0.22, late-field correlation 0.98.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, rgre_fire as R, tokens, teacher as TT

BURN_T = TT.HAZARD_T           # 400 K: the teacher's own hazard threshold, used for a hand as well
SC = ("obstacle", "ignition", "delayed_ignition", "full", "windy", "twin", "shelf_bed")


def decisions(case, st, as_record=tokens.as_record):
    rec = as_record(st, case.p, case.times, case.burners, case.patches, case.obstacles)
    out = {}
    # heat: burn / no burn at each probe, each frame
    t_heat = case.target["heat"]; c_heat = np.asarray(TT.g_heat(rec, case.probes), float).reshape(case.F, -1)
    tb, cb = t_heat > BURN_T, c_heat > BURN_T
    out["heat"] = dict(disagree=float((tb != cb).mean()),
                       missed_burn=float((tb & ~cb).sum() / max(tb.sum(), 1)),
                       false_burn=float((~tb & cb).sum() / max((~tb).sum(), 1)),
                       teacher_burn_rate=float(tb.mean()))
    # ignition: alight / not, per patch per frame
    if case.patches:
        t_ig = case.target["ignition"]; c_ig = np.asarray(TT.g_ignition(rec, case.patches), float).reshape(case.F, -1)
        ta, ca = t_ig > 0.5, c_ig > 0.5
        out["ignition"] = dict(disagree=float((ta != ca).mean()),
                               missed_alight=float((ta & ~ca).sum() / max(ta.sum(), 1)),
                               false_alight=float((~ta & ca).sum() / max((~ta).sum(), 1)),
                               teacher_alight_rate=float(ta.mean()))
    # ai: passable / impassable per cell per frame
    t_ai = case.target["ai"]; c_ai = np.asarray(TT.g_ai(rec), float).reshape(case.F, -1)
    tp, cp = t_ai > 0.5, c_ai > 0.5
    out["ai"] = dict(disagree=float((tp != cp).mean()),
                     missed_hazard=float((tp & ~cp).sum() / max(tp.sum(), 1)),
                     false_hazard=float((~tp & cp).sum() / max((~tp).sum(), 1)),
                     teacher_hazard_rate=float(tp.mean()))
    # visual: no decision; shape resemblance as corn reported it
    t_v = case.target["visual"]; c_v = np.asarray(TT.g_visual(rec), float).reshape(case.F, -1)
    late = slice(case.F // 2, None)
    corr = float(np.corrcoef(t_v[late].ravel(), c_v[late].ravel())[0, 1])
    out["visual"] = dict(rel_rms=float(np.sqrt(((t_v - c_v) ** 2).mean()) / case.scale["visual"]),
                         late_correlation=corr)
    return out


def main():
    floor = json.load(open("poc/results/f6_floor.json"))
    v0 = json.load(open("poc/results/f1_v0.json"))
    res = {}
    for nm in SC:
        case = R.FireCase(nm, getattr(scenes, nm)())
        st = tokens.FireState(**{k: v for k, v in floor[nm]["state"].items()})
        res[nm] = decisions(case, st)
        res[nm]["floor_error"] = floor[nm]["floor"]
        d = res[nm]
        print(f"{nm:<17} heat wrong {100*d['heat']['disagree']:4.1f}%  "
              f"ai wrong {100*d['ai']['disagree']:4.1f}%  "
              + (f"ignition wrong {100*d['ignition']['disagree']:4.1f}%  " if "ignition" in d else "no beds            ")
              + f"glow corr {d['visual']['late_correlation']:.2f}", flush=True)
    json.dump(res, open("poc/results/fire_decisions.json", "w"), indent=1)
    print("\nMEDIANS over the seven scenes, at the best-known fire state")
    def med(path):
        vals = []
        for nm in SC:
            d = res[nm]
            for k in path[:-1]:
                d = d.get(k, {})
            if path[-1] in d: vals.append(d[path[-1]])
        return float(np.median(vals)) if vals else float("nan")
    print(f"  heat     : decision wrong {100*med(('heat','disagree')):.1f}%   missed burns {100*med(('heat','missed_burn')):.1f}%   false burns {100*med(('heat','false_burn')):.1f}%   (teacher burns {100*med(('heat','teacher_burn_rate')):.0f}% of probe-frames)")
    print(f"  ignition : decision wrong {100*med(('ignition','disagree')):.1f}%   missed {100*med(('ignition','missed_alight')):.1f}%   false {100*med(('ignition','false_alight')):.1f}%")
    print(f"  ai grid  : decision wrong {100*med(('ai','disagree')):.1f}%   missed hazards {100*med(('ai','missed_hazard')):.1f}%   false hazards {100*med(('ai','false_hazard')):.1f}%   (teacher hazard {100*med(('ai','teacher_hazard_rate')):.0f}% of cells)")
    print(f"  visual   : rel rms {med(('visual','rel_rms')):.3f}   late correlation {med(('visual','late_correlation')):.2f}")
    print("\n  corn shipped with: coarse-field error 0.22, late-field correlation 0.98, trail overlap 0.95")


if __name__ == "__main__":
    main()
