# Where to get teacher data cheaply

Ranked by how fast you can get from zero to a recorded `(x(t), u(t))` pair
that is worth fitting. The first three are where I would actually start.

## Tier 1: free, same coordinate system, one evening each

| Source | What it gives you | Why it is worth it |
|---|---|---|
| **Your own Unity teacher** (PC, heavy CPU/Jobs sim, or HDRP) | Per-stalk bend, per-vertex snow/water displacement, per-agent crowd state, driven by *your own* player inputs | Same coordinates, same causes, same timing as the runtime. Nothing to convert. Start here for vegetation; the teacher in `poc/reactive/teacher.py` is a numpy sketch of what to write. |
| **Analytic PDE teachers** in numpy (wave equation, shallow water, heat/diffusion, a damped lattice) | Exact solutions or well-understood numerics | Cheapest possible reference and a sanity check: the search must rediscover the known closed form (a Gaussian for heat, a ring for the wave equation). If it cannot, the grammar or objective is broken, not the idea. |
| **Recorded player telemetry from SquishLabVR** (head, hands, feet tracks) | The input distribution `u(t)` | The fit must cover the causes players actually produce: stomps, hand swipes, crouch-crawls, standing still. Synthetic S-curves like the one in the proof of concept are not representative. Record 20 minutes of real play and drive every teacher with it. |

## Tier 2: free offline simulators with Python export

| Source | Systems | Notes |
|---|---|---|
| **Blender** (Python API) | Cloth, soft body, rigid body + cell fracture, hair dynamics (grass as hair with physics), Mantaflow liquid and smoke/fire | Free. Export per-frame vertex or particle positions to `.npz` from a script. Hair dynamics with collision is a decent grass teacher; Mantaflow liquid is a decent splash/wake teacher. |
| **Houdini Apprentice** (free, non-commercial) | Vellum (grass, cloth, snow-like grains), Pyro (fire/smoke), FLIP (water), RBD fracture | Best quality per hour of setup. Export point caches (`.bgeo`, or CSV via Python SOP). Apprentice watermark does not matter, you only need the numbers. |
| **Taichi / Taichi Elements** (Python, GPU) | MPM snow, sand, water, elastic bodies | The Disney MPM snow paper's method, in Python, runs on a laptop GPU. This is the snow-footprint teacher: drive a foot-shaped collider through it and record surface height per cell. |
| **NVIDIA Warp** (Python) | Cloth, particles, rigid, soft bodies, SPH fluids; differentiable | Differentiable means you can later fit primitive parameters by gradient instead of Powell/ECS for the smooth parts. |
| **PhiFlow** or **JAX-CFD** | Differentiable 2-D/3-D fluids | Smoke/fire velocity and density fields for the fire experiment. |
| **PyBullet / MuJoCo** | Rigid and soft bodies, deterministic contact | Destruction, debris, creature contact. MuJoCo is deterministic and fast; good for crowd-of-rigid-things and "what falls where" teachers. |

## Reachability note (from this sandbox, September 2026)

Downloaded and used: the DeepMind Learning-to-Simulate datasets on Google
Cloud Storage (`WaterDrop` validation set, 130 MB, parsed without
TensorFlow by `poc/water/gns_data.py`). GitHub raw files are reachable, so
the ETH/UCY pedestrian sets are too. Hugging Face (The Well), DaRUS
(PDEBench) and NOAA were blocked by the proxy here; fetch those from your
own machine.

## Tier 3: public datasets (skip the simulator entirely)

| Dataset | What it is | Use |
|---|---|---|
| **DeepMind "Learning to Simulate" datasets** (Water, Sand, Goop, WaterRamps, etc.) | MPM particle trajectories with obstacles, published with the GNS paper | Ready-made water/sand/goop teachers with causes (obstacles, initial conditions). Particle format needs projecting to a height field or density grid first. |
| **The Well** (Polymathic AI, 2024) | ~15 TB of physics simulations across many PDEs, in a uniform HDF5 format | Shallow water, turbulence, reaction-diffusion and more. Overkill in size, but the shallow-water sets are a direct water-surface teacher. |
| **PDEBench** | Benchmark PDE solutions (shallow water, diffusion-reaction, Navier-Stokes, Burgers) | Same idea, smaller and easier to download. |
| **ETH / UCY pedestrian datasets, Stanford Drone Dataset** | Real human trajectories in crowds | Real teacher for the panic/crowd field: fit density flow + local avoidance primitives to actual humans rather than to another simulator. |

## Tier 4: real-world capture (cheap, noisy, surprisingly good for tuning perceptual parameters)

- **Phone video of grass or a cornfield** with a hand or foot moving through
  it; extract optical flow (OpenCV Farneback or RAFT) to get a 2-D bend-rate
  field. You will not get absolute bend, but you get decay times, spatial
  extent and the recovery shape, which is what the kernels' `σ`, `λ`, `τ`
  need.
- **Depth camera (Kinect, RealSense, iPhone LiDAR)** over snow or sand while
  stepping in it: a direct height-field teacher for footprints and recovery.
- **Slow-motion phone video of water splashes** in a tray: ring speed,
  spreading and decay for the wave-packet kernel.

## Which experiment to run first

Vegetation, in this order, exactly as the write-up says, with one change:
drive the teacher with recorded SquishLabVR hand/feet tracks, not a synthetic
path. Then, in order of expected payoff for Quest:

1. **Snow footprints** (Taichi MPM or Blender soft body teacher): the trail
   token is already the right representation; the fit is mostly the crush
   kernel shape and the recovery curve.
2. **Water surface** (Blender Mantaflow or the DeepMind Water dataset): tests
   the corrected ring-wave kernel and geometric spreading.
3. **Crowd/panic field** (ETH/UCY real data): tests whether a coarse field
   plus local avoidance reproduces real trajectories at all.
4. **Fire** last: high-dimensional, chaotic, and the perceptual metric is
   hard. Do it once the pipeline is proven on the others.

## What to record, every time

- Causes `u(t)` at full rate: positions, velocities, radii, contact events.
- State `x(t)` at the *consumer's* resolution, not the simulator's: the
  visual consumer needs per-vertex bend, the AI consumer needs a 1 m grid.
  Recording both is cheap and lets you fit per-consumer errors.
- A held-out run with different causes for testing. A grammar fit to one
  walk and tested on the same walk proves nothing.
