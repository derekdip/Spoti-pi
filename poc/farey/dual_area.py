"""Extending the Doan-Li-Nguyen dual-area identity (arXiv 2605.14574, Thm 1.3, cusped tori:
Area(B*) = 4 sum_gamma l log coth(l/2) for the norm l) to every surface our gap law covers.

With the norm N = F = l/2 and B* = {lam : <lam, v> <= N(v) for all v}, a corner at a primitive w contributes the
triangle (origin, grad^- N(w), grad^+ N(w)) of area g_w N(w)/2; corners come in pairs +-w. If the gradient of N changes
only by jumps (which the vector Hines identity implies), Area(B*) = sum over curves gamma of g_gamma N(gamma).
In the norm l = 2F this is 4 sum g_gamma l_gamma / 2 ... (cusped: g = 2 log coth(l/2), giving Doan-Li-Nguyen's formula).

Independent check: Area(B*) = (1/2) int_0^{2pi} N*(u_theta)^-2 d theta, N*(u) = max_v <u, v>/N(v) over primitive v,
computed from traces only (no fans, no gap law).
"""
import heapq, sys
import numpy as np, mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from general import kap, sphere_C
mp.mp.dps = 60
F = lambda t: mp.acosh(t / 2)


def curves(C, s, X, Y, n_per_cone=2500):
    X, Y = mp.mpf(X), mp.mpf(Y); B = -(X * Y) + C[2]; c0 = X * X + Y * Y + C[0] * X + C[1] * Y + s; d = mp.sqrt(B * B - 4 * c0)
    Zs = (-B - d) / 2; W = X * Y - kap((1, 1), C) - Zs
    tr = {(1, 0): X, (0, 1): Y, (0, -1): Y, (1, -1): Zs, (1, 1): W}
    out = {(1, 0): X, (0, 1): Y}
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):   # two cones cover all directions mod sign
        h = [(-1.0, 0, e0, e1, opp)]; n = 0
        while h and n < n_per_cone:
            _, _, L, R, o = heapq.heappop(h); m = (L[0] + R[0], L[1] + R[1]); tr[m] = tr[L] * tr[R] - kap(m, C) - tr[o]; out[m] = tr[m]; n += 1
            for (a, b, oo) in ((L, m, R), (m, R, L)):
                heapq.heappush(h, (-float(1 / (tr[a] * tr[b])**2), n, a, b, oo))
    return out


def gap(v, c, C, s):
    """gap at curve v: the classes of its two Farey neighbours are the two classes other than v's own"""
    cls = {(1, 0): C[0], (0, 1): C[1], (1, 1): C[2]}; own = (v[0] % 2, v[1] % 2); km = cls[own]; kx, ky = [cls[k] for k in cls if k != own]
    return mp.log((c * c + km * c + s) / (c * c - 4) + (kx * kx + ky * ky + kx * ky * c) / (c * c - 4)**2)


def run(name, C, s, X, Y):
    cv = curves(C, s, X, Y)
    S = sum(gap(v, c, C, s) * F(c) for v, c in cv.items())
    V = np.array([v for v in cv], dtype=float); Nv = np.array([float(F(c)) for c in cv.values()])
    V = np.vstack([V, -V]); Nv = np.concatenate([Nv, Nv])
    th = np.linspace(0, np.pi, 400001)[:-1]; U = np.stack([np.cos(th), np.sin(th)], 1)   # B* is symmetric: half circle x 2
    Nstar = np.zeros(len(th))
    for i in range(0, len(th), 20000):
        Nstar[i:i + 20000] = np.max(U[i:i + 20000] @ V.T / Nv, axis=1)
    area = 2 * 0.5 * np.sum(Nstar**-2) * (np.pi / len(th))
    print(f"{name}: {len(cv)} curves; sum g N = {mp.nstr(S, 12)}; direct Area(B*) = {area:.12f}; rel. diff {abs(area / float(S) - 1):.1e}")


if __name__ == "__main__":
    z = (0, 0, 0)
    run("modular torus (3, 3), cusped", z, 0, 3, 3)
    run("punctured torus (2.6, 4.1), cusped", z, 0, mp.mpf("2.6"), mp.mpf("4.1"))
    run("one-holed torus k = -20, (3, 5)", z, 20, 3, 5)
    run("torus with cone point k = 1.5, (2.9, 3.6)", z, mp.mpf("-1.5"), mp.mpf("2.9"), mp.mpf("3.6"))
    C, s = sphere_C(*map(mp.mpf, ("2.5", "2.2", "3.0", "2.1"))); run("four-holed sphere (2.5, 2.2, 3.0, 2.1), (9, 11)", C, s, 9, 11)
    C, s = sphere_C(*map(mp.mpf, ("2", "2", "2", "2"))); run("four-punctured sphere (7, 7)", C, s, 7, 7)
