# ED10 preregistration: one run that stops itself, against the cross-fit and the published signals

Written 2026-11-11 after a declared pilot and before any scored fit.
Frozen by the commit "ED10 freeze", which adds this file,
`poc/results/ed10/run/config.json` and the version of
`poc/tools/lora_online.py` that runs and scores it (with
`poc/tools/lora_knee.py` and `poc/tools/lora_big.py`, which it uses).
After that commit none of them changes; a defect found later is named
in the results. Run:
`python3 poc/tools/lora_online.py run poc/results/ed10/run/config.json poc/results/ed10/run`;
report: `python3 poc/tools/lora_online.py score poc/results/ed10/run`.

## 1. The question

The cross-fitted rule costs a full fit and eight half-fits. Section 12
of `docs/prescreen-theory.md` gives an identity: along a fit the test
gain grows, per unit of training gain, at the real share of the step,
so the test gain peaks where the share reaches zero. The share can be
estimated during the fit from the gradients of two halves of the
training contexts, with no held-out data and no extra fits. Does
stopping where that estimate first reaches zero keep the gain, as well
as the cross-fit does, and better than the published signals for
stopping without a validation set?

## 2. Signals, all from the training contexts, every evaluation

With `g_A`, `g_B` the raw gradients of the adapter's factors on the
two halves and per-context gradients for the EB criterion:

- **share** = `<g_A, g_B> / (<g_A, g_B> + |g_A - g_B|^2 / 4)`. Stop at
  the first evaluation after the first at which it is at or below 0.
- **disparity** (Forouzesh and Thiran, 2021, as recalled): `|g_A - g_B|`;
  stop at the first point after which it rises 3 times in a row.
- **disparity_rel**: `|g_A - g_B|` over the mean of `|g_A|`, `|g_B|`; stop
  at its running minimum once it has risen 3 times in a row from it.
  Added after the pilot showed raw disparity rising from the start,
  because a LoRA starts at zero and its gradients grow.
- **eb** (Mahsereci et al., 2017, as recalled): `1 - (n / D) sum m_k^2 / s_k`;
  stop at the second of two consecutive evaluations with `eb > 0`
  (the pilot's single crossings were noisy).

The two published signals are rebuilt from memory, unchecked against
the papers, and adapted to a LoRA that starts at zero. A loss to them
here is a loss to these versions, not to the papers.

Arms read off the same full fit: **rule** (the cross-fitted knee: for
the four one-matrix adapters the median of their eight half-fit knees,
as in ED5; for each all-matrix adapter the mean of its own two, as in
ED9), and **val**, the minimum on 32 extra validation contexts, which
the use case does not have.

## 3. The pilot (declared, not scored)

`poc/results/ed10/pilot/` (recorded by the version at commit fa558b7):
GPT-2 base, plain text at 8 (seed 70) and 32 (seed 71) contexts, the
four one-matrix adapters. Share of the peak kept, mean (lowest): rule
0.98 (0.95, interpolated as in ED5), share 0.96 (0.71), raw disparity
0.03 (0.00), eb (single crossing) 0.29 (-0.20), validation 1.00 (0.98).
The share crossed zero within one or two evaluations of the test peak
in seven of eight fits and stopped one 20 steps early.

## 4. The scored run

GPT-2 base; plain text at 8, 16 and 32 contexts and leet at 32; 32
validation and 96 test contexts; seeds 81 to 84, none used before.
Six adapters per condition: rank 2 on `proj@2`, `proj@8`, `v@2`, `o@8`
(learning rate 1e-3, evaluated every 10 steps) and on all 48 matrices
at rank 2 (3e-4) and rank 8 (1e-4), evaluated every 5 steps, as in
ED9. Full fits until the test gain has fallen to a quarter of its peak
or 800 steps; half-fits until the other half's gain has fallen to half
its peak or 500 steps. 24 full fits.

## 5. Bars, over the 24 full fits

- **O1** (the share is safe): stopped by the share, the test gain is
  positive in all 24 and at least two thirds of the peak in at least 20.
- **O2** (close to the cross-fit): its mean share of the peak kept is no
  more than 0.05 below the rule's.
- **O3** (better than the published signals as implemented): its mean is
  higher than each of disparity, disparity_rel and eb.

**A**: all three hold: one run with no held-out data replaces the
cross-fit. **B**: O1 holds and O2 or O3 fails: safe, but not as good as
the cross-fit, or no better than an existing signal. **C**: O1 fails.

Reported with no bar: everything by condition and reach, and the steps
at which each signal stopped against the test peak.

## 6. Cost

About 2 to 2.5 hours on 4 CPU threads. Each condition is committed and
pushed as it finishes.
