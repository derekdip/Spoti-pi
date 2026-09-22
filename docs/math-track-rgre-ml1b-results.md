# RGRE-ML-1b results: Holds by the frozen bars, narrowly. Deferring where the residual is unexplainable beats deferring where it is large, by about two percent of the error

Preregistration: `docs/math-track-rgre-ml1b-prereg.md`, frozen at commit
`11aa643`, unchanged. Raw output: `poc/results/rgre_ml1b_seed{201,202,203}.json`,
`.log`. Three fresh seeds, 12 mixed cases each, 36 cases. Scored by the
same code that scored RGRE-ML-1 (`poc/rgre_ml/run.py`, `--mixed 12`).

## Verdict by the frozen bars

| bar | target | result | |
|---|---|---|---|
| B1 | global-orthogonal deferral beats magnitude on `>= 60%` of mixed cases, ties against | **64%** (23 of 36; 3 ties, 10 losses) | pass |
| B2 | median un-handled error under orthogonal below magnitude's and below random's | orthogonal **0.367**, magnitude 0.378, random 0.368 | pass |
| reported | share of cases where the growth step added the missing module | **42%** (15 of 36) | weakens the test |

Both bars hold, so by the frozen tree the outcome is **Holds**: "defer
where the residual is unexplainable, not where it is large" is a real
contribution over matching pursuit and goes into the write-up. It goes
in with the three qualifications below, which the numbers force.

## Qualifications

**The margin over random on B2 is 0.001.** Medians of 0.367 against
0.368 pass the letter of the bar and say nothing on their own. The
bar's intent survives elsewhere: orthogonal deferral leaves less error
than random on 86 percent of cases pairwise, and its mean is 0.377
against random's 0.404. Random deferral has a good median here because
on a mixed case any region it removes has some of the foreign term in
it. The honest reading is that the median comparison with random was
the wrong statistic to freeze, and the pairwise one, which was not
frozen, is the one that carries the claim.

**The growth step added the missing module on only 42 percent of
cases, and the reason is a defect in the case design.** Abstention was
off for this step, so the model grew on every case; on 21 of 36 it grew
a module other than the missing one, and on 15 of those the module was
the pair interaction. The foreign terms were chosen to be outside the
dictionary, but the exclusive-or and product-frequency terms are partly
a product of two inputs, which the pair module fits, and on 12 of the
21 the exhaustive oracle agrees that the pair module is the best single
step. So the "foreign" part of the residual was not fully foreign, the
largest explainable direction was often the foreign term's shadow
rather than the missing module, and growth went there. The bars still
hold on both subsets (62 percent wins and medians 0.404 against 0.412
where growth missed; 67 percent and 0.303 against 0.311 where it hit),
so the result does not depend on the growth step succeeding. But the
mechanism the preregistration described, growth clears the explainable
part and deferral sees only the foreign part, was exercised on 15 cases
rather than 36, and a redesign would need foreign terms with no
projection onto any dictionary atom.

**The effect is small and uneven across seeds.** Per seed the win rate
is 58, 75 and 58 percent, so one of three seeds sits above the bar and
two sit below it, and the pooled figure clears it by four points. The
relative gain, magnitude's un-handled error minus orthogonal's over the
no-deferral error, has median 1.8 percent and interquartile range
minus 0.1 to 5.4 percent. By foreign-term kind the wins are 78 percent
for the exclusive-or term, 67 for product-frequency and spiral, 44 for
ridge; by missing module they run from 100 percent (pair, quad) to 33
(abs2, exp3), on three to eight cases each, too few to rank.

## What the numbers say

Every deferral criterion helps against not deferring: orthogonal on 94
percent of cases, magnitude on 78, random on 56. Local orthogonality,
the per-region version RGRE-ML-1 found degenerate, is again the worst
of the three informed rules (median 0.383, the same as no deferral),
so the global projection onto the tangent span is what makes the
criterion work, not orthogonality as such.

Against that background the frozen claim is supported by a consistent
but small edge: the global-orthogonal rule sends to the teacher the
regions the dictionary cannot fit, and that is worth about two percent
of the error over sending the largest regions, on a design where the
two kinds of region were made to coexist. It is a contribution over
matching pursuit in the sense the preregistration meant. It is not a
large one, and the case where it would matter most, after growth has
already absorbed the explainable residual, was reached on 15 cases.

## What would make it a stronger claim

Not run, not promised. Mixed cases whose foreign term has no projection
onto any dictionary atom, so that the growth step can only take the
missing module and the intended mechanism runs on every case. A larger
foreign-term amplitude relative to the missing module would widen the
gap the rule is meant to exploit. Neither is a rescue of this run; this
run holds as scored.

No rescue, no second run on the fresh seeds. Nothing above is edited
after the run.
