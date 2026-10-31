# Math Track B5 results: smooth, singular, event decomposition

Preregistration: `docs/math-track-b5-prereg.md` (frozen, unchanged). Raw
outputs: `poc/results/b5.md`, `b5.json`, `b5.png`, `b5.log`. Run 1
completed every sweep and crashed in the scoring on a dictionary-key
format mismatch before writing any file; the fix touched only key
strings (declared in commit `997c94d`, log kept as `b5_run1.log`). Run 2
is the judged run and reproduces run 1 row for row.

## Verdict by the frozen rules: no named outcome; five bars fail

| test | bar | result |
|---|---|---|
| M1 stops localise (R1) | interior-stop enrichment >= 2 on four paths | 0.05, 0.45, 0.05, 0.21: **fail** |
| M2 corners localise (R2) | corner share >= 0.8 on three paths | 0.998, 0.999, 0.999: **pass** |
| R-stop | N(R2) <= 0.5 N(R1) and stop enrichment under R2 < 2 | counts pass on all four (R1 unreachable, R2 62 / 18 / 18 / 18); enrichment 0.01 on corner_stop_corner, 6.8 on the three dwell probes: **fail** |
| R-corner | N(R3) <= 0.9 N(R2), four paths, two primaries | 6 of 8 cells; bend_then_corner at 9.68 mm (51 to 48) and reversal at 9.68 mm (86 to 86) miss: **fail** |
| R-tangent | N(R4) <= N(R3) on four paths and <= 0.9 N(R2) on the control | 4 of 8 cells; control 252 = 252: **fail** |
| H4 | N_corner(tau) flat within 1.5 over 0.8, 0.4, 0.2 s under R2 | 23, 28, 43, ratio 1.87: **fail** |
| H5 | R2 flat within 2 over dwell; R0 grows | R2 exactly flat (18, 18, 18, 18 and 26, 26, 26, 26); R0 unreachable at every dwell including 0: **fail** |
| L | parameter-free law within [0.67, 1.5] on three_corners and reversal | 1.05, 1.46: **pass**; also 1.04, 1.09 and 1.48 on the other three |
| control | no corner detected, R3 = R2 | true; residual enrichment 0.99 |

The outcome rules name three results and this is none of them: M2 holds
so it is not "does not localise"; M1 fails so it is not "localises but
does not repair"; five bars fail so it is not "procedure transfers".
Recorded as a failure by the frozen rules. Three of the five failures
are defects of the frozen definitions, established below with the same
data; two are substantive.

## What the residual said before any repair (M1, M2)

**Corners.** On the three corner-dominated fresh paths, 99.8 to 99.9
percent of the smooth-only residual energy lies in the corner
neighbourhoods, at 2.8 to 4.1 times their share of stalks, which is the
maximum the masks allow. On the mixed path (a bend then a corner) the
corner holds 12 percent and the smooth bend 88 percent at the vertex
count that meets 19.35 mm. On the control the top-quartile turning mask
holds 25 percent of the residual for 25 percent of the stalks
(enrichment 0.99). The localisation is clean, before any repair, and it
does not fire on a difficult smooth path.

**Stops, and the M1 defect.** The frozen stop class excluded stops
within 0.3 s of the walk's start or end, to mean "interior" stops.
Without forced events the largest pass-time defect on every fresh stop
path is the *terminal* standing phase, exactly the degeneracy B2's run 1
found: post hoc (`poc/results/b5_terminal_stop_check.json`), at the
smallest-supremum R1 row, 73 percent of the residual on the dwell probes
sits in the four stalks around the end point (enrichment 73) and 34
percent on corner_stop_corner in five stalks (enrichment 24), while the
interior stop holds under 3 percent. The residual localised at a stop;
the mask was told not to look there. M1 fails by the letter and its
mechanism is confirmed by the same measurement it was meant to make. The
design pilot's stop_start, with three interior stops, had not exposed
this.

## The repairs on fresh paths (R-stop, R-corner, R-tangent)

**Stop events.** Every fresh path with a stop is unreachable at every
threshold without them and reachable with them (62 vertices on
corner_stop_corner; 18 on each dwell probe at 19.35 mm, 26 at 9.68 mm).
The enrichment half of the bar is ill-posed on a straight path whose
only feature is the stop: the straight legs are represented exactly, so
whatever residual remains under the threshold is at the stop by
elimination (41 percent of a small total in 6 percent of the stalks).
On the path with corners the stop's share after repair is 0.1 percent.
The count half of R-stop holds everywhere.

**Corner-class allocation (R3).** Calibrated once on the 90 degree
probe (f = 0.5, the mildest tightening tried), it cuts the count on all
four fresh corner paths at 19.35 mm (14, 24, 22, 29 percent) and on the
two corner-dominated ones at 9.68 mm (17, 21 percent). Its two misses
are both readable off the localisation table. On the bend-then-corner
path at 9.68 mm the residual is 88 percent in the smooth class, so a
corner repair has 12 percent to work on and returns 6 percent; that is
the procedure behaving as it should, and a bar that asked for 10 percent
regardless of where the residual lives was wrong. On the 175 degree
reversal at 9.68 mm the mild tightening does nothing (86 to 86) while
the tangent criterion reaches 67, so the class repair as calibrated on a
90 degree corner is too weak for a reversal at tight tolerance. That one
is substantive.

