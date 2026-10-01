"""Two checks on the runtime, declared as design checks and not preregistered.

Blend check: for every damaged design body with a fitted state (G7's terminal), the straight
parameter-space blend from the intact body's fitted state to the damaged one is played on the
damaged body at w = 0, 0.1, ..., 1 and scored against the damaged teacher with the consumers. A
blend that passes through states worse than both ends has a bump; the size of the largest bump, and
the fraction of frames with a joint outside the body's own range at w = 0.5 against the ends, are
the numbers.

Transition check: the intact body walks from its fitted state, at 2 s its left leg is removed and the
player blends to the one-leg body's fitted state over one second, then walks on. The largest joint
speed and root-height step across the switch frame against the same quantities inside the steady
gait, and a strip of the transition, are the output.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, grammar3d as G, rgre_gait3d as RG
from poc.gait3d.runtime import Player, blend, load_states, export, frame_at
from poc.gait3d.feasibility3d import _draw
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FPS = 50.0


def joint_range_violations(body, frames):
    m = body.m; out = 0; n = 0
    for j, name in enumerate(body.joints):
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, name); lo, hi = m.jnt_range[jid]
        a = frames[:, body.jadr[name]]; out += int(((a < lo) | (a > hi)).sum()); n += len(a)
    return out / max(n, 1)


def blend_check(states):
    src = states["intact_s0"]; rows = []
    for morph in ("weak_hip_left", "locked_knee_left", "short_shank_left", "stump_left", "noleg_left", "nolegs"):
        case = RG.GaitCase(morph, 0); dst = states[f"{morph}_s0"]
        ws = np.linspace(0, 1, 11); errs = []; viol = []
        for w in ws:
            st = blend(src, dst, float(w)); q = G.trajectory(st, case.body)
            errs.append(case.error(st)); viol.append(joint_range_violations(case.body, q))
        errs = np.array(errs); bump = float(max(0.0, errs.max() - max(errs[0], errs[-1])))
        mono = bool(np.all(np.diff(errs) <= 1e-6))
        rows.append(dict(morph=morph, errors=[round(float(e), 3) for e in errs], bump=round(bump, 3), monotone=mono,
                         violations=[round(float(v), 3) for v in (viol[0], viol[5], viol[-1])]))
        print(f"{morph:<18} error along the blend {np.round(errs, 3).tolist()}  bump {bump:.3f}  monotone {mono}  joint-range violations at w=0/0.5/1 {rows[-1]['violations']}", flush=True)
    return rows


def transition_check(states, out_png="poc/results/gait3d_runtime_transition.png", out_json="poc/results/gait3d_runtime_transition.json"):
    p = Player("intact", states["intact_s0"])
    before = p.frames(2.0, FPS)
    p.transition(states["noleg_left_s0"], 1.0, morph="noleg_left")
    after = p.frames(3.0, FPS)
    body_after = p.body
    # joint speeds in the frames after the switch, on the joints that remain, against steady speeds later on
    def speeds(fr, body):
        return np.abs(np.diff(fr[:, 7:], axis=0)) * FPS
    steady = speeds(after[int(1.5 * FPS):], body_after); switch = speeds(after[:int(0.2 * FPS)], body_after)
    # the same joints before the switch, matched by name
    ib = RG.Body("intact"); common = [n for n in body_after.joints if n in ib.jadr]
    qa_first = after[0]; qb_last = before[-1]
    step = {n: float(abs(qa_first[body_after.jadr[n]] - qb_last[ib.jadr[n]]) * FPS) for n in common}
    root_step = float(abs(after[0, 2] - before[-1, 2]))
    res = dict(max_joint_speed_at_switch=round(max(step.values()), 2), max_joint_speed_first_0p2s=round(float(switch.max()), 2),
               max_joint_speed_steady=round(float(steady.max()), 2), root_height_step_at_switch=round(root_step, 4),
               root_height_steady_max_step=round(float(np.abs(np.diff(after[int(1.5 * FPS):, 2])).max()), 4))
    print("transition:", res, flush=True)
    nb = len(before)
    idx = np.linspace(int(1.5 * FPS), int(3.6 * FPS), 8).astype(int)
    fig, axes = plt.subplots(2, len(idx), figsize=(2.1 * len(idx), 6.2))
    for j, k in enumerate(idx):
        body, fr = (ib, before[k]) if k < nb else (body_after, after[k - nb])
        body.d.qpos[:] = fr; mujoco.mj_kinematics(body.m, body.d)
        for r, view in ((0, "side"), (1, "front")):
            ax = axes[r, j]; _draw(ax, body.m, body.d, fr[0], fr[1], view)
            ax.axhline(0, color="0.6", lw=1); ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.05, 1.7); ax.set_aspect("equal"); ax.axis("off")
            if r == 0: ax.set_title(f"{k / FPS:.2f}s {'intact' if k < nb else 'one leg'}", fontsize=8)
    fig.suptitle("runtime: intact walk, left leg removed at 2.0 s, one-second blend to the one-leg state", fontsize=10)
    fig.tight_layout(); fig.savefig(out_png, dpi=75); plt.close(fig)
    json.dump(dict(check=res, export_after=export(after, body_after, FPS)), open(out_json, "w"))
    return res


if __name__ == "__main__":
    states = load_states()
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out_path = Path("poc/results/gait3d_runtime_check.json")
    prev = json.load(open(out_path)) if out_path.exists() else {}
    if which in ("all", "blend"):
        prev["blend"] = blend_check(states)
    if which in ("all", "transition"):
        prev["transition"] = transition_check(states)
    json.dump(prev, open(out_path, "w"), indent=1)
