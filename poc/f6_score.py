"""F6 frozen scorer. Committed with the preregistration, run once."""
from __future__ import annotations
import json, sys
import numpy as np

S_MAX = 8; DEAD = 0.01; M = 19


def main(path):
    d = json.load(open(path)); scenes = d["scenes"]
    design = [s for s in scenes if s["group"] == "design"]; transfer = [s for s in scenes if s["group"] == "transfer"]
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    P(f"# F6 scored: {len(design)} design scenes, {len(transfer)} transfer scenes\n")
    all_sc = design + transfer
    # ---- G1 value per step, steps with positive oracle gain
    def steps_of(v, group):
        return [st for s in group for st in s["variants"][v]["steps"] if st["oracle_drop_rel"] > 0]
    P("## G1 value captured per step (oracle gain > 0), median / mean, and repairs needed per step")
    vals = {}
    for v in ("projection", "hybrid", "oracle"):
        ss = steps_of(v, all_sc); vv = np.array([st["value"] for st in ss]); vals[v] = vv
        P(f"  {v:<11} median {np.median(vv):.3f} mean {vv.mean():.3f} over {len(ss)} steps | repairs/step median {np.median([st['evaluated'] for st in ss]):.0f} of {np.median([len(s['candidates']) for s in all_sc]):.0f}")
    for grp, name in ((design, "design"), (transfer, "transfer")):
        P(f"  [{name}] projection {np.median([st['value'] for st in steps_of('projection', grp)]):.2f} hybrid {np.median([st['value'] for st in steps_of('hybrid', grp)]):.2f}")
    g1 = np.median(vals["hybrid"]) >= 0.90 and np.median(vals["hybrid"]) > np.median(vals["projection"])
    P(f"-> G1 {'pass' if g1 else 'FAIL'} (bar: hybrid median >= 0.90 and above projection)\n")
    # ---- G2 terminal reduction
    P("## G2 terminal in-sample reduction after 8 steps, (e_v0 - e_8)/e_v0")
    red = {v: np.array([(s["e_v0"] - s["variants"][v]["e_in_final"]) / s["e_v0"] for s in all_sc]) for v in ("projection", "hybrid", "oracle")}
    for v in red: P(f"  {v:<11} median {np.median(red[v]):.3f} mean {red[v].mean():.3f}")
    wins = int((red["hybrid"] > red["projection"] + 1e-9).sum()); losses = int((red["hybrid"] < red["projection"] - 1e-9).sum())
    g2 = np.median(red["hybrid"]) >= np.median(red["projection"]) and np.median(red["hybrid"]) >= 0.95 * np.median(red["oracle"])
    P(f"  hybrid vs projection: wins {wins} losses {losses} ties {len(all_sc)-wins-losses}; hybrid / oracle median {np.median(red['hybrid'])/max(np.median(red['oracle']),1e-9):.3f}")
    for s in all_sc:
        P(f"    {s['scene']:<17} v0 {s['e_v0']:.3f} -> proj {s['variants']['projection']['e_in_final']:.3f} hyb {s['variants']['hybrid']['e_in_final']:.3f} orc {s['variants']['oracle']['e_in_final']:.3f} | held-out {s['variants']['projection']['e_ho_final']:.3f}/{s['variants']['hybrid']['e_ho_final']:.3f}/{s['variants']['oracle']['e_ho_final']:.3f} floor {s['noise_floor']:.3f}")
    P(f"-> G2 {'pass' if g2 else 'FAIL'} (bar: hybrid median >= projection median and >= 0.95 x oracle median)\n")
    # ---- G3 the dictionary check transfers: step-zero gaps on the transfer scenes fall on the same side of 0.25
    P("## G3 dictionary check on the transfer scenes: step-zero gap on the same side of 0.25 as the design classification")
    large = set(d["LARGE_GAP"]); small = set(d["SMALL_GAP"])
    agree, total, rows = 0, 0, []
    for s in transfer:
        g0 = s["variants"]["projection"]["steps"][0]["gaps"]
        for c, g in g0.items():
            if c in large or c in small:
                drop = None
                total += 1; ok = (g >= 0.25) == (c in large); agree += ok
                rows.append(f"{s['scene']}:{c}={g:.2f}{'' if ok else '!'}")
    P("  " + " ".join(rows))
    g3 = total > 0 and agree / total >= 0.80
    P(f"-> G3 {'pass' if g3 else 'FAIL'}: {agree}/{total} = {agree/max(total,1):.0%} (bar >= 80%)\n")
    # ---- S1 the null stop on the hybrid path, held-out regret
    P("## S1 stopping rules on the hybrid path, scored by held-out error at the stop")
    def curve(s, v="hybrid"):
        st = s["variants"][v]["steps"]; return np.array([st[0]["e_ho_before"]] + [x["e_ho_after"] for x in st])
    rules = {}
    for s in all_sc:
        st = s["variants"]["hybrid"]["steps"]; c = curve(s)
        rules.setdefault("null M=19", {})[s["scene"]] = next((x["t"] for x in st if x["q_top"] <= max(x["null"][:M])), S_MAX)
        rules.setdefault("null M=49", {})[s["scene"]] = next((x["t"] for x in st if x["q_top"] <= max(x["null"][:49])), S_MAX)
        rules.setdefault("one percent", {})[s["scene"]] = next((x["t"] for x in st if x["dead"]), S_MAX)
        rules.setdefault("never stop", {})[s["scene"]] = S_MAX
        rules.setdefault("no growth", {})[s["scene"]] = 0
        rules.setdefault("hindsight", {})[s["scene"]] = int(np.argmin(c))
    reg = {}
    for r, T in rules.items():
        reg[r] = np.array([curve(s)[T[s["scene"]]] - curve(s).min() for s in all_sc])
        P(f"  {r:<12} mean regret {reg[r].mean():.4f} median {np.median(reg[r]):.4f} | stops: " + " ".join(f"{s['scene'][:6]} {T[s['scene']]}" for s in all_sc))
    exhausted = [s for s in all_sc if all(x["e_ho_before"] - x["e_ho_after"] < DEAD * x["e_ho_before"] for x in s["variants"]["hybrid"]["steps"][-3:])]
    stopped_there = [s for s in exhausted if rules["null M=19"][s["scene"]] < S_MAX]
    s1 = reg["null M=19"].mean() < reg["one percent"].mean() and (len(exhausted) == 0 or len(stopped_there) / len(exhausted) >= 0.5)
    P(f"  scenes whose last three hybrid steps each gained under 1% held-out: {len(exhausted)}; the null rule stopped before the budget on {len(stopped_there)} of them")
    P(f"  q_top / null max, median over scenes by step: " + " ".join(f"{np.median([s['variants']['hybrid']['steps'][t]['q_top']/max(max(s['variants']['hybrid']['steps'][t]['null'][:M]),1e-12) for s in all_sc]):.1f}" for t in range(S_MAX)))
    P(f"-> S1 {'pass' if s1 else 'FAIL'} (bar: lower mean held-out regret than the one percent rule, and stops before the budget on at least half the exhausted scenes)\n")
    # ---- outcome
    letter = "A" if (g1 and g2) else ("B" if g1 else "C")
    P(f"## Outcome (frozen tree): G1 {'pass' if g1 else 'fail'}, G2 {'pass' if g2 else 'fail'} -> {letter}; G3 {'pass' if g3 else 'fail'}, S1 {'pass' if s1 else 'fail'}")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/f6.json")
