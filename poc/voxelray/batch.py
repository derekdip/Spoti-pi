"""Batch exact traversal in fixed-point int64 (S = 2^16 sub-voxel precision, |d| < 2^15, j < 2^20 steps, so every
product (j S - F) |d| < 2^51): many rays stepped in lockstep with numpy, the form a GPU/C kernel would take.
Checked against the exact Python reference; timed against a vectorised float32 Amanatides-Woo."""
import numpy as np, time, random
from voxelray import Ray
S = 1 << 16
def batch_exact(o, d, nsteps):
    """o: (n,3) int64 numerators over S; d: (n,3) int64. Returns (n, nsteps+1, 3) voxel indices ('face' policy, but
    tied axes stepped one per step in x, y, z order exactly as the reference)."""
    n = o.shape[0]; sg = np.sign(d); ad = np.abs(d)
    v = np.where(d >= 0, o // S, -((-o) // S) - 1)
    F = np.where(d >= 0, o - v * S, (v + 1) * S - o)
    j = np.ones_like(o); out = np.empty((n, nsteps + 1, 3), np.int64); out[:, 0] = v
    BIG = np.int64(1) << 62
    for k in range(1, nsteps + 1):
        num = j * S - F                                      # time = num / (ad S); compare num_a ad_b vs num_b ad_a
        # choose axis with smallest time; ties -> lowest axis index. Inactive axes (ad = 0) never chosen.
        best = np.zeros(n, np.int64); bn = np.where(ad[:, 0] > 0, num[:, 0], BIG); bd = np.where(ad[:, 0] > 0, ad[:, 0], 1)
        for a in (1, 2):
            act = ad[:, a] > 0
            better = act & ((bn == BIG) | (num[:, a] * bd < bn * ad[:, a]))
            best = np.where(better, a, best); bn = np.where(better, num[:, a], bn); bd = np.where(better, ad[:, a], bd)
        idx = np.arange(n)
        v[idx, best] += sg[idx, best]; j[idx, best] += 1; out[:, k] = v
    return out
def batch_aw32(o, d, nsteps):
    o = o.astype(np.float32) / np.float32(S); d = d.astype(np.float32); n = o.shape[0]
    v = np.where(d >= 0, np.floor(o), np.ceil(o) - 1).astype(np.int64); step = np.where(d > 0, 1, -1)
    with np.errstate(divide="ignore"):
        tdel = np.where(d != 0, np.abs(np.float32(1) / d), np.float32(np.inf)).astype(np.float32)
        tmax = np.where(d > 0, ((v + 1).astype(np.float32) - o) / d, np.where(d < 0, (v.astype(np.float32) - o) / d, np.inf)).astype(np.float32)
    out = np.empty((n, nsteps + 1, 3), np.int64); out[:, 0] = v; idx = np.arange(n)
    for k in range(1, nsteps + 1):
        a = np.argmin(tmax, axis=1); v[idx, a] += step[idx, a]; tmax[idx, a] += tdel[idx, a]; out[:, k] = v
    return out
rng = np.random.default_rng(3); n, steps = 4096, 2000
o = rng.integers(-(1 << 20), 1 << 20, (n, 3)).astype(np.int64); d = rng.integers(-(1 << 15) + 1, 1 << 15, (n, 3)).astype(np.int64)
d[np.all(d == 0, axis=1), 0] = 1
t0 = time.time(); ex = batch_exact(o, d, steps); te = time.time() - t0
t0 = time.time(); fl = batch_aw32(o, d, steps); tf = time.time() - t0
# check 40 random rays against the Python reference
for i in random.Random(0).sample(range(n), 40):
    assert [tuple(x) for x in ex[i]] == Ray(o[i].tolist(), S, d[i].tolist()).traverse(steps), i
wrong = np.any(ex != fl, axis=2); first = np.where(wrong.any(1), wrong.argmax(1), -1)
print("batch exact int64: %d rays x %d steps in %.2f s (%.1f ns/step-ray); float32 A&W %.2f s (%.1f ns)" % (n, steps, te, 1e9 * te / (n * steps), tf, 1e9 * tf / (n * steps)))
print("int64 batch = exact Python reference on 40 sampled rays")
print("float32 A&W: %d of %d rays (%.1f%%) differ within %d steps; median first differing step %d" % ((first >= 0).sum(), n, 100 * (first >= 0).mean(), steps, int(np.median(first[first >= 0])) if (first >= 0).any() else -1))
