# Doodle bots for Doodle Figure: a bank of real doodles, a hand, and bots that share a frame

A prototype, built 2026-10-21, for the party mode of Doodle Figure
(Binary Bit Studio: one to seven web players draw a word together on
a shared canvas, the VR player builds a 3D model of the drawing). The
ask: bots that draw together or struggle to, that leave as people
arrive, whose drawings are believable, coherent and do not repeat,
with no hand-authored paths and no language model in the loop. Code
in `poc/doodle/`, numbers in `poc/results/doodle_eval.md`, the viewer
at `poc/results/doodle-bots.html`.

## The idea, in this project's terms

A drawing is a clip. The lesson of the locomotion case
(`docs/gait3d-runtime.md`, G13) was that the deployable description
of a motion is the teacher's own clip with edits, not a grammar
fitted to statistics, and the same holds here with less effort: the
teacher is people. The Quick, Draw! dataset (Google, CC BY 4.0) holds
about fifty million human doodles of 345 words as ordered strokes,
each drawn in twenty seconds by someone asked for that word, with a
flag for whether it was recognised. That is a bank of clips per word,
free, in exactly the game's register.

Variation comes from causes, not from the paths:

- **Edits of a doodle** (`edits.py`): one stroke borrowed from
  another doodle of the same word, matched by where it sits and how
  big it is; a minor stroke dropped; the order after the first stroke
  shuffled; scale, aspect and tilt changed. Every step keeps the
  drawing a drawing of the word because every source was one.
- **A hand** (`hand.py`): a persona executes the strokes as timed pen
  motion: a hook where the pen lands, slowing at corners, tremor,
  a slow drift across the stroke, overshoot at the end, a think pause
  and pen-up travel between strokes. Five personas (neat, quick,
  shaky, lazy, bold). The same plan drawn twice by the same hand is
  two drawings.
- **Collaboration from one mechanism** (`bots.py`): a round has a
  shared plan (a variation of the word) and a frame, where on the
  canvas the figure goes and how big. No bot knows the frame. Each
  holds a belief, wrong by an amount set by its skill, and a team bot
  corrects its belief from what is already on the canvas, by as much
  as its stubbornness allows: one stroke fixes the anchor (the second
  person aligns to the first), two fix the scale. Bots claim the
  plan's next unclaimed stroke. Minor strokes of the plan are held
  back as details to add once the figure stands.
- **Chaos as a knob** in [0, 1]: it sets how wrong beliefs start, how
  stubborn bots are, the share of bots that are not team (solo: their
  own variation of the word, in a corner of the canvas at a smaller
  scale, doing their own thing; misheard: a variation of another
  word, drawn where the figure is because they think they are
  helping), and two traits any bot can have, copycat (retraces a
  stroke someone just drew) and fixer (redraws another bot's stroke
  where its own belief says it belongs). Bots speak short lines at
  their events ("I'll do the roof", "wait, where is it?", "that's not
  where it goes", "house? I heard cat").
- **Interference is a scene, not a shrug.** A stroke that lands inside
  the team's figure from a bot that is not on the team gets called out
  by the next team bot to notice ("who drew that?", "that's not a
  house"); a fixer may scribble it out, at most twice a round; the
  culprit, if not too stubborn, retreats to a corner ("fine, I'll go
  over here"), and a misheard bot may realise instead ("cat? oh,
  house!") and join the team. Team bots give up calling out after
  three, so a stubborn intruder becomes the running joke rather than
  a wall of complaints.
- **The room**: eight seats, one VR and seven web. Bots fill the web
  seats to four when the room is empty, stay as the first people
  arrive (company), and leave one by one, at the end of the current
  stroke, once the web seats are within one of full: the third person
  sends one bot away, the sixth sends the last. A person can always
  join; bots never block one.

## What was measured

`evaluate.py`, in this project's habit of scoring what a reader reads.
A nearest-neighbour classifier over the six sampled words (house,
cat, bicycle, tree, sun, fish; k = 7 on 32 by 32 bitmaps) trained on
1500 human doodles per word, applied to 400 held-out humans (the
ceiling), to bank variations, to variations drawn by a hand, and to
whole collaborative canvases at three chaos levels.

| | held-out humans | bank variations | drawn by a hand | whole canvas, chaos 0.15 | 0.5 | 0.85 | team's figure, chaos 0.15 | 0.5 | 0.85 |
|---|---|---|---|---|---|---|---|---|---|
| classified as the word, mean of six | 0.90 | 0.89 | 0.87 | 0.76 | 0.49 | 0.31 | 0.79 | 0.59 | 0.39 |
| worst word | sun 0.76 | sun 0.74 | sun 0.72 | sun 0.60 | sun 0.18 | sun 0.03 | sun 0.62 | sun 0.23 | sun 0.03 |
| best word | tree 0.98 | bicycle 0.95 | bicycle 0.96 | bicycle 0.90 | bicycle 0.77 | tree 0.67 | tree 0.93 | tree 0.92 | tree 0.78 |

The whole-canvas columns score everything, a solo bot's corner figure
and the scribbles included; the team's-figure columns score what the
team drew, which is what the VR player builds.

Novelty: a variation's distance to its nearest bank doodle (its own
source and donors excluded) equals a fresh human doodle's (0.74
against 0.72 on house, within 0.01 on every word), so a variation is
not a copy of anything in the bank. The spread of twenty variations
of one source equals the spread of twenty people on this coarse
distance, which saturates for anything not near-identical, so it says
only that they are not near-identical.

Reading: a bot's single drawing is as recognisable as a fresh
person's and as new. A team at low chaos keeps most of that (0.79 on
its figure); the chaos knob takes it down to 0.59 and 0.39, which is
the knob doing its job. Two defects were found and fixed on the way, by
measuring each factor in turn (`poc/doodle/bots.py` carries the
notes): details transplanted from other doodles cost up to a third
of the coherence, so details are now the plan's own held-back
strokes; and the non-team share at low chaos was 8 percent per bot,
a third of four-bot rounds with a second figure, so it now grows with
the square of chaos. The sun and the fish stay the fragile words: a
sun is a circle with rays and a misplaced ray is a different thing;
these are also the words the classifier is worst at on people.

