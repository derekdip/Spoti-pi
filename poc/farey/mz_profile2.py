"""Second-order profile of the normalised intersection numbers r_k = [tau_k]_{g,1}/V_{g,1}.

D_k(g) = sqrt(g) [ log r_k + (k^2 - 3k/2)/(pi^2 g) ]  should collapse onto Phi(x), x = k^2/g, if
rho_i = 1 - (2i - 1/2)/(pi^2 g) + Psi(i^2/g)/g + ...;  then a_g = 2 + C/sqrt(g) + ..., C = 7/(2 sqrt pi) + (2/pi^2) int e^{-x/pi^2} Phi.
Fit Phi(x) = c x^{3/2} (+ c' x^{1/2}) on the data and report the implied C.
"""
import sys, time
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from mz_engine import T

if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    rows = []
    for g in range(4, G + 1):
        t0 = time.time(); V0 = T(g, (0,))
        for k in range(1, 3 * g - 1):
            r = T(g, (k,)) / V0
            if r <= 0: continue
            x = mp.mpf(k * k) / g
            D = mp.sqrt(g) * (mp.log(r) + (k * k - mp.mpf(3) * k / 2) / (mp.pi**2 * g))
            rows.append((g, k, float(x), float(D)))
        print(f"g = {g} done ({time.time() - t0:.0f} s)", flush=True)
    # collapse table at x near 1, 2, 4, 8
    for xt in (1, 2, 4, 8, 12):
        best = {}
        for g, k, x, D in rows:
            if abs(x - xt) < 0.5 * xt**0.5 and (g not in best or abs(x - xt) < abs(best[g][0] - xt)): best[g] = (x, D)
        print(f"x ~ {xt}: " + "  ".join(f"g={g}: x={v[0]:.2f}, D={v[1]:+.4f}, D/x^1.5={v[1] / v[0]**1.5:+.5f}" for g, v in sorted(best.items())))
    # least squares Phi = c1 x^{3/2} + c0 x^{1/2} using the largest two genera, x <= 9
    import numpy as np
    sel = [(x, D) for g, k, x, D in rows if g >= G - 1 and x <= 9]
    A = np.array([[x**1.5, x**0.5] for x, D in sel]); b = np.array([D for x, D in sel])
    c1, c0 = np.linalg.lstsq(A, b, rcond=None)[0]
    integ = c1 * float(mp.gamma(2.5) * mp.pi**5) + c0 * float(mp.gamma(1.5) * mp.pi**3)
    C = 7 / (2 * float(mp.sqrt(mp.pi))) + 2 / float(mp.pi**2) * integ
    print(f"fit (g >= {G - 1}, x <= 9): Phi(x) = {c1:+.6f} x^1.5 {c0:+.6f} x^0.5;  (5/(3 pi^4) = {5 / (3 * float(mp.pi)**4):.6f});  implied C = {C:.4f}  (7/(2 sqrt pi) - sqrt 2 = {7 / (2 * float(mp.sqrt(mp.pi))) - 2**0.5:.4f})")
