# Farey Rooms: a drift-free hyperbolic world

A small walkable hyperbolic world (browser + WebXR) built on the Farey tessellation of the hyperbolic plane.

- **Rooms** are ideal triangles of the Farey tessellation with their three cusps walled off by horocycles; each has three doorways.
- **Exact bookkeeping**: the current room is an integer matrix M in PSL(2, Z) (BigInt); the player's pose is a small float
  matrix inside the room. Crossing a doorway multiplies M by one of three integer generators (T, T^-1, Q = [[1,0],[1,1]]) and
  re-expresses the pose locally. Neighbouring rooms are placed with M^-1 N computed exactly, then converted to float, so floats
  stay small however far you walk. Room identity = its three vertices as exact fractions (shown in the HUD).
- **Float-engine comparison**: the usual approach (absolute float matrices, inverse(M) N in floating point) is exact until
  entries pass about 2^26 (products pass 2^53), about 37 rooms out along a straight route, then rooms jump by whole tiles and
  from about 41 rooms the computation returns NaN.
- **Rendering**: equidistant projection from the player (true hyperbolic distance and direction; exact along lines through
  the player).

Files: `core.js` (exact core, ES module), `test_core.mjs` (node tests), `farey-rooms.html` (the page; inline copy of the core +
three.js r128 from cdnjs), `shot.cjs` (headless screenshots).

Results (`node test_core.mjs`): a 2000 m random walk crosses 1719 doorways; the room matrix reaches 218 digits while the
local pose stays bounded (max entry 1.57). Float engine: exact to 37 rooms, error 1-3 tiles at 38-40, NaN from 41.

**VR**: open `farey-rooms.html` from an HTTPS origin in a headset browser (e.g. Quest Browser) and press Enter VR. Left
stick moves (relative to where you look), right stick snaps turns. WebXR needs a secure context, so `file://` may not work;
any static HTTPS host (GitHub Pages, a local server with a certificate) does.
