# Implementation handoff: damaged-body locomotion for VR

For the chat that builds the runtime. Everything below was established
by the preregistered rounds G1 to G14 (`docs/rgre-writeup.md`, entries
17 to 29, and `docs/math-track-g*-results.md`); this page says what
those results mean for an implementation, what to build, in what
order, and what not to do. The motion bank an engine consumes is
`poc/results/gait_bank.json`, produced by `poc/gait3d/export_bank.py`.
The reference player is `poc/gait3d/cycle_runtime.py`. The viewer at
https://claude.ai/artifact/J6FuC4UF6NAxPaJYbMJ39j shows every clip.

## 1. What is settled

1. **A gait is a clip, not a parameter set.** The description that
   plays is the physics teacher's own motion: a mean stride cycle (32
   phase bins) for a body that walks, a four-second loop with a
   crossfaded seam for a body with no clean cycle (the stump's
   kneel-step, the one-leg hop, the crawl). Six objectives for fitting
   a parametric gait were each met by their own numbers and faulted
   by the eye (`docs/gait3d-runtime.md`). Do not fit a gait to
   statistics for the viewer.
2. **Damage on a walker is a dial on the walk clip.** The grammar's
   classes (limp, weak hip, stiff leg, held leg, vault) act as edits of
   the intact clip: amplitude ratios, offsets, lag shifts, a stance
   re-timing, all against a fixed reference (`poc/gait3d/clip_edit.py`).
   Fitted once per damage, they generalise to runs of the damaged
   teacher the fit never saw (G13, 8 of 9).
3. **Some damages are clips of their own.** The kneel-step, the hop and
   the crawl are not reachable by editing a walk: the walk clip carries
   its height and its stance parts and no edit gives them up. The
   runtime switches clips for these.
4. **A removed arm is free.** The walk clip with the arm's joints
   dropped describes a one-arm walker within the teacher's own
   run-to-run noise; nothing to fit (G14).
5. **Edits compose without fitting.** Two single-damage edits composed
   by rule (`clip_edit.compose`) took a body with both damages from an
   error of 0.69 to 0.52 on runs it never saw, within 1.26 of a fresh
   fit (0.42). Compose first; run the teacher only if it looks wrong.
6. **A body the physics cannot move has no clip.** The legless body
   with one arm flounders at 0.1 m/s with its head on the floor. Bank
   the teacher's own floundering or a static pose; do not edit a crawl
   onto it.
7. **Two runtime rules decide believability.** Progress comes from the
   clip's own root displacement (root motion); re-deriving it from
   foot planting on a mean cycle gave sliding, stepping back and
   treadmill artefacts across three rounds. Height comes from the
   clip's clearance (its own lowest part's height above the floor),
   not the root height, so a body that has lost the parts a clip
   stood on comes down to the floor.
8. **Transitions are crossfades in phase space** over about a second,
   with the skeleton switched at the start and the phase and root
   position continuous. They read as a blend, not a stumble. The cheap
   way to a stumble is a physics run of the injury event itself,
   banked as a clip.
9. **Which class "names" a damage is a research result, not a runtime
   need.** On a real clip the naming depends on the clip's own
   asymmetry (G13). The runtime never needs a label.

## 2. The motion bank

`poc/results/gait_bank.json` (341 KB): `conventions`, `style`,
`skeletons` (one per body) and `clips` (30). Every clip:

| field | meaning |
|---|---|
| `id`, `kind`, `body`, `note` | e.g. `locked_knee_left/teacher`, `teacher cycle`; kinds: teacher cycle, teacher loop, edited clip, composed edit |
| `joints` | joint names in the clip's column order |
| `nb`, `dur` | phase bins, cycle duration in seconds |
| `angles[nb][nj]` | joint angles per bin, radians |
| `quat_wxyz[nb][4]` | root orientation per bin, world frame |
| `root_z[nb]` | root height per bin as played on this body, metres, floor at 0 |
| `dx[nb+1]`, `dy[nb+1]` | root displacement from the clip's start at the phase edges 0, 1/nb, ..., 1; `dx[nb]` is the advance per cycle |
| `clear[nb]` | the clip's clearance per bin (already folded into `root_z`; kept for re-grounding on other bodies) |

Conventions: metres, radians, seconds; +z up, +x forward; root = free
joint, position then quaternion (w, x, y, z). Every joint is a hinge:
hip_y, knee, ankle_y, shoulder, elbow about the body's +y (hip flexion
forward is negative, knee flexion positive); hip_x and ankle_x about
+x (a positive left hip_x abducts the left leg, a positive right hip_x
adducts the right). Source frame rate 50 Hz; teacher window seconds 1
to 5. The skeleton per body lists each joint's axis, position in its
parent and range, and each geom's kind, size and pose, so a capsule
figure can be drawn directly.

Bodies in the bank: intact; weak hip, locked knee, short shank, stump,
one leg (left and right); no legs; and from G14 one arm removed, a
locked left knee with a weak right hip, a locked left knee without its
right arm, no legs with one arm. Right-side damages have their own
teacher clips; mirroring a left clip (swap sides, negate the lateral
terms) is untested and would halve the bank.

