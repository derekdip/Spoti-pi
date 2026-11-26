import math, sys
sys.path.insert(0,'.'); sys.argv=["x","check"]
src=open("wp_zeta_neg.py").read().split("print(\"\\nmodular")[0].replace('sys.path.insert(0, __file__.rsplit("/", 1)[0])','')
exec(src)
import wp_average as W
for m in (4, 2):
    W.Astar = lambda a, b, mu_, m=m: abs(ZB_neg(a, b, mu_, m)[0])
    vol, I, lmax = W.integrate(0.0, 20, 8)
    print("m = %d: int |Z_B(-%d)| over M (20 x 8 nodes) = %.3f" % (m, m, I), flush=True)
