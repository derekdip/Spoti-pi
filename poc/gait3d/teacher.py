"""Teacher runs for the 3D gait case: one trajectory per (body, seed) as qpos at 50 Hz, the planner
and cost of the feasibility build's final iteration. Every body gets three seeds so that the growth
rule of the 2D case (fit on one run, accept on the mean of two held-out runs) applies unchanged.
  python3 poc/gait3d/teacher.py {design|transfer|all} [workers]"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, mpc3d
from poc.gait3d.feasibility3d import metrics, strip, DURATION

OUT = Path("poc/results")
SEEDS = (0, 1, 2)
DESIGN = [(m, s) for m in biped3d.MORPHS for s in SEEDS]
TRANSFER = [(m, s) for m in biped3d.MIRRORS for s in SEEDS]


def path(morph, seed):
    return OUT / f"gait3d_teacher_{morph}_s{seed}_qpos.npy"


def run(morph, seed):
    T0 = time.time()
    m, d = biped3d.make(morph)
    sens, qpos, ctrl, cost, contacts = mpc3d.run(m, d, DURATION, seed=seed)
    met = metrics(m, sens, qpos, contacts)
    np.save(path(morph, seed), qpos)
    strip(m, qpos, str(OUT / f"gait3d_teacher_{morph}_s{seed}.png"), f"{morph} seed {seed}: speed {met['speed']:.2f} m/s, torso z {met['torso_z']:.2f}, tilt {met['tilt']:.2f}")
    met["seconds"] = round(time.time() - T0)
    return met


def _run(job):
    return job, run(*job)


def main(which, workers=1):
    jobs = {"design": DESIGN, "transfer": TRANSFER, "all": DESIGN + TRANSFER}[which]
    jobs = [j for j in jobs if not path(*j).exists()]
    log_path = OUT / f"gait3d_teacher_{which}.json"
    log = json.load(open(log_path)) if log_path.exists() else {}
    def record(morph, seed, met):
        log[f"{morph}_s{seed}"] = met
        print(f"{morph} s{seed}: speed {met['speed']:.2f} drift {met['drift']:.2f} tilt {met['tilt']:.2f} stance " +
              ", ".join(f"{k} {v:.2f}" for k, v in met["stance"].items() if v > 0) + f" airborne {met['no_contact']:.2f} [{met['seconds']}s]", flush=True)
        json.dump(log, open(log_path, "w"), indent=1)
    if workers > 1:
        from multiprocessing import Pool
        with Pool(workers) as pool:
            for (morph, seed), met in pool.imap_unordered(_run, jobs):
                record(morph, seed, met)
        return
    for morph, seed in jobs:
        record(morph, seed, run(morph, seed))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "design", int(sys.argv[2]) if len(sys.argv) > 2 else 1)
