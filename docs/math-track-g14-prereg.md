# G14: composition of edits, a removed arm, and a one-arm crawl. Preregistration (frozen before any scored case is run)

G13 (`docs/math-track-g13-results.md`) showed the grammar's classes
carry as edits of the intact teacher's own cycle: the growth rule
generalises on them, a limp, a weak hip and a stiff leg are dials on
the walk clip, and the kneel-step, the hop and the crawl are clips of
their own. The reason to have edits at all is that damages combine
without a teacher run each, and nothing has tested that. This round
does, with three questions and one design change.

1. **Composition.** Do two edits fitted separately, composed with no
   fitting, describe a body with both damages?
2. **A removed arm.** Is a dropped part free, that is, does the intact
   clip with the arm's joints dropped describe the one-arm walker
   within the teacher's own run-to-run noise, with nothing to fit?
3. **A one-arm crawl.** On the legless body the arms are the legs;
   is a one-arm crawl an edit of the crawl loop or a clip of its own?

## The bodies

`poc/gait3d/biped3d.py` gains combined morphs (damages joined by
`+`) and removed arms (`noarm_*`); the twelve existing bodies build
to byte-identical XML (checked before the freeze; the stump's legs
keep their order so that its stored teacher runs read as before).
Four new bodies, three teacher runs each under the iteration-7
planner unchanged (`poc/gait3d/teacher.py combined`):
`noarm_left`; `locked_knee_left+weak_hip_right`;
`locked_knee_left+noarm_right`; `nolegs+noarm_left`. The consumers
gain nothing; the reach block reads the hands the body has (every
earlier body had both, so no earlier number changes: the intact V0
error and the right stump's replay to G11's values).

## The design change, declared

`poc/gait3d/cycle_runtime.py`: a profile carries its clearance per
bin, the height of its own body's lowest part above the floor, and
the player puts the current body's lowest part at that clearance.
On the body the clip came from this is the rule it replaces (the
root at its recorded height unless a part would go below the floor):
the two agree to 0.007 m on the intact clip and 0.017 m on the short
shank's, the difference of interpolating between bins, and exactly on
the hop and the crawl. On a body that has lost the parts the clip
stood on, the body comes down to the floor: the G13 legless terminal,
which floated at 1.15 m, plays at 0.36 m (the teacher 0.46) with its
hands down, and its error falls from 0.802 to 0.769. The G13 stump
terminal does not change (its foot was on the floor; its 1.17 m
against the teacher's 0.85 is the crouch, not the grounding). G13's
scored trajectories replay unchanged under the old rule, which
`clip_edit` keeps as its default; this round runs under the new one.

## The procedure

`poc/g14_experiment.py`, two parts.

**The growth**, G13's procedure unchanged (the grammar's classes as
edits, held-out acceptance on the mean of two runs, the per-consumer
guard, the spent rule at 1 percent, six steps), fit on seed 0 with
seeds 1 and 2 held out, on each new body: the intact clip as base
for the three bodies with legs, the legless body's own loop for the
one-arm crawl (the operator's stepping parts are the hands there,
the leg operators have no joints to act on, the arm and root
operators act). Clearance grounding throughout.

**The compositions**, which fit nothing (`clip_edit.compose`: a
ratio parameter multiplies its ratios to R, any other adds its
differences from R, a sided class comes from whichever edit has it
on). On `locked_knee_left+weak_hip_right`: G13's terminal edit for
the left locked knee (limp on the left) and G13's for the right weak
hip (weak on the left, roll), composed; beside it the raw clip and
each edit alone. On `locked_knee_left+noarm_right`: G13's left
locked-knee edit with the arm's joints dropped; beside it the raw
clip. On `noarm_left`: the raw clip with the arm dropped. On
`nolegs+noarm_left`: the raw crawl loop with the arm dropped. Each
is scored against all three runs of the body's teacher. G13's edits
were fitted under the old grounding; on the walking bodies the two
groundings differ by 0.014 in error (the left locked knee, 0.420
against 0.434), which is declared and not corrected.

