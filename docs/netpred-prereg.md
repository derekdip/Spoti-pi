# NP1 preregistration: when to stop personalising a VR motion predictor

Written 2026-11-18 after a declared pilot, before any scored fit; frozen
by the commit "NP1 freeze", which adds this file,
`poc/results/netpred/run/config.json`, `poc/netpred/synth.py` and
`poc/netpred/personalize.py`. After it none of them changes. Run:
`python3 -m poc.netpred.personalize run poc/results/netpred/run/config.json poc/results/netpred/run`;
report: `python3 -m poc.netpred.personalize score poc/results/netpred/run`.

## The question

Multiplayer VR hides network delay by predicting where other players'
heads and hands will be. A generic predictor can be personalised on a
few minutes of one player's motion; trained too long it overfits and
predicts worse than the generic one. Does the cross-fitted stopping
rule (docs/prescreen-theory.md, sections 12 to 15) stop it well, with
none of the player's motion held back, and does one calibrated stopping
value, reused for every new player, do as well with no extra fits?

All motion is synthetic (`poc/netpred/synth.py`): head and both hands at
90 Hz, player styles drawn from a population, every session new motion
of the same style. Results here say nothing yet about real players.

## Design

- **Generic predictor:** MLP 216 -> 256 -> 256 -> 9 (267 ms of history
  in, displacement 100 ms ahead out, cm), trained on 60 players x 3
  minutes (seed 2).
- **Players:** 8 calibration and 16 evaluation players, styles from
  seed 77, none used before; each at 1, 2 and 5 minutes of motion, and
  tested on a fresh 2-minute session.
- **Personalisation:** a rank-4 LoRA on all three layers (B zero, no
  scaling), Adam at 1e-3, full batch, losses every 5 steps, to 2000
  steps or until the test gain falls to a quarter of its peak.
- **Arms**, read off the recorded curves: the **rule** (two half-fits on
  the first and second half in time, each watching the other; stop at
  the mean of their training-loss drops at the watched minimum);
  **reuse** (stop when the training loss has fallen by r* of its start,
  r* = the median, over the calibration players at the same data size,
  of the relative training-loss drop at their test peak); **holdout**
  (fit on the first 75% in time, stop at the minimum on the last 25%)
  and **holdout_refit** (the full fit at that step); fixed budgets of
  **100, 300 and 1000 steps**; the **last** step.
- **Measure:** share of the possible gain kept, (generic error - arm
  error) / (generic error - best error along the full fit).

## Pilot (declared, not scored)

`poc/results/netpred/pilot/`: 4 players at 1 and 5 minutes, losses
every 10 steps. Generic error 81% below constant velocity; best
personalisation 5.5% better than generic at 1 minute and 17% at 5. Share
kept, mean (lowest): rule 0.74 (0.28) and 0.87 (0.71); holdout 0.88
(0.64) and 0.85 (0.60); 300 steps -1.90 and 0.75. At 1 minute the best
point comes at step 10 to 60, so every fixed budget ends below the
generic model.

## Bars, at each data size, over the 16 evaluation players

- **N1:** the rule keeps at least two thirds of the possible gain on
  average, and ends above the generic model for at least 90% of players.
- **N2:** the rule keeps on average at least what the best of the three
  fixed budgets keeps, that budget chosen with the test data in hand, per
  data size. A deliberately strong comparison: no one deploying could
  pick it.
- **N3:** reuse keeps on average no less than the rule minus 0.1.

**A**: N1 to N3 hold at every size. **B**: N1 holds everywhere, N2 or N3
fails somewhere. **C**: N1 fails somewhere. Reported with no bar:
holdout, holdout_refit, errors in cm^2, constant velocity.

About 30 to 45 minutes on 4 workers; rows are committed when it ends.
