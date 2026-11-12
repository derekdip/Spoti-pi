# RGRE-1 results: residual-guided representation expansion, first test

Preregistration: `docs/math-track-rgre1-prereg.md` (frozen at commit
`ce464f3`, unchanged). Raw outputs: `poc/results/rgre1.md`, `rgre1.json`,
`rgre1.png`, `rgre1.log`. Run 1 was killed by the memory limit after 36
cases (fields cached per state; fixed by caching scalars only, commit
`1ec81da`, log kept as `rgre1_run1.log`); run 2 is the judged run and
reproduces run 1's 36 cases. The figure failed on a matplotlib keyword
and was regenerated from the saved JSON. 78 cases, 20 minutes.

## Verdict by the frozen rules: A, procedure supported; with H3, H6 and H7 failing

| test | bar | result |
|---|---|---|
| H1 oracle value captured | median `V_cap >= 0.75` over 72 known cases | 1.00 (mean 0.82; corn 1.00 / 0.88, water 1.00 / 0.74): **pass** |
| H2 search reduction | median `N_RGRE / N_all <= 1/3` | 0.17: **pass** |
| H3 beats three baselines at equal budget | RGRE median above each | cheapest-first 0.001, random 0.32, largest-opportunity 1.00, best-local-projection 1.00: **fail** (tied on the median with the two residual-based baselines; see below) |
| H4 mixtures | median two-step recovery `>= 0.7` | 0.88; ownership shift on 7 of 12: **pass** |
| H5 abstention | `>= 5/6` unknowns abstain, `<= 10%` known abstain | 5 of 6; 4 of 72 (5.6%): **pass** |
| H6 coherence predicts identity loss | identity lower at `mu >= 0.5` | 0.75 (n = 28) against 0.72 (n = 40): **fail** |
| H7 re-diagnosis beats top-two-once | wins more than half of non-tied mixtures | 4 wins, 5 losses, 3 ties: **fail** |

Identity: 0.86 against the injected class, 0.69 against the oracle's
class, 0.93 for the oracle's class in the top two. The outcome tree
checks A first and A's conditions (H1, H2, H4, H5) hold, so the letter
is A. The three failures are not incidental and are the content of this
document.

## What carried the value

Per injected class the median value captured is 1.00 for smooth, stop,
coordinate, unary and interaction, 0.99 for corner and 0.88 for tail.
Every corn stop, corn coordinate, corn unary, corn smooth and water
interaction case is captured in full, evaluating one or two repairs
out of nine or six. The unknowns behave: both wind fields and the hidden
walker leave 90 to 99 percent of the residual unexplained and abstain,
and the two hidden splashes 61 to 63 percent, above the 0.583 threshold
calibrated on old cases; the sixth unknown, a dragged pressure source,
was mostly a gain error in the vocabulary's terms and the oracle agrees
(a gain correction removes 1.2 of its 2.2 error). Mixtures sequence:
after a correct first repair the first class's ownership collapses
(0.64 to 0.00, 0.56 to 0.00, 0.94 to 0.06) and the second injected
class's rises (0.00 to 0.60, 0.27 to 0.79, 0.05 to 0.81), and the second
repair is then found. This is the residual-to-class-to-repair chain
working on 72 fresh cases across two teachers.

## What did not: the coherence score, and abstention on weak defects

**H3.** Two baselines tie RGRE's median of 1.00, and on the cases that
differ they are better. The largest-generic-opportunity baseline (raw
ownership, no coherence discount, no abstention) beats RGRE on 10 cases
and loses on 3; the class-free best-local-projection baseline (each
tangent direction and template scored by its own fraction) beats RGRE
on 12 cases and never loses. Mean value captured: RGRE 0.82,
largest-opportunity 0.90, best-local-projection 0.94, cheapest-first
0.35, random 0.34. Residual diagnosis beats cost-first and random by a
wide margin; the scoring built on top of it, `S = q (1 - mu)` plus
abstention, subtracts.

