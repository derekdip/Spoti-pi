# RGRE-ML-1: residual-guided expansion as a model-growing and deferral procedure. Preregistration (frozen before any fresh seed is run)

RGRE was validated on corn, water and fire as a way to choose which part
of a cheap representation to expand next, given an expensive teacher.
Stated without the simulations, it is a procedure for growing a small
structured model toward a big one and for knowing when the small model's
vocabulary cannot explain what it is seeing. That is a machine-learning
question, and this is the first test of it as one.

## What is being tested, and an identity stated up front

The student is a generalised additive model over a dictionary of ten
candidate modules (`poc/rgre_ml/dictionary.py`): linear, quadratic,
pairwise, cubic, two sinusoids, a Gaussian bump, a sigmoid step, an
absolute value and an exponential. Each has parameters, a cost equal to
its parameter count, and for gated modules a canonical on-state, exactly
as the fire's classes did. The teacher is a function composed from a
subset of the same dictionary, sometimes plus a term the dictionary
cannot express. The student starts with every module the teacher has
except one or two, at the teacher's own values, and the question is
which module to add.

This is the setting RGRE is honest about. Its selection rule projects
the residual onto candidate directions, which means something only when
a candidate has a direction before it is fitted; for a randomly
initialised neural block it does not, and RGRE would reduce to trying
each one, which is the oracle. So the claim is about structured models:
additive models, feature dictionaries, symbolic terms, fixed experts.

**The identity.** RGRE's selection rule applied to the field residual
ranks candidates by the squared cosine between the residual and each
tangent direction, which is exactly the atom-selection rule of matching
pursuit. The pilot confirms it: the two agree on every case. So RGRE's
selection is not a contribution over matching pursuit here, and B4
below must not be read as one. What RGRE adds is three things, and they
are what this experiment tests: a residual taken in the space of the
*consumers* rather than the field; an abstention signal, the fraction
of residual energy orthogonal to every candidate direction; and a
multi-step protocol with a blacklist for repairs that do nothing.

Diagnosis and selection are `poc/rgre/core.py`, unchanged from the
three simulation domains.

## The declared pilot, and what it changed

One dev seed (seed 1, 38 cases) was run before this document was
written and is excluded from every bar. It found five defects in the
testbed, each fixed before the freeze:

1. The oracle was refitting modules the student already had, absorbing
   residual by miscalibrating them; a third of its picks were
   compensation. **Candidates are now the off modules only.**
2. Value per parameter count let two-parameter modules beat the true
   six-parameter one. **The oracle and identity are by raw error
   reduction; per-cost value is reported alongside.**
3. RGRE-1's abstention threshold, carried over verbatim, abstained on
   31 percent of known cases and only 62 percent of out-of-vocabulary
   ones. It is kept as the transfer test it is (B5), and the abstention
   *quantity* is scored by separability (B1).
4. Per-cell orthogonality with local subspaces was degenerate: any
   six-parameter family explains 32 points. **A global-projection
   version was added** and both are reported.
5. Controls with nothing missing grew on noise. **A pick whose fitted
   gain is under one percent is declined**, the DEAD rule every fire
   run used.

The pilot then gave, on the same seed: value captured 1.00 with
abstention off on either residual; identity 0.61 on the consumer
residual against 0.78 on the field residual; out-of-vocabulary
separability by `q_perp` 0.82 on the consumer residual against 0.99 on
the field residual; two-step recovery 0.89 on the consumer residual
against 1.00 on the field residual; controls declined 100 percent;
global-orthogonal deferral beat magnitude on 25 percent of
out-of-vocabulary cases. Every bar below was set against those numbers.

## Cases

Per seed, 38 fresh cases from `poc/rgre_ml/cases.py`: 18 isolated (one
module missing), 8 two-missing, 8 out-of-vocabulary (the student has
everything the teacher's dictionary part has; the residual is a term no
module makes: a product frequency, a saturated XOR, a spiral, a ridge),
4 controls (nothing missing, two percent noise). Three fresh seeds,
101, 102, 103: 114 cases. Nothing about them is looked at before the
freeze.

Consumers: the prediction itself, a binary decision at the teacher's
median, and a 6x6 regional mean, each normalised by its own scale and
width. "Field residual" means the prediction block alone.

## Bars (frozen)

Scored on the pooled 114 cases; per-seed values reported.

- **B1, abstention as a quantity.** AUC of `q_perp` on the field
  residual, out-of-vocabulary against known cases, `>= 0.90`.
- **B2, sequencing.** Median two-step recovery on the field residual,
  abstention off, `>= 0.85` of the two-step oracle that knows both
  missing modules and fits them in the better order.
- **B3, field beats consumer for diagnosis.** Identity (the pick is the
  missing module, isolated cases, abstention off) is higher on the field
  residual than on the consumer residual, and the `q_perp` AUC is
  higher on the field residual.
- **B4, selection value.** Median value captured on the field residual,
  abstention off, `>= 0.90` of the oracle's error reduction, and above
  each of random, cheapest-first and gradient-norm on both median and
  mean. Equal to matching pursuit by the identity above, and reported
  as such.
- **B5, the borrowed constant.** RGRE-1's `tau = 0.5834` on the consumer
  residual abstains on `>= 80%` of out-of-vocabulary cases and `<= 10%`
  of known cases. **Predicted to fail**, as it did in fire.
- **B6, controls.** Declined or abstained on `>= 75%` of controls.
- **B7, deferral.** Deferring the regions with the largest
  global-orthogonal residual leaves less error un-handled after one
  growth step than deferring the regions with the largest residual, on
  `>= 60%` of out-of-vocabulary cases. **Predicted to fail.**
- **B8, search.** Median repairs evaluated per step over candidates
  `<= 1/3`.

## Outcome (frozen, exclusive)

Determined by B1 and B2, the two things RGRE adds over matching pursuit
that the pilot showed working.

- **A**: both hold. In this setting RGRE is matching pursuit plus a
  working out-of-vocabulary detector plus a working multi-step
  protocol, and the consumer residual is for scoring rather than
  diagnosis.
- **B**: B1 holds, B2 fails. The detector works; growing more than one
  step does not.
- **C**: B1 fails, B2 holds.
- **D**: neither. RGRE adds nothing over matching pursuit here.

No rescue, no second run on the fresh seeds. Results go in
`docs/math-track-rgre-ml1-results.md`; nothing above is edited after
the run.
