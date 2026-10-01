# RGRE-ML-1 results: outcome A. RGRE is matching pursuit plus an out-of-vocabulary detector plus a sequencing protocol, and the consumer residual is for scoring, not diagnosis

Preregistration: `docs/math-track-rgre-ml1-prereg.md`, frozen at commit
`8ca0e0d`, unchanged. Raw output: `poc/results/rgre_ml1_seed{101,102,103}.json`,
`.log`, `rgre_ml1_report.md` (the frozen scorer's output,
`poc/rgre_ml/score.py`, committed before the seeds ran). Three fresh
seeds, 114 cases, about six seconds each.

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| B1 abstention as a quantity | AUC of `q_perp` on the field residual `>= 0.90` | **0.964** (per seed 0.99, 0.88, 1.00) | pass |
| B2 sequencing | median two-step recovery, field residual `>= 0.85` | **1.000** (0.98, 1.00, 1.00) | pass |
| B3 field beats consumer for diagnosis | identity and AUC both higher | identity **0.85 vs 0.46**; AUC **0.96 vs 0.80** | pass |
| B4 selection value (= matching pursuit) | median `>= 0.90`, above three baselines | median 1.00, mean 0.83; random 0.16/0.31, cheapest 0.13/0.27, gradient-norm 0.97/0.68 | pass |
| B5 the borrowed threshold | oov `>= 80%`, known `<= 10%` | 67%, 27% | **fail, as predicted** |
| B6 controls decline | `>= 75%` | 83% | pass |
| B7 orthogonal deferral | beats magnitude on `>= 60%` of oov cases | **8%** | **fail, as predicted** |
| B8 search | `<= 1/3` of candidates evaluated | 0.10 | pass |

The tree is exclusive on B1 and B2, both hold, so the letter is **A**:
in this setting RGRE is matching pursuit plus a working
out-of-vocabulary detector plus a working multi-step protocol, and the
consumer residual is for scoring rather than diagnosis. Seed 102 alone
sits at 0.88 on B1, below the bar; the pooled value passes and the
per-seed spread is reported rather than smoothed.

## What each bar means

**The consumer-space residual halves the diagnosis.** Identity, the
share of isolated cases where the pick is the missing module, is 0.85
on the field residual and 0.46 on the consumer residual; the
out-of-vocabulary separability is 0.96 against 0.80. This is the
surprise of the experiment, because the consumer-space residual is
what the whole simulation arc used, on the argument that a defect is
defined by what reads the field. That argument is right for *scoring*
and this run says it is wrong for *diagnosing*: a thresholded consumer
turns a smooth residual into a spiky indicator that no smooth tangent
direction correlates with, and a coarse consumer is low-rank. The
simulation consumers were mostly smooth fields, which is likely why
selection still reached full value there; here one of three consumers
is a binary decision and it is enough to halve the identity. The
general statement is narrower than "consumer space is bad": thresholded
consumers degrade the residual as a diagnostic signal.

**The abstention signal works and the constant does not.** `q_perp` on
the field residual separates out-of-vocabulary teachers from in-
vocabulary ones at AUC 0.96. RGRE-1's threshold of 0.583, carried over
unchanged, abstains on 67 percent of the former and 27 percent of the
latter. That is the third domain in which a borrowed constant has
failed and the quantity under it has held, and it is the same finding
as fire's F1: recalibrate per domain, never transfer the number.

**Sequencing holds.** With abstention off and the spent-repair
blacklist on, the two-missing cases recover the full two-step oracle
in median, finding 1.4 of the 2 missing modules on average. On the
consumer residual the same protocol recovers 0.89 median with a
per-seed low of 0.66.

**Selection value is matching pursuit's, by construction.** RGRE's
per-direction projection on the field residual and matching pursuit's
atom selection agree on every one of 114 cases, as the preregistration
said they would. The bar passes; it is not a win over MP and is not
reported as one. Gradient-norm selection, the unnormalised version, is
nearly as good on median (0.97) and worse on mean (0.68), because it is
biased toward the classes with the largest tangents.

**Controls decline.** 83 percent of nothing-missing cases produced no
growth, by the one percent dead-repair rule or by abstention.

## The deferral test was not a test

B7 asked whether deferring the regions whose residual no single class
can explain beats deferring the regions with the largest residual. It
fails: 8 percent, worse than a coin flip, with the three deferral
criteria within 0.03 of each other and of random. It was predicted to
fail on the pilot's evidence, and the reason is a defect of the frozen
case design rather than a falsification. The claim needs a case in
which large-but-explainable residual and small-but-unexplainable
residual coexist, so that growth fixes one and deferral must catch the
other. The out-of-vocabulary cases here have nothing missing from the
dictionary part, so their whole residual is unexplainable and magnitude
and orthogonality rank the same regions; the isolated cases have
nothing unexplainable, so orthogonality is noise. Neither kind can
distinguish the hypothesis. It is unmeasured, not refuted, and a mixed
case (one missing module plus one foreign term) is what would measure
it. This is a defect in a frozen design, named as the earlier ones
were.

## What RGRE-ML-1 establishes

1. For growing a structured model toward a teacher, RGRE's selection
   is matching pursuit and should be called that. Its contribution is
   what MP lacks: an out-of-vocabulary signal (AUC 0.96) and a
   sequencing protocol (1.00 two-step recovery), both validated on 114
   fresh cases.
2. Diagnose on the field residual; score on the consumers. Using the
   consumer residual for diagnosis halves the identification rate when
   a consumer is thresholded.
3. No threshold transfers across domains. The quantity does.
4. "Defer where the residual is unexplainable" is untested by this
   design and needs mixed cases.

No rescue, no second run on the fresh seeds. Nothing above is edited
after the run.
