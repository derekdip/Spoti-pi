# Streaming latency check: does local reconstruction of a player-caused effect beat a streamed render?

A design check, not preregistered, run on 2026-10-06 after the question
whether this project's reconstruction could improve wireless PC-to-headset
streaming. `poc/latency_check.py`, results in `poc/results/latency_check.*`.

## The question, in the project's own terms

A streamed game renders the world on the PC and sends frames; what the
headset shows of a player-caused effect (grass bending under a foot) is
the true effect as it was one round trip ago, `F(t - L)`. Local
reconstruction shows the project's cheap model of the effect, driven by
the player's own tracking with no delay, `F^(t)`. Both are wrong against
the present truth `F(t)`: the stream by the latency, the reconstruction
by its fidelity. The project has measured the second error for years
(0.39 per stalk, 0.22 on the 16 by 16 field). The check measures the
first on the same teacher, walks and consumers, and finds the crossover.

## Method

The vegetation teacher (`poc/reactive/teacher.py`, 1600 stalks, 60 Hz,
the S-curve training walk and the held-out hook walk, 6 and 5 seconds of
walking then standing), the six-term model fitted in the original run
(`poc/results/summary.json`, 124 ops per stalk). Errors are the
project's relative RMS of stalk bend against the teacher's present
field, on four consumers: every stalk within 1 m of the player's
present position while walking (near, where the player looks and where
the effect is being caused), every stalk while walking, the whole window,
and the 16 by 16 coarse field. The stream is the teacher's own field
delayed by 1 to 12 frames (17 to 200 ms). A hybrid, the stream everywhere
and the reconstruction within 1 m of the player, is also scored.

## Results

| consumer, walk | reconstruction error | stream error at 33 ms | at 50 ms | at 67 ms | at 100 ms | crossover |
|---|---|---|---|---|---|---|
| near, S-curve | 0.428 | 0.171 | 0.252 | 0.329 | 0.470 | 90 ms |
| near, hook | 0.402 | 0.181 | 0.267 | 0.347 | 0.492 | 79 ms |
| walking, S-curve | 0.414 | 0.149 | 0.222 | 0.292 | 0.423 | 98 ms |
| walking, hook | 0.435 | 0.170 | 0.252 | 0.332 | 0.480 | 89 ms |
| whole window, S-curve | 0.393 | 0.121 | 0.179 | 0.236 | 0.342 | 118 ms |
| whole window, hook | 0.390 | 0.126 | 0.187 | 0.246 | 0.355 | 112 ms |
| coarse 16x16, S-curve | 0.223 | 0.067 | 0.099 | 0.132 | 0.194 | 117 ms |
| coarse 16x16, hook | 0.220 | 0.078 | 0.116 | 0.153 | 0.225 | 98 ms |

The stream's error grows linearly in the delay up to about 50 ms, at
5.0 to 5.3 per second near the player, 2.0 to 2.3 per second on the
coarse field. The hybrid is worse than the plain stream at every delay
below the crossover (0.26 against 0.06 at 17 ms near the player): a
reconstruction whose own error is 0.4 cannot improve a frame that is
0.1 wrong, wherever it is pasted.

## The criterion

In the linear regime the stream's error is `L / tau_eff`, where
`tau_eff` is the effect's own time scale as the consumer reads it: the
inverse of the measured slope, 190 to 225 ms near the player and while
walking, 430 to 500 ms on the coarse field (the grass responds through
a 0.13 s lead and a spring of period about 0.7 s, and the coarse field
averages over cells that change slower still). Local reconstruction pays
for itself only when

    L > L* = e_local * tau_eff

where `e_local` is the reconstruction's own error on that consumer.
Predicted `L*`: 85 and 76 ms near the player on the two walks, 93 and
86 ms while walking, 109 and 104 ms over the window, 112 and 94 ms on
the coarse field; measured crossovers 90, 79, 98, 89, 118, 112, 117 and
98 ms. The criterion predicts every crossover within 10 ms with no
fitted constant. It is the liveness and tolerance arguments of the
math track (`docs/math-track-b0-review.md`) read in the time direction:
the error of a delayed effect is first order in the delay over the
effect's time scale, as the path-tolerance error was first order in
the chord over the kernel's width (B4).

## Verdict for the Steam Frame

Valve's dedicated 6 GHz link is built for round trips well under the
80 to 120 ms this check needs before local reconstruction of grass pays
on any consumer. At the latencies such a link is designed for, the
delayed truth is three to four times closer to the present truth than
the project's reconstruction is, near the player included. For this
effect, on this link, local reconstruction does not improve the stream,
and pasting it over the stream near the player makes the frame worse.
The suggestion made before this check is withdrawn.

What would change the verdict, by the criterion, is any of three
things: a longer round trip (cloud or remote streaming at 100 ms and
up, where local reconstruction of grass wins on every consumer); a
faster effect (an effect with `tau_eff` of 50 ms, a splash front or a
hand through water, would cross at about 20 ms and local reconstruction
would win on a dedicated link); or a reconstruction several times
better than 0.4 per stalk, which the knee experiment says this grammar
does not have (the floor is the teacher's own per-stalk scatter,
`docs/review.md`). The second is the one worth a check if the question
comes back: the water tokens in `poc/water/` have the time scale, and
the same script applies.

## What this says about the project's claims

Nothing in the project was about latency, and nothing here contradicts
what it established: the reconstruction is a compute and state
replacement, measured as such, and its value is on a device that runs
the effect itself. On a headset that streams, the effect is already
computed elsewhere and arrives late by an amount this check now puts a
number on, and the project's representation is not accurate enough to
beat that number at the latencies a dedicated link gives. The honest
application on a streaming-first headset is standalone play, where the
compute argument holds unchanged.
