# G7: the 3D locomotion case. Preregistration (frozen before any scored case is run)

The 2D arc ended with a growth rule (G4: fit on one run, accept on the
mean of two held-out runs, guard each consumer by the runs' own
distance) and four lessons (`docs/math-track-g6-results.md`). G7 asks
whether the rule and the grammar's design carry to a body that can
fall sideways: the 3D teacher of `docs/gait3d-feasibility.md`, twelve
bodies with three runs each. The bars are absolute; there is no
earlier 3D run to compare with.

## The grammar, and what was checked before any fit

`poc/gait3d/grammar3d.py` is the 2D phase-clock grammar on the
free-rooted body. Five base classes: rhythm, legs, torso and arms as
in 2D, and a lateral class (root sway, hip abduction offset and
oscillation, ankle roll), with torso roll in the torso class. Five
impairment classes: stiff and limp as in 2D; hold (one hip at an
offset with its own small swing, the other knee bent), which is the
2D kneel class named for what it does since the 3D stump does not
kneel; vault reduced to what the arm and torso base cannot do, a lift
at the arm cycle with its own phase; weak with a torso roll during
the weak side's stance added.

**Twin check, by the algebra.** Every hop parameter in 2D entered
through a base parameter (G5). Here no impairment parameter does: the
sided terms act on one side of a symmetric base; limp's duty change
is one-sided where the base duty is not; weak's lag shifts one leg's
clock without the arm's; weak's roll and vault's lift are half-wave
terms where the base terms are full sinusoids; vault's lag is a phase
the base's bob does not have. The first draft of the grammar had two impairment terms that were
twins of each other, and the first exclusivity table
(`poc/results/gait3d_dictionary_check_draft1.*`) found both: limp's
hitch, a half-wave lift during the long side's stance, was vault's
lift at a lag of the leg phase difference (limp absorbed vault 0.98),
and hold's other-knee term was limp's sink on the same side (limp
absorbed hold 0.56). Both terms were removed before this document was
frozen; limp keeps its lift, sink and duty, hold its hip offset and
amplitude. V0 is unaffected (no base parameter changed). The table
below is the rerun on the grammar as frozen.

**Redundancy screen** (`poc/gait3d/redundancy_check3d.py`, at V0):
median over the design bodies, 1.0 meaning the base has the
direction at first order (the screen's threshold limit is on record,
`docs/math-track-g5-prereg.md`): stiff knee 0.81 and lift 0.85, class
step 0.71; limp lift 0.47, sink 0.99, duty 0.80, step 0.51; hold hip
0.86, amp 0.57, step 0.63; vault lift 0.83, lag 0.95, step 0.64; weak
scale 0.00, lag 0.99, roll 0.36, step 0.81. Higher than the 2D screen
throughout (there stiff's step was 0.26 and hold's 0.43), which is
what a base with a lateral class and torso roll buys: more of any
sided change is reproducible at first order by symmetric terms. No
parameter is an exact twin of the base by the algebra; the
exclusivity table is the check that matters.
(`poc/results/gait3d_redundancy_check.*`)

**Exclusivity table** (`poc/gait3d/dictionary_check3d.py`, at V0):
no pair over a half. The largest: legs absorbs hold 0.40, limp
absorbs weak 0.40, legs absorbs limp 0.39, hold absorbs vault 0.38,
legs absorbs vault 0.37. Per body at V0, the oracle and the top
impairment: the left locked knee, stiff at 31 percent on the correct
side with a gap of 0.03, nothing else above 11; the left stump, torso
at 47 percent, then limp at 36 percent on the stump's side and vault
at 36, hold at 2; the legless body, arms and torso at 23 percent
each, vault at 5. The one-leg body's oracle is the lateral class, the
short shank's and the intact body's the legs, the weak hip's the
torso. (`poc/results/gait3d_dictionary_check.*`; the draft grammar's
table is `gait3d_dictionary_check_draft1.*`.)

Two consequences for the design, decided here on that evidence and
before the run. The 3D stump hops on the good leg with the stump held
up (`docs/gait3d-feasibility.md`), and in this grammar's vocabulary
that is a limp with the stump as the short side: the good leg's knee
flexes more in swing and stance and the stump's stance fraction
falls, which the table puts at 36 percent on the correct side, where
hold, the class the 2D stump was named by, is worth 2. The stump's
designed class is therefore limp, with its side; whether hold is ever
added is reported. The legless body's vault is worth 5 percent at V0
against 23 for the arm and torso refits: the 3D legless teacher crawls
with little lift, and its designed class stays vault so that the run
says whether a lift class survives the base refits on it.

## Consumers, and the two pilot fixes

