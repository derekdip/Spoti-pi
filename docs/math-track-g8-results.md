# G8 results: outcome C, as predicted. Naming on top of a full base refit does not name the right stump or the legless body, and it loses the left locked knee: the base absorbs sided damage in both orders, in different places

Preregistration: `docs/math-track-g8-prereg.md`, frozen at commit
`5641499`, unchanged. Raw output: `poc/results/g8.json`, `g8.log`,
`g8_report.md` (the frozen scorer's output, `poc/g8_score.py`), and
one picture per case (`poc/results/g8_*_checked.png`). Fourteen cases
run, thirteen scored (the declared pilot excluded), eight steps with
the base phase at most six, 490 seconds on three workers, scored
against G7 on the same teachers.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **1 of 3, 1 of 3, 1 of 2** (G7: 2, 2, 1) | **fail** |
| K4 growth generalises | mean held-out below V0's on `>= 7` of 9 | 9 of 9, both runs lower on 9 of 9 | pass |
| K2 consumers | none beyond tolerance on `>= 7` of 9 | 9 of 9 | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | 0 | pass |

K1 fails and K4 holds, so the letter is **C**, the predicted letter,
for the predicted reasons and one more.

## What the naming step showed

The naming step is the first step at which only impairment classes
are offered, after the base has refitted until spent. Its drops, as a
fraction of the error at that point, on the five cases with a
designed class:

| case | designed | after the base refit | named |
|---|---|---|---|
| left locked knee | stiff, left | limp 0.207, stiff 0.195, others 0 | **limp, left** |
| right locked knee | stiff, right | stiff 0.092, limp 0.013 | stiff, right |
| left stump | limp, left | hold 0.083 (held-out rejected), stiff 0.026 (rejected), limp 0.013 | limp, left |
| right stump | limp, right | vault 0.044, hold 0.010, limp 0.000 | vault |
| legless | vault | vault 0.000 | none |

**The two predicted misses hold.** On the right stump limp is worth
nothing after the full base refit, and on the legless body vault is
worth nothing: the same G7 paths, the same terminals to the third
decimal. On the left stump limp is named, at 1.3 percent, because it
is the one class above the spent line that passes the held-out test;
hold, at 8 percent, raises the held-out mean. The base given every
chance describes the stump's hop and the legless crawl, and naming
them by a class is not something these consumers support.

**The unpredicted loss.** In G7 the left locked knee named stiff at
step zero at 31 percent with a gap of 0.03, the cleanest identity in
the run. In G8 the base refitted first (rhythm, arms, legs, torso,
down to 0.335 from 0.568) and at the naming step limp and stiff were
within a percent of each other, limp ahead, on the correct side. The
four base refits took most of what stiff explains, a knee that does
not bend and a hip that lifts to clear it, into symmetric knee and
hip terms; what was left, the asymmetry, limp's long-side knee terms
fit about as well as stiff's one-side knee scale. The right locked
knee kept stiff (9 percent against limp's 1) because its base refit
left more of the stiffness in place. The terminal errors say the
same: both locked knees end worse than in G7 (0.298 against 0.272,
0.425 against 0.396), the only cases that do; three cases end better,
seven identical.

**Growth, consumers, controls (K4, K2, K3).** As G7: nine of nine
damaged bodies below V0 on both held-out runs, nine of nine within
tolerance, no impairment class on any control. The order does not
touch what the rule generalises.

## What G8 establishes

1. The base-first order is not a better identity rule. It names what
   G7 named on one locked knee and one stump, loses the other locked
   knee, and names neither of the bodies it was tried for. The item
   G7 left open closes on the record: with the base given every
   chance first, the consumers do not support naming the right stump
   or the legless body by a class.
2. Absorption runs both ways and the exclusivity table reads only one
   of them. The table measures what one class can reproduce of
   another's fitted effect, starting from V0, and put legs absorbing
   stiff at 0.34. Four base classes refitted together absorb enough
   of the left locked knee's stiffness to leave stiff and limp tied.
   The table's pairwise numbers underestimate what the whole base
   does in sequence, which the redundancy screen's high first-order
   figures (stiff's step 0.71) had suggested.
3. The identity that survives both orders is a class that owns a
   direction the base cannot reach in either order: stiff on the
   right locked knee, limp on the left stump. Everything else named
   in this arc depends on the order in which the base is refitted,
   which is a property of the greedy fitter, not of the body.
4. For the runtime, the consequence is that the grammar state, not
   the class label, is the deployable description of a body: the
   state generalises on every damaged body under both orders, and
   the label does not.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
