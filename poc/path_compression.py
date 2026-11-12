"""Preregistered: spatial vs spacetime vs behaviour-weighted path compression.

Prediction (stated before running): at equal point counts on the held-out walk,
    E_behaviour_weighted(N) < E_spacetime(N) < E_spatial(N),
most clearly at the wake front, and the exponent of points against excess error
moves from about -0.73 (spatial) toward -0.5.

Methods, all Douglas-Peucker on the dense 200 Hz path with vertex times kept:
  spatial    : deviation measured in (x, y)                      [c_t = 0]
  spacetime  : deviation measured in (x, y, c_t t), c_t = mean walking speed
  behaviour  : same, with c_t = L_t / L_x from the fitted wake kernel, so that the
               DP tolerance bounds L_x delta_x + L_t delta_t directly

Also checks the corrected liveness bound: live-token count with the monotone
future envelope sup_{s >= tau} |K(s)| against (R / beta) log(C_s / eps).

Usage: python poc/path_compression.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout import parse_model  # noqa: E402
from reactive.causes import PathToken, emit_stride_events, holdout_walk, s_curve_walk  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.metrics import rel_rmse  # noqa: E402
from reactive.primitives import gkern, spring_response  # noqa: E402
from reactive.teacher import TeacherParams, run_teacher  # noqa: E402

TOLS = (0.5, 0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005, 0.002)
N_GRID = (5, 6, 8, 10, 12, 16, 20, 24, 32, 48)


def douglas_peucker_3d(pts3: np.ndarray, tol: float) -> np.ndarray:
    keep = np.zeros(len(pts3), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts3) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        seg = pts3[b] - pts3[a]
        L = np.linalg.norm(seg)
        rel = pts3[a + 1:b] - pts3[a]
        if L < 1e-12:
            d = np.linalg.norm(rel, axis=1)
        else:
            d = np.linalg.norm(np.cross(rel, seg), axis=1) / L
        i = int(np.argmax(d))
        if d[i] > tol:
            keep[a + 1 + i] = True
            stack.append((a, a + 1 + i))
            stack.append((a + 1 + i, b))
    return np.flatnonzero(keep)


def kernel_lipschitz(wake_params: dict) -> tuple[float, float]:
    """Max spatial and temporal slopes of the fitted wake kernel (unit amplitude)."""
    w, q = wake_params["w"], wake_params["q"]
    d = np.linspace(1e-4, 4 * w, 4000)
    Lx = float(np.max(np.abs(np.gradient(gkern(d, w, q), d))))
    tau = np.linspace(0, 3.0, 30000)
    env = spring_response(tau, wake_params["lam"], wake_params["k"], wake_params["zeta"])
    Lt = float(np.max(np.abs(np.gradient(env, tau))))
    return Lx, Lt


class Walk:
    def __init__(self, path, tp):
        self.path = path
        self.rec = run_teacher(path, tp)
        self.events = emit_stride_events(path, stride=0.5)
        self.late = self.rec.times >= path.t_walk + 1.0
        # reference: the dense path itself as the token
        self.dense = PathToken(path.points, path.times)
        g = build_geometry(self.rec.pos, self.events, self.dense, path)
        self.t_pass = g.path_tpass
        self.dperp = g.path_dperp
        # wake-front window: frames within [-0.3, +0.5] s of each stalk's pass time, stalks within 1 m
        dt = self.rec.times[:, None] - self.t_pass[None, :]
        self.front = (dt >= -0.3) & (dt <= 0.5) & (self.dperp[None, :] < 1.0)

    def score(self, model, token):
        g = build_geometry(self.rec.pos, self.events, token, self.path)
        pred, _ = model.evaluate(g, self.rec.times)
        e_all = rel_rmse(pred, self.rec.bend)
        e_front = rel_rmse(pred[self.front], self.rec.bend[self.front])
        return e_all, e_front


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    sweep = json.loads((out / "gpu_sweep.json").read_text())
    two = parse_model(sweep["terms"]["wake + presence"]["description"])
    wake = next(t for t in two.terms if t.prim.name == "wake").params
    Lx, Lt = kernel_lipschitz(wake)
    tp = TeacherParams()
    walks = {"training": Walk(s_curve_walk(t_total=tp.duration), tp),
             "held-out": Walk(holdout_walk(t_total=tp.duration), tp)}
    speed = float(np.mean([np.linalg.norm(np.diff(w.path.points, axis=0), axis=1).sum() / w.path.t_walk for w in walks.values()]))
    c_beh = Lt / Lx
    methods = {"spatial": 0.0, "spacetime": speed, "behaviour": c_beh}
    print(f"kernel Lipschitz: L_x={Lx:.3f} per m, L_t={Lt:.3f} per s -> c_t = L_t/L_x = {c_beh:.3f} m/s; mean walking speed {speed:.3f} m/s")

    ref = {w: walk.score(two, walk.dense) for w, walk in walks.items()}
    print("reference (dense 200 Hz path): " + ", ".join(f"{w}: all {e[0]:.4f} front {e[1]:.4f}" for w, e in ref.items()))
    curves = {m: {w: [] for w in walks} for m in methods}
    for m, c_t in methods.items():
        for tol in TOLS:
            for w, walk in walks.items():
                pts3 = np.column_stack([walk.path.points, c_t * walk.path.times])
                idx = douglas_peucker_3d(pts3, tol)
                tok = PathToken(walk.path.points[idx], walk.path.times[idx])
                e_all, e_front = walk.score(two, tok)
                curves[m][w].append({"tol": tol, "N": int(len(idx)), "E_all": e_all, "E_front": e_front,
                                     "excess_all": e_all - ref[w][0], "excess_front": e_front - ref[w][1]})
            r = curves[m]["held-out"][-1]
            print(f"  {m:10s} tol {tol:6.3f}: held-out N={r['N']:4d} excess all {r['excess_all']:+.4f} front {r['excess_front']:+.4f}")

    # equal-N comparison by log-log interpolation of excess error against N (held-out and training)
    def at_N(rows, key, N):
        rows = sorted(rows, key=lambda r: r["N"])
        Ns = np.array([r["N"] for r in rows], float)
        Es = np.array([max(r[key], 1e-6) for r in rows])
        # dedupe N (DP can give the same N for several tolerances)
        uniq = {}
        for n, e in zip(Ns, Es):
            uniq[n] = min(uniq.get(n, np.inf), e)
        Ns = np.array(sorted(uniq))
        Es = np.array([uniq[n] for n in Ns])
        if N < Ns.min() or N > Ns.max():
            return None
        return float(np.exp(np.interp(np.log(N), np.log(Ns), np.log(Es))))

    equal_n = {}
    for w in walks:
        equal_n[w] = []
        for N in N_GRID:
            row = {"N": N}
            for m in methods:
                row[m] = {"all": at_N(curves[m][w], "excess_all", N), "front": at_N(curves[m][w], "excess_front", N)}
            equal_n[w].append(row)

    # ordering test on the held-out walk: fraction of N where behaviour < spacetime < spatial
    order_hits = {"all": 0, "front": 0, "n": 0}
    for row in equal_n["held-out"]:
        for key in ("all", "front"):
            v = [row[m][key] for m in ("behaviour", "spacetime", "spatial")]
            if None in v:
                continue
            order_hits["n"] += 1 if key == "all" else 0
            if v[0] < v[1] < v[2]:
                order_hits[key] += 1

    # exponents: N against excess error (log-log), per method, both walks pooled
    def slope(m, key):
        xs, ys = [], []
        for w in walks:
            for r in curves[m][w]:
                if r[key] > 1e-4 and r["N"] > 3:
                    xs.append(r[key])
                    ys.append(r["N"])
        return float(np.polyfit(np.log(xs), np.log(ys), 1)[0]) if len(xs) > 3 else float("nan")

    exponents = {m: {"N_vs_excess_all": slope(m, "excess_all"), "N_vs_excess_front": slope(m, "excess_front")} for m in methods}

    # corrected liveness bound with the monotone future envelope
    six = parse_model(json.loads((out / "summary.json").read_text())["model"]["description"])
    rad = next(t for t in six.terms if t.prim.name == "radial_impulse").params
    tau = np.linspace(0, 6, 60001)
    env = np.abs(spring_response(tau, rad["lam"], rad["k"], rad["zeta"]))
    future = np.maximum.accumulate(env[::-1])[::-1]  # sup_{s >= tau} |K(s)|
    beta = min(rad["lam"], rad["zeta"] * np.sqrt(rad["k"]))
    C_s = float(np.max(future * np.exp(beta * tau)))  # smallest constant with future <= C_s e^{-beta tau}
    liveness = []
    walk = walks["training"]
    rate = len(walk.events) / walk.path.t_walk
    active = walk.rec.times <= walk.path.t_walk + 2.0
    for eps in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        tt = walk.rec.times[:, None] - walk.events.t0[None, :]
        fut = np.interp(np.clip(tt, 0, 6), tau, future) * (tt >= 0)
        measured = float((fut > eps).sum(1)[active].mean())
        bound = float(rate / beta * np.log(C_s / eps))
        liveness.append({"eps": eps, "live_future_envelope": measured, "bound": bound})
        print(f"  liveness eps {eps:.0e}: future-envelope live {measured:.2f}  bound (R/beta) log(C_s/eps) {bound:.2f}")

    report = {"prediction": "E_behaviour(N) < E_spacetime(N) < E_spatial(N) on held-out, strongest at the wake front; exponent toward -0.5",
              "kernel": {"L_x": Lx, "L_t": Lt, "c_t_behaviour": c_beh, "mean_speed": speed},
              "reference": {w: {"E_all": e[0], "E_front": e[1]} for w, e in ref.items()},
              "curves": curves, "equal_N": equal_n, "order_hits_heldout": order_hits, "exponents": exponents,
              "liveness_future_envelope": {"beta": float(beta), "C_s": C_s, "rows": liveness}}
    (out / "path_compression.json").write_text(json.dumps(report, indent=2))
    write_md(report, out / "path_compression.md")
    try:
        make_figure(report, out / "path_compression.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(json.dumps({"order_hits_heldout": order_hits, "exponents": exponents}, indent=2))
    print(f"wrote {out}")


def write_md(r, path: Path) -> None:
    k = r["kernel"]
    L = ["# Path compression: spatial vs spacetime vs behaviour-weighted (preregistered)", "",
         f"Prediction stated before the run: {r['prediction']}.", "",
         f"Fitted wake kernel slopes: L_x = {k['L_x']:.3f} per m, L_t = {k['L_t']:.3f} per s, so the behaviour-weighted time scale is "
         f"c_t = L_t / L_x = {k['c_t_behaviour']:.2f} m/s (mean walking speed {k['mean_speed']:.2f} m/s). Excess error is relative to the dense 200 Hz path as token.", ""]
    for w in ("held-out", "training"):
        L += [f"## Equal point counts, {w} walk (excess visual error, all frames / wake front)", "",
              "| N | spatial | spacetime | behaviour |", "|---|---|---|---|"]
        for row in r["equal_N"][w]:
            def f(m):
                v = row[m]
                return "-" if v["all"] is None else f"{v['all']:.4f} / {v['front']:.4f}"
            L.append(f"| {row['N']} | {f('spatial')} | {f('spacetime')} | {f('behaviour')} |")
        L.append("")
    oh = r["order_hits_heldout"]
    L += [f"Held-out ordering behaviour < spacetime < spatial held at {oh['all']} of {oh['n']} point counts on all frames "
          f"and {oh['front']} of {oh['n']} at the wake front.", "",
          "## Exponents: points against excess error (log-log, both walks)", "", "| method | all frames | wake front |", "|---|---|---|"]
    for m, e in r["exponents"].items():
        L.append(f"| {m} | {e['N_vs_excess_all']:.2f} | {e['N_vs_excess_front']:.2f} |")
    lv = r["liveness_future_envelope"]
    L += ["", f"Prediction was -0.5; the earlier spatial-only estimate was -0.73.", "",
          "## Corrected liveness bound (monotone future envelope)", "",
          f"beta = min(lam, c/2) = {lv['beta']:.2f} 1/s, C_s = {lv['C_s']:.2f}.", "",
          "| eps | live tokens (future envelope) | bound (R/beta) log(C_s/eps) |", "|---|---|---|"]
    for row in lv["rows"]:
        L.append(f"| {row['eps']:.0e} | {row['live_future_envelope']:.2f} | {row['bound']:.2f} |")
    path.write_text("\n".join(L) + "\n")


def make_figure(r, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, key, title in ((axes[0], "excess_all", "held-out, all frames"), (axes[1], "excess_front", "held-out, wake front")):
        for m, style in (("spatial", "o-"), ("spacetime", "s-"), ("behaviour", "^-")):
            rows = sorted(r["curves"][m]["held-out"], key=lambda x: x["N"])
            ax.loglog([x["N"] for x in rows], [max(x[key], 1e-5) for x in rows], style, label=m)
        ax.set_xlabel("path points kept")
        ax.set_ylabel("excess visual error over dense path")
        ax.set_title(title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
