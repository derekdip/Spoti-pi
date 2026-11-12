"""Two links between the exact model and the theorem: pivots vs eigenvalues, and the real theta kernel."""
import math, numpy as np
from fractions import Fraction as F
from ladder import build, ldl_pivots, laguerre



def main():
    print("=== 1. LDL pivots vs true eigenvalues of the same matrix (theta jets) ===")
    for eps in (F(1, 100), F(1, 1000)):
        At = build(7, "theta", eps, 9)
        piv = ldl_pivots(At)
        ev = np.linalg.eigvalsh(np.array([[float(x) for x in row] for row in At]))
        ev = sorted(ev, key=lambda z: -abs(z))
        print(f"  eps=1/{int(1/eps)}")
        print("    pivots     ", "  ".join(f"{float(p):+.6e}" for p in piv[:6]))
        print("    eigenvalues", "  ".join(f"{e:+.6e}" for e in ev[:6]))
        print("    rel diff   ", "  ".join(f"{abs(float(p)-e)/abs(e):.2e}" for p, e in zip(piv[:6], ev[:6])))
    
    print("\n=== 2. The real xi kernel: shells, hazard, and the reduction to exp(-(e^{eps s}-1)/eps) ===")
    def log_phi_terms(x, M=6):
        """log of each theta shell at x, in log space (the kernel itself underflows)."""
        out = []
        for m in range(1, M + 1):
            a = 2 * math.pi**2 * m**4 * math.exp(4.5 * x)
            b = 3 * math.pi * m**2 * math.exp(2.5 * x)
            val = a - b
            out.append((math.log(abs(val)) - math.pi * m * m * math.exp(2 * x), math.copysign(1, val)))
        return out
    
    def log_Phi(x, M=6):
        ts = log_phi_terms(x, M)
        lead = ts[0][0]
        s = sum(sg * math.exp(lg - lead) for lg, sg in ts)
        return lead + math.log(s)
    
    for a in (0.5, 1.0, 1.5):
        x0 = 2 * a
        t2 = log_phi_terms(x0)
        print(f"  a={a}: shell ratio phi_2/phi_1 at x0 = {math.exp(t2[1][0]-t2[0][0]):.3e}")
        d = 1e-6
        h  = -(log_Phi(x0 + d) - log_Phi(x0 - d)) / (2 * d)
        hp = -(log_Phi(x0 + d) - 2 * log_Phi(x0) + log_Phi(x0 - d)) / (d * d)
        eps_num = hp / h**2
        print(f"        h(2a) = {h:.6e}  vs 2*pi*e^{{4a}}-9/2 = {2*math.pi*math.exp(2*x0)-4.5:.6e}")
        print(f"        eps_a = {eps_num:.6e}  vs e^{{-4a}}/pi = {math.exp(-4*a)/math.pi:.6e}   ratio {eps_num/(math.exp(-4*a)/math.pi):.6f}")
        worst = 0.0
        for s in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
            true = log_Phi(x0 + s / h) - log_Phi(x0)
            model = -(math.exp(eps_num * s) - 1) / eps_num
            worst = max(worst, abs(true - model))
        print(f"        max |log k_true - log k_model| over s<=20 : {worst:.3e}  (eps_a = {eps_num:.2e})")


if __name__ == "__main__":
    main()
