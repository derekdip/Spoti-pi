"""G14 frozen scorer. Committed with the preregistration, run once. Two bars, K8 (composition) and K9
(a removed arm needs no edit); the one-arm crawl (K10) and the growth on the four bodies (K11) reported."""
from __future__ import annotations
import json, sys
import numpy as np

INTACT_CLIP_RUNS = 0.511          # the intact teacher's own clip against its other two runs, mean (G13 prereg)
CRAWL_LOOP_RUNS = 0.568           # the legless teacher's own loop against its other two runs, mean (G13 prereg)
BASE = ("rhythm", "legs", "lateral", "torso", "arms")


def main(path):
    d = json.load(open(path)); C = {c["case"]: c for c in d["cases"] if c["group"] != "pilot"}; comp = d["compositions"]
    out = []; P = lambda *a: out.append(" ".join(str(x) for x in a))
    fmt = lambda added: [f"{a}{s:+d}" if s else a for a, s in added]
    P(f"# G14 scored: {len(C)} growth cases, {len(comp)} bodies with compositions, {d['STEPS']} steps, grounding {d['GROUNDING']}\n")
    # ---- K8 composition: on each combined body, the composed no-fit edit against the raw clip on every run, and against the fresh growth's held-out terminal
    P("## K8 composition: the composed edit below the raw clip on >= 2 of 3 runs, and its mean over the held-out runs (1, 2) within 1.25 of the fresh growth's held-out terminal, on both combined bodies")
    k8 = True
    for morph, key in (("locked_knee_left+weak_hip_right", "composed"), ("locked_knee_left+noarm_right", "locked knee edit (G13 locked_knee_left_s0), arm dropped")):
        e = comp[morph]; raw = e[[k for k in e if k.startswith("raw")][0]]["errors"]; cm = e[key]["errors"]
        below = sum(a < b for a, b in zip(cm, raw)); ho = float(np.mean(cm[1:])); fresh = C[f"{morph}_s0"]["e_final_heldout"]
        ok = below >= 2 and ho <= 1.25 * fresh; k8 = k8 and ok
        P(f"  {morph:<32} raw " + " ".join(f"{v:.3f}" for v in raw) + " | composed " + " ".join(f"{v:.3f}" for v in cm) + f" ({below} of 3 below) | held-out mean {ho:.3f} vs fresh growth {fresh:.3f} (x1.25 = {1.25*fresh:.3f}) -> {'ok' if ok else 'MISS'}")
        for label, v in e.items():
            if label != key and not label.startswith("raw"):
                P(f"      {label:<58} " + " ".join(f"{x:.3f}" for x in v["errors"]))
    P(f"-> K8 {'pass' if k8 else 'FAIL'}\n")
    # ---- K9 a removed arm needs no edit
    P("## K9 a removed arm: the raw intact clip with the arm dropped against the one-arm teacher's runs within 1.2 of the intact clip's own run-to-run error (0.511) on >= 2 of 3 runs, and the growth adds no impairment edit")
    raw = comp["noarm_left"]["raw clip (arm dropped)"]["errors"]; within = sum(v <= 1.2 * INTACT_CLIP_RUNS for v in raw)
    imps = [e for e in C["noarm_left_s0"]["added"] if e[0] not in BASE]
    k9 = within >= 2 and not imps
    P(f"  raw clip errors " + " ".join(f"{v:.3f}" for v in raw) + f" ({within} of 3 within {1.2*INTACT_CLIP_RUNS:.3f}); growth added {fmt(C['noarm_left_s0']['added'])} (impairments {fmt(imps)})")
    P(f"-> K9 {'pass' if k9 else 'FAIL'}\n")
    # ---- K10 reported: the one-arm crawl
    P("## K10 (reported) the one-arm crawl: the legless body's loop with the arm dropped against the one-arm teacher's runs, the crawl's own run-to-run error (0.568), and the growth on the loop")
    raw = comp["nolegs+noarm_left"]["raw crawl loop (arm dropped)"]; c = C["nolegs+noarm_left_s0"]
    P(f"  raw loop errors " + " ".join(f"{v:.3f}" for v in raw["errors"]) + f" (crawl's own runs {CRAWL_LOOP_RUNS}); speed {raw['speed']:.2f}/{raw['speed_teacher']:.2f}; growth {fmt(c['added'])} fit {c['e_v0']:.3f} -> {c['e_final']:.3f}, held-out {c['e_v0_heldout']:.3f} -> {c['e_final_heldout']:.3f}\n")
    # ---- K11 reported: the growth on the four bodies
    P("## K11 (reported) the growth on each body: held-out error V0 -> terminal per run, edits, speed and airborne against the teacher")
    for name, c in C.items():
        P(f"  {name:<36} base {c['base']:<7} fit {c['e_v0']:.3f} -> {c['e_final']:.3f} | held-out " + ", ".join(f"{v:.3f}->{a:.3f}" for v, a in zip(c['e_v0_heldout_runs'], c['e_final_heldout_runs'])) + f" | edits {fmt(c['added'])}; rejections {sum(len(s['rejected']) for s in c['steps'])}")
    gen = sum(c["e_final_heldout"] < c["e_v0_heldout"] for c in C.values())
    P(f"  held-out mean below V0's on {gen} of {len(C)}")
    for morph, e in comp.items():
        for label, v in e.items():
            P(f"  {morph:<32} {label:<58} speed {v['speed']:.2f}/{v['speed_teacher']:.2f} airborne {v['airborne']:.2f}/{v['airborne_teacher']:.2f}")
    letter = "A" if (k8 and k9) else ("B" if k8 else ("C" if k9 else "D"))
    P(f"\n## Outcome (frozen tree): K8 {'pass' if k8 else 'fail'}, K9 {'pass' if k9 else 'fail'} -> {letter}; K10, K11 reported")
    text = "\n".join(out); print(text); return text


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "poc/results/g14.json")
