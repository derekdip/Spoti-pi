# Puddle slosh as a bouncing pulse (real MPM data, DeepMind WaterDrop)

Window starts 300 frames after the floor is 90% wet; 4 columns dropped at each wall.

30 trajectories, same window as the standing-mode fit. One pulse launched both ways from the impact,
reflected by the walls (method of images), Gaussian crest + trough-crest pair, exponential decay. 5 nonlinear
parameters plus 2 linear amplitudes.

| | in-window error (median, IQR) | held-out error (median, IQR) |
|---|---|---|
| bouncing pulse | 0.735 (0.66-0.80) | 1.000 (0.95-1.01) |

Shallow-water check c^2 / depth: median 13.4 in dataset units.

