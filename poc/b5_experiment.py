"""Math Track B5: smooth, singular, event decomposition. Implements docs/math-track-b5-prereg.md.

Usage: python poc/b5_experiment.py [--out poc/results] [--quick]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import b2_experiment as b2  # noqa: E402
import b3_experiment as b3  # noqa: E402
import b4_experiment as b4  # noqa: E402
from holdout import parse_model  # noqa: E402
from path_compression import douglas_peucker_3d  # noqa: E402
from reactive.causes import PathToken  # noqa: E402
from reactive.worldlines import corner_tau, dwell_probe, embedded_corner, fresh_family  # noqa: E402

TOLS = np.geomspace(1.0, 0.0001, 48)
SUP = b4.SUP
PRIMARY = (0.00968, 0.01935)
E19 = 0.01935
PEAK = 0.4838
DELTA = 0.25  # s, sample neighbourhood for R3's tolerance tightening
DELTA_M = 0.3  # m, class neighbourhood on the consumer
F_GRID = (0.5, 0.3, 0.2, 0.1, 0.05)
C_GRID = (0.5, 0.71, 1.0, 1.41, 2.0)
TAUS = (0.8, 0.4, 0.2, 0.1, 0.05)
DWELLS = (0.0, 0.5, 1.0, 2.0)
CORNER_PATHS = ("three_corners", "corner_stop_corner", "bend_then_corner", "reversal")
STOP_PATHS = ("corner_stop_corner", "dwell0.5", "dwell1", "dwell2")
PURE_CORNER = ("three_corners", "reversal")


# ---------------------------------------------------------------- classes and masks
def stop_intervals(w):
    still = w.speed <= b2.STOP_SPEED
    edges = np.flatnonzero(still[1:] != still[:-1]) + 1
    bounds = np.concatenate([[0], edges, [len(still)]])
    out = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        if still[a]:
            ta, tb = w.times[a], w.times[min(b, len(w.times) - 1)]
            if tb - ta >= 0.2 and ta >= 0.3 and tb <= w.t_walk - 0.3:
                out.append((int(a), int(b), float(ta), float(tb)))
    return out


def corner_neigh(w):
    """Sample mask of corner intervals widened by DELTA."""
    m = np.zeros(len(w.times), dtype=bool)
    for i0, i1, _ in b3.corners(w):
        lo = np.searchsorted(w.times, w.times[i0] - DELTA)
        hi = np.searchsorted(w.times, w.times[i1 - 1] + DELTA)
        m[lo:hi] = True
    return m


def masks(w, g, scored):
    """Class neighbourhoods on the consumer: a stalk belongs to a class if its foot on the dense path
    (the sample at its pass time) lies within DELTA_M of any sample of that class's interval."""
    tp = g.path_tpass
    idx = np.clip(np.searchsorted(w.times, tp), 0, len(w.times) - 1)
    foot = w.points[idx]
    cm = np.zeros(len(tp), dtype=bool)
    tm = np.zeros(len(tp), dtype=bool)
    for i0, i1, _ in b3.corners(w):
        seg = w.points[i0:i1]
        cm |= np.linalg.norm(foot[:, None, :] - seg[None, :, :], axis=-1).min(1) <= DELTA_M
    for a, b, _, _ in stop_intervals(w):
        seg = w.points[a:b]
        tm |= np.linalg.norm(foot[:, None, :] - seg[None, :, :], axis=-1).min(1) <= DELTA_M
    cm &= scored
    tm &= scored
    sm = scored & ~cm & ~tm
    # control mask: top quartile of |theta'| over moving samples, no widening
    moving = w.speed > b2.STOP_SPEED
    q = np.quantile(np.abs(w.heading_rate[moving]), 0.75) if moving.any() else np.inf
    hot = moving & (np.abs(w.heading_rate) >= q)
    qm = hot[idx] & scored
    return {"S": sm, "C": cm, "T": tm, "Q": qm}


