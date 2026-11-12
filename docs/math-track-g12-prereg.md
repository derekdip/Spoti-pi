> **Draft, not run.** Written after G11, abandoned before V0 was
> frozen: the V0 refit under this support rule lunged (feet 0.71 m
> apart on average against the teacher's 0.22,
> `poc/results/gait3d_v0_support_s0.json`, `_s1.json`), and the
> parametric fit was set aside for the cycle runtime
> (`docs/gait3d-runtime.md`, last section). The placeholders below
> (V0_TEXT, CHECKS, PILOT, the predictions) were never filled. The
> support rule is in `grammar3d.Ground.step` as an option, off by
> default, so the G9 to G11 states replay as scored;
> `poc/g12_experiment.py` and `poc/g12_score.py` are the draft's
> code, written when the rule was the default and not setting the
> option; `poc/results/g12_pilot.json` and
> `gait3d_dictionary_check_g12.*`, `gait3d_redundancy_check_g12.*`
> its partial pilot and checks. Kept as a record.

# G12: the support foot from the grammar's own clock. Preregistration (frozen before any scored case is run)

The web viewer of the G11 states showed bodies whose steps did not
move them forward much. Measured, the fitted intact state advanced at
the teacher's rate (1.47 m in four seconds against 1.66) with its feet
0.43 m apart on average against the teacher's 0.22: long strides,
short progress, a treadmill. The mechanism is in the grounding. Since
G9 the planted part was whichever part was lowest, whatever the
grammar's clock said; a foot in the grammar's early swing that was
still the lowest moved forward under the body, and planting it pushed
the body back. The fit paid for the lost progress with strides twice
the teacher's. Replayed with the support chosen by the clock, the
same G11 state advances 2.25 m in four seconds.

## The change

`poc/gait3d/grammar3d.py`, `Ground.step`: the support part is the
foot the grammar's clock has in stance (the warped phase in the
stance half, with the limp and weak terms) when that foot is on the
floor; when no such foot is down, the lowest part as before (the
stumps' thighs, the legless body's hands, a hop's flight). The
runtime player (`poc/gait3d/runtime.py`) uses the same rule. Nothing
else changes: G11's teacher, grammar, fourteen consumer blocks, rules,
cases, designed classes and pilot.

This is a grounding change, so V0 is refitted, the redundancy screen
and the exclusivity table are rerun, and the run is G11's procedure.

## V0

V0_TEXT

## Redundancy screen and exclusivity table

CHECKS

## The declared pilot

PILOT

## Bars (frozen)

As G11's (`poc/g12_score.py`, committed with this document, comparing
with `poc/results/g11.json`).

- **K1, identity.** First impairment repair names class and side on
  `>= 2` of 3 design bodies, within two on 3 of 3, mirrors 2 of 2.
- **K4, growth generalises.** Mean held-out error below V0's on `>= 7`
  of 9 damaged bodies.
- **K2, consumers.** None beyond tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.
- **K5, K6, reported.** Ground speed near the floor; foot travel.
- **K7, reported, the round's claim.** Mean forward separation of the
  feet and body speed at the terminal against the teacher's, per
  case. The claim: on the walking bodies the separation lands within
  a factor of 1.5 of the teacher's with the speed within 0.1 m/s,
  where G11's intact state was at twice the separation.

## Predictions

PREDICTIONS

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails.
- **D**: neither.

K2, K3, K5, K6 and K7 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
teacher, the grammar, the consumers, the rules or the budget after
this commit. Results go in `docs/math-track-g12-results.md`; nothing
above is edited after the run.
