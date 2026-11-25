"""The convergence rate of best-first Farey-Schauder refinement, predicted from the count of Markov numbers.

The Farey note (section 10) fitted log E_N ~ 0.478 - 3.312 sqrt(N) - 0.538 log N for the sup error after N
best-first refinements of the stable norm on the projective slice. Prediction, derived before this run: the
error after N refinements is set by the largest remaining normalised detail a_v = D_v/M_v, which decays like
1/m^2 in the Markov number m of the cell's mediant; the Markov numbers up to x number about C (log x)^2
(Zagier, C = 0.180717...), and the slice meets each Markov number twice (once each side of 1/2), so
N ~ 2C (log m)^2 and E_N ~ exp(-sqrt(2/C) sqrt(N)), sqrt(2/C) = 3.3267.

Here: exact best-first refinement on the modular torus (root traces 3, 3 at directions (1,0), (0,1)), the
refinement order by largest a_v, the error E_N = the largest a_v left on the frontier (the note's lower
certificate, attained at that cell's mediant); fits of log E_N against sqrt(N) and log N; and the count of
Markov numbers below x from the same tree, to estimate C directly.
"""
import heapq, sys
import mpmath as mp
mp.mp.dps = 400
F = lambda t: mp.acosh(t / 2)
child = lambda a, b: a * b / 2 * (1 + mp.sqrt(1 - 4 / a**2 - 4 / b**2))


def refine(n_max, a0=mp.mpf(3), b0=mp.mpf(3)):
    """Cells: (a_v, trace left, trace right, height left, height right). Heights X = p + q on the slice."""
    def cell(a, b, X, Y):
        c = child(a, b); M = X + Y; D = F(a) + F(b) - F(c); return (-(D / M), a, b, X, Y, c)
    h = [cell(a0, b0, 1, 1)]; errs = []; traces = []
    for n in range(n_max):
        neg, a, b, X, Y, c = heapq.heappop(h); traces.append(c)
        heapq.heappush(h, cell(a, c, X, X + Y)); heapq.heappush(h, cell(c, b, X + Y, Y))
        errs.append(-h[0][0])
    return errs, traces


def fit(errs, lo, hi):
    """Least squares of log E_N on [1, sqrt N, log N] over N in [lo, hi)."""
    import numpy as np
    N = np.arange(lo, hi) + 1; y = np.array([float(mp.log(e)) for e in errs[lo:hi]])
    A = np.stack([np.ones_like(N, dtype=float), np.sqrt(N), np.log(N)], 1); coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


def refine_mu(n_max, mu, a0=mp.mpf(4), b0=mp.mpf(4)):
    """As refine(), for x^2 + y^2 + z^2 - xyz = mu, with the slice values f at every node, for the area."""
    ch = lambda a, b: (a * b + mp.sqrt(a * a * b * b - 4 * (a * a + b * b - mu))) / 2
    def cell(a, b, X, Y, tx, ty):
        c = ch(a, b); M = X + Y; D = F(a) + F(b) - F(c); return (-(D / M), a, b, X, Y, c, tx, ty)
    h = [cell(a0, b0, 1, 1, (0, 1), (1, 1))]; errs = []; pts = {mp.mpf(0): F(a0), mp.mpf(1): F(b0)}; logt = []
    for n in range(n_max):
        neg, a, b, X, Y, c, tx, ty = heapq.heappop(h); tm = (tx[0] + ty[0], tx[1] + ty[1]); M = X + Y
        pts[mp.mpf(tm[0]) / tm[1]] = F(c) / M; logt.append(mp.log(c))
        heapq.heappush(h, cell(a, c, X, M, tx, tm)); heapq.heappush(h, cell(c, b, M, Y, tm, ty)); errs.append(-h[0][0])
    return errs, pts, logt


def area_quadrant(pts):
    """A = (1/2) int_0^1 f(t)^-2 dt over the slice, f linear between refined nodes (f is convex: the nodes are dense)."""
    ts = sorted(pts); A = mp.mpf(0)
    for t0, t1 in zip(ts, ts[1:]):
        f0, f1 = pts[t0], pts[t1]; A += (t1 - t0) / (f0 * f1)    # exact integral of (linear f)^-2 between nodes
    return A / 2


if __name__ == "__main__":
    import numpy as np
    for mu in (0, -2, -8, -20):
        mu = mp.mpf(mu); a0 = mp.mpf(3) if mu == 0 else mp.mpf(4)
        errs, pts, logt = refine_mu(6000, mu, a0, a0)
        c0, c1, c2 = fit(errs, 1000, 6000)
        # complete count of tree nodes up to trace 1e14 (not the refined set, which follows a_v, not the trace)
        ch = lambda a, b: (a * b + mp.sqrt(a * a * b * b - 4 * (a * a + b * b - mu))) / 2; st = [(a0, a0)]; Fs = []
        while st:
            a, b = st.pop(); c = ch(a, b)
            if c <= mp.mpf(10)**14: Fs.append(float(F(c))); st += [(a, c), (c, b)]
        Fs = np.sort(Fs); n = np.arange(1, len(Fs) + 1); k = slice(len(Fs) // 3, None); Cnode = float(np.polyfit(Fs[k], np.sqrt(n[k]), 1)[0]) ** 2
        A = area_quadrant(pts); pred_area = 2 * mp.pi / mp.sqrt(6 * A)
        print(f"mu = {int(mu):>4}: fitted rate {-c1:.4f}; from the node count 2/sqrt(C) = {2 / np.sqrt(Cnode):.4f}; from the ball area 2 pi/sqrt(6A) = {float(pred_area):.4f} (A = {mp.nstr(A, 8)})")
    print("cusp, Zagier: sqrt(2/C), C = 0.180717047:", f"{float(mp.sqrt(2 / mp.mpf('0.180717047'))):.4f}")
