# G14 results: outcome C. A removed arm is free, two edits compose to within 1.26 of a fresh fit where the bar was 1.25, and a one-arm legless body has no gait for any clip to reach

Preregistration: `docs/math-track-g14-prereg.md`, frozen at commit
`14bf0b5` (drafts `9ef3e03` and `948bb2f`, labelled, preceded it).
Raw output: `poc/results/g14.json`, `g14.log`, `g14_report.md` (the
frozen scorer's output, `poc/g14_score.py`, unchanged) and one picture
per growth case (`g14_*_checked.png`). Four bodies, three teacher runs
each, six steps, 349 seconds on four workers; the pilot excluded. The
teachers, the compositions and the fresh terminals are in the web
viewer (`poc/results/damaged-gait-player.html`, the group "combined
damages and removed arms").

**One defect after the freeze, named.** The one-arm legless body has
no hip and no left shoulder, and the consumers' fallback cycle clock
looked only for those joints; an edited crawl whose remaining hand
lost its touchdowns raised `StopIteration` inside a worker, which the
pool's iterator read as the end of its results, and two launches of
the scored run ended with no growth case scored. The fallback now
clocks on any present joint (`ed90c68`). No earlier body takes that
path (each has a hip or a left shoulder), the intact V0 replays to
0.3400, and no case had been scored before the fix; the run was
relaunched in full.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K8 composition | composed below the raw clip on `>= 2` of 3 runs, and held-out mean within 1.25 of the fresh growth's, on both combined bodies | below on 3 of 3 on both; **0.524 against 1.25 × 0.416 = 0.520** on the locked knee with the weak hip; 0.556 against 0.706 on the locked knee without an arm | **fail** |
| K9 a removed arm | raw clip within 0.613 on `>= 2` of 3 runs, and no impairment edit applied | 3 of 3 within (0.548, 0.549, 0.489); nothing applied | pass |

Letter **C**. The prediction was B: K8 was predicted to hold narrowly
and missed by 0.004; K9 was predicted to fail on its second clause
and passed. Both predictions were wrong in direction and right about
the margins.

## What each bar means

**Two edits compose, and a fresh fit finds what neither had (K8).**
On the locked left knee with the weak right hip, G13's two single
edits, composed with no fitting, score 0.497, 0.528 and 0.519 against
the three runs, below the raw clip's 0.69 on every run and below
either edit alone (0.51 to 0.53). The fresh growth on the same body
went further, to 0.343 fitting and 0.416 held-out, in five steps:
limp on the left (29 percent; rhythm, worth 31, fell to the guard on
the coupling block), rhythm (6), weak on the left (7), **stiff on the
left (12), the locked knee named on its own side for the first time
on a left-side body**, and lateral (7). The composition captures 62
percent of the fresh fit's held-out gain with nothing fitted; the
remaining 38 percent is the combined teacher's cadence, which no
single-damage edit carried, and the knee itself, which the composed
limp edit leaves bending. The bar asked for the composition within a
quarter of the fresh fit and it landed at 1.26. On the locked knee
without its right arm the carried edit is within 0.98 of the fresh
fit (0.556 against 0.565): where the second damage is a dropped
part, the single edit is the whole answer.

**A removed arm is free (K9).** The intact clip with the arm's joints
dropped is within 0.613 of every run of the one-arm walker, closer
to two of its runs than the body's own cycle is (0.69 and 0.61,
prereg). The growth applied nothing: at the first step every
candidate raised at least one held-out run, the impairment edits
worth a fifth on the fitting run (stiff 25, limp 22, weak 21) raising
both. The pilot on the third run had applied limp; on the first run
the held-out test refused it. The one-arm teacher's runs differ from
each other by more than they differ from the intact walk, and an
edit fitted to one of them is an edit fitted to noise, which the rule
saw and the prediction did not.

**A one-arm legless body has no gait (K10).** The physics moves it at
0.09 to 0.14 m/s with its head on the floor most of the time; the
crawl loop with the arm dropped scores 2.7, 1.9 and 2.1 against its
runs (the crawl's own run-to-run error 0.57), and the growth on the
loop, with torso and arms, brings the held-out mean from 1.97 to 1.19
and no further: rhythm, worth 65 to 71 percent at every step, was
refused by the guard three times for moving the orientation and
reach blocks beyond the runs' distance. The edited loop still crawls
at 0.4 m/s and 0.4 m high over a body the teacher leaves lying at
0.15 m. This is the clip-switch case with nothing to switch to: for
this body there is no motion to bank, and a runtime should show a
body that cannot move rather than a crawl.

**The growth (K11).** Held-out mean below V0's on 3 of 4; the one
miss is the one-arm walker, where nothing was applied.

## What G14 establishes

1. A dropped part is free. The description of a body that has lost
   an arm is the walk clip with the arm's joints dropped, and the
   growth rule, given the chance to add an edit, correctly adds
   none. That is the first control in the 3D arc that the procedure
   left untouched, and it did so on a body whose own runs disagree.
2. Edits compose. Two single-damage edits, composed by rule with
   nothing fitted, take a body with both damages from 0.69 to 0.52
   against runs it never saw, three of three below the raw clip and
   below either edit alone. What they miss is what the combined
   teacher does that neither single teacher did (its cadence) and
   the joint the single edit never clamped. A fresh fit on the
   combined body finds both, and names the locked knee stiff on the
   correct side with the limp already in place.
3. Where no gait exists, no clip reaches it. The one-arm legless
   body is not a clip switch but an absence, and the runtime's honest
   description of it is the teacher's own floundering, not an edited
   crawl.

The margins are the finding as much as the letters: composition is
within a quarter of a fresh fit on one body and within one percent
of the bar on the other; the free arm holds by the held-out test's
refusal of edits worth a fifth on the fitting run. Both are decided
by the teachers' run-to-run spread, which three runs per body cannot
average out, and that is where any further round would have to
start.

No rescue, no second run on the scored cases (the two launches that
scored nothing are described above). Nothing above is edited after
the run.