## 3. The player contract

State: the current clip, a phase in cycles, the root's x and y.

```
advance(dt):
    p0 = phase; p1 = p0 + dt / clip.dur
    x += dx(p1 mod 1) - dx(p0 mod 1) + (floor(p1) - floor(p0)) * dx[nb]
    y  = y0 + dy(p1 mod 1)
    phase = p1
pose(phase):
    joints      = lerp(angles, phase)          # linear between bins, periodic
    orientation = nlerp(quat, phase)           # normalised interpolation, sign-aligned
    root.z      = lerp(root_z, phase)
    root.x, root.y = x, y
transition(to, seconds):
    source = current blended clip; target = to; weight ramps 0 -> 1 over seconds
    switch the skeleton to the target's body at the start
blend(a, b, w):
    resample the shorter to the longer's bins; shared joints interpolated,
    joints only b has enter at b's values; dur, dx, dy, root_z interpolated; quats nlerp
```

Any frame rate. Reference implementation: `CycleProfile`, `blend`,
`CyclePlayer` in `poc/gait3d/cycle_runtime.py` (about 200 lines).
Test vector: `CyclePlayer(profile).frames(seconds, fps)` dumps the
root pose and joints per frame; an engine port should match it to
within interpolation error.

Style layer (`style` in the bank): add the offsets to the shoulders
(−1.35 rad) and elbows (−0.35), keep a quarter of the arms' own swing,
pitch the torso forward 0.22 rad; the legless body keeps its arms and
its pitch. Character and gait are separate layers.

## 4. Retargeting to a character model

The biped is a capsule skeleton: torso capsule (0.5 m) with a pelvis
box, head sphere, upper arm 0.28 m and forearm 0.26 m from shoulders
0.20 m off the midline, thigh 0.42 m and shank 0.42 m with box feet
0.24 by 0.10 m, standing height 1.17 m at the root. Map each hinge to
the humanoid rig's local rotation about the matching axis (shoulder
and hip pitch, knee, ankle pitch and roll, hip abduction, elbow). Two
things need care:

- **Leg length.** A rig with longer legs walks the same angles over a
  longer stride; scale `dx` by the leg-length ratio, or keep the
  bank's `dx` and accept some foot slip. Foot IK to the floor at stance
  is optional; the bank does not carry stance flags, and the clips'
  own feet touch by construction on their own skeleton.
- **Missing parts.** A damaged body's clip lists only the joints it
  has; hide or detach the mesh of the missing part and leave its
  joints unread. The one-leg and legless bodies' clips already carry
  the root at the right height for the parts that remain.

## 5. Suggested order

1. **Engine player** (Unity C# or three.js) that loads the bank and
   plays any clip on the capsule skeleton, matched against the Python
   player's frames. Start with `intact/teacher`, `noleg_left/teacher`,
   `nolegs/teacher`.
2. **Transitions and injury events**: body switch plus crossfade;
   the intact-to-one-leg transition is the reference case.
3. **Retarget** to a humanoid model; hide missing parts.
4. **Steering**: rotate `dx`, `dy` into the heading; turn by yawing the
   root. Root motion makes this trivial.
5. **Style layer** and per-character variation (clip choice, offsets,
   playback rate within about 20 percent).
6. **New bodies**: compose existing edits first (`clip_edit.compose`);
   if it looks wrong, run the teacher offline (`poc/gait3d/teacher.py`,
   about five minutes per run, three seeds) and bank the clip with
   `export_bank.py`.

## 6. What not to do

- Do not fit a parametric gait to consumer statistics for the viewer;
  four rounds of adding what the eye used never closed the gap.
- Do not derive progress by planting the stance foot of a mean cycle.
- Do not carry a clip's root height onto a body that has lost the
  parts it stood on; carry clearance.
- Do not expect a damage's class label to be stable across bodies;
  the runtime does not need it.
- Do not compose base-class edits (rhythm, legs) across bodies as if
  they were damage; only impairment edits were tested in composition.
- Do not treat three teacher runs as ground truth: the runs of one
  body differ by more than some damages do. Judge by eye against the
  viewer, and by numbers only within that spread.

## 7. Pointers

- Runtime: `poc/gait3d/cycle_runtime.py`; edits and composition:
  `poc/gait3d/clip_edit.py`; bank: `poc/gait3d/export_bank.py`.
- Bodies, planner, teacher: `poc/gait3d/biped3d.py`, `mpc3d.py`,
  `teacher.py`; the teacher's history: `docs/gait3d-feasibility.md`.
- Viewer: `poc/gait3d/export_web.py`, `web_template.html`,
  `build_web.py` (plays baked geom poses, not the bank).
- Why the parametric route was abandoned: `docs/gait3d-runtime.md`.
- The rounds: `docs/math-track-g13-results.md`,
  `docs/math-track-g14-results.md`; the whole arc:
  `docs/rgre-writeup.md`.
