# hypertile: exact Farey-tree rendering of the hyperbolic tiling (for Farey Rooms)

The rooms of Farey Rooms are the tiles of the Farey tessellation: ideal triangles with vertices at rationals, viewed
in the Poincare disk. This directory compares exact integer machinery with the usual float approach, measured on
three things a renderer cares about.

| file | what |
|---|---|
| `hypertile.py` | exact enumeration `farey_tiles(eps)` (Stern-Brocot walk, integer vertices, covering-arc pruning); float BFS baseline `float_bfs_tiles(eps)` |
| `exp_a.py` -> `exp_a.log` | enumeration speed and tile-set equality |
| `exp_b.py` -> `exp_b.log`, `exp_b_renorm.log` | long camera walks: float64 camera matrix vs exact `gamma in SL2(Z)` times float residual `h` |
| `exp_c.py` -> `exp_c.log`, `exp_c32_probe.log` | float BFS in screen coordinates (as a renderer does it), float64 and float32: cracks, drift, breakdown |

## The two exact ideas

1. **Enumerate, don't search.** The visible tiles are the nodes of the Stern-Brocot tree whose covering arc on the
   boundary circle is at least eps, plus the strip tiles (n, n+1, inf). Children lie inside the parent's arc, so a
   whole subtree is pruned at once. Each tile is produced exactly once: no visited set, no hashing, and
   shared vertices are the same exact rational, so seams are watertight by construction.
2. **Split the camera as g = gamma h.** gamma is an exact integer SL2(Z) matrix (the room label, Python ints or
   int64/int128 in C), and h is a float matrix kept in the fundamental domain by exact integer moves (T^n, S) after
   every step. This is the hyperbolic analogue of floating-origin rebasing. Because the tiling is SL2(Z)-invariant,
   the renderer only ever sees h, so its numbers are O(1) however far the player walks.

## Results

**(a) Enumeration** (`exp_a.log`, Python, camera at the centre):

| eps | tiles | exact Farey | float BFS | speedup | same tile set |
|---|---|---|---|---|---|
| 2e-2 | 1066 | 4.4 us/tile | 14.6 us/tile | 3.3x | yes |
| 5e-3 | 5282 | 4.1 | 14.0 | 3.4x | yes |
| 2e-3 | 15010 | 3.5 | 12.8 | 3.7x | yes |
| 1e-3 | 32750 | 3.6 | 12.8 | 3.6x | yes |

The speedup is the cost of hashing and of re-testing already-visited neighbours. It is a Python number, and a C port
would shift it.

**(b) Long walks** (`exp_b.log`). The walk takes steps of 0.05 along a slowly turning heading, R = 2000 px. Each
method is judged against an exact (300-digit) rendering of its *own* camera state, over all visible tiles:

| distance | float64 g | float64 g, det renormalised each step | gamma h |
|---|---|---|---|
| 5 | 2e-12 px | 2e-12 px | 7e-13 px |
| 10 | 3e-10 | 2e-10 | 7e-13 |
| 20 | 5e-6 | 6e-6 | 7e-13 |
| 30 | 0.11 px (4 rooms wrong) | 0.12 px | 7e-13 |
| 40 | 2300 px (room set wrong) | 2300 px | 8e-13 |
| 50-60 | 4000 px (garbage; det -> 0 or 2e7) | det evaluates to 0, crash | 7e-13 |

The float64 camera loses about one digit per 2.3 units walked, as eps e^d predicts: drawing g^-1 x cancels numbers
of size e^(d/2). Renormalising the determinant does not help, because det g itself is computed with the same
cancellation. A float32 camera would fail about 8x sooner (at roughly d ~ 5). The gamma h camera has constant error
at every distance tested, and gamma names the room exactly.

*What this does **not** fix* (an earlier version of the test measured this by mistake). Hyperbolic geodesics diverge
exponentially, so a rounding error in the heading at one step grows like e^(distance walked since then), relative to
the infinitely precise product of the inputs. No finite-precision camera avoids this, exact or not. Head-tracking
input is noisy anyway, so the drift is invisible. It does mean two machines replaying the same float inputs diverge
unless the steps themselves are exact, for example quantised moves in SL2(Z) or in a fixed finite set.

**(c) Float BFS in screen coordinates** (`exp_c.log`). This is the renderer's version: vertices are camera-frame
float vectors, edges are crossed by float reflection, and each tile also carries its exact label. That lets every
float copy of a vertex be grouped and compared:

| precision | eps | tiles | crack between copies | drift from exact |
|---|---|---|---|---|
| float64 | 2e-2 to 1e-3 | 1104 to 33430 | 0 | 2e-11 to 3e-9 px |
| float32 | 2e-2 | 1104 | 0 | 0.035 px |
| float32 | 5e-3 | 5457 | 0 | 0.081 px |
| float32 | 2e-3 | **breaks down**: >46000 accepted (true 15394), 30346 NaN/degenerate vertices | | |
| float32 | 1e-3 | **breaks down**: >46000 accepted (true 33430), 14557 NaN/degenerate vertices | | |

Cracks are 0 because the BFS passes shared vertices to neighbours rather than recomputing them. The error shows up
instead as drift: whole fans of tiles are misplaced together. That drift is negligible in float64 and sub-pixel but
growing in float32 down to eps = 5e-3. Below that the float32 BFS fails outright (`exp_c32_probe.log`): reflections of
near-degenerate edges give zero determinants, NaN vertices make the size test pass, and the search runs away
(the first full run was killed by the OOM killer). Exact enumeration has neither cracks nor drift: every vertex is an exact rational, converted to
the screen once.

## Verdict

- **Visual quality.** The real win is camera range. A float64 camera matrix corrupts the view after about 30 units of
  walking (float32 after about 5), while gamma h keeps rendering at 1e-12 px indefinitely, with exact room labels for
  free. This is the result to use in Farey Rooms: store the player as (gamma, h) and rebase h after every move.
- **Speed.** Exact enumeration is 3.3-3.7x faster than BFS in Python, with an identical tile set and no hash table.
  It has not yet been measured in C or on a GPU.
- **Seams.** With careful BFS (passing vertices along), float64 has no cracks at these depths. Exact rationals
  guarantee it, rather than relying on that care.
