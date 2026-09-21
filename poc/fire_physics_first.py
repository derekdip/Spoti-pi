"""Fit only what the teacher cannot measure directly, and see whether the fire looks right.

Three places in this arc show the consumer-space RMS objective selecting against appearance: F4's
gusted fits filled the swept envelope with slow cold parcels; F5's look objective tracked the sway
better on seven of nine scenes while losing on total error on eight of nine; and the height control
found that pinning one measured parameter reached a glow correlation of 0.84, the best in the arc,
on 7 parcels, at a total error the fitter scored 14 percent worse and would never have chosen.

So this stops asking the fitter for the parameters the teacher states outright. Seven physical
constants are measured ONCE on `plume`, the reference scene, and applied unchanged everywhere:
peak flame temperature, rise speed, its acceleration, parcel width at birth and its growth, the
cooling time, and the soot load. Nothing is measured per scene. Everything else is fitted as
before, by identical code and settings.

Prediction, recorded before the run: the physics-first fit raises the glow correlation and lowers
the visual consumer error against the free fit on a majority of scenes, and costs total error.
If the correlation does not rise, the objective is not the binding constraint and the grammar is.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP, teacher as TT
from poc.fire_decisions import decisions

REFERENCE = "plume"
SC = ["plume", "gusty", "gust_shelf", "strong_gust", "bed_chain"]
PINNED = ("amp", "v_rise", "accel", "width", "grow", "cool", "soot_amp")


def measure_constants():
    """Seven numbers read off the reference teacher. No consumer error is involved."""
    p, burners, patches, obstacles = getattr(scenes, REFERENCE)()
    rec = TT.run(p, burners, patches, obstacles)
    X, Y = TT._grid(p)
    ex = rec.T - TT.T_AMBIENT
    t = rec.times
    ys = np.arange(p.ny) * p.dx
    amp = float(ex.max())
    # the start-up front: first time each height exceeds the hazard temperature
    hs, ta = [], []
    for h in np.arange(0.2, 1.9, 0.1):
        j = int(round(h / p.dx))
        hit = np.where(ex[:, j, :].max(1) > 107.0)[0]
        if len(hit):
            hs.append(h); ta.append(t[hit[0]])
    hs, ta = np.array(hs), np.array(ta)
    a = ta - ta[0]                                   # age of the front since it passed hs[0]
    y = hs - hs[0]
    # y(a) = v (a - (1 - exp(-k a)) / k); fit v and k by least squares on a grid
    best = (np.inf, 2.0, 2.0)
    for v in np.linspace(0.5, 4.0, 60):
        for k in np.linspace(0.5, 10.0, 60):
            pred = v * (a - (1.0 - np.exp(-k * a)) / k)
            r = float(((pred - y) ** 2).sum())
            if r < best[0]:
                best = (r, v, k)
    _, v_rise, accel = best
    # lateral sigma of the time-mean excess, against height, converted to age at the fitted speed
    late = t >= 1.0
    mean = ex[late].mean(0)
    sig_h = []
    for h in np.arange(0.2, 1.3, 0.1):
        j = int(round(h / p.dx))
        row = np.maximum(mean[j], 0.0)
        if row.sum() > 1:
            xc = (row * X[j]).sum() / row.sum()
            sig_h.append((h, float(np.sqrt((row * (X[j] - xc) ** 2).sum() / row.sum()))))
    hh = np.array([s[0] for s in sig_h]); ss = np.array([s[1] for s in sig_h])
    ages = (hh - hh[0]) / max(v_rise, 1e-3)
    grow, w0 = np.polyfit(ages, ss, 1)
    # cooling: the centreline peak against age at the fitted speed
    prof = ex[late].max(axis=2).mean(axis=0)
    js = [int(round(h / p.dx)) for h in hh]
    vals = prof[js]
    ok = vals > 20
    cool = float(-1.0 / np.polyfit(ages[ok], np.log(vals[ok]), 1)[0])
    soot = float(rec.soot[late].max())
    c = dict(amp=amp, v_rise=float(v_rise), accel=float(accel), width=float(max(w0, 0.02)),
             grow=float(max(grow, 0.0)), cool=float(cool), soot_amp=soot)
    return {k: float(np.clip(v, *RP.RANGES[k])) for k, v in c.items()}


def main():
    T0 = time.time()
    const = measure_constants()
    print("constants measured once on the reference scene `plume`, applied unchanged everywhere:")
    for k, v in const.items():
        print(f"   {k:<9} {v:.3f}")
    prior = {}
    try:
        f5 = json.load(open("poc/results/f5.json"))
        for r in f5["fresh"] + [f5["pilot"]]:
            prior[r["scene"]] = r["fits"][r["best"]]
    except Exception:
        pass
    try:
        hc = json.load(open("poc/results/height_control.json"))
        for nm, v in hc.items():
            prior.setdefault(nm, v["free"])
    except Exception:
        pass
    res = {"constants": const, "scenes": {}}
    print(f"\n{'scene':<13} {'free E':>7} {'phys E':>7} {'free vis':>9} {'phys vis':>9} {'free corr':>10} {'phys corr':>10} {'free n':>7} {'phys n':>7}")
    for nm in SC:
        case = RP.PuffCase(nm, getattr(scenes, nm)())
        base = puffs.PuffState(**const)
        names = [n for n in RP.active_params(case) if n not in PINNED]
        x, e, nev = RP.de_fit(RP.BudgetCase(case), base, names)
        st = RP._vec_to_state(x, names, base)
        pc = case.per_consumer(st)
        c = case._consumers(st)["visual"]
        corr = float(np.corrcoef(case.target["visual"][case.F // 2:].ravel(), c[case.F // 2:].ravel())[0, 1])
        dec = decisions(case, st, as_record=puffs.as_record)
        row = dict(error=case.error(st), per_consumer=pc, corr=corr, live=st.live_count(),
                   n_free=len(names), decisions=dec,
                   state={k: getattr(st, k) for k in st.__dataclass_fields__})
        p0 = prior.get(nm)
        if p0:
            row["free"] = dict(error=p0["error"], visual=p0["per_consumer"]["visual"],
                               corr=p0.get("corr", p0.get("decisions", {}).get("visual", {}).get("late_correlation")),
                               live=p0["live"])
            f = row["free"]
            print(f"{nm:<13} {f['error']:7.3f} {row['error']:7.3f} {f['visual']:9.3f} {pc['visual']:9.3f} "
                  f"{(f['corr'] or float('nan')):10.2f} {corr:10.2f} {f['live']:7d} {row['live']:7d}", flush=True)
        else:
            print(f"{nm:<13} {'-':>7} {row['error']:7.3f} {'-':>9} {pc['visual']:9.3f} {'-':>10} {corr:10.2f} {'-':>7} {row['live']:7d}", flush=True)
        res["scenes"][nm] = row
        json.dump(res, open("poc/results/physics_first.json", "w"), indent=1)
    print(f"\n[{time.time()-T0:.0f}s] VERDICT by the prediction in this file's docstring:")
    up = [nm for nm in SC if "free" in res["scenes"][nm] and res["scenes"][nm]["corr"] > (res["scenes"][nm]["free"]["corr"] or 0)]
    dn = [nm for nm in SC if "free" in res["scenes"][nm] and res["scenes"][nm]["corr"] <= (res["scenes"][nm]["free"]["corr"] or 0)]
    print(f"  correlation rose on {len(up)} of {len(up)+len(dn)}: {', '.join(up) or 'none'}")
    print(f"  correlation fell or held on: {', '.join(dn) or 'none'}")
    vs = [(res["scenes"][nm]["per_consumer"]["visual"] - res["scenes"][nm]["free"]["visual"]) / res["scenes"][nm]["free"]["visual"]
          for nm in SC if "free" in res["scenes"][nm]]
    es = [(res["scenes"][nm]["error"] - res["scenes"][nm]["free"]["error"]) / res["scenes"][nm]["free"]["error"]
          for nm in SC if "free" in res["scenes"][nm]]
    print(f"  median visual error change {np.median(vs):+.1%}, median total error change {np.median(es):+.1%}")
    print(f"  -> {'the objective was the binding constraint' if len(up) > len(dn) else 'the objective is NOT the binding constraint; the grammar is'}")


if __name__ == "__main__":
    main()
