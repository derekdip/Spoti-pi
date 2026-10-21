#!/usr/bin/env node
/* The bot service for Doodle Figure (docs/doodle-bots.md, "Deployment"): bots join a room as web
   players, draw the round's word together, loop round after round, fill and vacate seats as people
   come and go, and leave when the room closes.

     node poc/doodle/run_bots.js --room ABCD --bots 4 --chaos 0.3 --seed 7 [--stars poc/results/doodle_curated.json] [--adapter mock|<module>]

   The game is behind an adapter (one class, poc/doodle/adapters/mock.js is the model): the service
   asks it to connect bots to the room by code and to send pen events, and it tells the service when a
   round starts and ends, who is in the room, what people draw, and when the room closes. Everything
   else (the bank, the hand, the frame beliefs, the scenes, the room rule) is DoodleSim, the same code
   the studio page runs. Writing the adapter for the real game is the integration: the pen events are
   normalised to [0, 1] on the game's canvas, so only the transport is the game's. */
'use strict';
const path = require('path'), fs = require('fs');
const Sim = require('./sim.js');

function parseArgs(argv) { const a = { room: '', bots: 4, chaos: 0.3, seed: String(Date.now() % 100000), stars: '', adapter: 'mock', bank: path.join(__dirname, '..', 'results', 'doodle_live_bank.json'), tick: 33 };
  for (let i = 2; i < argv.length; i++) { const k = argv[i].replace(/^--/, ''); if (k in a) { const v = argv[++i]; a[k] = typeof a[k] === 'number' ? Number(v) : v; } } return a; }

class BotService {
  constructor(adapter, opts) { this.adapter = adapter; this.opts = opts; this.bank = JSON.parse(fs.readFileSync(opts.bank, 'utf8'));
    this.stars = opts.stars && fs.existsSync(opts.stars) ? JSON.parse(fs.readFileSync(opts.stars, 'utf8')) : {};
    this.srcOf = word => { const all = this.bank[word] || []; const st = new Set(this.stars[word] || []); if (st.size) { const s = all.filter(d => st.has(d.id)); if (s.length) return s; } return all; };
    this.srcOf.words = () => Object.keys(this.bank);
    this.humans = new Set(); this.round = null; this.t0 = null; this.timer = null; this.emitted = new Map(); this.roundIndex = 0; this.closed = false; this.bots = []; }

  log(msg) { const t = this.round ? (this.now() - 0).toFixed(1) : '-'; console.log(`[${t}s] ${msg}`); }
  now() { return this.t0 === null ? 0 : (Date.now() - this.t0) / 1000; }

  async start() {
    const A = this.adapter;
    A.on('players', humans => { this.humans = new Set(humans); this.applyRoom(); });
    A.on('round', ({ word, seconds }) => this.beginRound(word, seconds));
    A.on('roundEnd', () => this.endRound());
    A.on('stroke', ({ playerId, points }) => { if (this.round && !this.round.over) Sim.humanStroke(this.round, playerId, points.map(([x, y]) => [x * Sim.W, y * Sim.H]), this.now()); });
    A.on('closed', () => this.shutdown('the room closed'));
    await A.connect(this.opts.room);
    this.applyRoom(); this.log(`joined room ${this.opts.room}; waiting for a round`);
  }

