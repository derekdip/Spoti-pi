"""G2 frozen scorer. Committed with the preregistration, run once. Identity is a class and, for a
sided class, the sign of its side."""
from __future__ import annotations
import json, sys
import numpy as np


def hit(entry, c):
    """Does an applied repair (class, side) name the designed (class, sign)?"""
    cls, side = entry
    return cls == c["designed"] and (c["designed_sign"] == 0 or side == c["designed_sign"])


def main(path):
    d = json.load(open(path)); C = d["cases"]
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# G2 scored: {len(C)} cases, {d['STEPS']} steps\n")
    design = [c for c in C if c["group"] == "design" and c["designed"]]
    mirrors = [c for c in C if c["group"] == "transfer" and c["designed"] and c["seed"] == 0]
    imp = [c for c in C if c["designed"] or c["morph"].startswith("short_shank")]     # the ten damaged bodies
    controls = [c for c in C if not c["designed"] and not c["morph"].startswith("short_shank")]
    shorts = [c for c in C if c["morph"].startswith("short_shank")]
    BASE = ("rhythm", "legs", "torso", "arms")
    imps = lambda c, v: [e for e in c["variants"][v]["added"] if e[0] not in BASE]     # impairment repairs only
    first = lambda c, v: (imps(c, v)[0] if imps(c, v) else None)
    two = lambda c, v: any(hit(e, c) for e in imps(c, v)[:2])
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    P("## J1 first IMPAIRMENT repair names the damage (class and side), oracle path, design bodies; J2 within the first two impairment repairs (base re-fits do not count)")
    for c in design:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  oracle {fmt(c['variants']['oracle']['added'])} | safe {fmt(c['variants']['oracle_safe']['added'])} | projection {fmt(c['variants']['projection']['added'])}")
    j1 = sum(first(c, "oracle") is not None and hit(first(c, "oracle"), c) for c in design)
    j2 = sum(two(c, "oracle") for c in design)
    P(f"-> J1 {'pass' if j1 >= 3 else 'FAIL'}: {j1} of {len(design)} (bar >= 3 of 4)")
    P(f"-> J2 {'pass' if j2 >= 3 else 'FAIL'}: {j2} of {len(design)} (bar >= 3 of 4)\n")
    P("## J3 within two repairs on the mirrored bodies, oracle path")
    for c in mirrors:
        P(f"  {c['case']:<20} designed {c['designed']}{c['designed_sign']:+d}  oracle {fmt(c['variants']['oracle']['added'])} | safe {fmt(c['variants']['oracle_safe']['added'])}")
    j3 = sum(two(c, "oracle") for c in mirrors)
    P(f"-> J3 {'pass' if j3 >= 2 else 'FAIL'}: {j3} of {len(mirrors)} (bar >= 2 of 3)\n")
    P("## J4 terminal reduction against the local floor (Powell from V0 and from the oracle terminal), impaired cases")
    ratios = []
    for c in imp:
        e0 = c["e_v0"]; eo = c["variants"]["oracle"]["e_final"]; ef = c["floor"]["e"]
        r = (e0 - eo) / max(e0 - ef, 1e-9); ratios.append(min(r, 2.0))
        P(f"  {c['case']:<20} v0 {e0:.3f} oracle {eo:.3f} safe {c['variants']['oracle_safe']['e_final']:.3f} projection {c['variants']['projection']['e_final']:.3f} floor {ef:.3f} (v0 {c['floor']['from_v0']:.3f}, terminal {c['floor']['from_oracle']:.3f}) | {r:.2f}")
    j4 = np.median(ratios) >= 0.80
    P(f"-> J4 {'pass' if j4 else 'FAIL'}: median {np.median(ratios):.3f} (bar >= 0.80, ratios capped at 2)\n")
    P("## J5 no consumer worse than V0 at the oracle terminal, impaired cases")
    ok = 0
    for c in imp:
        worse = [k for k, v in c["variants"]["oracle"]["per_consumer"].items() if v > c["per_consumer_v0"][k] + 1e-9]
        ok += not worse
        P(f"  {c['case']:<20} {'none worse' if not worse else 'worse: ' + ', '.join(worse)}")
    j5 = ok >= 6
    P(f"-> J5 {'pass' if j5 else 'FAIL'}: {ok} of {len(imp)} (bar >= 6 of 10)\n")
    P("## Reported: the short-shank bodies (no designed class), the safe path's identity, and the controls")
    for c in shorts:
        P(f"  {c['case']:<20} oracle added {fmt(c['variants']['oracle']['added'])} ({c['e_v0']:.3f} -> {c['variants']['oracle']['e_final']:.3f}); impairment repairs {fmt(imps(c, 'oracle'))}")
    P(f"  safe path: designed within two on {sum(two(c, 'oracle_safe') for c in design)} of {len(design)} design, {sum(two(c, 'oracle_safe') for c in mirrors)} of {len(mirrors)} mirrors; declined at step zero on {sum(not c['variants']['oracle_safe']['added'] for c in imp)} of {len(imp)} impaired")
    for c in controls:
        P(f"  {c['case']:<20} oracle added {fmt(c['variants']['oracle']['added'])} ({c['e_v0']:.3f} -> {c['variants']['oracle']['e_final']:.3f}); safe {fmt(c['variants']['oracle_safe']['added'])}")
    steps = [s for c in C for s in c["variants"]["projection"]["steps"] if s["oracle_drop_rel"] > 0]
    P(f"  projection value per step: median {np.median([s['value'] for s in steps]):.2f} mean {np.mean([s['value'] for s in steps]):.2f} ({len(steps)} steps)")
    a, b = j2 >= 3, j3 >= 2
    letter = "A" if (a and b) else ("B" if a else ("C" if b else "D"))
    P(f"\n## Outcome (frozen tree): J2 {'pass' if a else 'fail'}, J3 {'pass' if b else 'fail'} -> {letter}; J1 {j1}/{len(design)}, J4 {'pass' if j4 else 'fail'}, J5 {'pass' if j5 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g2.json")
