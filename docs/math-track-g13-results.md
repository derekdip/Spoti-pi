# G13 results: outcome C. The growth rule generalises on the clip base, the classes name a limp where the body has a stiff leg, and a hop, a kneel-step and a crawl stay out of the edits' reach

Preregistration: `docs/math-track-g13-prereg.md`, frozen at commit
`dff9b98` (a draft labelled as such, `64a7485`, preceded it; the
pre-build checks that shaped the edit operator are declared in the
document). Raw output: `poc/results/g13.json`, `g13.log`,
`g13_report.md` (the frozen scorer's output, `poc/g13_score.py`,
unchanged) and one picture per case (`g13_*_checked.png`). Fourteen
cases, six steps, 732 seconds on three workers; the declared pilot
excluded from every bar. The terminal edited clips are in the web
viewer (`poc/results/damaged-gait-player.html`, the group "the intact
teacher's cycle with the edits fitted to each body").

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **0 of 3, 0 of 3, 1 of 2** | **fail** |
| K4 growth generalises | held-out mean below V0's on `>= 7` of 9 | **8 of 9** (both runs lower on 7) | pass |
| K2 consumers | none beyond tolerance on `>= 7` of 9 | **9 of 9** | pass |
| K3 controls | `<= 4` impairment repairs on four controls | **3** | pass |

Letter **C**, as predicted. K3 was predicted to fail and passed; K1
was predicted at 0 of 2 on the mirrors and one mirror named its
damage. K5, K6 and K7 reported below.

## What each bar means

**Growth generalises on a clip base (K4, K2, K3).** Eight damaged
bodies of nine end with a lower mean held-out error than the raw
clip, seven on both runs; every terminal is within tolerance on
every consumer; the controls took three impairment edits. The one
K4 miss is the right short shank, where every candidate at V0 raised
one of the two held-out runs and nothing was applied: its two runs
differ by more (0.615 and 0.523 from the clip) than any edit moves
them together. The controls stayed clean for a reason the
exclusivity table gave and the prediction misread: on the intact
body's first run the weak edit, worth 26 percent, was rejected by
the guard (stance asymmetry beyond the runs' distance) and the legs
edit took the drop; after it every impairment edit was worth under
1 percent and was spent. Base and impairment edits overlap on the
clip as on the grammar, and whichever is applied first leaves the
other nothing. The held-out test rejected 62 candidates, the spent
rule 89, the guard 6.

**The classes do not name the damage as edits of this clip (K1).**
The left locked knee named limp on the left at the first step, worth
28 percent against stiff's 3.8, and then nothing: the edited clip's
left knee still bends 0.73 rad (the teacher's 0.15) and its right
knee was lifted and sunk instead. The left stump named rhythm, then
vault; the legless body torso; the right stump lateral, then rhythm.
The right locked knee, a mirror, named stiff on its own side first,
worth 31 percent, then legs, then stiff again, and its terminal
right knee does not bend at all (range 0.00 against the teacher's
0.15) with the hip swinging a third as far as the teacher's. The
same damage on the two sides of the same body names differently,
and the difference is the base clip's: the intact teacher's own walk
swings its right hip 0.90 rad and its left 0.63, so a clamped right
knee reads as the damage and a clamped left knee reads as a limp.
On a clip base the identity of a damage depends on the clip's own
asymmetry, which the grammar's symmetric walk base never had.

**Reach (K7).** The walking bodies: the left locked knee, the left
short shank and the right locked knee lowered both held-out runs
(0.671 to 0.555, 0.680 to 0.521, 0.630 to 0.480), through limp, weak
on the long side, and stiff; the right short shank kept the raw clip.
Against the parametric fit's terminal on the same held-out runs
(G11), the edited clip is lower on the left short shank and the
right locked knee and higher on the other two, and lower on seven
cases of thirteen overall, from a handful of edits on a base that
plays right against 44 fitted parameters. Speeds are within 0.1 m/s
of the teachers' on three of four, the right short shank at the
clip's 0.40 against 0.29.

The gait-switch bodies: the left stump's held-out error fell from
0.797 to 0.553 with rhythm and vault, but its terminal stands at a
pelvis height of 1.17 m against the teacher's 0.85 and is off the
floor 39 percent of the time against 3: the vault edit lifts the
body on its one foot, and no edit lowers it. The legless body took
one torso edit, which pitched it prone, and stays at 1.000 held-out:
it lies prone at the walk's pelvis height, 1.15 m above the floor
against the teacher's 0.46, touching nothing on any frame. The one-leg
bodies read 0.580 and 0.414, below the parametric fit's, as
one-legged walks gliding on the remaining foot at the teacher's
speed. The mechanism, named: the runtime's floor rule only raises a
body whose lowest part would go below the floor, and the edited clip
carries the intact walk's root height; a body that has lost the
parts the clip stands on keeps that height, and the crouch of the
kneel-step and the crawl are not edits of a walk. This is a limit of
the operator on such bodies, stated here and not repaired, and it is
the clip-switch case the preregistration expected for the stump, the
hop and the crawl, reached for the stump and the crawl by the
height alone before any gait question arises.

**Reported (K5, K6).** The planted part's ground speed at the
terminals is 0.28 to 0.87 m/s against the teachers' 0.17 to 0.31: the
cycle runtime does not plant, and the edited clips slide on the
stance foot as the teacher's own mean cycle does (the stride ratio
sets the progress, not the foot). The foot-travel block improves on
eleven cases of thirteen.

## What G13 establishes

1. The growth rule carries to a clip base. With the grammar's classes
   as edits of the teacher's own cycle, held-out acceptance
   generalises on eight damaged bodies of nine, the guard holds on
   nine of nine and the controls stay clean. The edit operator is a
   representation RGRE can grow.
2. Identity is the base's, not the class's. On the grammar's
   symmetric walk base the stiff class named a locked knee; on the
   asymmetric clip it named the right one and called the left one a
   limp. A class names a damage only relative to a base that has
   none of it, and a clip of a real walk always has some.
3. The taxonomy holds where the preregistration put it, for a
   plainer reason than the gait: a limp, a weak hip and a stiff leg
   are dials on the walk clip within the teacher's own run-to-run
   noise; a kneel-step, a hop and a crawl are clips of their own,
   because the walk clip carries its height and its stance parts
   and the edits cannot give them up.
4. Against the parametric fit on the same teachers the edited clip
   is as good or better on the held-out runs in seven cases of
   thirteen, from a base that plays right. Whether the edited
   walkers read right is in the viewer: the left locked knee walks
   with a limp and a bending knee, the right with a straight leg.

No rescue, no second run on the scored cases. Nothing above is
edited after the run.
