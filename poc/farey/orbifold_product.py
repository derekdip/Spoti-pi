"""Product law on complexity-one orbifolds: four-holed spheres with cone points (traces k_i = 2 cos(theta_i/2), L_i = i theta_i).
Prediction (Do-Norbury: volumes at L = i theta for cone angles <= pi): Vol = (4 pi^2 - sum theta^2)/2,
<A*> = (4 pi^2 - sum theta^2)/4, <Area(B)> = 4 pi^2/(4 pi^2 - sum theta^2), product pi^2.
Cases: k-Markoff (1,1,1): three order-3 points + cusp (theta = 2pi/3); (2,2,2,inf): three order-2 points + cusp (theta = pi),
the quotient of the cusped torus by its elliptic involution (same lengths, so the averages must equal the torus's 4 and pi^2/4).
Fundamental domain and charts as in wp_average_sphere.py, with the Fricke coefficients from the traces directly.
"""
import math, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import wp_average_sphere as WS
from wp_ball_average import sphere_area


def setup_traces(al, be, ga, de):
    return (al * be + ga * de, be * ga + al * de, al * ga + be * de), al * al + be * be + ga * ga + de * de + al * be * ga * de - 4


def run(traces, nx=40, nt=16):
    vol = IA = IB = 0.0
    for perm in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        C, s = setup_traces(*[traces[i] for i in perm])
        def interval(x):
            X, _, _, _, (ue, uo, R) = WS.chart(x, 0.0, C, s)
            v = math.acosh(max(1.0, (X - ue) / R)); w = math.acosh(max(1.0, (X - uo) / R)); return (v, x / 2 - w) if x / 2 - w > v else None
        xs = np.linspace(1e-4, 30, 30000); ok = [i for i, x in enumerate(xs) if interval(x) is not None]
        if not ok: continue
        xmax = xs[max(ok)]
        gx, wx = np.polynomial.legendre.leggauss(nx); gt, wt = np.polynomial.legendre.leggauss(nt)
        for u, wu in zip(gx, wx):
            sv = (u + 1) / 2; x = xmax * sv * sv; dx = xmax * 2 * sv * wu / 2; iv = interval(x)
            if iv is None: continue
            for y, wy in zip(gt, wt):
                tau = iv[0] + (iv[1] - iv[0]) * (y + 1) / 2; dt = (iv[1] - iv[0]) * wy / 2
                X, Y, Zm, Zp, _ = WS.chart(x, tau, C, s); w = 2 * dx * dt
                vol += w; IA += w * WS.Astar(X, Y, Zm, C, s); IB += w * sphere_area(X, Y, Zm, C, s)
    return vol, IA / vol, IB / vol


if __name__ == "__main__":
    p2 = math.pi**2
    for name, thetas in (("k-Markoff (1,1,1): cone angles 2pi/3 x3 + cusp", [2 * math.pi / 3] * 3 + [0.0]),
                         ("(2,2,2,inf): cone angles pi x3 + cusp", [math.pi] * 3 + [0.0])):
        traces = [2 * math.cos(t / 2) for t in thetas]; S = 4 * p2 - sum(t * t for t in thetas)
        vol, A, B = run(traces)
        print(f"{name}: traces {[round(t, 4) for t in traces]}")
        print(f"   Vol = {vol:.5f} (predicted {S / 2:.5f});  <A*> = {A:.5f} (predicted {S / 4:.5f});  <Area(B)> = {B:.5f} (predicted {4 * p2 / S:.5f});  "
              f"product = {A * B:.5f} (pi^2 = {p2:.5f})", flush=True)
