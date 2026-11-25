"""Is c^2 A = 2 pi^2 / 3 universal? Best-first Farey-Schauder refinement on trees with a general mediant rule
    c = a b - k - (trace of the cell's opposite vertex),
which covers the punctured and one-holed torus (k = 0) and the four-punctured sphere
    X^2 + Y^2 + Z^2 - XYZ + 8 (X + Y + Z) + 28 = 0   (k = 8; symmetric point (7, 7, 7)),
whose simple curves are also indexed by Farey slopes. F = arccosh(t/2) is the half-length of the curve of trace t.
Prediction: log E_N = -c sqrt(N) + O(log N) with c = 2 pi / sqrt(6 A), A = (1/2) int_0^1 f^-2 on the slice.
Also: the ball area over the punctured torus's Teichmuller space (root traces a, b; the third from Markoff).

  python3 poc/farey/universal.py sphere|moduli
"""
import heapq, sys
import numpy as np, mpmath as mp
F = lambda t: mp.acosh(t / 2)


def refine(a0, b0, opp0, k, n_max):
    """Cells (a_v, trace left, trace right, opposite trace, heights, slope ends); returns errors and slice values."""
    def cell(a, b, o, X, Y, tx, ty):
        c = a * b - k - o; D = F(a) + F(b) - F(c); return (-(D / (X + Y)), a, b, o, X, Y, tx, ty, c, D)
    h = [cell(a0, b0, opp0, 1, 1, (0, 1), (1, 1))]; errs = []; pts = {mp.mpf(0): F(a0), mp.mpf(1): F(b0)}; negD = 0
    for n in range(n_max):
        neg, a, b, o, X, Y, tx, ty, c, D = heapq.heappop(h); negD += D <= 0; tm = (tx[0] + ty[0], tx[1] + ty[1]); M = X + Y
        pts[mp.mpf(tm[0]) / tm[1]] = F(c) / M
        heapq.heappush(h, cell(a, c, b, X, M, tx, tm)); heapq.heappush(h, cell(c, b, a, M, Y, tm, ty)); errs.append(-h[0][0])
    return errs, pts, negD


def area(pts):
    ts = sorted(pts); return sum((t1 - t0) / (pts[t0] * pts[t1]) for t0, t1 in zip(ts, ts[1:])) / 2


def fit(errs, lo, hi):
    N = np.arange(lo, hi) + 1; y = np.array([float(mp.log(e)) for e in errs[lo:hi]])
    return np.linalg.lstsq(np.stack([np.ones(len(N)), np.sqrt(N), np.log(N)], 1), y, rcond=None)[0]


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "sphere"
    if what == "sphere":
        mp.mp.dps = 400
        for name, a0, b0, o0, k in (("punctured torus (3,3; opposite 3)", 3, 3, 3, 0), ("four-punctured sphere (7,7; opposite 7)", 7, 7, 7, 8)):
            a0, b0, o0 = map(mp.mpf, (a0, b0, o0))
            assert k == 8 or abs(a0**2 + b0**2 + o0**2 - a0 * b0 * o0) < 1e-30
            if k == 8: assert abs(a0**2 + b0**2 + o0**2 - a0 * b0 * o0 + 8 * (a0 + b0 + o0) + 28) < 1e-30
            errs, pts, negD = refine(a0, b0, o0, k, 6000); c0, c1, c2 = fit(errs, 1000, 6000); A = area(pts)
            print(f"{name}: non-positive defects {negD}; fitted c = {-c1:.4f}; 2 pi/sqrt(6A) = {float(2 * mp.pi / mp.sqrt(6 * A)):.4f}; c^2 A = {float(c1 * c1 * A):.4f} (2 pi^2/3 = {float(2 * mp.pi**2 / 3):.4f}); A = {mp.nstr(A, 8)}")
    else:
        mp.mp.dps = 60
        rows = []
        for a0 in np.linspace(2.02, 3.0, 25):
            for b0 in np.linspace(2.02, 4.5, 40):
                if b0 < a0: continue
                a, b = mp.mpf(a0), mp.mpf(b0); disc = (a * b)**2 - 4 * (a * a + b * b)
                if disc < 0: continue
                o, cf = (a * b - mp.sqrt(disc)) / 2, (a * b + mp.sqrt(disc)) / 2   # traces of e0 - e1 and e0 + e1
                if o < 2 or o < b: continue      # fundamental domain: a <= b <= o (the root triple sorted, o the third)
                _, p1, _ = refine(a, b, o, 0, 1500); _, p2, _ = refine(a, b, cf, 0, 1500)   # cones (e0, e1) and (e0, -e1)
                Ah = area(p1) + area(p2); rows.append((a0, b0, float(o), float(Ah), float(2 * mp.pi / mp.sqrt(6 * Ah))))
        rows.sort(key=lambda r: r[3])
        print("triple (a, b, o) of e0, e1, e0 - e1, sorted: half-ball area A (all directions up to sign), rate c = 2 pi/sqrt(6A); smallest A first")
        for r in rows[:6] + [None] + rows[-4:]:
            print("  ..." if r is None else f"  ({r[0]:.2f}, {r[1]:.2f}, {r[2]:.2f}): A = {r[3]:.4f}, c = {r[4]:.3f}")
        print("modular torus (3, 3, 3) for reference:", end=" "); a = b = o = mp.mpf(3); cf = mp.mpf(6)
        _, p1, _ = refine(a, b, o, 0, 1500); _, p2, _ = refine(a, b, cf, 0, 1500); Ah = area(p1) + area(p2); print(f"A = {float(Ah):.4f}, c = {float(2 * mp.pi / mp.sqrt(6 * Ah)):.3f}")
