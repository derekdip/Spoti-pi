# RGRE-ML-1b: the deferral claim on the cases that can measure it. Preregistration (frozen before the seeds run)

RGRE-ML-1's B7 asked whether deferring the regions whose residual no
class can explain beats deferring the regions with the largest residual.
It failed, and its results document says why that was not a test: the
out-of-vocabulary cases had nothing missing from the dictionary part, so
their whole residual was unexplainable and both criteria ranked the same
regions; the isolated cases had nothing unexplainable, so orthogonality
was noise. Neither can distinguish the hypothesis.

This is the case that can. **Mixed**: the teacher is linear plus one
known module plus one module the student lacks plus one term the
dictionary cannot make. Growth can fix the missing module and cannot
touch the foreign term. A deferral rule that ranks by "unexplainable"
should send the teacher the foreign term's regions and not the missing
module's; a rule that ranks by magnitude at step zero cannot tell them
apart. Scored, as before, by the error left un-handled in the
non-deferred regions after one growth step, with the growth step taken
by the field-residual rule RGRE-ML-1 validated. No pilot: the case
construction and the scorer are what RGRE-ML-1 froze, with one new case
kind.

## Bars (frozen)

Three fresh seeds (201, 202, 203), 12 mixed cases each, 36 cases.

- **B1.** Global-orthogonal deferral leaves less un-handled error than
  magnitude deferral on `>= 60%` of mixed cases (ties count against).
- **B2.** Median un-handled error under global-orthogonal deferral is
  below magnitude's and below random's.
- Reported: the share of cases in which the growth step actually added
  the missing module; if it is low, the test is weakened and that is
  said.

## Outcome (frozen)

- **Holds** if B1 and B2 both hold: "defer where the residual is
  unexplainable, not where it is large" is a real contribution over
  matching pursuit and goes into the write-up.
- **Fails** otherwise, and the claim is dropped rather than carried as
  "unmeasured".

Nothing above is edited after the run.
