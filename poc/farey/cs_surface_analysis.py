"""Growth exponent of <|Z_B(1/2+it)|^2> on three tori (modular, X*, thin cusped (2.2, 4.86, 5.0)), t in [10, 1000]."""
import numpy as np, glob
for tag in ("modular", "Xstar", "thin"):
    L = np.load("poc/farey/csline_%s.npy" % tag); t, a = L[:, 0], L[:, 1] ** 2
    ex = np.polyfit(np.log(t), np.log(a), 1)[0]
    # bootstrap error on the exponent
    rng = np.random.default_rng(0); bs = [np.polyfit(np.log(t[i]), np.log(a[i]), 1)[0] for i in [rng.integers(0, len(t), len(t)) for _ in range(300)]]
    bands = [(10, 100), (100, 300), (300, 600), (600, 1000)]
    ms = ["%.0f" % np.mean(a[(t >= lo) & (t < hi)]) for lo, hi in bands]
    # mean-square exponent from band means
    mid = np.array([np.mean(t[(t >= lo) & (t < hi)]) for lo, hi in bands]); mm = np.array([np.mean(a[(t >= lo) & (t < hi)]) for lo, hi in bands])
    ex2 = np.polyfit(np.log(mid), np.log(mm), 1)[0]
    print("%-8s n = %3d: band means <|Z|^2> %s;  exponent of band means %.2f;  log-log fit %.2f +- %.2f" % (tag, len(t), ms, ex2, ex, np.std(bs)))
