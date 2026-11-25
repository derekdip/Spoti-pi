"""The rate law with mixed parity classes: a proof sketch and a test.

(1) Detail asymptotics. Torus (no linear terms): cosh(N(L+R)) = cosh N(L) cosh N(R) + sinh N(L) sinh N(R) cos(theta),
    sin^2 theta = 4(4 - mu)/((a^2 - 4)(b^2 - 4)), so D = N(L) + N(R) - N(L+R) = (4 - mu) e^{-2 N(m)} (1 + o(1)) x Theta(1):
    kappa = 2. With a linear coefficient kappa_m != 0 on the mediant's class, c = ab - kappa_m - o, D ~ kappa_m/(ab) =
    Theta(e^{-N(m)}): kappa = 1 for that class.
(2) Counting. Best-first refinement by a_v = D_v/M_v refines, up to an O(log L) band, the primitive m with
    kappa(class m) N(m) < L, where E_N = e^{-L}. Primitive vectors equidistribute over the three classes mod 2, so
    N = (1/3)(6/pi^2) A L^2 sum_i kappa_i^-2 + O(L log L),   A = area of the norm ball in the cone.
    Hence log E_N = -c sqrt(N) + O(log N) with   c^2 A = 3 zeta(2) / sum_i kappa_i^-2.
Uniform kappa: kappa^2 zeta(2) (the earlier law). Mixed (2, 2, 1): 2 zeta(2). Mixed (2, 1, 1): (4/3) zeta(2).
"""
import heapq, sys
import numpy as np, mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from general import kap, sphere_C
mp.mp.dps = 400
F = lambda t: mp.acosh(t / 2)


def refine(C, s, X, Y, n_max):
    X, Y = mp.mpf(X), mp.mpf(Y); B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(B * B - 4 * c0)
    tr = {(1, 0): X, (0, 1): Y, (1, -1): (-B - d) / 2}
    def cell(L, R, o):
        m = (L[0] + R[0], L[1] + R[1]); c = tr[L] * tr[R] - kap(m, C) - tr[o]; tr[m] = c
        D = F(tr[L]) + F(tr[R]) - F(c); return (-(D / (m[0] + m[1])), L, R, o, m, D)
    h = [cell((1, 0), (0, 1), (1, -1))]; errs = []; pts = {mp.mpf(0): F(X), mp.mpf(1): F(Y)}; negD = 0
    for n in range(n_max):
        neg, L, R, o, m, D = heapq.heappop(h); negD += D <= 0
        pts[mp.mpf(m[1]) / (m[0] + m[1])] = F(tr[m]) / (m[0] + m[1])
        heapq.heappush(h, cell(L, m, R)); heapq.heappush(h, cell(m, R, L)); errs.append(-h[0][0])
    ts = sorted(pts); A = sum((t1 - t0) / (pts[t0] * pts[t1]) for t0, t1 in zip(ts, ts[1:])) / 2
    return errs, A, negD


def fit(errs, lo, hi):
    N = np.arange(lo, hi) + 1; y = np.array([float(mp.log(e)) for e in errs[lo:hi]])
    return np.linalg.lstsq(np.stack([np.ones(len(N)), np.sqrt(N), np.log(N)], 1), y, rcond=None)[0]


if __name__ == "__main__":
    z2 = float(mp.zeta(2))
    cases = [("punctured torus (3, 3)", (0, 0, 0), 0, 3, 3),
             ("four-punctured sphere (7, 7)", *sphere_C(2, 2, 2, 2), 7, 7),
             ("k-Markoff (1, 2, 3): tau root (8, 7)", *sphere_C(2, 3, 1, 2), 8, 7),
             ("k-Markoff (0, 0, 5): classes (0, 0, 10)", *sphere_C(0, 5, 0, 2), 8, 8),
             ("k-Markoff (0, 0, 1): classes (0, 0, 2)", *sphere_C(0, 1, 0, 2), 5, 5),
             ("cubic (p, q, r) = (0, 3, 5), s = 80: root (8, 9)", (0, 3, 5), 80, 8, 9)]
    for name, C, s, X, Y in cases:
        C = tuple(mp.mpf(c) for c in C); s = mp.mpf(s)
        kap_eff = [2 if c == 0 else 1 for c in C]; pred = 3 * z2 / sum(k**-2 for k in kap_eff)
        errs, A, negD = refine(C, s, X, Y, 9000)
        for lo, hi in ((1000, 5000), (3000, 9000)):
            c0, c1, c2 = fit(errs, lo, hi)
            print(f"{name}: classes kappa (p, q, r) = ({', '.join(mp.nstr(c, 3) for c in C)}) -> effective {tuple(kap_eff)}; "
                  f"fit N in [{lo}, {hi}): c = {-c1:.4f}, log N coeff {c2:.3f}; c^2 A = {c1 * c1 * float(A):.4f}; predicted 3 zeta(2)/sum kappa^-2 = {pred:.4f}; non-positive defects {negD}")


def detail_check():
    """Cell by cell: is -log D = N(m) (1 + rho) + O(1), with rho as in the refined law?
    zero-class mediant, one nonzero neighbour class: rho = N(zero-class endpoint)/N(m);
    zero-class mediant, both neighbours nonzero: rho = min(N(L), N(R))/N(m); nonzero class: rho = 0; pure torus: rho = 1."""
    for name, C, s, X, Y in (("k-Markoff (0, 0, 5)", *sphere_C(0, 5, 0, 2), 8, 8), ("cubic (0, 3, 5), s = 80", (0, 3, 5), 80, 8, 9),
                             ("punctured torus", (0, 0, 0), 0, 3, 3), ("four-punctured sphere", *sphere_C(2, 2, 2, 2), 7, 7)):
        C = tuple(mp.mpf(c) for c in C); s = mp.mpf(s)
        X, Y = mp.mpf(X), mp.mpf(Y); B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(B * B - 4 * c0)
        tr = {(1, 0): X, (0, 1): Y, (1, -1): (-B - d) / 2}; level = [((1, 0), (0, 1), (1, -1))]; resid = {}
        mp.mp.dps = 700
        for depth in range(1, 13):
            nxt = []
            for (L, R, o) in level:
                m = (L[0] + R[0], L[1] + R[1]); tr[m] = tr[L] * tr[R] - kap(m, C) - tr[o]; nxt += [(L, m, R), (m, R, L)]
                if depth < 8: continue
                Nm, NL, NR = F(tr[m]), F(tr[L]), F(tr[R]); D = NL + NR - Nm
                zero = lambda v: kap(v, C) == 0
                if all(c == 0 for c in C): pred = 2 * Nm
                elif not zero(m): pred = Nm
                elif zero(L) or zero(R): pred = Nm + (NL if zero(L) else NR)
                else: pred = Nm + min(NL, NR)
                key = "nonzero class" if not zero(m) else ("zero class" if not all(c == 0 for c in C) else "torus")
                resid.setdefault(key, []).append(float(-mp.log(D) - pred) / float(Nm))
            level = nxt
        print(f"{name}: (-log D - predicted exponent)/N(m) over cells at depths 8-12:", "; ".join(f"{k}: mean {np.mean(v):+.4f}, max |.| {np.max(np.abs(v)):.4f} ({len(v)} cells)" for k, v in resid.items()))


if __name__ == "__main__":
    z2 = float(mp.zeta(2))
    print(f"refined law: pattern (2,2,1): 3 zeta(2)/2 = {1.5 * z2:.4f};  pattern (2,1,1): 9 zeta(2)/8 = {9 * z2 / 8:.4f}")
    detail_check()
