# G1 results: outcome C. Selection carries to locomotion at the oracle's value; the grammar's classes do not name the damage on three bodies of five, for three different reasons

Preregistration: `docs/math-track-g1-prereg.md`, frozen at commit
`061e963`, unchanged. Raw output: `poc/results/g1.json`, `g1.log`,
`g1_report.md` (the frozen scorer's output, `poc/g1_score.py`), and
one picture per case of teacher against hybrid terminal
(`poc/results/g1_*_hybrid.png`). Fourteen cases, four steps, three
paths, 1697 seconds on three workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| I1 first pick = designed class, design bodies | `>= 3` of 5 | **2** (one leg, no legs) | **fail** |
| I2 designed class within two steps, design bodies | `>= 4` of 5 | **3** (stump joins) | **fail** |
| I3 designed class within two steps, mirrored bodies | `>= 3` of 4 | **1** (one leg); the scorer also counted the legless reseed and printed 2 of 5 | **fail** |
| I4 value per step, hybrid | median `>= 0.90` | **1.000** (mean 0.83) at 6 repairs a step of 10; projection 0.77 (0.54) | pass |
| I5 terminal reduction over the joint floor | median `>= 0.80` | vacuous: the frozen floor returned V0 itself on 7 of 14 cases | **not measured** |
| I6 no consumer worse than V0 at the terminal | `>= 10` of 12 | **4 of 10**; the bar miscounted the impaired cases, and 8 of 10 fails too | **fail** |

I4 holds and I2 fails, so the letter is **C**: selection works and
the classes do not name the damage. The scorer's last line printed A,
because its letter logic tested a count for truth instead of against
the bar; the bar lines above it are right and the tree's text is
unambiguous. That is a defect in a frozen scorer and is recorded as
one.

## What each bar means

**Selection carries (I4).** The hybrid rule, fitting the kneel and
weak classes and the top two projected classes, takes the oracle's own
repair on the median step and 0.83 of its value on average, at six
repairs a step against the oracle's ten. The arc's projection selector
alone captures 0.77 in median and 0.54 on average. On the one-leg and
legless bodies, all three rules take the same path and end at the same
error, on both sides and both seeds.

**Identity fails three ways (I1, I2, I3).**

- *Locked knee: a selection miss.* The oracle's first repair is the
  stiff class on both sides (drop 0.115 of the error, gap 0.02). The
  projection ranked hop and short above it, so the hybrid's two
  projected slots went elsewhere, stiff was never fitted, and the
  fitted kneel class took the step; on the mirror the stiff class
  arrived third. The class is right and the two-slot rule is too
  narrow for this dictionary: with ten classes at three seconds a fit,
  the oracle is thirty seconds a step and should simply be used.
- *Short shank: a grammar ambiguity.* Both short classes fit a
  leg-length asymmetry, one by lifting the short side and one by
  sinking the other side, and the oracle itself prefers the wrong
  side by 0.017 of the error on the left body and takes kneel on the
  right. Two classes that can each explain the other's damage do not
  name anything.
- *Stump: class overlap.* The teacher's kneel-and-step is 28 percent
  airborne, hop wins the first step on both sides, and kneel arrives
  second on the left and not within four steps on the right. Hop and
  kneel share the crouch and the flight and differ in the thigh
  contact, which the hop class is free to produce as well.
- *One leg and no legs: identity holds* at the first step on both
  sides and both seeds, by every rule.

**The floor was not a floor (I5).** Differential evolution over 55
parameters from V0 with 25 generations returned V0 itself on seven
cases, so the frozen ratio is meaningless. A post-hoc local floor
(`poc/gait/posthoc_floor.py`, Powell from V0 and from the hybrid
terminal, the better of the two) puts the hybrid at 0.95 of the
available reduction in median: at or beyond the local floor on the
short-shank, stump, one-leg and legless bodies, and at 0.20 and 0.38
on the two locked-knee bodies, where the local floor is 0.411 against
the hybrid's 0.615 and 0.577. The greedy reaches what is reachable
except where it chose the wrong class, which is the identity failure
seen from the other side. Unregistered, reported as such.

**Consumers get worse (I6).** On six of ten impaired cases the
terminal state is worse than V0 on at least one consumer: rhythm and
contact timing on the locked knee, reach on both stumps, pitch on the
legless reseed. The objective is the mean over nine blocks and a class
fitted on it will trade one block for another; fire's F1 recorded the
same once, and here it is the rule rather than the exception. The
grammar has no class that touches rhythm, and every class touches
reach through the arms.

**Controls.** The intact body with its own teacher declined every
repair at step zero, as it should. The intact body against a second
teacher seed, V0 error 0.475 against a seed-to-seed floor of 0.409,
grew four classes (vault, stiff, weak on both sides) to 0.413: growth
absorbs the teacher's run-to-run variability with whatever classes
are at hand, which is what a control is meant to show and what the
one percent spent rule does not prevent. The weak-hip bodies, whose
teacher walked, took hop and vault on both sides.

## What G1 establishes

1. The fire workflow carries to locomotion as far as the procedure is
   concerned: V0 fits below the teacher's own seed-to-seed
   variability, the hybrid rule captures the oracle's value at six
   repairs of ten, and the two bodies whose gait is a different
   contact pattern from the walk, one leg and none, are identified at
   the first step every time.
2. The grammar does not partition the gaits. Two-sided classes that
   can each fit the other side's damage, and a hop class that can
   produce a kneel's contacts, mean that the residual can be explained
   by the wrong class at nearly the same value, and no selection rule
   can tell them apart. The next grammar needs classes that are
   exclusive in what they can produce: one asymmetry class with a
   signed side, and a kneel class that owns the thigh contact.
3. Two projected slots are too few when fits cost three seconds.
   Selection economy was the point in fire, where a repair was an
   optimiser run; here the oracle is the method.
4. The greedy reaches the local floor where it picks the right class,
   and stays 0.2 of the way there where it does not.
5. Three defects in the freeze: a floor optimiser that did not move,
   a consumer bar counted against twelve cases where there are ten,
   and a scorer whose letter line tested a count for truth. Each is
   named here and none changes a verdict.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
