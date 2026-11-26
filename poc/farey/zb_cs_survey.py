"""Survey with the Chowla-Selberg evaluator. mode 'line': |Z_B(1/2+it)| at random t in [10, 2000];
mode 'zeros': Z_B(rho_k) and c_k = Z_B/(2 rho zeta'(rho)) for k in a range."""
import sys, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); import zb_cs as C
mode, a, b, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
out = []
if mode == "line":
    rng = np.random.default_rng(seed); ts = np.sort(rng.uniform(10, 2000, b - a))
    for t in ts: out.append((t, abs(C.Z(complex(0.5, t)))))
else:
    for k in range(a, b):
        r = mp.zetazero(k); z = C.Z(complex(r)); zp = complex(mp.zeta(r, derivative=1))
        out.append((float(r.imag), abs(z), abs(zp), abs(z / (2 * complex(r) * zp))))
np.save("poc/farey/cs_%s_%d_%d.npy" % (mode, a, b), np.array(out)); print("done", mode, a, b)
