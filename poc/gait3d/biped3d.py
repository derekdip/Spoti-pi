"""A three-dimensional biped for the gait teacher: the planar body of poc/gait/biped.py given a free
root (position and orientation), hip abduction and ankle roll on each leg, and box feet. Morphologies
damage or remove parts of the legs and nothing else changes, as in 2D:

  intact, weak_hip_*, locked_knee_*, short_shank_*, stump_*, noleg_*, nolegs

Joints per leg: hip_x (abduction, about the body's x axis), hip_y (flexion), knee, ankle_y (pitch),
ankle_x (roll). Arms as in 2D: shoulder pitch and elbow. Position actuators with bounded force.
"""
from __future__ import annotations
import numpy as np
import mujoco

MORPHS = ("intact", "weak_hip_left", "locked_knee_left", "short_shank_left", "stump_left", "noleg_left", "nolegs")
MIRRORS = ("weak_hip_right", "locked_knee_right", "short_shank_right", "stump_right", "noleg_right")
# G14: damages combined with '+', and arms removed (noarm_*). A combined morph applies each part in turn;
# the bodies above are unchanged (their XML is compared in the G14 prereg).
COMBINED = ("noarm_left", "locked_knee_left+weak_hip_right", "locked_knee_left+noarm_right", "nolegs+noarm_left")
LEG_KINDS = ("weak_hip", "locked_knee", "short_shank", "stump", "noleg")
SHANK = 0.42
STAND_Z = 1.17
SPEED_TARGET = 0.6      # m/s: below the 2D target of 0.8, at which the planar teacher ran rather than walked
LEG_JOINTS = ("hip_x", "hip_y", "knee", "ankle_y", "ankle_x")
KP = {"hip_x": 200, "hip_y": 300, "knee": 300, "ankle_y": 100, "ankle_x": 60, "shoulder": 150, "elbow": 100}
FMAX = {"hip_x": 120, "hip_y": 150, "knee": 150, "ankle_y": 60, "ankle_x": 40, "shoulder": 60, "elbow": 40}
RANGE_DEG = {"hip_x": (-30, 30), "hip_y": (-110, 30), "knee": (0, 150), "ankle_y": (-45, 45), "ankle_x": (-20, 20), "shoulder": (-180, 60), "elbow": (-150, 0)}


def _leg(side, stump=False, shank=SHANK, knee_range=(0, 150)):
    y = 0.09 if side == "l" else -0.09
    s = f'''
      <body name="thigh_{side}" pos="0 {y} -0.25">
        <joint name="hip_x_{side}" axis="1 0 0" range="-30 30"/>
        <joint name="hip_y_{side}" axis="0 1 0" range="-110 30"/>
        <geom name="thigh_{side}" type="capsule" fromto="0 0 0 0 0 -0.42" size="0.06"/>
        <site name="knee_{side}" pos="0 0 -0.42" size="0.07" type="sphere" rgba="0 0 0 0"/>'''
    if not stump:
        s += f'''
        <body name="shank_{side}" pos="0 0 -0.42">
          <joint name="knee_{side}" axis="0 1 0" range="{knee_range[0]} {knee_range[1]}"/>
          <geom name="shank_{side}" type="capsule" fromto="0 0 0 0 0 -{shank}" size="0.05"/>
          <body name="foot_{side}" pos="0 0 -{shank}">
            <joint name="ankle_y_{side}" axis="0 1 0" range="-45 45"/>
            <joint name="ankle_x_{side}" axis="1 0 0" range="-20 20"/>
            <geom name="foot_{side}" type="box" pos="0.04 0 -0.04" size="0.12 0.05 0.02"/>
            <site name="foot_{side}" pos="0.04 0 -0.04" size="0.13 0.06 0.03" type="box" rgba="0 0 0 0"/>
          </body>
        </body>'''
    s += '''
      </body>'''
    return s


