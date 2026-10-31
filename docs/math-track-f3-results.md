# F3 results: the vocabulary is the limit, and two experiments were spent tuning the wrong thing

Preregistration: `docs/math-track-f3-prereg.md`, frozen at commit
`dc583b9`, unchanged. Raw output: `poc/results/f3.json`, `f3_run.log`,
`f3_noise_floor.json`. One run, nine scenes.

## Verdict by the frozen bars: outcome C

| bar | target | result | |
|---|---|---|---|
| B1 vocabulary floor | joint fit median <= 0.35 | **0.626** | **fail** |
| B2 search adequacy | greedy >= 0.80 of joint | **0.959** | pass |
| B3 gated classes reachable | >= 1 of three | `soot`, `flicker` | pass |
| B4 terminal reduction | median >= 0.40 | **0.225** | **fail** |
| B5 consumer transfer | >= 6 of 7 | 7 of 7, none vacuous | pass |

Outcome C: the vocabulary is the limit. The C-versus-D boundary was
written as "beats V0 by a wide margin" and never quantified, which is a
defect in the tree and the third such defect across the three fire
freezes. The number is 23 percent median reduction, so C is the closer
reading and a reader can judge for themselves.

## The argument, in four numbers

| quantity | value |
|---|---|
| V0 error, median over scored scenes | 0.818 |
| greedy search, best it reaches | 0.617 |
| joint fit of every parameter at once | 0.626 |
| two teacher runs differing only in random seed | 0.003 to 0.098 |

**Greedy reaches 96 percent of what joint fitting reaches**, and on
three of seven scenes it beat the joint fit outright. So selection is
not the bottleneck and never was. Any perfect search could gain about
four percent more.

**The joint fit still leaves 0.626.** With nothing withheld, no
stopping rule, no greed and every parameter of every class free, the
cheap model is still wrong by 63 percent of the signal's own magnitude.

**Almost none of that is chaos.** Two teacher runs differing only in
seed agree to 0.003 on the forced scenes and 0.098 on the bare plume,
which is the error any deterministic model must pay. The explainable gap
is therefore about 0.61, some sixty times the noise floor. This was
measured after the run, as a property of the teacher rather than of the
procedure, and it is what separates outcome C from a claim that the
model has hit an information limit. It has not. The structure is there
and the grammar cannot express it.

## The correction this forces on F1

F1's frozen tree returned outcome B, "selection transfers, the
vocabulary is too weak". F1's write-up disputed that label in its own
first section: "The bars are right and the label is wrong, and the
reason is in the stop column."

The label was right and the dispute was wrong. F3 shows the ceiling on
terminal reduction is about 23 percent, so F1-B3's target of 40 percent
was **unreachable at the moment it was frozen**, whatever the stopping
rule did. F1 failed that bar because the bar was above the possible, not
because seven scenes stopped early. The stopping-rule analysis in F1 is
still correct about why `q_perp` misfires, and F2 confirmed the same
failure in a second disguise. It was simply not the reason F1 failed.

Two experiments, F1 and F2, were therefore spent repairing a search
whose target was out of reach. The check that would have caught it is
the one F3 ran first and costs under a minute a scene: fit everything
jointly and see whether the bar is achievable before freezing it. That
is the methodology lesson and it is cheap to adopt.

## What the grammar cannot express

Per-consumer error at the joint fit, median over scored scenes:

| consumer | error |
|---|---|
| heat probes | 0.317 |
| visual glow | 0.617 |
| ignition | 0.684 |
| AI hazard grid | 0.753 |

Heat is the only consumer the vocabulary serves reasonably. Point
temperatures near the flame are what a single Gaussian column is
actually good at. Everything that depends on the *shape* of the hot
region fails: the glow the player sees, whether a bed is alight, and
where the AI may not walk. On `obstacle` the visual error at the joint
fit is exactly 1.0, meaning the fit is no better than predicting
nothing at all for that consumer.

The structural reason is the same in every case. Every source in this
grammar is one Gaussian column anchored to its cause, so it cannot
split around a shelf, cannot detach when the burner stops, and cannot
hand off to a bed that lights on its own clock and burns out. Those are
missing shapes, not missing parameter values, and no amount of fitting
reaches a shape that is not in the grammar. `secondary` exists to model
the bed and was never chosen in any of the three runs even once it was
reachable, because a second anchored Gaussian is not what a burning bed
looks like either.

The joint fit does switch on classes greedy never reaches, `deflect`
and `floor` on every scene and the full `sec_*` group on three, and it
is still no better overall. Turning on more of the same vocabulary does
not help.

## What survives

The procedure's machinery is sound and this run is the cleanest evidence
for it. Greedy selection by residual projection reaches 96 percent of an
exhaustive joint fit while evaluating one repair per step, it never made
a consumer worse on any of seven scenes, and the fitter fix made two of
the three previously inert classes reachable and chosen. Given a
vocabulary that can express the target, the search finds it.

What does not survive is the fire representation. It should not be
extended parameter by parameter. It needs source shapes it does not
have: a plume that can split, a puff that detaches from its cause, and a
bed whose fire has its own life cycle rather than borrowing the burner's.
Those are three new token types, and building them is a different task
from anything RGRE was asked to do here.
