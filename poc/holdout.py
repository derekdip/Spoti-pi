"""Held-out test: evaluate the model discovered by run_experiment.py on a walk it never saw.

Usage: python poc/holdout.py [--results poc/results]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reactive.causes import bank_path, emit_stride_events, holdout_walk, s_curve_walk  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.metrics import coarse_corr, coarse_rel_rmse, rel_rmse, trail_iou  # noqa: E402
from reactive.model import CheapModel, make_term  # noqa: E402
from reactive.teacher import TeacherParams, run_teacher  # noqa: E402


def parse_model(description: str) -> CheapModel:
    model = CheapModel()
    for line in description.strip().splitlines():
        m = re.match(r"\s*(\w+)\((.*)\)", line)
        name, body = m.group(1), m.group(2)
        params = {k: float(v) for k, v in re.findall(r"(\w+)=([-+0-9.e]+)", body)}
        if name == "saturate":
            model.saturate = params
        else:
            term = make_term(name)
            term.params.update(params)
            model.terms.append(term)
    return model


def evaluate(model: CheapModel, path, tp: TeacherParams) -> dict:
    rec = run_teacher(path, tp)
    events = emit_stride_events(path, stride=0.5)
    ptoken = bank_path(path, hz=20.0)
    g = build_geometry(rec.pos, events, ptoken, path)
    pred, cost = model.evaluate(g, rec.times)
    late = rec.times >= path.t_walk + 1.0
    return {
        "E_all": rel_rmse(pred, rec.bend),
        "E_late": rel_rmse(pred[late], rec.bend[late]),
        "E_coarse16_all": coarse_rel_rmse(pred, rec.bend, rec.pos, 16, tp.extent),
        "E_coarse16_late": coarse_rel_rmse(pred[late], rec.bend[late], rec.pos, 16, tp.extent),
        "coarse16_late_corr": coarse_corr(pred[late], rec.bend[late], rec.pos, 16, tp.extent),
        "trail_iou_16": trail_iou(pred[late], rec.bend[late], rec.pos, 16, tp.extent),
        "cost": cost,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.results)
    summary = json.loads((out / "summary.json").read_text())
    model = parse_model(summary["model"]["description"])
    tp = TeacherParams()
    rows = {"training walk (S-curve, 6 s)": evaluate(model, s_curve_walk(t_total=tp.duration), tp),
            "held-out walk (diagonal hook, 5 s)": evaluate(model, holdout_walk(t_total=tp.duration), tp)}
    keys = ["E_all", "E_late", "E_coarse16_all", "E_coarse16_late", "coarse16_late_corr", "trail_iou_16"]
    lines = ["# Held-out walk", "", "Same model parameters, no refitting.", "",
             "| walk | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for name, r in rows.items():
        lines.append(f"| {name} | " + " | ".join(f"{r[k]:.3f}" for k in keys) + " |")
    text = "\n".join(lines) + "\n"
    (out / "holdout.md").write_text(text)
    (out / "holdout.json").write_text(json.dumps(rows, indent=2))
    print(text)


if __name__ == "__main__":
    main()
