"""Argument-principle certificate for the zero of Z_B(rho_1) at X*.
Loop: circle of radius r about the Newton root in the chart (x, v). At N loop points:
  Z_trunc = cell formula with cells a + b <= S0 (double precision, ray theta = pi/3);
  err_tail = sum over cells S0 < a + b <= S1 of the explicit Lemma C bound (exact delta from 60-digit traces)
             + envelope bound beyond S1;
  err_num = 10 x |Z(theta = pi/3) - Z(theta = 0.4 pi)| (two independent quadrature rays; numerical, not interval);
  Lipschitz: L = 10 x max |grad Z| from central differences on a grid covering the annulus.
Certified winding if |Z_i| > err_tail + err_num + L h/2 at every point (h = chord between neighbours): then Z cannot
vanish or wind differently between samples, and the sampled winding equals the degree."""
import sys, math, numpy as np, mpmath as mp
from scipy.integrate import quad
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB, tree
rho = complex(mp.zetazero(1)); m0 = 0.304554
def surf(x, v):
    lo = max(x, math.sqrt(4 + 16 / (x * x - 4))); hi = x / math.sqrt(x - 2); y = lo + v * (hi - lo)
    z = (x * y - math.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y), 0))) / 2
    return x, y, z
def lemma_c(s, a, b, c, dl):
    sig, tau = s.real, abs(s.imag); eta = 1 / (1 + tau); th = math.pi / 2 - eta; se = math.sin(eta)
    pref = math.exp(-th * tau) / abs(complex(mp.gamma(s)))
    d2 = dl / (a * b * c); kap = 1 / (a + b); r1 = math.pi / c; q1 = r1 * se
    M = math.exp(c * r1) * dl * r1 * math.exp(dl * r1) / (m0 ** 3 * a * b * c * r1 ** 3) + d2 * r1 ** -2 * math.exp(kap * r1) * (1 + kap * r1)
    f = lambda q: q ** sig * math.exp(-c * q) * (1 + 1 / (a * q)) * (1 + 1 / (b * q)) * (1 + 1 / (c * q))
    I = quad(f, q1, q1 + 1 / c, limit=200)[0] + quad(f, q1 + 1 / c, np.inf, limit=200)[0]
    return pref * (M * r1 ** sig / sig + dl * se ** (-sig - 1) * I + d2 * (1 + 1 / (math.e * se)) * r1 ** (sig - 2) / (2 - sig)) + d2 * kap ** (2 - sig) / abs(s - 2)
x0, y0, z0 = np.load("poc/farey/zb_root.npy")
lo = max(x0, math.sqrt(4 + 16 / (x0 * x0 - 4))); hi = x0 / math.sqrt(x0 - 2); v0 = (y0 - lo) / (hi - lo)
S0, S1 = 40.0, 64.0
# tail bound: worst case over the loop region -> evaluate at the centre and at 4 extreme loop points, take the max x 1.5
r = 0.02; N = 400
def tail(tr):
    cl = tree(*tr, S1); keep = cl[(cl[:, 0] + cl[:, 1] > S0)]
    t1 = 2 * sum(lemma_c(rho, a, b, c, d) for a, b, c, d in keep)
    env = max(lemma_c(rho, a, b, c, d) / (d * (a + b) ** 6) for a, b, c, d in keep[::7])
    H = max(d * math.exp(a + b) for a, b, c, d in keep)
    far = 2 * sum(env * S ** 6 * 2 * H * math.exp(-S) * 2 * (S + 1) ** 2 for S in range(int(S1), 600))
    return t1, far, len(keep)
tails = [tail(surf(x0 + r * math.cos(t), v0 + r * math.sin(t))) for t in np.linspace(0, 2 * math.pi, 5)[:-1]] + [tail((x0, y0, z0))]
err_tail = 1.5 * max(t[0] + t[1] for t in tails)
print("tail bound (cells %g < a+b <= %g: %d cells; Lemma C) %.3e, beyond %g %.3e  -> err_tail = %.3e (x1.5 over loop)" % (S0, S1, tails[-1][2], tails[-1][0], S1, tails[-1][1], err_tail))
ts = np.linspace(0, 2 * math.pi, N + 1)[:-1]
pts = [(x0 + r * math.cos(t), v0 + r * math.sin(t)) for t in ts]
Z1 = np.array([ZB(rho, *surf(*p), th=math.pi / 3, smax=S0)[0] for p in pts])
Z2 = np.array([ZB(rho, *surf(*p), th=0.4 * math.pi, smax=S0)[0] for p in pts])
err_num = 10 * np.abs(Z1 - Z2).max()
# Lipschitz on the annulus r/2 .. 3r/2
hh = 1e-5; gmax = 0
for rr in (0.5 * r, 0.75 * r, r, 1.25 * r, 1.5 * r):
    for t in np.linspace(0, 2 * math.pi, 64, endpoint=False):
        p = (x0 + rr * math.cos(t), v0 + rr * math.sin(t))
        gx = (ZB(rho, *surf(p[0] + hh, p[1]), th=math.pi / 3, smax=S0)[0] - ZB(rho, *surf(p[0] - hh, p[1]), th=math.pi / 3, smax=S0)[0]) / (2 * hh)
        gv = (ZB(rho, *surf(p[0], p[1] + hh), th=math.pi / 3, smax=S0)[0] - ZB(rho, *surf(p[0], p[1] - hh), th=math.pi / 3, smax=S0)[0]) / (2 * hh)
        gmax = max(gmax, math.hypot(abs(gx), abs(gv)))
L = 10 * gmax; h = 2 * r * math.sin(math.pi / N)
need = err_tail + err_num + L * h / 2
w = np.sum(np.angle(np.roll(Z1, -1) / Z1)) / (2 * math.pi)
print("loop radius %g in (x, v), N = %d, chord h = %.2e" % (r, N, h))
print("min |Z| on loop %.4f; err_num %.2e; max |grad Z| %.2f -> L = %.1f; L h/2 = %.3e; required margin %.3e" % (np.abs(Z1).min(), err_num, gmax, L, L * h / 2, need))
print("largest phase step between samples: %.3f rad" % np.abs(np.angle(np.roll(Z1, -1) / Z1)).max())
print("winding number %.6f; CERTIFIED: %s" % (w, bool(np.abs(Z1).min() > need and abs(w - round(w)) < 1e-9 and round(w) != 0)))
