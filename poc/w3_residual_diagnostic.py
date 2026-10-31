"""Post-hoc residual diagnostic for W3 (exploratory, unregistered, not scored).

Asks what the single-splash residual is made of after amplitude conditioning,
so the next track can be preregistered against a measured signature rather than
a guess. Uses the models fitted by `w3_experiment.py` (`poc/results/w3.json`)
and re-runs the teacher at A = 1, 4, 8 (the A = 1 fixed-token residual is the
family's own misfit floor).

Decompositions reported, all on W1's evaluation set (r < 2 m, t >= 0.15 s):

* axisymmetric share of the residual energy (a single cause should leave an
  axisymmetric residual; anything else is grid noise);
* share explained by a gain and a time-shift correction of the token itself,
  at three granularities: one pair of scalars for the whole field, one pair
  per frame, one pair per radius bin (tests whether the missing thing is the
  *same* two axes conditioned on local state instead of on cause amplitude);
* share along the A = 1 floor residual (is the unrecovered part the linear
  family's misfit grown with amplitude, or something new);
* where the residual energy sits (near-field early box vs the rest) compared
  with where the teacher's energy sits;
* crest/trough asymmetry and the residual's radial zero-crossing count
  relative to the token's (harmonic content test).

Usage: python poc/w3_residual_diagnostic.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from w1_experiment import CENTRE, NL  # noqa: E402
from w3_experiment import token_field  # noqa: E402
from water.teacher import WaterParams, run_splash  # noqa: E402

AMPS = (1.0, 4.0, 8.0)
MODELS = ("M0", "M2", "M4")
DT = 1.0 / 240.0


def explained(R: np.ndarray, basis: list[np.ndarray]) -> float:
    """Fraction of ||R||^2 explained by a least-squares fit on `basis` (same shape as R)."""
    B = np.stack([b.ravel() for b in basis], 1)
    coef, *_ = np.linalg.lstsq(B, R.ravel(), rcond=None)
    fit = B @ coef
    return float(1.0 - ((R.ravel() - fit) ** 2).sum() / (R.ravel() ** 2).sum())


def zero_crossings(profile: np.ndarray) -> int:
    s = np.sign(profile)
    s = s[s != 0]
    return int((s[1:] * s[:-1] < 0).sum())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    w3 = json.loads((out / "w3.json").read_text())
    theta0, fitted = w3["theta0"], w3["models"]

    p = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **NL)
    xs = np.arange(p.n) * p.dx
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    times_all = np.arange(int(p.duration * p.fps) + 1) / p.fps
    ok = times_all >= 0.15
    t_eval = times_all[ok]
    rad = np.sqrt((X - CENTRE[0]) ** 2 + (Y - CENTRE[1]) ** 2)
    ev = rad < 2.0
    pts = np.stack([X[ev], Y[ev]], -1)
    rr = rad[ev]
    bins = np.floor(rr / p.dx).astype(int)
    nb = int(bins.max()) + 1
    counts = np.bincount(bins, minlength=nb).astype(float)

    def axisym(F):
        prof = np.stack([np.bincount(bins, weights=F[t], minlength=nb) for t in range(F.shape[0])]) / counts
        return prof, prof[:, bins]

    def token(name, A, times):
        m = fitted[name]
        return token_field(theta0, m["slopes"], m["gain_s1"], A, pts, times, [CENTRE])

    report = {"note": "post-hoc, exploratory, not part of the frozen W3 scoring", "amps": AMPS, "models": MODELS, "cells": {}}
    floor_R = None
    profiles = {}
    for A in AMPS:
        eta = run_splash(p, *CENTRE, v0=A, sigma=0.03).eta.astype(float)[ok][:, ev]
        print(f"teacher A={A} done")
        E_eta = float((eta ** 2).sum())
        near = (rr < 0.5)[None, :] & (t_eval < 1.0)[:, None]
        for name in MODELS:
            K = token(name, A, t_eval)
            Kp = token(name, A, t_eval + DT)
            Km = token(name, A, t_eval - DT)
            dK = (Kp - Km) / (2 * DT)
            R = eta - K
            E_R = float((R ** 2).sum())
            if A == 1.0 and name == "M0":
                floor_R = R.copy()
            prof_R, R_axi = axisym(R)
            prof_eta, _ = axisym(eta)
            prof_K, _ = axisym(K)
            cell = {"rel_rmse": float(np.sqrt(E_R / E_eta)), "axisym_share": float((R_axi ** 2).sum() / E_R)}
            # gain + time-shift corrections at three granularities
            cell["gain_phase_global"] = explained(R, [K, dK])
            per_frame = 0.0
            for t in range(R.shape[0]):
                B = np.stack([K[t], dK[t]], 1)
                c, *_ = np.linalg.lstsq(B, R[t], rcond=None)
                per_frame += ((R[t] - B @ c) ** 2).sum()
            cell["gain_phase_per_frame"] = float(1.0 - per_frame / E_R)
            per_bin = 0.0
            for b in range(nb):
                sel = bins == b
                if not sel.any():
                    continue
                B = np.stack([K[:, sel].ravel(), dK[:, sel].ravel()], 1)
                c, *_ = np.linalg.lstsq(B, R[:, sel].ravel(), rcond=None)
                per_bin += ((R[:, sel].ravel() - B @ c) ** 2).sum()
            cell["gain_phase_per_radius"] = float(1.0 - per_bin / E_R)
            cell["gain_only_per_frame"] = float(1.0 - sum(((R[t] - K[t] * (R[t] @ K[t]) / max(K[t] @ K[t], 1e-30)) ** 2).sum() for t in range(R.shape[0])) / E_R)
            # projection on the floor residual
            if floor_R is not None:
                cell["floor_share"] = explained(R, [floor_R])
            # where the residual sits
            cell["near_early_share_residual"] = float((R[near] ** 2).sum() / E_R)
            cell["near_early_share_teacher"] = float((eta[near] ** 2).sum() / E_eta)
            # asymmetry and wavenumber content
            asym_eta = np.median([eta[t].max() / max(-eta[t].min(), 1e-9) for t in range(eta.shape[0])])
            asym_K = np.median([K[t].max() / max(-K[t].min(), 1e-9) for t in range(K.shape[0])])
            cell["crest_trough_teacher"] = float(asym_eta)
            cell["crest_trough_token"] = float(asym_K)
            zc = {}
            for tq in (0.5, 1.0, 2.0):
                f = int(np.argmin(np.abs(t_eval - tq)))
                sel = (np.arange(nb) * p.dx > 0.2)
                zc[str(tq)] = {"teacher": zero_crossings(prof_eta[f][sel]), "token": zero_crossings(prof_K[f][sel]), "residual": zero_crossings(prof_R[f][sel])}
            cell["zero_crossings"] = zc
            report["cells"][f"{name}_A{A:g}"] = cell
            if A == 8.0 and name in ("M0", "M2"):
                profiles[name] = {"eta": prof_eta, "K": prof_K, "R": prof_R}
            print(f"  {name}: " + ", ".join(f"{k} {v:.3f}" for k, v in cell.items() if isinstance(v, float)))

    (out / "w3_residual.json").write_text(json.dumps(report, indent=2))
    write_md(report, out / "w3_residual.md")
    try:
        plot(report, profiles, t_eval, np.arange(nb) * p.dx, out / "w3_residual.png")
    except Exception as e:  # noqa: BLE001
        print("plot failed:", e)
    print(f"wrote {out / 'w3_residual.md'}")


def write_md(r, path: Path) -> None:
    keys = ["rel_rmse", "axisym_share", "gain_phase_global", "gain_phase_per_frame", "gain_phase_per_radius", "gain_only_per_frame", "floor_share",
            "near_early_share_residual", "near_early_share_teacher", "crest_trough_teacher", "crest_trough_token"]
    L = ["# W3 post-hoc residual diagnostic (exploratory, unregistered, not scored)", "",
         "Single-splash residual `teacher - token` on W1's evaluation set, by model and amplitude. Shares are fractions of the residual energy.", "",
         "| cell | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for name, c in r["cells"].items():
        L.append(f"| {name} | " + " | ".join(f"{c[k]:.3f}" if k in c else "-" for k in keys) + " |")
    L += ["", "Zero crossings of the azimuthally averaged radial profile (0.2 < r < 2 m) at t = 0.5, 1, 2 s: teacher / token / residual.", "",
          "| cell | t=0.5 | t=1 | t=2 |", "|---|---|---|---|"]
    for name, c in r["cells"].items():
        z = c["zero_crossings"]
        L.append(f"| {name} | " + " | ".join(f"{z[t]['teacher']} / {z[t]['token']} / {z[t]['residual']}" for t in ("0.5", "1.0", "2.0")) + " |")
    path.write_text("\n".join(L) + "\n")


def plot(r, profiles, t_eval, rbins, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for j, tq in enumerate((0.5, 1.0, 2.0)):
        f = int(np.argmin(np.abs(t_eval - tq)))
        ax = axes[0, j]
        pr = profiles["M2"]
        ax.plot(rbins, pr["eta"][f], "k", lw=1.5, label="teacher A=8")
        ax.plot(rbins, pr["K"][f], "C0", lw=1, label="M2 token")
        ax.plot(rbins, pr["R"][f], "C3", lw=1, label="residual")
        ax.plot(rbins, profiles["M0"]["R"][f], "C1", lw=0.8, ls="--", label="residual, fixed token")
        ax.set_title(f"radial profile, t = {tq} s")
        ax.set_xlabel("r (m)")
        if j == 0:
            ax.legend(fontsize=8)
    ax = axes[1, 0]
    names = list(r["cells"].keys())
    for k, lab in (("gain_phase_global", "global gain+shift"), ("gain_phase_per_frame", "per-frame gain+shift"), ("gain_phase_per_radius", "per-radius gain+shift"), ("floor_share", "along A=1 floor residual")):
        ax.plot(range(len(names)), [r["cells"][n].get(k, np.nan) for n in names], "o-", label=lab)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, fontsize=8)
    ax.set_ylabel("share of residual energy explained")
    ax.legend(fontsize=8)
    ax = axes[1, 1]
    ax.plot(range(len(names)), [r["cells"][n]["near_early_share_residual"] for n in names], "o-", label="residual in r<0.5 m, t<1 s")
    ax.plot(range(len(names)), [r["cells"][n]["near_early_share_teacher"] for n in names], "s--", label="teacher energy in same box")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, fontsize=8)
    ax.legend(fontsize=8)
    ax = axes[1, 2]
    ax.plot(range(len(names)), [r["cells"][n]["crest_trough_teacher"] for n in names], "o-", label="teacher crest/trough")
    ax.plot(range(len(names)), [r["cells"][n]["crest_trough_token"] for n in names], "s--", label="token crest/trough")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, fontsize=8)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
