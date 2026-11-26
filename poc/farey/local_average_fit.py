"""Analysis of the local average. For each bump width:
 Abar(R) = sum_k k Pbar(R/k)  (all lattice classes, stable-norm homogeneity, Riesz-1) -> lattice error = Abar - cubic.
 Explicit formula: Pbar = (6/pi^2) c3 R^3 - 2 c1 R - 12 c0 + sum_rho 2 Re[Ahat(1+rho) R^(1+rho) / zeta'(rho)],
 with Ahat continued from Abar. Compare with the actual residual of Pbar."""
import math, numpy as np, mpmath as mp
mp.mp.dps = 20
D = np.load("poc/farey/local_average.npz"); Rg = D["R"]; dR = Rg[1] - Rg[0]
zs = [complex(mp.zetazero(k)) for k in range(1, 31)]; zp = [complex(mp.zeta(mp.mpc(r.real, r.imag), derivative=1)) for r in zs]
R0, R1 = 20.0, Rg[-1]
def analyse(P, name):
    A = np.zeros_like(P)
    for k in range(1, int(R1 / 1.5) + 2):
        A += k * np.interp(Rg / k, Rg, P)
    m = (Rg >= R0)
    X = np.array([Rg[m] ** j for j in range(4)]).T
    c, *_ = np.linalg.lstsq(X, A[m], rcond=None); c0, c1, c2, c3 = c
    eA = A[m] - X @ c
    # continued Mellin transform at s = 1 + rho
    def Ahat(s):
        Rp = Rg[(Rg > 0) & (Rg <= R0)]; Ap = A[(Rg > 0) & (Rg <= R0)]
        I1 = np.trapezoid(Ap * Rp ** (-s - 1), Rp)
        Rq = Rg[m]; I2 = np.trapezoid((A[m] - c3 * Rq ** 3 - c2 * Rq ** 2) * Rq ** (-s - 1), Rq)
        return I1 + c3 * R0 ** (3 - s) / (s - 3) + c2 * R0 ** (2 - s) / (s - 2) + I2 + c1 * R1 ** (1 - s) / (s - 1) + c0 * R1 ** (-s) / s
    co = [Ahat(1 + r) / d for r, d in zip(zs, zp)]
    Rm = Rg[m]
    smooth = (6 / math.pi ** 2) * c3 * Rm ** 3 - 2 * c1 * Rm - 12 * c0
    zsum = sum(2 * (cc * Rm ** (1 + r)).real for cc, r in zip(co, zs))
    res = P[m] - smooth
    # also: best free cubic for P, to see how much non-smooth structure there is at all
    cp, *_ = np.linalg.lstsq(X, P[m], rcond=None); resfree = P[m] - X @ cp
    print("\n=== %s" % name)
    print("   Abar: c3 = %.6f (Area-type), lattice error rms %.4f, /R^1.5 rms %.2e" % (c3, eA.std(), (eA / Rm ** 1.5).std()))
    print("   Pbar: smooth part from Abar's c's; residual rms %.4f;  predicted zero sum rms %.4f;  residual - zero sum rms %.4f" % (
        res.std(), zsum.std(), (res - zsum).std()))
    print("   corr(residual, zero sum) = %.4f;  free-cubic residual of Pbar rms %.4f" % (np.corrcoef(res, zsum)[0, 1], resfree.std()))
    print("   |coefficient| of first zeros:", " ".join("%.2e" % abs(x) for x in co[:4]))
    for lo, hi in ((20, 60), (60, 100), (100, 150)):
        k = (Rm >= lo) & (Rm < hi)
        print("     R in [%3d,%3d): residual rms %.3f   zero sum rms %.3f   mismatch rms %.3f" % (lo, hi, res[k].std(), zsum[k].std(), (res - zsum)[k].std()))
    return res, zsum
for key in D.files:
    if key == "R": continue
    analyse(D[key], "sigma_a = " + key[1:])
