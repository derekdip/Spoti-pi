"""Frames for the web viewer: world-space pose of every geom per frame. Three sources per design body:
the physics teacher, the cycle runtime playing the teacher's own motion (poc/gait3d/cycle_runtime.py,
the deployable description after G11), and the G11 fitted grammar state played by the parametric
runtime (kept for comparison: the viewer faulted it, docs/gait3d-runtime.md). Two transitions, one per
runtime. Written to poc/results/gait3d_web_data.json; the viewer embeds it."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import mujoco
from scipy.spatial.transform import Rotation
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, grammar3d as G, rgre_gait3d as RG
from poc.gait3d.runtime import Player, load_states
from poc.gait3d import cycle_runtime as CR
from dataclasses import replace

FPS = 25.0
# A style layer: a posture on top of a fitted gait, not fitted to anything. Arms forward and stiff,
# the head down, a little more forward lean. The fitted state carries the gait; these numbers carry
# the character, which is the point of a parametric state.
ZOMBIE = dict(arm_off=-1.35, arm_amp=0.08, arm_lag=0.0, elbow_off=-0.35, lean=0.22, pitch_amp=0.12)


def styled(st, morph):
    over = dict(ZOMBIE)
    if morph == "nolegs":                      # the crawl's arms are its legs: keep them, drop the head
        over = dict(lean=st.lean + 0.1)
    return replace(st, **over)


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


def speed_of(frames, fps=FPS):
    return (frames[-1, 0] - frames[0, 0]) / (len(frames) / fps)


def cycle_transition(profiles, style):
    """Intact walk from the teacher's cycle, the leg removed at 2 s, a one-second blend to the one-leg loop."""
    a, b = profiles["intact"], profiles["noleg_left"]
    if style: a, b = CR.styled(a), CR.styled(b)
    p = CR.CyclePlayer(a); before = p.frames(2.0, FPS); ib = p.body
    p.transition(b, 1.0); after = p.frames(3.0, FPS)
    return [dict(morph="intact", geoms=geoms_of(ib), frames=poses(ib, before)), dict(morph="noleg_left", geoms=geoms_of(p.body), frames=poses(p.body, after))]


