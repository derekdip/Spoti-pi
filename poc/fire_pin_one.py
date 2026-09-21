"""Which of the seven measured constants is correctly identified with a model parameter?

Pinning all seven at once made the fire worse on every scene (`docs/fire-physics-first.md`), while
pinning one of them, `v_rise` at 2.25, had produced the best-looking state in the arc on this same
scene (`docs/fire-height-control.md`). One helped and seven hurt, so the seven cannot be judged
together. This pins each alone, refits everything else, and reports what each one costs or buys.

Scene: `plume`, the reference scene, never scored in any experiment, and the one place a pinned
constant is known to help, so the test can discriminate. `v_rise` is tested at both measured
values, 2.25 (the average front speed over 1.2 to 1.8 m, which the height control used) and 3.47
(the asymptotic speed fitted to the whole front, which the physics-first run used), because the
two disagree and that disagreement is itself part of what is being tested.

Prediction, recorded before the run: fewer than half of the seven improve the correlation on their
own, and `v_rise` at 2.25 is among those that do, replicating the height control. If most improve
individually while all seven together failed, the identifications are individually sound and the
failure was an interaction between them, which would leave the objective question open rather
than settle it against the grammar.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, puffs, rgre_puffs as RP, teacher as TT
from poc.fire_physics_first import measure_constants

SCENE = "plume"


def evaluate(case, st):
    pc = case.per_consumer(st)
    c = case._consumers(st)["visual"]
    corr = float(np.corrcoef(case.target["visual"][case.F // 2:].ravel(), c[case.F // 2:].ravel())[0, 1])
    return dict(error=case.error(st), visual=pc["visual"], corr=corr, live=st.live_count(),
                per_consumer=pc, state={k: getattr(st, k) for k in st.__dataclass_fields__})


def main():
    T0 = time.time()
    const = measure_constants()
    const_v225 = dict(const, v_rise=2.25)
    case = RP.PuffCase(SCENE, getattr(scenes, SCENE)())
    allp = RP.active_params(case)
    print(f"scene {SCENE}: {len(allp)} fittable parameters; constants measured on the reference teacher:")
    for k, v in const.items():
        print(f"   {k:<9} {v:.3f}" + ("   (also tested at 2.25)" if k == "v_rise" else ""))

    res = {"constants": const, "runs": {}}
    x, e, _ = RP.de_fit(RP.BudgetCase(case), puffs.PuffState(), allp)
    free = evaluate(case, RP._vec_to_state(x, allp, puffs.PuffState()))
    res["runs"]["free"] = free
    print(f"\n[{time.time()-T0:5.0f}s] {'free (nothing pinned)':<26} E {free['error']:.4f}  visual {free['visual']:.3f}  "
          f"corr {free['corr']:.2f}  live {free['live']}", flush=True)
    json.dump(res, open("poc/results/pin_one.json", "w"), indent=1)

    trials = [(k, {k: const[k]}) for k in const] + [("v_rise@2.25", {"v_rise": 2.25})]
    print(f"\n{'pinned':<26} {'value':>8} {'E':>8} {'dE':>7} {'visual':>8} {'dvis':>7} {'corr':>6} {'dcorr':>7} {'live':>5}")
    for lab, fix in trials:
        base = puffs.PuffState(**fix)
        names = [n for n in allp if n not in fix]
        x, e, _ = RP.de_fit(RP.BudgetCase(case), base, names)
        r = evaluate(case, RP._vec_to_state(x, names, base))
        res["runs"][lab] = dict(r, pinned=fix)
        v = list(fix.values())[0]
        print(f"{lab:<26} {v:8.3f} {r['error']:8.4f} {(r['error']-free['error'])/free['error']:+6.1%} "
              f"{r['visual']:8.3f} {(r['visual']-free['visual'])/free['visual']:+6.1%} "
              f"{r['corr']:6.2f} {r['corr']-free['corr']:+7.3f} {r['live']:5d}", flush=True)
        json.dump(res, open("poc/results/pin_one.json", "w"), indent=1)

    print(f"\n[{time.time()-T0:.0f}s] VERDICT by the prediction in this file's docstring:")
    helped = [k for k, r in res["runs"].items() if k != "free" and r["corr"] > free["corr"]]
    hurt = [k for k, r in res["runs"].items() if k != "free" and r["corr"] <= free["corr"]]
    print(f"  correlation improved by pinning, alone: {', '.join(helped) or 'none'}")
    print(f"  correlation unchanged or worse:         {', '.join(hurt)}")
    n = len(res["runs"]) - 1
    print(f"  {len(helped)} of {n} identifications improve appearance on their own")
    v225 = res["runs"].get("v_rise@2.25")
    if v225:
        print(f"  v_rise at 2.25 replicates the height control: {'yes' if v225['corr'] > free['corr'] else 'NO'} "
              f"({free['corr']:.2f} -> {v225['corr']:.2f})")
    if len(helped) > n / 2:
        print("  -> identifications are individually sound; the seven-at-once failure was an interaction")
    elif helped:
        print("  -> a minority are sound; the rest are misidentified and the joint failure is explained")
    else:
        print("  -> none are sound on this scene; measured constants do not transfer to token parameters")


if __name__ == "__main__":
    main()
