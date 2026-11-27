"""One hour of Quest-like frames at 72 Hz: tick scheduling strategies compared."""
import numpy as np, math, sys
from schedule import TickSchedule, continued_fraction, convergents, amortize
F, T = 72, 50                     # display Hz, physics Hz (a common awkward pair)
H = 3600 * F                      # frames in one hour (at 1 vsync each; drops add vsyncs)
def vsyncs(seed, drop=0.01):
    r = np.random.default_rng(seed); inc = np.where(r.random(H) < drop, 2, 1); return np.cumsum(inc)
def run(seed, method, drop_seed=1):
    """Per-frame tick counts and interpolation alpha for one strategy. Drops from drop_seed, timing noise from seed.
    Noise is on the absolute timestamps (dt = difference of timestamps, so it telescopes: no random walk)."""
    r = np.random.default_rng(1000 + seed); s = vsyncs(drop_seed); s_prev = np.concatenate([[0], s[:-1]])
    stamp = s / F + r.normal(0, 0.15e-3, H); stamp_prev = np.concatenate([[0.0], stamp[:-1]])
    meas = stamp - stamp_prev
    step = 1.0 / T; ticks = np.zeros(H, np.int64); alpha = np.zeros(H)
    if method == "exact":
        sch = TickSchedule(T, F); tb = (s * sch.T) // sch.F; tbp = (s_prev * sch.T) // sch.F
        return tb - tbp, ((s * sch.T) % sch.F) / sch.F, s
    dtype = np.float32 if method.endswith("32") else np.float64
    acc = dtype(0); st = dtype(step); n_done = 0
    for f in range(H):
        if method.startswith("measured"): dt = dtype(meas[f])
        elif method.startswith("nominal"): dt = dtype((s[f] - s_prev[f]) / F)
        elif method.startswith("snapped"): dt = dtype(round(meas[f] * F) / F)     # snap measured dt to vsync multiples
        acc = dtype(acc + dt); k = 0
        while acc >= st: acc = dtype(acc - st); k += 1
        ticks[f] = k; alpha[f] = float(acc / st)
    return ticks, alpha, s
methods = ["measured32", "measured64", "nominal32", "snapped32", "snapped64", "exact"]
print("display %d Hz, physics %d Hz, one hour (%d frames), 1%% dropped frames, 0.15 ms timestamp noise\n" % (F, T, H))
print("%-11s %10s %10s %12s %12s %14s %12s" % ("method", "irregular", "drift", "pos err rms", "pos err max", "same as seed2", "vs exact"))
ex1 = run(1, "exact")
for m in methods:
    tk, al, s = run(1, m); tk2, _, _ = run(2, m)          # same drops, different timing noise
    # irregular frames: tick count outside {floor, ceil} of the ideal for that frame's vsync span
    span = s - np.concatenate([[0], s[:-1]]); lo = np.floor(span * T / F); hi = np.ceil(span * T / F)
    irregular = int(np.sum((tk < lo) | (tk > hi)))
    drift = int(np.sum(tk) - (s[-1] * T) // F)
    # rendered position of an object moving 1 unit/s, interpolating between the last two tick states (one-tick lag):
    # pos = (n - 1 + alpha)/T, true = s/F - 1/T  -> error in units (multiply by speed)
    n = np.cumsum(tk); pos = (n - 1 + al) / T; true = s / F - 1.0 / T; err = pos - true
    same = bool(np.array_equal(tk, tk2))
    vs = int(np.sum(tk != ex1[0]))
    # differences from exact at coincidence frames (s T / F an integer) vs elsewhere
    coinc = (s * T) % F == 0; d = tk != ex1[0]; dc = int(np.sum(d & (coinc | np.roll(coinc, 1)))); de = vs - dc
    print("%-11s %10d %10d %12.2e %12.2e %14s %8d (%d at coincidence frames, %d elsewhere)" % (m, irregular, drift, np.sqrt(np.mean(err ** 2)), np.abs(err).max(), same, vs, dc, de))
print("\npos err: rendered minus true position of an object at 1 unit/s, interpolating between the last two tick states.")
print("'same as seed2': identical tick sequence when only the timing noise changes (same dropped frames).")
