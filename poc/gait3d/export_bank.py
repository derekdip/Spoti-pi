"""The motion bank for an engine: every clip the cycle runtime plays, as JSON, with the skeleton it
plays on. docs/implementation-handoff.md describes the format and the player an engine needs.

  python3 poc/gait3d/export_bank.py            -> poc/results/gait_bank.json

Per clip: the body it plays on, its kind (teacher cycle, teacher loop, edited clip, composed edit),
the joint names, angles per phase bin (radians), the root's orientation per bin as a unit quaternion
(w, x, y, z), the root's height per bin as played on that body (root_z, metres, the floor at 0), its
forward displacement from the clip's start at the nb + 1 phase edges (dx) and lateral offset (dy), the
cycle duration in seconds, and the clip's clearance per bin. Playing a clip: phase advances by
dt / dur; joints and orientation are interpolated at the phase; the root moves by dx's difference
(plus dx[-1] per wrap); the root's height is root_z at the phase.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.gait3d import biped3d, grammar3d as G, rgre_gait3d as RG, cycle_runtime as CR, clip_edit as CE
from poc.gait3d.runtime import state_from_json


def skeleton(morph):
    body = G.Body(morph); m = body.m; out = dict(morph=morph, joints=[], geoms=[])
    for j in range(m.njnt):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
        if name == "root": continue
        parent = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.body_parentid[m.jnt_bodyid[j]])
        out["joints"].append(dict(name=name, body=mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.jnt_bodyid[j]), parent=parent,
                                  axis=[float(x) for x in m.jnt_axis[j]], pos_in_parent=[round(float(x), 4) for x in m.body_pos[m.jnt_bodyid[j]]],
                                  range_rad=[round(float(x), 4) for x in m.jnt_range[j]]))
    for g in range(m.ngeom):
        if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_PLANE: continue
        kind = {int(mujoco.mjtGeom.mjGEOM_CAPSULE): "capsule", int(mujoco.mjtGeom.mjGEOM_SPHERE): "sphere", int(mujoco.mjtGeom.mjGEOM_BOX): "box"}[int(m.geom_type[g])]
        out["geoms"].append(dict(name=mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g), body=mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]), kind=kind,
                                 size=[round(float(x), 4) for x in m.geom_size[g]], pos_in_body=[round(float(x), 4) for x in m.geom_pos[g]],
                                 quat_in_body=[round(float(x), 4) for x in m.geom_quat[g]]))
    return out


def root_z(prof: CR.CycleProfile, body: G.Body):
    """The root's height per bin as the player sets it on this body."""
    m, d = body.m, body.d; nb = len(prof.angles); z = np.zeros(nb)
    for b in range(nb):
        d.qpos[:] = 0.0; d.qpos[3:7] = prof.quat[b]
        for n, a in body.jadr.items():
            if n in prof.joints: d.qpos[a] = prof.angles[b, prof.joints.index(n)]
        mujoco.mj_kinematics(m, d); low = float(body.lowest(body.all_gids).min())
        z[b] = (-low + prof.clear[b]) if prof.clear is not None else max(prof.z[b], -low)
    return z


def entry(cid, kind, prof: CR.CycleProfile, body: G.Body, note=""):
    return dict(id=cid, kind=kind, body=body.morph, note=note, joints=prof.joints, nb=len(prof.angles), dur=round(prof.dur, 5),
                angles=prof.angles.round(5).tolist(), quat_wxyz=prof.quat.round(5).tolist(), root_z=root_z(prof, body).round(4).tolist(),
                dx=prof.dx.round(4).tolist(), dy=prof.dy.round(4).tolist(), clear=(prof.clear.round(4).tolist() if prof.clear is not None else None))


