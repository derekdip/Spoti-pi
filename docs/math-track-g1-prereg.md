# G1: growing a gait grammar toward damaged bodies. Preregistration (frozen before any scored case is run)

The first locomotion case for the procedure. A physics teacher
(`docs/gait-feasibility.md`: a planar biped under predictive sampling,
one cost for every body) produces a gait for each of seven bodies:
intact, weak left hip, locked left knee, short left shank, left shank
removed, left leg removed, both legs removed. The cheap side is a gait
grammar (`poc/gait/grammar.py`): a phase clock drives every joint in
closed form, the root is grounded on whatever part of the body is
lowest, and the grammar has a walk base and one class per contact
pattern the teacher showed: stiff leg, short leg, kneel-and-step,
one-leg hop, arm vault, and a weak hip, each with a left and a right
version where the body has sides. The question is the one the arc has
asked in every domain: given the teacher's gait for a damaged body,
does residual-guided growth add the class that names the damage.

## Setting

**Consumers** (`poc/gait/rgre_gait.py`), what a game reads from a
gait, each normalised by its own scale and width: floor contact of
every part (feet, thighs, hands, pelvis) in six time bins; per-part
stance fraction, bout rate and bout length; per-joint mean, spread,
minimum and maximum; forward speed; torso height in six bins and head
height; pitch mean and spread; cycle frequency and regularity; the
hands' reach; and every joint's mean cycle in sixteen phase bins of
the body's own cycle. Nine blocks. The window is one to five seconds
of the teacher's run.

**V0** is the walk base fitted once to the intact teacher by
differential evolution (`poc/gait/v0.py`, `poc/results/gait_v0.json`),
error 0.265. Two teacher runs of the intact body with different seeds
score 0.409 against each other on these consumers and two legless
runs 0.284, so V0 is closer to its teacher than another run of the
same body is: the consumers measure the gait and not the run.

**Growth.** From V0, on every body, three selection rules grow the
grammar along their own paths for four steps with the arc's spent
rule and no stopping rule: the projection selector, the hybrid rule
with the dictionary check, and the oracle. The full oracle table is
computed at every step of every path. The joint floor, every
repairable parameter free at once by differential evolution from V0,
is computed once per case. `poc/g1_experiment.py`, scorer
`poc/g1_score.py`, both committed with this document.

**The dictionary check** (`poc/gait/dictionary_check.py`,
`poc/results/gait_dictionary_check.json`) was run on the seven design
bodies at V0. Median linearisation gap by class type over repairs
worth at least one percent: short 0.04, stiff 0.05, vault 0.11, hop
0.17, weak 0.42, kneel 0.67. So the hybrid rule fits the kneel and
weak classes (both sides) and projects stiff, short, hop and vault,
fitting the top two projected: six repairs a step of ten.

**Cases.** Design: the seven bodies, teacher seed 0. Transfer: the
right-side mirror of each impairment (weak hip, locked knee, short
shank, stump, one leg), teacher seed 0, and a second teacher seed of
the intact and legless bodies. Fourteen cases. The designed class per
body: locked knee → stiff on that side, short shank → short on that
side, stump → kneel on that side, one leg → hop, no legs → vault. The
weak hip has no designed class: its teacher walked (the feasibility
build's result), and what growth does with it is reported. The intact
second seed is a control.

## The declared pilot, and what it changed

Everything above was reached by iteration on the intact body and the
step-zero tables, before this document, and none of it is used as a
bar. In order:

1. Poses compared at absolute instants let a static crouch beat a walk
   whose phase was slightly off; V0 fitted as a crouch. **Periodic
   quantities are compared per phase bin of the body's own cycle.**
2. A plain sinusoid cannot hold the hip extended through stance and
   flex it quickly in swing. **A stance-duty phase warp was added to
   the walk base.**
3. Two teacher runs of the same body differed more on the consumers
   than the fitted grammar differed from either, because two or three
   irregular cycles average into a smeared waveform. **The blocks that
   carry the gait's size became timing-free statistics** (per-joint
   mean, spread, range; per-part stance fraction, bout rate, bout
   length), speed, height and pitch became blocks of their own, and
   the window grew from three seconds to four.
4. The teacher's pitch in time differs between seeds by 1.5 scales.
   **Pitch is a statistics block, and the grammar has a pitch
   oscillation.** V0 went from 0.415 to 0.265 and below the
   seed-to-seed floor.
5. The student clipped its joints to the body's ranges, so on the
   locked-knee body the stiff class was inert: the clip had already
   stiffened the leg, and the class had nothing to add. **The student
   no longer clips**: it does not know which joint the damage locked,
   and the teacher's behaviour has to reveal it. With that, the
   step-zero oracle on the locked-knee body is the stiff class (gap
   0.02), where before it was the kneel class.

The step-zero tables after these fixes, on the design bodies: the
oracle's first repair is the designed class on the locked knee
(stiff), the one-leg body (hop) and the legless body (vault); on the
short shank the oracle prefers the right-side short class over the
left by 0.017 of the error, both fitting the asymmetry; on the stump
the oracle prefers hop (0.511) over kneel (0.476), the teacher's
kneel-and-step being 28 percent airborne. The projection alone picks
the designed class on the short shank, the one-leg body and the
legless body, and hop on the locked knee. These tables are the reason
identity is barred within two steps as well as at the first step.

Smoke test of the experiment code: the legless body, teacher seed 1,
one step (`poc/results/g1_pilot.*`), excluded from every bar.

## Bars (frozen)

- **I1, first pick.** The hybrid rule's first repair is the designed
  class on `>= 3` of the five design bodies that have one.
- **I2, identity within two steps.** The designed class is among the
  hybrid rule's first two applied repairs on `>= 4` of those five.
- **I3, transfer.** On the four mirrored bodies with a designed class,
  the right-side designed class is among the first two applied repairs
  on `>= 3` of four.
- **I4, value.** Over every step of every path with positive oracle
  gain, the hybrid rule's median value captured `>= 0.90`.
- **I5, floor.** Median over the twelve impaired cases of the hybrid
  terminal reduction over the joint floor's reduction `>= 0.80`.
- **I6, consumers.** At the hybrid terminal no consumer is worse than
  at V0 on `>= 10` of the twelve impaired cases.

Reported: the projection and oracle paths on every line; the two
controls (intact seed 1, and the weak hip on both sides), with whether
the first repair was declined; per-case pictures of teacher against
terminal grammar.

## Predictions

I2, I3 and I4 hold: fitting six of ten classes a step, with the
designed classes either fitted (kneel) or first or second by
projection on the tables above, should reach them within two steps.
I1 is open, on the stump and the short shank in particular. I5 is
open: the fire found the greedy path 0.73 of the joint floor with this
grammar's cousin. I6 should hold; the consumer at risk is rhythm,
which no class addresses.

## Outcome (frozen, exclusive)

Determined by I2 and I4: whether growth names the damage, and whether
the selection is worth the oracle's value at its cost.

- **A**: both hold. The grammar and the procedure identify impairments
  from the teacher's gait, and the fire workflow carries to locomotion.
- **B**: I2 holds, I4 fails. Identity holds; the hybrid rule loses
  value on this dictionary and the oracle should be used, which is
  cheap here.
- **C**: I4 holds, I2 fails. Selection works and the classes do not
  name the damage: a grammar problem.
- **D**: neither.

I1, I3, I5 and I6 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
grammar, the consumers, the classification or the budget after this
commit. Results go in `docs/math-track-g1-results.md`; nothing above
is edited after the run.