**Tangent criterion (R4).** The stated prediction, that a class-free
tangent criterion does at least as well everywhere and also repairs the
smooth control, is wrong. R4 loses at 19.35 mm on three of four corner
paths, does nothing on the control (252 = 252 at 19.35 mm; 9.68 mm
unreachable for all three representations), and over-allocates on the
gentle 0.8 s corner (36 against 33). It wins at 9.68 mm on three of four
corner paths (113 against 121, 76 against 105, 67 against 86), on the
reversal at both thresholds, and by a wide margin on the sharpest corner
(20 and 22 against 33 and 33). Its calibration already said this: on the
probe no strength of the criterion beat plain R2, and the loosest was
chosen by the tie rule. The tangent coordinate is the right tool where
turning is concentrated and tolerance is tight, and the wrong one where
turning is spread. The class/coordinate question has a regime answer
here, not a winner, unlike W4.

## Singular mass under sharpening (H4)

| tau (s) | class by rule | R2 | R3 | R4 | cap | law |
|---|---|---|---|---|---|---|
| 0.8 | smooth | 23 | 23 | 26 | 160 | 19.6 |
| 0.4 | corner | 28 | 25 | 28 | 80 | 19.6 |
| 0.2 | corner | 43 | 24 | 31 | 40 | 19.6 |
| 0.1 | corner | 9 | 9 | 18 | 20 | 19.3 |
| 0.05 | corner | 39 | 23 | 10 | 10 | 10.1 |

The frozen bar was written on R2 and fails (ratio 1.87). Under the
class repair the series is 23, 25, 24 across the 0.8, 0.4, 0.2 s range,
flat within 9 percent and flat across the class boundary at 0.52 s, so
the rule's boundary is not a burden boundary. The B2 smooth predictor's
factor-of-two collapse over that range is refuted; the tangent law's
constant 19.6 is within 25 percent of the plateau. R2's 43 at 0.2 s is
the misallocation the class repair exists to fix (a uniform tolerance
tight enough for the apex buys vertices on the ramps), so the bar was
scored on the representation whose defect the track was testing. At
0.1 s the corner resolves with 9 vertices, under its 20-sample cap, as
B4 said sharp corners do under the supremum. At 0.05 s the class
tightening is too mild again (23 for a 10-sample corner) and only the
tangent criterion lands on the cap (10).

## Dwell as an event coordinate (H5)

With stop events the count is identical at every dwell: 18, 18, 18, 18
at 19.35 mm and 26, 26, 26, 26 at 9.68 mm. Nothing outside the event
changes when 0.5, 1 or 2 s of standing is inserted; only `t_leave -
t_enter` does. That is the prediction, exactly. The spatial-only
baseline fails at dwell 0 as well as at every other dwell, and for a
reason that has nothing to do with dwell: a straight walk has no
positional deviation at all, so a position-only compressor keeps two
vertices and cannot represent even the speed ramps. The R0 half of H5
was degenerate as frozen and is void in substance; it fails by the
letter.

## The parameter-free law (L)

`N_hat = N_straight + N_interior_events + turning * peak / (2 eps)`,
with the corner terms capped at their sample counts and no constant
fitted in this track, predicts the fresh counts at 19.35 mm within a
factor 1.5 on all five paths: 1.05, 1.46, 1.04, 1.09 and 1.48 (the
control, expected near 1.8 from the old slalom, came in at 1.48). The
constant 0.4838 m is B4's reference peak bend; the exponent is the
tangent argument's. Two paths were scored and pass; the other three are
reported and would pass the same bar.

## What B5 establishes

1. **The residual names the class before the repair is fitted**, on
   fresh paths, for both classes: corners at 99.9 percent, stops at 73
   percent (the terminal one, which the frozen mask excluded). The
   procedure's first step transfers from water to corn.
2. **The class-specific repairs work where the residual is**: stop
   events make every stop path reachable at a dwell-independent count;
   corner allocation cuts 14 to 29 percent at the perceptual threshold
   on every fresh corner path. Where the residual is not in the class
   (the bend), the class repair correctly does little.
3. **No single coordinate wins.** The tangent criterion beats the class
   allocation for sharp turns and tight tolerance and loses for spread
   turning and loose tolerance. Unlike W4, the corner class does not
   dissolve into one coordinate for this consumer; both are needed and
   the regime decides. My stated prediction was wrong.
4. **Singular mass is stable** under the right representation (23 to 25
   from 0.8 to 0.2 s, across the class boundary) and the smooth
   predictor's collapse does not happen; **dwell is a pure event
   coordinate** (counts identical at every dwell).
5. **A law with no fitted constant** predicts fresh vertex counts within
   a factor 1.5.
6. **Three frozen definitions were wrong** in ways the data itself
   exposes: the interior-only stop mask, the enrichment bar on a
   featureless path, and the spatial baseline on a straight line. They
   are recorded, not repaired, and the verdict stands as a failure by
   the rules.

## On the decision procedure

The chain the track owner asked to test, smooth-only fails, the residual
localises at a defect class, the class predicts the representation, the
representation repairs fresh cases, was observed at each link on corn,
with the third link modified: the class predicts a *set* of candidate
representations (allocation, coordinate), and which one is cheaper
depends on tolerance and on how concentrated the defect is. That is the
same lesson as W3/W4's tangent coherence, seen from the other side: two
representations can own overlapping parts of the residual, and only the
intervention (fresh paths, both thresholds) separates them. A procedure
built on this must score candidates per regime, not pick one per class.

Whether to formalise the procedure now, as proposed, or to first rerun
the three defective bars with corrected definitions on new fresh paths,
is the track owner's call; nothing in this document was rescued.
