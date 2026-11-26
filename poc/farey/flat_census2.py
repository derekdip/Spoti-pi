"""Fast census of blind flat tori (zeros of E*(z, rho_k/2) on 0 <= x <= 1/2, |z| >= 1) up to large gamma, with a
Kac-Rice-with-mean prediction. Rows in y carry precomputed Fourier coefficients; x-evaluation by cosines (numpy);
every winding cell is Newton-confirmed with the full mpmath series.
Prediction: N_KR = int_{F/2} (t^2/4 pi) exp(-|C(y)|^2/sigma^2(y)) dx dy/y^2, t = gamma/2,
C = xi(2-2s) y^{1-s}, sigma^2 = (1/2) sum_n |a_n(y)|^2, a_n = 4 sqrt(y) n^{s-1/2} sigma_{1-2s}(n) K_{s-1/2}(2 pi n y)."""
import sys, math, numpy as np, mpmath as mp
from scipy.optimize import fsolve
mp.mp.dps = 20
xi = lambda w: mp.pi ** (-w / 2) * mp.gamma(w / 2) * mp.zeta(w)
def run(k):
    rho = mp.zetazero(k); s = rho / 2; t = float(rho.imag) / 2
    C0 = xi(2 * s - 1)                       # = xi(2 - 2s)
    NT = int(t / (2 * math.pi * 0.8)) + 12
    sig = [mp.fsum(mp.mpf(d) ** (1 - 2 * s) for d in range(1, n + 1) if n % d == 0) * mp.mpf(n) ** (s - 0.5) for n in range(1, NT + 1)]
    def coeffs(y):
        out = []
        for n in range(1, NT + 1):
            u = 2 * mp.pi * n * y
            if u > t + 40 + 6 * t ** (1 / 3): out.append(0j); continue
            out.append(complex(4 * mp.sqrt(y) * sig[n - 1] * mp.besselk(s - 0.5, u)))
        return np.array(out), complex(C0 * mp.mpf(y) ** (1 - s))
    YMAX = 1.25 * t / (2 * math.pi) + 2.0
    ys = [0.86]
    while ys[-1] < YMAX: ys.append(ys[-1] * (1 + 0.6 / (t + 4)))
    ys = np.array(ys); nx = int(3.0 * t) + 40; xs = np.linspace(0, 0.5, nx)
    cosm = np.cos(2 * math.pi * np.outer(np.arange(1, NT + 1), xs))
    F = np.zeros((len(ys), nx), complex); KR = 0.0
    for i, y in enumerate(ys):
        a, c = coeffs(y); F[i] = c + a @ cosm
        s2 = 0.5 * np.sum(np.abs(a) ** 2)
        if i + 1 < len(ys):
            dy = ys[i + 1] - y; xlo = math.sqrt(max(1 - y * y, 0)) if y < 1 else 0.0
            width = max(0.5 - xlo, 0) if y < 1 else 0.5
            if y < 1: width = max(0.0, 0.5 - math.sqrt(max(1 - y * y, 0))) if y >= math.sqrt(3) / 2 else 0.0
            KR += (t * t / (4 * math.pi)) * math.exp(-abs(c) ** 2 / s2) * width * dy / y ** 2 if s2 > 0 else 0.0
    def Efull(x, y):
        tot = C0 * mp.mpf(y) ** (1 - s)
        for n in range(1, NT + 1):
            u = 2 * mp.pi * n * y
            if u > t + 40 + 6 * t ** (1 / 3): break
            tot += 4 * mp.sqrt(y) * sig[n - 1] * mp.besselk(s - 0.5, u) * mp.cos(2 * mp.pi * n * x)
        return complex(tot)
    found = []
    for i in range(len(ys) - 1):
        for j in range(nx - 1):
            lp = [F[i, j], F[i + 1, j], F[i + 1, j + 1], F[i, j + 1], F[i, j]]
            if abs(sum(np.angle(lp[q + 1] / lp[q]) for q in range(4))) < math.pi: continue
            x0, y0 = (xs[j] + xs[j + 1]) / 2, (ys[i] + ys[i + 1]) / 2
            if x0 * x0 + y0 * y0 < 0.97: continue
            sol = fsolve(lambda p: (lambda w: [w.real, w.imag])(Efull(p[0], p[1])), [x0, y0], xtol=1e-12)
            x, y = sol
            if np.hypot(*(lambda w: [w.real, w.imag])(Efull(x, y))) < 1e-8 * abs(complex(C0)) * y ** 0.75 and 0 < x < 0.5 and x * x + y * y > 1 \
               and not any(abs(x - a) < 1e-6 and abs(y - b) < 1e-6 for a, b in found):
                found.append((x, y))
    ymax_found = max((p[1] for p in found), default=float("nan"))
    print("k = %3d gamma = %7.3f t = %6.2f: %4d blind flat tori;  Kac-Rice-with-mean %.1f;  Berry t^2/24 %.1f;  ratio N/(gamma^2) %.5f;  highest y %.3f vs turning t/(2pi) = %.3f" % (
        k, 2 * t, t, len(found), KR, t * t / 24, len(found) / (4 * t * t), ymax_found, t / (2 * math.pi)), flush=True)
for k in [int(a) for a in sys.argv[1].split(",")]: run(k)
