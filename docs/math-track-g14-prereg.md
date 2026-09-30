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

V0_TEXT

## Exclusivity table on the new bodies

CHECKS

## The declared pilot

PILOT

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

PREDICTIONS

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
