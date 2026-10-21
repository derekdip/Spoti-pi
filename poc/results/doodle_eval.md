# Doodle bots: coherence and novelty

Nearest-neighbour classifier (k = 7, cosine on 32x32 bitmaps) over six words, trained on 1500 human doodles per word; test sets of 400 held-out human doodles per word.

## Coherence: fraction classified as the word

| word | held-out humans | bank variations | variations drawn by a hand | canvas, chaos 0.15 | chaos 0.5 | chaos 0.85 |
|---|---|---|---|---|---|---|
| house | 0.95 | 0.90 | 0.88 | 0.80 | 0.52 | 0.25 |
| cat | 0.86 | 0.86 | 0.84 | 0.82 | 0.53 | 0.43 |
| bicycle | 0.96 | 0.95 | 0.96 | 0.88 | 0.85 | 0.55 |
| tree | 0.98 | 0.95 | 0.96 | 0.95 | 0.98 | 0.88 |
| sun | 0.76 | 0.73 | 0.70 | 0.60 | 0.18 | 0.03 |
| fish | 0.91 | 0.88 | 0.84 | 0.68 | 0.25 | 0.07 |
| **mean** | 0.90 | 0.88 | 0.86 | 0.79 | 0.55 | 0.37 |

## Novelty: distance to the nearest bank doodle, and spread

| word | held-out human to bank | variation to bank (own source excluded) | hand-drawn variation to bank | spread of 20 variations of one source | spread of 20 human doodles |
|---|---|---|---|---|---|
| house | 0.718 | 0.744 | 0.736 | 1.105 | 1.070 |
| cat | 0.768 | 0.776 | 0.753 | 1.030 | 1.032 |
| bicycle | 0.729 | 0.739 | 0.722 | 1.014 | 1.006 |
| tree | 0.763 | 0.765 | 0.754 | 1.098 | 1.065 |
| sun | 0.835 | 0.840 | 0.831 | 1.104 | 1.119 |
| fish | 0.700 | 0.702 | 0.690 | 1.066 | 1.081 |

Reading: a variation is as far from its nearest bank doodle as a fresh human doodle is (the two 'to bank' columns against the first), so it is not a copy of anything in the bank. The spread columns are on the same coarse bitmap distance, which saturates near 1 for any two doodles that are not near-identical; they say that twenty variations of one source are not near-identical to each other, and no more than that.

