/* The doodle-bot simulation, shared by the studio page (poc/doodle/live_template.html embeds it) and
   the bot service (poc/doodle/run_bots.js requires it). docs/doodle-bots.md explains the design; the
   Python reference is poc/doodle/bots.py, hand.py, edits.py, and the two implementations follow the
   same rules and constants.

   Everything is pure: a round is a state R advanced by advance(R, t) with t in seconds; strokes
   appear in R.canvas with absolute times per point, so a caller can pace them out to a game (the
   service) or draw them (the page). The caller supplies the bank: srcOf(word) -> [{id, s}], where s
   is a list of strokes, each a list of [x, y] in a 256 box. Coordinates in R.canvas are on a
   640 by 420 canvas; the service normalises them. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.DoodleSim = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  const BOX = 256, W = 640, H = 420, TRAVEL = 900, EXTRAS = 2, CALLOUTS = 3, SCRIBBLES = 2, SEATS = 7, FILL_TO = 4, RESERVE = 1;
  const PERSONAS = { neat: { speed: 260, tremor: 0.5, drift: 0.8, overshoot: 2, hook: 1, think: 0.6 }, quick: { speed: 430, tremor: 1.4, drift: 2.2, overshoot: 7, hook: 3, think: 0.25 },
    shaky: { speed: 170, tremor: 2.6, drift: 3.0, overshoot: 3, hook: 2, think: 0.9 }, lazy: { speed: 210, tremor: 1.0, drift: 1.6, overshoot: 4, hook: 1.5, think: 1.5 }, bold: { speed: 340, tremor: 0.9, drift: 1.2, overshoot: 9, hook: 2, think: 0.4 } };
  const NAMES = ['Pip', 'Mo', 'Zed', 'Lou', 'Kit', 'Bea', 'Ash', 'Rue', 'Tam', 'Jo'];
  const COLORS = ['#1e7b73', '#c0552b', '#5b4fb8', '#b8892f', '#a3326f', '#2f7fb8', '#5f8a2f', '#8a4a2f', '#2f8a7a', '#7a2f8a'];
  const LINES = { claim: ['{part}!', "I'll do this bit", 'on it', 'mine', 'watch this'], confused: ['wait, where is it?', 'is that the {word}?', 'hm', 'which way is up?', 'ok ok'],
    fix: ["that's not where it goes", 'let me fix that', 'no no, like this', 'moving it'], copy: ['same', 'like that?', 'me too', 'copying you'], solo: ["I'll just draw my own", 'doing it my way', "mine's better", 'another {word}'],
    misheard: ['{word}? I heard {other}', 'oh. {other}, right?', 'drawing a {other}'], leave: ['gotta go, have fun!', 'people are here, bye', "I'll make room", 'later!'], join: ['hi!', 'hello everyone', 'what are we drawing?', "I'm here"],
    foreign: ["hey, what's that?", 'who drew that?', "that's not a {word}", 'excuse me', 'stop that', 'not there!'], retreat: ['oops', "fine, I'll go over here", 'ok ok, my corner', 'sorry!'],
    realise: ['{word}? oh. {word}!', 'ohh, {word}. got it', 'wait, {word}? ok joining'], scribble: ['nope', 'undo!', "that's gone", 'fixing this'], detail: ['a detail!', 'one more thing', 'a little extra', 'the finishing touch'],
    unknown: ["{word}? never heard of it", "I'll sit this one out", 'no idea what a {word} is'] };
  const CORNERS = [[105, 95], [535, 95], [105, 325], [535, 325]];

  function rngOf(seed) { let a = 0; for (const ch of String(seed)) a = (a * 31 + ch.charCodeAt(0)) >>> 0; a = (a || 7) >>> 0;
    const u = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
    return { u, uni: (lo, hi) => lo + (hi - lo) * u(), int: n => Math.floor(u() * n), norm: (m = 0, s = 1) => m + s * Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * Math.PI * u()), pick: arr => arr[Math.floor(u() * arr.length)] }; }

  const bbox = strokes => { let lo = [1e9, 1e9], hi = [-1e9, -1e9]; strokes.forEach(s => s.forEach(([x, y]) => { lo[0] = Math.min(lo[0], x); lo[1] = Math.min(lo[1], y); hi[0] = Math.max(hi[0], x); hi[1] = Math.max(hi[1], y); })); return [lo, hi]; };
  const slen = s => { let L = 0; for (let i = 1; i < s.length; i++) L += Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1]); return L; };
  const mean = s => [s.reduce((a, p) => a + p[0], 0) / s.length, s.reduce((a, p) => a + p[1], 0) / s.length];
  function affine(strokes, scale, aspect, rot, about = [BOX / 2, BOX / 2]) { const c = Math.cos(rot), s = Math.sin(rot), sx = scale * aspect, sy = scale / aspect;
    return strokes.map(st => st.map(([x, y]) => { const px = (x - about[0]) * sx, py = (y - about[1]) * sy; return [c * px - s * py + about[0], s * px + c * py + about[1]]; })); }
  function descriptor(stroke, lo, size) { const m = mean(stroke), [l2, h2] = bbox([stroke]); return [(m[0] - lo[0]) / size[0], (m[1] - lo[1]) / size[1], (h2[0] - l2[0]) / size[0], (h2[1] - l2[1]) / size[1], slen(stroke) / Math.max(size[0], size[1])]; }
  const dist = (a, b) => Math.sqrt(a.reduce((s, v, i) => s + (v - b[i]) ** 2, 0));
  function recombine(A, B, rng) { if (A.length < 2 || B.length < 1) return A.map(s => s.slice()); const [loA, hiA] = bbox(A), [loB, hiB] = bbox(B); const sA = [Math.max(hiA[0] - loA[0], 1), Math.max(hiA[1] - loA[1], 1)], sB = [Math.max(hiB[0] - loB[0], 1), Math.max(hiB[1] - loB[1], 1)];
    const k = 1 + rng.int(A.length - 1), dA = descriptor(A[k], loA, sA); let j = 0, best = 1e9; B.forEach((s, i) => { const d = dist(descriptor(s, loB, sB), dA); if (d < best) { best = d; j = i; } });
    const out = A.map(s => s.slice()); out[k] = B[j].map(([x, y]) => [(x - loB[0]) / sB[0] * sA[0] + loA[0], (y - loB[1]) / sB[1] * sA[1] + loA[1]]); return out; }
  function dropMinor(strokes, rng) { if (strokes.length < 3) return { kept: strokes, dropped: null }; const L = strokes.map(slen), sorted = L.slice().sort((a, b) => a - b), thr = sorted[Math.floor(0.67 * (L.length - 1))];
    const cands = []; for (let i = 1; i < strokes.length; i++) if (L[i] < thr) cands.push(i); if (!cands.length) return { kept: strokes, dropped: null }; const k = rng.pick(cands); return { kept: strokes.filter((_, i) => i !== k), dropped: strokes[k] }; }
  function reorder(strokes, rng) { if (strokes.length < 3) return strokes; const idx = []; for (let i = 1; i < strokes.length; i++) idx.push(i); for (let r = 0; r < 2; r++) { const i = rng.int(idx.length - 1); [idx[i], idx[i + 1]] = [idx[i + 1], idx[i]]; } return [strokes[0]].concat(idx.map(i => strokes[i])); }
  function variation(sources, rng, pDrop = 0.3) { let A = rng.pick(sources).s; if (rng.u() < 0.5 && sources.length > 1) A = recombine(A, rng.pick(sources).s, rng); if (rng.u() < pDrop) A = dropMinor(A, rng).kept; if (rng.u() < 0.5) A = reorder(A, rng);
    return affine(A, rng.uni(0.85, 1.15), rng.uni(0.88, 1.12), rng.uni(-0.12, 0.12)); }

  function resample(stroke, step = 2) { if (stroke.length < 2) return [stroke[0], [stroke[0][0] + step, stroke[0][1]]]; const cum = [0]; for (let i = 1; i < stroke.length; i++) cum.push(cum[i - 1] + Math.hypot(stroke[i][0] - stroke[i - 1][0], stroke[i][1] - stroke[i - 1][1]));
    const L = cum[cum.length - 1]; if (L < 1e-6) return [stroke[0], [stroke[0][0] + step, stroke[0][1]]]; const n = Math.max(2, Math.floor(L / step) + 1), out = []; let j = 0;
    for (let k = 0; k < n; k++) { const u = L * k / (n - 1); while (j < cum.length - 2 && cum[j + 1] < u) j++; const w = (u - cum[j]) / Math.max(cum[j + 1] - cum[j], 1e-9); out.push([stroke[j][0] + w * (stroke[j + 1][0] - stroke[j][0]), stroke[j][1] + w * (stroke[j + 1][1] - stroke[j][1])]); } return out; }
  function executeStroke(stroke, p, rng, t0) { let pts = resample(stroke, 2); const n0 = pts.length; let d = [pts[n0 - 1][0] - pts[n0 - 2][0], pts[n0 - 1][1] - pts[n0 - 2][1]]; const dn = Math.hypot(d[0], d[1]) || 1; d = [d[0] / dn, d[1] / dn];
    const ang = rng.uni(-Math.PI, Math.PI), hook = p.hook * rng.uni(0.3, 1); pts = [[pts[0][0] + hook * Math.cos(ang), pts[0][1] + hook * Math.sin(ang)]].concat(pts);
    const over = p.overshoot * rng.uni(0.2, 1); if (over > 2) { const k = Math.max(1, Math.floor(over / 2)), last = pts[pts.length - 1]; for (let i = 0; i < k; i++) { const e = k === 1 ? over : 2 + (over - 2) * i / (k - 1); pts.push([last[0] + d[0] * e, last[1] + d[1] * e]); } }
    const n = pts.length; const raw = []; for (let i = 0; i < n; i++) raw.push([rng.norm(0, p.tremor), rng.norm(0, p.tremor)]); const noise = raw.map((_, i) => { let sx = 0, sy = 0; for (let j = Math.max(0, i - 2); j <= Math.min(n - 1, i + 2); j++) { sx += raw[j][0]; sy += raw[j][1]; } return [sx / 5, sy / 5]; });
    const amp = p.drift * rng.uni(0.4, 1), f = rng.uni(0.5, 1.5), ph = rng.uni(0, 2 * Math.PI); const out = [];
    for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)]; let tx = b[0] - a[0], ty = b[1] - a[1]; const tn = Math.hypot(tx, ty) || 1; tx /= tn; ty /= tn; const dr = amp * Math.sin(2 * Math.PI * f * i / (n - 1) + ph); out.push([pts[i][0] + noise[i][0] - ty * dr, pts[i][1] + noise[i][1] + tx * dr]); }
    const t = [t0]; let prev = null; for (let i = 1; i < n; i++) { const seg = Math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]); const v = [out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]]; const vn = Math.hypot(v[0], v[1]) || 1; v[0] /= vn; v[1] /= vn;
      let turn = 0; if (prev) turn = Math.acos(Math.max(-1, Math.min(1, v[0] * prev[0] + v[1] * prev[1]))); prev = v; const speed = p.speed * (0.3 + 0.7 * Math.exp(-3 * turn)) * rng.uni(0.85, 1.15), ramp = Math.min(1, 0.3 + (i - 1) / 6); t.push(t[i - 1] + seg / (speed * ramp)); }
    return { t, xy: out }; }

  const mapF = (f, strokes) => strokes.map(s => s.map(([x, y]) => [(x - BOX / 2) * f.scale + f.anchor[0], (y - BOX / 2) * f.scale + f.anchor[1]]));
  function farCorner(anchor, rng, scale) { let best = null, bd = -1; CORNERS.forEach(c => { const d = Math.hypot(c[0] - anchor[0], c[1] - anchor[1]); if (d > bd) { bd = d; best = c; } }); return { anchor: [best[0] + rng.uni(-15, 15), best[1] + rng.uni(-15, 15)], scale: scale * rng.uni(0.5, 0.7) }; }
  function teamBox(canvas, margin = 20) { const pts = []; canvas.forEach(s => { if (s.kind === 'plan' || s.kind === 'extra' || s.kind === 'fix' || s.kind === 'human') pts.push(...s.xy); }); if (!pts.length) return null; const [lo, hi] = bbox([pts]); return [[lo[0] - margin, lo[1] - margin], [hi[0] + margin, hi[1] + margin]]; }
  const inside = (box, xy) => { if (!box) return false; const m = mean(xy); return m[0] >= box[0][0] && m[1] >= box[0][1] && m[0] <= box[1][0] && m[1] <= box[1][1]; };
  function scribbleOver(xy, rng) { const [lo, hi] = bbox([xy]); const n = 3 + rng.int(3), pts = []; for (let i = 0; i <= n; i++) pts.push([lo[0] - 4 + (hi[0] - lo[0] + 8) * i / n, i % 2 === 0 ? lo[1] - 4 : hi[1] + 4]); return pts; }
  function inferFrame(plan, canvas, ownScale) { const drawn = canvas.filter(s => s.kind === 'plan' && s.src >= 0); if (!drawn.length) {
      // nothing of the plan yet: a person's strokes say where the figure is (the bots align to the first person to draw)
      const human = canvas.filter(s => s.kind === 'human'); if (!human.length) return null; const pts = []; human.forEach(s => pts.push(...s.xy)); const [lo, hi] = bbox([pts]); return { anchor: [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2], scale: ownScale }; }
    const src = [], dst = []; drawn.forEach(s => { src.push(...plan[s.src]); dst.push(...s.xy); });
    const [ls, hs] = bbox([src]), [ld, hd] = bbox([dst]); const ss = [Math.max(hs[0] - ls[0], 8), Math.max(hs[1] - ls[1], 8)], sd = [Math.max(hd[0] - ld[0], 8), Math.max(hd[1] - ld[1], 8)];
    const scale = drawn.length > 1 ? Math.max(0.4, Math.min(2.5, (sd[0] / ss[0] + sd[1] / ss[1]) / 2)) : ownScale; return { anchor: [(ld[0] + hd[0]) / 2 - ((ls[0] + hs[0]) / 2 - BOX / 2) * scale, (ld[1] + hd[1]) / 2 - ((ls[1] + hs[1]) / 2 - BOX / 2) * scale], scale }; }
  function transplant(plan, donor, rng) { const [lp, hp] = bbox(plan), [ld, hd] = bbox(donor); const sp = [Math.max(hp[0] - lp[0], 1), Math.max(hp[1] - lp[1], 1)], sd = [Math.max(hd[0] - ld[0], 1), Math.max(hd[1] - ld[1], 1)];
    const dp = plan.map(s => descriptor(s, lp, sp)); const gaps = donor.map(s => { const d = descriptor(s, ld, sd); return Math.min(...dp.map(q => dist(d, q))); }); let j = 0; gaps.forEach((g, i) => { if (g > gaps[j]) j = i; }); if (rng.u() >= 0.7) j = rng.int(donor.length);
    return donor[j].map(([x, y]) => [(x - ld[0]) / sd[0] * sp[0] + lp[0], (y - ld[1]) / sd[1] * sp[1] + lp[1]]); }

  function say(b, t, kind, kw = {}) { const arr = LINES[kind]; let line = arr[(b.lines + b.name.length) % arr.length]; b.lines++; Object.entries(kw).forEach(([k, v]) => { line = line.split('{' + k + '}').join(v); }); b.bubble = { t, text: line }; if (b.onSay) b.onSay(t, line); }
  function makeBot(i, name, chaos, rng, cfg = {}) { const r = rng.u(), pOff = 0.6 * chaos * chaos; let behaviour = r > pOff ? 'team' : (r > pOff / 3 ? 'solo' : 'misheard'); if (i === 0 && !cfg.behaviour) behaviour = 'team'; if (cfg.behaviour && cfg.behaviour !== 'auto') behaviour = cfg.behaviour;
    const persona = cfg.persona && cfg.persona !== 'random' ? cfg.persona : rng.pick(Object.keys(PERSONAS));
    return { name, color: COLORS[Math.max(0, NAMES.indexOf(name)) % COLORS.length], persona, behaviour, skill: Math.max(0.05, Math.min(1, rng.norm(0.8 - 0.6 * chaos, 0.15))), stubborn: Math.max(0, Math.min(1, rng.norm(0.2 + 0.6 * chaos, 0.2))), copycat: 0.25 * chaos * rng.u(), fixer: 0.35 * chaos * rng.u(), belief: null, ownPlan: null, ownWord: '', ownNext: 0, freeAt: 0, lastXY: null, strokes: 0, noticed: new Set(), calledOut: 0, inCorner: false, lines: 0, bubble: null, here: true, leaving: false, onSay: null }; }
  function shareableOf(srcOf) { return word => { const all = srcOf(word) || []; const s = all.filter(d => d.s.length >= 4); return s.length ? s : all; }; }
  function startRound(word, bots, chaos, rng, t0, dur, srcOf) { const shareable = shareableOf(srcOf); const words = srcOf.words ? srcOf.words() : [];
    const known = shareable(word).length > 0;
    let plan = [], nCore = 0; if (known) { plan = variation(shareable(word), rng, 0); const details = []; for (let i = 0; i < EXTRAS; i++) { const r = dropMinor(plan, rng); if (r.dropped) { details.push(r.dropped); plan = r.kept; } } nCore = plan.length; plan = plan.concat(details); }
    const frame = { anchor: [W / 2 + rng.uni(-40, 40), H / 2 + rng.uni(-25, 25)], scale: rng.uni(1.0, 1.25) };
    bots.forEach(b => { const err = [(1 - b.skill) * rng.uni(-110, 110), (1 - b.skill) * rng.uni(-70, 70)]; b.belief = { anchor: [frame.anchor[0] + err[0], frame.anchor[1] + err[1]], scale: frame.scale * Math.max(0.5, Math.min(1.8, rng.norm(1, 0.35 * (1 - b.skill)))) };
      b.ownNext = 0; b.strokes = 0; b.freeAt = t0 + rng.uni(0.3, 2.5); b.lastXY = null; b.noticed = new Set(); b.calledOut = 0; b.inCorner = false; b.bubble = null;
      if (!known) { say(b, b.freeAt, 'unknown', { word }); b.freeAt = Infinity; return; }
      if (b.behaviour === 'solo') { b.ownWord = word; b.ownPlan = variation(shareable(word), rng); say(b, b.freeAt, 'solo', { word }); b.belief = farCorner(b.belief.anchor, rng, frame.scale); b.inCorner = true; }
      else if (b.behaviour === 'misheard') { const others = words.filter(w => w !== word && shareable(w).length); if (others.length) { b.ownWord = rng.pick(others); b.ownPlan = variation(shareable(b.ownWord), rng); say(b, b.freeAt, 'misheard', { word, other: b.ownWord }); } else b.behaviour = 'team'; } });
    return { word, known, plan, nCore, frame, claimed: {}, canvas: [], t0, tEnd: t0 + dur, chaos, rng, bots, over: false, shareable }; }
  function step(R, b) { const t = b.freeAt, rng = R.rng, plan = R.plan, canvas = R.canvas, chaos = R.chaos, word = R.word; const P = PERSONAS[b.persona];
    if (b.leaving) { b.here = false; say(b, t, 'leave'); b.freeAt = Infinity; return; }
    if (b.behaviour === 'team') { const inf = inferFrame(plan, canvas, b.belief.scale); if (inf) { const w = (1 - b.stubborn) * 0.7; b.belief = { anchor: [b.belief.anchor[0] + w * (inf.anchor[0] - b.belief.anchor[0]), b.belief.anchor[1] + w * (inf.anchor[1] - b.belief.anchor[1])], scale: b.belief.scale + w * (inf.scale - b.belief.scale) }; } }
    let action = null; const others = canvas.filter(s => s.bot !== b.name); const box = teamBox(canvas);
    if (b.behaviour === 'team') { const foreign = canvas.map((s, i) => [i, s]).filter(([i, s]) => (s.kind === 'solo' || s.kind === 'misheard') && !b.noticed.has(i) && inside(box, s.xy));
      if (foreign.length && b.noticed.size < CALLOUTS) { const [i, s] = foreign[foreign.length - 1]; b.noticed.add(i); const culprit = R.bots.find(x => x.name === s.bot); if (culprit) culprit.calledOut++; const scr = canvas.filter(x => x.kind === 'scribble' && x.bot === b.name).length;
        if (b.fixer > 0 && scr < SCRIBBLES && rng.u() < Math.min(0.6, b.fixer * 3) && !s.scribbled) { s.scribbled = true; say(b, t, 'scribble'); action = ['scribble', scribbleOver(s.xy, rng), -1]; } else say(b, t, 'foreign', { word }); } }
    else if (b.calledOut && !b.inCorner && rng.u() < 1 - b.stubborn) { if (b.behaviour === 'misheard' && rng.u() < 0.6) { say(b, t, 'realise', { word }); b.behaviour = 'team'; b.ownPlan = null; b.calledOut = 0; } else { say(b, t, 'retreat'); b.belief = farCorner(b.belief.anchor, rng, R.frame.scale); b.inCorner = true; b.calledOut = 0; } }
    if (!action && b.fixer > 0 && others.length && rng.u() < b.fixer) { for (const s of others.slice(-4).reverse()) { if (s.kind === 'plan' && s.src >= 0) { const want = mapF(b.belief, [plan[s.src]])[0]; const m1 = mean(want), m2 = mean(s.xy); if (Math.hypot(m1[0] - m2[0], m1[1] - m2[1]) > 28) { action = ['fix', want, s.src]; break; } } } }
    if (!action && b.copycat > 0 && others.length && rng.u() < b.copycat) { const s = others[others.length - 1 - rng.int(Math.min(3, others.length))]; const dx = (1 - b.skill) * rng.uni(-18, 18), dy = (1 - b.skill) * rng.uni(-18, 18); action = ['copy', s.xy.map(([x, y]) => [x + dx, y + dy]), s.src]; }
    if (!action) { if (b.behaviour === 'team') { let nxt = -1; for (let i = 0; i < plan.length; i++) if (!(i in R.claimed)) { nxt = i; break; }
        if (nxt < 0) { const extras = canvas.filter(s => s.kind === 'extra').length;
          if (chaos >= 0.4 && extras < EXTRAS && rng.u() < chaos * 0.5) { const donor = rng.pick(R.shareable(word)).s; action = ['extra', mapF(b.belief, [transplant(plan, donor, rng)])[0], -1]; say(b, t, 'detail'); }
          else { b.freeAt = t + rng.uni(2, 5); if (rng.u() < 0.3 + chaos) return; b.freeAt = R.tEnd; return; } }
        if (!action) { R.claimed[nxt] = b.name; action = ['plan', mapF(b.belief, [plan[nxt]])[0], nxt]; if (nxt >= R.nCore && rng.u() < 0.5) say(b, t, 'detail'); else if (b.strokes === 0 && b.skill < 0.5) say(b, t, 'confused', { word }); else if (rng.u() < 0.3) say(b, t, 'claim', { part: ['roof', 'the door', 'a window', 'this line', 'the top', 'the side', 'this part'][nxt % 7] }); } }
      else { if (b.ownNext >= b.ownPlan.length) { b.freeAt = R.tEnd; return; } action = [b.behaviour === 'solo' ? 'solo' : 'misheard', mapF(b.belief, [b.ownPlan[b.ownNext]])[0], -1]; b.ownNext++; } }
    const [kind, xy, idx] = action; if (kind === 'fix') say(b, t, 'fix'); if (kind === 'copy') say(b, t, 'copy');
    const travel = b.lastXY ? Math.hypot(xy[0][0] - b.lastXY[0], xy[0][1] - b.lastXY[1]) / TRAVEL : 0; const ex = executeStroke(xy, P, rng, t + travel);
    if (ex.t[ex.t.length - 1] > R.tEnd + 2) { b.freeAt = R.tEnd; return; }
    canvas.push({ bot: b.name, color: b.color, t: ex.t, xy: ex.xy, kind, src: idx, scribbled: false }); b.strokes++; b.lastXY = ex.xy[ex.xy.length - 1]; b.freeAt = ex.t[ex.t.length - 1] + P.think * rng.uni(0.4, 1.6); }
  function advance(R, t) { for (let guard = 0; guard < 200; guard++) { const active = R.bots.filter(b => b.here && b.freeAt <= t && (b.freeAt < R.tEnd + 1e-9 || b.leaving)); if (!active.length) break; const b = active.reduce((a, c) => c.freeAt < a.freeAt ? c : a); step(R, b); }
    if (!R.over && t >= R.tEnd) R.over = true; }
  /* a person's stroke on the canvas (the service feeds these in): the bots treat it as part of the figure */
  function humanStroke(R, playerId, xy, t) { R.canvas.push({ bot: 'human:' + playerId, color: '#888', t: xy.map(() => t), xy, kind: 'human', src: -1, scribbled: false }); }
  const roomTarget = h => Math.max(0, Math.min(FILL_TO, SEATS - RESERVE - h));
  /* a bot joining a round in progress */
  function joinRound(R, name, chaos, cfg, t) { const b = makeBot(R.bots.length, name, chaos, R.rng, cfg || {}); const err = [(1 - b.skill) * R.rng.uni(-60, 60), (1 - b.skill) * R.rng.uni(-40, 40)]; b.belief = { anchor: [R.frame.anchor[0] + err[0], R.frame.anchor[1] + err[1]], scale: R.frame.scale }; b.freeAt = t + R.rng.uni(1, 3);
    if (!R.known) { b.freeAt = Infinity; } else if (b.behaviour !== 'team') { b.ownWord = R.word; b.ownPlan = variation(R.shareable(R.word), R.rng); b.belief = farCorner(b.belief.anchor, R.rng, R.frame.scale); b.inCorner = true; b.behaviour = 'solo'; }
    say(b, t, 'join'); R.bots.push(b); return b; }

  return { BOX, W, H, SEATS, FILL_TO, RESERVE, EXTRAS, PERSONAS, NAMES, COLORS, LINES, rngOf, variation, executeStroke, makeBot, startRound, step, advance, humanStroke, roomTarget, joinRound, farCorner, mapF, say, shareableOf };
});