def localise(pred, ref, ms, scored):
    r = (np.linalg.norm(pred - ref, axis=-1) ** 2).sum(0)
    E, n = r[scored].sum(), scored.sum()
    out = {}
    for k, m in ms.items():
        if m.sum() == 0 or E <= 0:
            out[k] = {"share": None, "enrich": None, "n": int(m.sum())}
        else:
            share = float(r[m].sum() / E)
            out[k] = {"share": share, "enrich": float(share / (m.sum() / n)), "n": int(m.sum())}
    return out


# ---------------------------------------------------------------- representations
def tangent_dp(points, times, tangents, moving, tol, forced, dtheta):
    """Spacetime DP with a second refusal criterion on the chord direction (R4)."""
    keep = np.zeros(len(points), dtype=bool)
    keep[0] = keep[-1] = True
    if forced is not None:
        keep[forced] = True
    anchors = np.flatnonzero(keep)
    stack = [(anchors[k], anchors[k + 1]) for k in range(len(anchors) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        u = (times[a + 1:b] - times[a]) / max(times[b] - times[a], 1e-12)
        phat = points[a] + u[:, None] * (points[b] - points[a])
        d = np.linalg.norm(points[a + 1:b] - phat, axis=1) / tol
        chord = points[b] - points[a]
        L = np.linalg.norm(chord)
        if L > 1e-9:
            cdir = chord / L
            cosang = np.clip((tangents[a + 1:b] * cdir[None, :]).sum(1), -1.0, 1.0)
            ang = np.arccos(cosang) / dtheta
            ang = np.where(moving[a + 1:b], ang, 0.0)
        else:
            ang = np.zeros(b - a - 1)
        v = np.maximum(d, ang)
        i = int(np.argmax(v))
        if v[i] > 1.0:
            keep[a + 1 + i] = True
            stack.append((a, a + 1 + i))
            stack.append((a + 1 + i, b))
    return np.flatnonzero(keep)


def dense_tangents(w):
    vel = np.gradient(w.points, w.times, axis=0)
    n = np.linalg.norm(vel, axis=1)
    return vel / np.maximum(n, 1e-9)[:, None]


def vertices(w, rep, tol, param=None, eps=None):
    ones = np.ones(len(w.times))
    stops = b2.event_vertices(w.speed)
    if rep == "R0":
        pts3 = np.concatenate([w.points, np.zeros((len(w.points), 1))], 1)
        return douglas_peucker_3d(pts3, tol)
    if rep == "R1":
        return b2.weighted_time_dp(w.points, w.times, ones, tol, None)
    if rep == "R2":
        return b2.weighted_time_dp(w.points, w.times, ones, tol, stops)
    if rep == "R3":
        wts = np.where(corner_neigh(w), 1.0 / param, 1.0)
        return b2.weighted_time_dp(w.points, w.times, wts, tol, stops)
    if rep == "R4":
        return tangent_dp(w.points, w.times, dense_tangents(w), w.speed > b2.STOP_SPEED, tol, stops, param * eps / PEAK)
    raise ValueError(rep)


# ---------------------------------------------------------------- sweeps
class Run:
    def __init__(self, w, model, tols):
        self.w = w
        self.tols = tols
        self.pos = b4.strip_grid(w)
        times = np.arange(int(w.times[-1] * b2.FPS) + 1) / b2.FPS
        self.cons = b2.Consumer(model, self.pos, times)
        self.ref, g = self.cons.field(w, PathToken(w.points, w.times))
        self.scored = (g.path_dperp < b2.LOCAL_R) & b4.unambiguous(self.pos, w)
        self.masks = masks(w, g, self.scored)
        self.n_event = int(len(b2.event_vertices(w.speed)))
        self.n_interior_events = int(sum(1 for i in b2.event_vertices(w.speed) if 0.3 < w.times[i] < w.t_walk - 0.3))

    def evaluate(self, idx):
        pred, _ = self.cons.field(self.w, PathToken(self.w.points[idx], self.w.times[idx]))
        s, r = b4.errors(pred, self.ref, self.scored)
        return pred, s, r

    def sweep(self, rep, param=None):
        """R4's dtheta depends on the threshold being scored, so R4 is swept once per primary threshold."""
        out = {"rep": rep, "param": param, "N_sup": {}, "loc_at_19": None, "loc_loose": None, "curve": {}}
        eps_list = PRIMARY if rep == "R4" else (None,)
        for eps in eps_list:
            rows = []
            for tol in self.tols:
                idx = vertices(self.w, rep, tol, param, eps)
                pred, s, r = self.evaluate(idx)
                rows.append({"tol": float(tol), "N": int(len(idx)), "sup": s, "rms": r, "idx": idx, "pred": pred})
            targets = [eps] if eps is not None else list(SUP)
            for e in targets:
                out["N_sup"][str(e)] = b4.n_at(rows, e, "sup")[0]
            key = "all" if eps is None else str(eps)
            out["curve"][key] = [{k: v for k, v in r.items() if k not in ("idx", "pred")} for r in rows]
            if eps is None:
                N19, idx19 = b4.n_at(rows, E19, "sup")
                if idx19 is not None:
                    row = next(r for r in rows if r["N"] == N19 and r["sup"] <= E19)
                    out["loc_at_19"] = localise(row["pred"], self.ref, self.masks, self.scored)
                # loosest reachable row, else smallest supremum (M1)
                ok = [r for r in rows if r["sup"] <= SUP[-1]]
                row = min(ok, key=lambda r: r["N"]) if ok else min(rows, key=lambda r: r["sup"])
                out["loc_loose"] = {"N": row["N"], "sup": row["sup"], **localise(row["pred"], self.ref, self.masks, self.scored)}
        return out


def law(w, run, N_straight):
    cs = b3.corners(w)
    dt = w.times[1] - w.times[0]
    turning = float(np.trapezoid(np.abs(w.heading_rate) * (w.speed > 1e-6), dx=dt))
    theta_c = float(sum(th for _, _, th in cs))
    out = {}
    for e in SUP:
        Ns = N_straight.get(str(e))
        if Ns is None:
            out[str(e)] = None
            continue
        corner_term = sum(min(th * PEAK / (2 * e), i1 - i0) for i0, i1, th in cs)
        out[str(e)] = float(Ns + run.n_interior_events + corner_term + (turning - theta_c) * PEAK / (2 * e))
    return out, {"turning": turning, "theta_corners": theta_c, "n_corners": len(cs)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    ap.add_argument("--quick", action="store_true", help="smoke test: 6 tolerances, straight twin only")
    args = ap.parse_args()
    out = Path(args.out)
    tols = np.geomspace(1.0, 0.0001, 6) if args.quick else TOLS
    model = parse_model(json.loads((out / "gpu_sweep.json").read_text())["terms"]["wake + presence"]["description"])
    t0 = time.time()
    res: dict = {"reps": {}, "law": {}, "kin": {}}

    def log(name, r):
        print(f"{name:20s} {r['rep']:3s} f/c={r['param']}  N_sup={r['N_sup']}  loc19={None if r['loc_at_19'] is None else {k: (None if v['share'] is None else round(v['share'], 3)) for k, v in r['loc_at_19'].items()}}  [{time.time() - t0:.0f}s]", flush=True)

    # straight twin
    straight = Run(embedded_corner(8, False), model, tols)
    r = straight.sweep("R2")
    res["reps"]["straight_L8"] = {"R2": r}
    log("straight_L8", r)
    N_straight = r["N_sup"]
    if args.quick:
        print("quick smoke test done")
        return

    # calibration on corner_L8
    probe = Run(embedded_corner(8, True), model, tols)
    res["reps"]["corner_L8"] = {"R2": probe.sweep("R2")}
    log("corner_L8", res["reps"]["corner_L8"]["R2"])
    cal = {"R3": {}, "R4": {}}
    for f in F_GRID:
        r = probe.sweep("R3", f)
        cal["R3"][str(f)] = r["N_sup"]
        log("corner_L8", r)
    for c in C_GRID:
        r = probe.sweep("R4", c)
        cal["R4"][str(c)] = r["N_sup"]
        log("corner_L8", r)

    def pick(table, grid, prefer_large):
        best = None
        for p in grid:
            n = table[str(p)].get(str(E19))
            if n is None:
                continue
            if best is None or n < best[1] or (n == best[1] and ((p > best[0]) == prefer_large)):
                best = (p, n)
        return best
    f_star = pick(cal["R3"], F_GRID, True)
    c_star = pick(cal["R4"], C_GRID, True)
    res["calibration"] = {"R3": cal["R3"], "R4": cal["R4"], "f_star": f_star, "c_star": c_star}
    print(f"calibrated f* = {f_star}, c* = {c_star}", flush=True)
    f_star, c_star = f_star[0], c_star[0]

    # fresh family
    runs = {}
    for w in fresh_family():
        runs[w.name] = Run(w, model, tols)
        res["reps"][w.name] = {}
        for rep, p in (("R1", None), ("R2", None), ("R3", f_star), ("R4", c_star)):
            r = runs[w.name].sweep(rep, p)
            res["reps"][w.name][rep] = r
            log(w.name, r)
        res["law"][w.name], res["kin"][w.name] = law(w, runs[w.name], N_straight)
    # tau series
    for tau in TAUS:
        w = corner_tau(tau)
        runs[w.name] = Run(w, model, tols)
        res["reps"][w.name] = {}
        for rep, p in (("R2", None), ("R3", f_star), ("R4", c_star)):
            r = runs[w.name].sweep(rep, p)
            res["reps"][w.name][rep] = r
            log(w.name, r)
        res["law"][w.name], res["kin"][w.name] = law(w, runs[w.name], N_straight)
    # dwell series
    for D in DWELLS:
        w = dwell_probe(D)
        runs[w.name] = Run(w, model, tols)
        res["reps"][w.name] = {}
        for rep in ("R0", "R1", "R2"):
            r = runs[w.name].sweep(rep)
            res["reps"][w.name][rep] = r
            log(w.name, r)

    # ---------------------------------------------------------------- scoring
    R = res["reps"]

    def N(name, rep, e):
        return R[name][rep]["N_sup"].get(str(e))

    tests = {}
    # M1
    m1 = {}
    for name in STOP_PATHS:
        loc = R[name]["R1"]["loc_loose"]
        m1[name] = None if loc["T"]["enrich"] is None else loc["T"]["enrich"]
    tests["M1"] = {"enrich_T_under_R1": m1, "pass": bool(all(v is not None and v >= 2 for v in m1.values()))}
    # M2
    m2 = {}
    for name in ("three_corners", "reversal", "corner_stop_corner", "bend_then_corner"):
        loc = R[name]["R2"]["loc_at_19"]
        m2[name] = None if loc is None else {"share_C": loc["C"]["share"], "enrich_C": loc["C"]["enrich"], "enrich_Q": loc["Q"]["enrich"]}
    locq = R["tight_slalom"]["R2"]["loc_at_19"]
    m2["tight_slalom"] = None if locq is None else {"share_C": None, "enrich_C": None, "enrich_Q": locq["Q"]["enrich"]}
    tests["M2"] = {"rows": m2, "pass": bool(all(m2[n] is not None and m2[n]["share_C"] is not None and m2[n]["share_C"] >= 0.8 for n in ("three_corners", "reversal", "corner_stop_corner")))}
    # R-stop
    rs = {}
    for name in STOP_PATHS:
        n1, n2 = N(name, "R1", E19), N(name, "R2", E19)
        loc2 = R[name]["R2"]["loc_at_19"]
        enr = None if (loc2 is None or loc2["T"]["enrich"] is None) else loc2["T"]["enrich"]
        ok = (n2 is not None) and ((n1 is None) or n2 <= 0.5 * n1) and (enr is not None and enr < 2)
        rs[name] = {"N_R1": n1, "N_R2": n2, "enrich_T_R2": enr, "pass": bool(ok)}
    tests["R_stop"] = {"rows": rs, "pass": bool(all(v["pass"] for v in rs.values()))}
    # R-corner and R-tangent
    rc, rt = {}, {}
    for name in CORNER_PATHS:
        rc[name], rt[name] = {}, {}
        for e in PRIMARY:
            n2, n3, n4 = N(name, "R2", e), N(name, "R3", e), N(name, "R4", e)
            rc[name][str(e)] = {"N_R2": n2, "N_R3": n3, "pass": None if (n2 is None or n3 is None) else bool(n3 <= 0.9 * n2)}
            rt[name][str(e)] = {"N_R3": n3, "N_R4": n4, "pass": None if (n3 is None or n4 is None) else bool(n4 <= n3)}
    ctrl = {}
    for e in PRIMARY:
        n2, n3, n4 = N("tight_slalom", "R2", e), N("tight_slalom", "R3", e), N("tight_slalom", "R4", e)
        ctrl[str(e)] = {"N_R2": n2, "N_R3": n3, "N_R4": n4, "pass": None if (n2 is None or n4 is None) else bool(n4 <= 0.9 * n2)}
    def allpass(d):
        vals = [v["pass"] for row in d.values() for v in row.values()] if isinstance(next(iter(d.values())), dict) and "pass" not in next(iter(d.values())) else [v["pass"] for v in d.values()]
        return bool(all(v for v in vals if v is not None)), int(sum(v is None for v in vals))
    rc_pass, rc_void = allpass(rc)
    rt_pass, rt_void = allpass(rt)
    ctrl_pass, ctrl_void = allpass(ctrl)
    tests["R_corner"] = {"rows": rc, "void": rc_void, "pass": rc_pass}
    tests["R_tangent"] = {"rows": rt, "control": ctrl, "void": rt_void + ctrl_void, "pass": bool(rt_pass and ctrl_pass)}
    # H4
    h4 = {}
    for tau in TAUS:
        name = f"corner_tau{tau:g}"
        h4[str(tau)] = {rep: (None if (N(name, rep, E19) is None or N_straight.get(str(E19)) is None) else N(name, rep, E19) - N_straight[str(E19)]) for rep in ("R2", "R3", "R4")}
        h4[str(tau)]["cap"] = int(round(200 * tau))
        h4[str(tau)]["law"] = res["law"][name][str(E19)]
    trio = [h4[str(t)]["R2"] for t in (0.8, 0.4, 0.2)]
    ratio = None if any(v is None or v <= 0 for v in trio) else max(trio) / min(trio)
    tests["H4"] = {"N_corner": h4, "ratio_0.8_0.4_0.2": ratio, "pass": bool(ratio is not None and ratio <= 1.5 and all(v is not None and v > 0 for v in [h4[str(t)]["R2"] for t in TAUS]))}
    # H5
    h5 = {"R2": {}, "R0": {}, "R1": {}}
    for D in DWELLS:
        name = f"dwell{D:g}"
        for rep in ("R2", "R0", "R1"):
            h5[rep][str(D)] = {str(e): N(name, rep, e) for e in PRIMARY}
    r2ok = all(h5["R2"][str(D)][str(e)] is not None and h5["R2"]["0"][str(e)] is not None and abs(h5["R2"][str(D)][str(e)] - h5["R2"]["0"][str(e)]) <= 2 for D in DWELLS[1:] for e in PRIMARY)
    n0, n2_ = h5["R0"]["0"][str(E19)], h5["R0"]["2"][str(E19)]
    r0ok = (n0 is not None) and ((n2_ is None) or n2_ >= 2 * n0)
    tests["H5"] = {"table": h5, "R2_flat": bool(r2ok), "R0_grows": bool(r0ok), "pass": bool(r2ok and r0ok)}
    # L
    lrows = {}
    for name in ("three_corners", "reversal", "corner_stop_corner", "bend_then_corner", "tight_slalom"):
        n, nh = N(name, "R2", E19), res["law"][name][str(E19)]
        lrows[name] = {"N": n, "N_hat": nh, "ratio": None if (n is None or nh is None) else n / nh}
    tests["L"] = {"rows": lrows, "pass": bool(all(lrows[n]["ratio"] is not None and 0.67 <= lrows[n]["ratio"] <= 1.5 for n in PURE_CORNER))}
    tests["control_no_corner"] = bool(res["kin"]["tight_slalom"]["n_corners"] == 0)
    core = all(tests[k]["pass"] for k in ("M1", "M2", "R_stop", "R_corner", "H4", "H5"))
    if core:
        verdict = "procedure transfers; " + ("coordinate over class" if tests["R_tangent"]["pass"] else "corner class stands")
    elif tests["M1"]["pass"] and tests["M2"]["pass"] and not tests["R_corner"]["pass"]:
        verdict = "localises but does not repair"
    elif not tests["M2"]["pass"]:
        verdict = "does not localise"
    else:
        verdict = "mixed: " + ", ".join(k for k in ("M1", "M2", "R_stop", "R_corner", "H4", "H5") if not tests[k]["pass"]) + " fail"
    res["tests"] = tests
    res["verdict"] = verdict
    res["N_straight"] = N_straight
    (out / "b5.json").write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    write_md(res, out / "b5.md")
    try:
        make_figure(res, out / "b5.png")
    except Exception as exc:  # noqa: BLE001
        print(f"(figure skipped: {exc})")
    print(json.dumps({k: {kk: vv for kk, vv in tests[k].items() if kk in ("pass", "ratio_0.8_0.4_0.2", "R2_flat", "R0_grows")} for k in tests if isinstance(tests[k], dict)}, indent=1))
    print("verdict:", verdict)
    print(f"wrote {out / 'b5.md'}  [{time.time() - t0:.0f}s]")


def write_md(res, path: Path) -> None:
    t = res["tests"]
    R = res["reps"]
    L = ["# Math Track B5 results: smooth, singular, event decomposition", "", "Preregistration: `docs/math-track-b5-prereg.md`.", "",
         f"Calibration on corner_L8 at 19.35 mm: f* = {res['calibration']['f_star']}, c* = {res['calibration']['c_star']} (grid results in `b5.json`).", "",
         "## N_eps (sup) per trajectory and representation", "", "| trajectory | rep | 4.84 | 9.68 | 19.35 | 38.70 |", "|---|---|---|---|---|---|"]
    for name, reps in R.items():
        for rep, r in reps.items():
            L.append(f"| {name} | {rep} | " + " | ".join(str(r["N_sup"].get(str(e))) for e in SUP) + " |")
    L += ["", "## M1: stop-neighbourhood enrichment under R1 (bar >= 2)", "", "| path | enrichment |", "|---|---|"]
    for k, v in t["M1"]["enrich_T_under_R1"].items():
        L.append(f"| {k} | {'-' if v is None else round(v, 2)} |")
    L += [f"", f"M1 pass {t['M1']['pass']}.", "", "## M2: corner share and enrichment under R2 at N_eps(19.35) (bar: share >= 0.8 on the three pure/mixed corner paths)", "",
          "| path | corner share | corner enrichment | top-quartile |theta'| enrichment |", "|---|---|---|---|"]
    for k, v in t["M2"]["rows"].items():
        if v is None:
            L.append(f"| {k} | void | | |")
        else:
            L.append(f"| {k} | {'-' if v['share_C'] is None else round(v['share_C'], 3)} | {'-' if v['enrich_C'] is None else round(v['enrich_C'], 2)} | {'-' if v['enrich_Q'] is None else round(v['enrich_Q'], 2)} |")
    L += ["", f"M2 pass {t['M2']['pass']}.", "", "## R-stop (bar: N(R2) <= 0.5 N(R1) at 19.35 mm and stop enrichment under R2 < 2)", "", "| path | N R1 | N R2 | enrichment R2 | pass |", "|---|---|---|---|---|"]
    for k, v in t["R_stop"]["rows"].items():
        L.append(f"| {k} | {v['N_R1']} | {v['N_R2']} | {'-' if v['enrich_T_R2'] is None else round(v['enrich_T_R2'], 2)} | {v['pass']} |")
    L += ["", f"R-stop pass {t['R_stop']['pass']}.", "", "## R-corner and R-tangent (primaries 9.68 and 19.35 mm)", "", "| path | eps | N R2 | N R3 | N R4 | R3 <= 0.9 R2 | R4 <= R3 |", "|---|---|---|---|---|---|---|"]
    for name in CORNER_PATHS:
        for e in PRIMARY:
            a, b = t["R_corner"]["rows"][name][str(e)], t["R_tangent"]["rows"][name][str(e)]
            L.append(f"| {name} | {e*1000:.2f} | {a['N_R2']} | {a['N_R3']} | {b['N_R4']} | {a['pass']} | {b['pass']} |")
    for e in PRIMARY:
        c = t["R_tangent"]["control"][str(e)]
        L.append(f"| tight_slalom (control) | {e*1000:.2f} | {c['N_R2']} | {c['N_R3']} | {c['N_R4']} | (R3 = R2) | R4 <= 0.9 R2: {c['pass']} |")
    L += ["", f"R-corner pass {t['R_corner']['pass']} (void cells {t['R_corner']['void']}); R-tangent pass {t['R_tangent']['pass']} (void cells {t['R_tangent']['void']}).", "",
          "## H4: N_corner(tau) at 19.35 mm (R2; also R3, R4), the sampling cap and the tangent law", "", "| tau (s) | R2 | R3 | R4 | cap 200 tau | law N_hat - N_straight |", "|---|---|---|---|---|---|"]
    ns = res["N_straight"].get(str(E19))
    for tau in TAUS:
        v = t["H4"]["N_corner"][str(tau)]
        lawv = None if (v["law"] is None or ns is None) else round(v["law"] - ns, 1)
        L.append(f"| {tau} | {v['R2']} | {v['R3']} | {v['R4']} | {v['cap']} | {lawv} |")
    L += ["", f"H4 ratio over 0.8/0.4/0.2 = {t['H4']['ratio_0.8_0.4_0.2']}; pass {t['H4']['pass']}.", "", "## H5: dwell series", "", "| D (s) | R2 9.68 | R2 19.35 | R0 9.68 | R0 19.35 | R1 9.68 | R1 19.35 |", "|---|---|---|---|---|---|---|"]
    for D in DWELLS:
        h = t["H5"]["table"]
        L.append(f"| {D:g} | " + " | ".join(str(h[rep][str(D)][str(e)]) for rep in ("R2", "R0", "R1") for e in PRIMARY) + " |")
    L += ["", f"H5: R2 flat {t['H5']['R2_flat']}, R0 grows {t['H5']['R0_grows']}, pass {t['H5']['pass']}.", "", "## L: parameter-free tangent law at 19.35 mm", "", "| path | N | N_hat | N / N_hat |", "|---|---|---|---|"]
    for k, v in t["L"]["rows"].items():
        L.append(f"| {k} | {v['N']} | {'-' if v['N_hat'] is None else round(v['N_hat'], 1)} | {'-' if v['ratio'] is None else round(v['ratio'], 2)} |")
    L += ["", f"L pass (three_corners, reversal within [0.67, 1.5]) {t['L']['pass']}. Negative control has no corner: {t['control_no_corner']}.", "", f"## Verdict: {res['verdict']}", ""]
    path.write_text("\n".join(L) + "\n")


def make_figure(res, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = res["tests"]
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    ax = axes[0, 0]
    names = list(t["M2"]["rows"].keys())
    ax.bar(range(len(names)), [(t["M2"]["rows"][n] or {}).get("enrich_C") or 0 for n in names], 0.4, label="corner neighbourhood")
    ax.bar(np.arange(len(names)) + 0.4, [(t["M2"]["rows"][n] or {}).get("enrich_Q") or 0 for n in names], 0.4, label="top-quartile |theta'|")
    ax.set_xticks(np.arange(len(names)) + 0.2); ax.set_xticklabels(names, rotation=30, fontsize=8); ax.set_ylabel("residual enrichment under R2"); ax.set_title("M2: where the smooth-only residual lives"); ax.legend(fontsize=8)
    ax = axes[0, 1]
    names = list(t["M1"]["enrich_T_under_R1"].keys())
    ax.bar(range(len(names)), [t["M1"]["enrich_T_under_R1"][n] or 0 for n in names], color="C3")
    ax.axhline(2, color="k", ls=":"); ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=30, fontsize=8); ax.set_title("M1: stop enrichment without stop events")
    ax = axes[0, 2]
    x = np.arange(len(CORNER_PATHS) + 1)
    for k, rep in enumerate(("R2", "R3", "R4")):
        vals = []
        for n in CORNER_PATHS:
            vals.append(res["reps"][n][rep]["N_sup"].get(str(E19)) or 0)
        vals.append(res["reps"]["tight_slalom"][rep]["N_sup"].get(str(E19)) or 0)
        ax.bar(x + 0.25 * k, vals, 0.25, label=rep)
    ax.set_xticks(x + 0.25); ax.set_xticklabels(list(CORNER_PATHS) + ["tight_slalom"], rotation=30, fontsize=8); ax.set_ylabel("N at 19.35 mm"); ax.set_title("R-corner / R-tangent"); ax.legend(fontsize=8)
    ax = axes[1, 0]
    for rep, st in (("R2", "ko-"), ("R3", "C1s-"), ("R4", "C0^-")):
        ax.plot(TAUS, [t["H4"]["N_corner"][str(tau)][rep] or np.nan for tau in TAUS], st, label=rep)
    ax.plot(TAUS, [t["H4"]["N_corner"][str(tau)]["cap"] for tau in TAUS], "k:", label="sampling cap")
    ns = res["N_straight"].get(str(E19))
    ax.plot(TAUS, [(t["H4"]["N_corner"][str(tau)]["law"] or np.nan) - (ns or 0) for tau in TAUS], "C2--", label="tangent law")
    ax.set_xscale("log"); ax.set_xlabel("corner duration tau (s)"); ax.set_ylabel("vertices attributed to the corner"); ax.set_title("H4: singular mass vs sharpness"); ax.legend(fontsize=8)
    ax = axes[1, 1]
    h = t["H5"]["table"]
    for rep, st in (("R2", "ko-"), ("R0", "C3s-"), ("R1", "C7^-")):
        ax.plot(DWELLS, [h[rep][str(D)][str(E19)] or np.nan for D in DWELLS], st, label=rep)
    ax.set_xlabel("dwell D (s)"); ax.set_ylabel("N at 19.35 mm"); ax.set_title("H5: dwell as an event coordinate"); ax.legend(fontsize=8)
    ax = axes[1, 2]
    rows = t["L"]["rows"]
    for n, v in rows.items():
        if v["N"] is not None and v["N_hat"] is not None:
            ax.scatter(v["N_hat"], v["N"]); ax.annotate(n, (v["N_hat"], v["N"]), fontsize=8, xytext=(3, 3), textcoords="offset points")
    m = max([v["N"] or 0 for v in rows.values()] + [v["N_hat"] or 0 for v in rows.values()]) * 1.1
    ax.plot([0, m], [0, m], "k--", lw=0.8); ax.plot([0, m], [0, 1.5 * m], "k:", lw=0.6); ax.plot([0, m], [0, m / 1.5], "k:", lw=0.6)
    ax.set_xlabel("N_hat (parameter-free tangent law)"); ax.set_ylabel("N at 19.35 mm (R2)"); ax.set_title("L")
    fig.tight_layout(); fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
