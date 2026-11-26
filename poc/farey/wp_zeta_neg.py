"""Test of <Z_B(s)>_WP = 0 at s = 0, -2, -4 (conjecture from the eps-regularised unfolding), any boundary length L.
Per surface: Z_B(-m) = root hexagon 2[T(a,w) + T(w,b) + T(b,a)] + 2 sum_cells [T(a,c) + T(c,b) - T(a,b)],
root triangle e0 (trace x), e1 (trace y), e0+e1 (trace W, larger root); cells via t_m = t_u t_w - t_d.
Atoms are computed from sympy-simplified delta * Q(a, b, delta) to avoid cancellation."""
import math, sys, sympy as sp, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import wp_average as W
A_, B_, D_, t = sp.symbols('a b d t', positive=True)
gen = sp.series(t ** 2 / ((1 - sp.exp(-A_ * t)) * (1 - sp.exp(-B_ * t))), t, 0, 9).removeO()
def Tm(m):
    Bc = sp.factorial(m + 2) * sp.expand(gen).coeff(t, m + 2)
    z2 = sp.factorial(m) / sp.factorial(m + 2) * Bc
    return sp.simplify(z2 + (sp.zeta(-m) if m > 0 else sp.Rational(-1, 2)) * (A_ ** m + B_ ** m) / 2)
T, ATOM = {}, {}
for m in (0, 2, 4):
    Tf = Tm(m); T[m] = sp.lambdify((A_, B_), Tf, "math")
    C = A_ + B_ - D_
    at = sp.together(Tf.subs({B_: C}) + Tf.subs({A_: C}).subs({B_: B_}) - Tf)
    # careful: T(a,c) + T(c,b) - T(a,b)
    at = sp.together(Tf.subs(B_, C) + Tf.subs(A_, C) - Tf)
    num, den = sp.fraction(sp.factor(at))
    ATOM[m] = sp.lambdify((A_, B_, D_), sp.cancel(num / D_) / den, "math")
    print("m = %d: T = %s;  atom = delta * %s" % (m, sp.factor(Tf), sp.factor(sp.cancel(num / D_) / den)))
L2 = lambda tr: 2 * math.acosh(tr / 2)
def ZB_neg(x, y, mu, m, ecut=1e-15):
    W_ = (x * y + math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y - mu), 0.0))) / 2
    a, b, w = L2(x), L2(y), L2(W_)
    tot = 2 * (T[m](a, w) + T[m](w, b) + T[m](b, a))
    st = [(x, W_, y), (W_, y, x), (y, x, W_)]; acc = 0.0; n = 0
    while st:
        tu, tw, td = st.pop(); tm = tu * tw - td
        Nu, Nw, Nm = L2(tu), L2(tw), L2(tm)
        S_ = Nu + Nw
        if S_ > 60: continue
        dl = 8 * math.exp(-S_) if S_ > 25 else S_ - Nm   # deep cells: delta = H e^{-(Nu+Nw)}, H -> 8 (proved asymptotics)
        at = dl * ATOM[m](Nu, Nw, dl); acc += at; n += 1
        st += [(tu, tm, tw), (tm, tw, tu)]
    return tot + 2 * acc, n
print("\nmodular torus: Z_B(0) = %.12f, Z_B(-2) = %.12f, Z_B(-4) = %.12f  (cell sums of the previous section: -0.653651620282, 0.387555229911, -2.116651789288)"
      % tuple(ZB_neg(3.0, 3.0, 0.0, m)[0] for m in (0, 2, 4)))
if len(sys.argv) > 1 and sys.argv[1] == "check": sys.exit()
for L in (0.0, 2.0):
    mu = 2 - 2 * math.cosh(L / 2)
    for m in (0, 2, 4):
        W.Astar = lambda a, b, mu_, m=m: ZB_neg(a, b, mu_, m)[0]
        vol, I, lmax = W.integrate(L, 40, 16)
        print("L = %.1f, m = %d: Vol = %.6f (pred %.6f);  int Z_B(-%d) = %+.6f;  average = %+.6f   (conjecture 0)" % (
            L, m, vol, (L * L + 4 * math.pi ** 2) / 24, m, I, I / vol), flush=True)
