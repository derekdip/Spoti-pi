# G2: growing a gait grammar with exclusive classes. Preregistration (frozen before any scored case is run)

G1 (`docs/math-track-g1-results.md`) found the procedure's selection
carrying to locomotion and the grammar's classes failing to name the
damage: a left and a right version of a class could each fit the
other side's damage, a hop class could produce a kneel's contacts,
and a two-slot selection rule missed the stiff class where the oracle
had it first. G2 changes the grammar and the selection rule, keeps
the fourteen teachers, and asks the same question: given the teacher's
gait for a damaged body, does growth add the class that names the
damage.

## What changed since G1, and what the pilot found

**Classes.** Every sided class has one signed side parameter in
[-1, 1] instead of a left and a right copy: stiff, limp, kneel, weak,
plus hop and vault. A body's damage is named by a class and the sign
of its side. The walk base is four re-fittable classes (rhythm, legs,
torso, arms) rather than one frozen block, so that growth can absorb
what a damaged body changed about the walk itself before the
impairment classes are asked to explain what is left; identity counts
impairment repairs only.

**Selection.** The oracle: every repairable class fitted at every
step, best drop taken. Fits cost three to five seconds here, and G1's
two-slot hybrid lost the locked knee where the oracle had it. The
projection selector is run beside it for the record, and a third path,
the oracle restricted to repairs that make no consumer worse, is run
and reported.

**The floor** is Powell over every repairable parameter from V0 and
from the oracle terminal, with a budget of 4000 evaluations each, the
better of the two. G1's differential-evolution floor returned its
start on half the cases.

**Pilot fixes, in order, all before this document.** (6) Left-right
asymmetry blocks were added to the consumers, differences of the
per-joint and per-part statistics between sides, because a symmetric
re-fit of the base absorbed most of every damaged body's residual and
left the sided classes nothing to name. Scaled by their own rms they
were a noise magnet on the intact body (two teacher seeds differed by
two scales there), so they are scaled by the units of the block they
are a difference of. (7) The limp class was rewritten twice: the
teacher's long knee flexes more in stance and in swing, so both the
class's lift and its sink act on the long side, and a stance-duty
term was added. Neither made the class name the short shank. A forced
grid over the class on that body found no setting that beats a
symmetric base re-fit, because the student's grounding on the shorter
leg reproduces the teacher's stance asymmetry by itself (student 0.20
against 0.44 for the two feet, teacher 0.30 against 0.70) and what is
left is symmetric. **The short shank therefore has no designed class
in G2**: whether any impairment class is added on it at over one
percent is reported, not barred. V0 was refitted with the new
consumers: 0.300 on the intact teacher, against a seed-to-seed floor
of 0.425.

**The dictionary check** (`poc/gait/dictionary_check.py`,
`poc/results/gait_dictionary_check.{json,log}`) now has two parts,
measured on the seven design bodies at V0. The linearisation gap by
class over repairs worth at least one percent: stiff 0.01, limp 0.09,
vault 0.11, hop 0.13, kneel 0.20, arms 0.21, legs 0.30, torso 0.51,
weak 0.64, rhythm 0.82. The exclusivity table, the share of one
class's fitted effect another class can reproduce, median over the
bodies where the first did something:

| effect of | absorbed by | share |
|---|---|---|
| limp | legs | 0.62 |
| limp | hop | 0.58 |
| kneel | legs | 0.57 |
| kneel | limp | 0.55 |
| limp | kneel | 0.42 |
| weak | limp | 0.38 |
| kneel | hop | 0.34 |
| hop | legs | 0.32 |
| stiff | any | at most 0.15 |
| vault | any | at most 0.16 |
| hop | any but legs | at most 0.25 |

So stiff, vault and hop are exclusive; kneel is absorbable by a base
re-fit and by limp above a half; limp is absorbable by legs and hop.
This is the check G1's results asked for, and it predicts where
identity can and cannot be measured before a case is run.

**Step-zero tables** on the design bodies with the new grammar: the
oracle's first repair is a base re-fit on every body with legs
(legs on the locked knee, stump and short shank; torso on the intact
and weak-hip bodies) and the designed class on the one-leg (hop) and
legless (vault) bodies. After the best base re-fit, the best
impairment class is stiff on the locked knee (0.087 of the error,
side left) and kneel on the stump (0.109, side left), with hop second
on the stump at 0.062.

Smoke test: the legless body, teacher seed 1, two steps
(`poc/results/g2_pilot.*`), excluded from every bar.

## Cases

The fourteen G1 teachers, unchanged. Design bodies with a designed
class: locked knee (stiff, left), stump (kneel, left), one leg (hop),
no legs (vault): four. Mirrors with a designed class: locked knee
(stiff, right), stump (kneel, right), one leg (hop): three. Reported:
the two short-shank bodies, the weak-hip bodies, the intact second
seed as a control, the legless second seed. Six steps.

## Bars (frozen)

- **J1, first impairment repair.** On the oracle path, the first
  impairment repair applied names the designed class and side on
  `>= 3` of the four design bodies.
- **J2, within two.** The designed class and side is among the first
  two impairment repairs applied on `>= 3` of four.
- **J3, transfer.** The same within two on `>= 2` of the three
  mirrors.
- **J4, floor.** Median over the ten damaged bodies (the four, the
  three, the two short shanks and the legless reseed) of the oracle
  terminal reduction over the local floor's reduction `>= 0.80`,
  ratios capped at 2.
- **J5, consumers.** At the oracle terminal, no consumer worse than
  at V0 on `>= 6` of those ten.

Reported: the safe path's identity and how often it declined at step
zero; the projection path's value per step; the controls' growth; the
short-shank bodies' impairment repairs; pictures of teacher against
oracle terminal.

## Predictions

J1 and J2 hold for the locked knee, the one leg and the no-legs
bodies, whose classes the exclusivity table calls separable. The stump
is the open one: kneel is absorbable by legs (0.57) and limp (0.55),
the step-zero table has kneel first after the base re-fit and hop at
half its value, and hop took the stump first in G1. J3 follows J2.
J4 is open. J5 is expected to fail as it did in G1 (four of ten),
since the objective is a mean over eleven blocks; the safe path is
there to show what identity costs when it is enforced.

## Outcome (frozen, exclusive)

Determined by J2 and J3: identity within two impairment repairs on the
design bodies, and on the mirrors.

- **A**: both hold. Exclusive classes name the damage, on both sides.
- **B**: J2 holds, J3 fails.
- **C**: J3 holds, J2 fails.
- **D**: neither. The exclusivity table was right about kneel and
  wrong about the rest, or the residual does not carry the damage.

J1, J4 and J5 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
grammar, the consumers, the classes or the budget after this commit.
Results go in `docs/math-track-g2-results.md`; nothing above is edited
after the run.
