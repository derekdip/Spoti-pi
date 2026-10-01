"""Does 'diagnose on the field, score on the consumers' hold in fire, or only where a consumer is binary?

RGRE-ML-1 found that diagnosing on the consumer-space residual halved the identification rate
against diagnosing on the raw field, with the binary decision consumer the suspected cause. Every
fire experiment diagnosed on the consumer residual. This re-runs the step-0 diagnosis on nine
fire scenes three ways and compares each pick with the oracle that fits every class:

  consumer+templates  the residual every fire run used, with the support templates F1 declared
  consumer            the same residual, no templates (what RGRE-ML-1 ran)
  field               the coarse excess-temperature field, no thresholds, no emission, no soot

Scored by the oracle's raw error reduction, and by the mechanism each scene was built around
where there is one. No bar and nothing frozen: this is a check on a claim made yesterday.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP, teacher as TT
from poc.rgre.core import diagnose, select_projection

SC = ["windy", "obstacle", "twin", "split", "shutoff", "ignition", "delayed_ignition", "full", "shelf_bed"]
MECH = {"windy": "wind", "obstacle": "deflect", "twin": "attract", "split": "deflect", "shutoff": None,
        "ignition": "bed", "delayed_ignition": "bed", "full": "bed", "shelf_bed": "bed"}
NO_GATE = 1.01


class FieldDiag:
    """Diagnosis on the raw field. Scoring stays on the consumers, so the oracle is unchanged."""
    def __init__(self, case):
        self.case = case
        keep = np.arange(0, 241, 4)
        rec = TT.run(case.p, case.burners, case.patches, case.obstacles)
        self.T = TT.coarsen(rec.T[keep] - TT.T_AMBIENT, 4).reshape(case.F, -1)
        self.scale = float(np.sqrt((self.T ** 2).mean())) or 1.0

    def residual(self, st):
        rec = puffs.as_record(st, self.case.p, self.case.times, self.case.burners, self.case.patches, self.case.obstacles)
        c = TT.coarsen(rec.T - TT.T_AMBIENT, 4).reshape(self.case.F, -1)
        return (self.T - c) / (self.scale * np.sqrt(self.T.shape[1]))

    def tangents(self, st):
        return RP.PuffCase.tangents(self, st)   # same finite-difference code, this residual


def pick(diag_r, signed, templates, support):
    d = diagnose(diag_r, signed, templates, support=support)
    c, why, ranked = select_projection(d, NO_GATE, {k: [k] for k in RP.CLASSES}, unrepairable=(), blacklist=[])
    return c, d["q_perp"], ranked[:3]


def main():
    T0 = time.time()
    out = []
    print(f"{'scene':<17} {'oracle':<8} {'mech':<8} | {'cons+tmpl':<10} {'consumer':<10} {'field':<10} | value cons+t / cons / field")
    for nm in SC:
        case = RP.PuffCase(nm, getattr(scenes, nm)())
        fd = FieldDiag(case)
        v0 = puffs.PuffState()
        e0 = case.error(v0)
        # oracle: every class fitted once, best raw drop
        table = {}
        for c in RP.CLASSES:
            if c == "bed" and not case.patches: continue
            if c == "deflect" and not case.obstacles: continue
            if c == "attract" and len(case.burners) < 2: continue
            g = RP.repair_gain(case, v0, c)
            table[c] = g["drop"]
        oracle = max(table, key=table.get)
        signed_c = case.tangents(v0)
        r_c = case.residual(v0)
        p1, q1, rk1 = pick(r_c, signed_c, case.templates(), RP.SUPPORT_CLASSES)
        p2, q2, rk2 = pick(r_c, signed_c, {}, ())
        signed_f = fd.tangents(v0)
        r_f = fd.residual(v0)
        p3, q3, rk3 = pick(r_f, signed_f, {}, ())
        def val(p):
            return table.get(p, 0.0) / max(table[oracle], 1e-9)
        row = dict(scene=nm, oracle=oracle, mech=MECH[nm], e0=e0, table=table,
                   picks=dict(cons_tmpl=p1, consumer=p2, field=p3),
                   q_perp=dict(cons_tmpl=q1, consumer=q2, field=q3),
                   ranked=dict(cons_tmpl=rk1, consumer=rk2, field=rk3),
                   value=dict(cons_tmpl=val(p1), consumer=val(p2), field=val(p3)))
        out.append(row)
        print(f"{nm:<17} {oracle:<8} {str(MECH[nm]):<8} | {str(p1):<10} {str(p2):<10} {str(p3):<10} | "
              f"{val(p1):.2f} / {val(p2):.2f} / {val(p3):.2f}   [{time.time()-T0:.0f}s]", flush=True)
        json.dump(out, open("poc/results/fire_diag_space.json", "w"), indent=1)
    print("\nsummary over 9 scenes:")
    for k in ("cons_tmpl", "consumer", "field"):
        vals = [r["value"][k] for r in out]
        ident = np.mean([r["picks"][k] == r["oracle"] for r in out])
        mech = [r["picks"][k] == r["mech"] for r in out if r["mech"]]
        top3 = np.mean([r["oracle"] in r["ranked"][k] for r in out])
        print(f"  {k:<10} value median {np.median(vals):.2f} mean {np.mean(vals):.2f} | pick = oracle {ident:.0%} | "
              f"oracle in top-3 {top3:.0%} | pick = scene's mechanism {np.mean(mech):.0%} of {len(mech)}")


if __name__ == "__main__":
    main()
