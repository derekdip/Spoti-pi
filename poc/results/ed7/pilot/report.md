# The trade: the rule on all n against held-out splits

Test gain in nats on the condition's test contexts; held-out arms averaged over their folds. `extra_val` stops at the minimum on 32 extra contexts and `peak` is the best the full fit reached; neither is available in the use case.

| condition | matrix | g* | rule | hold25 | hold25+refit@step | hold25+refit@gain | hold12 | hold12+refit@step | hold12+refit@gain | extra_val | peak |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pilot-none-8 | transformer.h.2.mlp.c_proj | 1.53 | +0.234 | +0.309 | +0.309 | +0.276 | +0.278 | +0.259 | +0.207 | +0.322 | +0.322 |
| pilot-none-8 | transformer.h.8.attn.c_proj | 1.53 | +0.455 | +0.406 | +0.455 | +0.476 | +0.454 | +0.472 | +0.479 | +0.490 | +0.490 |

| arm | mean test gain | rule minus arm: mean | fits where the rule is ahead |
|---|---|---|---|
| rule | +0.344 | +0.000 | 0 of 2 |
| hold25 | +0.358 | -0.013 | 1 of 2 |
| hold25+refit@step | +0.382 | -0.038 | 0 of 2 |
| hold25+refit@gain | +0.376 | -0.031 | 0 of 2 |
| hold12 | +0.366 | -0.022 | 1 of 2 |
| hold12+refit@step | +0.365 | -0.021 | 0 of 2 |
| hold12+refit@gain | +0.343 | +0.001 | 1 of 2 |
| extra_val | +0.406 | -0.062 | 0 of 2 |
| peak | +0.406 | -0.062 | 0 of 2 |

By condition, rule minus arm (mean over matrices):

| condition | hold25 | hold25+refit@step | hold25+refit@gain | hold12 | hold12+refit@step | hold12+refit@gain |
|---|---|---|---|---|---|---|
| pilot-none-8 | -0.013 | -0.038 | -0.031 | -0.022 | -0.021 | +0.001 |