## The studio: a tool for the stream

`poc/results/doodle-bots-live.html` (built by `export_live.py` and
`build_live.py` from `live_template.html`) runs the whole simulation
in the browser, so a round can be configured and watched live with
no Python: word, number of bots, chaos, round length, speed, a seed
that reproduces a round, and per-bot persona and behaviour (auto,
team, solo in a corner, misheard). "+ person joins" and "− person
leaves" drive the room rule live: a bot finishes its stroke, says
bye and greys out. The Bank tab shows 300 doodles per word as
thumbnails; starring a doodle keeps it (in this browser) and, when
any doodle of a word is starred, the bots draw that word only from
the stars. "Copy stars as JSON" gives the list; saved as
`poc/results/doodle_curated.json`, `bank.load_bank(curated=...)` makes
the Python side use the same picks. The configuration the stream
needs is therefore a set of stars per word, a chaos level and a seed.

## What this does not do, and what it needs from the game

- **The words.** Six were sampled. Quick, Draw! has 345; the game's
  hardcoded prompts that are among them are covered at once by
  pulling that word's file. A prompt outside the 345 needs either a
  few doodles drawn by hand (five to ten per word is enough for a
  bank with edits; faster than coding paths) or a composition of
  known words with a spatial relation ("cat on a bicycle": a cat
  variation placed on a bicycle variation), which is the one place a
  language model would earn its keep later: mapping a custom word to
  parts the bank has and a relation, offline, never drawing.
- **Attribution.** CC BY 4.0: a credit line in the game for the
  dataset. To be confirmed against the licence text before shipping.
- **The game's stroke protocol.** The bots are headless web clients:
  they should join through the same path a phone does and send the
  same stroke events, so the server treats them as players and the
  VR player sees them as players. The prototype emits strokes as
  timed polylines on a 640 by 420 canvas; the mapping to the game's
  canvas and event format is the integration work, and the hand
  model's timing is what makes a bot look like a person drawing
  rather than a path appearing.
- **The room rule in the game**: the target is a function of the
  number of people present (`room_target`); a bot leaves at the end
  of its current stroke, with a line; whether a bot can rejoin when
  a person leaves is a design choice (the prototype does not).
- **Eyes on it.** The classifier is a stand-in for the VR player
  reading the drawing. The viewer is the real test; the chaos levels
  that look like fun rather than noise are a judgement, and the
  prototype's sessions at 0.1, 0.4, 0.5, 0.7 and 0.85 are there to
  make it.

## Files

- `poc/doodle/bank.py`, `edits.py`, `hand.py`, `bots.py`,
  `evaluate.py`; the recorded-session viewer `export_web.py`,
  `build_web.py`, `web_template.html`; the studio `export_live.py`,
  `build_live.py`, `live_template.html`.
- `poc/results/doodle_bank/<word>.ndjson`: the first 4000 records of
  six words from the public bucket (`gs://quickdraw_dataset/full/simplified/`).
- `poc/results/doodle_eval.md`, `doodle_sessions.json`,
  `doodle-bots.html`, `doodle_live_bank.json`, `doodle-bots-live.html`.
