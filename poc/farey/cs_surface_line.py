"""Critical-line growth of |Z_B(1/2 + it)|^2 on a given torus (TRACES env), t random in [10, 1000], incremental save."""
import sys, os, numpy as np
sys.path.insert(0, "poc/farey"); import zb_cs as C
tag, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ts = np.sort(np.random.default_rng(seed).uniform(10, 1000, n)); out = []
for i, t in enumerate(ts):
    out.append((t, abs(C.Z(complex(0.5, t)))))
    if i % 10 == 9 or i == n - 1: np.save("poc/farey/csline_%s.npy" % tag, np.array(out))
