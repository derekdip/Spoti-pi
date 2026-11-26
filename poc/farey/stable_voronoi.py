"""Fourier transform of Phi(N) for the stable norm N of the modular torus, as a sum over simple geodesics.

Claim (exact):  F[Phi(N)](xi) = (1/2 pi i) sum_{v primitive, both signs} G(v) <v,xi> K(<v,xi>/N(v)) / (<J n_v^+, xi> <J n_v^-, xi>)
  G(v) = 2 log(t^2/(t^2-4)) (gap law, N = l normalization), n^+-n^- = G(v) J v, K(a) = int_0^inf Phi(t) e^{-2 pi i t a} dt,
  n_v^+: <n,v> = N(v), <n,w> = c(v,w);  n_v^-: <n,v> = N(v), <n,-w> = c(v,-w);  w the ccw neighbour (det(v,w) = 1),
  c(v,+-w) = 2 log[(t_{v+-w} - t_w e^{-N(v)/2}) / sqrt(t_v^2 - 4)].
Tests with Phi(t) = e^{-t}, K(a) = 1/(1 + 2 pi i a):
 (1) corner sum with B's closed-form data vs the exact FT of the polygon hull of many corners (face formula);
 (2) brute-force 2D quadrature at one xi;
 (3) Poisson: sum_{x in Z^2} e^{-eps N(x)} = eps^-2 sum_xi Fhat(xi/eps)."""
import math, numpy as np, sys
sys.setrecursionlimit(10000)
TMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
L = lambda t: 2 * math.acosh(t / 2) if t < 1e300 else 2 * math.log(t)
J = lambda x: np.array([-x[1], x[0]])
corners = []   # (v, N, G, n+, n-)
def add(v, w, tv, tw, tvpw, tvmw):
    N = L(tv); e = math.exp(-N / 2); s = math.sqrt(tv * tv - 4.0)
    cp = 2 * math.log((tvpw - tw * e) / s); cm = 2 * math.log((tvmw - tw * e) / s)
    Mv = np.array([[v[0], v[1]], [w[0], w[1]]], float)
    npl = np.linalg.solve(Mv, [N, cp]); nmi = np.linalg.solve(Mv, [N, -cm])
    G = 2 * math.log(tv * tv / (tv * tv - 4.0))
    corners.append((np.array(v, float), N, G, npl, nmi))
def cone(u, w, tu, tw, td):
    tm = tu * tw - td
    if L(tm) > TMAX: return
    m = (u[0] + w[0], u[1] + w[1])
    add(m, w, tm, tw, tm * tw - tu, tu)        # neighbour w: m+w has trace tm tw - tu, m-w = u
    cone(u, m, tu, tm, tw); cone(m, w, tm, tw, tu)
add((1, 0), (0, 1), 3, 3, 3, 6); add((0, 1), (-1, 0), 3, 3, 6, 3); add((1, 1), (0, 1), 3, 3, 6, 3)
cone((1, 0), (1, 1), 3, 3, 3); cone((1, 1), (0, 1), 3, 3, 3); cone((0, 1), (-1, 0), 3, 3, 3)
corners += [(-v, N, G, -npl, -nm) for v, N, G, npl, nm in list(corners)]   # rotation by pi keeps the ccw order
print("corners (both signs) with N <= %g: %d" % (TMAX, len(corners)))
# consistency of the closed forms: jump = G J v, and the gradient is the same from neighbouring corners
err = max(np.abs((npl - nm) - G * J(v)).max() for v, N, G, npl, nm in corners)
print("max | (n+ - n-) - G J v | = %.2e" % err)
V = np.array([c[0] for c in corners]); Nv = np.array([c[1] for c in corners]); Gv = np.array([c[2] for c in corners])
NP = np.array([c[3] for c in corners]); NM = np.array([c[4] for c in corners])
K = lambda a: 1 / (1 + 2j * math.pi * a)
def fhat_B(xi, Tcut=TMAX):
    k = (Nv <= Tcut); vx = V[k] @ xi
    den = (np.array([J(n) @ xi for n in NP[k]]) * np.array([J(n) @ xi for n in NM[k]]))
    return np.sum(Gv[k] * vx * K(vx / Nv[k]) / den) / (2j * math.pi)
