"""Math Track B2: causal path complexity. Implements docs/math-track-b2-prereg.md exactly.

Usage: python poc/b2_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout import parse_model  # noqa: E402
from reactive.causes import PathToken, emit_stride_events  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.teacher import TeacherParams, stalk_grid  # noqa: E402
from reactive.worldlines import HZ, family  # noqa: E402

THRESHOLDS = (0.00065, 0.00130, 0.00261, 0.00521)  # metres
PRIMARY = (0.00130, 0.00261)
ALPHA = 0.05
X_VISIBLE = 4.5
TOLS = np.geomspace(1.0, 0.0005, 48)
LOCAL_R = 1.5
SIGMA_S = 0.025
N_BINS = 12
H5_EPS = 0.00261
FPS = 60.0


STOP_SPEED = 0.05


def event_vertices(speed):
    """Amendment 1: samples where speed crosses STOP_SPEED and where zero-speed intervals begin/end."""
    moving = speed > STOP_SPEED
    cross = np.flatnonzero(moving[1:] != moving[:-1]) + 1
    still = speed <= 1e-9
    edges = np.flatnonzero(still[1:] != still[:-1]) + 1
    return np.unique(np.concatenate([cross, edges]))


def weighted_time_dp(points, times, weights, tol, forced=None):
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
        d = weights[a + 1:b] * np.linalg.norm(points[a + 1:b] - phat, axis=1)
        i = int(np.argmax(d))
        if d[i] > tol:
            keep[a + 1 + i] = True
            stack.append((a, a + 1 + i))
            stack.append((a + 1 + i, b))
    return np.flatnonzero(keep)


def complexity(w, L_t):
    dt = w.times[1] - w.times[0]
    acc = np.linalg.norm(w.accel, axis=1)
    c_analytic = float(np.trapezoid(np.sqrt(L_t * acc), dx=dt))
    sm = gaussian_filter1d(w.points, sigma=SIGMA_S * HZ, axis=0, truncate=4.0, mode="nearest")
    vel = np.gradient(sm, dt, axis=0)
    acc_est = np.linalg.norm(np.gradient(vel, dt, axis=0), axis=1)
    c_est = float(np.trapezoid(np.sqrt(L_t * acc_est), dx=dt))
    return c_analytic, c_est, acc


def baselines(w):
    dt = w.times[1] - w.times[0]
    length = float(np.linalg.norm(np.diff(w.points, axis=0), axis=1).sum())
    turning = float(np.trapezoid(np.abs(w.heading_rate) * (w.speed > 1e-6), dx=dt))
    int_acc = float(np.trapezoid(np.linalg.norm(w.accel, axis=1), dx=dt))
    moving = w.speed > 0.05
    down = np.flatnonzero(moving[:-1] & ~moving[1:])
    stops = int(np.sum(w.times[down] < w.t_walk - 0.1))
    return {"length": length, "turning": turning, "int_acc": int_acc, "stops": stops}


class Consumer:
    def __init__(self, model, pos, times):
        self.model, self.pos, self.times = model, pos, times

    def field(self, w, token):
        g = build_geometry(self.pos, emit_stride_events(w.as_path()), token, w.as_path())
        pred, _ = self.model.evaluate(g, self.times)
        return pred, g


def rms_error(pred, ref, mask, stalk_w=None):
    d2 = ((pred - ref) ** 2).sum(-1)[:, mask]  # (F, n_local)
    if stalk_w is None:
        return float(np.sqrt(d2.mean())), float(np.sqrt(d2.max()))
    wts = stalk_w[mask][None, :]
    return float(np.sqrt((d2 * wts).sum() / (wts.sum() * d2.shape[0]))), float(np.sqrt(d2.max()))


def n_at(rows, eps, key="err"):
    ok = [r for r in rows if r[key] <= eps]
    if not ok:
        return None, None
    best = min(ok, key=lambda r: r["N"])
    return best["N"], best["idx"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    out = Path(args.out)
    two = parse_model(json.loads((out / "gpu_sweep.json").read_text())["terms"]["wake + presence"]["description"])
    tp = TeacherParams()
    pos = stalk_grid(tp)
    times = np.arange(int(tp.duration * FPS) + 1) / FPS
    cons = Consumer(two, pos, times)
    results = {}
    for w in family():
        ref, g = cons.field(w, PathToken(w.points, w.times))
        mask = g.path_dperp < LOCAL_R
        ones = np.ones(len(w.times))
        c_an, c_est, acc = complexity(w, ones)
        forced = event_vertices(w.speed)
        rows = []
        for tol in TOLS:
            idx = weighted_time_dp(w.points, w.times, ones, tol, forced)
            pred, _ = cons.field(w, PathToken(w.points[idx], w.times[idx]))
            e, s = rms_error(pred, ref, mask)
            rows.append({"tol": float(tol), "N": int(len(idx)), "err": e, "sup": s, "idx": idx})
        N = {str(eps): n_at(rows, eps)[0] for eps in THRESHOLDS}
        _, idx5 = n_at(rows, H5_EPS)
        # H5: vertex density per bin vs sqrt(q) per bin over the walking interval
        h5 = None
        if idx5 is not None:
            edges = np.linspace(0, w.t_walk, N_BINS + 1)
            tv = w.times[idx5]
            tv = tv[(tv > 0) & (tv < w.t_walk)]
            dens = np.histogram(tv, bins=edges)[0] / np.diff(edges)
            sq = np.sqrt(acc)
            pred_d = np.array([sq[(w.times >= edges[k]) & (w.times < edges[k + 1])].mean() for k in range(N_BINS)])
            h5 = {"spearman": float(spearmanr(dens, pred_d).correlation), "density": dens.tolist(), "sqrt_q": pred_d.tolist()}
        results[w.name] = {"C_analytic": c_an, "C_estimated": c_est, "baselines": baselines(w), "N": N,
                           "curve": [{k: v for k, v in r.items() if k != "idx"} for r in rows], "h5": h5}
        print(f"{w.name:11s} C={c_an:6.2f} (est {c_est:6.2f})  N(eps)={[N[str(e)] for e in THRESHOLDS]}  "
              f"baselines={ {k: round(v, 2) for k, v in results[w.name]['baselines'].items()} }  H5 rho={h5['spearman'] if h5 else None}")

    # H4 control on the wandering trajectory
    wnd = next(w for w in family() if w.name == "wandering")
    ref, g = cons.field(wnd, PathToken(wnd.points, wnd.times))
    mask = g.path_dperp < LOCAL_R
    L_B = np.where(wnd.points[:, 0] < X_VISIBLE, 1.0, ALPHA)
    stalk_w = np.where(pos[:, 0] < X_VISIBLE, 1.0, ALPHA)
    cB_an, cB_est, _ = complexity(wnd, L_B)
    forced = event_vertices(wnd.speed)
    rows_w, rows_u = [], []
    for tol in TOLS:
        idx = weighted_time_dp(wnd.points, wnd.times, L_B, tol, forced)
        pred, _ = cons.field(wnd, PathToken(wnd.points[idx], wnd.times[idx]))
        rows_w.append({"tol": float(tol), "N": int(len(idx)), "err": rms_error(pred, ref, mask, stalk_w)[0], "idx": idx})
        idx = weighted_time_dp(wnd.points, wnd.times, np.ones(len(wnd.times)), tol, forced)
        pred, _ = cons.field(wnd, PathToken(wnd.points[idx], wnd.times[idx]))
        rows_u.append({"tol": float(tol), "N": int(len(idx)), "err": rms_error(pred, ref, mask, stalk_w)[0], "idx": idx})
    h4 = {"C_A": results["wandering"]["C_analytic"], "C_B": cB_an, "C_B_estimated": cB_est,
          "N_A": results["wandering"]["N"], "N_B_weighted": {str(e): n_at(rows_w, e)[0] for e in THRESHOLDS},
          "N_B_unweighted": {str(e): n_at(rows_u, e)[0] for e in THRESHOLDS}}
    print(f"H4: C_A={h4['C_A']:.2f} C_B={h4['C_B']:.2f}  N_A={list(h4['N_A'].values())}  N_B weighted={list(h4['N_B_weighted'].values())}  N_B unweighted={list(h4['N_B_unweighted'].values())}")

    # ---- analysis ----
    names = list(results)
    C = np.array([results[n]["C_analytic"] for n in names])
    analysis = {"H1": {}, "H2": {}, "H3": {}, "H6": {}}
    Z_all, N_all = [], []
    for eps in THRESHOLDS:
        vals = [results[n]["N"][str(eps)] for n in names]
        if any(v is None for v in vals):
            continue
        Ns = np.array(vals, float)
        rho = float(spearmanr(C, Ns).correlation)
        b, a = np.polyfit(C, Ns, 1)
        r2 = float(1 - ((Ns - (a + b * C)) ** 2).sum() / ((Ns - Ns.mean()) ** 2).sum())
        analysis["H1"][str(eps)] = rho
        analysis["H2"][str(eps)] = {"a": float(a), "b": float(b), "R2": r2}
        Z_all += list(Ns * np.sqrt(eps) / C)
        N_all += list(Ns)
        base = {k: np.array([results[n]["baselines"][k] for n in names], float) for k in ("length", "turning", "int_acc", "stops")}
        analysis["H6"][str(eps)] = {}
        for k, x in base.items():
            if np.std(x) < 1e-12:
                analysis["H6"][str(eps)][k] = {"spearman": None, "R2": None}
                continue
            bb, aa = np.polyfit(x, Ns, 1)
            analysis["H6"][str(eps)][k] = {"spearman": float(spearmanr(x, Ns).correlation),
                                           "R2": float(1 - ((Ns - (aa + bb * x)) ** 2).sum() / ((Ns - Ns.mean()) ** 2).sum())}
        analysis["H6"][str(eps)]["C_G"] = {"spearman": rho, "R2": r2}
    Z_all, N_all = np.array(Z_all), np.array(N_all)
    analysis["H3"] = {"CV_N": float(N_all.std() / N_all.mean()), "CV_Z": float(Z_all.std() / Z_all.mean()),
                      "pass": bool(Z_all.std() / Z_all.mean() < 0.5 * N_all.std() / N_all.mean())}
    analysis["H4"] = h4
    analysis["H5"] = {"per_trajectory": {n: (results[n]["h5"]["spearman"] if results[n]["h5"] else None) for n in names}}
    vals = [v for v in analysis["H5"]["per_trajectory"].values() if v is not None and not np.isnan(v)]
    analysis["H5"]["median"] = float(np.median(vals)) if vals else None
    report = {"thresholds_m": THRESHOLDS, "results": results, "analysis": analysis}
    (out / f"b2{args.tag}.json").write_text(json.dumps(report, indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    write_md(report, out / f"b2{args.tag}.md")
    try:
        make_figure(report, out / f"b2{args.tag}.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(json.dumps({k: analysis[k] for k in ("H1", "H3", "H5")}, indent=2, default=str))
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    res, an = r["results"], r["analysis"]
    eps_list = r["thresholds_m"]
    L = ["# Math Track B2 results: causal path complexity", "",
         "Preregistration: `docs/math-track-b2-prereg.md`. Thresholds in mm: " + ", ".join(f"{e*1000:.2f}" for e in eps_list) + ".", "",
         "## Per trajectory", "", "| trajectory | C_G analytic | C_G estimated | length | turning | int acc | stops | " +
         " | ".join(f"N({e*1000:.2f} mm)" for e in eps_list) + " | H5 rho |", "|---|---|---|---|---|---|---|" + "---|" * len(eps_list) + "---|"]
    for n, x in res.items():
        b = x["baselines"]
        h5 = f"{x['h5']['spearman']:.2f}" if x["h5"] else "-"
        L.append(f"| {n} | {x['C_analytic']:.2f} | {x['C_estimated']:.2f} | {b['length']:.1f} | {b['turning']:.2f} | {b['int_acc']:.1f} | {b['stops']} | "
                 + " | ".join(str(x["N"][str(e)]) for e in eps_list) + f" | {h5} |")
    L += ["", "## H1 Spearman(C_G, N) per threshold (bar 0.8)", "", "| eps (mm) | rho |", "|---|---|"]
    for e, v in an["H1"].items():
        L.append(f"| {float(e)*1000:.2f} | {v:.3f} |")
    L += ["", "## H2 linear fit N = a + b C_G (bar R^2 0.8 at primary thresholds 1.30, 2.61 mm)", "", "| eps (mm) | a | b | R^2 |", "|---|---|---|---|"]
    for e, v in an["H2"].items():
        L.append(f"| {float(e)*1000:.2f} | {v['a']:.1f} | {v['b']:.2f} | {v['R2']:.3f} |")
    h3 = an["H3"]
    L += ["", f"## H3 normalisation: CV(N) = {h3['CV_N']:.3f}, CV(Z) = {h3['CV_Z']:.3f}, pass (CV_Z < 0.5 CV_N): {h3['pass']}", ""]
    h4 = an["H4"]
    L += ["## H4 identical path, two consumers (wandering)", "", f"C_A = {h4['C_A']:.2f}, C_B = {h4['C_B']:.2f}.", "",
          "| eps (mm) | N_A | N_B weighted compressor | N_B unweighted compressor |", "|---|---|---|---|"]
    for e in eps_list:
        L.append(f"| {e*1000:.2f} | {h4['N_A'][str(e)]} | {h4['N_B_weighted'][str(e)]} | {h4['N_B_unweighted'][str(e)]} |")
    med = an["H5"]["median"]
    L += ["", f"## H5 vertex placement: median Spearman over trajectories = {med if med is None else round(med, 2)} (bar 0.6)", ""]
    L += ["## H6 baselines vs C_G (Spearman / R^2)", "", "| eps (mm) | C_G | length | turning | int acc | stops |", "|---|---|---|---|---|---|"]
    for e, v in an["H6"].items():
        def f(k):
            z = v[k]
            return "-" if z["spearman"] is None else f"{z['spearman']:.2f} / {z['R2']:.2f}"
        L.append(f"| {float(e)*1000:.2f} | {f('C_G')} | {f('length')} | {f('turning')} | {f('int_acc')} | {f('stops')} |")
    path.write_text("\n".join(L) + "\n")


def make_figure(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    res, eps_list = r["results"], r["thresholds_m"]
    names = list(res)
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    ax = axes[0]
    C = np.array([res[n]["C_analytic"] for n in names])
    for e, col in zip(eps_list, ("C0", "C1", "C2", "C3")):
        Ns = [res[n]["N"][str(e)] for n in names]
        if any(v is None for v in Ns):
            continue
        ax.scatter(C, Ns, color=col, label=f"eps = {e*1000:.2f} mm")
        for n, c, N in zip(names, C, Ns):
            if e == eps_list[1]:
                ax.annotate(n, (c, N), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("C_G (analytic)")
    ax.set_ylabel("vertices needed N(eps)")
    ax.set_title("H1/H2: N against causal complexity")
    ax.legend(fontsize=8)
    ax = axes[1]
    for e in eps_list:
        if any(res[n]["N"][str(e)] is None for n in names):
            continue
        Z = [res[n]["N"][str(e)] * np.sqrt(e) / res[n]["C_analytic"] for n in names]
        ax.plot(range(len(names)), Z, "o-", label=f"eps = {e*1000:.2f} mm")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=40, fontsize=8)
    ax.set_ylabel("Z = N sqrt(eps) / C_G")
    ax.set_title("H3: normalised vertex count")
    ax.legend(fontsize=8)
    ax = axes[2]
    w = res["wandering"]["h5"]
    if w:
        x = np.arange(len(w["density"]))
        ax.bar(x - 0.2, np.array(w["density"]) / max(np.max(w["density"]), 1e-9), width=0.4, label="kept-vertex density")
        ax.bar(x + 0.2, np.array(w["sqrt_q"]) / max(np.max(w["sqrt_q"]), 1e-9), width=0.4, label="sqrt(q_G) (analytic)")
        ax.set_xlabel("time bin (wandering walk)")
        ax.set_title(f"H5: where vertices go (rho = {w['spearman']:.2f})")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
