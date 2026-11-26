"""Control: the same explicit-formula pipeline on the single modular torus (no averaging)."""
import math, numpy as np, sys
sys.argv = ["x"]
exec(open("poc/farey/local_average_fit.py").read().split("for key in D.files")[0])
def Lt(t): return 2 * math.acosh(t / 2) if t < 10**300 else 2 * math.log(t)
l3 = Lt(3); out = [l3, l3, l3]; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; lm = Lt(tm)
    if lm > R1: continue
    out.append(lm); st += [(tu, tm, tw), (tm, tw, tu)]
ls = np.sort(out); cs = np.concatenate([[0], np.cumsum(ls)]); n = np.searchsorted(ls, Rg)
res, zsum = analyse(n * Rg - cs[n], "single modular torus (no averaging)")
