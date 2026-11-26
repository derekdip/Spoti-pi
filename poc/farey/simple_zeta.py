"""Simple closed geodesics on the modular torus as primitive lattice points of the stable-norm ball.

McShane-Rivin: simple closed geodesics <-> primitive v in Z^2 mod sign, with l(gamma_v) = N(v), N the stable norm
(convex, homogeneous). Homogeneity + Moebius give the exact identity
    D(s) := sum_{gamma simple} l^-s = Z_B(s) / (2 zeta(s)),     Z_B(s) := sum_{v in Z^2 \\ 0} N(v)^-s,
and the counting identities  A(R) := #{v != 0 : N(v) <= R} = sum_{k>=1} 2 P(R/k),  P(R) = (1/2) sum_d mu(d) A(R/d).
Here: enumerate the Markoff tree (traces 3,3,3), check the main terms Area(B) R^2 and (3/pi^2) Area(B) R^2,
and measure the error exponents of A and P.
"""
import math, sys, numpy as np
sys.setrecursionlimit(100000)
RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 160.0
ell = lambda t: 2 * math.acosh(t / 2) if t < 1e300 else 2 * (math.log(t))  # t integer trace
def L(t):
    return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)  # never reached at these R

prim = []        # lengths of primitive classes mod sign
area_half = 0.0
def cone(u, w, tu, tw, td):
    """cone between u, w (det 1); td = trace of u - w. Mediant trace tu*tw - td."""
    global area_half
    tm = tu * tw - td
    lu, lw, lm = L(tu), L(tw), L(tm)
    if lm > RMAX:          # traces increase down the tree, so no primitive class in this cone has l <= RMAX;
        area_half += 0.5 / (lu * lw)   # chord u/N(u) -> w/N(w), det(u, w) = 1; the missed sliver is O(gap) = O(e^-l)
        return
    prim.append(lm)
    m = (u[0] + w[0], u[1] + w[1])
    cone(u, m, tu, tm, tw)       # diff u - m = -w
    cone(m, w, tm, tw, tu)       # diff m - w = u
e0, e1, e01 = (1, 0), (0, 1), (1, 1)
prim += [L(3), L(3), L(3)]
cone(e0, e01, 3, 3, 3)
cone(e01, e1, 3, 3, 3)
cone(e1, (-1, 0), 3, 3, 3)      # mediant e1 - e0 has trace 9 - 3 = 6
area = 2 * area_half
prim = np.sort(np.array(prim))
print("primitive classes mod sign with l <= %.0f: %d;  Area(B) = %.12f (l = 2 arccosh(t/2))" % (RMAX, len(prim), area))

Rs = np.sort(np.random.default_rng(1).uniform(10, RMAX, 4000))
P = np.searchsorted(prim, Rs, side="right").astype(float)
# A(R) = 2 sum_prim floor(R / N): accumulate the multiples k*N <= RMAX
mult = np.sort(np.concatenate([prim * k for k in range(1, int(RMAX / prim[0]) + 1)]))
mult = mult[mult <= RMAX]
A = 2 * np.searchsorted(mult, Rs, side="right").astype(float)
eP = P - 3 / math.pi**2 * area * Rs**2
eA = A - area * Rs**2
print("P(R)/R^2 -> %.6f   (3/pi^2) Area = %.6f" % (P[-1] / Rs[-1] ** 2, 3 / math.pi**2 * area))
print("A(R)/R^2 -> %.6f   Area = %.6f" % (A[-1] / Rs[-1] ** 2, area))
def expo(e):
    seg = np.array_split(np.arange(len(Rs)), 8)
    env = [np.abs(e[s]).max() for s in seg]; mid = [Rs[s].mean() for s in seg]
    return np.polyfit(np.log(mid[1:]), np.log(env[1:]), 1)[0], env
for name, e in (("lattice error  A - Area R^2", eA), ("primitive error P - (3/pi^2) Area R^2", eP)):
    a, env = expo(e)
    print("%-40s envelope by sixth of range: %s ; fitted exponent %.3f" % (name, " ".join("%.1f" % x for x in env), a))
# the Moebius part alone: if A were exactly Area R^2, P would be (1/2) Area R^2 sum_{d <= R/l_min} mu(d)/d^2

# separate the two sources: P from the exact Moebius formula with A replaced by its main term
mu = np.ones(int(RMAX / prim[0]) + 2, dtype=int); mu[0] = 0
for p in range(2, len(mu)):
    if all(p % q for q in range(2, int(p ** 0.5) + 1)):
        mu[p::p] *= -1; mu[p * p::p * p] = 0
Pm = np.array([0.5 * area * R ** 2 * sum(mu[d] / d ** 2 for d in range(1, int(R / prim[0]) + 1)) for R in Rs])
a, env = expo(Pm - 3 / math.pi ** 2 * area * Rs ** 2)
print("%-40s envelope: %s ; fitted exponent %.3f" % ("Moebius-tail part alone", " ".join("%.1f" % x for x in env), a))