  // the room rule: bots to hold given the people present; join and leave accordingly
  applyRoom() {
    if (this.closed) return; const target = Sim.roomTarget(this.humans.size); const present = this.bots.filter(b => b.here && !b.leaving);
    while (this.bots.filter(b => b.here && !b.leaving).length > Math.min(target, this.opts.bots)) { const leaver = this.bots.filter(b => b.here && !b.leaving).reduce((a, c) => c.strokes > a.strokes ? c : a); leaver.leaving = true; leaver.freeAt = Math.max(leaver.freeAt === Infinity ? 0 : leaver.freeAt, this.now()); this.log(`${leaver.name} will leave after this stroke`); if (!this.round) this.finishLeave(leaver); }
    while (this.bots.filter(b => b.here && !b.leaving).length < Math.min(target, this.opts.bots)) { const used = new Set(this.bots.filter(b => b.here).map(b => b.name)); const name = Sim.NAMES.find(n => !used.has(n)); if (!name) break;
      let b; if (this.round && !this.round.over) b = Sim.joinRound(this.round, name, this.opts.chaos, {}, this.now()); else { b = Sim.makeBot(this.bots.length, name, this.opts.chaos, this.rng || Sim.rngOf(this.opts.seed), {}); }
      b.onSay = (t, text) => this.adapter.say(b.name, text); if (!(this.round && !this.round.over)) this.bots.push(b); this.adapter.join(b.name); this.log(`${b.name} joined (${b.persona}, ${b.behaviour})`); }
  }
  finishLeave(b) { if (b.left) return; b.left = true; b.here = false; b.freeAt = Infinity; this.adapter.leave(b.name); this.log(`${b.name} left`); }

  beginRound(word, seconds) {
    this.roundIndex++; this.rng = Sim.rngOf(`${this.opts.seed}|${word}|${this.roundIndex}`); this.t0 = Date.now(); this.emitted = new Map();
    const bots = this.bots.filter(b => b.here && !b.leaving); bots.forEach(b => { b.onSay = (t, text) => this.adapter.say(b.name, text); });
    this.round = Sim.startRound(word, bots, this.opts.chaos, this.rng, 0, seconds, this.srcOf); this.round.bots = this.bots;     // leavers stay listed so their last stroke completes
    this.log(`round ${this.roundIndex}: "${word}" for ${seconds}s, ${bots.length} bots${this.round.known ? '' : ' (word not in the bank: the bots sit out)'}`);
    clearInterval(this.timer); this.timer = setInterval(() => this.tick(), this.opts.tick);
  }
  endRound() { if (!this.round) return; this.round.over = true; this.flush(this.now() + 10); clearInterval(this.timer); this.log(`round over: ${this.round.canvas.filter(s => s.kind !== 'human').length} bot strokes`); this.round = null; }

  // pace the strokes out as pen events, as their times come due
  tick() { if (!this.round) return; const t = this.now(); Sim.advance(this.round, t); this.flush(t);
    this.bots.forEach(b => { if (b.leaving && !b.left && b.freeAt === Infinity) this.finishLeave(b); });
    if (this.round.over && this.round.bots.every(b => !b.here || b.freeAt >= this.round.tEnd || b.freeAt === Infinity) && t > this.round.tEnd + 2) { clearInterval(this.timer); } }
  flush(t) { const R = this.round; R.canvas.forEach((s, i) => { if (s.kind === 'human') return; let k = this.emitted.get(i) || 0; if (k >= s.xy.length) return;
      while (k < s.xy.length && s.t[k] <= t) { const [x, y] = s.xy[k]; const p = [Math.max(0, Math.min(1, x / Sim.W)), Math.max(0, Math.min(1, y / Sim.H))];
        if (k === 0) this.adapter.penDown(s.bot, p); else this.adapter.penMove(s.bot, p); k++; }
      if (k >= s.xy.length) this.adapter.penUp(s.bot); this.emitted.set(i, k); }); }

  shutdown(why) { if (this.closed) return; this.closed = true; clearInterval(this.timer); this.log(`stopping: ${why}`); this.bots.filter(b => b.here && !b.left).forEach(b => this.finishLeave(b)); this.adapter.disconnect(); }
}

if (require.main === module) {
  const opts = parseArgs(process.argv); if (!opts.room) { console.error('usage: node run_bots.js --room CODE [--bots 4 --chaos 0.3 --seed 7 --stars file.json --adapter mock]'); process.exit(2); }
  const Adapter = require(opts.adapter === 'mock' ? './adapters/mock.js' : path.resolve(opts.adapter));
  const svc = new BotService(new Adapter(), opts); svc.start().catch(e => { console.error(e); process.exit(1); });
}
module.exports = { BotService, parseArgs };
