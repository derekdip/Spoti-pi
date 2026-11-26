"""Mismatch vs number of zeros, and a frequency scan of the residual, for the single torus and the local average."""
import math, numpy as np, mpmath as mp, sys
exec(open("poc/farey/local_average_fit.py").read().split("zs = [")[0])
NZ = 120
zs = [complex(mp.zetazero(k)) for k in range(1, NZ + 1)]; zp = [complex(mp.zeta(mp.mpc(r.real, r.imag), derivative=1)) for r in zs]
R0, R1 = 20.0, Rg[-1]
def pipeline(P):
    A = np.zeros_like(P)
    for k in range(1, int(R1 / 1.5) + 2): A += k * np.interp(Rg / k, Rg, P)
    m = Rg >= R0; X = np.array([Rg[m] ** j for j in range(4)]).T
    c0, c1, c2, c3 = np.linalg.lstsq(X, A[m], rcond=None)[0]
    def Ahat(s):
        k0 = (Rg > 0) & (Rg <= R0); Rq = Rg[m]
        return (np.trapezoid(A[k0] * Rg[k0] ** (-s - 1), Rg[k0]) + c3 * R0 ** (3 - s) / (s - 3) + c2 * R0 ** (2 - s) / (s - 2)
                + np.trapezoid((A[m] - c3 * Rq ** 3 - c2 * Rq ** 2) * Rq ** (-s - 1), Rq) + c1 * R1 ** (1 - s) / (s - 1) + c0 * R1 ** (-s) / s)
    co = np.array([Ahat(1 + r) / d for r, d in zip(zs, zp)])
    Rm = Rg[m]; res = P[m] - ((6 / math.pi ** 2) * c3 * Rm ** 3 - 2 * c1 * Rm - 12 * c0)
    terms = np.array([2 * (cc * Rm ** (1 + r)).real for cc, r in zip(co, zs)])
    return Rm, res, terms, co
def Lt(t): return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)
l3 = Lt(3); out = [l3, l3, l3]; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lt(tm)
    if lm > R1: continue
    out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
ls = np.sort(out); cs = np.concatenate([[0], np.cumsum(ls)]); n = np.searchsorted(ls, Rg)
for name, P in (("single modular torus", n * Rg - cs[n]), ("local average sigma_a = 0.03", D["s0.030"])):
    Rm, res, terms, co = pipeline(P)
    print("\n=== %s: residual rms %.3f" % (name, res.std()))
    for k in (1, 3, 10, 30, 60, 120):
        z = terms[:k].sum(0); print("   %3d zeros: mismatch rms %.4f  (%.2f%% of residual)" % (k, (res - z).std(), 100 * (res - z).std() / res.std()))
    print("   |coef| at zeros 1, 10, 30, 60, 120: %s" % " ".join("%.2e" % abs(co[i]) for i in (0, 9, 29, 59, 119)))
    # frequency scan of residual / R^1.5 against cos/sin(g log R), after removing a free quadratic-in-log trend
    y = res / Rm ** 1.5; lg = np.log(Rm)
    gs = np.linspace(5, 45, 801); pw = []
    for g in gs:
        Xf = np.array([np.ones_like(lg), np.cos(g * lg), np.sin(g * lg)]).T
        cf = np.linalg.lstsq(Xf, y, rcond=None)[0]; pw.append(math.hypot(cf[1], cf[2]))
    pw = np.array(pw); pk = [gs[i] for i in range(1, len(gs) - 1) if pw[i] > pw[i - 1] and pw[i] > pw[i + 1] and pw[i] > 0.15 * pw.max()]
    print("   spectral peaks of residual/R^1.5 in log R: %s" % " ".join("%.2f" % p for p in pk))
print("   zeta zeros:", " ".join("%.2f" % r.imag for r in zs[:6]))
