"""Is the part of the sharp error E_P not explained by the first 20 zeros correlated with the Diophantine lattice error?
E_P(R) = (1/2) sum_d mu(d) A(R/d) exactly; E_A(t) = A(t) - Area t^2 is the ball lattice error (plateau rms ~300, driven by
large partial quotients). Regress the residual r = E_P - 0.6537 - 2 Re sum_{k<=20} c_k R^rho_k on E_A(R/d), d = 1..6, and
on Moebius partial sums. Under completeness with E_A = O(R^eps), the lattice terms are a decaying R^{-1/2} component in
E_P/sqrt R, so any correlation must fade between the low and high halves of the sample range."""
import numpy as np, sys, math
sys.argv = ["x"]
exec(open("poc/farey/primitive_large.py").read().split("# check against direct")[0])
Rs, EP = np.load("poc/farey/sharp_samples.npy")
z = np.load("poc/farey/zeros_angle_0p785.npy"); rho, c = z[:, 0], z[:, 1]
zs = np.array([2 * np.real(np.sum(c * R ** rho)) for R in Rs])
r = EP - 0.6537 - zs
EA = {d: np.array([A(R / d) - area * (R / d) ** 2 for R in Rs]) for d in range(1, 7)}
n = len(Rs); halves = (slice(0, n // 2), slice(n // 2, n), slice(0, n))
print("rms E_P %.1f, rms zero sum %.1f, rms residual %.1f" % (EP.std(), zs.std(), r.std()))
for d in range(1, 7): print("d = %d: rms E_A(R/d) %.1f" % (d, EA[d].std()))
for name, sl in zip(("low half [3e4, 9.5e4]", "high half [9.5e4, 3e5]", "all"), halves):
    print("\n" + name)
    for d in range(1, 7):
        cc = np.corrcoef(r[sl], EA[d][sl])[0, 1]; print("   corr(residual, E_A(R/%d)) = %+.3f" % (d, cc))
    X = np.column_stack([EA[d][sl] for d in range(1, 7)] + [np.ones(len(Rs[sl]))])
    beta, *_ = np.linalg.lstsq(X, r[sl], rcond=None); fit = X @ beta
    print("   joint regression on E_A(R/d), d<=6: R^2 = %.3f; coefficients %s (Moebius prediction mu(d)/2 = +.5 -.5 -.5 0 -.5 +.5)" % (
        1 - np.var(r[sl] - fit) / np.var(r[sl]), np.round(beta[:6], 3)))
    D = 0.5 * (EA[1] - EA[2] - EA[3] - EA[5] + EA[6])
    print("   M_6 = (1/2) sum_{d<=6} mu(d) E_A(R/d): rms %.1f, share of residual variance explained by adding it with coefficient 1: %.3f" % (
        D[sl].std(), 1 - np.var(r[sl] - D[sl]) / np.var(r[sl])))
np.save("poc/farey/residual_lattice.npy", np.array([Rs, r] + [EA[d] for d in range(1, 7)]))
