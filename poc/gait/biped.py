"""A planar biped for the gait feasibility check: torso, head, two arms, two legs, all joints about
the y axis, the root free in x, z and pitch. Morphologies remove parts of the legs, nothing else
changes: same masses elsewhere, same actuators on what remains, same sensors where they exist.

  The torso ends in a flat pelvis box (iteration 4): a legless body can sit on it and cannot
  balance and hop on a rounded torso end, which iteration 3's controller had found.

  intact        both legs
  stump_left    left shank and foot removed: the left leg ends at the knee
  noleg_left    left leg removed at the hip
  nolegs        both legs removed at the hip
"""
from __future__ import annotations
import numpy as np
import mujoco

MORPHS = ("intact", "weak_hip_left", "locked_knee_left", "short_shank_left", "stump_left", "noleg_left", "nolegs")
MIRRORS = ("weak_hip_right", "locked_knee_right", "short_shank_right", "stump_right", "noleg_right")   # the transfer bodies
# iteration 6: a limp needs a leg that is present and impaired, so three impairments join the removals:
#   weak_hip_left      the left hip actuator at a fifth of its gain
#   locked_knee_left   the left knee's range closed to three degrees: a stiff leg
#   short_shank_left   the left shank 0.16 m shorter: a leg-length discrepancy
SHANK = 0.42
STAND_Z = 1.16          # torso centre when standing on straight legs
SPEED_TARGET = 0.8      # m/s, the same for every morphology


def _leg(side, stump=False, shank=SHANK, knee_range=(0, 150)):
    y = 0.08 if side == "l" else -0.08
    s = f'''
      <body name="thigh_{side}" pos="0 {y} -0.25">
        <joint name="hip_{side}" axis="0 1 0" range="-110 30"/>
        <geom name="thigh_{side}" type="capsule" fromto="0 0 0 0 0 -0.42" size="0.06"/>
        <site name="knee_{side}" pos="0 0 -0.42" size="0.07" type="sphere" rgba="0 0 0 0"/>'''
    if not stump:
        s += f'''
        <body name="shank_{side}" pos="0 0 -0.42">
          <joint name="knee_{side}" axis="0 1 0" range="{knee_range[0]} {knee_range[1]}"/>
          <geom name="shank_{side}" type="capsule" fromto="0 0 0 0 0 -{shank}" size="0.05"/>
          <body name="foot_{side}" pos="0 0 -{shank}">
            <joint name="ankle_{side}" axis="0 1 0" range="-45 45"/>
            <geom name="foot_{side}" type="capsule" fromto="-0.08 0 -0.03 0.16 0 -0.03" size="0.03"/>
            <site name="foot_{side}" pos="0.04 0 -0.03" size="0.14 0.05 0.05" type="box" rgba="0 0 0 0"/>
          </body>
        </body>'''
    s += '''
      </body>'''
    return s


def _arm(side):
    y = 0.12 if side == "l" else -0.12
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
    """('left' | 'right' | None, kind): which side an impairment is on, and what it is."""
    for k in ("weak_hip", "locked_knee", "short_shank", "stump", "noleg"):
        if morph.startswith(k + "_"):
            return morph[len(k) + 1:], k
    return None, morph


