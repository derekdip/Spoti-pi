"""Frames for the web viewer: world-space pose of every geom per frame, for the runtime transition
and for each design body's fitted gait (the player) and its physics teacher. Written to
poc/results/gait3d_web_data.json; the viewer embeds it."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, grammar3d as G, rgre_gait3d as RG
from poc.gait3d.runtime import Player, load_states

FPS = 25.0


def geoms_of(body):
    m = body.m; out = []
    for g in range(m.ngeom):
        t = m.geom_type[g]
        if t == mujoco.mjtGeom.mjGEOM_PLANE: continue
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g)
        kind = {int(mujoco.mjtGeom.mjGEOM_CAPSULE): "capsule", int(mujoco.mjtGeom.mjGEOM_SPHERE): "sphere", int(mujoco.mjtGeom.mjGEOM_BOX): "box"}[int(t)]
        out.append(dict(name=name, kind=kind, size=[round(float(x), 4) for x in m.geom_size[g]]))
    return out


def poses(body, frames):
    m, d = body.m, body.d; gids = [g for g in range(m.ngeom) if m.geom_type[g] != mujoco.mjtGeom.mjGEOM_PLANE]
    out = []
    for q in frames:
        d.qpos[:] = q; mujoco.mj_kinematics(m, d)
        row = []
        for g in gids:
            p = d.geom_xpos[g]; quat = Rotation.from_matrix(d.geom_xmat[g].reshape(3, 3)).as_quat()
            row += [round(float(v), 3) for v in p] + [round(float(v), 3) for v in quat]
        out.append(row)
    return out


def main():
    states = load_states()
    clips = []
    # the transition: intact walk, leg removed at 2 s, one-second blend to the one-leg state
    p = Player("intact", states["intact_s0"]); before = p.frames(2.0, FPS); ib = p.body
    p.transition(states["noleg_left_s0"], 1.0, morph="noleg_left"); after = p.frames(3.0, FPS)
    clips.append(dict(id="transition", title="Runtime: intact walk, left leg removed at 2.0 s, one-second blend to the one-leg state", fps=FPS,
                      segments=[dict(morph="intact", geoms=geoms_of(ib), frames=poses(ib, before)), dict(morph="noleg_left", geoms=geoms_of(p.body), frames=poses(p.body, after))]))
    g7 = {c["case"]: c for c in json.load(open("poc/results/g7.json"))["cases"]}
    for morph in biped3d.MORPHS:
        case = RG.GaitCase(morph, 0); st = states[f"{morph}_s0"]
        pl = Player(morph, st); student = pl.frames(4.0, FPS)
        teacher = case.q_teacher[::2]                                  # 50 to 25 frames a second
        added = [f"{a}{s:+d}" if s else a for a, s in g7[f"{morph}_s0"]["added"]]
        clips.append(dict(id=f"{morph}_student", title=f"{morph}: the fitted state played by the runtime (repairs {added}, error {case.error(st):.3f})", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms_of(case.body), frames=poses(case.body, student))]))
        clips.append(dict(id=f"{morph}_teacher", title=f"{morph}: the physics teacher (seed 0, seconds 1 to 5)", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms_of(case.body), frames=poses(case.body, teacher))]))
        print(morph, "student frames", len(student), "teacher frames", len(teacher), flush=True)
    json.dump(dict(clips=clips), open("poc/results/gait3d_web_data.json", "w"), separators=(",", ":"))
    print("clips", len(clips), "size", Path("poc/results/gait3d_web_data.json").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
