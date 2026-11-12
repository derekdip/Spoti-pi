/* The adapter contract, as a mock game. The real adapter for Doodle Figure implements the same
   methods over the game's web-client transport (the one a phone uses), one connection per bot.

   Calls the service makes:
     connect(roomCode)            join the room; resolve when the room state is known
     join(botName) / leave(botName)   a bot takes or gives up a web seat
     penDown(botName, [x, y]) / penMove(botName, [x, y]) / penUp(botName)   pen events, x and y in [0, 1] of the game canvas
     say(botName, text)           optional: a chat line or emote, if the game has one
     disconnect()
   Events the adapter emits (on(name, handler)):
     'players'  -> [humanPlayerId, ...]        the people (not bots) in the room, whenever it changes
     'round'    -> { word, seconds }           a round started
     'roundEnd' -> {}                          the round ended
     'stroke'   -> { playerId, points: [[x, y], ...] }   a person drew a stroke (normalised), so the bots can align to it
     'closed'   -> {}                          the room closed (the VR player left)

   The mock plays five rounds of 20 seconds cycling the bank's words, has people arrive and leave,
   and closes. It counts pen events per bot so the loop can be checked without the game. */
'use strict';
class MockGame {
  constructor(opts = {}) { this.h = {}; this.words = opts.words || ['house', 'cat', 'bicycle', 'skateboard', 'tree', 'fish']; this.roundSeconds = opts.roundSeconds || 20; this.rounds = opts.rounds || 5; this.humans = []; this.counts = {}; this.timers = []; }
  on(name, fn) { this.h[name] = fn; }
  emit(name, payload) { if (this.h[name]) this.h[name](payload); }
  async connect(room) { this.room = room; const after = (ms, fn) => this.timers.push(setTimeout(fn, ms));
    let t = 1500;
    for (let r = 0; r < this.rounds; r++) { const word = this.words[r % this.words.length];
      after(t, () => { this.emit('round', { word, seconds: this.roundSeconds }); });
      after(t + this.roundSeconds * 1000, () => { this.emit('roundEnd', {}); });
      t += (this.roundSeconds + 5) * 1000; }
    // people: two join during round 1, a third during round 2 (a bot leaves), one person draws a stroke first in round 3, two more join in round 4 (two bots leave), one leaves in round 5 (a bot returns)
    after(6000, () => this.person('+', 'p1')); after(12000, () => this.person('+', 'p2')); after(32000, () => this.person('+', 'p3'));
    after(53000, () => this.emit('stroke', { playerId: 'p1', points: [[0.3, 0.4], [0.5, 0.35], [0.7, 0.4]] }));
    after(80000, () => this.person('+', 'p4')); after(84000, () => this.person('+', 'p5')); after(108000, () => this.person('-', 'p5'));
    after(t + 2000, () => this.emit('closed', {}));
    return true; }
  person(op, id) { if (op === '+') this.humans.push(id); else this.humans = this.humans.filter(x => x !== id); console.log(`  (mock) person ${id} ${op === '+' ? 'joined' : 'left'}: ${this.humans.length} people`); this.emit('players', this.humans.slice()); }
  join(name) { this.counts[name] = this.counts[name] || { down: 0, move: 0, up: 0, say: 0 }; console.log(`  (mock) seat taken by ${name}`); }
  leave(name) { console.log(`  (mock) seat freed by ${name} (${JSON.stringify(this.counts[name])})`); }
  penDown(name, p) { this.counts[name].down++; this.last = p; }
  penMove(name, p) { this.counts[name].move++; }
  penUp(name) { this.counts[name].up++; }
  say(name, text) { this.counts[name].say++; console.log(`  (mock) ${name}: ${text}`); }
  disconnect() { this.timers.forEach(clearTimeout); console.log('  (mock) disconnected; pen events per bot: ' + JSON.stringify(this.counts)); setTimeout(() => process.exit(0), 50); }
}
module.exports = MockGame;
