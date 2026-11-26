"""Numerical status of the lemmas for lim a_g = 2 (r_k = [tau_k]_{g,1}/V_{g,1}).

(L1) lower bound from Mirzakhani-Zograf Thm 3.2(ii):  r_k >= 1 - 2k^2/(pi^2 g)  (asymptotically)
(L2) monotonicity: r_{k+1} < r_k
(L3) Gaussian tail domination:  r_k <= exp(-c k^2/g) for all k >= 1; report c_g = min_k (-g log r_k / k^2)
(L4) uniform ratio error:  E_k(g) = g^2 [ r_{k+1}/r_k - 1 + (2k - 1/2)/(pi^2 g) ] / (1 + k^2); report max over k <= sqrt(g) and over all k
"""
import sys
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from mz_engine import T

if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    for g in range(2, G + 1):
        V0 = T(g, (0,)); K = 3 * g - 2
        r = [T(g, (k,)) / V0 for k in range(K + 1)]
        L1 = min(r[k] - (1 - 2 * mp.mpf(k * k) / (mp.pi**2 * g)) for k in range(K + 1))
        L2 = all(r[k + 1] < r[k] for k in range(K))
        cg = min(-g * mp.log(r[k]) / (k * k) for k in range(1, K + 1))
        kc = min(range(1, K + 1), key=lambda k: -g * mp.log(r[k]) / (k * k))
        # k = 0 has its own formula r_1/r_0 = 1 - 1/(2 pi^2 g); (3.7) is for k >= 1
        E0 = g * g * (r[1] - 1 + 1 / (2 * mp.pi**2 * g))
        E = {k: (g * g * (r[k + 1] / r[k] - 1 + (2 * k - mp.mpf(1) / 2) / (mp.pi**2 * g)) / (1 + k * k)) for k in range(1, K)}
        Es = max(abs(E[k]) for k in range(1, min(K, int(mp.sqrt(g)) + 1)))
        Ea = max(abs(x) for x in E.values())
        print(f"g = {g:>2}: (L1) min [r_k - (1 - 2k^2/(pi^2 g))] = {mp.nstr(L1, 4)};  (L2) decreasing: {L2};  "
              f"(L3) c_g = {mp.nstr(cg, 5)} (at k = {kc}; 1/pi^2 = {mp.nstr(1 / mp.pi**2, 5)});  (L4) k=0 error g^2(...) = {mp.nstr(E0, 4)}; max|E| 1<=k<=sqrt g: {mp.nstr(Es, 4)}, all k>=1: {mp.nstr(Ea, 4)}", flush=True)
