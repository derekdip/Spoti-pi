# ED1: ECS-Decision v1 on a model with adapters. Results

Preregistration: `docs/math-track-ed1-prereg.md` (frozen at commit
2dd0e35). One scored run on world seed 1, seven arms as separate
processes, `poc/results/ed1/` (per-arm JSON and logs, `ed1.json`,
`per_case_metrics.csv`, `equivalence_summary.csv`, `sweeps.csv`,
`report.md` from the frozen scorer `poc/ecsdec/score.py`).

**Outcome: A** by the frozen tree. E1, E2 and E3 hold; E4 reported.
Every prediction in the prereg held, including the two that
predicted failures (the handoff's matched-`p` equivalence rule on
its own Case 8, and the adequate case at the highest noise).

Defects and incidents after the freeze, none of which changed a
number: nothing in the rule, the thresholds, the cases or the scorer
was touched. (1) The seven arms launched together ran four-fold
oversubscribed (XLA sizes its worker pool from the cores visible at
start and ignores the single-thread flag in `model.py`; each process
had 33 threads, 4 runnable), so an exhausted case took 20 minutes
instead of 3; the A and sweeps arms were killed and relaunched
unchanged under `taskset`, the killed logs are kept beside the final
ones (`arm_A_killed.log`, `arm_sweeps_killed.log`) and every verdict
and diagnostic the killed runs had logged recurs to the printed
digit in the relaunched runs. (2) The D arm was killed by the memory
cgroup during its first case (`arm_D_killed.log`) and relaunched
unchanged once the load dropped. (3) A watcher fired a second time
after D finished and started a duplicate D, which was killed in its
base training; the finished D's result is the one scored. The B, C,
E and full arms ran oversubscribed to the end (6100 to 6600 s
against 1365 to 1645 s for the single-threaded D and A).

## E1, actions (holds, 8 of 8)

| case | truth | full rule | first stage | what decided |
|---|---|---|---|---|
| refine_early | REFINE | REFINE | REFINE | `D` 0.236, `s` 0.14, `kappa` 1.2e5 |
| refine_mid | REFINE | REFINE | REFINE | `D` 0.300, `s` 0.13, `kappa` 2.2e4 |
| saddle | GLOBALIZE | GLOBALIZE | GLOBALIZE | `s = 0`, `lambda_min = -||H||`; the budget lowers `F` by 100 percent |
| reuse | EXPAND on `wv@0` | EXPAND on `wv@0` | GLOBALIZE | budget gains nothing; `wo@0` and `wo@1` collapse; beam `wv@0`, `wv@1`, `out_bias`; `wv@0` held-out 0.007, `J` 0.010 against the fallback's 0.042 and the current's 0.199 |
| collinear | REPARAMETERIZE | REPARAMETERIZE | REPARAMETERIZE | `s` 0.097, `kappa` 9.6e7 |
| extend | EXPAND on `w2@1` | EXPAND on `w2@1` | GLOBALIZE | beam `w1@1`, `out_bias`, `w2@1`; `w2@1` held-out 0.024, `J` 0.029 against `w1@1` 0.202, the fallback's 0.068 and the current's 0.247 |
| noise | FALLBACK | FALLBACK (current) | GLOBALIZE | budget 0.04 percent; every fit worse on held-out (0.47 to 0.57 against 0.47) |
| adequate | STOP | STOP | STOP | `D` 0.006 |

Two things the table does not say. The first-order proposal score
is a weak ranker here: on extend the planted module came third in
the beam by `eta` at `p = 12` (`w1@1` 0.08, `out_bias` 0.03, `w2@1`
0.03, the next candidate 0.02), and on reuse the collapsed `wo@0`
scored a hundredth above the kept `wv@0`. The beam of 3 held the
planted module both times; a beam of 2 would have lost the extend
case. The full fit, not the proposal score, decided every EXPAND,
and the deployment objective's size term never changed an order
(every winning candidate also won on held-out distortion alone).
Second, every student fitted to the budget has `lambda_min < 0`
(the pilot said so), so the first stage read GLOBALIZE on every
exhausted case and the bounded budget did the work the curvature
test could not: it found nothing better on reuse, extend and noise
and everything on the saddle. The curvature test is therefore not
what separates the saddle from exhaustion in this setting; the
budget is.

