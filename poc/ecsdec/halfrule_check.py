"""The half rule (docs/prescreen-theory.md, section 6) checked on GPT-2: per module, is the held-out gain at the
training line-search step, as a share of the training gain there, equal to 2 rho - 1, rho the held-out slope
over the training slope?

  /usr/bin/python3 -m poc.ecsdec.halfrule_check      -> poc/results/ed4/halfrule_check.json and a table
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import prescreen as PS


def main(seed=5):
    P = GM.load_params(); tok = GM.tokenizer(); rows = []
    for transform, n in (("none", 8), ("altcaps", 8), ("none", 96), ("altcaps", 96)):
        t = time.time(); W = PS.make_world(seed, n, transform, P=P, tok=tok); sub = []
        for m in W.lib:
            s = W.cheap_scores(m); s.update(W.step_scores(m, 1.0)); rho = s["slope"] / s["trainslope"]
            sub.append(dict(transform=transform, n=n, module=m, rho=rho, predicted=2 * rho - 1, measured=s["line"] / s["trainline"], line=s["line"], trainline=s["trainline"], eta=s["eta_line"]))
        rows += sub; pr = np.array([x["predicted"] for x in sub]); me = np.array([x["measured"] for x in sub])
        PS.log(f"{transform} n={n}: rho median {np.median([x['rho'] for x in sub]):.3f}; 2rho-1 median {np.median(pr):+.3f}; measured line/trainline median {np.median(me):+.3f}; "
               f"modules with a negative look-ahead gain: measured {int((me < 0).sum())}/16, predicted {int((pr < 0).sum())}/16; sign agreement {int(((me < 0) == (pr < 0)).sum())}/16; "
               f"corr {np.corrcoef(pr, me)[0, 1]:+.2f}; mean |measured - predicted| {np.mean(np.abs(me - pr)):.3f} ({time.time() - t:.0f}s)")
        for x in sub: PS.log(f"   {x['module']:<8} rho {x['rho']:+.3f}  2rho-1 {x['predicted']:+.3f}  measured {x['measured']:+.3f}  (held gain {x['line']:+.4f}, train gain {x['trainline']:.4f}, step {x['eta']:.2f})")
        json.dump(rows, open(PS.OUT / "halfrule_check.json", "w"), indent=1)
    PS.log("half rule check done")


if __name__ == "__main__":
    main()
