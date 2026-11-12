"""The frozen scorer for ED5 (docs/math-track-ed5-prereg.md): reads poc/results/ed5/ed5.json and config.json,
applies bars E1 to E4, reports the rest, prints the outcome.

  /usr/bin/python3 -m poc.ecsdec.score5                        the scored run -> report.md
  /usr/bin/python3 -m poc.ecsdec.score5 ROWS.json CONFIG.json  any rows (a pilot), printed only
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed5"; cv = lambda v: float(np.std(v) / np.mean(v))


def main(rows_path=None, cfg_path=None):
    cfg = json.load(open(cfg_path or OUT / "config.json")); rows = json.load(open(rows_path or OUT / "ed5.json"))["rows"]; B = cfg["bars"]
    L = ["# ED5 report (frozen scorer)\n", "| condition | matrix | peak test gain (step) | training gain at the peak | turned within the cap | kept: at `g*` | at step 60 | at the validation minimum | at the last step | steps run |", "|---|" + "---|" * 9]; recs = []; conds = []
    for r in rows:
        knees = [tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for tj in r["half"].values()]; gstar = float(np.median(knees)); sub = []
        for m, tj in r["full"].items():
            gt = tj["tr"][0] - np.array(tj["tr"]); ge = tj["te"][0] - np.array(tj["te"]); k = int(np.argmax(ge)); pk = float(ge[k]); reached = bool((gt >= gstar).any()); i = int(np.argmax(gt >= gstar)) if reached else len(gt) - 1
            if reached and i > 0 and gt[i] > gt[i - 1]: w = (gstar - gt[i - 1]) / (gt[i] - gt[i - 1]); g = ge[i - 1] + w * (ge[i] - ge[i - 1])
            else: g = ge[i]
            x = dict(cond=r["name"], m=m, peak=pk, peak_step=tj["step"][k], knee=float(gt[k]), turned=tj["stopped"] == "turned", rule=float(g / pk), reached=reached, s60=float(ge[min(6, len(ge) - 1)] / pk), val=float(ge[int(np.argmin(tj["ho"]))] / pk), last=float(ge[-1] / pk), steps=tj["step"][-1],
                     early=float(np.mean([ge[j] / gt[j] for j in (1, 2, 3)]))); sub.append(x)
            L.append(f"| {x['cond']} | {m} | {pk:+.3f} ({x['peak_step']}) | {x['knee']:.2f} | {'yes' if x['turned'] else 'no'} | {x['rule']:.2f}{'' if reached else ' (g* not reached)'} | {x['s60']:.2f} | {x['val']:.2f} | {x['last']:+.2f} | {x['steps']} |")
        recs += sub; kn = [x["knee"] for x in sub]
        conds.append(dict(name=r["name"], n=r["cond"]["n"], gstar=gstar, half=knees, half_cv=cv(knees), half_turned=sum(tj["stopped"] == "turned" for tj in r["half"].values()), knee_mean=float(np.mean(kn)), knee_cv=cv(kn), ok=sum(x["rule"] >= B["keep"] for x in sub), seconds=r["seconds"]))
    L.append("\n| condition | contexts | training gain at the test peak: mean, c.v. over the matrices | the eight half-fit knees | their c.v. | half-fits that turned | `g*` | seconds |"); L.append("|---|" + "---|" * 7)
    for c in conds: L.append(f"| {c['name']} | {c['n']} | {c['knee_mean']:.2f}, {c['knee_cv']:.2f} | {' '.join(f'{v:.2f}' for v in c['half'])} | {c['half_cv']:.2f} | {c['half_turned']} of {len(c['half'])} | {c['gstar']:.2f} | {c['seconds']:.0f} |")
    n = len(recs); E1 = bool(conds) and all(c["knee_cv"] < B["cv_max"] for c in conds); pos = sum(x["rule"] > 0 for x in recs); ok = sum(x["rule"] >= B["keep"] for x in recs)
    E2 = n > 0 and pos == n and ok >= B["keep_share"] * n and all(c["ok"] >= B["keep_per_condition"] for c in conds); turned = sum(x["turned"] for x in recs); E3 = n > 0 and turned >= B["turn_share"] * n
    mr, m60 = float(np.mean([x["rule"] for x in recs])), float(np.mean([x["s60"] for x in recs])); E4 = n > 0 and mr >= m60
    L.append(f"\n**E1, the knee is common to the matrices**: the c.v. of the training gain at the test peak is {', '.join(f'{c['knee_cv']:.2f} ({c['name']})' for c in conds)} (needs below {B['cv_max']} in every condition). **{'holds' if E1 else 'fails'}**.\n")
    L.append(f"**E2, the rule keeps the gain**: stopped at `g*`, the test gain is positive in {pos} of {n} fits (needs all) and at least {B['keep']:.0%} of the peak in {ok} (needs {int(np.ceil(B['keep_share'] * n))}, and {B['keep_per_condition']} in every condition: {', '.join(f'{c['ok']} ({c['name']})' for c in conds)}). **{'holds' if E2 else 'fails'}**.\n")
    L.append(f"**E3, long fits go bad at this size**: the test gain fell to a quarter of its peak within the cap in {turned} of {n} fits (needs {int(np.ceil(B['turn_share'] * n))}). **{'holds' if E3 else 'fails'}**.\n")
    L.append(f"**E4, the rule is at least as good as the 60-step budget**: mean share of the peak kept {mr:.3f} against {m60:.3f}. **{'holds' if E4 else 'fails'}**.\n")
    L.append("## Reported\n"); L.append(f"- Share of the peak kept, mean and lowest over the {n} fits: at `g*` {mr:.2f}, {min(x['rule'] for x in recs):.2f}; at step 60 {m60:.2f}, {min(x['s60'] for x in recs):.2f}; at the validation minimum {np.mean([x['val'] for x in recs]):.2f}, {min(x['val'] for x in recs):.2f}; at the last step {np.mean([x['last'] for x in recs]):+.2f}, {min(x['last'] for x in recs):+.2f}.")
    L.append(f"- Fits whose training gain never reached `g*` before they stopped: {sum(not x['reached'] for x in recs)}. Fits below the unadapted model at their last step: {sum(x['last'] < 0 for x in recs)}.")
    L.append("- Test gain over training gain in the first 30 steps: " + "; ".join(f"{c['name']} " + " ".join(f"{x['early']:.2f}" for x in recs if x["cond"] == c["name"]) for c in conds) + ".")
    letter = "A" if (E1 and E2 and E3 and E4) else "B" if E2 else "C"
    L.append(f"\n## Outcome: **{letter}** (E1 {'holds' if E1 else 'fails'}, E2 {'holds' if E2 else 'fails'}, E3 {'holds' if E3 else 'fails'}, E4 {'holds' if E4 else 'fails'})\n")
    if rows_path is None: (OUT / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:3])
