"""Is plume height the visual defect, or is that another mirage? A controlled A/B.

F5's control showed its own premise was wrong: the sway law it replaced swayed better, and the
visual defect was attributed to height instead, on the strength of fitted rise speeds near
0.5 m/s against a measured front speed of 2.25 and pictures of a leaning stub. That is the same
kind of evidence the sway claim had before a control overturned it, so it gets the same test
before any round is built on it.

Prediction, recorded before the run: if height is the defect, pinning `v_rise` to the measured
2.25 m/s and refitting everything else lowers the VISUAL consumer error, even if the total error
rises. If the visual error does not move, the diagnosis is wrong and the grammar is at its limit.

Scenes: `gusty` (F5's declared-seen pilot) and `plume` (never scored anywhere; used only for the
teacher probes). No scored scene is touched. Fit settings are F5's verbatim.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP, teacher as TT

PINNED_V = 2.25          # m/s, the teacher's measured start-up front speed (poc/results/puff_probe.log)
SC = ("gusty", "plume")


def visible_height(rec, thresh=0.05):
    """Highest row whose coarse glow exceeds a fraction of the teacher's own peak, per frame."""
    g = TT.g_visual(rec)
    ny = g.shape[1]
    ys = (np.arange(ny) + 0.5) * 4 * rec.p.dx
    out = []
    for f in range(g.shape[0]):
        rows = np.where(g[f].max(1) > thresh)[0]
        out.append(ys[rows.max()] if len(rows) else 0.0)
    return np.array(out)


def main():
    T0 = time.time()
    res = {}
    for nm in SC:
        case = RP.PuffCase(nm, getattr(scenes, nm)())
        scale = float(TT.g_visual(TT.run(case.p, case.burners, case.patches, case.obstacles)).max())
        th = 0.05 * scale
        t_rec = TT.run(case.p, case.burners, case.patches, case.obstacles)
        t_h = visible_height(t_rec, th)
        names = RP.active_params(case)
        free_names = names
        pin_names = [n for n in names if n != "v_rise"]
        print(f"\n{nm}: teacher visible plume height {t_h.mean():.2f} m mean, {t_h.max():.2f} m max "
              f"({len(names)} free parameters)", flush=True)
        res[nm] = dict(teacher_height_mean=float(t_h.mean()), teacher_height_max=float(t_h.max()))
        for lab, nmz, base in (("free", free_names, puffs.PuffState()),
                               ("v_rise pinned to 2.25", pin_names, puffs.PuffState(v_rise=PINNED_V))):
            x, e, nev = RP.de_fit(RP.BudgetCase(case), base, nmz)
            st = RP._vec_to_state(x, nmz, base)
            pc = case.per_consumer(st)
            rec = puffs.as_record(st, case.p, case.times, case.burners, case.patches, case.obstacles)
            m_h = visible_height(rec, th)
            c = case._consumers(st)["visual"]
            corr = float(np.corrcoef(case.target["visual"][case.F // 2:].ravel(), c[case.F // 2:].ravel())[0, 1])
            res[nm][lab] = dict(error=case.error(st), per_consumer=pc, corr=corr, live=st.live_count(),
                                v_rise=st.v_rise, height_mean=float(m_h.mean()), height_max=float(m_h.max()),
                                state={k: getattr(st, k) for k in st.__dataclass_fields__})
            print(f"[{time.time()-T0:5.0f}s]  {lab:<22} E {case.error(st):.4f}  visual {pc['visual']:.3f}  "
                  f"corr {corr:.2f}  height {m_h.mean():.2f} m (teacher {t_h.mean():.2f})  "
                  f"v_rise {st.v_rise:.2f}  live {st.live_count()}", flush=True)
            json.dump(res, open("poc/results/height_control.json", "w"), indent=1)
    print("\nVERDICT by the prediction recorded in this file's docstring:")
    for nm in SC:
        f, p = res[nm]["free"], res[nm]["v_rise pinned to 2.25"]
        dv = (p["per_consumer"]["visual"] - f["per_consumer"]["visual"]) / f["per_consumer"]["visual"]
        dh = p["height_mean"] - f["height_mean"]
        print(f"  {nm}: visual error {dv:+.1%} when the rise speed is pinned, plume height {dh:+.2f} m "
              f"(teacher is {res[nm]['teacher_height_mean'] - f['height_mean']:+.2f} m above the free fit)")
        print(f"      -> {'height helps: the diagnosis holds' if dv < -0.02 else 'height does NOT help: the diagnosis fails'}")


if __name__ == "__main__":
    main()
