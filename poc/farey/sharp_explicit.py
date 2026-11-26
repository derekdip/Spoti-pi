"""Is the sharp simple-geodesic counting error on the modular torus the explicit formula over the zeta zeros?
 E_P(R) = P(R) - (3/pi^2) Area R^2  vs  Z(R) = sum_{k<=K} 2 Re[ Z_B(rho_k) R^{rho_k} / (2 rho_k zeta'(rho_k)) ]   (mod sign).
Z_B(rho_k) from the Farey-cell sum (cells with max N <= 22, tail < 1e-6)."""
import math, numpy as np, sys, time
sys.path.insert(0, "poc/farey")
import mpmath as mp
src = open("poc/farey/certify_rho1.py").read().split("NC = 22")[0]
exec(src)
traces = []; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td
    if max(L(tu), L(tw)) > 22: continue
    traces.append((tu, tw, tm)); st += [(tu, tm, tw), (tm, tw, tu)]
K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
coef = []
t0 = time.time()
for k in range(1, K + 1):
    r = mp.zetazero(k)
    mp.mp.dps = 30 + int(math.pi * float(r.imag) / (2 * math.log(10))) + 15
    BN[:] = [mp.bernoulli(n) for n in range(KSER + 4)]; BN[1] = mp.mpf(-1) / 2
    cells_k = [(L(mp.mpf(tu_)), L(mp.mpf(tw_)), L(mp.mpf(tm_))) for tu_, tw_, tm_ in traces]
    r = mp.zetazero(k)
    Z = 6 * L(mp.mpf(3)) ** (-r) * mp.zeta(r - 1) + 2 * mp.fsum(Delta(r, a, b, c)[0] for a, b, c in cells_k)
    cf = Z / (2 * r * mp.zeta(r, derivative=1))
    coef.append((complex(r), complex(cf), complex(Z)))
    print("k = %2d: gamma = %8.4f  Z_B(rho) = %s  |c_k| = %.4f" % (k, r.imag, mp.nstr(Z, 8), abs(cf)), flush=True)
np.save("poc/farey/sharp_explicit_coef.npy", np.array([[c[0], c[1], c[2]] for c in coef]))
print("zeros done in %.0f s" % (time.time() - t0), flush=True)
