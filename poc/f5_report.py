"""Score F5 by its frozen bars. Reads poc/results/f5.json; prints tables and nothing else.

Written while the run was still going and before any glow correlation had been seen, so the
scoring cannot be tuned to the result.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BED = ("bed_chain",)


def corr_of(fit, scene):
    v = fit["decisions"]["visual"]
    c = v["late_correlation"]
    return v["full_correlation"] if not np.isfinite(c) else c


def static_reference():
    """Correlation a perfect static blob reaches, from the measure check: a scene-independent 0.85."""
    return 0.85


def main(path="poc/results/f5.json"):
    d = json.load(open(path))
    fresh = d.get("fresh", [])
    print(f"{len(fresh)} of 5 fresh scenes present" + ("" if "finished" in d else "   (run not finished)"))
    if not fresh:
        return
    print("\n### Fresh scenes, at the cross-evaluated best state\n")
    print("| scene | gust | V0 | floor (de, two-stage) | best fit | sway: model / teacher | ratio | phase err | glow corr | burn wrong | passable wrong | missed alight | parcels | greedy / floor |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    ratios, phases, corrs, heats, ais, alights, lives, searches = [], [], [], [], [], [], [], []
    for r in fresh:
        b = r["fits"][r["best"]]
        c = corr_of(b, r["scene"]); dec = b["decisions"]
        ma = dec["ignition"]["missed_alight"] if "ignition" in dec else None
        g = r.get("greedy")
        frac = (r["e_v0"] - g["e_final"]) / max(r["e_v0"] - b["error"], 1e-9) if g else float("nan")
        ratios.append(b["sway_ratio"]); phases.append(b["sway_phase_err"]); corrs.append(c)
        heats.append(dec["heat"]["disagree"]); ais.append(dec["ai"]["disagree"]); lives.append(b["live"])
        if ma is not None: alights.append(ma)
        if g: searches.append(frac)
        sp = b["spread"]
        print(f"| {r['scene']} | {r['gust_amp']:.1f} m/s @ {r['gust_hz']:.1f} Hz | {r['e_v0']:.3f} | {b['error']:.3f} ({sp['de']:.3f}, {sp['two_stage']:.3f}) | {r['best']} | "
              f"{100*b['sway_amp']:.1f} / {100*r['teacher_sway']:.1f} cm | {b['sway_ratio']:.0%} | {b['sway_phase_err']:.0f} deg | {c:.2f} | "
              f"{100*dec['heat']['disagree']:.1f}% | {100*dec['ai']['disagree']:.1f}% | {'' if ma is None else f'{100*ma:.0f}%'} | {b['live']} | {frac:.2f} |")
    B1r, B1p = float(np.median(ratios)), float(np.median(phases))
    B2 = float(np.median(corrs))
    B3h, B3a = float(np.median(heats)), float(np.median(ais))
    B3m = float(np.median(alights)) if alights else float("nan")
    B4 = max(lives)
    tr = d.get("transfer", [])
    B5 = all(0.5 <= t["sway_ratio"] <= 1.5 and t["sway_phase_err"] <= 60 for t in tr) if len(tr) == 2 else None
    print("\n### Bars\n")
    print("| bar | target | result | |")
    print("|---|---|---|---|")
    ok1 = 0.5 <= B1r <= 1.5 and B1p <= 45
    print(f"| B1 motion | median ratio in [0.5,1.5], median phase err <= 45 deg | {B1r:.2f}, {B1p:.0f} deg | {'pass' if ok1 else 'FAIL'} |")
    print(f"| B2 shape | median glow correlation >= 0.70 | {B2:.3f} (a static blob reaches {static_reference():.2f}) | {'pass' if B2 >= 0.70 else 'FAIL'} |")
    ok3 = B3h <= .05 and B3a <= .05 and (not np.isfinite(B3m) or B3m <= .25)
    print(f"| B3 decisions | burn <=5%, passable <=5%, alight missed <=25% | {100*B3h:.1f}%, {100*B3a:.1f}%, {100*B3m:.0f}% | {'pass' if ok3 else 'FAIL'} |")
    print(f"| B4 cost | <= 20 parcels on every fresh scene | max {B4} | {'pass' if B4 <= 20 else 'FAIL'} |")
    if B5 is not None:
        print(f"| B5 transfer | ratio in [0.5,1.5] and phase err <= 60 deg on both | " +
              "; ".join(f"{t['scene']} {t['sway_ratio']:.0%}/{t['sway_phase_err']:.0f}deg" for t in tr) + f" | {'pass' if B5 else 'FAIL'} |")
    if searches:
        print(f"| (reported) search | median greedy / floor | {float(np.median(searches)):.2f} | |")
    letter = {(True, True): "A", (True, False): "B", (False, True): "C", (False, False): "D"}[(ok1, B2 >= 0.70)]
    print(f"\nOutcome by the frozen tree (B1 motion x B2 shape): **{letter}**" + ("" if len(fresh) == 5 else "  (provisional)"))
    paired = d.get("paired", [])
    if paired:
        F4 = {"ignition": 0.481, "full": 0.470, "windy": 0.329}
        F4SW = {"ignition": None, "full": None, "windy": None}
        print("\n### Paired re-measurement (declared seen; F4 numbers are its frozen standard floors)\n")
        print("| scene | F4 error | F5 error | change | F5 sway ratio | phase err | parcels | F4 parcels |")
        print("|---|---|---|---|---|---|---|---|")
        F4L = {"ignition": 26, "full": 7, "windy": 6}
        for r in paired:
            b = r["fits"][r["best"]]
            f4 = F4[r["scene"]]
            print(f"| {r['scene']} | {f4:.3f} | {b['error']:.3f} | {(b['error']-f4)/f4:+.1%} | {b['sway_ratio']:.0%} | {b['sway_phase_err']:.0f} deg | {b['live']} | {F4L[r['scene']]} |")
    if "pilot" in d:
        p = d["pilot"]; b = p["fits"][p["best"]]
        print(f"\npilot `gusty` (seen): error {b['error']:.3f}, sway {b['sway_ratio']:.0%} at {b['sway_phase_err']:.0f} deg, {b['live']} parcels")
    print("\nlook-fit versus standard-fit sway ratio, every scene that has both:")
    for r in ([d["pilot"]] if "pilot" in d else []) + fresh + paired:
        s, l = r["fits"]["standard"], r["fits"]["look"]
        print(f"  {r['scene']:<13} standard {s['sway_ratio']:5.0%} ({s['sway_phase_err']:3.0f} deg, E {s['error']:.3f})   look {l['sway_ratio']:5.0%} ({l['sway_phase_err']:3.0f} deg, E {l['error']:.3f})   best: {r['best']}")
    print("\nv_rise at the best state, against F4's 0.37 to 0.56 on gusted scenes (P1):")
    for r in fresh + paired:
        print(f"  {r['scene']:<13} v_rise {r['fits'][r['best']]['state']['v_rise']:.2f} m/s")


if __name__ == "__main__":
    main(*sys.argv[1:])
