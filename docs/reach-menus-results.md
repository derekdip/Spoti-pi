# RM1 results: reach-aware menus

Written 2026-11-19 from the frozen scorer's report
(`poc/results/reach/run/report.md`), which is the record.
Preregistration `docs/reach-menus-prereg.md`, frozen at 0fec506. The run
ended at 00:52 UTC with no restart; the diff of the code, config and
preregistration against 0fec506 is empty. Synthetic players (generator v2).

## Outcome, by the frozen bars: B

| bar | 1 minute | 2 minutes | 5 minutes |
|---|---|---|---|
| R1: the rule places at least 0.5 more buttons than the height-scaled default | 3.00 against 1.12: holds | 3.33 against 1.12: holds | 4.17 against 1.12: holds |
| R2: at least training without stopping, and not worse than the default for 90% of players | 3.00 against 2.25, 96%: holds | 3.33 against 2.67, 100%: holds | 4.17 against 3.46, 100%: holds |
| R3: one calibrated value within 0.3 of the rule | 2.83 against 3.00: holds | 3.12 against 3.33: holds | 3.42 against 4.17: **fails** |

Buttons of 6 inside the player's true 50% comfort region, mean over 24
evaluation players (80% region in brackets):

| placement | 1 minute | 2 minutes | 5 minutes |
|---|---|---|---|
| fixed panel | 0.12 (0.42) | 0.12 (0.42) | 0.12 (0.42) |
| height-scaled default | 1.12 (2.29) | 1.12 (2.29) | 1.12 (2.29) |
| personalised, rule | 3.00 (4.42) | 3.33 (4.83) | 4.17 (5.42) |
| personalised, reuse | 2.83 (4.04) | 3.12 (4.71) | 3.42 (4.79) |
| personalised, holdout | 2.67 (4.38) | 3.54 (4.88) | 4.12 (5.29) |
| personalised, 100 steps | 3.29 (4.67) | 3.75 (5.04) | 4.46 (5.54) |
| personalised, 1500 steps (no stop) | 2.25 (3.75) | 2.67 (4.46) | 3.46 (4.75) |
| personalised, best step | 3.12 (4.42) | 3.58 (4.62) | 4.21 (5.33) |

## What it shows

- **Personalising is the large effect**: about 1 button of 6 in the
  comfort region with the height-scaled default, 3 to 4.2 after 1 to 5
  minutes of play. It helps seated players (0.86 to 2.9 to 4.0) and
  limited-reach players (1.83 to 2.9 to 4.2) as much as anyone.
- **Not training too long matters**: training to 1500 steps loses 0.7 to
  0.75 buttons against the rule.
- **But a short fixed budget does as well or slightly better.** 100 steps
  placed 3.29, 3.75 and 4.46, above the rule everywhere, with no bar on
  it. The stopping math is a safe choice here, not a necessary one; what
  matters is stopping early, and on this data 100 steps happens to be
  early enough for every size.
- **Calibrate once falls short at 5 minutes** (3.42 against 4.17): one
  relative drop from 8 players stops the fits too late or too early for
  enough players to lose 0.75 buttons.

## Departures and defects

- None to the frozen files.
- The calibrated relative drop is measured against the magnitude of a
  negative log-likelihood, which has no natural zero; values above 1
  (1.12, 0.94, 1.05) are possible and make r* less portable than in the
  language-model and motion-prediction cases. Named, not changed.
- Synthetic players; reach detection assumed solved.
