"""Score F4 by its frozen bars. Reads poc/results/f4.json and the column reference; writes nothing
but the tables it prints. Written before the run finished, so it cannot be tuned to the result.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BED_SCORABLE = ("ignition", "delayed_ignition", "full")


def main(path="poc/results/f4.json"):
    d = json.load(open(path)); ref = json.load(open("poc/results/column_reference.json"))
    rows = d["unseen"]
    if not rows:
        print("no scenes yet"); return
    print(f"{len(rows)} of 7 unseen scenes present" + ("" if "finished" in d else "  (run not finished)"))
    print()
    print("| scene | V0 | standard floor (de, two-stage) | column best-known | beats column | look fit -> linear | glow corr (look) | burn wrong | passable wrong | missed alight | parcels | greedy / floor |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    corr, beats, heat, ai, alight, live, search = [], [], [], [], [], [], []
    for r in rows:
        nm = r["scene"]; st, lk = r["fits"]["standard"], r["fits"]["look"]
        c = lk["decisions"]["visual"]["late_correlation"]
        if nm == "shutoff" or not np.isfinite(c):
            c = lk["decisions"]["visual"]["full_correlation"]
        corr.append(c)
        b = st["error"] < ref[nm]["best_known"]; beats.append(b)
        dh, da = st["decisions"]["heat"]["disagree"], st["decisions"]["ai"]["disagree"]
        heat.append(dh); ai.append(da); live.append(st["live"])
        ma = st["decisions"]["ignition"]["missed_alight"] if nm in BED_SCORABLE else None
        if ma is not None: alight.append(ma)
        g = r["greedy"]; frac = (r["e_v0"] - g["e_final"]) / max(r["e_v0"] - st["error"], 1e-9); search.append(frac)
        sp = st["spread"]
        print(f"| {nm} | {r['e_v0']:.3f} | **{st['error']:.3f}** ({sp['de']:.3f}, {sp['two_stage']:.3f}) | {ref[nm]['best_known']:.3f} | {'yes' if b else 'no'} | "
              f"{lk['fit_objective']:.3f} -> {lk['error']:.3f} | {c:.2f} | {100*dh:.1f}% | {100*da:.1f}% | "
              f"{'' if ma is None else f'{100*ma:.0f}%'} | {st['live']} | {frac:.2f} |")
    print()
    B1 = float(np.median(corr)); B2 = int(sum(beats)); B3h, B3a = float(np.median(heat)), float(np.median(ai))
    B3m = float(np.median(alight)) if alight else float("nan"); B4 = max(live); B5 = float(np.median(search))
    n = len(rows)
    print("| bar | target | result | |")
    print("|---|---|---|---|")
    print(f"| B1 glow | median corr >= 0.80 | {B1:.3f} ({sum(x >= 0.9 for x in corr)} of {n} at >= 0.90) | {'pass' if B1 >= 0.80 else 'FAIL'} |")
    print(f"| B2 floor vs column | >= 6 of 7 | {B2} of {n} | {'pass' if B2 >= 6 else 'FAIL'} |")
    print(f"| B3 decisions | burn <= 5%, passable <= 5%, alight missed <= 25% | {100*B3h:.1f}%, {100*B3a:.1f}%, {100*B3m:.0f}% | {'pass' if (B3h <= .05 and B3a <= .05 and B3m <= .25) else 'FAIL'} |")
    print(f"| B4 cost | parcels <= 24 everywhere | max {B4} | {'pass' if B4 <= 24 else 'FAIL'} |")
    print(f"| B5 search | median greedy/floor >= 0.80 | {B5:.3f} | {'pass' if B5 >= 0.80 else 'FAIL'} |")
    letter = {(True, True): "A", (True, False): "B", (False, True): "C", (False, False): "D"}[(B1 >= 0.80, B2 >= 6)]
    print(f"\nOutcome by the frozen tree (B1 x B2): **{letter}**" + ("" if n == 7 else "  (provisional, run incomplete)"))
    print("\nP1 split/shutoff below column:", {r["scene"]: (round(r["fits"]["standard"]["error"], 3), ref[r["scene"]]["best_known"]) for r in rows if r["scene"] in ("split", "shutoff")})
    picks = {}
    for r in rows:
        picks[r["scene"]] = [s["picked"] for s in r["greedy"]["steps"] if s.get("picked")]
    print("P2 greedy picks:", picks)
    print("\nper consumer at the standard floor:")
    for r in rows:
        print(f"  {r['scene']:<17} " + "  ".join(f"{k} {v:.3f}" for k, v in r["fits"]["standard"]["per_consumer"].items())
              + f"   | column: " + "  ".join(f"{k} {v:.3f}" for k, v in ref[r["scene"]]["per_consumer"].items()))


if __name__ == "__main__":
    main(*sys.argv[1:])
