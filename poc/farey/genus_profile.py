"""What sets the large-genus per-pair limit: the profile of normalised psi-intersection numbers.

V_{g,1}(x) = sum_k c_k x^{2k};  r_k(g) = c_k 2^{2k} (2k+1)! / c_0  (= 1 for every k if V_{g,1}(x) = V(0) sinh(x/2)/(x/2)).
Per pair: a_g = 2 sum_k c_k G_k(0) / V_{g,2}(0), G_k(0) = (2k+2)! 2^{2k+3} (1 - 2^-(2k+4)) zeta(2k+4); with r_k ~ exp(-alpha k^2/g)
and V_{g,2}(0) ~ 4 pi^2 (2g - 1) V_{g,1}(0):  a_g -> 2/(alpha pi^2).
Here: r_k(g) for g <= 5 (exact), the collapse in k^2/g, a fitted alpha, the predicted limit, and the exact sum term by term.
"""
import sys
import sympy as sp, mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from higher_volumes import V, coeffs_in, P

L1, L2 = sp.symbols("L1 L2")
if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    for g in range(1, G + 1):
        V1 = sp.expand(V(g, 1)); c = coeffs_in(L1, V1); c0 = c[0]
        V2 = sp.expand(V(g, 2)).subs({L1: 0, L2: 0})
        rk = {k: float((c[k] * 2**(2 * k) * sp.factorial(2 * k + 1) / c0).subs(P, sp.pi)) for k in sorted(c)}
        ratio = float((V2 / (4 * P**2 * (2 * g - 1) * c0)).subs(P, sp.pi))
        # per-pair a_g and its term-by-term pieces
        terms = {k: float((2 * c[k] * sp.factorial(2 * k + 2) * 2**(2 * k + 3) * (1 - sp.Rational(1, 2**(2 * k + 4))) * sp.zeta(2 * k + 4) / V2).subs(P, sp.pi)) for k in c}
        a = sum(terms.values()) / mp.pi**2
        # fit alpha from r_k for 1 <= k <= max(1, g): log r_k = -alpha k^2 / g
        ks = [k for k in rk if 1 <= k <= max(2, g) and rk[k] > 0]
        alpha = sum(-mp.log(rk[k]) * (k * k / g) for k in ks) / sum((k * k / g)**2 for k in ks)
        print(f"g = {g}: V(g,2)(0)/(4pi^2(2g-1)V(g,1)(0)) = {ratio:.5f};  a_g = {float(a):.6f} pi^2;  fitted alpha = {float(alpha):.4f} -> 2/(alpha pi^4) = {float(2 / (alpha * mp.pi**4)):.4f}", flush=True)
        print("     r_k:", "  ".join(f"k={k}: {rk[k]:.4f} (k^2/g = {k * k / g:.2f})" for k in sorted(rk)[:8]), flush=True)