`poc/gait3d/rgre_gait3d.py`: the twelve blocks are the 2D eleven with
the pitch block replaced by the torso's up-axis statistics (pitch and
roll, mean and spread, no Euler angles so the prone body has no
gimbal lock) and a lateral block (the root's sway about its drift).
Yaw and drift are left out: the grammar has no heading, so they would
be a floor on every body. Two fixes were made while fitting V0, before
any scored run, and are declared here:

1. The cycle clock is the touchdowns of the first contact part that
   has them (a foot, a thigh, a hand), with a lower bound of half a
   second on a cycle; the intact 3D teacher's left hip crossed its
   mean once in four seconds, and a hip-angle clock read a two-second
   cycle, which the first V0 fit matched with both legs in phase.
2. The stance block carries the fractions of time with no part, one
   part, and two or more parts down. Alternating legs and legs in
   phase have the same per-part stance fractions and differ here.

## V0

`poc/gait3d/v0.py`: the five base classes (28 parameters) fitted to
the intact body's seed-0 run by differential evolution, 80
generations, population 12 per parameter, two seeds, the better kept
(`poc/results/gait3d_v0.json`, from `gait3d_v0_s1.json`; the other is
`gait3d_v0_s0.json`). Error 0.331 against the default state's 0.609
(the 2D V0 was 0.300 on eleven blocks). Per block: contact 0.39,
coupling 0.27, stance 0.21, joint statistics 0.52, asymmetries 0.32
and 0.26, speed 0.04, height 0.02, orientation 0.46, lateral 0.26,
rhythm 0.13, reach 0.14, phase-binned pose 0.62. The student walks
upright with the legs a quarter cycle apart (`phase_r` 1.58): the
teacher's own left-right hip correlation is +0.15 and its foot
contacts' -0.35, a shuffle rather than a clean alternation, and the
fit follows it. Three V0 fits preceded this one and are the reason
for the two consumer fixes above: with the hip-angle clock and no
coupling block, both seeds put the legs in phase (`phase_r` 0.42 and
-0.41) at half the teacher's cadence, error 0.318 and 0.334 on the
old blocks (`gait3d_compare_intact_v0.png` shows the kept fit).

## The procedure

G4's, unchanged (`poc/g7_experiment.py`, a copy of G6's script on the
3D modules): every repairable class fitted by the seven-point sweeps,
candidates in order of fitting drop, the first that passes the spent
rule (one percent), the held-out test (the mean of the two held-out
runs must fall) and the guard (no consumer worse than the mean
distance between the fitting run and the held-out runs on it at V0)
is applied; declined when none passes; six steps. Fourteen cases: the
seven design bodies at seed 0, the five mirrors at seed 0, and the
intact and legless bodies at seed 1. Designed classes: stiff for the
locked knees, limp for the stumps (see the exclusivity table), vault
for the legless body; none for the one-leg bodies (the hop is the base on one leg, G6), the weak
hips (the 3D weak hip walks with a mild limp) or the short shanks
(the limp is their geometry in 2D; if the exclusivity table's oracle
on the short shank is limp, that is recorded above and reported, not
barred).

## The declared pilot

The legless body, teacher seed 1, seeds 0 and 2 held out, two steps
(`poc/results/g7_pilot.*`): arms (fitting 0.761 to 0.697, held-out
mean 0.664 to 0.561, both runs lower), then declined with every class
spent. That run of the legless teacher tumbles rather than crawling
prone (its torso's up axis averages upright with a spread of 0.52),
so the torso class had nothing to do; probed after the pilot, a lean
sweep alone raises its error at every grid point. The pilot ran the
path and is excluded from every bar. No change was made after it.

## Bars (frozen)

Thirteen scored cases (the pilot excluded): three design bodies with
a designed class, two mirrors, nine damaged bodies, four controls.
`poc/g7_score.py`, committed with this document.

- **K1, identity.** The first impairment repair names the class and
  side on `>= 2` of the three design bodies, within two on 3 of 3, and
  within two on 2 of the 2 mirrors.
- **K4, growth generalises.** The terminal state's mean held-out error
  is below V0's on `>= 7` of the nine damaged bodies.
- **K2, consumers.** No consumer beyond its tolerance on `>= 7` of 9.
- **K3, controls.** At most 4 impairment repairs on the four controls.

Reported: repairs per case, rejections by reason, held-out agreement,
value against the best fitting drop, pictures of teacher against
terminal in side and front view.

## Predictions

K4 holds: the rule generalised on nine of nine in 2D and the 3D
teachers have three runs each. K1 fails, on the legless body: vault
is worth 5 percent at V0 and the arm and torso refits it competes
with are worth 23 each, so it is predicted spent before it is named,
and the within-two bar (3 of 3) is then lost; the locked knees are
predicted named first on both sides (stiff has no competitor above a
third of it), and the stumps within two (limp on the stump's side,
after the torso refit). K2 holds. K3 is open: the 3D weak hip limps a
little, and a held-out-passing weak or limp repair on it would count.
Predicted letter C.

## Outcome (frozen, exclusive)

Determined by K1 and K4.

- **A**: both hold. The 2D workflow carries to 3D.
- **B**: K1 holds, K4 fails.
- **C**: K4 holds, K1 fails. The growth carries; the naming does not.
- **D**: neither.

K2 and K3 are reported under every letter.

No rescue, no second run on the scored cases, no change to the
grammar, the consumers, the rules or the budget after this commit.
Results go in `docs/math-track-g7-results.md`; nothing above is
edited after the run.