def main(out_path="poc/results/gait_bank.json"):
    ref = RG.load_v0(); clips = []; skel = {}
    bodies = list(biped3d.MORPHS) + list(biped3d.MIRRORS) + list(biped3d.COMBINED)
    for morph in bodies:
        body = G.Body(morph); skel[morph] = skeleton(morph)
        if morph in biped3d.COMBINED and not Path(f"poc/results/gait3d_teacher_{morph}_s0_qpos.npy").exists(): continue
        loop = morph in CR.LOOP_BODIES or (biped3d.legless(morph))
        prof = (CR.CycleProfile.from_teacher_loop(morph, 0) if loop else CR.CycleProfile.from_teacher(morph, 0)).with_clearance(body)
        clips.append(entry(f"{morph}/teacher", "teacher loop" if loop else "teacher cycle", prof, body, "the physics teacher's own motion, seed 0"))
        print(morph, "teacher", "loop" if loop else "cycle", flush=True)
    g13 = {c["case"]: c for c in json.load(open("poc/results/g13.json"))["cases"]}
    for morph in biped3d.MORPHS:
        c = g13[f"{morph}_s0"]; body = G.Body(morph); st = state_from_json(c["state"])
        prof = CE.edited_profile(st, body, ref, CE.base_clip(), "clearance")
        added = [f"{a}{s:+d}" if s else a for a, s in c["added"]]
        clips.append(entry(f"{morph}/intact-clip+edits", "edited clip", prof, body, f"the intact teacher's cycle with the edits G13 fitted to this body: {added}; the parametric state is in poc/results/g13.json"))
    g14 = json.load(open("poc/results/g14.json"))
    for morph, entries in g14["compositions"].items():
        body = G.Body(morph); base = CE.base_clip(morph="nolegs") if biped3d.legless(morph) else CE.base_clip()
        for label, v in entries.items():
            if label.startswith("raw"): continue
            prof = CE.edited_profile(state_from_json(v["state"]), body, ref, base, "clearance")
            clips.append(entry(f"{morph}/" + ("composed" if label == "composed" else "carried-edit"), "composed edit" if label == "composed" else "edited clip", prof, body, f"{label}; nothing fitted on this body (G14)"))
    for c in g14["cases"]:
        if c["group"] == "pilot" or not c["added"]: continue
        morph = c["morph"]; body = G.Body(morph); base = CE.base_clip(morph="nolegs") if biped3d.legless(morph) else CE.base_clip()
        prof = CE.edited_profile(state_from_json(c["state"]), body, ref, base, "clearance")
        added = [f"{a}{s:+d}" if s else a for a, s in c["added"]]
        clips.append(entry(f"{morph}/base-clip+edits", "edited clip", prof, body, f"the base clip with the edits G14 fitted to this body: {added}"))
    style = dict(joint_offsets=CR.STYLE, torso_pitch_rad=CR.STYLE_PITCH, arm_swing_kept=0.25, note="the style layer: add the offsets to the shoulders and elbows, keep a quarter of their swing, pitch the torso forward; the legless body keeps its arms and its pitch")
    conventions = dict(units="metres, radians, seconds", up="+z", forward="+x", root="free joint: position (x, y, z) then orientation quaternion (w, x, y, z), world frame",
                       hinges="every joint is a hinge; hip_y, knee, ankle_y, shoulder, elbow about the body's +y (hip flexion forward is negative, knee flexion positive); hip_x and ankle_x about +x (a positive left hip_x abducts the left leg, a positive right hip_x adducts the right)",
                       phase="a clip is periodic in phase in [0, 1); bins are at phase b / nb; interpolate linearly between bins (quaternions by normalised interpolation); dx and dy have nb + 1 entries at the phase edges 0, 1/nb, ..., 1",
                       playing="phase += dt / dur; root.x += dx(phase1) - dx(phase0) + dx[nb] per wrap; root.y = start + dy(phase); root.z = root_z(phase); joints = angles(phase); orientation = quat(phase)",
                       transitions="blend two clips in phase space over about a second (joints, orientation, dur, dx, dy, root_z interpolated; joints only one clip has enter at that clip's values); switch the skeleton at the start of the blend; the phase and the root position are continuous",
                       fps_source=50.0, phase_bins=32, teacher_window_s=[1.0, 5.0])
    json.dump(dict(conventions=conventions, style=style, skeletons=skel, clips=clips), open(out_path, "w"), separators=(",", ":"))
    print("clips", len(clips), "skeletons", len(skel), "size", Path(out_path).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:])
