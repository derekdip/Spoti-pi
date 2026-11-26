"""Partial (twist) average of simple-geodesic counts on a cusped one-holed torus.

Fenchel-Nielsen (a, tau) for alpha; the full Dehn twist tau -> tau + a maps class (r, q) to (r + q, q). Unfolding:
    <F(R)>_tau = w(a) + (1/a) sum_{q>=1} sum_{r in (Z/q)^*} int_R w(l_{r,q}(tau)) dtau
for any weight w; here the Riesz weight w(l) = (R - l)_+, which makes the sum over zeros converge.
Flat analogue (exact): (1/a) sum_q phi(q) f(R/q) -> explicit formula over zeta zeros only, no lattice error.
Here: compute the hyperbolic twist average exactly (traces of Christoffel words), and compare its residual with
the single-surface residual.
"""
import math, numpy as np, mpmath as mp
a = 2 * math.log((3 + math.sqrt(5)) / 2)        # alpha = e0 of the modular torus: trace 3
lam = math.exp(a / 2); K = 1 / math.tanh(a / 2)  # cusp: y(tau) = 2K cosh(tau/2), z(tau) = 2K cosh((tau+a)/2)
RMAX = 150.0
def traces_word(r, q, taus):
    """trace of the (r, q) Christoffel word in A (alpha) and B (beta_tau), vectorised over tau."""
    y = 2 * K * np.cosh(taus / 2); z = 2 * K * np.cosh((taus + a) / 2)
    p = (z - y / lam) / (lam - 1 / lam); s = y - p
    # B = [[p, 1], [p s - 1, s]], A = diag(lam, 1/lam)
    M = [np.ones_like(taus), np.zeros_like(taus), np.zeros_like(taus), np.ones_like(taus)]
    def mulB(M):
        m00, m01, m10, m11 = M; b10 = p * s - 1
        return [m00 * p + m01 * b10, m00 + m01 * s, m10 * p + m11 * b10, m10 + m11 * s]
    def mulA(M, k):
        m00, m01, m10, m11 = M; f = lam ** k
        return [m00 * f, m01 / f, m10 * f, m11 / f]
    for i in range(1, q + 1):
        M = mulB(M); k = (i * r) // q - ((i - 1) * r) // q
        if k: M = mulA(M, k)
    return np.abs(M[0] + M[3])
L = lambda t: 2 * np.arccosh(np.maximum(t, 2.0) / 2)

# sanity: the Markoff trace at tau = 0 for (0,1), (1,1)
t0 = np.array([0.0]); print("traces at tau=0: alpha %.6f, beta %.6f, alpha*beta %.6f" % (2 * math.cosh(a / 2), traces_word(0, 1, t0)[0], traces_word(1, 1, t0)[0]))
Rs = np.linspace(8, RMAX, 1500)
F = np.maximum(Rs - a, 0)        # q = 0: alpha itself
qmax = 0; npairs = 0; rdep = []
for q in range(1, 400):
    best = None
    for r in range(q):
        if math.gcd(r, q) != 1: continue
        # convex in tau; minimum near tau ~ -(r/q) a
        c = -(r / q) * a - a / 2
        T = RMAX / q + 6
        taus = np.arange(c - T, c + T, 0.004)
        l = L(traces_word(r, q, taus))
        lm = l.min()
        if lm > RMAX: continue
        best = lm if best is None else min(best, lm)
        ls = np.sort(l[l < RMAX]); cs = np.concatenate([[0], np.cumsum(ls)])
        n = np.searchsorted(ls, Rs)
        F += (n * Rs - cs[n]) * 0.004 / a
        npairs += 1
        if q in (7, 20): rdep.append((q, r, lm, np.sum(np.maximum(100 - l, 0)) * 0.004))
    if best is None: break
    qmax = q
print("pairs used: %d, q up to %d" % (npairs, qmax))
for q in (7, 20):
    v = np.array([x[3] for x in rdep if x[0] == q]); mn = np.array([x[2] for x in rdep if x[0] == q])
    print("q = %d: r-dependence of min length: %.6f..%.6f; of the Riesz integral at R=100: rel. spread %.2e" % (q, mn.min(), mn.max(), (v.max() - v.min()) / v.mean()))
np.save("poc/farey/twist_average.npy", np.array([Rs, F]))
