"""Teacher runs for the gait case: one trajectory per (body, seed), saved as qpos at 50 Hz with the
same planner and cost as iteration 7 of the feasibility build. The design teachers are iteration 7's
own runs (seed 0 of the seven bodies); this script produces the transfer teachers: the right-side
mirrors of the five impairments, and a second seed of the intact and legless bodies."""
from __future__ import annotations
import json, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait import biped, mpc
from poc.gait.feasibility import metrics, strip, DURATION

OUT = Path("poc/results")
DESIGN = [(m, 0) for m in biped.MORPHS]
TRANSFER = [(m, 0) for m in biped.MIRRORS] + [("intact", 1), ("nolegs", 1)]
# G3: a second run of every remaining body, so that every case has a held-out realisation of its own teacher
HELDOUT = [(m, 1) for m in ("weak_hip_left", "locked_knee_left", "short_shank_left", "stump_left", "noleg_left")] + [(m, 1) for m in biped.MIRRORS]
# G4: a third run of every body, so that acceptance can be judged against two held-out runs
THIRD = [(m, 2) for m in biped.MORPHS + biped.MIRRORS]


def path(morph, seed):
    return OUT / f"gait_teacher_{morph}_s{seed}_qpos.npy"


def run(morph, seed):
    T0 = time.time()
    m, d = biped.make(morph)
    sens, qpos, ctrl, cost, contacts = mpc.run(m, d, DURATION, seed=seed)
    met = metrics(m, sens, qpos, contacts)
    np.save(path(morph, seed), qpos)
    strip(m, qpos, str(OUT / f"gait_teacher_{morph}_s{seed}.png"), f"{morph} seed {seed}: speed {met['speed']:.2f} m/s, torso z {met['torso_z']:.2f}")
    met["seconds"] = round(time.time() - T0)
    return met


def _run(job):
    return job, run(*job)


def main(which, workers=1):
    jobs = {"transfer": TRANSFER, "design": DESIGN, "heldout": HELDOUT, "third": THIRD}[which]
    log = {}
    if workers > 1:
        from multiprocessing import Pool
        with Pool(workers) as pool:
            for (morph, seed), met in pool.imap_unordered(_run, jobs):
                log[f"{morph}_s{seed}"] = met
                print(f"{morph} s{seed}: speed {met['speed']:.2f} torso z {met['torso_z']:.2f} stance " +
                      ", ".join(f"{k} {v:.2f}" for k, v in met["stance"].items() if v > 0) + f" airborne {met['no_contact']:.2f} [{met['seconds']}s]", flush=True)
                json.dump(log, open(OUT / f"gait_teacher_{which}.json", "w"), indent=1)
        return
    for morph, seed in jobs:
        if which == "design" and seed == 0 and (OUT / f"gait_iter7_{morph}_qpos.npy").exists():
            shutil.copy(OUT / f"gait_iter7_{morph}_qpos.npy", path(morph, seed))
            print(f"{morph} s{seed}: copied from iteration 7", flush=True); continue
        met = run(morph, seed)
        log[f"{morph}_s{seed}"] = met
        print(f"{morph} s{seed}: speed {met['speed']:.2f} torso z {met['torso_z']:.2f} stance " +
              ", ".join(f"{k} {v:.2f}" for k, v in met["stance"].items() if v > 0) + f" airborne {met['no_contact']:.2f} [{met['seconds']}s]", flush=True)
        json.dump(log, open(OUT / f"gait_teacher_{which}.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "transfer", int(sys.argv[2]) if len(sys.argv) > 2 else 1)
