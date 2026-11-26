"""Twisted horocycles on Y_1(N) and zeros of Dirichlet L-functions.

For an even primitive character chi mod N, f_chi(z) = sum_{Gamma_inf \\ Gamma} chi(c) psi(Im gamma z) (psi = exp(-1/t))
is Gamma_1(N)-invariant (c mod N is preserved by right multiplication by Gamma_1(N)), so f_chi lives on Y_1(N).
The closed horocycle of height y at the cusp infinity (width 1) gives, by the same Farey unfolding as for zeta:
    a_chi(y) = sqrt(pi y) * sum_{c>=1} chi(c) phi(c)/c * exp(-c^2 y)        (mean 0 for chi != 1)
Mellin: L(2s-1,chi)/L(2s,chi) * sqrt(pi) Gamma(s-1/2). The poles at the zeros rho of L(s,chi) give
    a_chi(y) = sum_rho R_rho y^(1-rho/2) + sum_{k>=0} T_k y^(1+k),
    R_rho = sqrt(pi) L(rho-1,chi) Gamma((rho-1)/2) / (2 L'(rho,chi)),  T_k = sqrt(pi) L(-2k-1,chi) Gamma(-k-1/2) / (2 L'(-2k,chi)).
GRH for chi  <=>  a_chi(y) = O(y^(3/4 - eps)).
"""
import numpy as np, mpmath as mp
mp.mp.dps = 25
NMAX = 4_000_000
phi = np.arange(NMAX + 1, dtype=np.int64)
for p in range(2, NMAX + 1):
    if phi[p] == p:
        phi[p::p] -= phi[p::p] // p
cc = np.arange(1, NMAX + 1)
base = phi[1:].astype(np.longdouble) / cc.astype(np.longdouble)
c2 = cc.astype(np.longdouble) ** 2

def char_table(N, gen, order, k):
    """chi(gen^j) = exp(2 pi i k j / order); gen a primitive root mod N."""
    t = [0j] * N; x = 1
    for j in range(order):
        t[x] = complex(mp.exp(2j * mp.pi * k * j / order)); x = x * gen % N
    return t

CHARS = {
    "chi_5 (Legendre mod 5, real)": char_table(5, 2, 4, 2),
    "chi_8 (Kronecker mod 8, real)": [0, 1, 0, -1, 0, -1, 0, 1],
    "chi_7 cubic (complex)": char_table(7, 3, 6, 2),
    "chi_13 sextic (complex)": char_table(13, 2, 12, 2),
}

def zeros_on_line(chi, T=60, step=0.02):
    """zeros of L(1/2+it, chi), |t| < T: local minima of |L| on a grid, refined by findroot (complex)."""
    ts = np.arange(-T, T, step)
    v = [abs(mp.dirichlet(mp.mpc(0.5, t), chi)) for t in ts]
    out = []
    for i in range(1, len(ts) - 1):
        if v[i] < v[i - 1] and v[i] < v[i + 1] and v[i] < 0.3:
            r = mp.findroot(lambda s: mp.dirichlet(s, chi), mp.mpc(0.5, ts[i]))
            if abs(mp.dirichlet(r, chi)) < 1e-15 and 0.1 < r.real < 0.9 and all(abs(r - q) > 1e-6 for q in out):
                out.append(r)
    return sorted(out, key=lambda r: abs(r.imag))

def a_measured(chi, y):
    N = len(chi); y = np.longdouble(y)
    n = int(min(NMAX, np.sqrt(80 / float(y))))
    ch = np.array(chi, dtype=np.clongdouble)[cc[:n] % N]
    e = base[:n] * np.exp(-c2[:n] * y)
    return complex(np.sqrt(np.longdouble(np.pi) * y) * np.sum(ch * e))

for name, chi in CHARS.items():
    N = len(chi)
    assert abs(chi[N - 1] - 1) < 1e-12, "need an even character"
    Z = zeros_on_line(chi)
    R = [mp.sqrt(mp.pi) * mp.dirichlet(r - 1, chi) * mp.gamma((r - 1) / 2) / (2 * mp.dirichlet(r, chi, derivative=1)) for r in Z]
    Tk = [mp.sqrt(mp.pi) * mp.dirichlet(-2 * k - 1, chi) * mp.gamma(-k - mp.mpf(1) / 2) / (2 * mp.dirichlet(-2 * k, chi, derivative=1)) for k in range(5)]
    off = max(abs(r.real - 0.5) for r in Z)
    print("\n=== %s, N = %d: %d zeros with |t| < 60, max |Re rho - 1/2| = %.1e; lowest |t| = %s" % (
        name, N, len(Z), off, ", ".join("%.5f" % r.imag for r in Z[:4])))
    print("    |R| of lowest zeros:", " ".join("%.2e" % abs(x) for x in R[:4]))
    def pred(y):
        y = mp.mpf(y)
        return complex(sum(Rr * y ** (1 - r / 2) for Rr, r in zip(R, Z)) + sum(t * y ** (1 + k) for k, t in enumerate(Tk)))
    ys = np.logspace(-2, -11, 28)
    worst = 0; env = {}
    print("      y        |a_chi(y)|        |a - prediction|     |a|/y^(3/4)")
    for i, y in enumerate(ys):
        a = a_measured(chi, y); d = abs(a - pred(y)); worst = max(worst, d)
        if i % 3 == 0:
            print("  %.2e   %.6e   %.3e       %.4e" % (y, abs(a), d, abs(a) / y ** 0.75))
    print("    max |measured - predicted| = %.1e" % worst)
    yy = np.logspace(-4, -11, 350)
    triv = lambda y: complex(sum(t * mp.mpf(y) ** (1 + k) for k, t in enumerate(Tk)))
    A = np.array([abs(a_measured(chi, y) - triv(y)) for y in yy]) / yy ** 0.75
    dec = [A[(yy <= 10.0 ** -k) & (yy > 10.0 ** -(k + 1))].max() for k in range(4, 11)]
    print("    trivial-zero terms: T_0 y with |T_0| = %.3e; nontrivial part E = a - sum T_k y^(1+k)" % abs(Tk[0]))
    print("    max |E|/y^(3/4) per decade 1e-4..1e-11:", " ".join("%.3e" % d for d in dec), "  (bound sum|R_rho| = %.3e)" % sum(abs(x) for x in R))
    print("    max |E|/y^(1/2) at 1e-4 vs 1e-11: %.2e -> %.2e" % (A[:30].max() * 1e-4 ** 0.25, A[-30:].max() * 1e-11 ** 0.25))
