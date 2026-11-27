# Exact frame and tick scheduling from Christoffel words

**Model.** Display at F Hz, with vsync counter s; simulation at T Hz.
- Ticks completed by vsync s: n(s) = floor(s T / F).
- Ticks to run this frame: n(s1) - n(s0), which also handles dropped frames.
- Interpolation factor: alpha = (s T mod F)/F, exactly.

The per-frame tick counts form the Christoffel word of slope T/F (`poc/christoffel`). Every window of w frames holds
floor or ceil of (w T/F) ticks. The schedule depends only on the integer vsync counter, so it cannot drift, does not
depend on timing noise, needs no accumulator state, and can be evaluated at any frame directly (replay seek, rollback,
network resync). `schedule.py` provides the schedule, amortised spreading, and continued-fraction tools; the Unity
mirror is `unity/TickSchedule.cs` (uncompiled).

## (2) One hour at 72 Hz, physics 50 Hz, 1% dropped frames, 0.15 ms timestamp noise (`experiment.py`)

| strategy | irregular frames | drift (ticks) | position error, rms (1 unit/s) | same ticks under different timing noise | frames differing from exact |
|---|---|---|---|---|---|
| float32 accumulator, measured dt | 0 | 0 | 1.6e-4 | no | 5728 (5724 at coincidence frames) |
| float64 accumulator, measured dt | 0 | 0 | 1.5e-4 | no | 7258 (7256 at coincidence frames) |
| float32 accumulator, nominal dt | 0 | 0 | 2.9e-5 | yes | 14 418 (all at coincidence frames) |
| float32, dt snapped to vsync multiples | 0 | 0 | 2.9e-5 | yes | 14 418 (all at coincidence frames) |
| float64, dt snapped | 0 | 0 | 2e-13 | yes | 14 418 (all at coincidence frames) |
| **exact (vsync counter)** | 0 | 0 | 2e-13 | yes | 0 |

A coincidence frame is one where a tick falls exactly on a vsync, i.e. s T/F is an integer.

**Reading.**
- With timestamps taken from a monotonic clock, so that noise telescopes, ordinary accumulators neither drift nor
  produce irregular frames.
- The visible error is about 0.15 ms-equivalent, which is negligible. Exactness does not fix anything you would see.
- Exactness gives:
  - a tick sequence independent of timing noise, which measured-dt accumulators lack;
  - exact handling of coincidence frames, where snapped float accumulators consistently defer the tick by one frame;
  - stateless O(1) evaluation of any frame.
- The value is for deterministic replay, rollback, lockstep, and simpler code, not for image quality.
- An earlier run of this experiment put noise on each dt instead of on the timestamps, which wrongly produced a 70 ms
  random-walk drift. It was corrected before these numbers.

## (3) Amortised updates (`ratios.py`)

Updating N objects once per M frames with the round-robin range [floor(f N/M), floor((f+1) N/M)) mod N:
- The load per frame is floor or ceil of N/M (13-14 for N = 1000, M = 72), against 6-14 for naive ceil-sized chunks.
- Every object's staleness is exactly M frames.

## (4) Tick rate for Quest display rates (`ratios.py`, `ratios.log`)

Without interpolation, the per-frame motion is ticks/T. Its coefficient of variation is the visible judder.

| display | tick 50 | tick 60 | tick 72 | tick 90 | tick 120 | zero-judder tick rates |
|---|---|---|---|---|---|---|
| 72 | 0.66 (`011`, period 36) | 0.45 | **0** | 0.35 | 0.28 | 72, 144, 360, 720 |
| 80 | 0.78 | 0.58 | 0.33 | 0.29 | 0.33 | 720 |
| 90 | 0.89 | 0.71 | 0.50 | **0** | 0.35 | 90, 360, 720 |
| 120 | 1.18 | 1.00 | 0.82 | 0.58 | **0** | 120, 360, 720 |

The worst-case age of the newest state at display time is up to 19 ms for 50 Hz on 72 Hz.

**Recommendations.**
- With interpolation, any tick rate works.
- Without interpolation, which suits cheap kernels evaluated per frame like this repo's, use a multiple of the display
  rate. 720 Hz is the smallest single rate that is judder-free on all of 72/80/90/120 Hz.
- For stateless closed-form kernels, evaluating at the exact display time s/F avoids ticks altogether.

**Near-rational ratios.** The continued fraction gives the hiccup structure:
- 59.94 Hz content on 60 Hz = [0; 1, 1000]: one empty frame every 1001 frames (16.7 s).
- 59.94 Hz video on 72 Hz = [0; 1, 4, 1, 32, 2]: runs of 4-5 with a 400-frame (5.6 s) super-period.

**Limits.**
- The noise and drop models are simple.
- On a headset, the compositor's timewarp and frame pacing interact with these patterns. That has not been measured.
- `unity/TickSchedule.cs` has not been compiled.
