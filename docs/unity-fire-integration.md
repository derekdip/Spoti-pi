# Putting the cheap fire in a Unity VR project

Everything needed to run the fire from `poc/fire/puffs.py` on a headset, plus an
honest account of what has been measured and what has not. Read the
**What is measured** section before shipping anything from here.

Code: `unity/Fire/`. **None of it has been compiled in Unity.** The Python is
the validated artefact (`poc/tests/test_puffs.py`, and five frozen experiments
in `docs/math-track-f*.md`); the C# and HLSL are line-for-line ports that will
need the usual first-compile fixes. Where they disagree with the Python, the
Python is right.

## What this is

A fire that has no simulation in it. A source emits parcels at a rate; a parcel
emitted at `t_k` has a position, a size and a temperature at time `t` that are
closed-form functions of its age. The flame is the combination of the parcels
alive right now, so a frame is computed from the causes alone — where the
burner is, when it lit, which way the wind blows — with nothing carried over
from the frame before.

Three things follow, and they are the reason to use this rather than a particle
system:

- **Any time can be evaluated**, including one you never rendered. Late-stage
  reprojection can ask for the fire at the reprojected display time.
- **Nothing to synchronise.** Two headsets that agree on the causes draw the
  same fire, frame-exactly, with no state replication and no drift. Send the
  burner's position and its on/off times, not a particle buffer.
- **Gameplay queries are arithmetic.** "Is the player's hand in the flame" is a
  loop over about a dozen parcels, not a raycast into a simulation.

## Files

| file | what it is |
|---|---|
| `FireState.cs` | the parameters, and the five fitted presets |
| `ReactiveFire.cs` | the model: parcel resolution, temperature at a point, bed ignition |
| `ReactiveFireRenderer.cs` | the MonoBehaviour: pushes constants, one draw call, the query API |
| `FireParcels.hlsl` | the same parcel maths on the GPU |
| `FireBillboard.shader` | URP pass; no mesh, no buffers, `SV_VertexID` becomes a parcel |

## Setup

1. Drop `unity/Fire/` into `Assets/`. URP; for Built-in, change the include in
   the shader from the URP `Core.hlsl` to `UnityCG.cginc` and swap
   `TransformWorldToHClip` for `UnityObjectToClipPos` on a world-space vertex.
2. Make a material from `ReactiveFields/FireBillboard`.
3. Add `ReactiveFireRenderer` to an empty GameObject. Assign the material. Set
   `source.position` to the burner, `windDirection` to where the wind pushes.
4. Set `state` from a preset in code: `renderer.state = FirePresets.Breezy;`
   The inspector fields are all live, so tune from there.

`Graphics.RenderPrimitives` needs Unity 2022.1+; there is a `DrawProcedural`
fallback in the file for older versions.

## The gameplay API

This is the part that is in good shape, and it is why the fire is worth having
even though it does not look right yet.

```csharp
// per hand, per frame — about a dozen exponentials
if (fire.IsHot(hand.position))
    damage.ApplyBurn();

// exact temperature, for a gradient or a warning
float k = fire.TemperatureAt(hand.position);

// has this fuel bed caught yet?
if (fire.IsBedLit(0)) spreadVfx.Play();

// hazard map for an agent, on a schedule rather than per frame
fire.BakeHazardGrid(area, 16, 16, 0.9f, hazardCells);
```

Thresholds come from the teacher, not from taste: 400 K is hazardous, 573 K
lights fuel. Both are in `FireConstants`.

**Evaluating at another time is free**, because the model is closed form in
`t`. `fire.TemperatureAt(p, atTime: Time.time + 0.2f)` asks where the fire will
be in 200 ms, which is how you give an agent lookahead without simulating.

## Presets

Each is a joint fit to one scene of the reacting-flow teacher. **Pick one; do
not average them.** They are joint optima, so the median of the parameters is
not a fitted state and scores worse than any of them.

| preset | the scene it was fitted to | parcels | shape agreement | a still image of that scene scores |
|---|---|---|---|---|
| `Calm` | unforced flame, no wind | 7 | 0.88 | **0.997** |
| `Breezy` | steady breeze with a 0.7 Hz gust | 11 | 0.82 | 0.852 |
| `Windy` | strong gust | 11 | **0.80** | **0.796** |
| `UnderShelf` | gust plus an overhang | 12 | 0.80 | 0.853 |
| `SpreadingToBeds` | gust plus three beds lighting in sequence | 12 | 0.81 | 0.827 |

