"""Per-pair cusped corner average for n = 2 at larger genus:
    a_g = F_{g,2}(0)/V_{g,2}(0) = 2 sum_k c_k G_k(0) / V_{g,2}(0),   V_{g,1}(x) = sum_k c_k x^{2k},
    G_k(0) = (1/2) int x^{2k+2} log coth(x/4) dx = (2k+2)! 2^{2k+3} (1 - 2^-(2k+4)) zeta(2k+4).
"""
import sys, time
import sympy as sp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from higher_volumes import V, coeffs_in, P, zeta_even

L1, L2 = sp.symbols("L1 L2")
if __name__ == "__main__":
    for g in range(1, 8):
        t0 = time.time()
        V1 = sp.expand(V(g, 1)); V2 = sp.expand(V(g, 2)).subs({L1: 0, L2: 0})
        num = 0
        for k, c in coeffs_in(L1, V1).items():
            num += c * 2 * sp.factorial(2 * k + 2) * 2**(2 * k + 3) * (1 - sp.Rational(1, 2**(2 * k + 4))) * zeta_even(2 * k + 4)
        a = sp.cancel(sp.expand(num) / (sp.expand(V2) * P**2))
        print(f"g = {g}: a_g = F_(g,2)(0)/V_(g,2)(0) = {float(a):.8f} pi^2  ({time.time() - t0:.0f} s)", flush=True)
