"""The frozen scorer for ED4 (docs/math-track-ed4-prereg.md): reads poc/results/ed4/ed4.json and config.json,
applies bars H1 and H2, reports H3, prints the letter. Run: /usr/bin/python3 -m poc.ecsdec.score4"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed4"
SEL = ("slope", "step", "line", "full", "rgn", "gradnorm", "trainline", "trainslope")


def main():
    cfg = json.load(open(OUT / "config.json")); rows = json.load(open(OUT / "ed4.json"))["rows"]; prim, gate, go_min, frac = cfg["primary"], cfg["gate"], cfg["go_min"], cfg["frac"]
    L = ["# ED4 report (frozen scorer)\n", f"Placement selector `{prim}`, go/no-go gate `{gate}`, a condition is 'go' when the sweep's best fitted gain is at least {go_min} nats.\n"]
    gain = lambda r, s: r["base"]["ho"] - r["read"][s]["best_held"]
    L.append("## Per condition\n"); L.append("| condition | base held-out loss | sweep's best module, gain | " + " | ".join(f"{s} beam gain" for s in (prim, "rgn", "gradnorm", "random")) + f" | max `{gate}` | go by the sweep | go by the gate |"); L.append("|---|---|---|---|---|---|---|---|---|---|")
    go, agree = [], []
    for r in rows:
        sw = r["read"]["sweep"]; is_go = sw["gain"] >= go_min; gate_go = max(r["scores"][m][gate] for m in r["scores"]) > 0; agree.append(is_go == gate_go)
        if is_go: go.append(r)
        L.append(f"| {r['name']} | {r['base']['ho']:.3f} | {sw['module']} {sw['gain']:+.3f} | " + " | ".join(f"{gain(r, s):+.3f}" for s in (prim, "rgn", "gradnorm", "random")) + f" | {max(r['scores'][m][gate] for m in r['scores']):+.4f} | {is_go} | {gate_go} |")
    hits = [gain(r, prim) >= frac * r["read"]["sweep"]["gain"] for r in go]
    mean = lambda s: float(np.mean([r["read"][s]["best_held"] for r in go])) if go else float("nan")
    H1a = len(go) >= 3 and sum(hits) >= len(go) - 1; H1b = bool(go) and all(mean(prim) < mean(s) for s in ("rgn", "gradnorm", "random")); H1 = H1a and H1b
    L.append(f"\n**H1, placement**: on the {len(go)} go conditions, the `{prim}` beam reaches at least {frac:.0%} of the sweep's best gain on {sum(hits)} (needs {max(len(go) - 1, 0)} and at least 3 go conditions); its mean best held-out loss {mean(prim):.3f} against Auto-RGN {mean('rgn'):.3f}, the training-gradient probe {mean('gradnorm'):.3f}, random placement {mean('random'):.3f}, the sweep {mean('sweep'):.3f}. **{'holds' if H1 else 'fails'}**.\n")
    H2 = all(agree); L.append(f"**H2, go or no-go**: the gate agrees with the sweep on {sum(agree)} of {len(rows)} conditions. **{'holds' if H2 else 'fails'}**.\n")
    L.append("## H3, reported\n"); L.append("Rank correlation (Spearman) of each score with the fitted held-out gain, and whether its beam of " + str(cfg["beam"]) + " holds the sweep's best module:\n")
    present = [s for s in SEL if all(s in r["read"] for r in rows)] + [s for s in ("full",) if any(s in r["read"] for r in rows) and not all(s in r["read"] for r in rows)]
    L.append("| condition | " + " | ".join(present) + " |"); L.append("|---|" + "---|" * len(present))
    for r in rows: L.append(f"| {r['name']} | " + " | ".join((f"{r['read'][s]['spearman']:+.2f}{' *' if r['read'][s]['hit'] else ''}" if s in r["read"] else "") for s in present) + " |")
    L.append("\n(* the beam contains the sweep's best module.)\n")
    for r in rows:
        f = r["fits"]; order = sorted(f, key=lambda m: -f[m]["gain"])
        L.append(f"- {r['name']}: fitted gains " + ", ".join(f"{m} {f[m]['gain']:+.3f}" for m in order) + f"; `{prim}` beam {r['read'][prim]['beam']}; seconds: scores {r['seconds']['scores']:.0f}, fits {r['seconds']['fits']:.0f}")
    letter = "A" if (H1 and H2) else "B" if H1 else "C" if H2 else "D"
    L.append(f"\n## Letter: **{letter}** (H1 {'holds' if H1 else 'fails'}, H2 {'holds' if H2 else 'fails'})\n")
    (OUT / "report.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