The right-hand column is the thing to read carefully, and it corrects an error
that stood in this project for a while. "Shape agreement" is the correlation
between the cheap glow and the teacher's over the second half of a run. A
**single frozen frame** of the same fire also scores on that measure, and it
scores *very well* when the flame barely moves — 0.997 on the calm scene. So on
calm scenes the model is far worse than a still image, and only on `Windy` does
it beat one. Do not read the raw correlation as "how good it looks" without the
reference beside it.

## VR specifics

**Billboards are cylindrical, not camera-facing.** A fully camera-facing quad
shears differently in each eye and the flame reads as a flat card. The shader
yaws the quad toward the eye but keeps world up, which is what a vertically
structured thing like fire wants anyway.

**The blend mode is physics, not style.** Parcels combine with `BlendOp Max`
because temperature is intensive: two parcels overlapping are the same hot gas,
not twice as hot. Additive blending double-counts overlaps, and in the Python
that mistake made the fitter shrink the flame until it was invisible. If you
change the blend, you are no longer running this model.

**Fill rate is the cost, not the maths.** Twelve parcels is nothing
arithmetically; twelve large transparent quads over the same pixels is real
overdraw on a mobile GPU. In order of value: lower `extent` from 3 sigmas to
2.5 (the outer ring contributes almost nothing), keep flames off the near field
where they fill the view, and use `impostorDistance` so far fires draw three
parcels instead of twelve.

**No soft particles.** They want a depth prepass that costs more than the fire.
The parcels are volumetric enough that hard intersections are not very visible.

**A caveat on the two-pass version.** The model combines temperature and soot
separately by maximum and only then computes the glow. The shader combines the
per-parcel *glow* by maximum, which is not identical. The difference is small
because soot varies slowly between neighbouring parcels. If you need exactness,
render `(excess, soot)` into a two-channel RT with max blending and resolve the
glow in a full-screen pass; on Quest that is an extra pass on a small target.

## Performance

No numbers from a headset yet — the only device measurements in this project
are for the grass work, on a phone (`docs/bendbench-results.md`), where six
bend terms cost under 1% of a frame at realistic densities. For the fire,
what can be stated from the model rather than measured:

- **CPU per fire per frame: zero.** The renderer pushes about 8 vectors and
  issues one draw. Parcels are only resolved on the CPU when something asks a
  gameplay question.
- **A gameplay query: ~12 parcels × one `pow` and one `exp`.** Per hand per
  frame this does not register.
- **A 16×16 hazard bake: ~3000 evaluations.** Schedule it a few times a second,
  not every frame.
- **GPU: 12 quads and their fill.** The arithmetic is trivial; the overdraw is
  what you budget for.

The bend-cost measurement carries one warning that applies here too: op counts
mispredicted measured cost by up to 8× on real hardware. Profile before
trusting any of the above.

## What is measured, and what is not

**Measured, and holds.** The gameplay side. Against the teacher, burn and
passability decisions are 2–5% wrong on simple scenes. Fuel beds light on their
own clock and are missed on 6–20% of alight frames, where the previous
representation missed 28–67%. Parcel counts of 11–16 come from a fit that had
the cost in its objective.

**Measured, and does not hold.** How it looks. On the scenes with a shelf or a
fuel bed, the decisions are 11–15% wrong, and that split has been the same in
every fire experiment run here. The shape agreement is at or below what a still
image of the same fire achieves on four of five scenes.

**Not measured at all.**

- *This code.* It has never been compiled. The Python has tests; this does not.
- *Anything in three dimensions.* The teacher is a 2-D slice and every number
  quoted here came from that. The port treats the model's lateral coordinate as
  an axis along the wind and makes the parcel axially symmetric about vertical.
  That is the natural reading and it is a guess; the sideways spread across the
  wind has never been fitted to anything.
- *Any headset.* No part of the fire has run on a Quest.
- *More than one fire at a time.* Every fit is a single source, or two sources
  far enough apart not to interact much. Two fires close together will not
  merge the way real ones do.

## If you want to tune it

The sliders in the browser bench are the fastest way to get a feel before
touching Unity: it runs this exact model live beside the real simulation, with
the presets loaded. The parameters that move the look most, in order:
`cool` (how far the flame reaches before fading), `amp` and `baseAmp` (the
bright core), `sharp` (soft blob versus defined edge), `gust` and `swayBase`
(how much it leans and whips), `rate` (granularity, and the direct cost).

One honest warning from the fitting work: fitting these against an error metric
reliably produces a fire that scores well and looks worse than one tuned by
eye. Three separate experiments in this project found the objective preferring
the average of a flame to a flame. If it looks right to you and scores badly,
trust your eyes — that is the documented failure mode, not a mistake on your
part.