## E2, equivalence (holds)

| pair | truth | frozen rule (containment) | matched-`p` rule | containment | atoms | `mu`/`d` at `p` 1, 3, 12 |
|---|---|---|---|---|---|---|
| `wv@1` against `wo@1` | COLLAPSE | COLLAPSE | KEEP DISTINCT | 1.000/1.000 | 1.000 | 0.65/0.76, 0.84/0.93, 0.93/1.00 |
| `wv@0` against `w2@1` | KEEP DISTINCT | KEEP DISTINCT | KEEP DISTINCT | 0.802/0.555 | 0.933 | 0.75/0.66, 0.80/0.99, 0.87/1.00 |

The same verdicts in every arm. The pair that spans one space by
construction has principal directions a projector distance of 0.76
apart at `p = 1`: the handoff's section 12, with the editorial's
tolerances, reads the parameterisation (`Wo` and `Wv` weigh the
directions differently) and fails Case 8, as the pilot predicted.
Section 11's directed containment on the full spans is the test
that holds.

## E3, the layers earn their place (holds)

| ablation | misses among the cases the full rule gets right |
|---|---|
| A, magnitude only | refine_early, refine_mid, saddle (all EXPAND), collinear (EXPAND) |
| B, gradient only | saddle (EXPAND), collinear (REFINE) |
| C, no conditioning | collinear (REFINE) |
| D, no tangent quotient | none: 8 of 8 agree with the full rule |
| E, no equivalence | none in action; 2 redundant fits (`wo@0` beside `wv@0` on reuse and on noise) against 0 |

Exactly the predicted set. D's agreement is the prediction too:
`tau` is 0.00 to 0.08 on every exhausted student, so projecting off
the current tangent removes almost nothing and the quotient is
untested by these cases rather than useless.

## E4, reported

- **Misspecification, 5 of 5.** The extend defect at 0.01, 0.03 and
  0.1 of the scale leaves the fitted student at `D` 0.003, 0.009 and
  0.030, under `D_max`, and the rule says STOP; at 0.3 and 1 (`D`
  0.088 and 0.265) it says EXPAND on `w2@1`. The deployment bar
  decides where detectable structure becomes worth a syntax.
- **Noise.** Fifteen of sixteen actions hold across noise at 0,
  0.01, 0.05 and 0.1 of the rms: REFINE, EXPAND on `wv@0`, EXPAND on
  `w2@1` at every level, STOP for the adequate case up to 0.05
  (`D` 0.049 against the bar 0.05). At 0.1 the adequate case has
  `D` 0.097: inadequate, stationary (`s` 1e-3), the budget finds
  nothing, no candidate improves held-out, FALLBACK naming the
  current. That is the rule reading unfittable noise as "nothing
  to add" rather than STOP, which the prereg predicted and which is
  the right deployment call once the noise exceeds the bar.
- **Cost.** 0 fits for the first-stage verdicts, 8 for a GLOBALIZE,
  12 for an EXPAND or FALLBACK (8 budget, 3 beam, 1 fallback); the
  equivalence stage saved 2 fits across the suite.
- **Fallback.** The all-modules fallback generalises (held-out 0.023
  on reuse, 0.048 on extend) and loses to the right single syntax
  on distortion before any size term; on noise it overfits worst
  (0.57).

## What it says

The handoff's rule, run unchanged in structure on a model with
adapters, returns the right action on all eight constructed cases,
tells the equivalent syntaxes from the distinct ones, and each
removed layer costs the cases it was meant for. Three of the
handoff's proposals did not survive contact with the model and were
replaced before the freeze with the reason recorded: the literal
`sigma_min` (a LoRA pair has an exact gauge), the optimiser-precision
`eps_g` (a budgeted Adam iterate is stationary to 1e-2 at best), and
the matched-`p` equivalence tolerances (metric-dependent; the
containment test is the one that reads the span). Two findings
belong in the next round's design: the first-order proposal score
discriminates weakly on this model and the beam width carried the
EXPAND cases; and with every fitted student indefinite, GLOBALIZE
versus exhausted is decided by the bounded budget, not the Hessian.
The construction-time defects the pilot caught (two heads break the
Case 8 equivalence, dense candidate fits overfit, a frozen current
adapter cannot reach the target) are in the prereg, not here.
