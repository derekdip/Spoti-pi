"""Latency check for the streaming application (docs/streaming-latency-check.md): does local
reconstruction of a player-caused effect beat a streamed render of the true effect, once the
stream's round-trip delay is counted?

Design check, not preregistered. The teacher vegetation field F(t) is the truth. A streamed render
shows the truth as it was one round trip ago, F(t - L); its error against F(t) is the latency's cost.
Local reconstruction shows the fitted cheap model's field F^(t) from the player's own path with no
delay; its error against F(t) is the representation's cost, the number the project has measured all
along (0.39 per stalk, 0.22 on the 16 x 16 field). The question is the crossover: the delay L at
which the stream's latency error exceeds the reconstruction's fidelity error, in the whole field and
near the player, where the player looks and where the effect is being caused. The teacher runs at
60 Hz, so L is a multiple of 16.7 ms. Both walks (training S-curve and held-out hook) are evaluated.

  python3 poc/latency_check.py   -> poc/results/latency_check.md, .json
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reactive.causes import bank_path, emit_stride_events, holdout_walk, s_curve_walk
from reactive.geometry import build_geometry
from reactive.metrics import rel_rmse, coarse_rel_rmse
from reactive.teacher import TeacherParams, run_teacher
from holdout import parse_model

OUT = Path(__file__).resolve().parent / "results"
DELAYS = [1, 2, 3, 4, 5, 6, 8, 12]          # frames at 60 Hz: 17 to 200 ms
NEAR = 1.0                                     # m: the stalks within this radius of the player's present position


def masked_rel(pred, true, mask):
    """Relative RMS over the selected (frame, stalk) entries: ||pred - true|| / ||true||."""
    d = ((pred - true) ** 2).sum(-1)[mask].sum(); n = (true ** 2).sum(-1)[mask].sum()
    return float(np.sqrt(d / n)) if n > 0 else float("nan")


def run(path, tp, model):
    rec = run_teacher(path, tp); F = rec.bend; T = rec.times; pos = rec.pos
    g = build_geometry(pos, emit_stride_events(path, stride=0.5), bank_path(path, hz=20.0), path)
    pred, cost = model.evaluate(g, T)
    walking = T <= path.t_walk
    ppos = path.position(T)                                   # the player's present position per frame
    near = (np.linalg.norm(pos[None, :, :] - ppos[:, None, :], axis=-1) <= NEAR) & walking[:, None]
    out = dict(frames=int(len(T)), fps=tp.fps, cost=cost,
               local=dict(all=rel_rmse(pred, F), walking=masked_rel(pred, F, np.broadcast_to(walking[:, None], F.shape[:2])), near=masked_rel(pred, F, near),
                          coarse16=coarse_rel_rmse(pred, F, pos, 16, tp.extent)),
               stream={})
    for k in DELAYS:
        delayed = np.concatenate([np.repeat(F[:1], k, 0), F[:-k]], 0)       # the truth as of k frames ago
        out["stream"][k] = dict(ms=round(1000 * k / tp.fps), all=rel_rmse(delayed, F), walking=masked_rel(delayed, F, np.broadcast_to(walking[:, None], F.shape[:2])),
                                near=masked_rel(delayed, F, near), coarse16=coarse_rel_rmse(delayed, F, pos, 16, tp.extent))
    # the hybrid an engine would build: the stream everywhere, local reconstruction within NEAR of the player
    for k in DELAYS:
        delayed = np.concatenate([np.repeat(F[:1], k, 0), F[:-k]], 0); hyb = np.where(near[:, :, None], pred, delayed)
        out["stream"][k]["hybrid_all"] = rel_rmse(hyb, F); out["stream"][k]["hybrid_walking"] = masked_rel(hyb, F, np.broadcast_to(walking[:, None], F.shape[:2]))
    return out


def main():
    tp = TeacherParams(); model = parse_model(json.loads((OUT / "summary.json").read_text())["model"]["description"])
    res = {"training walk (S-curve)": run(s_curve_walk(t_total=tp.duration), tp, model), "held-out walk (hook)": run(holdout_walk(t_total=tp.duration), tp, model)}
    lines = ["# Latency check: streamed truth delayed by one round trip against local reconstruction with none", "",
             "Relative RMS of the stalk bend against the teacher's present field. 'near' is the stalks within 1 m of the player's present position while walking; 'walking' is every stalk while the player moves; 'all' is the whole window including the 4 s of standing. The hybrid shows the stream everywhere and the local reconstruction within 1 m of the player.", ""]
    for name, r in res.items():
        lines += [f"## {name}", "", f"Local reconstruction (no delay, {r['cost']:.0f} ops per stalk): all {r['local']['all']:.3f}, walking {r['local']['walking']:.3f}, near {r['local']['near']:.3f}, coarse 16x16 {r['local']['coarse16']:.3f}", "",
                  "| delay | ms | stream all | stream walking | stream near | stream coarse | hybrid all | hybrid walking |", "|---|---|---|---|---|---|---|---|"]
        for k, s in r["stream"].items():
            lines.append(f"| {k} frames | {s['ms']} | {s['all']:.3f} | {s['walking']:.3f} | {s['near']:.3f} | {s['coarse16']:.3f} | {s['hybrid_all']:.3f} | {s['hybrid_walking']:.3f} |")
        lines.append("")
    text = "\n".join(lines); (OUT / "latency_check.md").write_text(text); (OUT / "latency_check.json").write_text(json.dumps(res, indent=1, default=float)); print(text)


if __name__ == "__main__":
    main()
