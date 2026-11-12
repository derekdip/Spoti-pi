# ED2: ECS-Decision with sketched geometry on GPT-2. Results

Preregistration: `docs/math-track-ed2-prereg.md` (frozen at commit
4811504). One scored run: the planted cases on world seed 1
(`poc/results/ed2/ed2.json`, `run.log`), the real-data case on world
seed 2 (`real.json`, `real.log`); `report.md` from the frozen scorer
`poc/ecsdec/score2.py`.

**Outcome: C** by the frozen tree. F1 fails (4 of 5, the extend case
lost before its module stage); F2 holds (the rule's choice beats the
sweep's best module, at 6 fits against 13); F3 reported. The planted
cases took 50 minutes, the real-data case two hours.

Nothing in the rule, the thresholds, the cases or the scorer was
touched after the freeze; no incident during the run.

## F1, the planted cases (fails: 4 of 5, the extend case lost before its module stage)

| case | truth | got | D | D_held | s | first stage | budget gain | beam (held-out gain) | beam the matched-p score would give | fits |
|---|---|---|---|---|---|---|---|---|---|---|
| refine | REFINE | REFINE | 0.275 | 0.066 | 0.96 | REFINE | | | | 0 |
| saddle | GLOBALIZE | GLOBALIZE | 0.370 | 0.069 | 0 | GLOBALIZE | 0.999 | | | 2 |
| extend | EXPAND on `fc@7` | GLOBALIZE (miss) | 0.047 | 0.061 | 0.24 | GLOBALIZE | 0.151 | not reached | not reached | 2 |
| noise | FALLBACK | FALLBACK naming the base | 0.440 | 0.482 | 2.8e-3 | EXHAUSTED | 0.004 | `v@7 v@3 v@11` | `proj@3 fc@7 proj@7` | 6 |
| adequate | STOP | STOP | 0.008 | 0.029 | 0.070 | STOP | | | | 0 |

The extend miss is the student's construction, not the module
stage, which never ran. The prereg predicted the budget would find
nothing, as it had on the pilot world (0.0 percent); on the scored
world the two multistarts found a rank-2 fit on `v@7` with `F` 15
percent lower than the student's, above the frozen 10 percent, and
the rule said GLOBALIZE, which is the handoff's own Case 12 and the
right call when a better same-family point exists. The student was
a single 60-step fit. ED1 guarded this with students that were the
best of four fits, and its prereg named the risk; ED2 dropped the
restarts to save time and paid for it. What this says about the
rule is that "exhausted" is a property of the optimiser's budget,
not of the family: with budgeted Adam on a 124M-parameter model, a
single fit is not the family's best point to within 15 percent, and
the globalization stage then correctly refuses to expand.

The four cases that were right were right the way the prereg said:
refine by stationarity (0.96 against 0.5), the saddle by the budget
(99.9 percent), adequate by the bar (0.008 against 0.015), and
noise by the deployment objective after every stage ran: a positive
definite Hessian (the only one in either round), a budget gain of
0.4 percent, every held-out gain negative (-0.005 to -0.06), every
fitted module worse on held-out than the current (0.487 to 0.491
against 0.482) and the all-modules adapter worst (0.501), the base
better by 2 percent (0.470): FALLBACK naming the base. The matched-p
score's beam on that case (`proj@3`, `fc@7`, `proj@7`) and the
held-out gain's (`v@7`, `v@3`, `v@11`) share no module, both over a
residual that is noise; the equivalence stage collapsed nothing in
66 pairs under either rule.

## F2, the real-data case against the sweep (holds)

The rank-2 `v@7` adapter fitted on 1536 next-token targets from the
training documents: training `D` 0.962, held-out 0.990 against the
base's 0.991, held-out cross-entropy 6.115 against the base's 6.124.
Stationary (`s` 0.021), indefinite (`lambda_min` -23 against
`||H||` 74), the budget of two gains 0.3 percent, the sketched `tau`
0.001. Every candidate's linearised held-out gain is
zero or negative (`v@11` -0.000, `o@11` -0.002, `fc@11` -0.004, `o@3` -0.004, `v@7` -0.004, `proj@11` -0.005, `fc@3` -0.008, `v@3` -0.009, `proj@7` -0.016, `fc@7` -0.017, `proj@3` -0.021, `o@7` -0.022),
with training gains of 0.01 to 0.06. The beam by held-out gain,
`v@11`, `o@11`, `fc@11`; the matched-`p` score would have given
`o@11`, `v@3`, `proj@11`.

Every fitted module is worse on held-out than the current adapter,
and the sweep agrees:

| module | held-out `D` | `J` | in the beam |
|---|---|---|---|
| `o@3` (sweep best) | 1.0009 | 1.0015 |  |
| `proj@3` | 1.0086 | 1.0097 |  |
| `v@11` | 1.0147 | 1.0153 | yes |
| `v@7` | 1.0177 | 1.0183 |  |
| `o@11` | 1.0179 | 1.0185 | yes |
| `proj@7` | 1.0185 | 1.0196 |  |
| `proj@11` | 1.0207 | 1.0218 |  |
| `v@3` | 1.0213 | 1.0219 |  |
| `o@7` | 1.0245 | 1.0251 |  |
| `fc@11` | 1.0263 | 1.0273 | yes |
| `fc@3` | 1.0304 | 1.0315 |  |
| `fc@7` | 1.0359 | 1.0370 |  |
| all modules (reported) | 1.0276 | 1.0343 | |
| the base (the fallback) | 0.9906 | 0.9906 | |
| the current adapter | 0.9903 | 0.9906 | |

The rule returns FALLBACK naming the current (the base is not 1
percent better than it); its deployment objective, 0.9906, beats the
sweep's best module (`o@3`, 1.0015) by 1.1 percent. The sweep cannot
return this answer: it ranks modules and picks one, and every one of
them would have shipped a model worse than the one it started from.
The rule spent 6 fits (2 budget, 3 beam, 1 all-modules) to the
sweep's 13, and the first-order held-out gains had said, before any
fit, that no module would help: the only positive numbers in the
candidate stage were the training gains, the mimicry measured at
first order.

## F3, reported

- noise: tau_sketch 0.000; held-out gain / train gain / eta p12 per module: v@7 -0.005/0.007/0.000, v@3 -0.024/0.006/0.000, v@11 -0.025/0.011/0.000, fc@11 -0.027/0.027/0.000, o@11 -0.027/0.015/0.000, o@7 -0.037/0.008/0.000, proj@11 -0.041/0.019/0.000, o@3 -0.041/0.008/0.000, fc@3 -0.043/0.014/0.000, proj@3 -0.051/0.009/0.000, fc@7 -0.060/0.025/0.000, proj@7 -0.062/0.015/0.000; collapsed []; matched-p collapses 0 of 66
- real: tau_sketch 0.001; held-out gain / train gain / eta p12 per module: v@11 -0.000/0.012/0.001, o@11 -0.002/0.013/0.001, fc@11 -0.004/0.033/0.001, o@3 -0.004/0.024/0.001, v@7 -0.004/0.012/0.000, proj@11 -0.005/0.016/0.001, fc@3 -0.008/0.044/0.000, v@3 -0.009/0.019/0.001, proj@7 -0.016/0.034/0.000, fc@7 -0.017/0.061/0.000, proj@3 -0.021/0.036/0.001, o@7 -0.022/0.032/0.000; collapsed []; matched-p collapses 0 of 66
- noise fits: v@7 held 0.4873 J 0.4879, v@3 held 0.4914 J 0.4920, v@11 held 0.4908 J 0.4914, all_modules held 0.5012 J 0.5080, base held 0.4704 J 0.4704; J_current 0.4819
- real fits: v@11 held 1.0147 J 1.0153, o@11 held 1.0179 J 1.0185, fc@11 held 1.0263 J 1.0273, all_modules held 1.0276 J 1.0343, base held 0.9906 J 0.9906; J_current 0.9906

The matched-`p` equivalence rule collapsed nothing in 66 pairs on
either exhausted case, as the containment rule did; GPT-2's twelve
heads leave no first-order coincidence between modules. The sketched
`tau` was 0.0 on noise and 0.001 on the real case: the current
adapter's tangent carries almost none of either residual.

## What it says

The first stage transfers. On a real pretrained model with every
quantity estimated by products, stationarity, the saddle, adequacy
and a residual that is noise were called as on the toy, and the
noise case ran every stage to the right end: a positive definite
Hessian, a budget that finds nothing, negative held-out gains
everywhere, every fitted module worse than the current, the base
better by 2 percent, FALLBACK naming the base.

The extend miss says what "exhausted" means at this size: a single
60-step fit is not the family's best point to within 15 percent,
two restarts find a better one, and the rule then refuses to expand,
which is the handoff's Case 12 and the right refusal. The prereg
named the opposite prediction from a pilot world where the budget
found nothing; the construction should have used best-of-restarts
students as ED1 did, and the cost it saved was paid in the letter.
On an LLM, "restart before adding modules" is the rule's first
practical instruction, and it is cheap.

The candidate stage does not find modules from training geometry on
a model this size, and ED2 measured why: with a few hundred
contexts, a rank-2 adapter on any module removes 65 to 88 percent of
the training residual at first order and the right module is not
distinguishable among them. The held-out linearised gain, the
preregistered variant, separated modules on the pilot's extend case
(the planted module third of twelve, where the handoff's score had
it eighth) and on the scored real-data case said correctly that none
would help. The claim that it finds the right module stays at pilot
strength: the scored extend case never reached it.

On real data at this scale the rule's value is a stopping decision.
It kept the adapter it had, every module in a thirteen-fit sweep
would have made the held-out model worse, and the first-order gains
had said so before a fit was run. A round at a data scale where some
module actually helps, with best-of-restarts students and the
held-out gain against a full sweep, is the test that would turn the
pilot's module-finding into a result.