# polygon hull of corners with N <= T: exact face formula
def fhat_poly(xi, T):
    k = Nv <= T; P = V[k] / Nv[k][:, None]; P = P[np.argsort(np.arctan2(P[:, 1], P[:, 0]))]
    Q = np.roll(P, -1, axis=0); a1 = P @ xi; a2 = Q @ xi; det = P[:, 0] * Q[:, 1] - P[:, 1] * Q[:, 0]
    return np.sum(det * (K(a1) - K(a2)) / (2j * math.pi * (a2 - a1)))
xis = [np.array(x, float) for x in ((1, 0), (0.37, 0.81), (2, -1), (3.3, 1.7), (0.5, 0.05))]
print("\n(1) corner sum with B's closed-form data vs polygon hulls")
for xi in xis:
    print("   xi = (%.2f, %.2f):  B-corners (N<=8, 16, %g): %s   polygons (N<=8, 16, %g): %s" % (xi[0], xi[1], TMAX,
          "  ".join("%.10f" % fhat_B(xi, T).real for T in (8, 16, TMAX)), TMAX, "  ".join("%.10f" % fhat_poly(xi, T).real for T in (8, 16, TMAX))))
# (2) brute force at one xi: integrate e^{-N(x)} cos(2 pi x.xi) on a grid, N = gauge of the N<=TMAX polygon
k = Nv <= 20; P = V[k] / Nv[k][:, None]; P = P[np.argsort(np.arctan2(P[:, 1], P[:, 0]))]; Q = np.roll(P, -1, axis=0)
nrm = np.stack([Q[:, 1] - P[:, 1], P[:, 0] - Q[:, 0]], 1); nrm /= np.sum(nrm * P, 1)[:, None]
h = 0.02; g = np.arange(-40, 40 + h, h); X, Y = np.meshgrid(g, g)
Ng = np.zeros_like(X)
for nx, ny in nrm: Ng = np.maximum(Ng, nx * X + ny * Y)
xi = xis[1]; bf = np.sum(np.exp(-Ng) * np.cos(2 * math.pi * (X * xi[0] + Y * xi[1]))) * h * h
print("\n(2) brute-force quadrature at xi = (0.37, 0.81): %.8f   corner formula: %.8f   (int e^-N = 2 Area: %.8f vs %.8f)" % (
    bf, fhat_B(xi).real, np.sum(np.exp(-Ng)) * h * h, 2 * 0.891803166))
# (3) Poisson summation
print("\n(3) Poisson: sum_x e^{-eps N(x)} vs eps^-2 sum_xi Fhat(xi/eps)  (vectorised; dual truncated at max|xi_i| <= M)")
Np = Nv[: len(Nv) // 2]
JP = np.stack([-NP[:, 1], NP[:, 0]], 1); JM = np.stack([-NM[:, 1], NM[:, 0]], 1)
for eps in (1.0, 0.5):
    lhs = 1 + 2 * np.sum(1 / np.expm1(eps * Np))
    out = []
    for M in (30, 60, 120, 240):
        a_ = np.arange(-M, M + 1); A_, B_ = np.meshgrid(a_, a_); XI = np.stack([A_.ravel(), B_.ravel()], 1).astype(float)
        XI = XI[np.any(XI != 0, axis=1)] / eps
        tot = 0.0
        for c0 in range(0, len(V), 64):
            sl = slice(c0, c0 + 64)
            vx = XI @ V[sl].T; den = (XI @ JP[sl].T) * (XI @ JM[sl].T)
            tot += np.sum((Gv[sl] * vx * (1 / (1 + 2j * math.pi * vx / Nv[sl])) / den).real) / (2 * math.pi) * 0 + np.sum((Gv[sl] * vx / (1 + 2j * math.pi * vx / Nv[sl]) / den / (2j * math.pi)).real)
        out.append((M, (2 * 0.891803166008 + tot) / eps ** 2))
    print("   eps = %.2f: lattice side %.10f;  dual side: %s" % (eps, lhs, "  ".join("M=%d: %.10f (diff %.1e)" % (M, d, lhs - d) for M, d in out)))
