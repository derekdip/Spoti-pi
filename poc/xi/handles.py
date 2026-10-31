"""Two handles on the open conjecture, checked exactly."""
import math
from fractions import Fraction as F
from math import factorial as fact

# ---- Handle 1: the quadratic form is a backward heat flow on the squared Laplace transform.
#   Claim:  <A_eps f, f> = [ exp(-(eps/2) d^2/dw^2) (Lf)(w)^2 ]_{w=1}
#   Test f(u) = e^{-u}(1 + a u), so (Lf)(w) = 1/(1+w) + a/(1+w)^2.
def direct(a, M):
    """Series coefficients of <A_eps f,f> from the kernel exp(-(u+v) - eps(u+v)^2/2)."""
    def mom(k):            # int_0^inf u^k (1 + a u) e^{-2u} du
        return F(fact(k), 2 ** (k + 1)) + a * F(fact(k + 1), 2 ** (k + 2))
    out = []
    for m in range(M + 1):
        c = F(0)
        for k in range(2 * m + 1):
            c += F(fact(2 * m), fact(k) * fact(2 * m - k)) * mom(k) * mom(2 * m - k)
        out.append(F((-1) ** m, 2 ** m * fact(m)) * c)
    return out

def heat(a, M):
    """Series coefficients of [exp(-(eps/2) d_w^2) G]_{w=1}, G = (Lf)^2 = sum c_p/(1+w)^p."""
    terms = {2: F(1), 3: 2 * a, 4: a * a}
    out = []
    for m in range(M + 1):
        g = F(0)
        for p, c in terms.items():
            poch = F(fact(p + 2 * m - 1), fact(p - 1))     # (p)_{2m}
            g += c * poch / F(2 ** (p + 2 * m))
        out.append(F((-1) ** m, 2 ** m * fact(m)) * g)
    return out

for a in (F(0), F(1, 3), F(-2, 5)):
    d, h = direct(a, 5), heat(a, 5)
    print(f"a={a}:  identical to order eps^5: {d == h}")
    if a == F(1, 3):
        print("   coefficients:", [str(x) for x in d])

# ---- Handle 2: why the ladder alternates at all.
#   A Hankel kernel k(u+v) is positive semidefinite iff k is completely monotone, and every
#   completely monotone function is log-convex. So a log-CONCAVE tail forces indefiniteness.
#   eps = h'/h^2 > 0 is exactly log-concavity, since (log Phi)'' = -h'.
def log_phi(x, M=6):
    ts = []
    for m in range(1, M + 1):
        val = 2 * math.pi**2 * m**4 * math.exp(4.5 * x) - 3 * math.pi * m**2 * math.exp(2.5 * x)
        ts.append((math.log(abs(val)) - math.pi * m * m * math.exp(2 * x), math.copysign(1, val)))
    lead = ts[0][0]
    return lead + math.log(sum(sg * math.exp(lg - lead) for lg, sg in ts))

print("\n(log Phi)'' on (0, 3], which is -h' and must be negative for log-concavity:")
d = 1e-5
worst = 1e9
for x in [0.05, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0]:
    second = (log_phi(x + d) - 2 * log_phi(x) + log_phi(x - d)) / (d * d)
    worst = min(worst, -second)
    print(f"   x={x:4.2f}  (log Phi)'' = {second:+.4e}")
print(f"   most negative margin on -(log Phi)'': {worst:.3e}  -> log-concave throughout, so Phi is")
print("   not completely monotone on any half-line, so no H_a is positive semidefinite.")
