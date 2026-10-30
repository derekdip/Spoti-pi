"""The frozen scorer for ED1 (docs/math-track-ed1-prereg.md): reads poc/results/ed1/ed1.json, applies bars E1 to
E3, reports E4, and prints the letter by the frozen tree. Run: /usr/bin/python3 -m poc.ecsdec.score"""
from __future__ import annotations
import json, sys
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / "poc/results/ed1"


def redundant_fits(rec):
    """Beam members equivalent, under the frozen rule, to an earlier beam member of the same case."""
    beam = rec.get("beam", []); pairs = rec.get("pairs", {}); n = 0
    for i, b in enumerate(beam):
        for a in beam[:i]:
            pg = pairs.get(f"{a}|{b}") or pairs.get(f"{b}|{a}")
            if pg and pg["collapse"]: n += 1; break
    return n


def main():
    R = json.load(open(OUT / "ed1.json")); rows = R["rows"]; pairs = R["pairs"]; sweeps = R["sweeps"]
    by = {}
    for r in rows: by.setdefault(r["abl"], {})[r["case"]] = r
    full = by["full"]; cases = list(full)
    L = []
    L.append("# ED1 report (frozen scorer)\n")
    L.append("## Actions per arm\n")
    L.append("| case | truth | " + " | ".join(by) + " |"); L.append("|---|---|" + "---|" * len(by))
    for c in cases:
        L.append(f"| {c} | {full[c]['truth']} | " + " | ".join(f"{by[a][c]['got']}{'' if by[a][c]['correct'] else ' (miss)'}" if c in by[a] else "" for a in by) + " |")
    n_full = sum(full[c]["correct"] for c in cases)
    expand_ok = all(full[c]["correct"] for c in ("reuse", "extend"))
    E1 = n_full >= 7 and expand_ok
    L.append(f"\n**E1**: the full rule gets {n_full} of {len(cases)}; EXPAND cases name the planted module: {expand_ok}. **{'holds' if E1 else 'fails'}**.\n")
    pf = {tuple(p["pair"]): p for p in pairs if p["abl"] == "full"}
    p1 = pf.get(("wv@1", "wo@1")); p2 = pf.get(("wv@0", "w2@1"))
    E2 = bool(p1 and p1["collapse"] and p2 and not p2["collapse"])
    L.append("## Equivalence (full arm)\n")
    L.append("| pair | truth | frozen rule | matched-p rule | containment | align | p1 mu/d | p3 mu/d | p12 mu/d |"); L.append("|---|---|---|---|---|---|---|---|---|")
    for p in pairs:
        if p["abl"] != "full": continue
        g = p["geometry"]; pp = g["p"]; f = lambda q: (f"{pp[q]['mu']:.2f}/{pp[q]['d']:.2f}" if q in pp else "")
        L.append(f"| {'|'.join(p['pair'])} | {'COLLAPSE' if p['truth'] else 'KEEP DISTINCT'} | {'COLLAPSE' if p['collapse'] else 'KEEP DISTINCT'} | {'COLLAPSE' if p['collapse_matched'] else 'KEEP DISTINCT'} | {g['c_ij']:.3f}/{g['c_ji']:.3f} | {g['align']:.3f} | {f('1')} | {f('3')} | {f('12')} |")
    L.append(f"\n**E2**: **{'holds' if E2 else 'fails'}**.\n")
    L.append("## Ablations\n")
    misses = {}
    for a in ("A", "B", "C"):
        misses[a] = [c for c in cases if c in by.get(a, {}) and full[c]["correct"] and not by[a][c]["correct"]]
    red_full = sum(redundant_fits(full[c]) for c in cases); red_E = sum(redundant_fits(by["E"][c]) for c in cases if c in by.get("E", {}))
    E3 = all(len(misses[a]) >= 1 for a in ("A", "B", "C")) and red_E >= 1 and red_full == 0
    for a in ("A", "B", "C"): L.append(f"- {a} misses, among the cases the full rule gets right: {', '.join(misses[a]) or 'none'}")
    L.append(f"- redundant fits: full {red_full}, E {red_E}")
    d_agree = [c for c in cases if c in by.get("D", {}) and by["D"][c]["got"] == full[c]["got"]]
    L.append(f"- D agrees with the full rule on {len(d_agree)} of {len(cases)} cases" + (f" (differs on {', '.join(c for c in cases if c not in d_agree)})" if len(d_agree) < len(cases) else ""))
    L.append(f"\n**E3**: **{'holds' if E3 else 'fails'}**.\n")
    L.append("## E4, reported\n")
    L.append("| arm | case | D | D_held | s | tau | kappa | lam_min/|H| | stage | glob. gain | beam | collapsed | fits |"); L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r['abl']} | {r['case']} | {r['D']:.3f} | {r['D_held']:.3f} | {r['stat']:.1e} | {r['tau']:.2f} | {r['kappa']:.1e} | {r['lam_min']:.1e}/{r['hnorm']:.1e} | {r['first_stage']} | {r.get('glob_improvement', float('nan')):.3f} | {' '.join(r.get('beam', []))} | {' '.join(r.get('collapsed', []))} | {r['fits_run']} |")
    L.append("\n### Candidate eta at p = 12 and on the full span, and the fitted candidates (full arm)\n")
    for c in cases:
        r = full[c]
        if "cands" in r:
            L.append(f"- {c}: " + ", ".join(f"{n} {v['eta'].get('12', v['eta'].get(12, 0)):.2f}/{v['eta_full']:.2f}" for n, v in r["cands"].items()) + "; fits: " + ", ".join(f"{n} held {v['D_held']:.3f} J {v['J']:.3f}" for n, v in r["fits"].items()) + f"; J_current {r['J_cur']:.3f}")
    if sweeps:
        L.append("\n### Sweeps\n")
        L.append("| kind | level | case | truth | got | D | D_held | s | stage |"); L.append("|---|---|---|---|---|---|---|---|---|")
        for s in sweeps: L.append(f"| {s['kind']} | {s['level']} | {s['case']} | {s['truth']} | {s['got']}{'' if s['correct'] else ' (miss)'} | {s['D']:.3f} | {s['D_held']:.3f} | {s['stat']:.1e} | {s['first_stage']} |")
        ms = [s for s in sweeps if s["kind"] == "misspec"]; L.append(f"\nMisspecification: {sum(s['correct'] for s in ms)} of {len(ms)} match the bar-defined truth.")
    letter = "A" if (E1 and E2 and E3) else "B" if E1 else "C" if (n_full == 6 and E2) else "D"
    L.append(f"\n## Letter: **{letter}** (E1 {'holds' if E1 else 'fails'}, E2 {'holds' if E2 else 'fails'}, E3 {'holds' if E3 else 'fails'})\n")
    L.append(f"Seconds per arm: {R['seconds']}")
    (OUT / "report.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
