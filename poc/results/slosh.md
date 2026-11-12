# Puddle slosh on real MPM data (DeepMind WaterDrop, validation set)

10 trajectories. Window starts 150 frames (0.375 s) after the drop has wet 90% of the floor. Model: K standing shallow-water modes with fitted wave speed and damping; amplitudes and phases by least squares. Held-out: fit on the first half of the window, score the second half.

| modes | damping | in-window error (median, IQR) | held-out error (median, IQR) | wave speed c (median) |
|---|---|---|---|---|
| 1 | per mode | 0.973 (0.94-0.99) | 0.996 (0.99-1.00) | 0.78 |
| 1 | shared | 0.973 (0.94-0.99) | 0.996 (0.99-1.00) | 0.78 |
| 2 | per mode | 0.818 (0.79-0.86) | 0.964 (0.94-0.99) | 0.81 |
| 2 | shared | 0.823 (0.79-0.86) | 0.979 (0.94-1.01) | 0.82 |
| 3 | per mode | 0.778 (0.74-0.83) | 0.969 (0.96-1.00) | 0.78 |
| 3 | shared | 0.780 (0.75-0.83) | 0.972 (0.93-1.00) | 0.76 |
| 4 | per mode | 0.730 (0.71-0.80) | 0.998 (0.98-1.02) | 0.76 |
| 4 | shared | 0.749 (0.73-0.82) | 0.967 (0.92-1.02) | 0.78 |
| 6 | per mode | 0.704 (0.69-0.78) | 1.001 (0.98-1.02) | 0.76 |
| 6 | shared | 0.741 (0.72-0.80) | 1.004 (0.95-1.02) | 0.79 |
| 8 | per mode | 0.693 (0.68-0.76) | 0.995 (0.97-1.02) | 0.72 |
| 8 | shared | 0.739 (0.71-0.80) | 1.012 (0.98-1.03) | 0.76 |

Shallow-water check: c^2 / depth should be the simulator's g. Median 13.2 (IQR 7.3-16.1) in dataset units.