def _arm(side):
    # iteration 7f (docs/gait3d-feasibility.md): shoulders at 0.20 m from the midline, not 0.14. The
    # hands hang at pelvis height, and against a pelvis box 0.13 m wide a hand at 0.14 m jammed on it
    # within a second of swinging; every teacher up to iteration 7e had still arms for this reason.
    y = 0.20 if side == "l" else -0.20
    return f'''
      <body name="uarm_{side}" pos="0 {y} 0.22">
        <joint name="shoulder_{side}" axis="0 1 0" range="-180 60"/>
        <geom name="uarm_{side}" type="capsule" fromto="0 0 0 0 0 -0.28" size="0.04"/>
        <body name="larm_{side}" pos="0 0 -0.28">
          <joint name="elbow_{side}" axis="0 1 0" range="-150 0"/>
          <geom name="larm_{side}" type="capsule" fromto="0 0 0 0 0 -0.26" size="0.035"/>
          <body name="hand_{side}" pos="0 0 -0.28">
            <geom name="hand_{side}" type="sphere" size="0.045"/>
            <site name="hand_{side}" size="0.06" type="sphere" rgba="0 0 0 0"/>
          </body>
        </body>
      </body>'''


def side_of(morph):
    """(side, kind) of the first leg damage in the morph name; (None, morph) for a body with none."""
    for part in morph.split("+"):
        for k in LEG_KINDS:
            if part.startswith(k + "_"):
                return part[len(k) + 1:], k
    return None, morph


def parts_of(morph):
    """The body's parts: per leg its kind ('normal', a leg damage, or 'missing') and per arm whether it
    is there. A combined morph applies each '+' part in turn; 'nolegs' removes both legs."""
    legs = {"l": "normal", "r": "normal"}; arms = {"l": True, "r": True}
    for part in morph.split("+"):
        if part == "intact": continue
        if part == "nolegs": legs["l"] = legs["r"] = "missing"; continue
        if part.startswith("noarm_"): arms[part[6]] = False; continue
        side, kind = side_of(part)
        assert side in ("left", "right") and kind in LEG_KINDS, part
        legs[side[0]] = "missing" if kind == "noleg" else kind
    return legs, arms


def leg_order(legs):
    """Legs in the body's XML order: a stump first, as the stump bodies were built (their teacher runs
    store qpos in that order), else left then right."""
    return sorted("lr", key=lambda s: (legs[s] != "stump", s))


def present_joints(morph):
    legs, arms = parts_of(morph); out = []
    for s in leg_order(legs):
        if legs[s] == "stump": out += [f"hip_x_{s}", f"hip_y_{s}"]
        elif legs[s] != "missing": out += [f"{j}_{s}" for j in LEG_JOINTS]
    for s in "lr":
        if arms[s]: out += [f"shoulder_{s}", f"elbow_{s}"]
    return out


def legless(morph):
    return all(k == "missing" for k in parts_of(morph)[0].values())


