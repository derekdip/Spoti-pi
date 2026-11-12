"""The frozen scorer for ED3 (docs/math-track-ed3-prereg.md): reads poc/results/ed3/ed3.json, applies bars G1 and
G2, reports G3, prints the letter. Run: /usr/bin/python3 -m poc.ecsdec.score3"""
from __future__ import annotations
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed3"


def main():
    rows = {r["case"]: r for r in json.load(open(OUT / "ed3.json"))["rows"]}; L = ["# ED3 report (frozen scorer)\n"]
    def selector_table(r):
        T = ["| selector | modules fitted | best J among them |", "|---|---|---|"]
        for k, v in r["selectors"].items(): T.append(f"| {k} | {' '.join(v)} | {r['selector_J'][k]:.4f} |")
        T.append(f"| random, expected over draws | | {r['selector_J']['expected_random']:.4f} |"); T.append(f"| the full sweep | all | {r['selector_J']['sweep']:.4f} |")
        T.append(f"| the base | | {r['fits']['base']['J']:.4f} |"); T.append(f"| the current | | {r['J_cur']:.4f} |"); return T
    e = rows["extend"]; L.append("## G1, the planted module under a format shift\n")
    L.append(f"Truth {e['truth']}; got {e['got']}; first stage {e['first_stage']}; budget gain {e.get('glob_improvement', float('nan')):.3f}; restarts beating the first fit {e['note']['restarts_better']} of {len(e['note']['restart_F']) - 1}.")
    in_beam = e["truth"].split(":")[1] in e.get("beam", []); G1 = e["correct"] is True
    L.append(f"The planted module in the held-out-gain beam: {in_beam}; in the matched-p beam: {e['truth'].split(':')[1] in e.get('beam_matched_p', [])}; in the Auto-RGN beam: {e['truth'].split(':')[1] in e.get('beam_rgn', [])}.")
    if "selectors" in e: L += selector_table(e)
    L.append(f"\n**G1**: the rule returns EXPAND on the planted module: **{'holds' if G1 else 'fails'}**.\n")
    r = rows["real"]; L.append("## G2, the format shift itself: selectors against the sweep\n"); L += selector_table(r)
    sj = r["selector_J"]; G2 = sj["held_gain"] <= sj["rgn"] + 1e-12 and sj["held_gain"] <= sj["expected_random"] + 1e-12 and sj["held_gain"] <= sj["sweep"] * 1.01 + 1e-12
    L.append(f"\nAction {r['got']}; held-out NLL base {r['nll_held']['base']:.3f}, current {r['nll_held']['current']:.3f}; restarts beating the first fit {r['note']['restarts_better']}.")
    L.append(f"\n**G2**: the held-out gain's beam does at least as well as Auto-RGN's and as random placement's expectation, and within 1 percent of the sweep: **{'holds' if G2 else 'fails'}**.\n")
    L.append("## G3, reported\n")
    for name, rr in rows.items():
        if "predictor" in rr:
            pr = rr["predictor"]; extra = f", against the fitted cross-entropy gain Pearson {pr['pearson_nll']:.2f}, Spearman {pr['spearman_nll']:.2f}" if "pearson_nll" in pr else ""
            L.append(f"- {name}: first-order held-out gain against the fitted held-out distortion gain, Pearson {pr['pearson']:.2f}, Spearman {pr['spearman']:.2f}{extra}; per module (predicted / fitted distortion gain" + (" / fitted cross-entropy gain" if "fitted_nll_gain" in pr else "") + "): " + ", ".join(f"{m} {rr['cands'][m]['gain_held']:+.3f}/{pr['fitted_gain'][m]:+.3f}" + (f"/{pr['fitted_nll_gain'][m]:+.3f}" if "fitted_nll_gain" in pr else "") for m in sorted(rr["cands"], key=lambda m: -rr['cands'][m]['gain_held'])))
            L.append(f"- {name}: D {rr['D']:.4f} D_held {rr['D_held']:.4f} s {rr['stat']:.2e} first stage {rr['first_stage']} tau_sketch {rr.get('tau_sketch', float('nan')):.3f} fits {rr['fits_run']}; sweep (J): " + ", ".join(f"{m} {rr['sweep'][m]['J']:.4f}" for m in sorted(rr["sweep"], key=lambda m: rr["sweep"][m]["J"])))
    letter = "A" if (G1 and G2) else "B" if G1 else "C" if G2 else "D"
    L.append(f"\n## Letter: **{letter}** (G1 {'holds' if G1 else 'fails'}, G2 {'holds' if G2 else 'fails'})\n")
    (OUT / "report.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
