"""Where float64 Amanatides-Woo fails: (1) rays through lattice edges/corners (ties), (2) very long rays, and the
error-free alternative. Reports the first step where the float traversal differs from the exact one."""
import random, time
from voxelray import Ray, amanatides_woo
rnd = random.Random(9)
print("(1) tie-heavy rays: integer start, small integer directions (pass exactly through edges and corners)")
for d in ((1, 1, 1), (2, 3, 6), (1, 2, 2), (3, 4, 12), (5, 5, 7)):
    r = Ray((0, 0, 0), 1, d); n = 3000; ex = r.traverse(n)
    for dt in ("f64", "f32"):
        fl = amanatides_woo((0.0, 0.0, 0.0), d, n, dt)
        bad = next((i for i in range(n + 1) if fl[i] != ex[i]), None)
        print("   d = %-11s %s: first differing voxel at step %s" % (d, dt, bad))
print("(2) long generic rays, float64")
for trial in range(3):
    S = 10**9 + 7; o = [rnd.randint(0, S) for _ in range(3)]; d = [rnd.randint(1, 10**7) for _ in range(3)]
    r = Ray(o, S, d); n = 2_000_000
    t0 = time.time(); ex = r.traverse(n); te = time.time() - t0
    fl = amanatides_woo([x / S for x in o], d, n, "f64")
    bad = next((i for i in range(n + 1) if fl[i] != ex[i]), None)
    print("   trial %d: first differing voxel at step %s of %d (exact sequential %.1f s)" % (trial, bad, n, te))
