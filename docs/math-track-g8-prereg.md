# G8: impairments on top of a full base refit. Preregistration (frozen before any scored case is run)

G7 (`docs/math-track-g7-results.md`) carried the 2D growth rule to the
3D body and left one open item: on the right stump a lateral refit,
taken first because it had the largest drop, reached the stump-side
asymmetry, and limp, worth 27 percent at V0 on the correct side, was
under a percent from then on. Whether a sided class is named depended
on which base class refitted first. G8 changes the order and nothing
else: the base does everything it can first, and an impairment class
is then named for what the refitted base cannot do.

## The procedure

`poc/g8_experiment.py`, G7's script with the candidate set changed by
phase; the rules (spent at one percent, the held-out mean must fall,
no consumer beyond its tolerance), the fits, the teachers, V0, the
grammar as frozen for G7, and the designed classes are G7's.

- **Phase 1, base.** Only the five base classes are candidates, taken
  greedily as before, until none passes or six steps are spent.
- **Phase 2, naming.** From that state, only the impairment classes
  are candidates, for one step. The first impairment repair of the
  case is this step's pick, if any passes; if none does, the case has
  no impairment repair at that point.
- **Phase 3, rest.** Every class competes for the remaining budget, as
  in G7. Eight steps in all, so at least one step follows the naming
  step.

Identity counts impairment repairs only, with the side sign, as
before. Fourteen cases as G7; the same pilot.

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, four steps
(`poc/results/g8_pilot.*`): arms in the base phase, then the base
declined, the naming step declined (vault spent), the rest declined;
fitting 0.761 to 0.697, as G7's pilot. Excluded from every bar. No
change was made after it.

## Bars (frozen)

As G7's, on the thirteen scored cases (`poc/g8_score.py`, committed
with this document, comparing with `poc/results/g7.json`).

- **K1, identity.** First impairment repair names class and side on
  `>= 2` of 3 design bodies, within two on 3 of 3, mirrors 2 of 2.
- **K4, growth generalises.** Mean held-out error below V0's on `>= 7`
  of 9 damaged bodies.
- **K2, consumers.** None beyond tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.

Reported: the naming step of every case with a designed class (every
impairment's drop after the base phase, what was rejected and why),
terminal fitting and held-out errors against G7's on every case,
repairs per case, rejections by reason.

## Predictions

K4, K2, K3 hold as in G7. K1 is the question, and the prediction is
that it **fails as in G7**: after the full base refit the right
stump's limp is predicted under one percent (it was under one after
the lateral refit alone), and the legless body's vault under one (it
was 0.3 percent after arms and torso). Design 2 of 3, mirrors 1 of 2,
letter C. If K1 holds instead, the order of the base refits was what
lost the right stump in G7 and the two-phase order is the rule; if it
fails as predicted, the consumers do not support naming those two
bodies by a class, with the base given every chance first, and that
closes the item on the record rather than in the procedure.

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold. The two-phase order names what G7 could not.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails. The order was not the cause. The
  predicted letter.
- **D**: neither.

K2 and K3 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
procedure, the grammar, the rules or the budget after this commit.
Results go in `docs/math-track-g8-results.md`; nothing above is
edited after the run.
