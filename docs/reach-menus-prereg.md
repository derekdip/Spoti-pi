# RM1 preregistration: reach-aware menus

Written 2026-11-19 after two declared pilots, before any scored fit.
Frozen by the commit "RM1 freeze", which adds this file,
`poc/results/reach/run/config.json` and the version of
`poc/reach/menus.py` that runs and scores it. After that commit none of
them changes. Run:
`python3 -m poc.reach.menus run poc/results/reach/run/config.json poc/results/reach/run`;
report: `python3 -m poc.reach.menus score poc/results/reach/run`.

## The question

From 1, 2 or 5 minutes of play, can a game learn where a player's hands
comfortably go and place menu buttons there, better than the usual
height-scaled default; does the cross-fitted stopping rule keep the
personal model from overfitting; and does one stopping value,
calibrated once on other players, do as well?

## Players (synthetic, generator v2)

Heights 1.50 to 1.92 m; 30% seated (eyes 0.45 m lower); arm length 0.44
x height x a reach factor of 0.6 to 1.05, independent of height; right
hand making 25 to 90% of reaches. Each hand reaches into four zones every
player shares (in front of the chest, down at desk height, out to the
side, up and forward), each shifted per player (12 degrees in azimuth,
10 in elevation, 8% in distance) and reweighted (Dirichlet, 8 x the
shared weights), plus with probability 0.35 one personal zone. The game
sees hand positions in the body frame during pauses at the end of
reaches (reach detection assumed solved), with hold jitter, 1 mm
tracking noise and 3 degrees of body-frame yaw error.

## Design

Population model: an 8-component Gaussian mixture per hand on 60 players
x 5 minutes, positions scaled by height (seed 51), rescaled to each
player's height. Players: seed 52, 8 calibration and 24 evaluation, each
at 1, 2 and 5 minutes, tested on a fresh 5-minute session. Personal
model: the population mixture fine-tuned by Adam (0.01, full batch) to
1500 steps. Arms read off the recorded fit: **rule** (two half-fits in
time, each watching the other; stop at the mean of their training-loss
drops at the watched minimum), **reuse** (stop at r* times the starting
loss's magnitude, r* the median over the calibration players at that
data size of their best-step relative drop), **holdout** (last quarter
held out), budgets of **100, 300, 1000** steps, **last** (1500),
**oracle** (best step on the fresh session), **fixed** (a panel 0.45 m
ahead, 0.3 m below the eyes) and **generic** (the height-scaled
population model). Score: buttons of 6 (3 per hand, on the model's
highest-density points, at least 12 cm apart) inside the player's true
50% comfort region; the 80% region reported beside it.

## Pilots (declared, not scored)

`poc/results/reach/pilot/` (generator v1, 8 players) and
`poc/results/reach/pilot_v2/` (generator v2, 2 calibration and 4
evaluation players). With v2, buttons in the 50% region at 1, 2 and 5
minutes: generic 0.75 each; rule 3.5, 3.75, 5.0; reuse 2.5, 3.25, 4.25;
holdout 3.5, 3.5, 4.75; last 2.75, 2.75, 3.25.

## Bars, at each data size, over the 24 evaluation players

- **R1:** the rule places on average at least 0.5 more buttons in the
  comfort region than the height-scaled default.
- **R2:** the rule places on average at least as many as training to
  1500 steps without stopping, and no fewer than the default for at
  least 90% of players.
- **R3:** reuse places on average no fewer than the rule minus 0.3.

**A**: R1 to R3 hold at every size. **B**: R1 holds everywhere, R2 or R3
fails somewhere. **C**: R1 fails somewhere. Reported with no bar: the
other arms, the 80% region, and limited-reach, seated and left-leaning
players separately.

About 20 to 30 minutes on 4 workers.
