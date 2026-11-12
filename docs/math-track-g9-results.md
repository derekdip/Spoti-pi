# G9 results: outcome C, as predicted. Planted grounding takes the sliding out of every fitted state, speed becomes what the stride produces, growth generalises as before, and the classes, coupled through the stride, name less than they did

Preregistration: `docs/math-track-g9-prereg.md`, frozen at commit
`d4be367`, unchanged. Raw output: `poc/results/g9.json`, `g9.log`,
`g9_report.md` (the scorer's output, `poc/g9_score.py`), one picture
per case (`poc/results/g9_*_checked.png`), and the rebuilt web viewer
(`poc/results/damaged-gait-player.html`). Fourteen cases run,
thirteen scored, six steps, 834 seconds on three workers, scored
against G7 on the same teachers.

Two defects in the frozen scorer, named and fixed after the run with
the bars untouched: a numpy import inside the K5 block shadowed the
module's and stopped the script before any output, and the default
input path still named G8's file. The run was scored by giving the
path. One misreading in the frozen preregistration: it says the
legless body's vault was under a percent at V0; the table it cites
puts vault at 7 percent there.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| K1 identity | first `>= 2` of 3, within two 3 of 3, mirrors 2 of 2 | **1 of 3, 1 of 3, 0 of 2** (G7: 2, 2, 1) | **fail** |
| K4 growth generalises | mean held-out below V0's on `>= 7` of 9 | 9 of 9, both runs lower on 9 of 9 | pass |
| K2 consumers | none beyond tolerance on `>= 7` of 9 | 8 of 9 (the left one-leg body's contact timing) | pass |
| K3 controls | `<= 4` impairment repairs on the four controls | 2 (limp on the left weak hip, hold on the intact body's second run) | pass |

K1 fails and K4 holds: **C**, the predicted letter.

## The round's claim: no sliding, and the speed from the stride

Every terminal state's forward speed is now what its legs, or the
legless body's arms, produce, and it matches the teacher's on every
body: 0.37 against 0.36 m/s on the intact body, 0.38 and 0.38 on the
left weak hip, 0.45 and 0.44 on the left short shank, 0.49 and 0.50
on the left stump, 0.40 and 0.37 on the legless body, 0.29 and 0.30
on the right one-leg body; the widest gap is the right stump, 0.32
against 0.41. In G7 the same numbers were a free parameter and the
feet skated; under planting the G7 intact state moved at 0.003 m/s.

The reported ground speed of parts within two centimetres of the
floor (K5): on the walking bodies the fitted states read 0.02 to 0.08
m/s where the physics teachers read 0.16 to 0.32, because the
teachers shuffle with the swing foot dragging low and the metric
counts it. On the hopping bodies (the stumps, the one-leg bodies) the
fitted states read 0.23 to 0.52: a hop's foot passes low over the
floor between landings and the metric counts that too; nothing
planted moves, by construction. The web viewer is the check that
matters, and there the bodies now step and hop where before they
slid.

## Identity

The left locked knee names stiff first, at step zero, as in G7. The
right locked knee names limp on the correct side after a legs refit:
the two classes were tied at V0 on the left body and the tie broke
the other way on the right. Neither stump takes an impairment class
at all: five base refits each, with limp and vault (31 and 33 percent
at V0 on the left stump, near-tied) rejected by the held-out test or
spent once the torso and legs had refitted. The legless body takes
arms and rhythm. Two controls take a class (limp on the left weak
hip, hold on the intact body's second run) where G7's took none.

This is what the exclusivity table on the planted grammar said before
the run: eight pairs over a half where the G7 grammar had none,
because every parameter that changes the stride now changes the speed
and the contact blocks, and the classes overlap through them. The
terminal errors are better than G7's on six cases of thirteen (both
stumps by a clear margin, 0.250 against 0.274 and 0.265 against
0.317) and worse on the locked knees and the legless body.

## What G9 establishes

1. The grounding was the defect a viewer saw, and it is a grammar
   matter: with the part on the floor planted, the fitted states do
   not slide and their speed is their stride's, matched to the
   teacher's on every body with no speed parameter. Nothing about the
   growth rule changed and it generalised exactly as before.
2. Consumers score what they measure. No block measured foot slip, so
   three rounds of growth in 3D fitted states that slid, at errors
   that looked fine. The web viewer found it in one look. A runtime
   defect that the consumers cannot see is a missing consumer or a
   missing constraint, and here the constraint was the right fix.
3. Planting couples the classes: identity, already order-dependent
   (G8), is weaker still when every leg parameter also sets the
   speed. A grammar whose classes separate under planting is a design
   question for the next round, and the exclusivity table on the
   planted grammar is the tool to design it with.

No rescue, no second run on the scored cases. Nothing above is edited
after the run.
