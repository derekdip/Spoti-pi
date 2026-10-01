"""Math Track B0, item 18: sweep behavioural tolerance and look for the knee.

Convention: expectation over recorded inputs (training walk and held-out walk,
averaged), three consumers:
  visual   per-stalk relative RMS of bend (the strictest consumer)
  ai       relative RMS of the 16x16 coarse field (mean |bend| per cell, per frame)
  gameplay 1 - correlation of the late-phase coarse fields (can the trail be found)
Cost is machine-independent ops per stalk per frame from the existing cost model
(bake costs amortised over the stalk count).

Sweeps:
  A. representations: field-only at several grids, wake only, wake + presence,
     wake + presence + radial impulse (subset of the joint six-term fit, not refit),
     full six-term grammar, and the teacher itself (error 0).
  B. liveness threshold eps: live radial-impulse tokens per frame and the error
     when tokens below eps are dropped. Prediction: N_live ~ (R / lambda') log(1/eps).
  C. path polyline tolerance delta (Douglas-Peucker on the dense path): points kept
     and excess error. Prediction: N_points ~ delta^{-1/2}, excess error ~ delta.

Usage: python poc/knee_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout import parse_model  # noqa: E402
from reactive import primitives  # noqa: E402
from reactive.causes import PathToken, bank_path, emit_stride_events, holdout_walk, s_curve_walk  # noqa: E402
from reactive.field import bake_and_sample  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.metrics import coarse_corr, coarse_rel_rmse, rel_rmse  # noqa: E402
from reactive.model import CheapModel  # noqa: E402
from reactive.primitives import spring_response  # noqa: E402
from reactive.teacher import TeacherParams, run_teacher  # noqa: E402

TEACHER_OPS = 320.0  # per stalk per frame, plus 4 neighbour reads per substep


def consumers(pred, ref, pos, late, extent):
    return {"visual": rel_rmse(pred, ref),
            "ai": coarse_rel_rmse(pred, ref, pos, 16, extent),
            "gameplay": 1.0 - coarse_corr(pred[late], ref[late], pos, 16, extent)}


def douglas_peucker(points: np.ndarray, tol: float) -> np.ndarray:
    """Indices of the polyline simplification of `points` within `tol` (recursive)."""
    keep = np.zeros(len(points), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        seg = points[b] - points[a]
        L = np.linalg.norm(seg)
        rel = points[a + 1:b] - points[a]
        if L < 1e-12:
            d = np.linalg.norm(rel, axis=1)
        else:
            d = np.abs(rel[:, 0] * seg[1] - rel[:, 1] * seg[0]) / L
        i = int(np.argmax(d))
        if d[i] > tol:
            keep[a + 1 + i] = True
            stack.append((a, a + 1 + i))
            stack.append((a + 1 + i, b))
    return np.flatnonzero(keep)


class Walk:
    def __init__(self, path, tp):
        self.path = path
        self.rec = run_teacher(path, tp)
        self.events = emit_stride_events(path, stride=0.5)
        self.ptoken = bank_path(path, hz=20.0)
        self.geom = build_geometry(self.rec.pos, self.events, self.ptoken, path)
        self.late = self.rec.times >= path.t_walk + 1.0
        self.extent = tp.extent

    def score_direct(self, model):
        pred, cost = model.evaluate(self.geom, self.rec.times)
        return consumers(pred, self.rec.bend, self.rec.pos, self.late, self.extent), cost

    def score_baked(self, model, grid):
        s, cost = bake_and_sample(model, self.rec.pos, self.rec.times, grid, self.extent, self.events, self.ptoken, self.path)
        return consumers(s, self.rec.bend, self.rec.pos, self.late, self.extent), cost

    def score_with_path(self, model, ptoken):
        g = build_geometry(self.rec.pos, self.events, ptoken, self.path)
        pred, cost = model.evaluate(g, self.rec.times)
        return consumers(pred, self.rec.bend, self.rec.pos, self.late, self.extent), cost


def mean_scores(a, b):
    return {k: 0.5 * (a[k] + b[k]) for k in a}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    six = parse_model(json.loads((out / "summary.json").read_text())["model"]["description"])
    sweep = json.loads((out / "gpu_sweep.json").read_text())
    two = parse_model(sweep["terms"]["wake + presence"]["description"])
    one = parse_model(sweep["terms"]["wake only"]["description"])
    three = CheapModel([t for t in six.terms if t.prim.name in ("wake", "presence", "radial_impulse")])

    tp = TeacherParams()
    walks = {"training": Walk(s_curve_walk(t_total=tp.duration), tp),
             "held-out": Walk(holdout_walk(t_total=tp.duration), tp)}
    print("teachers ready")

    # ---------------- A. representations ----------------
    reps = []

    def add(name, kind, scorer, cost_override=None):
        per = {w: scorer(walk) for w, walk in walks.items()}
        cost = cost_override if cost_override is not None else float(np.mean([per[w][1] for w in per]))
        row = {"name": name, "kind": kind, "cost": cost,
               "mean": mean_scores(per["training"][0], per["held-out"][0]),
               "training": per["training"][0], "held-out": per["held-out"][0]}
        reps.append(row)
        print(f"  {name:38s} cost {cost:7.1f}  visual {row['mean']['visual']:.3f}  ai {row['mean']['ai']:.3f}  gameplay {row['mean']['gameplay']:.3f}")

    print("A. representations")
    for grid in (8, 10, 16, 20, 25, 32, 40, 64):
        add(f"field only, {grid}x{grid} (wake+presence baked)", "field", lambda w, g=grid: w.score_baked(two, g))
    add("path only (wake)", "direct", lambda w: w.score_direct(one))
    add("path + local kernels (wake + presence)", "direct", lambda w: w.score_direct(two))
    add("path + local + event residuals (subset of six)", "direct", lambda w: w.score_direct(three))
    add("full grammar (six terms)", "direct", lambda w: w.score_direct(six))
    reps.append({"name": "teacher itself", "kind": "teacher", "cost": TEACHER_OPS,
                 "mean": {"visual": 0.0, "ai": 0.0, "gameplay": 0.0},
                 "training": {"visual": 0.0, "ai": 0.0, "gameplay": 0.0}, "held-out": {"visual": 0.0, "ai": 0.0, "gameplay": 0.0}})
    # lower envelope per consumer: cheapest representation achieving each error level
    envelope = {}
    for c in ("visual", "ai", "gameplay"):
        pts = sorted(((r["cost"], r["mean"][c], r["name"]) for r in reps), key=lambda x: x[0])
        env, best = [], np.inf
        for cost, err, name in pts:
            if err < best - 1e-6:
                env.append({"cost": cost, "error": err, "name": name})
                best = err
        envelope[c] = env

    # ---------------- B. liveness threshold ----------------
    print("B. liveness threshold (radial impulse tokens of the six-term fit)")
    rad = next(t for t in six.terms if t.prim.name == "radial_impulse")
    lam, k, zeta = rad.params["lam"], rad.params["k"], rad.params["zeta"]
    lam_eff = min(lam, zeta * np.sqrt(k))  # slower of the two decay rates in the spring envelope
    live_rows = []
    base_eps = primitives.LIVE_EPS
    for eps in (3e-1, 1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 1e-5):
        counts, errs = [], []
        for w in walks.values():
            tau = w.rec.times[:, None] - w.geom.ev_t0[None, :]
            env = spring_response(tau, lam, k, zeta)
            active = w.rec.times <= w.path.t_walk + 2.0  # while tokens are being made and dying
            counts.append(float((np.abs(env) > eps).sum(1)[active].mean()))
            primitives.LIVE_EPS = eps
            pred, _ = six.evaluate(w.geom, w.rec.times)
            primitives.LIVE_EPS = base_eps
            errs.append(rel_rmse(pred, w.rec.bend))
        rate = len(walks["training"].events) / walks["training"].path.t_walk
        live_rows.append({"eps": eps, "live_mean": float(np.mean(counts)), "visual": float(np.mean(errs)),
                          "predicted": float(rate / lam_eff * np.log(1.0 / eps))})
        print(f"  eps {eps:8.0e}: live {live_rows[-1]['live_mean']:5.2f}  predicted (R/lambda') log(1/eps) {live_rows[-1]['predicted']:5.2f}  visual {live_rows[-1]['visual']:.4f}")
    primitives.LIVE_EPS = base_eps

    # ---------------- C. path tolerance ----------------
    print("C. path polyline tolerance (Douglas-Peucker on the dense 200 Hz path)")
    path_rows = []
    full = {w: walk.score_direct(two)[0] for w, walk in walks.items()}
    for tol in (1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002):
        n_pts, scores = [], []
        for w, walk in walks.items():
            idx = douglas_peucker(walk.path.points, tol)
            tok = PathToken(walk.path.points[idx], walk.path.times[idx])
            n_pts.append(len(idx))
            s, _ = walk.score_with_path(two, tok)
            scores.append({c: s[c] - full[w][c] for c in s})  # excess over the 20 Hz banked path
        row = {"tol": tol, "points_mean": float(np.mean(n_pts)),
               "excess": {c: float(np.mean([s[c] for s in scores])) for c in scores[0]}}
        path_rows.append(row)
        print(f"  tol {tol:6.3f} m: {row['points_mean']:6.1f} points  excess visual {row['excess']['visual']:+.4f}  ai {row['excess']['ai']:+.4f}")

    # power-law fits on the clean parts of each sweep
    def loglog_slope(x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        m = (x > 0) & (y > 0)
        if m.sum() < 3:
            return float("nan")
        return float(np.polyfit(np.log(x[m]), np.log(y[m]), 1)[0])

    tols = [r["tol"] for r in path_rows]
    fits = {"points_vs_tol_slope": loglog_slope(tols, [r["points_mean"] for r in path_rows]),
            "excess_visual_vs_tol_slope": loglog_slope(tols, [r["excess"]["visual"] for r in path_rows]),
            "live_vs_log_inv_eps_slope": float(np.polyfit(np.log(1.0 / np.array([r["eps"] for r in live_rows])),
                                                          [r["live_mean"] for r in live_rows], 1)[0]),
            "live_predicted_slope": float(len(walks["training"].events) / walks["training"].path.t_walk / lam_eff)}
    report = {"convention": "expectation over recorded inputs (training + held-out walks, averaged)",
              "representations": reps, "envelope": envelope, "liveness": live_rows, "path": path_rows,
              "fits": fits, "radial_decay": {"lam": lam, "k": k, "zeta": zeta, "lam_eff": float(lam_eff)}}
    (out / "knee.json").write_text(json.dumps(report, indent=2))
    write_md(report, out / "knee.md")
    try:
        make_figure(report, out / "knee.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(json.dumps(fits, indent=2))
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    L = ["# Behavioural tolerance sweep (Math Track B0, item 18)", "",
         f"Convention: {r['convention']}. Cost is ops per stalk per frame; the teacher is {TEACHER_OPS:.0f} plus neighbour reads.", "",
         "## A. Representations", "", "| representation | cost | visual | AI field | gameplay | visual (held-out) |", "|---|---|---|---|---|---|"]
    for x in r["representations"]:
        L.append(f"| {x['name']} | {x['cost']:.0f} | {x['mean']['visual']:.3f} | {x['mean']['ai']:.3f} | {x['mean']['gameplay']:.3f} | {x['held-out']['visual']:.3f} |")
    L += ["", "Lower envelope (cheapest representation reaching each error level):", ""]
    for c, env in r["envelope"].items():
        L.append(f"- **{c}**: " + " -> ".join(f"{e['name']} ({e['cost']:.0f} ops, {e['error']:.3f})" for e in env))
    f = r["fits"]
    L += ["", "## B. Liveness threshold", "",
          f"Radial-impulse token of the six-term fit: lam={r['radial_decay']['lam']:.2f}, k={r['radial_decay']['k']:.0f}, zeta={r['radial_decay']['zeta']:.2f}, "
          f"slower decay rate lambda' = {r['radial_decay']['lam_eff']:.2f} 1/s.", "",
          "| eps | live tokens per frame (measured) | predicted (R/lambda') log(1/eps) | visual error with pruning |", "|---|---|---|---|"]
    for x in r["liveness"]:
        L.append(f"| {x['eps']:.0e} | {x['live_mean']:.2f} | {x['predicted']:.2f} | {x['visual']:.4f} |")
    L += ["", f"Measured slope of live count against log(1/eps): {f['live_vs_log_inv_eps_slope']:.3f}; predicted R/lambda' = {f['live_predicted_slope']:.3f}.", "",
          "## C. Path tolerance", "", "| tolerance (m) | points kept | excess visual error | excess AI error |", "|---|---|---|---|"]
    for x in r["path"]:
        L.append(f"| {x['tol']:.3f} | {x['points_mean']:.1f} | {x['excess']['visual']:+.4f} | {x['excess']['ai']:+.4f} |")
    L += ["", f"Log-log slope of points against tolerance: {f['points_vs_tol_slope']:.2f} (prediction -0.5). "
          f"Log-log slope of excess visual error against tolerance: {f['excess_visual_vs_tol_slope']:.2f} (Lipschitz prediction +1).", ""]
    path.write_text("\n".join(L) + "\n")


def make_figure(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    ax = axes[0]
    markers = {"field": "s", "direct": "o", "teacher": "*"}
    for c, col in (("visual", "C0"), ("ai", "C1"), ("gameplay", "C2")):
        for x in r["representations"]:
            ax.scatter(x["cost"], x["mean"][c], marker=markers[x["kind"]], color=col, alpha=0.6, s=40)
        env = r["envelope"][c]
        ax.plot([e["cost"] for e in env], [e["error"] for e in env], color=col, lw=2, label=f"{c} envelope")
    ax.set_xscale("log")
    ax.set_xlabel("cost (ops per stalk per frame)")
    ax.set_ylabel("error (expectation over walks)")
    ax.set_title("A. cost vs error; squares = baked field, circles = direct, star = teacher")
    ax.legend(fontsize=8)
    ax = axes[1]
    eps = np.array([x["eps"] for x in r["liveness"]])
    ax.plot(np.log(1 / eps), [x["live_mean"] for x in r["liveness"]], "o-", label="measured live tokens")
    ax.plot(np.log(1 / eps), [x["predicted"] for x in r["liveness"]], "--", label="(R/lambda') log(1/eps)")
    ax.set_xlabel("log(1/eps)")
    ax.set_ylabel("live radial tokens per frame")
    ax.set_title("B. liveness: prediction log(1/eps)")
    ax.legend(fontsize=8)
    ax = axes[2]
    tol = np.array([x["tol"] for x in r["path"]])
    ax.loglog(tol, [x["points_mean"] for x in r["path"]], "o-", label="points kept")
    ax2 = ax.twinx()
    ex = np.array([max(x["excess"]["visual"], 1e-5) for x in r["path"]])
    ax2.loglog(tol, ex, "s--", color="C3", label="excess visual error")
    ax.set_xlabel("polyline tolerance delta (m)")
    ax.set_ylabel("points kept")
    ax2.set_ylabel("excess visual error", color="C3")
    ax.set_title(f"C. path: points ~ delta^{r['fits']['points_vs_tol_slope']:.2f}, excess ~ delta^{r['fits']['excess_visual_vs_tol_slope']:.2f}")
    ax.legend(loc="upper right", fontsize=8)
    ax2.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
