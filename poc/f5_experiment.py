"""F5: does the quasi-static sway law make the cheap fire follow a gust? Prereg: docs/math-track-f5-prereg.md.

Five fresh scenes the puff grammar has never been fitted to, four F4 scenes re-measured as a
paired before-and-after (declared seen), and one transfer test in which a state fitted on the
pilot is applied unchanged to two scenes where only the cause differs.

Per scene: the V0 error; a floor fit under the four standard consumers with the parcel budget in
the objective; the same under the tone-mapped look consumer; both states cross-evaluated on the
unpenalised standard error with the better kept; sway amplitude and phase against the teacher;
decision rates; glow correlation; parcels. Every number is saved as it is produced.
"""
from __future__ import annotations

import json, sys, time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poc.fire import scenes, puffs, rgre_puffs as RP
from poc.fire_decisions import decisions
from poc.rgre.core import diagnose, select_projection

NO_GATE = 1.01
DEAD = 0.01
STEPS = 10
FRESH = ["gust_shelf", "fast_gust", "strong_gust", "gust_twin", "bed_chain"]
PAIRED = ["ignition", "full", "windy"]
TRANSFER = ["fast_gust", "strong_gust"]
OUT = "poc/results/f5.json"


def sway(case, st=None):
    """0.7-Hz-band sway of the coarse-glow centroid: amplitude in metres and phase in radians.

    Measured at the scene's own gust frequency, which is a property of the cause. `st=None` gives
    the teacher's own sway, so the two are measured by identical code.
    """
    hz = case.p.gust_hz
    w = 2.0 * np.pi * hz
    g = case.target["visual"] if st is None else case._consumers(st)["visual"]
    nx = case.p.nx // 4
    G = np.asarray(g, float).reshape(case.F, -1, nx)
    xs = (np.arange(nx) + 0.5) * 4 * case.p.dx
    m = G.sum((1, 2))
    xc = (G.sum(1) * xs[None]).sum(1) / np.maximum(m, 1e-9)
    t = case.times
    late = t >= 1.0
    M = np.stack([np.ones(int(late.sum())), np.sin(w * t[late]), np.cos(w * t[late])], 1)
    c, *_ = np.linalg.lstsq(M, xc[late], rcond=None)
    return float(np.hypot(c[1], c[2])), float(np.arctan2(-c[2], c[1]))


def score(case, st, t_sway):
    dec = decisions(case, st, as_record=puffs.as_record)
    A, ph = sway(case, st)
    dphi = float(np.degrees(np.abs(np.angle(np.exp(1j * (ph - t_sway[1]))))))
    return dict(error=case.error(st), per_consumer=case.per_consumer(st), live=st.live_count(),
                sway_amp=A, sway_ratio=A / max(t_sway[0], 1e-9), sway_phase_err=dphi,
                decisions=dec, state={k: getattr(st, k) for k in st.__dataclass_fields__})


def greedy(case, v0, log):
    st, e0 = v0, case.error(v0)
    rec = dict(steps=[], traj=[e0])
    blacklist, stopped = [], "budget"
    for step in range(STEPS):
        t0 = time.time()
        diag = diagnose(case.residual(st), case.tangents(st), case.templates(), support=RP.SUPPORT_CLASSES)
        if diag is None:
            stopped = "no residual"; break
        pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in RP.CLASSES},
                                              unrepairable=RP.UNREPAIRABLE, blacklist=blacklist)
        evaluated, chosen, g = 0, None, None
        while pick is not None:
            evaluated += 1
            g = RP.repair_gain(case, st, pick)
            if g["drop"] >= DEAD * g["e0"]:
                chosen = pick; break
            blacklist.append(pick)
            pick, why, ranked = select_projection(diag, NO_GATE, {c: [c] for c in RP.CLASSES},
                                                  unrepairable=RP.UNREPAIRABLE, blacklist=blacklist)
        s = dict(step=step, q_perp=diag["q_perp"], ranked=ranked[:4], picked=chosen,
                 evaluated=evaluated, seconds=round(time.time() - t0, 1))
        if chosen is None:
            rec["steps"].append(s); stopped = "exhausted"; break
        s.update(e_before=g["e0"], e_after=g["e1"], dcost=g["dcost"])
        st = g["state"]
        rec["traj"].append(g["e1"]); rec["steps"].append(s)
        log(f"   step {step}: pick {chosen:<8} E {g['e0']:.4f}->{g['e1']:.4f} ({evaluated} tried) {s['seconds']}s")
    rec.update(stopped=stopped, e_final=case.error(st), per_consumer=case.per_consumer(st),
               state={k: getattr(st, k) for k in st.__dataclass_fields__})
    return rec


