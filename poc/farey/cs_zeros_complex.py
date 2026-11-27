"""Complex Z_B(rho_k) and c_k = Z_B/(2 rho zeta'(rho)) for the modular torus via the Chowla-Selberg evaluator."""
import sys, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); import zb_cs as C
a, b = int(sys.argv[1]), int(sys.argv[2]); out = []
for k in range(a, b):
    r = mp.zetazero(k); z = C.Z(complex(r)); zp = complex(mp.zeta(r, derivative=1))
    out.append((complex(r), z, z / (2 * complex(r) * zp)))
    if k % 10 == 9 or k == b - 1: np.save("poc/farey/cs_czeros_%d_%d.npy" % (a, b), np.array(out))
