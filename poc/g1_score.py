"""G1 frozen scorer. Committed with the preregistration, run once."""
from __future__ import annotations
import json, sys
import numpy as np


def main(path):
    d = json.load(open(path)); C = d["cases"]
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G1 scored: {len(C)} cases, {d['STEPS']} steps\n")
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    transfer = [c for c in C if c["group"] == "transfer" and c["designed"]]
    controls = [c for c in C if not c["designed"]]
    def first(c, v="hybrid"):
        st = c["variants"][v]["steps"]; return st[0].get("pick") if st else None
    def within2(c, v="hybrid"):
        return c["designed"] in c["variants"][v]["added"][:2]
    # ---- I1, I2: identity on the design bodies
    P("## I1 first pick = designed class, design bodies (hybrid); I2 designed class added within two steps")
    for c in design:
        P(f"  {c['case']:<20} designed {c['designed']:<8} first {str(first(c)):<8} added {c['variants']['hybrid']['added']} | projection first {str(first(c, 'projection')):<8} oracle first {str(first(c, 'oracle'))}")
    i1 = sum(first(c) == c["designed"] for c in design); i2 = sum(within2(c) for c in design)
    P(f"-> I1 {'pass' if i1 >= 3 else 'FAIL'}: {i1} of {len(design)} (bar >= 3 of 5)")
    P(f"-> I2 {'pass' if i2 >= 4 else 'FAIL'}: {i2} of {len(design)} (bar >= 4 of 5)\n")
    # ---- I3: transfer identity within two steps
    P("## I3 designed class within two steps on the mirrored bodies (hybrid)")
    for c in transfer:
        P(f"  {c['case']:<20} designed {c['designed']:<8} added {c['variants']['hybrid']['added']} | projection {c['variants']['projection']['added']} oracle {c['variants']['oracle']['added']}")
    i3 = sum(within2(c) for c in transfer)
    P(f"-> I3 {'pass' if i3 >= 3 else 'FAIL'}: {i3} of {len(transfer)} (bar >= 3 of 4)\n")
    # ---- I4: value per step
    steps = {v: [s for c in C for s in c["variants"][v]["steps"] if s["oracle_drop_rel"] > 0.0] for v in ("projection", "hybrid", "oracle")}
    P("## I4 value per step against the oracle table, all cases, steps with positive oracle gain")
    for v, ss in steps.items():
        P(f"  {v:<11} median {np.median([s['value'] for s in ss]):.3f} mean {np.mean([s['value'] for s in ss]):.3f} over {len(ss)} steps; repairs/step median {np.median([s['evaluated'] for s in ss]):.0f}")
    i4 = np.median([s["value"] for s in steps["hybrid"]]) >= 0.90
    P(f"-> I4 {'pass' if i4 else 'FAIL'} (bar: hybrid median >= 0.90)\n")
    # ---- I5: floor
    imp = [c for c in C if c["designed"]]
    P("## I5 terminal reduction against the joint floor (differential evolution from V0), impaired cases")
    ratios = []
    for c in imp:
        e0 = c["e_v0"]; eh = c["variants"]["hybrid"]["e_final"]; ef = c["floor"]["e"]
        ratios.append((e0 - eh) / max(e0 - ef, 1e-9))
        P(f"  {c['case']:<20} v0 {e0:.3f} hybrid {eh:.3f} projection {c['variants']['projection']['e_final']:.3f} oracle {c['variants']['oracle']['e_final']:.3f} floor {ef:.3f} | hybrid/floor {ratios[-1]:.2f}")
    i5 = np.median(ratios) >= 0.80
    P(f"-> I5 {'pass' if i5 else 'FAIL'}: median {np.median(ratios):.3f} (bar >= 0.80)\n")
    # ---- I6: consumers
    P("## I6 no consumer worse than V0 at the hybrid terminal, impaired cases")
    ok = 0
    for c in imp:
        worse = [k for k, v in c["variants"]["hybrid"]["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        ok += not worse
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}")
    i6 = ok >= 10
    P(f"-> I6 {'pass' if i6 else 'FAIL'}: {ok} of {len(imp)} (bar >= 10 of 12)\n")
    # ---- reported: controls
    P("## Reported: controls (nothing designed to be missing)")
    for c in controls:
        st = c["variants"]["hybrid"]["steps"][0]
        P(f"  {c['case']:<20} first pick {str(st.get('pick'))} drop {st.get('drop_rel', 0):.3f} dead {st['dead']} | added {c['variants']['hybrid']['added']} | v0 {c['e_v0']:.3f} -> {c['variants']['hybrid']['e_final']:.3f}")
    letter = "A" if (i2 and i4) else ("B" if i2 else ("C" if i4 else "D"))
    P(f"\n## Outcome (frozen tree): I2 {'pass' if i2 >= 4 else 'fail'}, I4 {'pass' if i4 else 'fail'} -> {letter}; I1 {i1}/5, I3 {i3}/4, I5 {'pass' if i5 else 'fail'}, I6 {'pass' if i6 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g1.json")
