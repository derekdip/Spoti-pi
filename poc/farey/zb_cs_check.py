"""Stability of the Chowla-Selberg evaluator in its numerical parameters at large t, and the t = 90.5 arbitration."""
import numpy as np, importlib, sys
sys.path.insert(0, "poc/farey"); import zb_cs as C
print("t = 90.50: |Z| = %.5f   (mpmath pi/4 gave 31.3421, pi/3 gave 34.4167)" % abs(C.Z(complex(0.5, 90.5))))
for t in (200.0, 500.0, 1000.0):
    vals = []
    for (P, M, K) in ((8192, 1500, 16), (16384, 3000, 16), (16384, 3000, 22), (32768, 6000, 22)):
        C.P, C.M, C.K = P, M, K
        if K != 16: C.XN, C.NN, C.QN = C.nodes()
        vals.append(C.Z(complex(0.5, t)))
        C.K = 16; C.XN, C.NN, C.QN = C.nodes()
    v = np.array(vals); print("t = %6.1f: " % t + "  ".join("%+.5f%+.5fj" % (z.real, z.imag) for z in v) + "   spread %.1e" % (np.abs(v - v[-1]).max() / abs(v[-1])))
