# G2 results: outcome A. With exclusive classes and the oracle as selector, growth names the damage on four design bodies of four and two mirrors of three; the consumers still get worse on six terminals of ten

Preregistration: `docs/math-track-g2-prereg.md`, frozen at commit
`5528ab5`, unchanged. Raw output: `poc/results/g2.json`, `g2.log`,
`g2_report.md` (the frozen scorer's output, `poc/g2_score.py`), and
one picture per case of teacher against oracle terminal
(`poc/results/g2_*_oracle.png`). Fourteen cases, six steps, three
paths, 1718 seconds on three workers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| J1 first impairment repair names the damage, design bodies | `>= 3` of 4 | **4 of 4** | pass |
| J2 within the first two impairment repairs, design bodies | `>= 3` of 4 | **4 of 4** | pass |
| J3 within two, mirrored bodies | `>= 2` of 3 | **2 of 3** (the right one-leg body never took hop) | pass |
| J4 terminal reduction over the local floor | median `>= 0.80` | **0.976** | pass |
| J5 no consumer worse than V0 at the terminal | `>= 6` of 10 | **4 of 10** | **fail, as predicted** |

J2 and J3 hold, so the letter is **A**: exclusive classes name the
damage, on both sides. G1's identity on the same teachers was two of
five at the first step and three of five within two; here it is four
of four and four of four, and the change between the two runs is the
grammar and the selector, not the teachers or the consumers' purpose.

## What each bar means

**Identity holds where the exclusivity table said it would (J1, J2,
J3).** The locked knee takes a base re-fit of the legs and then the
stiff class on the correct side, on both bodies. The stump takes legs
then kneel on the left, and hop then kneel on the right, both with
the correct side. The one-leg and legless bodies take hop and vault
first on the design side and on the reseed. The one miss is the
right one-leg body, where four base re-fits took the error from 0.457
to 0.245, within 0.012 of the local floor, and hop was never worth
one percent: the walk base, re-fitted, produced the kneel-and-hop
gait on its own. That is the table's warning about hop and legs
(0.32) arriving at the case level, and it is the reason the bar was
two of three and not three.

**The short shank is unnamed, as declared.** The left body took one
base re-fit and no impairment class; the right took rhythm and then
weak on the correct side at just over one percent. The student's
geometry carries the limp.

**The oracle reaches the local floor (J4).** Median 0.976, the lowest
0.87 on the left one-leg body. With every class fitted at every step
the greedy path ends where a joint local optimiser from the same start
ends, on every damaged body.

**Consumers get worse (J5), and the guard that would stop it stops
everything.** Six terminals of ten are worse than V0 on at least one
block, rhythm and reach most often, as in G1. The safe path, the
oracle restricted to repairs that make no consumer worse, declined at
step zero on six of ten damaged bodies and named the damage on none:
a repair that improves the mean of eleven blocks and worsens none of
them does not exist at step zero. The guard a workflow needs is a
tolerance per consumer, the seed-to-seed floor of that consumer being
the natural one, and it is not built here.

**Controls grow.** The intact body with its own teacher took a torso
re-fit and then vault and weak; the intact reseed took legs, rhythm,
legs and vault; the right weak hip took stiff, weak and kneel after
three base re-fits. The one percent spent rule admits impairment
classes on a teacher's run-to-run variability, which G1 found and G2
did not set out to fix. It is the same fact as J5 from the other
side: the residual after the base is explained has structure the
teacher's noise put there, and any class will take a percent of it.

**The projection selector is useless on this dictionary.** Median
value 0.31, mean 0.06 over 83 steps: with four base classes whose
tangents dominate the residual, the projection ranks a base re-fit
above the impairment class on almost every step and then ranks the
wrong impairment. The oracle is the selector for this case, at ten
fits of three to five seconds a step.

## What G2 establishes

1. Exclusive classes name the damage. Identity went from two of five
   to four of four on the design bodies and from one of four to two of
   three on the mirrors, with the same teachers, by giving each
   impairment one class with a signed side, by letting the walk base
   re-fit before the impairment classes are asked to explain anything,
   and by using the oracle.
2. The exclusivity table predicts identity before a run. Stiff, hop
   and vault, which no other class absorbs above a sixth, were named
   every time on the design side; kneel, absorbable by a base re-fit
   and by limp above a half, was named second on the right stump; hop,
   absorbable by legs at a third, was missed once. That is the check
   G1 asked for, and it works.
3. A limp made by leg-length difference is carried by the student's
   geometry and needs no class. Damage that changes the body changes
   the grammar's output without a switch; damage that changes what the
   body does needs one.
4. The consumer objective still trades blocks against each other, and
   a zero-tolerance guard is the wrong fix. A per-consumer tolerance
   is the next change to the workflow, and with it a decline rule that
   a teacher's noise cannot pass.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
