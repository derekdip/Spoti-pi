# Reach-aware menus: a pilot, 2026-11-19

Exploratory, not preregistered. `poc/reach/menus.py`; record
`poc/results/reach/pilot.log` and `pilot/pilot_rows.json`.

The question: can a game learn, from 1 to 5 minutes of play, where a
player's hands comfortably go, and put menu buttons there? Eight
synthetic players differing in height, seated or standing, reach (0.71
to 0.93 of typical arm length) and handedness; 6 buttons, 3 per hand,
scored by how many fall inside the player's true 50% comfort region.

| placement | 1 minute | 2 minutes | 5 minutes |
|---|---|---|---|
| fixed panel (0.45 m ahead, 0.3 m below the eyes) | 0.1 | 0.1 | 0.1 |
| population model scaled to the player's height | 0.5 | 0.5 | 0.5 |
| personalised, cross-fitted stopping rule | 3.1 | 3.4 | 4.4 |
| personalised, a quarter of the reaches held out | 3.0 | 3.8 | 4.0 |
| personalised, 100 steps | 3.4 | 3.6 | 4.1 |
| personalised, trained to 1500 steps | 2.9 | 3.0 | 3.4 |
| personalised, best step on a fresh session | 3.6 | 3.8 | 4.4 |

Buttons of 6 inside the 80% region, same order, at 5 minutes: 0.4, 0.9,
5.0, 5.1, 5.0, 5.2, 5.1.

- **Personalising is the large effect**: from about half a button to 3
  to 4.4 of 6 inside the comfort region.
- **Stopping adds about half a button to one button** over training
  too long (3.4 against 4.4 at 5 minutes); the rule, held-out stopping
  and a short fixed budget are close to each other and to the best.
- **The generic result is exaggerated by the generator.** Each synthetic
  player has a few narrow habitual reach zones in random directions, so
  players differ more than real people probably do, and any one placement
  misses most of them. Real players' comfort zones are likely more alike,
  which would raise the generic rows. Reach detection is assumed solved:
  the game sees the hand's position during pauses at the end of reaches.

Next: a scored run with rules fixed in advance, a generator with more
shared structure between players (a common comfortable region plus
personal variation), and real tracking recordings when available.
