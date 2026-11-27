"""Driver for dda.c: generate rays, run the four methods, validate the exact C kernels against the Python reference
(same path hash), count float errors (path hash differs from exact)."""
import numpy as np, subprocess, random, os
from voxelray import Ray
M64 = (1 << 64) - 1
def rotl(h, r): return ((h << r) | (h >> (64 - r))) & M64
def mix(h, x, y, z):
    h ^= (x * 0x9E3779B97F4A7C15) & M64; h = rotl(h, 13)
    h ^= (y * 0xC2B2AE3D27D4EB4F) & M64; h = rotl(h, 17)
    h ^= (z * 0x165667B19E3779F9) & M64; h = (h * 0xFF51AFD7ED558CCD) & M64; return h
S = 1 << 16; STEPS = 4096
rng = np.random.default_rng(11)
n1, n2 = 65536, 4096
o1 = rng.integers(-(1 << 26), 1 << 26, (n1, 3)); d1 = rng.integers(-(1 << 10) + 1, 1 << 10, (n1, 3))
o2 = S * rng.integers(-1000, 1000, (n2, 3)); d2 = rng.integers(-12, 13, (n2, 3))          # integer starts, small d: ties
o = np.vstack([o1, o2]); d = np.vstack([d1, d2]); d[np.all(d == 0, axis=1), 0] = 1
with open("rays.txt", "w") as f:
    f.write("%d\n" % len(o)); f.writelines("%d %d %d %d %d %d\n" % tuple(list(a) + list(b)) for a, b in zip(o, d))
for threads in (1, 4):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads))
    out = subprocess.run(["./dda", "rays.txt", str(STEPS), "out.txt"], capture_output=True, text=True, env=env).stdout
    print("threads = %d\n%s" % (threads, out))
rows = [l.split() for l in open("out.txt")]
H = np.array([[int(r[1 + 4 * m], 16) for m in range(4)] for r in rows], dtype=object)
# validate exact kernels against the Python reference on 60 random + 40 tie rays
pick = random.Random(0).sample(range(n1), 60) + random.Random(1).sample(range(n1, n1 + n2), 40)
for i in pick:
    p = Ray(o[i].tolist(), S, d[i].tolist()).traverse(STEPS); h = 0
    for v in p: h = mix(h, *v)
    assert H[i, 0] == h and H[i, 1] == h, i
print("exact C kernels (cross-multiplication and integer tMax) = Python exact reference on 100 sampled rays (60 generic, 40 tie-heavy)")
print("exact_xmul == exact_tmax on all %d rays: %s" % (len(o), bool(np.all(H[:, 0] == H[:, 1]))))
for m, name in ((2, "float32 A&W"), (3, "float64 A&W")):
    g = H[:n1, m] != H[:n1, 0]; t = H[n1:, m] != H[n1:, 0]
    print("%s: wrong path on %.1f%% of generic rays, %.1f%% of tie-heavy rays (%d steps)" % (name, 100 * g.mean(), 100 * t.mean(), STEPS))