The mechanism is in the tables. Coherence was defined within a
diagnostic type (a template cannot counterfeit a tangent), which is
right, but it leaves a template class with no same-type competitor at
`mu = 0` while every tangent class in a coherent family is discounted by
0.7 to 0.9. In both interaction+coordinate mixtures the raw ownership
was correct, coordinate 0.73 and 0.67 against interaction 0.14 and 0.27,
and the discounted score flipped it (0.12 against 0.14); RGRE evaluated
the pair term (worth 0.005) instead of the shift (worth 0.24), and
re-diagnosis re-committed to interaction because the residual had not
changed. The unary+stop mixture flipped the same way (unary 0.68 raw
against stop 0.29), and three of six corn tail cases lost to the smooth
template at a tenth of their ownership. Where the discount helped (water
delays of 5 and 6 frames, where the four-dimensional unary subspace
out-owns the one-dimensional coordinate direction on raw share), the
per-direction projection baseline got the same answer without it,
because the single time direction's own fraction beat each unary
direction's.

**Abstention on known cases** cost four cases: three water unary cases
whose residual is mostly the token's own floor (two of them with oracle
values of 0.006 and 0.007, where abstaining is the right call) and one
water tail case (oracle 0.059). The threshold itself was fine: the
largest unexplained fraction on a known case was 0.48 against the 0.583
threshold, and the five abstaining unknowns sat at 0.61 to 0.99.

**H6** fails for the same reason H3 does: identity errors are
concentrated in the undiscounted classes (corner chosen where uniform
refinement was the better buy, interaction and stop chosen over coherent
tangent classes), not in the high-coherence ones. The coherent water
classes were right 75 percent of the time. The prediction that coherence
predicts identity loss is not supported by this scoring; the discount
made coherence self-fulfilling in the other direction.

**H7** fails because re-diagnosis is only as good as the first
diagnosis: on the three mixtures where the first class was wrong, the
residual after a worthless repair is unchanged and the same wrong class
is chosen again (0.005 and 0.006 total), while executing the initial
top two classes reaches the second, correct one (0.24, 0.18, 0.20). On
the mixtures where the first class was right, re-diagnosis and the
static top-two tie or re-diagnosis wins by a little (0.085 against
0.045 on corner+stop). Re-diagnosis is not a static classifier, as
hoped, but it is also not self-correcting: it needs the first step to
have moved the residual.

## Smaller findings

- Corner cases: the corner class is diagnosed on all six and captures
  0.74 to 1.00, but on four of six the oracle's best value per vertex
  is uniform refinement, not the corner tightening. B5's lesson again:
  the class is right and the cheapest repair within reach is generic.
- Water tail cases with strong global damping (gamma0 0.75 to 1.5) are
  diagnosed as tail but the oracle prefers the gain, because stronger
  damping mostly lowers amplitude within 2 m; value captured 0.55 to
  0.99.
- Water delays of 7 and 8 frames (117 and 133 ms) are misread as unary,
  the same linearisation limit W4 met at 96 ms: the time tangent stops
  spanning the shift.
- Cost-first is useless on corn (median 0.00): the cheap parameter
  repairs never touch a geometry defect.
- Runtime: 7.8 s median per case including the oracle over every
  repair; the diagnosis itself is a handful of consumer evaluations.

## What RGRE-1 establishes

1. **Residual ownership chooses the repair.** On fresh cases in two
   domains, projecting the consumer residual onto the representation's
   tangent directions and class supports finds the oracle's repair or
   its value in the median case while evaluating a sixth of the repair
   space, sequences two-defect cases with 0.88 median recovery, and
   abstains on five of six out-of-vocabulary cases. That is the claim
   the track set out to test, and it holds.
2. **The scoring refinements do not earn their place.** The
   coherence-discounted score and the abstention on known cases cost
   value against the plain per-direction projection, which never loses.
   The mechanistic procedure should be the projection, and coherence
   should be reported as a warning about identity, not used as a weight.
3. **Re-diagnosis needs a moved residual.** It corrects nothing after a
   worthless repair.
4. **Class and repair remain separate**, as B5 said: the diagnosed class
   was right 86 percent of the time, the oracle's repair class only 69
   percent, and the value captured stayed high because the class's
   repair set usually contained a good buy even when it did not contain
   the best one.

## On the next step

The track owner's rule was: if A, stop synthetic theory tracks and run
the end-to-end test on a new expensive simulation with neither the
cheap representation nor the defect sequence chosen by hand. A holds by
the frozen tree, and the procedure to carry forward is the simpler one
that this run identified: per-direction residual projection and support
localisation, repair sets per class, abstention on unexplained residual,
no coherence weighting. Whether that counts as A in spirit, or as an
amendment that needs one more frozen check before fire, is the owner's
call; this document changes nothing that was frozen.
