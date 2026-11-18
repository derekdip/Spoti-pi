# NP1 results: when to stop personalising a VR motion predictor

Written 2026-11-18 from the frozen scorer's report
(`poc/results/netpred/run/report.md`), which is the record.
Preregistration `docs/netpred-prereg.md`, frozen at 42083b4. The run
started at 22:36 UTC and ended at 23:21 with no restart; the diff of
the code, config and preregistration against 42083b4 is empty. All
motion is synthetic.

## Outcome, by the frozen bars: C

The rule fails N1 at 1 minute of motion and passes every bar at 2 and 5
minutes.

| data | N1: rule keeps 2/3 on average, 90% of players above generic | N2: at least the hindsight-best step budget | N3: reuse within 0.1 of the rule |
|---|---|---|---|
| 1 minute | 0.47, 94%: **fails** | 0.47 against -1.68: holds | 0.61 against 0.47: holds |
| 2 minutes | 0.82, 100%: holds | 0.82 against 0.50: holds | 0.76 against 0.82: holds |
| 5 minutes | 0.90, 100%: holds | 0.90 against 0.88: holds | 0.87 against 0.90: holds |

Error 100 ms ahead, mean over 16 evaluation players (cm^2):

| data | constant velocity | generic | best personalised | rule | reuse | holdout | holdout + refit | 300 steps |
|---|---|---|---|---|---|---|---|---|
| 1 minute | 5.653 | 1.271 | 1.215 | 1.235 | 1.228 | 1.246 | 1.234 | 1.309 |
| 2 minutes | 5.653 | 1.271 | 1.170 | 1.185 | 1.191 | 1.199 | 1.189 | 1.234 |
| 5 minutes | 5.653 | 1.271 | 1.069 | 1.091 | 1.088 | 1.123 | 1.086 | 1.085 |

## What it shows

- **The generic predictor is the large win**: 78% less error than
  constant-velocity extrapolation. Personalising adds 4% at 1 minute,
  8% at 2 and 16% at 5, at best.
- **Personalising is easy to overdo.** At 1 minute every fixed step
  budget ends worse than the generic model for 10 or 11 of 16 players;
  at 2 minutes for 3 of 16.
- **The rule is a safe guard from 2 minutes up**: 82% and 90% of the
  possible gain, no player worse off, and at least as good as holding a
  quarter of the motion back (68% and 71%) and as holding back then
  refitting (80% and 90%).
- **At 1 minute it fails its bar.** Its mean share is 0.47 (median
  0.70); one player whose possible gain was only 0.016 cm^2 ended at
  -3.04, below the generic model, and pulls the mean down. In error it
  still beats the generic model on average (1.235 against 1.271) and
  holding back (1.246). The share is unstable where the possible gain
  is that small, but the bar was set on it before the run.
- **One calibrated value, reused, works as well** (N3 holds at every
  size): measured once on 8 other players, it keeps 61%, 76% and 87%
  with no extra training runs.

## Departures and defects

- None to the frozen files. The generic model's training error (1.80
  cm^2) differs from the pilot's (0.99): a different draw of players.
- The share-of-gain measure is volatile when the possible gain is a few
  hundredths of a cm^2, as for several 1-minute players; an error-based
  bar would have read the 1-minute case differently. Named, not changed.
- Synthetic motion, one predictor size, one learning rate, rank 4.
