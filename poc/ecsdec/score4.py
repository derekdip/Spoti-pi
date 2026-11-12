"""The frozen scorer for ED4 (docs/math-track-ed4-prereg.md): reads poc/results/ed4/ed4.json and config.json,
applies the placement bars H1 and H1p and the stopping bars H2a and H2b, reports the rest, prints the outcome.

  /usr/bin/python3 -m poc.ecsdec.score4                        the scored run -> report.md
  /usr/bin/python3 -m poc.ecsdec.score4 ROWS.json CONFIG.json  any rows (a pilot), printed only
"""
from __future__ import annotations
import json, sys, itertools
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed4"
SEL = ("slope", "line", "step", "trainslope", "trainline", "cfslope", "rgn", "gradnorm")
rk = lambda a: np.argsort(np.argsort(np.asarray(a, float)))
spearman = lambda a, b: float(np.corrcoef(rk(a), rk(b))[0, 1])


def main(rows_path=None, cfg_path=None):
    cfg = json.load(open(cfg_path or OUT / "config.json")); rows = json.load(open(rows_path or OUT / "ed4.json")); rows = rows["rows"] if isinstance(rows, dict) else rows
    prim, frac, k, prior, tol = cfg["primary"], cfg["frac"], cfg["beam"], cfg["prior"], cfg["prior_tol"]
    place = [r for r in rows if r.get("kind", "placement") == "placement"]; stop = [r for r in rows if r.get("kind") == "stopping"]; ev = lambda r: "te" if "te" in r["base"] else "ho"
    L = ["# ED4 report (frozen scorer)\n", f"Placement selector `{prim}`, beam of {k}; the fixed choice is {', '.join('`' + m + '`' for m in prior)}. Losses are on the test contexts.\n"]
    # ---- placement
    beam = lambda r, s: sorted(r["scores"], key=lambda m: -r["scores"][m][s])[:k]; held = lambda r, mods: min(r["fits"][m]["held"] for m in mods)
    rand = lambda r: float(np.mean([held(r, c) for c in itertools.combinations(r["fits"], k)]))
    best = lambda r: max(r["fits"], key=lambda m: r["fits"][m]["gain"]); cols = (prim, "the fixed choice", "rgn", "gradnorm", "random")
    val = lambda r, c: held(r, prior) if c == "the fixed choice" else rand(r) if c == "random" else held(r, beam(r, c))
    L.append("## Placement\n"); L.append("| condition | base loss | sweep's best module, gain | " + " | ".join(f"{c}: best gain in beam" for c in cols) + f" | `{prim}` beam |"); L.append("|---|---|---|" + "---|" * (len(cols) + 1))
    for r in place:
        b = r["base"][ev(r)]; L.append(f"| {r['name']} | {b:.3f} | {best(r)} {r['fits'][best(r)]['gain']:+.3f} | " + " | ".join(f"{b - val(r, c):+.3f}" for c in cols) + f" | {', '.join(beam(r, prim))} |")
    hits = [r["base"][ev(r)] - held(r, beam(r, prim)) >= frac * r["fits"][best(r)]["gain"] for r in place]; mean = lambda c: float(np.mean([val(r, c) for r in place])) if place else float("nan")
    H1a = len(place) >= 3 and sum(hits) >= len(place) - 1; H1b = bool(place) and all(mean(prim) < mean(c) for c in ("rgn", "gradnorm", "random")); H1 = H1a and H1b
    H1p = bool(place) and mean(prim) <= mean("the fixed choice") + tol
    L.append(f"\n**H1, the pre-screen picks well**: the `{prim}` beam reaches at least {frac:.0%} of the sweep's best gain on {sum(hits)} of {len(place)} conditions (needs {max(len(place) - 1, 0)}, and at least 3 conditions); "
             f"its mean best test loss is {mean(prim):.3f} against random {mean('random'):.3f}, rgn {mean('rgn'):.3f}, gradnorm {mean('gradnorm'):.3f} (needs to be below all three). **{'holds' if H1 else 'fails'}**.\n")
    L.append(f"**H1p, it is no worse than a fixed choice**: mean best test loss {mean(prim):.3f} against the fixed choice's {mean('the fixed choice'):.3f} (needs to be within {tol} nats above it, or below). **{'holds' if H1p else 'fails'}**.\n")
    # ---- stopping
    recs = []
    for r in stop:
        e = ev(r)
        for m, tj in r["traj"].items():
            g = r["base"][e] - np.array(tj[e]); i = int(np.argmax(g)); j = int(np.argmin(tj["ho"])); sc = r["scores"][m]
            recs.append(dict(cond=r["name"], m=m, rho=sc["rho"], cf=sc["cf"], peak=float(g[i]), peak_step=tj["step"][i], final=float(g[-1]), kept=float(g[-1] / g[i]) if g[i] > 0 else float("nan"),
                             val_step=tj["step"][j], val_gain=float(g[j]), val_ratio=float(g[j] / g[i]) if g[i] > 0 else float("nan"), train=float(r["base"]["tr"] - tj["tr"][-1])))
    if stop:
        L.append("## Stopping\n"); L.append("| condition | module | `rho` | cross-fitted share | peak test gain (step) | test gain at the end | kept | gain when stopped at the validation minimum (step) | share of the peak | training gain at the end |"); L.append("|---|" + "---|" * 9)
        for x in recs: L.append(f"| {x['cond']} | {x['m']} | {x['rho']:+.2f} | {x['cf']:+.2f} | {x['peak']:+.3f} ({x['peak_step']}) | {x['final']:+.3f} | {x['kept']:+.2f} | {x['val_gain']:+.3f} ({x['val_step']}) | {x['val_ratio']:.2f} | {x['train']:+.2f} |")
    n = len(recs); a = sum(x["kept"] < cfg["kept_max"] for x in recs); b = sum(x["val_ratio"] >= cfg["val_keep"] for x in recs); H2a = n > 0 and a == n; H2b = n > 0 and b >= cfg["val_min_share"] * n
    above = [x for x in recs if x["rho"] > 0.5]
    L.append(f"\n**H2a, a long fit goes bad whatever the share**: the test gain at the end is below {cfg['kept_max']:.0%} of its peak in {a} of {n} fits (needs all). **{'holds' if H2a else 'fails'}**. "
             f"Of the {len(above)} fits with `rho` above one half, {sum(x['kept'] < cfg['kept_max'] for x in above)} are among them; {sum(x['final'] < 0 for x in recs)} of {n} end below the unadapted model.\n")
    L.append(f"**H2b, stopping on validation keeps the gain**: stopping at the validation minimum keeps at least {cfg['val_keep']:.0%} of the peak test gain in {b} of {n} fits (needs {int(np.ceil(cfg['val_min_share'] * n))}). **{'holds' if H2b else 'fails'}**.\n")
    # ---- reported
    L.append("## Reported\n"); present = [s for s in SEL if any(all(s in r["scores"][m] for m in r["scores"]) for r in place)]
    L.append("Rank correlation of each score with the fitted test gain; * marks a beam that holds the sweep's best module.\n"); L.append("| condition | " + " | ".join(present) + " | the fixed choice |"); L.append("|---|" + "---|" * (len(present) + 1))
    for r in place:
        mods = list(r["fits"]); g = [r["fits"][m]["gain"] for m in mods]
        cell = lambda s: (f"{spearman([r['scores'][m][s] for m in mods], g):+.2f}{' *' if best(r) in beam(r, s) else ''}" if all(s in r["scores"][m] for m in mods) else "")
        L.append(f"| {r['name']} | " + " | ".join(cell(s) for s in present) + f" | {'*' if best(r) in prior else ''} |")
    for r in place:
        f = r["fits"]; L.append(f"\n- {r['name']}: fitted test gains " + ", ".join(f"{m} {f[m]['gain']:+.3f}" for m in sorted(f, key=lambda m: -f[m]["gain"])) + f"; seconds: scores {r['seconds']['scores']:.0f}, fits {r['seconds']['fits']:.0f}")
    for r in stop:
        sub = [x for x in recs if x["cond"] == r["name"]]
        L.append(f"\n- {r['name']}: rank correlation with the test gain at the end: `rho` {spearman([x['rho'] for x in sub], [x['final'] for x in sub]):+.2f}, cross-fitted share {spearman([x['cf'] for x in sub], [x['final'] for x in sub]):+.2f}; seconds {r['seconds']:.0f}")
    letter = "A" if (H1 and H1p) else "B" if H1 else "C"; S = "confirmed" if (H2a and H2b) else "not confirmed"
    L.append(f"\n## Outcome: placement **{letter}** (H1 {'holds' if H1 else 'fails'}, H1p {'holds' if H1p else 'fails'}); stopping **{S}** (H2a {'holds' if H2a else 'fails'}, H2b {'holds' if H2b else 'fails'})\n")
    if rows_path is None: (OUT / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:3])
