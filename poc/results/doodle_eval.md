# Doodle bots: coherence and novelty

Nearest-neighbour classifier (k = 7, cosine on 32x32 bitmaps) over six words, trained on 1500 human doodles per word; test sets of 400 held-out human doodles per word.

## Coherence: fraction classified as the word

The canvas columns score everything on the canvas; the team columns score the team's figure alone (its plan, details, fixes and copies), which is what the VR player builds, leaving out a solo bot's corner figure, a misheard bot's other word and the scribbles.

| word | held-out humans | bank variations | variations drawn by a hand | canvas, chaos 0.15 | chaos 0.5 | chaos 0.85 | team figure, chaos 0.15 | chaos 0.5 | chaos 0.85 |
|---|---|---|---|---|---|---|---|---|---|
| house | 0.95 | 0.90 | 0.88 | 0.73 | 0.37 | 0.05 | 0.77 | 0.50 | 0.25 |
| cat | 0.83 | 0.88 | 0.86 | 0.78 | 0.60 | 0.43 | 0.82 | 0.77 | 0.47 |
| bicycle | 0.96 | 0.95 | 0.96 | 0.90 | 0.77 | 0.65 | 0.92 | 0.75 | 0.72 |
| tree | 0.98 | 0.95 | 0.96 | 0.90 | 0.77 | 0.67 | 0.93 | 0.92 | 0.78 |
| sun | 0.76 | 0.74 | 0.72 | 0.60 | 0.18 | 0.03 | 0.62 | 0.23 | 0.03 |
| fish | 0.91 | 0.89 | 0.83 | 0.63 | 0.27 | 0.05 | 0.68 | 0.35 | 0.12 |
| **mean** | 0.90 | 0.89 | 0.87 | 0.76 | 0.49 | 0.31 | 0.79 | 0.59 | 0.39 |

## Novelty: distance to the nearest bank doodle, and spread

| word | held-out human to bank | variation to bank (own source excluded) | hand-drawn variation to bank | spread of 20 variations of one source | spread of 20 human doodles |
|---|---|---|---|---|---|
| house | 0.718 | 0.759 | 0.752 | 1.095 | 1.070 |
| cat | 0.767 | 0.783 | 0.761 | 1.050 | 1.032 |
| bicycle | 0.729 | 0.738 | 0.727 | 1.017 | 1.006 |
| tree | 0.763 | 0.788 | 0.783 | 1.062 | 1.065 |
| sun | 0.835 | 0.836 | 0.819 | 1.103 | 1.119 |
| fish | 0.700 | 0.716 | 0.699 | 1.059 | 1.081 |

Reading: a variation is as far from its nearest bank doodle as a fresh human doodle is (the two 'to bank' columns against the first), so it is not a copy of anything in the bank. The spread columns are on the same coarse bitmap distance, which saturates near 1 for any two doodles that are not near-identical; they say that twenty variations of one source are not near-identical to each other, and no more than that.