def build_xml(morph="intact", z0=None):
    assert morph in MORPHS or morph in MIRRORS
    full = ["hip_l", "knee_l", "ankle_l", "hip_r", "knee_r", "ankle_r", "shoulder_l", "elbow_l", "shoulder_r", "elbow_r"]
    arms = ["shoulder_l", "elbow_l", "shoulder_r", "elbow_r"]
    side, kind = side_of(morph)
    a = side[0] if side else None                     # the impaired side's letter
    b = ("r" if a == "l" else "l") if a else None     # the other side
    knee_rng = {"l": (0, 150), "r": (0, 150)}
    if kind == "locked_knee":
        knee_rng[a] = (0, 3)
    if kind == "stump":
        legs = _leg(a, stump=True) + _leg(b); present = [f"hip_{a}", f"hip_{b}", f"knee_{b}", f"ankle_{b}"] + arms
    elif kind == "noleg":
        legs = _leg(b); present = [f"hip_{b}", f"knee_{b}", f"ankle_{b}"] + arms
    elif morph == "nolegs":
        legs = ""; present = arms
    else:
        legs = (_leg("l", shank=0.26 if (kind == "short_shank" and a == "l") else SHANK, knee_range=knee_rng["l"])
                + _leg("r", shank=0.26 if (kind == "short_shank" and a == "r") else SHANK, knee_range=knee_rng["r"]))
        present = full
    if z0 is None:
        z0 = STAND_Z if morph != "nolegs" else 0.6
    # iteration 3 (docs/gait-feasibility.md): position actuators, so that zero action holds the
    # initial pose stiffly and the sampler explores steps from a body that stands by default
    kp = {"hip": 300, "knee": 300, "ankle": 100, "shoulder": 150, "elbow": 100}
    kp_joint = {j: kp[j.split("_")[0]] for j in full}
    if kind == "weak_hip":
        kp_joint[f"hip_{a}"] = 60
    rng_deg = {j: {"hip": (-110, 30), "knee": (0, 150), "ankle": (-45, 45), "shoulder": (-180, 60), "elbow": (-150, 0)}[j.split("_")[0]] for j in full}
    rng_deg["knee_l"] = knee_rng["l"]; rng_deg["knee_r"] = knee_rng["r"]
    def _rng(j):
        lo, hi = rng_deg[j]; return f"{np.radians(lo):.4f} {np.radians(hi):.4f}"
    # iteration 7: bounded actuator force. Unbounded position actuators let a legless body launch
    # itself off its pelvis with arm swings; a person's joints cannot. Newton-metres.
    fmax = {"hip": 150, "knee": 150, "ankle": 60, "shoulder": 60, "elbow": 40}
    actuators = "\n".join(f'    <position name="p_{j}" joint="{j}" kp="{kp_joint[j]}" ctrlrange="{_rng(j)}" forcerange="-{fmax[j.split("_")[0]]} {fmax[j.split("_")[0]]}"/>' for j in present)
    jointsensors = "\n".join(f'    <jointpos name="q_{j}" joint="{j}"/>' for j in present)
    has = {"l": True, "r": True}; foot = {"l": True, "r": True}
    if morph == "nolegs":
        has = {"l": False, "r": False}; foot = dict(has)
    elif kind == "noleg":
        has[a] = False; foot[a] = False
    elif kind == "stump":
        foot[a] = False
    touch_sites = [s for s in ("foot_l", "foot_r", "knee_l", "knee_r", "hand_l", "hand_r") if
                   (s.startswith("foot") and foot[s[-1]]) or (s.startswith("knee") and has[s[-1]]) or s.startswith("hand")]
    touches = "\n".join(f'    <touch name="touch_{s}" site="{s}"/>' for s in touch_sites)
    return f'''
<mujoco model="planar_biped_{morph}">
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <default>
    <joint damping="3.0" armature="0.02" limited="true"/>
    <geom condim="3" friction="1.0 0.005 0.0001" density="1000" contype="1" conaffinity="1"/>
    <position ctrllimited="true"/>
  </default>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="40 2 0.1" pos="0 0 0" friction="1.0 0.005 0.0001"/>
    <body name="torso" pos="0 0 {z0}">
      <joint name="rootx" type="slide" axis="1 0 0" limited="false" damping="0" armature="0"/>
      <joint name="rootz" type="slide" axis="0 0 1" limited="false" damping="0" armature="0"/>
      <joint name="rooty" type="hinge" axis="0 1 0" limited="false" damping="0" armature="0"/>
      <geom name="torso" type="capsule" fromto="0 0 -0.25 0 0 0.25" size="0.09"/>
      <geom name="pelvis" type="box" pos="0 0 -0.28" size="0.14 0.10 0.04"/>
      <site name="torso_site" pos="0 0 0" size="0.01" rgba="0 0 0 0"/>
      <body name="head" pos="0 0 0.38">
        <geom name="head" type="sphere" size="0.1"/>
        <site name="head" pos="0 0 0" size="0.01" rgba="0 0 0 0"/>
      </body>{_arm("l")}{_arm("r")}{legs}
    </body>
  </worldbody>
  <actuator>
{actuators}
  </actuator>
  <sensor>
    <framepos name="torso_pos" objtype="site" objname="torso_site"/>
    <framelinvel name="torso_vel" objtype="site" objname="torso_site"/>
    <framepos name="head_pos" objtype="site" objname="head"/>
    <jointpos name="pitch" joint="rooty"/>
{jointsensors}
{touches}
  </sensor>
</mujoco>'''


def rest_pose(m, d, morph):
    """Each body starts at its own rest: standing on what legs it has; a legless body prone with the
    arms ahead of the head and the hands on the floor (iteration 7)."""
    if morph != "nolegs":
        return
    d.qpos[:] = 0
    d.qpos[2] = np.pi / 2
    hid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "hand_l")
    best = None
    for a in np.linspace(-np.pi, np.radians(60), 61):
        d.qpos[3] = d.qpos[5] = a; d.qpos[4] = d.qpos[6] = 0.0
        mujoco.mj_forward(m, d)
        x = d.site_xpos[hid][0]
        if best is None or x > best[0]:
            best = (x, a)
    d.qpos[3] = d.qpos[5] = best[1]
    mujoco.mj_forward(m, d)
    lowest = min(d.geom_xpos[g][2] - m.geom_rbound[g] for g in range(m.ngeom) if m.geom_type[g] != mujoco.mjtGeom.mjGEOM_PLANE)
    d.qpos[1] -= lowest - 0.01
    d.qvel[:] = 0
    mujoco.mj_forward(m, d)


def make(morph="intact"):
    xml = build_xml(morph)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    rest_pose(m, d, morph)
    return m, d


def sensor_index(m):
    """Start index and dimension of every sensor by name."""
    out = {}
    for i in range(m.nsensor):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_SENSOR, i)
        out[name] = (int(m.sensor_adr[i]), int(m.sensor_dim[i]))
    return out
