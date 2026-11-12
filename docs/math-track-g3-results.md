# G3 results: outcome D. Held-out acceptance generalises the growth on every damaged body, loses one mirror to the teacher's own variability, and lets a control grow where the teacher's second run agrees with its first; the measured guard never binds

Preregistration: `docs/math-track-g3-prereg.md`, frozen at commit
`831b9a8`, unchanged. Raw output: `poc/results/g3.json`, `g3.log`,
`g3_report.md` (the frozen scorer's output, `poc/g3_score.py`), and
one picture per case (`poc/results/g3_*_checked.png`). Fourteen cases,
six steps, one path, 531 seconds on three workers, scored against G2's
oracle path on the same fitting teachers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity kept | first `>= 3` of 4, within two `>= 3` of 4, mirrors `>= 2` of 3 | **4 of 4, 4 of 4, 1 of 3** | **fail** on the mirrors |
| K2 consumers | none worse on `>= 6` of 10; none beyond tolerance on `>= 8` | **3 of 10**; 10 of 10 | **fail** on the first clause |
| K3 controls | impairment classes on `<= 1` of 4 | **2 of 4** | **fail** |
| K4 growth generalises | held-out error below V0's on `>= 8` of 10 | **10 of 10** | pass |

K1 and K2 both fail, so the letter is **D**. The bars were the right
bars to have frozen and three of them fail for reasons that are worth
more than a pass would have been.

## What each bar means

**Identity on the design bodies is untouched; one mirror is lost to
the held-out test (K1).** The four design bodies name their damage at
the first impairment repair, as in G2. On the right stump, the kneel
class was fitted at steps one to four and rejected each time because
it raised the held-out error, by 0.01 to 0.02, until at step five a
fit passed; kneel was the fourth impairment repair, the sixth overall. The kneel class fitted to one run of
that body does not transfer to the other run of the same body: the two
runs differ by 0.45 of a scale on contact timing and 0.40 on rhythm,
and a class whose fit is tuned to one run's timing loses on the other.
The right one-leg body never took hop, as in G2, for G2's reason.

**The consumers still trade, and the trading is inside the teacher's
own noise (K2).** Seven terminals of ten are worse than V0 on some
consumer, one more than G2. None is worse by more than the distance
between the two runs of the same body on that consumer: the guard, as
measured, never rejected a candidate anywhere in the run: of the 125
rejections, 35 were the held-out test's and 90 the spent rule's. So the strict
clause fails and the tolerance clause passes, and the reading is not
that the guard is loose but that the strict bar, frozen in G1 and kept
since, asks for more consistency from the student than the teacher
has with itself. A consumer worsened by less than the teacher's
run-to-run spread is not evidence of anything.

**Two controls grew and two did not (K3).** Two of four grew impairment
classes and two did not, and the test read the teacher correctly both
times. The intact body's first run took torso, then vault, then weak,
and the held-out error went from 0.488 to 0.479; the right weak hip
took stiff, weak and kneel after two base refits, and its held-out
error went from 0.539 to 0.380. On the other two the test stopped what
G2's oracle had grown: the intact body's second run took torso only,
with legs, rhythm, weak, arms and stiff all rejected for raising the
first run's error, where G2 had taken legs, rhythm, legs and vault;
the left weak hip took torso and legs and declined where G2 had added
arms. A class fitted on one run that lowers the other run's error has
found something both runs share, so the two that grew were not fits to
noise: there is something in the intact teacher's arms the vault class
expresses and something in its hips the weak class expresses that V0's
walk base does not, worth two percent on the run not fitted. The
premise of the control, that an undamaged body has nothing for an
impairment class to name, was wrong for this teacher, and the weak-hip
bodies, whose teacher walked, were never controls by the same
argument. The bar counts a correct answer as a failure, and the letter
stands.

**Growth generalises (K4).** Every damaged body's terminal state is
better against the run it never saw than V0 was, by 0.005 (the left
stump) to 0.37 (the legless body's first run and the right locked
knee). Held-out acceptance did what
it was for. It rejected 35 candidate repairs across the run, all for
raising the held-out error, and the repairs it applied were the
oracle's own on the median step.

## What G3 establishes

1. Held-out acceptance is the growth rule for this case: no constant,
   every damaged body generalises to a second run of its teacher, and
   the design-body identity of G2 is kept. Its cost is one teacher run
   per body and one rejected true class on one mirror.
2. The strict consumer bar is retired. A consumer worse than V0 by
   less than the teacher's run-to-run spread on that consumer is
   within noise, and the measured tolerance is the bar that should
   have been frozen from G1.
3. The teacher has structure the base cannot express even when
   undamaged, and the held-out test admits it exactly where a second
   run confirms it. A control for this procedure is a body whose two
   runs agree, not a body without damage; none of these bodies is one,
   and the K3 bar measured that premise rather than the rule.
4. Two runs of a noisy teacher are not enough to decide a class on
   the mirrors: a single held-out run rejected kneel four times on a
   body that kneels. Where the teacher is this variable, three runs
   and a majority would be the test, and that is a cost to weigh
   against the identity it buys.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
