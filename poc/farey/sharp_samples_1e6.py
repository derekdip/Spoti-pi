"""Exact sharp error E_P(R) on the modular torus at log-uniform R in [1e6, 2e6] (two halves by argv)."""
import numpy as np, sys, math
part = int(sys.argv[1]); sys.argv = ["x"]
exec(open("poc/farey/primitive_large.py").read().split("# check against direct")[0])
Rs = np.exp(np.linspace(math.log(1e6), math.log(2e6), 200))[part::2]; out = []
for R in Rs:
    out.append((R, P(R) - 3 / math.pi ** 2 * area * R * R))
    np.save("poc/farey/sharp_1e6_%d.npy" % part, np.array(out))
