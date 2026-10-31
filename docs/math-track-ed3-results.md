# ED3: where to put an adapter. Results

Preregistration: `docs/math-track-ed3-prereg.md` (frozen at commit
8c20d99). One scored run on world seed 1, both cases in one process
(`poc/results/ed3/ed3.json`, `run.log`); `report.md` from the frozen
scorer `poc/ecsdec/score3.py`.

**Outcome: A** by the frozen tree. G1 holds (the rule returns EXPAND
on the planted module, first of twelve by its score), G2 holds (on
the format shift the rule's beam reaches the full sweep's best at 6
fits against 13, ahead of the handoff's score, of Auto-RGN and of
random placement); G3 reported. The run took 4.2 hours.

Nothing in the rule, the thresholds, the transform, the cases or the
scorer was touched after the freeze; no incident during the run. The
extend case took two hours, the format case two and a quarter; the
candidate stage (twelve modules, three scores each) was 72 and 81
minutes of that, the sweep's extra nine fits about 25.

## G1, the planted module (holds)

The teacher (rank 2 on `fc@7`, fitted on the format targets, doubled)
moved the state by 0.73 on the training probes and 0.69 on the
held-out probes. The best-of-3 student on `v@7` reached `D` 0.63
(held-out 0.59), stationary at `s` 0.23, with no restart beating the
first fit; the budget of two lowered `F` by 0.6 percent. The three
selectors then disagreed:

| selector | beam | best held-out distortion among its fits |
|---|---|---|
| held-out gain (the rule's) | `fc@7`, `fc@11`, `proj@7` | 0.318 (`fc@7`) |
| matched-`p` (the handoff's) | `proj@11`, `o@7`, `v@11` | 0.428 |
| Auto-RGN | `v@3`, `o@3`, `v@11` | 0.445 |
| random, one draw | | 0.417 |
| random, expected over draws of three | | 0.391 |
| the full sweep | all twelve | 0.318 (`fc@7`) |
| the all-modules adapter (reported) | | 0.284 |
| the current | | 0.594 |

The held-out gain ranked the planted module first of twelve (0.41
against 0.36 for the next), the rule fitted it and returned EXPAND on
`fc@7`, and its beam's best equals the sweep's. The handoff's score
and Auto-RGN both ranked it outside their beams, and their beams did
worse than random placement's expectation. The first-order held-out
gain correlated with the fitted held-out gain across the twelve
modules at Pearson 0.69 and Spearman 0.59. One number outside the
bars: the all-modules adapter (rank 2 on all twelve, 55k parameters)
beat the single best module on held-out, 0.284 against 0.318, at
twice the parameters of the fallback this rule does not use for its
decision.

## G2, the format shift (holds)

The best-of-3 student (rank 2 on `v@7`) on the alternating-caps
targets: held-out cross-entropy 6.425 against the base's 6.585,
stationary (`s` 0.037), indefinite (`lambda_min` -3.4 against
`||H||` 14.9), the budget of two gains 0.0 percent, the sketched
`tau` 0.002. Every module's first-order held-out gain is small and
positive (0.0005 to 0.0094); the held-out gain's beam is `fc@11`,
`fc@7`, `proj@7`; the matched-`p` score's would be `proj@11`, `o@7`,
`v@7`; Auto-RGN's `v@3`, `o@3`, `v@7`.

| selector | beam | best held-out cross-entropy among its fits (`J`) |
|---|---|---|
| held-out gain (the rule's) | fc@11 fc@7 proj@7 | 6.080 (`fc@11`) |
| matched-`p` (the handoff's) | proj@11 o@7 v@7 | 6.170 |
| Auto-RGN | v@3 o@3 v@7 | 6.234 |
| random, one draw | o@3 v@3 o@7 | 6.234 |
| random, expected over draws of three | | 6.172 |
| the full sweep | all twelve | 6.080 (`fc@11`) |
| the all-modules adapter (reported) | | 6.499 |
| the base | | 6.585 |
| the current | | 6.425 |

The rule returned EXPAND on `fc@11`, the sweep's best module, with
`J` 6.080 against the current's 6.425: a gain of 0.35 nats on
held-out cross-entropy from a rank-2 adapter on one module, where the
base-to-current adapter had gained 0.16. The sweep in full:
`fc@11` 6.080, `proj@11` 6.170, `o@11` 6.182, `fc@3` 6.206, `v@11` 6.213, `v@3` 6.234, `o@3` 6.256, `fc@7` 6.268, `proj@7` 6.337, `v@7` 6.350, `proj@3` 6.369, `o@7` 6.463. The beam
beat the handoff's score by 0.09 nats, Auto-RGN by 0.15, random
placement's expectation by 0.09 and a random draw by 0.15, and it
cost 6 fits (2 budget, 3 beam, 1 all-modules) against the sweep's
13. The all-modules adapter overfitted here (6.499, worse than nine
single modules), the opposite of the planted case where it was best:
55k parameters on 1536 targets memorise, 3072 on one module do not.

## G3, reported

- extend: first-order held-out gain against the fitted held-out distortion gain, Pearson 0.69, Spearman 0.59; per module (predicted / fitted distortion gain): fc@7 +0.411/+0.466, fc@11 +0.364/+0.311, proj@7 +0.351/+0.327, proj@11 +0.283/+0.240, o@7 +0.275/+0.280, o@11 +0.275/+0.242, v@11 +0.261/+0.232, proj@3 +0.224/+0.296, o@3 +0.212/+0.251, v@7 +0.198/+0.208, fc@3 +0.164/+0.300, v@3 +0.140/+0.240
- extend: D 0.6295 D_held 0.5936 s 2.27e-01 first stage GLOBALIZE tau_sketch 0.038 fits 15; sweep (J): fc@7 0.3182, proj@7 0.4006, fc@11 0.4103, fc@3 0.4169, proj@3 0.4192, o@7 0.4278, o@3 0.4451, o@11 0.4506, v@3 0.4519, proj@11 0.4524, v@11 0.4567, v@7 0.4707
- real: first-order held-out gain against the fitted held-out distortion gain, Pearson 0.74, Spearman 0.70, against the fitted cross-entropy gain Pearson 0.41, Spearman 0.22; per module (predicted / fitted distortion gain / fitted cross-entropy gain): fc@11 +0.009/+0.007/+0.346, fc@7 +0.009/+0.003/+0.158, proj@7 +0.005/+0.003/+0.089, o@7 +0.005/+0.000/-0.037, o@3 +0.005/+0.002/+0.170, proj@11 +0.004/+0.003/+0.256, o@11 +0.004/+0.002/+0.243, fc@3 +0.004/+0.002/+0.220, v@3 +0.003/+0.002/+0.191, v@11 +0.003/+0.002/+0.212, v@7 +0.002/+0.001/+0.076, proj@3 +0.001/+0.001/+0.057
- real: D 0.9986 D_held 0.9992 s 3.73e-02 first stage GLOBALIZE tau_sketch 0.002 fits 15; sweep (J): fc@11 6.0800, proj@11 6.1702, o@11 6.1824, fc@3 6.2059, v@11 6.2135, v@3 6.2345, o@3 6.2561, fc@7 6.2678, proj@7 6.3373, v@7 6.3501, proj@3 6.3688, o@7 6.4626

Two readings of the predictor. On the planted case it tracks the
fitted distortion gain (Pearson 0.69, Spearman 0.59) and puts the
winner first by a clear margin (0.41 against 0.36). On the format
case it tracks the fitted distortion gain as well (0.74, 0.70) but
the fitted cross-entropy gain only weakly (0.41, 0.22): it predicts
the Brier residual on the support, and the deployment objective is
cross-entropy on the full vocabulary. The beam held because the
module it put first was first on both; its second and third
(`fc@7`, `proj@7`) were eighth and ninth on cross-entropy. The
margin by which G2 held is the top pick, not the ranking.

Auto-RGN ranked the early attention modules first (`v@3` 0.18,
`o@3` 0.12) on both cases, a sensitivity order that did not match
the fitted order on either; the equivalence stage collapsed nothing
in 66 pairs on either case; no restart beat the first fit in either
case (0 of 2, 0 of 2); the first stage read GLOBALIZE on both, as
in ED2, with the budget finding 0.6 and 0.0 percent.

## What it says

The question ED2 left open is answered on this model, at this scale,
on one shift. A first-order estimate of a module's held-out gain, at
a third of a fit's cost per module, picked the planted module first
of twelve and, on a real format shift, the module the full sweep
would have picked, at less than half the sweep's fits. The two
standard single-run selectors (the handoff's principal-subspace
score and the literature's validation-gradient norm) picked wrong
modules on both cases and did no better than random placement,
which is the finding the literature's negative results asked
placement claims to be checked against. The rule's whole chain ran
as frozen: stationarity, curvature, the budget, the beam, the base
as the fallback, the deployment objective.

Three qualifications belong with that. The predictor's ranking
beyond its top pick is weak against cross-entropy, because it
predicts a Brier residual on a support; a first-order cross-entropy
gain (a Gauss-Newton step on the log-loss) is the natural next
instrument, and the pilot's single-module scan suggests the order it
would have to reproduce. The placement effect here is large (0.43
nats across modules) because the shift is a rule GPT-2 does not know;
on ED2's plain next-token data no module helped and the same rule
said so. And twelve modules at rank 2 on one 124M model is one point;
the literature's 3B result where placement was not load-bearing is
the other, and which regime a given fine-tune is in is itself what
the held-out gains report before any fit.

What this gives the LLM use case, in order of evidence: a cheap
pre-screen for where to put an adapter that found the sweep's answer
here and beats the standard shortcuts; a cheap sign that fine-tuning
will help or hurt (all gains positive here, all negative in ED2) that
agreed with the fits both times; and the restart-before-expand rule
from ED2, which cost nothing here because the best-of-3 students
were already at the family's best.
