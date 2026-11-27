"""Does the non-zero-sum part of the sharp error decay like 1/sqrt R (lattice piece) as the limiting-distribution theorem
requires? Residual r = E_P/sqrt R - 0.6537/sqrt R - 2 Re sum_{k<=K} c_k R^{i gamma_k}, mean squares on
[3e4, 3e5] (sharp_samples.npy, 400) and [1e6, 2e6] (sharp_1e6_*.npy), for K up to the available zeros."""
import numpy as np, glob
cz = np.concatenate([np.load(f) for f in sorted(glob.glob("poc/farey/cs_czeros_*.npy"))]); cz = cz[np.argsort(cz[:, 0].imag)]
g = cz[:, 0].imag; c = cz[:, 2]
lo = np.load("poc/farey/sharp_samples.npy"); hi = np.concatenate([np.load(f) for f in glob.glob("poc/farey/sharp_1e6_*.npy")]).T
print("zeros available: %d (gamma <= %.0f); 2 sum |c|^2 = %.4f" % (len(g), g[-1], 2 * np.sum(np.abs(c) ** 2)))
for name, (R, E) in (("[3e4,3e5]", lo), ("[1e6,2e6]", hi)):
    f = E / np.sqrt(R) - 0.6537 / np.sqrt(R)
    print("%s (%d samples): mean square of E_P/sqrt R = %.4f" % (name, len(R), np.mean(f ** 2)))
    for K in (20, 100, 200, 300, len(g)):
        zs = 2 * np.real((c[:K, None] * np.exp(1j * np.outer(g[:K], np.log(R))) * 1).sum(0))
        r = f - zs
        print("    K = %3d zeros: MS(zero sum) %.4f   MS(residual) %.4f   explained %.1f%%   corr %.3f" % (K, np.mean(zs ** 2), np.mean(r ** 2), 100 * (1 - np.var(r) / np.var(f)), np.corrcoef(f, zs)[0, 1]))
