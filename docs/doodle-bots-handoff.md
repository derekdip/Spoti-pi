# Handoff: drawing bots for Doodle Figure's party mode

For the chat that integrates the bots with the game. Everything
referenced here is on the branch
`claude/vr-simulation-ecs-compression-iuraw7` of this repository
(`derekdip/Spoti-pi`). The design and the measurements are in
`docs/doodle-bots.md`; this page says only what to build and how.

## What exists and works

A bot service that joins a game room as web players and draws the
round's word together with the other players, round after round,
until the room closes. It is plain Node (version 18 or later), no
dependencies, five files:

| file | what | size |
|---|---|---|
| `poc/doodle/sim.js` | the simulation: the bank edits, the hand, the bots' beliefs and scenes, the room rule | 25 KB |
| `poc/doodle/run_bots.js` | the service: takes a room code, loops rounds, paces strokes out as pen events in real time | 8 KB |
| `poc/doodle/adapters/mock.js` | the adapter contract, as a mock game; the service is verified against it | 4 KB |
| `poc/doodle/adapters/doodlefigure.js` | the skeleton of the real adapter, every game-specific fact marked TODO | 5 KB |
| `poc/results/doodle_live_bank.json` | the bank: 300 real human doodles for each of six words (house, cat, bicycle, tree, sun, fish) | 840 KB |

Copy those five into the game's repository (or run them from this
one). Verify the loop first, before touching the game:

```
node poc/doodle/run_bots.js --room DEMO --bots 4 --chaos 0.4 --seed 7 --adapter mock
```

That plays five rounds of twenty seconds against the mock: bots join,
draw, people arrive and bots leave after their stroke, an unknown
word is sat out, a person leaving brings a bot back, the room closes
and every seat is freed. The last line prints pen events per bot.

The same simulation runs in a page, the studio,
`poc/results/doodle-bots-live.html`: open it in a browser (no server
needed) to watch bots draw with any word, bot count, chaos, seed and
per-bot setup, and to star the doodles the bots may use. Rebuild it
after changing the bank with `python3 poc/doodle/build_live.py`.

## The one thing to build: the adapter

`poc/doodle/adapters/doodlefigure.js` is a skeleton of a class with
this contract (the mock is the reference implementation):

Calls the service makes on the adapter:

- `connect(roomCode)`: join the room; resolve when the room's state is known.
- `join(botName)`, `leave(botName)`: a bot takes or frees a web seat. One connection per bot, so the server and the VR player see ordinary web players.
- `penDown(botName, [x, y])`, `penMove(botName, [x, y])`, `penUp(botName)`: pen events with x and y in [0, 1] of the game's canvas. The service sends moves at about a hundred a second; thin them to what the phone client sends (the skeleton does, at 40 a second).
- `say(botName, text)`: a chat line or emote if the game has one; leave empty otherwise.
- `disconnect()`.

Events the adapter emits with `on(name, handler)`:

- `'players'` with `[humanId, ...]`: the people (not bots) in the room, whenever it changes. The room rule runs on this.
- `'round'` with `{ word, seconds }`: a round started. The bots draw that word for that long.
- `'roundEnd'` with `{}`.
- `'stroke'` with `{ playerId, points: [[x, y], ...] }` in [0, 1]: a person finished a stroke. The bots align their figure to the first person who draws.
- `'closed'` with `{}`: the room closed (the VR player left). The service frees every seat and exits.

The facts only the game knows, marked TODO in the skeleton: the
socket endpoint and library, the join and leave messages, the pen
message format and the canvas size, the round and player messages,
and whether a web player must press Start when no person is present
(if so, set the flag and the first bot presses it after a pause).

## Parameters

- Room rule, at the top of `sim.js`: `SEATS = 7` web seats,
  `FILL_TO = 4` bots in an empty room, `RESERVE = 1` seat always kept
  for a person. Bots stay as the first people arrive; the third
  person sends one bot away, the sixth the last; a person leaving
  brings a bot back.
- Service flags: `--bots` (at most how many), `--chaos` in [0, 1]
  (0.3 is a team with a little confusion; 0.6 has a corner artist or
  a misheard word most rounds; 0.85 is a brawl), `--seed` (the same
  seed, word and settings reproduce a round), `--stars` (a JSON file
  of doodle ids per word; the bots then draw a word only from its
  stars), `--tick` (ms between service ticks, 33).
- Bot names and colours are in `sim.js` (`NAMES`, `COLORS`); the
  lines they say are in `LINES`.

## Words

The bank holds six words. The game's prompt list decides the rest:

- A prompt that is one of the Quick, Draw! dataset's 345 words is one
  file pull: `python3 poc/doodle/export_live.py` reads
  `poc/results/doodle_bank/<word>.ndjson`, which `gsutil cat
  gs://quickdraw_dataset/full/simplified/<word>.ndjson | head -n 2000`
  fetches (the bucket is public). Add the word to `WORDS` in
  `poc/doodle/bank.py` and rebuild the bank JSON.
- A prompt outside the 345 needs either five to ten doodles drawn by
  hand (put them in the bank JSON in the same format: `{id, s:
  [[[x, y], ...], ...]}` in a 256 box) or, later, a composition of
  known words. A language model's only place in this design is
  mapping a custom word to parts the bank has, offline; it never
  draws.
- A word the bank does not have is sat out: the bots say so and
  wait for the next round. Nothing breaks.

## Curating the bank

In the studio's Bank tab, star the doodles you like for a word, then
"Copy stars as JSON" and save it as `poc/results/doodle_curated.json`.
Pass it to the service with `--stars`. The format is
`{"house": ["id", ...], "cat": [...]}`; a word with no stars uses the
whole bank.

## Deployment

1. Now, for the stream: run the service from a laptop against the
   live site with the real adapter and a room code. Nothing in the
   game changes.
2. Later, in the site: host the same service beside the game server
   behind one endpoint, `POST /rooms/{code}/bots` with count, chaos
   and seed, called by a "play with bots" button. Then add what a
   shipped feature needs: only the room's host may request bots, a
   cap on the count, bots marked as bots and excluded from stats, a
   kill switch.

## Attribution

The bank is from the Quick, Draw! dataset (Google), licensed CC BY
4.0: a credit line in the game. Confirm against the licence text
before shipping.

## Do not

- Do not replay recorded sessions; run the simulation live so the
  bots react to people's strokes and to each other.
- Do not send a stroke as one message; pace the pen events by their
  times, which is what makes a bot look like a person drawing.
- Do not use a language model in the drawing loop.
- Do not change `sim.js` to fit the game; change the adapter. The
  studio and the service share that file so that what is tuned in
  the studio is what the service plays.
