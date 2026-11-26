"""Exact sharp simple-geodesic counting error E_P(R) on the modular torus at 400 log-uniform R in [3e4, 3e5]."""
import numpy as np, sys, math, time
sys.argv = ["x"]
src = open("poc/farey/primitive_large.py").read().split("# check against direct")[0]
exec(src)
Rs = np.exp(np.linspace(math.log(3e4), math.log(3e5), 400))
t0 = time.time(); E = np.array([P(R) - 3 / math.pi ** 2 * area * R * R for R in Rs])
np.save("poc/farey/sharp_samples.npy", np.array([Rs, E]))
print("done %d samples in %.0f s; rms E/sqrt R = %.3f" % (len(Rs), time.time() - t0, np.std(E / np.sqrt(Rs))))