def build_xml(morph="intact", z0=None):
    assert morph in MORPHS or morph in MIRRORS or morph in COMBINED, morph
    legs_k, arms_p = parts_of(morph)
    knee_rng = {s: ((0, 3) if legs_k[s] == "locked_knee" else (0, 150)) for s in "lr"}
    legs = ""
    for s in leg_order(legs_k):
        k = legs_k[s]
        if k == "missing": continue
        if k == "stump": legs += _leg(s, stump=True); continue
        legs += _leg(s, shank=0.26 if k == "short_shank" else SHANK, knee_range=knee_rng[s])
    arm_xml = "".join(_arm(s) for s in "lr" if arms_p[s])
    present = present_joints(morph)
    if z0 is None:
        z0 = STAND_Z if not legless(morph) else 0.6
    kind_of = lambda j: j.rsplit("_", 1)[0]
    kp = {j: KP[kind_of(j)] for j in present}
    for s in "lr":
        if legs_k[s] == "weak_hip":
            kp[f"hip_x_{s}"] = KP["hip_x"] // 5; kp[f"hip_y_{s}"] = KP["hip_y"] // 5
    rng = {j: RANGE_DEG[kind_of(j)] for j in present}
    for s in "lr":
        if f"knee_{s}" in rng: rng[f"knee_{s}"] = knee_rng[s]
    def _rng(j):
        lo, hi = rng[j]; return f"{np.radians(lo):.4f} {np.radians(hi):.4f}"
    actuators = "\n".join(f'    <position name="p_{j}" joint="{j}" kp="{kp[j]}" ctrlrange="{_rng(j)}" forcerange="-{FMAX[kind_of(j)]} {FMAX[kind_of(j)]}"/>' for j in present)
    jointsensors = "\n".join(f'    <jointpos name="q_{j}" joint="{j}"/>' for j in present)
    feet = [s_ for s_ in "lr" if f"knee_{s_}" in present]           # a foot exists where a knee does
    footsensors = "\n".join(f'    <framepos name="foot_pos_{s_}" objtype="site" objname="foot_{s_}"/>' for s_ in feet)
    return f'''
<mujoco model="biped3d_{morph}">
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <default>
    <joint damping="3.0" armature="0.02" limited="true"/>
    <geom condim="3" friction="1.0 0.005 0.0001" density="1000" contype="1" conaffinity="1"/>
    <position ctrllimited="true"/>
  </default>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="40 40 0.1" pos="0 0 0" friction="1.0 0.005 0.0001"/>
    <body name="torso" pos="0 0 {z0}">
      <freejoint name="root"/>
      <geom name="torso" type="capsule" fromto="0 0 -0.25 0 0 0.25" size="0.09"/>
      <geom name="pelvis" type="box" pos="0 0 -0.28" size="0.14 0.13 0.04"/>
      <site name="torso_site" pos="0 0 0" size="0.01" rgba="0 0 0 0"/>
      <body name="head" pos="0 0 0.38">
        <geom name="head" type="sphere" size="0.1"/>
        <site name="head" pos="0 0 0" size="0.01" rgba="0 0 0 0"/>
      </body>{arm_xml}{legs}
    </body>
  </worldbody>
  <actuator>
{actuators}
  </actuator>
  <sensor>
    <framepos name="torso_pos" objtype="site" objname="torso_site"/>
    <framelinvel name="torso_vel" objtype="site" objname="torso_site"/>
    <framezaxis name="torso_up" objtype="site" objname="torso_site"/>
    <framexaxis name="torso_fwd" objtype="site" objname="torso_site"/>
    <framepos name="head_pos" objtype="site" objname="head"/>
{jointsensors}
{footsensors}
  </sensor>
</mujoco>'''


def rest_pose(m, d, morph):
    """Standing on what legs the body has; the legless body prone, head forward, arms ahead, hands on
    the floor, as in 2D (iteration 7)."""
    d.qpos[:] = 0; d.qpos[3] = 1.0
    if not legless(morph):
        d.qpos[2] = STAND_Z; mujoco.mj_forward(m, d); return
    d.qpos[3:7] = [np.cos(np.pi / 4), 0.0, np.sin(np.pi / 4), 0.0]     # pitched forward by 90 degrees
    shoulders = [m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"shoulder_{s}")] for s in "lr" if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"shoulder_{s}") >= 0]
    hid = next(mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"hand_{s}") for s in "lr" if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"hand_{s}") >= 0)
    best = None
    for ang in np.linspace(-np.pi, np.radians(60), 61):
        for j in shoulders: d.qpos[j] = ang
        mujoco.mj_forward(m, d)
        x = d.site_xpos[hid][0]
        if best is None or x > best[0]:
            best = (x, ang)
    for j in shoulders: d.qpos[j] = best[1]
    mujoco.mj_forward(m, d)
    lowest = min(d.geom_xpos[g][2] - m.geom_rbound[g] for g in range(m.ngeom) if m.geom_type[g] != mujoco.mjtGeom.mjGEOM_PLANE)
    d.qpos[2] -= lowest - 0.01
    d.qvel[:] = 0
    mujoco.mj_forward(m, d)


def make(morph="intact"):
    m = mujoco.MjModel.from_xml_string(build_xml(morph))
    d = mujoco.MjData(m)
    rest_pose(m, d, morph)
    return m, d


def sensor_index(m):
    out = {}
    for i in range(m.nsensor):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_SENSOR, i)
        out[name] = (int(m.sensor_adr[i]), int(m.sensor_dim[i]))
    return out