def main(states_path="poc/results/g11.json", out_path="poc/results/gait3d_web_data.json", edits_path="poc/results/g13.json"):
    states = load_states(states_path)
    edits = load_states(edits_path) if Path(edits_path).exists() else {}
    clips = []
    profiles = {m: CR.profile_for(m) for m in biped3d.MORPHS}
    clips.append(dict(id="transition_cycle", title="Cycle runtime: intact walk from the teacher's cycle, left leg removed at 2.0 s, one-second blend to the one-leg loop", fps=FPS, segments=cycle_transition(profiles, False)))
    clips.append(dict(id="transition_cycle_zombie", title="Cycle runtime with the style layer: the same transition, arms forward and the torso pitched", fps=FPS, segments=cycle_transition(profiles, True)))
    # the parametric runtime's transition, from the G11 states
    p = Player("intact", states["intact_s0"]); before = p.frames(2.0, FPS); ib = p.body
    p.transition(states["noleg_left_s0"], 1.0, morph="noleg_left"); after = p.frames(3.0, FPS)
    clips.append(dict(id="transition", title="Parametric runtime (G11 states): intact walk, left leg removed at 2.0 s, one-second blend to the one-leg state", fps=FPS,
                      segments=[dict(morph="intact", geoms=geoms_of(ib), frames=poses(ib, before)), dict(morph="noleg_left", geoms=geoms_of(p.body), frames=poses(p.body, after))]))
    ps = Player("intact", styled(states["intact_s0"], "intact")); zb = ps.frames(2.0, FPS); zib = ps.body
    ps.transition(styled(states["noleg_left_s0"], "noleg_left"), 1.0, morph="noleg_left"); za = ps.frames(3.0, FPS)
    clips.append(dict(id="transition_zombie", title="Parametric runtime with the style layer: the same transition, arms forward and head down", fps=FPS,
                      segments=[dict(morph="intact", geoms=geoms_of(zib), frames=poses(zib, zb)), dict(morph="noleg_left", geoms=geoms_of(ps.body), frames=poses(ps.body, za))]))
    gstates = {c["case"]: c for c in json.load(open(states_path))["cases"]}
    for morph in biped3d.MORPHS:
        case = RG.GaitCase(morph, 0); st = states[f"{morph}_s0"]; geoms = geoms_of(case.body)
        teacher = case.q_teacher[::2]                                  # 50 to 25 frames a second
        v_t = speed_of(case.q_teacher, 50.0)
        clips.append(dict(id=f"{morph}_teacher", title=f"{morph}: the physics teacher (seed 0, seconds 1 to 5, {v_t:.2f} m/s)", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms, frames=poses(case.body, teacher))]))
        prof = profiles[morph]; loop = morph in CR.LOOP_BODIES
        what = f"the teacher's four-second window as a loop with a 0.3 s crossfaded seam" if loop else f"the teacher's mean cycle ({prof.dur:.2f} s, {len(prof.angles)} phase bins)"
        cp = CR.CyclePlayer(prof); cyc = cp.frames(4.0, FPS)
        clips.append(dict(id=f"{morph}_cycle", title=f"{morph}: {what}, played by the cycle runtime at {speed_of(cyc):.2f} m/s (teacher {v_t:.2f})", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms, frames=poses(case.body, cyc))]))
        cz = CR.CyclePlayer(CR.styled(prof)); cycz = cz.frames(4.0, FPS)
        clips.append(dict(id=f"{morph}_cycle_zombie", title=f"{morph}: the same clip with the style layer (arms forward, torso pitched), played by the cycle runtime", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms, frames=poses(case.body, cycz))]))
        if f"{morph}_s0" in edits:                                  # G13: the intact clip with that body's fitted edits
            from poc.gait3d import clip_edit as CEd
            ref = RG.load_v0(); ep = CEd.edited_profile(edits[f"{morph}_s0"], case.body, ref); ecl = CR.CyclePlayer(ep, body=case.body).frames(4.0, FPS)
            eadded = [f"{a}{s:+d}" if s else a for a, s in {c["case"]: c for c in json.load(open(edits_path))["cases"]}[f"{morph}_s0"]["added"]]
            clips.append(dict(id=f"{morph}_edit", title=f"{morph}: the intact teacher's cycle with the edits G13 fitted to this body (edits {eadded}), played by the cycle runtime at {speed_of(ecl):.2f} m/s (teacher {v_t:.2f})", fps=FPS,
                              segments=[dict(morph=morph, geoms=geoms, frames=poses(case.body, ecl))]))
        pl = Player(morph, st); student = pl.frames(4.0, FPS)
        added = [f"{a}{s:+d}" if s else a for a, s in gstates[f"{morph}_s0"]["added"]]
        clips.append(dict(id=f"{morph}_student", title=f"{morph}: the G11 fitted grammar state played by the parametric runtime (repairs {added}, error {case.error(st):.3f}, {speed_of(student):.2f} m/s)", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms, frames=poses(case.body, student))]))
        pz = Player(morph, styled(st, morph)); zombie = pz.frames(4.0, FPS)
        clips.append(dict(id=f"{morph}_zombie", title=f"{morph}: the G11 fitted state with the style layer (arms forward, head down), played by the parametric runtime", fps=FPS,
                          segments=[dict(morph=morph, geoms=geoms, frames=poses(case.body, zombie))]))
        print(f"{morph:<18} teacher {v_t:.2f} m/s; cycle runtime {speed_of(cyc):.2f}; parametric {speed_of(student):.2f}", flush=True)
    json.dump(dict(clips=clips), open(out_path, "w"), separators=(",", ":"))
    print("clips", len(clips), "size", Path(out_path).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:])
