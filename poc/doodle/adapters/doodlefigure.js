/* The Doodle Figure adapter: a skeleton to fill in (docs/doodle-bots-handoff.md). It implements the
   contract in ./mock.js over the game's web-client transport. Every TODO is a fact about the game
   that only its code knows; nothing else needs to change.

   Assumptions made here, each to confirm against the web client:
   - one connection per bot, so the server sees each bot as a web player with its own seat and name;
   - a WebSocket (Node 22 has a global WebSocket client; swap in socket.io or fetch if the client uses those);
   - pen events are sent as the phone client sends them, in the game's canvas coordinates;
   - the server tells clients when a round starts (with the word and the duration), when it ends, who is
     in the room, and when the room closes.

   Run:  node poc/doodle/run_bots.js --room ABCD --bots 4 --chaos 0.3 --seed 7 --adapter ./poc/doodle/adapters/doodlefigure.js */
'use strict';

const GAME_URL = process.env.DOODLE_WS || 'wss://TODO.your-site/ws';     // TODO: the web client's socket endpoint
const CANVAS = { w: 1000, h: 1000 };                                      // TODO: the game canvas size the phone client sends coordinates in
const MOVE_HZ = 40;                                                       // pen moves per second to send (the hand produces ~100/s; thin to what the client sends)
const PRESS_START_WHEN_ALONE = false;                                     // TODO: true if a web player must press Start when no person is present

class DoodleFigure {
  constructor() { this.h = {}; this.sockets = new Map(); this.lastMove = new Map(); this.humans = new Set(); this.room = ''; }
  on(name, fn) { this.h[name] = fn; }
  emit(name, payload) { if (this.h[name]) this.h[name](payload); }

  // ---- room
  async connect(room) {
    this.room = room;
    // The service joins bots through join(); the room's state arrives on the first bot's socket.
    // If the game needs a "spectator" connection to learn the room state before any bot joins, open it here.
    return true;
  }
  disconnect() { for (const ws of this.sockets.values()) { try { ws.close(); } catch (e) {} } this.sockets.clear(); }

  // ---- seats: one socket per bot
  join(botName) {
    const ws = new WebSocket(GAME_URL); this.sockets.set(botName, ws);
    ws.addEventListener('open', () => {
      ws.send(JSON.stringify({ type: 'join', room: this.room, name: botName }));                 // TODO: the join message the phone client sends
    });
    ws.addEventListener('message', ev => this.onMessage(botName, JSON.parse(ev.data)));
    ws.addEventListener('close', () => { this.sockets.delete(botName); });
    ws.addEventListener('error', e => { console.error(`[${botName}] socket error`, e.message || e); });
  }
  leave(botName) { const ws = this.sockets.get(botName); if (!ws) return; try { ws.send(JSON.stringify({ type: 'leave' })); } catch (e) {} ws.close(); this.sockets.delete(botName); }   // TODO: the leave message, if any

  // ---- what the server says (TODO: the message types and fields are the game's)
  onMessage(botName, msg) {
    switch (msg.type) {
      case 'room': {                                                       // the player list changed
        const people = (msg.players || []).filter(p => !this.isBot(p.name)).map(p => p.id || p.name);
        this.humans = new Set(people); this.emit('players', people); break; }
      case 'round_start': this.emit('round', { word: msg.word, seconds: msg.seconds || 60 }); break;
      case 'round_end': this.emit('roundEnd', {}); break;
      case 'stroke':                                                       // a person's finished stroke: normalise to [0, 1]
        if (!this.isBot(msg.name)) this.emit('stroke', { playerId: msg.name, points: (msg.points || []).map(([x, y]) => [x / CANVAS.w, y / CANVAS.h]) }); break;
      case 'room_closed': this.emit('closed', {}); break;
      case 'lobby':                                                        // between rounds; if the game needs a web player to press Start
        if (PRESS_START_WHEN_ALONE && this.humans.size === 0 && [...this.sockets.keys()][0] === botName) setTimeout(() => this.send(botName, { type: 'start' }), 3000); break;
      default: break;
    }
  }
  isBot(name) { return this.sockets.has(name); }
  send(botName, obj) { const ws = this.sockets.get(botName); if (ws && ws.readyState === 1) ws.send(JSON.stringify(obj)); }

  // ---- the pen (TODO: the phone client's pen messages; these mirror a typical down/move/up protocol)
  penDown(botName, [x, y]) { this.lastMove.set(botName, 0); this.send(botName, { type: 'pen_down', x: x * CANVAS.w, y: y * CANVAS.h }); }
  penMove(botName, [x, y]) { const now = Date.now(); if (now - (this.lastMove.get(botName) || 0) < 1000 / MOVE_HZ) return; this.lastMove.set(botName, now); this.send(botName, { type: 'pen_move', x: x * CANVAS.w, y: y * CANVAS.h }); }
  penUp(botName) { this.send(botName, { type: 'pen_up' }); }
  say(botName, text) { /* TODO: a chat line or emote if the game has one; otherwise leave empty */ }
}
module.exports = DoodleFigure;
