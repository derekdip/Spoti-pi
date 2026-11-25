"""Is the product law <Area(B)> <Area(B*)> = pi^2 structural? Other weightings of the curve sums, and the covariance.

Cusped tori (Mirzakhani unfolding, D-normalisation, Vol = zeta(2) = pi^2/6, g = 2 log coth(x/2), N = x/2):
    int sum_gamma g N^s = int_0^inf x (x/2)^s 2 log coth(x/2) dx,   int_0^inf x^m log coth(x/2) dx = 2 m! (1 - 2^-(m+2)) zeta(m+2):
    s = 0:  int sum g       = (7/2) zeta(3)          -> <sum g>      = 21 zeta(3)/pi^2
    s = 1:  int A*          = (15/4) zeta(4) = pi^4/24 -> <A*>        = pi^2/4
    s = 2:  int sum g N^2   = (93/16) zeta(5)        -> <sum g N^2>  = (93/16) zeta(5) 6/pi^2
    int Area(B) = 4 zeta(2)  -> <Area(B)> = 4;   product law: 15 zeta(4)/zeta(2) = pi^2 (Euler: zeta(4) = (2/5) zeta(2)^2).
Also measured: <M> = <Area(B) Area(B*)> and Cov(Area(B), Area(B*)) = <M> - <Area(B)><A*>.
"""
import math, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import wp_average as WT
from limits import curves as torus_curves
from wp_ball_average import area_from


def all_quantities(a, b, mu):
    cv, _ = torus_curves(a, b, mu, tol=1e-14)
    Ns = {v: math.acosh(t / 2) for v, t in cv.items()}; gs = {v: math.log1p((4 - mu) / (t * t - 4)) for v, t in cv.items()}
    AB = area_from(list(Ns.items())); As = sum(gs[v] * Ns[v] for v in cv)
    return dict(area=AB, Astar=As, M=AB * As, sum_g=sum(gs.values()), sum_gN2=sum(gs[v] * Ns[v]**2 for v in cv))


def run(L, nl=48, nt=20):
    mu, C, tau_interval, lmax = WT.domain(L)
    xl, wl = np.polynomial.legendre.leggauss(nl); xt, wt = np.polynomial.legendre.leggauss(nt)
    vol = 0.0; acc = {}
    for x, w in zip(xl, wl):
        s = (x + 1) / 2; l = lmax * s * s; dl = lmax * 2 * s * w / 2; iv = tau_interval(l)
        if iv is None: continue
        for y, v in zip(xt, wt):
            tau = iv[0] + (iv[1] - iv[0]) * (y + 1) / 2; dt = (iv[1] - iv[0]) * v / 2; wgt = 2 * dl * dt
            q = all_quantities(2 * math.cosh(l / 2), C(l) * math.cosh(tau / 2), mu); vol += wgt
            for k, val in q.items(): acc[k] = acc.get(k, 0.0) + wgt * val
    return vol, {k: val / vol for k, val in acc.items()}


if __name__ == "__main__":
    from mpmath import zeta, pi
    vol, avg = run(0.0); p2 = float(pi**2)
    pred = dict(area=4.0, Astar=p2 / 4, sum_g=float(21 * zeta(3) / pi**2), sum_gN2=float(93 / 16 * zeta(5) * 6 / pi**2))
    print(f"cusped tori: Vol = {vol:.6f} (pi^2/6 = {p2 / 6:.6f})")
    for k in ("area", "Astar", "sum_g", "sum_gN2"):
        print(f"  <{k}> = {avg[k]:.6f}   predicted {pred[k]:.6f}   (rel. diff {abs(avg[k] / pred[k] - 1):.1e})")
    print(f"  <Area(B)> <A*> = {avg['area'] * avg['Astar']:.6f} (pi^2 = {p2:.6f});  <M> = <Area(B) A*> = {avg['M']:.6f} = {avg['M'] / p2:.5f} pi^2;  "
          f"Cov(Area(B), A*) = {avg['M'] - avg['area'] * avg['Astar']:+.6f};  correlation coefficient needs variances (not computed)")
    print(f"  pairing the s = 0 and s = 2 moments with <Area(B)>: <Area(B)> <sum g> = {avg['area'] * avg['sum_g']:.6f} = 84 zeta(3)/pi^2 (not a power of pi);  "
          f"<Area(B)> <sum g N^2> = {avg['area'] * avg['sum_gN2']:.6f}")
    # mixtures over the boundary length: product of averages >= pi^2 (Cauchy-Schwarz), equality iff one boundary length
    Ls = np.array([0.0, 2.0, 5.0]); w = np.array([1.0, 1.0, 1.0]); S = Ls**2 + 4 * p2; V = S / 24
    mean_area = (w * (2 * p2 / 3)).sum() / (w * V).sum(); mean_A = (w * S**2 / 384).sum() / (w * V).sum()
    print(f"  mixture of boundaries L = 0, 2, 5 (equal weight per boundary, WP within each): <Area(B)> <A*> = {mean_area * mean_A:.6f} >= pi^2 (Cauchy-Schwarz)")
