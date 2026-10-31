# Latency check: streamed truth delayed by one round trip against local reconstruction with none

Relative RMS of the stalk bend against the teacher's present field. 'near' is the stalks within 1 m of the player's present position while walking; 'walking' is every stalk while the player moves; 'all' is the whole window including the 4 s of standing. The hybrid shows the stream everywhere and the local reconstruction within 1 m of the player.

## training walk (S-curve)

Local reconstruction (no delay, 124 ops per stalk): all 0.393, walking 0.414, near 0.428, coarse 16x16 0.223

| delay | ms | stream all | stream walking | stream near | stream coarse | hybrid all | hybrid walking |
|---|---|---|---|---|---|---|---|
| 1 frames | 17 | 0.061 | 0.075 | 0.086 | 0.033 | 0.257 | 0.320 |
| 2 frames | 33 | 0.121 | 0.149 | 0.171 | 0.067 | 0.263 | 0.327 |
| 3 frames | 50 | 0.179 | 0.222 | 0.252 | 0.099 | 0.273 | 0.339 |
| 4 frames | 67 | 0.236 | 0.292 | 0.329 | 0.132 | 0.287 | 0.356 |
| 5 frames | 83 | 0.290 | 0.360 | 0.402 | 0.163 | 0.303 | 0.376 |
| 6 frames | 100 | 0.342 | 0.423 | 0.470 | 0.194 | 0.322 | 0.398 |
| 8 frames | 133 | 0.435 | 0.539 | 0.589 | 0.252 | 0.362 | 0.448 |
| 12 frames | 200 | 0.579 | 0.717 | 0.767 | 0.354 | 0.438 | 0.540 |

## held-out walk (hook)

Local reconstruction (no delay, 124 ops per stalk): all 0.390, walking 0.435, near 0.402, coarse 16x16 0.220

| delay | ms | stream all | stream walking | stream near | stream coarse | hybrid all | hybrid walking |
|---|---|---|---|---|---|---|---|
| 1 frames | 17 | 0.063 | 0.085 | 0.092 | 0.039 | 0.227 | 0.310 |
| 2 frames | 33 | 0.126 | 0.170 | 0.181 | 0.078 | 0.236 | 0.322 |
| 3 frames | 50 | 0.187 | 0.252 | 0.267 | 0.116 | 0.251 | 0.341 |
| 4 frames | 67 | 0.246 | 0.332 | 0.347 | 0.153 | 0.270 | 0.366 |
| 5 frames | 83 | 0.302 | 0.408 | 0.423 | 0.190 | 0.293 | 0.396 |
| 6 frames | 100 | 0.355 | 0.480 | 0.492 | 0.225 | 0.318 | 0.429 |
| 8 frames | 133 | 0.452 | 0.610 | 0.612 | 0.291 | 0.371 | 0.499 |
| 12 frames | 200 | 0.599 | 0.809 | 0.784 | 0.405 | 0.467 | 0.626 |