def run_scene(nm, log, do_greedy=True):
    case = RP.PuffCase(nm, getattr(scenes, nm)())
    look = RP.LookCase(case)
    v0 = puffs.PuffState()
    t_sway = sway(case, None)
    rec = dict(scene=nm, consumers=case.names, e_v0=case.error(v0), gust_hz=case.p.gust_hz,
               gust_amp=case.p.gust_amp, teacher_sway=t_sway[0], fits={})
    log(f"{nm}: V0 {rec['e_v0']:.4f}, teacher sway {100*t_sway[0]:.1f} cm at {case.p.gust_hz} Hz")
    for lab, c in (("standard", case), ("look", look)):
        t0 = time.time()
        st, e, names, spread = RP.floor_fit(RP.BudgetCase(c), v0, maxfev_per_dim=40, verbose=False)
        sc = score(case, st, t_sway)
        sc.update(fit_objective=e, spread=spread, n_params=len(names), seconds=round(time.time() - t0))
        rec["fits"][lab] = sc
        d = sc["decisions"]
        log(f"{nm} {lab:<8} fit {e:.4f} ({', '.join(f'{k} {v:.3f}' for k, v in spread.items())}) -> linear {sc['error']:.4f} "
            f"live {sc['live']} sway {100*sc['sway_amp']:.1f} cm ({sc['sway_ratio']:.0%}) phase err {sc['sway_phase_err']:.0f} deg {sc['seconds']}s")
        log(f"{nm} {lab:<8} " + ", ".join(f"{k} {v:.3f}" for k, v in sc["per_consumer"].items())
            + f" | heat wrong {100*d['heat']['disagree']:.1f}% ai wrong {100*d['ai']['disagree']:.1f}% "
            + (f"alight missed {100*d['ignition']['missed_alight']:.1f}% " if "ignition" in d else "")
            + f"corr {d['visual']['late_correlation']:.2f}")
    best = min(rec["fits"], key=lambda k: rec["fits"][k]["error"])
    rec["best"] = best
    log(f"{nm}: cross-evaluated best is the {best} fit at {rec['fits'][best]['error']:.4f}")
    if do_greedy:
        t0 = time.time()
        rec["greedy"] = greedy(RP.BudgetCase(case), v0, log)
        rec["greedy"]["seconds"] = round(time.time() - t0)
        g = rec["greedy"]
        log(f"{nm}: greedy {g['e_final']:.4f} after {len(g['steps'])} steps ({g['stopped']}), "
            f"{(rec['e_v0'] - g['e_final']) / max(rec['e_v0'] - rec['fits'][best]['error'], 1e-9):.3f} of the floor's reduction")
    rec["evals"] = case.evals
    return rec


def transfer(source_state, log):
    """One state, fitted on the pilot, applied unchanged where only the cause differs."""
    out = []
    st = puffs.PuffState(**source_state)
    for nm in TRANSFER:
        case = RP.PuffCase(nm, getattr(scenes, nm)())
        t_sway = sway(case, None)
        sc = score(case, st, t_sway)
        sc.update(scene=nm, gust_hz=case.p.gust_hz, gust_amp=case.p.gust_amp,
                  teacher_sway=t_sway[0], e_v0=case.error(puffs.PuffState()))
        out.append(sc)
        log(f"transfer -> {nm}: teacher sway {100*t_sway[0]:.1f} cm at {case.p.gust_hz} Hz, "
            f"model {100*sc['sway_amp']:.1f} cm ({sc['sway_ratio']:.0%}) phase err {sc['sway_phase_err']:.0f} deg, "
            f"E {sc['error']:.4f} (V0 {sc['e_v0']:.4f}) corr {sc['decisions']['visual']['late_correlation']:.2f}")
    return out


def main():
    out = dict(fresh=[], paired=[], transfer=[], started=time.strftime("%Y-%m-%d %H:%M:%S"))
    T0 = time.time()
    def log(msg):
        print(f"[{time.time()-T0:6.0f}s] {msg}", flush=True)
    pilot = run_scene("gusty", log)
    out["pilot"] = pilot
    json.dump(out, open(OUT, "w"), indent=1)
    out["transfer"] = transfer(pilot["fits"][pilot["best"]]["state"], log)
    json.dump(out, open(OUT, "w"), indent=1)
    for nm in FRESH:
        out["fresh"].append(run_scene(nm, log))
        json.dump(out, open(OUT, "w"), indent=1)
    for nm in PAIRED:
        out["paired"].append(run_scene(nm, log, do_greedy=False))
        json.dump(out, open(OUT, "w"), indent=1)
    out["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(out, open(OUT, "w"), indent=1)
    log("done")


if __name__ == "__main__":
    main()
