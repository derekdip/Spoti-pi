"""F7 frozen scorer: the no-templates hybrid against F4's projection greedy, F4's global floor, the
column grammar's reference, and F6's hybrid, on F4's seven scenes. Committed with the
preregistration, run once."""
from __future__ import annotations
import json, sys
import numpy as np


def main(path, f4_path="poc/results/f4.json", f6_path="poc/results/f6.json", col_path="poc/results/column_reference.json"):
    d = json.load(open(path)); S = {s["scene"]: s for s in d["scenes"]}
    f4 = {s["scene"]: s for s in json.load(open(f4_path))["unseen"]}
    f6 = {s["scene"]: s for s in json.load(open(f6_path))["scenes"]}
    col = json.load(open(col_path))
    names = [n for n in ["ignition", "delayed_ignition", "full", "twin", "shelf_bed", "split", "shutoff"] if n in S]
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# F7 scored: {len(names)} scenes, {d['STEPS']} steps\n")
    V = "hybrid_nt"
    steps = [st for n in names for st in S[n]["variants"][V]["steps"] if st["oracle_drop_rel"] > 0]
    steps2 = [st for n in names for st in S[n]["variants"]["hybrid_nt2"]["steps"] if st["oracle_drop_rel"] > 0]
    f6steps = [st for n in names for st in f6[n]["variants"]["hybrid"]["steps"] if st["oracle_drop_rel"] > 0]
    v = np.array([s["value"] for s in steps]); v2 = np.array([s["value"] for s in steps2]); v6 = np.array([s["value"] for s in f6steps])
    P("## K1 value per step against the oracle table")
    P(f"  hybrid, no templates      median {np.median(v):.3f} mean {v.mean():.3f} ({len(steps)} steps) repairs/step median {np.median([s['evaluated'] for s in steps]):.0f}")
    P(f"  hybrid, no templates, 2   median {np.median(v2):.3f} mean {v2.mean():.3f} ({len(steps2)} steps) repairs/step median {np.median([s['evaluated'] for s in steps2]):.0f}")
    P(f"  F6 hybrid with templates  median {np.median(v6):.3f} mean {v6.mean():.3f} ({len(f6steps)} steps, 8 per scene)")
    small = ("width", "deflect", "profile", "base", "attract", "jitter", "soot", "floor")
    lost = [s for s in steps if s["value"] < 0.9]; lost6 = [s for s in f6steps if s["value"] < 0.9]
    P(f"  steps under 0.9: {len(lost)} of {len(steps)} (oracle small-gap on {sum(s['oracle'] in small for s in lost)}); F6 hybrid: {len(lost6)} of {len(f6steps)} (small-gap {sum(s['oracle'] in small for s in lost6)})")
    k1 = np.median(v) >= 0.90 and v.mean() > v6.mean()
    P(f"-> K1 {'pass' if k1 else 'FAIL'} (bar: median >= 0.90 and mean above F6's hybrid on these scenes)\n")
    P("## K2 terminal error against F4's projection greedy (10 steps, the arc's workflow)")
    P(f"  {'scene':<17} {'v0':>6} {'F4 greedy':>10} {'F7 hybrid':>10} {'F7 hyb2':>8} {'F4 floor':>9} {'column':>7} | glow: F4 floor / F4 look / F7 hybrid | F6 hybrid(8)")
    w2 = 0; l2 = 0; red_h, red_f, red_g = [], [], []; glow_w = 0; below_col = 0
    for n in names:
        e0 = S[n]["e_v0"]; eh = S[n]["variants"][V]["e_final"]; eh2 = S[n]["variants"]["hybrid_nt2"]["e_final"]
        eg = f4[n]["greedy"]["e_final"]; ef = f4[n]["fits"]["standard"]["error"]; ec = col[n]["best_known"]
        gh = S[n]["variants"][V]["terminal"]["decisions"]["visual"]["late_correlation"]
        gf = f4[n]["fits"]["standard"]["decisions"]["visual"]["late_correlation"]; gl = f4[n]["fits"]["look"]["decisions"]["visual"]["late_correlation"]
        e6 = f6[n]["variants"]["hybrid"]["e_in_final"]
        w2 += eh < eg - 1e-9; l2 += eh > eg + 1e-9; glow_w += gh > gf; below_col += eh < ec
        red_h.append((e0 - eh) / e0); red_f.append((e0 - ef) / e0); red_g.append((e0 - eg) / e0)
        P(f"  {n:<17} {e0:6.3f} {eg:10.3f} {eh:10.3f} {eh2:8.3f} {ef:9.3f} {ec:7.3f} | {gf:.2f} / {gl:.2f} / {gh:.2f} | {e6:.3f}")
    k2 = w2 >= 6
    P(f"  hybrid below F4 greedy on {w2} of {len(names)} (above on {l2}); below the column grammar's best known on {below_col}")
    P(f"-> K2 {'pass' if k2 else 'FAIL'} (bar: below F4's greedy on >= 6 of 7)\n")
    P("## K3 terminal reduction against F4's global floor (differential evolution, 22 parameters)")
    ratio = np.median(red_h) / max(np.median(red_f), 1e-9)
    P(f"  median reduction: F4 greedy {np.median(red_g):.3f}, F7 hybrid {np.median(red_h):.3f}, F4 floor {np.median(red_f):.3f}; hybrid / floor {ratio:.3f} (F4 greedy / floor {np.median(red_g)/max(np.median(red_f),1e-9):.3f})")
    k3 = ratio >= 0.95
    P(f"-> K3 {'pass' if k3 else 'FAIL'} (bar: >= 0.95)\n")
    P("## K4 the look: glow correlation at the hybrid terminal against F4's floor state")
    P(f"  hybrid above F4 floor state on {glow_w} of {len(names)}; medians hybrid {np.median([S[n]['variants'][V]['terminal']['decisions']['visual']['late_correlation'] for n in names]):.3f} F4 floor {np.median([f4[n]['fits']['standard']['decisions']['visual']['late_correlation'] for n in names]):.3f} F4 look fit {np.median([f4[n]['fits']['look']['decisions']['visual']['late_correlation'] for n in names]):.3f}")
    k4 = glow_w >= 4
    P(f"-> K4 {'pass' if k4 else 'FAIL'} (bar: above on >= 4 of 7)\n")
    P("## Reported: decisions at the hybrid terminal (heat wrong, ai wrong, ignition missed) against F4's floor")
    for n in names:
        dh = S[n]["variants"][V]["terminal"]["decisions"]; df = f4[n]["fits"]["standard"]["decisions"]
        P(f"  {n:<17} heat {100*dh['heat']['disagree']:.1f}% / {100*df['heat']['disagree']:.1f}%  ai {100*dh['ai']['disagree']:.1f}% / {100*df['ai']['disagree']:.1f}%"
          + (f"  ignition missed {100*dh['ignition']['missed_alight']:.0f}% / {100*df['ignition']['missed_alight']:.0f}%" if "ignition" in dh else "")
          + f"  parcels {S[n]['variants'][V]['terminal']['live']} / {f4[n]['fits']['standard']['live']}")
    letter = "A" if (k2 and k3) else ("B" if k2 else ("C" if k3 else "D"))
    P(f"\n## Outcome (frozen tree): K2 {'pass' if k2 else 'fail'}, K3 {'pass' if k3 else 'fail'} -> {letter}; K1 {'pass' if k1 else 'fail'}, K4 {'pass' if k4 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/f7.json")
