// Hyperbolic world core: the Farey tessellation of the upper half-plane, tiles tracked exactly in PSL(2,Z) with BigInt.
// Base tile T0 = ideal triangle (0, 1, inf), cusps truncated by horocycles (Im z = 2 at inf; circles of diameter 1/2 at 0 and 1).
// Doorways: edge x = 0 -> generator Tinv, edge x = 1 -> T, semicircle |z - 1/2| = 1/2 -> Q = [[1,0],[1,1]] (z -> z/(z+1)).
// Player state: exact tile matrix M (BigInt) + float pose g in SL(2,R) (player at g(i), heading = image of +y at i), within T0.

export const GEN = {
  T: [[1n, 1n], [0n, 1n]], Tinv: [[1n, -1n], [0n, 1n]], Q: [[1n, 0n], [1n, 1n]],
};
export const GEN_INV = { T: 'Tinv', Tinv: 'T', Q: 'Qinv' };
GEN.Qinv = [[1n, 0n], [-1n, 1n]];

export const mul = (A, B) => [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
                             [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]];
export const invExact = A => [[A[1][1], -A[0][1]], [-A[1][0], A[0][0]]];          // det = 1
export const I2 = [[1n, 0n], [0n, 1n]];
export const toFloat = A => A.map(r => r.map(Number));
export const fmul = (A, B) => [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
                              [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]];
export const finv = A => { const d = A[0][0] * A[1][1] - A[0][1] * A[1][0]; return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]; };

// complex helpers (as [re, im])
const cdiv = (a, b) => { const d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
export function mobius(A, z) {   // A float 2x2 real, z complex
  const num = [A[0][0] * z[0] + A[0][1], A[0][0] * z[1]], den = [A[1][0] * z[0] + A[1][1], A[1][0] * z[1]];
  return cdiv(num, den);
}

// tile identity: the set of its three vertices M(0), M(1), M(inf) as reduced fractions -> canonical string key
const gcd = (a, b) => { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) [a, b] = [b, a % b]; return a; };
function frac(p, q) {   // p/q, q may be 0 (infinity)
  if (q === 0n) return 'inf';
  if (q < 0n) { p = -p; q = -q; }
  const g = gcd(p, q); return `${p / g}/${q / g}`;
}
export function tileKey(M) {
  const v = [frac(M[0][1], M[1][1]), frac(M[0][0] + M[0][1], M[1][0] + M[1][1]), frac(M[0][0], M[1][0])];
  return v.sort().join('|');
}

// geometry of the base tile
export const CENTER = [0.5, Math.sqrt(3) / 2];
export const H_INF = 2.0, R_CUSP = 0.25;              // horocycle heights: Im z = 2 at inf; circles radius 1/4 tangent at 0 and 1
export function exitGenerator(z) {                    // which doorway did the point leave through (null = still inside)
  const [x, y] = z;
  if (x < 0) return 'Tinv';
  if (x > 1) return 'T';
  if ((x - 0.5) ** 2 + y * y < 0.25) return 'Q';
  return null;
}
export function inWall(z) {                           // inside a truncated cusp (wall region)
  const [x, y] = z;
  return y > H_INF || (x * x + (y - R_CUSP) ** 2 < R_CUSP * R_CUSP) || ((x - 1) ** 2 + (y - R_CUSP) ** 2 < R_CUSP * R_CUSP);
}

// player pose in SL(2,R): rotation about i by theta and translation along the imaginary axis by s
export const Krot = th => [[Math.cos(th / 2), Math.sin(th / 2)], [-Math.sin(th / 2), Math.cos(th / 2)]];
export const Atr = s => [[Math.exp(s / 2), 0], [0, Math.exp(-s / 2)]];
export function normalize(g) { const d = Math.sqrt(Math.abs(g[0][0] * g[1][1] - g[0][1] * g[1][0])); return g.map(r => r.map(v => v / d)); }

export class World {
  constructor() { this.M = I2; this.g = [[1, 0.5], [0, 1]]; this.g = fmul(this.g, [[Math.sqrt(0.75) ** 0.5, 0], [0, 1 / Math.sqrt(0.75) ** 0.5]]); this.crossings = 0; this.path = []; }
  position() { return mobius(this.g, [0, 1]); }
  // move by distance s in direction alpha relative to heading (alpha = 0 forward); returns true if moved
  move(s, alpha = 0) {
    const g2 = normalize(fmul(fmul(fmul(this.g, Krot(alpha)), Atr(s)), Krot(-alpha)));
    const z = mobius(g2, [0, 1]);
    if (inWall(z)) return false;
    this.g = g2;
    for (let guard = 0; guard < 4; guard++) {
      const e = exitGenerator(mobius(this.g, [0, 1]));
      if (!e) break;
      this.cross(e);
    }
    return true;
  }
  turn(th) { this.g = normalize(fmul(this.g, Krot(th))); }
  cross(e) {   // pass through doorway e: tile M -> M X, local pose g -> X^{-1} g
    this.M = mul(this.M, GEN[e]); this.g = normalize(fmul(toFloat(GEN[GEN_INV[e]]), this.g)); this.crossings++; this.path.push(e);
  }
  // visible tiles: best-first by graph distance (breadth-first), exact relative transforms G = M^{-1} N kept in BigInt
  visible(depth) {
    const out = [], seen = new Set(), Minv = invExact(this.M);
    const q = [{ rel: I2, d: 0 }]; seen.add(tileKey(this.M));
    while (q.length) {
      const { rel, d } = q.shift(); out.push({ rel, d, key: tileKey(mul(this.M, rel)) });
      if (d >= depth) continue;
      for (const e of ['T', 'Tinv', 'Q']) {
        const r2 = mul(rel, GEN[e]), k = tileKey(mul(this.M, r2));
        if (!seen.has(k)) { seen.add(k); q.push({ rel: r2, d: d + 1 }); }
      }
    }
    return out;
  }
  // the naive engine's view of the same tile: absolute float matrices, relative transform inv(M_f) N_f in floating point
  naiveRelative(rel) { const Mf = toFloat(this.M), Nf = toFloat(mul(this.M, rel)); return fmul(finv(Mf), Nf); }
}

// map a point of the base-tile frame, placed by exact relative transform rel, into player-centred polar coords (distance, angle)
export function toPlayerPolar(world, relFloat, z) {
  const w = mobius(fmul(finv(world.g), relFloat), z);            // player at i, heading +y
  const u = cdiv([w[0], w[1] - 1], [w[0], w[1] + 1]);              // Poincare disk, player at 0, heading -> +real
  const r = Math.min(Math.hypot(u[0], u[1]), 0.999999999999);
  return { d: 2 * Math.atanh(r), th: Math.atan2(u[1], u[0]) };
}
