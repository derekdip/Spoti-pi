# NB1 preregistration: bandwidth of model-predictive avatar sync

Written 2026-11-25 after a declared pilot, before any scored run; frozen
by the commit "NB1 freeze", which adds this file,
`poc/results/netpred/bw_run/config.json` and the version of
`poc/netpred/bandwidth.py` that runs and scores it (with
`poc/netpred/synth.py` and `poc/netpred/personalize.py`, frozen since
NP1). Run: `python3 -m poc.netpred.bandwidth run poc/results/netpred/bw_run/config.json poc/results/netpred/bw_run`;
report: `python3 -m poc.netpred.bandwidth score poc/results/netpred/bw_run`.

## The question

The Farey and ECS work say a shared model lets you send only how the
data departs from it. Applied to multiplayer avatars: sender and
receiver run the same predictor of head and hand motion; the sender
transmits a tracker only when the receiver's prediction would be more
than a tolerance away, so the receiver's error is guaranteed below it.
How many bytes does a learned shared predictor save over the simple
receivers games use, and does personalising it or a larger receiver
model save more?

## Design

Synthetic motion (`synth.py`, 90 Hz, head and both hands). Packets: a
4-byte header plus 6 bytes per tracker sent; streaming every frame
costs 1980 B/s. No network delay. Receivers: **hold** (last value),
**deadreck** (velocity from the last two frames), **deadreck_smooth**
(velocity over the last six frames), **generic** (an MLP of width 256
from 24 frames of the receiver's own track to the displacement 1 to 45
frames ahead, trained on 60 players x 3 minutes, seed 21),
**generic_small** (the same at width 64), **personal** (generic plus a
rank-4 LoRA on 2 minutes of the player, stopped by the cross-fitted
rule). 24 players (seed 22), tested on a fresh 3-minute session, at
tolerances 0.5, 1 and 2 cm.

## Pilot (declared, not scored)

`poc/results/netpred/bw_pilot/`: 6 players, without deadreck_smooth
and generic_small. Mean bytes/s at 0.5, 1, 2 cm: hold 1109, 716, 418;
deadreck 1383, 1046, 861; generic 724, 401, 299; personal 731, 402,
299. While adding deadreck_smooth one value was seen before freezing:
454 B/s at 1 cm on a single test session (hold 892 there). The bars
below are as planned before that.

## Bars

- **W1:** generic sends at least 30% fewer bytes than the best of hold,
  deadreck and deadreck_smooth, at every tolerance.
- **W2:** no receiver's error exceeds the tolerance at any frame.
- **W3:** personal sends at least 5% fewer bytes than generic at 1 cm.
- **W4:** generic (width 256) sends fewer bytes than generic_small
  (width 64) at every tolerance.

Each is reported as it stands; no letter grade. The pilot suggests W3
fails and that W1 depends on how good smoothed dead reckoning is.