## V0 on the new bodies

The teachers first (`poc/results/gait3d_teacher_combined.log`). The
one-arm walker walks at 0.41, 0.33 and 0.38 m/s (the intact teacher
0.42), its first run with an uneven stance (the left foot down 25
percent of the time, the right 78) and the other two even. The locked
knee with a weak hip on the other side walks at 0.23, 0.45 and 0.28,
three runs a factor of two apart. The locked knee without its right
arm walks at 0.41, 0.19 and 0.46. The legless body with one arm does
not crawl: 0.09, 0.14 and 0.09 m/s with its head on the floor 80 to
90 percent of the time and its pelvis 75; the physics has no gait for
it, and the third question is answered by the teacher before any
edit is tried.

The raw base clip with the missing parts dropped, against each run:
the intact clip on the one-arm walker 0.548, 0.549, 0.489; on the
locked knee with the weak hip 0.686, 0.672, 0.691; on the locked knee
without an arm 0.518, 0.756, 0.558; the crawl loop on the one-arm
legless body 2.667, 1.852, 2.080 (the loop crawls at 0.42 m/s and
0.40 m high where the teacher lies at 0.15 m and moves at 0.1).

Each body's own clip (its mean cycle or loop from run 0) against its
runs 1 and 2: 0.691 and 0.614 (one-arm walker), 0.604 and 0.582
(locked knee with weak hip), 0.821 and 0.714 (locked knee without an
arm), 0.632 and 0.418 (one-arm legless). On two of the three walking
bodies the raw intact clip is closer to the held-out runs than the
body's own cycle is: the runs of these teachers differ by more than
their damage, as in G13, and K9's first clause is met by the raw
clip's numbers above (all three within 0.613) before the round runs;
its open clause is whether the growth finds an impairment edit the
held-out test accepts. On the combined bodies the raw clip's largest
blocks are rhythm (1.47 on the locked knee with the weak hip, whose
cadence and speed are not in either single edit), speed (0.76),
stance (0.90) and joint asymmetry (0.85).

## Exclusivity table on the new bodies

`poc/results/gait3d_dictionary_check_g14.*`, the G13 operator on the
three bodies with legs at V0 (the one-arm legless body has only the
arm and root operators and is not tabled). The value of each class's
fitted edit as a share of the error, with the side:

- One-arm walker: lateral 30 percent (the oracle), **stiff 25 on the
  right, limp 22 on the right, weak 21 on the right, hold 19**, vault
  20, torso 16, legs 15, rhythm 13, arms 0. Impairment edits worth a
  fifth to a quarter on a body with two sound legs: its first run
  walks unevenly (V0 above), and an uneven run of a sound body reads
  as a leg damage to every class that makes one.
- Locked left knee with a weak right hip: rhythm 31 (the oracle),
  limp 29 on the left, weak 28 on the left, torso 16, hold 21 on the
  left, lateral 21, vault 19, legs 14, **stiff 2.8 on the right**.
  Neither single edit carries a rhythm change, and the combined
  teacher's cadence is the largest thing the raw clip misses.
- Locked left knee without its right arm: lateral 13.5 (the oracle),
  limp 13 on the left, weak 13 on the right, rhythm 12, torso 10,
  hold 4, **stiff 4 on the left**, legs 3, arms 1, vault 0.

Absorption: on the combined body, of stiff's effect weak absorbs
0.83, limp 0.77 and hold 0.75; of weak's, limp 0.61 and legs 0.57; on
the one-arm walker, of hold's effect limp absorbs 0.76 and stiff
0.74; on the locked knee without an arm, of hold's effect weak
absorbs 0.65. As in G13, stiff is worth little and the limp-like
classes stand in for each other.

## The declared pilot

