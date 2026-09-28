# G3: growth that a teacher's noise cannot pass, and a per-consumer guard. Preregistration (frozen before any scored case is run)

G2 (`docs/math-track-g2-results.md`) named the damage on four design
bodies of four and left two problems on record: six terminals of ten
were worse than V0 on some consumer, and the controls grew impairment
classes on their teacher's run-to-run variability. A zero-tolerance
guard declined every repair at step zero. G3 adds two rules to G2's
oracle path, both measured from a second run of the same teacher
rather than chosen, and keeps everything else: the same grammar, the
same consumers, the same V0, the same fourteen fitting teachers.

## The two rules

Every case now has a held-out run: the same body, the teacher's seed
advanced by one, produced by `poc/gait/teacher.py heldout` for the ten
bodies that did not have one (the intact and legless bodies already
had two runs, which serve as each other's held-out).

**Held-out acceptance.** A repair fitted on the fitting run is applied
only if it also lowers the error against the held-out run. A class
that fits one run's noise does not lower the other run's error; a
class that names the damage does. No constant.

**Per-consumer guard.** A repair may not worsen any consumer, against
the fitting run, by more than that consumer's tolerance: the distance
between the two runs of this body on that consumer at V0's scale.
Measured per body and per consumer, not chosen. On the intact body it
is 0.03 on height, 0.04 on speed and 0.65 on the mean cycle, which is
the pattern a guard should have: strict where the teacher is
consistent, loose where it is not.

At each step every repairable class is fitted on the fitting run,
candidates are taken in order of fitting drop, the first that passes
the spent rule, the held-out test and the guard is applied, and the
step is declined when none passes, which ends growth. Six steps.
`poc/g3_experiment.py`, scorer `poc/g3_score.py`, both committed with
this document. Identity counts impairment repairs only, with the side
sign, as in G2.

## The declared pilot

The legless body, teacher seed 1 with seed 0 held out, three steps
(`poc/results/g3_pilot.*`), excluded from every bar: vault, torso,
rhythm, each lowering both errors, nothing rejected. Fitting error
0.724 to 0.307, held-out 0.728 to 0.359.

## Bars (frozen)

Scored against G2's oracle path on the same teachers
(`poc/results/g2.json`), which is the same procedure without the two
rules.

- **K1, identity is kept.** On the checked path, G2's three identity
  bars: the first impairment repair names the class and side on
  `>= 3` of the four design bodies, within two on `>= 3` of four, and
  within two on `>= 2` of the three mirrors.
- **K2, consumers.** At the checked terminal, against V0 on the
  fitting run, no consumer is worse on `>= 6` of the ten damaged
  bodies (G2 had four), and none is worse beyond its tolerance on
  `>= 8` of ten.
- **K3, controls.** Impairment classes are added on at most one of the
  four control cases (the two intact runs and the two weak-hip
  bodies). G2 added them on all four.
- **K4, growth generalises.** The terminal state's error against the
  held-out run is below V0's held-out error on `>= 8` of the ten
  damaged bodies.

Reported: repairs applied per case against G2's, rejections by reason,
the value of the applied repair against the best fitting drop, the
short-shank bodies, pictures of teacher against terminal.

## Predictions

K1 holds: the designed classes improved the fitting run by a tenth of
the error or more in G2, and a class that names real damage should
lower the held-out error too. K3 holds: the classes the controls grew
in G2 were worth one to three percent on one run. K4 holds. K2 is the
open one; its first clause failed in G1 and G2 with nothing guarding
it, and the guard is measured rather than chosen, so it may be loose
where it needs to be strict.

## Outcome (frozen, exclusive)

Determined by K1 and K2.

- **A**: both hold. The checked path keeps identity and stops trading
  consumers, and is the workflow's growth rule.
- **B**: K1 holds, K2 fails. Identity is kept and the guard as
  measured is not strict enough.
- **C**: K2 holds, K1 fails. The rules protect the consumers at the
  price of naming the damage.
- **D**: neither.

K3 and K4 are reported under every letter.

No rescue, no second run on the scored cases, no change to the rules,
the tolerances' definition or the budget after this commit. Results go
in `docs/math-track-g3-results.md`; nothing above is edited after the
run.
