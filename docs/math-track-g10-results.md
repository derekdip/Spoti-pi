# G10 results: outcome C, as predicted. On the iteration-7 teacher the fitted states walk with swinging arms at the teacher's speed, growth generalises on eight damaged bodies of nine, and the classes name the locked knees and little else

Preregistration: `docs/math-track-g10-prereg.md`, frozen at commit
`9e45507`, unchanged. Raw output: `poc/results/g10.json`, `g10.log`,
`g10_report.md` (the scorer's output, `poc/g10_score.py`), one picture
per case (`poc/results/g10_*_checked.png`), and the web viewer rebuilt
from these states (`poc/results/damaged-gait-player.html`). Fourteen
cases run, thirteen scored, six steps, 1540 seconds on three workers,
scored against G9 as a reference (the same bodies on the old
teacher, so not like for like).

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **0 of 3, 1 of 3, 1 of 2** | **fail** |
| K4 growth generalises | mean held-out below V0's on `>= 7` of 9 | 8 of 9, both runs lower on 6 of 9 | pass |
| K2 consumers | none beyond tolerance on `>= 7` of 9 | 9 of 9 | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | 2 (stiff on the left weak hip, weak on the intact body) | pass |

K1 fails and K4 holds: **C**, the predicted letter.

## The round's claim: the states walk

Every fitted state moves at its teacher's speed from its own stride:
0.36 against 0.41 m/s on the left weak hip, 0.33 and 0.34 on the left
locked knee, 0.16 and 0.16 on the left stump (a kneel-step), 0.35 and
0.34 on the left one-leg body, 0.34 and 0.33 on the short shank, 0.25
and 0.24 on the right stump, 0.28 and 0.29 on the right one-leg body;
the intact body's fitted state is a little fast (0.46 against 0.42)
and the legless body's slow (0.18 against 0.44, see below). The
intact V0 has arms swinging 0.32 rad against the legs, hips 0.43 rad,
knees 1.0 rad, and reads as a walk in the viewer, which no earlier
teacher's fit did. The reported ground-speed figure (K5) counts any
part within two centimetres of the floor, and a striding swing foot
passes that low; it reads 0.3 to 0.5 m/s on the students and 0.17 to
0.31 on the teachers, and says nothing about the planted part, which
does not move by construction.

**The legless body did not grow.** Every candidate at step zero was
rejected by the held-out test or spent, so its terminal is V0, the
walk, on a body with no legs: fitting 0.666 and held-out 0.579
unchanged, the one damaged body K4 does not count. Its three
teachers crawl in three different ways (torso pitched 1.99, 1.11 and
1.07 rad), and no single repair from the walk lowered the mean of the
two runs that were not the fitting run. The G9 legless body took two
base refits under the old teacher; the new teacher's runs disagree
with each other more than the old one's did.

## Identity

The left locked knee names limp first (on the correct side) and
stiff second, so it is within two; the right locked knee names stiff
first after a rhythm refit. Neither stump names limp: the left,
whose teacher kneel-steps, takes rhythm, weak on the left and torso;
the right, whose teacher hops, takes four base refits and then stiff
and weak on the right. The legless body takes nothing. The
preregistration predicted the stumps' failure from the table (limp
was 8 percent on the wrong side at V0) and the locked knees' naming
after a lateral refit; the left knee's limp-before-stiff is the tie
G8 and G9 found breaking the other way. The short shank, which has
no designed class, names limp first on the correct side, its oracle
at V0 (32 percent): the one body whose teacher limps cleanly is named
by the class built for a limp.

Terminal fitting errors are below G9's on nine cases of thirteen
and the held-out means on six.

## What G10 establishes

1. The runtime now plays what the owner asked to see: a walk with
   swinging arms, a stiff-leg walk, a limp on the long leg, a
   kneel-step and a hop, each at its teacher's speed with the feet
   planted, from states of forty numbers. The teacher's gait prior
   is the reason, and the viewer is the check.
2. A prior in the teacher changes what the classes name. With a
   clean walk as the base, the short shank is a limp and is named
   one; the stump is a kneel-step or a hop, neither of which is the
   limp its designed class describes, and the two bodies that kept
   their names across every 3D round are the locked knees. The
   designed classes were carried over for comparability and the
   table said before the run which would fail.
3. The legless body under the new teacher is the first damaged body
   on which the growth rule admitted nothing: its three runs are
   three crawls. A body whose teacher has no consistent gait has
   nothing for a held-out rule to generalise, and that is the rule
   working, not failing.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
