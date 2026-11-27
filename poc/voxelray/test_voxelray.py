import random, time
from fractions import Fraction as Fr
from voxelray import Ray, brute_events, amanatides_woo
rnd = random.Random(5)
def rand_ray(big=False):
    S = rnd.randint(1, 50) if not big else 10**6 + rnd.randint(0, 999)
    o = [rnd.randint(-5 * S, 5 * S) for _ in range(3)]
    d = [rnd.randint(-30, 30) for _ in range(3)] if not big else [rnd.randint(-10**6, 10**6) for _ in range(3)]
    if not any(d): d[0] = 1
    if rnd.random() < 0.2: o = [S * rnd.randint(-5, 5) for _ in range(3)]          # integer start: many ties
    if rnd.random() < 0.2: d = [rnd.choice([0, 1, -1, 2]) * rnd.randint(1, 3) for _ in range(3)] or [1, 1, 1]
    if not any(d): d = [1, 1, 1]
    return Ray(o, S, d)
def test_sequential():
    for _ in range(600):
        r = rand_ray(); n = rnd.randint(1, 120)
        assert r.traverse(n) == brute_events(r, n)
    print("sequential exact DDA = independent event sort: 600 random rays (incl. ties, axis-parallel)")
def test_random_access():
    for _ in range(300):
        r = rand_ray(); n = 150; seq = r.traverse(n)
        for k in rnd.sample(range(n + 1), 25): assert r.voxel_at(k) == seq[k], (k,)
    print("random access voxel_at(k) = sequential: 300 rays x 25 positions")
def test_chunks():
    for _ in range(100):
        r = rand_ray(); n = 200; seq = r.traverse(n); cs = 37; got = []
        for k0 in range(0, n, cs):
            ch = r.traverse_chunk(k0, min(cs, n - k0)); got += ch if not got else ch[1:]
        assert got == seq
    print("parallel chunks (independent starts) concatenate to the sequential traversal: 100 rays")
def test_connectivity():
    for _ in range(200):
        r = rand_ray(); p = r.traverse(100)
        assert all(sum(abs(a - b) for a, b in zip(p[i], p[i + 1])) == 1 for i in range(100))
        q = r.traverse(100, "all"); assert all(max(abs(a - b) for a, b in zip(q[i], q[i + 1])) == 1 for i in range(100))
    print("'face' paths 6-connected, 'all' paths 26-connected")
def test_long_and_float():
    rows = []
    for trial in range(6):
        r = rand_ray(big=True); n = 200000
        t0 = time.time(); ex = r.traverse(n); te = time.time() - t0
        o = [x / r.S for x in r.o]
        res = []
        for dt in ("f64", "f32"):
            fl = amanatides_woo(o, r.d, n, dt)
            bad = next((i for i in range(n + 1) if fl[i] != ex[i]), None); res.append(bad)
        t0 = time.time(); va = r.voxel_at(n); tr = time.time() - t0
        assert va == ex[n]
        rows.append((res[0], res[1], te, tr))
        print("   ray %d: first wrong voxel float64 DDA at step %s, float32 at step %s; exact sequential %.2f s; random access to step %d in %.2f ms" % (
            trial, res[0], res[1], te, n, 1e3 * tr))
    print("long rays: exact traversal vs floating-point Amanatides-Woo")
if __name__ == "__main__":
    for f in (test_sequential, test_random_access, test_chunks, test_connectivity, test_long_and_float):
        t0 = time.time(); f(); print("   (%.1f s)" % (time.time() - t0))
