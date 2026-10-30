"""The frozen scorer for ED2 (docs/math-track-ed2-prereg.md): reads poc/results/ed2/ed2.json (the planted cases)
and real.json (the real-data case with its sweep), applies bars F1 and F2, reports F3, prints the letter.
Run: /usr/bin/python3 -m poc.ecsdec.score2"""
from __future__ import annotations
import json
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed2"


def main():
    rows = json.load(open(OUT / "ed2.json"))["rows"]; real = json.load(open(OUT / "real.json"))["rows"][0]; L = ["# ED2 report (frozen scorer)\n", "## F1, the planted cases\n"]
    L.append("| case | truth | got | D | D_held | s | first stage | budget gain | beam (held-out gain) | beam the matched-p score would give | fits |"); L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r['case']} | {r['truth']} | {r['got']}{'' if r['correct'] else ' (miss)'} | {r['D']:.3f} | {r['D_held']:.3f} | {r['stat']:.1e} | {r['first_stage']} | {r.get('glob_improvement', float('nan')):.3f} | {' '.join(r.get('beam', []))} | {' '.join(r.get('beam_matched_p', []))} | {r['fits_run']} |")
    n_ok = sum(r["correct"] for r in rows); expand_ok = all(r["correct"] for r in rows if r["truth"].startswith("EXPAND"))
    F1 = n_ok >= 4 and expand_ok; L.append(f"\n**F1**: {n_ok} of {len(rows)} right, the extend case names the planted module: {expand_ok}. **{'holds' if F1 else 'fails'}**.\n")
    L.append("## F2, the real-data case against the sweep\n")
    sw = real["sweep"]; best = real["sweep_best"]; chosen = real.get("chosen"); fits_rule = real["fits_run"] - (len(sw) - len([m for m in real.get('beam', [])]))
    L.append("| module | D_held | J | in beam |"); L.append("|---|---|---|---|")
    for m, v in sorted(sw.items(), key=lambda kv: kv[1]["J"]): L.append(f"| {m}{' (sweep best)' if m == best else ''}{' (chosen)' if m == chosen else ''} | {v['D_held']:.4f} | {v['J']:.4f} | {'yes' if m in real.get('beam', []) else ''} |")
    fb = real["fits"]["base"]; am = real["fits"]["all_modules"]; L.append(f"| base (the fallback) | {fb['D_held']:.4f} | {fb['J']:.4f} | |"); L.append(f"| all modules (reported) | {am['D_held']:.4f} | {am['J']:.4f} | |"); L.append(f"| current | {real['D_held']:.4f} | {real['J_cur']:.4f} | |")
    J_best = sw[best]["J"]; J_chosen = sw[chosen]["J"] if chosen in sw else (fb["J"] if chosen == "base" else real["J_cur"])
    F2 = real["action"] in ("EXPAND", "FALLBACK") and J_chosen <= J_best * (1 + 0.01) + 1e-12
    L.append(f"\nAction {real['got']}; the sweep's best is {best} (J {J_best:.4f}); the rule's choice scores J {J_chosen:.4f}. Fits: rule {fits_rule} (budget plus beam plus fallback), sweep {len(sw)} plus the fallback. Held-out NLL: {real.get('nll_held')}.")
    L.append(f"\n**F2**: the rule's choice is within 1 percent of the sweep's best deployment objective: **{'holds' if F2 else 'fails'}**.\n")
    L.append("## F3, reported\n")
    for r in rows + [real]:
        if "cands" in r:
            e12 = lambda c: c['eta'].get('12', c['eta'].get(12, 0))
            L.append(f"- {r['case']}: tau_sketch {r.get('tau_sketch', float('nan')):.3f}; held-out gain / train gain / eta p12 per module: " + ", ".join(f"{m} {c['gain_held']:.3f}/{c['gain_train']:.3f}/{e12(c):.3f}" for m, c in sorted(r["cands"].items(), key=lambda kv: -kv[1]['gain_held'])) + f"; collapsed {r.get('collapsed', [])}; matched-p collapses {sum(1 for p in r.get('pairs', {}).values() if p['collapse_matched'])} of {len(r.get('pairs', {}))}")
    for r in rows + [real]:
        if "fits" in r: L.append(f"- {r['case']} fits: " + ", ".join(f"{m} held {v['D_held']:.4f} J {v['J']:.4f}" for m, v in r["fits"].items()) + f"; J_current {r['J_cur']:.4f}")
    letter = "A" if (F1 and F2) else "B" if F1 else "C" if F2 else "D"
    L.append(f"\n## Letter: **{letter}** (F1 {'holds' if F1 else 'fails'}, F2 {'holds' if F2 else 'fails'})\n")
    (OUT / "report.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