The one-arm walker, teacher seed 2, seeds 0 and 1 held out, two steps
(`poc/results/g14_pilot.*`): at the first step the two largest edits,
lateral (18 percent) and torso (16), were rejected by the guard for
moving the speed beyond the runs' distance, and **limp on the left**
(13.5 percent) was applied, lowering both held-out runs; fitting 0.489
to 0.422, held-out mean 0.549 to 0.499; at the second step every
candidate was under 1 percent. Excluded from every bar. No change was
made after it. What it shows is written into the predictions: the
growth names a leg damage on a body whose legs are sound, because the
teacher's runs of that body are uneven.

## Bars (frozen)

`poc/g14_score.py`, committed with this document.

- **K8, composition.** On both combined bodies, the composed edit's
  error is below the raw clip's on `>= 2` of 3 runs, and its mean on
  the held-out runs (1 and 2) is within 1.25 of the fresh growth's
  held-out terminal on the same runs.
- **K9, a removed arm.** The raw intact clip with the arm dropped
  scores within 1.2 of the intact clip's own run-to-run error (0.511,
  G13 prereg) on `>= 2` of 3 runs of the one-arm teacher, and the
  growth on that body applies no impairment edit.
- **K10, reported.** The crawl loop with the arm dropped against the
  one-arm crawl's runs, beside the crawl's own run-to-run error
  (0.568), and the growth's terminal on the loop.
- **K11, reported.** The growth on each body: held-out error per run,
  the edits, speed and airborne fraction against the teacher.

## Predictions

- **K9 fails on its second clause.** Its first clause is met by the
  V0 numbers (the intact clip with the arm dropped is within 0.613 of
  every one-arm run): a removed arm changes the consumers less than
  the teacher's own run-to-run variation. Its second clause is
  predicted to fail: the pilot applied limp on the one-arm walker's
  third run, and on the first run stiff, limp, weak and hold are each
  worth a fifth or more with the lateral base edit's speed change
  likely to fall to the guard as it did in the pilot. The dropped arm
  is free; the teacher's uneven run of the one-arm body is not, and
  the growth names it a leg damage.
- **K8 holds, narrowly.** On the locked knee without its right arm,
  the carried G13 limp edit is worth about what any single edit is
  worth there (13 percent), and the fresh growth starts from the
  same raw clip: within 1.25 and below the raw clip on at least two
  runs. On the locked knee with the weak hip, the composed edit
  (limp on the left with weak on the left, G13's two terminals) is
  predicted below the raw clip on all three runs, and its held-out
  mean within 1.25 of the fresh growth's because the fresh growth's
  largest candidate, rhythm, fits the first run's slow cadence (0.23
  m/s) and the two held-out runs disagree on it (0.45 and 0.28), so
  the held-out test is predicted to reject or halve it. If the fresh
  growth does take rhythm and keep it, the composition loses this
  clause: that is the risk, stated. Letter **B**.
- **K10.** The crawl loop with the arm dropped stays far above the
  crawl's own run-to-run error on every run (2 to 2.7 against 0.57),
  and the growth on the loop, with torso, arms, rhythm and vault to
  edit, ends above 1.5 on every run: the one-arm legless body has no
  gait in the physics, lying at 0.15 m and moving at 0.1 m/s, and no
  edit of a crawl at 0.42 m/s and 0.40 m reaches a body that does
  not crawl.
- **K11.** Held-out mean below V0's on `>= 3` of 4 bodies, the crawl
  included (its raw error is far enough off that any torso edit
  lowers both runs).

## Outcome (frozen, exclusive)

Determined by K8 and K9.

- **A**: both hold.
- **B**: K8 holds, K9 fails.
- **C**: K9 holds, K8 fails.
- **D**: neither.

K10 and K11 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
teacher, the bodies, the clips, the operator, the composition, the
consumers, the rules or the budget after this commit. Results go in
`docs/math-track-g14-results.md`; nothing above is edited after the
run.
