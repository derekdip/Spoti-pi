# Math Track B3 results: smooth + singular causal path complexity

Preregistration: `docs/math-track-b3-prereg.md` (frozen). Raw outputs:
`poc/results/b3.md`, `b3.json`, `b3.png`.

## Verdict by the frozen rules: failure, with one half of the model confirmed

B3-H1 fails at the three tighter thresholds: the calibrated law reaches
Spearman 0.94, 0.77 and 0.89 against the six holdout trajectories, but
total turning is above it each time (0.99, 0.93, 0.93). At 5.21 mm the
law passes cleanly (0.94 against turning's 0.64). B3-H2 fails: the
stop/start residual shrinks at every threshold (1.35 to 0.18 at 1.30 mm,
0.76 to 0.09 at 2.61 mm), but the zigzag residual grows at both primary
thresholds (0.37 to 1.13, 0.24 to 0.47). The outcome rule says failure
if H2 fails in either direction.

| test | result |
|---|---|
| H1 at 0.65 / 1.30 / 2.61 mm | 0.94 / 0.77 / 0.89, turning higher each time: fail |
| H1 at 5.21 mm (H3) | 0.94 vs turning 0.64: pass |
| H2 stop/start | residual shrinks at every threshold |
| H2 zigzag | residual grows at both primary thresholds: fail |
| H4 corner bins | excess vertex density in 8 of 8 corner bins |
| H4 clean bins | inconclusive: s_curve 0.76, slalom -0.28, wandering -0.03, others too few bins |

Calibrated constants: `m_par = 0.0133` (along-track acceleration charged
`0.0133^(1/4) = 0.34` times across-track per unit); `A` = 16.7, 8.3, 4.2,
4.2 and `B` = 13.6, 16.6, 5.0, 2.1 at the four thresholds.

## What held

**Anisotropy is real and the tangential weight is small.** Down-weighting
along-track acceleration repaired the stop/start trajectory at every
threshold, and the two-speed probe agrees. The consumer cares roughly
three times less, per unit of `(a^2)^(1/4)`, about where the walker is
along its own track than about where the track lies. That was B2's
second residual, and it is fixed.

**Corners attract vertices beyond the smooth prediction.** Every corner
bin on the zigzag and the wandering reversal shows excess density over
the smooth law scaled to that trajectory. The singular mechanism exists.

**The loose-tolerance regime is now well described.** At 5.21 mm the
calibrated law predicts five of six trajectories within 15 percent and
beats every baseline.

## What failed, and the diagnosis

**The corner term does not transfer from an isolated probe to a
corner-dense path.** The probe needed 27 non-stop vertices for one 90
degree corner at 1.30 mm; six 78 degree corners on the zigzag needed 54
in total, about a third as many per corner. Calibrating `B` on the probe
therefore over-predicts the zigzag two to one. The smooth law itself, with
the across-track constant, predicts about 8 vertices per zigzag corner,
which is what was measured; it is the probe that is anomalous.

**The cause is the error metric, and it is the same for the slalom.**
The theory bounds a *local* error, `E_local <= h^2/8 * L * |p''|`, and
the frozen consumer metric is a *global RMS* over every stalk within 1.5 m
of the whole path. A single corner on an 8 m straight path contributes to
that RMS through about 30 of 470 local stalks, so meeting a global
threshold forces the corner's local error far below it, and the probe
keeps far more vertices than the corner's geometry needs. The zigzag's
corners cover most of its path, so the dilution is much weaker there. The
probe's vertex count is the same at 0.65 and 1.30 mm (31 and 31), a
plateau that shows the count is set by dilution, not by tolerance. The
slalom is the mirror case: it is under-predicted at every threshold (286
against 157, 143 against 80, 67 against 43) because `A` was calibrated on
the 12 m circle, whose constant curvature spreads its error over more
stalks than the slalom's 8 m of dense oscillation, so the circle looks
cheap per unit of `C_smooth`. Both misses have the same sign as dilution
predicts.

**`m_par` is not stably measured.** Its per-threshold estimates span
0.002 to 0.079, a factor of 40. The two-speed probe yields only 6 to 10
non-stop vertices, so the estimate is quantised, and the probe carries an
accidental momentary stop where its two ramps meet at zero speed (a
design flaw, frozen and therefore reported, not fixed). The geometric
mean 0.0133 is the frozen value, and it worked on stop/start, but the
instrument is too weak to claim a digit.

## What this means for the branch

The smooth anisotropic term survives; the singular term's *form* is
plausible (corner bins show the excess) but its *calibration* cannot be
done with an isolated probe under a global RMS metric. The theory and the
experiment were measuring different things: the derivation is local, the
score was global. That is the third time in this track that a mismatch
between the object the math bounds and the object the experiment scores
produced a failure (state RMS versus consumer error in the first review,
pass-time conditioning at stops in B2, dilution here).

B4, if run, should change exactly one thing and preregister it: score the
consumer by the local supremum (max over stalks within 1.5 m and frames
of `|G[p] - G[p-hat]|`), which is the quantity the derivation bounds and
which does not dilute with path length. B2 recorded that supremum as a
secondary quantity; B3 did not store it, so a rerun is needed. Two
smaller amendments: a tangential probe with several ramps and no
accidental stop so `m_par` rests on more than ten vertices, and an
`A_eps` check against the predicted `eps^(-1/2)` scaling, which the
present `A` values (ratios 2.0, 2.0, 1.0 across the thresholds) do not
follow because `N(eps)` plateaus at loose tolerance.

Under the frozen rules this branch is a failure at tight tolerance, twice
now. The loose-tolerance regime is solved, the anisotropy is solved, and
the remaining open question is narrow: whether the singular term
calibrates and transfers once the metric matches the theory.
