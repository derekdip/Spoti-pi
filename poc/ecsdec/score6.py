"""The frozen scorer for ED6 (docs/math-track-ed6-prereg.md): the knee and the stopping rule on other models.
Reads poc/results/ed6/run/rows.json and config.json, applies ED5's bars E1 to E4 to each model, prints the
outcome per model and overall.

  /usr/bin/python3 -m poc.ecsdec.score6                        the scored run -> poc/results/ed6/run/report.md
  /usr/bin/python3 -m poc.ecsdec.score6 ROWS.json CONFIG.json  any rows (a pilot), printed only
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed6/run"; cv = lambda v: float(np.std(v) / np.mean(v)); short = lambda m: m.replace("transformer.h.", "")


def fits(r, keep):
    knees = [tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for tj in r["half"].values()]; gstar = float(np.median(knees)); sub = []
    for m, tj in r["full"].items():
        gt = tj["tr"][0] - np.array(tj["tr"]); ge = tj["te"][0] - np.array(tj["te"]); k = int(np.argmax(ge)); pk = float(ge[k]); reached = bool((gt >= gstar).any()); i = int(np.argmax(gt >= gstar)) if reached else len(gt) - 1
        if reached and i > 0 and gt[i] > gt[i - 1]: w = (gstar - gt[i - 1]) / (gt[i] - gt[i - 1]); g = ge[i - 1] + w * (ge[i] - ge[i - 1])
        else: g = ge[i]
        sub.append(dict(cond=r["name"], m=m, peak=pk, peak_step=tj["step"][k], knee=float(gt[k]), turned=tj["stopped"] == "turned", rule=float(g / pk), reached=reached, s60=float(ge[min(6, len(ge) - 1)] / pk), val=float(ge[int(np.argmin(tj["ho"]))] / pk),
                        last=float(ge[-1] / pk), steps=tj["step"][-1], base=tj["te"][0]))
    kn = [x["knee"] for x in sub]
    return sub, dict(name=r["name"], n=r["cond"]["n"], transform=r["cond"]["transform"], gstar=gstar, half_cv=cv(knees), half_turned=sum(tj["stopped"] == "turned" for tj in r["half"].values()), n_half=len(knees), knee_mean=float(np.mean(kn)), knee_cv=cv(kn),
                     ok=sum(x["rule"] >= keep for x in sub), seconds=r["seconds"])


def main(rows_path=None, cfg_path=None):
    cfg = json.load(open(cfg_path or OUT / "config.json")); rows = json.load(open(rows_path or OUT / "rows.json"))["rows"]; B = cfg["bars"]; L = ["# ED6 report (frozen scorer)\n"]; letters = {}
    for model in dict.fromkeys(r["cond"]["model"] for r in rows):
        recs, conds = [], []
        for r in rows:
            if r["cond"]["model"] != model: continue
            sub, c = fits(r, B["keep"]); recs += sub; conds.append(c)
        L += [f"## {model}\n", "| condition | matrix | base test loss | peak test gain (step) | training gain at the peak | turned | kept: at `g*` | at step 60 | at the validation minimum | at the last step | steps run |", "|---|" + "---|" * 10]
        for x in recs: L.append(f"| {x['cond']} | {short(x['m'])} | {x['base']:.3f} | {x['peak']:+.3f} ({x['peak_step']}) | {x['knee']:.2f} | {'yes' if x['turned'] else 'no'} | {x['rule']:.2f}{'' if x['reached'] else ' (g* not reached)'} | {x['s60']:.2f} | {x['val']:.2f} | {x['last']:+.2f} | {x['steps']} |")
        L += ["\n| condition | text, contexts | training gain at the test peak: mean, c.v. | half-fit knees: c.v., turned | `g*` | seconds |", "|---|" + "---|" * 5]
        for c in conds: L.append(f"| {c['name']} | {c['transform']}, {c['n']} | {c['knee_mean']:.2f}, {c['knee_cv']:.2f} | {c['half_cv']:.2f}, {c['half_turned']} of {c['n_half']} | {c['gstar']:.2f} | {c['seconds']:.0f} |")
        n = len(recs); E1 = all(c["knee_cv"] < B["cv_max"] for c in conds); pos = sum(x["rule"] > 0 for x in recs); ok = sum(x["rule"] >= B["keep"] for x in recs)
        E2 = pos == n and ok >= B["keep_share"] * n and all(c["ok"] >= B["keep_per_condition"] for c in conds); turned = sum(x["turned"] for x in recs); E3 = turned >= B["turn_share"] * n
        mr, m60 = float(np.mean([x["rule"] for x in recs])), float(np.mean([x["s60"] for x in recs])); E4 = mr >= m60; h = lambda b: "holds" if b else "fails"
        L.append(f"\n**E1, the knee is common to the matrices**: c.v. {', '.join(f'{c['knee_cv']:.2f}' for c in conds)} (needs below {B['cv_max']} in every condition). **{h(E1)}**.\n")
        L.append(f"**E2, the rule keeps the gain**: positive in {pos} of {n} (needs all); at least {B['keep']:.0%} of the peak in {ok} (needs {int(np.ceil(B['keep_share'] * n))}, and {B['keep_per_condition']} in every condition: {', '.join(str(c['ok']) for c in conds)}). **{h(E2)}**.\n")
        L.append(f"**E3, long fits go bad**: {turned} of {n} fell to a quarter of their peak within the cap (needs {int(np.ceil(B['turn_share'] * n))}). **{h(E3)}**.\n")
        L.append(f"**E4, the rule is at least as good as the 60-step budget**: mean share of the peak {mr:.3f} against {m60:.3f}. **{h(E4)}**.\n")
        L.append(f"Reported: share of the peak kept, mean and lowest: at `g*` {mr:.2f}, {min(x['rule'] for x in recs):.2f}; at step 60 {m60:.2f}, {min(x['s60'] for x in recs):.2f}; at the validation minimum {np.mean([x['val'] for x in recs]):.2f}, {min(x['val'] for x in recs):.2f}; "
                 f"at the last step {np.mean([x['last'] for x in recs]):+.2f}, {min(x['last'] for x in recs):+.2f}. Fits that never reached `g*`: {sum(not x['reached'] for x in recs)}. Fits below the unadapted model at their last step: {sum(x['last'] < 0 for x in recs)}.\n")
        letters[model] = "A" if (E1 and E2 and E3 and E4) else "B" if E2 else "C"; L.append(f"**{model}: {letters[model]}** (E1 {h(E1)}, E2 {h(E2)}, E3 {h(E3)}, E4 {h(E4)})\n")
    L.append("## Outcome: " + ", ".join(f"{m} **{v}**" for m, v in letters.items()) + f"; A on {sum(v == 'A' for v in letters.values())} of {len(letters)} models, the rule keeps the gain (A or B) on {sum(v in 'AB' for v in letters.values())}\n")
    if rows_path is None: (OUT / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:3])
