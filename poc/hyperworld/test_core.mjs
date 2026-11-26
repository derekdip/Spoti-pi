import { World, GEN, mul, invExact, tileKey, toFloat, I2 } from './core.js';
let ok = true; const check = (c, m) => { if (!c) { ok = false; console.log('FAIL', m); } };
// 1. generators have det 1 and the back-door of each doorway leads home
for (const e of ['T', 'Tinv', 'Q']) { const A = GEN[e]; check(A[0][0] * A[1][1] - A[0][1] * A[1][0] === 1n, 'det ' + e); }
// 2. neighbour symmetry: from tile N = X, one of its three doorways leads back to the identity tile
const k0 = tileKey(I2);
for (const e of ['T', 'Tinv', 'Q']) { const N = GEN[e]; const back = ['T', 'Tinv', 'Q'].some(f => tileKey(mul(N, GEN[f])) === k0); check(back, 'back door from ' + e); }
// 3. visible set: distinct tiles, counts 1 + 3 + 6 + 12 ... (trivalent tree)
const w = new World(); const vis = w.visible(5); const keys = new Set(vis.map(v => v.key));
check(keys.size === vis.length, 'distinct'); check(vis.length === 1 + 3 + 6 + 12 + 24 + 48, 'tree count ' + vis.length);
// 4. walking: random walk of 2000 metres; tile keys stay consistent and the local pose stays bounded
const rnd = (s => () => (s = (s * 1103515245 + 12345) % 2147483648) / 2147483648)(7);
let maxEntry = 0;
for (let i = 0; i < 20000; i++) { if (!w.move(0.1)) w.turn(1.3 + rnd()); if (rnd() < 0.02) w.turn(rnd() - 0.5); maxEntry = Math.max(maxEntry, ...w.g.flat().map(Math.abs)); }
check(maxEntry < 20, 'local pose bounded ' + maxEntry);
console.log(`walked 2000 m: ${w.crossings} doorway crossings; tile matrix entries have ${w.M.flat().map(x => (x < 0n ? -x : x).toString().length).reduce((a, b) => Math.max(a, b))} digits; local pose max entry ${maxEntry.toFixed(3)}`);
// 5. naive vs exact relative transforms of nearby tiles, as the player heads straight away from the origin
const w2 = new World(); const out = [];
for (let n = 0; n <= 70; n++) {
  if (n > 0) { w2.cross(n % 2 ? 'T' : 'Q'); }                     // alternate doorways: a path that heads away (entries grow)
  let err = 0;
  for (const v of w2.visible(2)) { const E = toFloat(v.rel), N = w2.naiveRelative(v.rel); err = Math.max(err, ...[0, 1].flatMap(i => [0, 1].map(j => Math.abs(N[i][j] - E[i][j])))); }
  if (n % 10 === 0) out.push(`${n} tiles out: |M| ~ 1e${Math.max(...w2.M.flat().map(x => (x < 0n ? -x : x).toString().length)) - 1}, naive relative-transform error ${err.toExponential(1)}`);
}
console.log(out.join('\n'));
console.log(ok ? 'ALL CORE TESTS PASSED' : 'SOME TESTS FAILED');
