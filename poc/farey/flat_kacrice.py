"""Gaussian Kac-Rice prediction for the number of zeros of E*(z, rho/2) on the half fundamental domain, without
isotropy: at each height y, (Re/Im of f, f_x, f_y) with x uniform is modelled as a 6-dim real Gaussian whose mean is
(C, 0, C') and whose covariance is computed exactly from the Fourier coefficients a_n(y), a_n'(y).
Density per dx dy = p_f(0) E[|det J| | f = 0], by Monte Carlo; integrated over F/2."""
import sys, math, numpy as np, mpmath as mp
mp.mp.dps = 20
xi = lambda w: mp.pi ** (-w / 2) * mp.gamma(w / 2) * mp.zeta(w)
rng = np.random.default_rng(0)
def predict(k):
    rho = mp.zetazero(k); s = rho / 2; t = float(rho.imag) / 2; C0 = xi(2 * s - 1)
    NT = int(t / (2 * math.pi * 0.8)) + 12
    sig = [mp.fsum(mp.mpf(d) ** (1 - 2 * s) for d in range(1, n + 1) if n % d == 0) * mp.mpf(n) ** (s - 0.5) for n in range(1, NT + 1)]
    def co(y):
        a = []
        for n in range(1, NT + 1):
            u = 2 * mp.pi * n * y
            a.append(0j if u > t + 40 + 6 * t ** (1 / 3) else complex(4 * mp.sqrt(y) * sig[n - 1] * mp.besselk(s - 0.5, u)))
        return np.array(a), complex(C0 * mp.mpf(y) ** (1 - s))
    YMAX = 1.25 * t / (2 * math.pi) + 2.0; ys = [0.86]
    while ys[-1] < YMAX: ys.append(ys[-1] * (1 + 0.6 / (t + 4)))
    tot = 0.0; ns = 2 * math.pi * np.arange(1, NT + 1); scale = None
    for i in range(len(ys) - 1):
        y = ys[i]; h = 1e-6 * y
        a, c = co(y); a2, c2 = co(y + h); ap = (a2 - a) / h; cp = (c2 - c) / h
        if scale is None: scale = abs(c) + 1e-300
        a, ap, c, cp = a / scale, ap / scale, c / scale, cp / scale
        # basis functions: g = sum a_n cos, gx = sum -n a_n sin, gy = sum ap_n cos ; E[cos^2] = E[sin^2] = 1/2, cross 0
        Cc = [a, ap]          # cos-coefficient vectors for (g, gy)
        V = np.zeros((6, 6)); comps = []
        def rc(v): return [v.real, v.imag]
        # variables: 0 Re g, 1 Im g, 2 Re gx, 3 Im gx, 4 Re gy, 5 Im gy
        cosv = {0: a.real, 1: a.imag, 4: ap.real, 5: ap.imag}; sinv = {2: -(ns * a).real, 3: -(ns * a).imag}
        for p in range(6):
            for q in range(6):
                if p in cosv and q in cosv: V[p, q] = 0.5 * np.dot(cosv[p], cosv[q])
                elif p in sinv and q in sinv: V[p, q] = 0.5 * np.dot(sinv[p], sinv[q])
        m = np.array([c.real, c.imag, 0, 0, cp.real, cp.imag])
        S11 = V[:2, :2]; S12 = V[:2, 2:]; S22 = V[2:, 2:]
        if np.linalg.det(S11) <= 1e-300: continue
        inv = np.linalg.inv(S11); pf0 = math.exp(-0.5 * m[:2] @ inv @ m[:2]) / (2 * math.pi * math.sqrt(np.linalg.det(S11)))
        cm = m[2:] + S12.T @ inv @ (0 - m[:2]); cc = S22 - S12.T @ inv @ S12
        w_, U_ = np.linalg.eigh(0.5 * (cc + cc.T)); L = U_ * np.sqrt(np.clip(w_, 0, None))[None, :]
        J = cm[None, :] + rng.standard_normal((20000, 4)) @ L.T
        Edet = np.mean(np.abs(J[:, 0] * J[:, 3] - J[:, 1] * J[:, 2]))
        dy = ys[i + 1] - y
        width = 0.5 if y >= 1 else (max(0.0, 0.5 - math.sqrt(1 - y * y)) if y >= math.sqrt(3) / 2 else 0.0)
        tot += pf0 * Edet * width * dy
    return float(rho.imag), tot
obs = {1: 1, 2: 3, 3: 4, 4: 8, 5: 7, 6: 10, 7: 12, 8: 11, 9: 18, 15: 26, 20: 36, 30: 61, 45: 119}
for k in [int(a) for a in sys.argv[1].split(",")]:
    g, N = predict(k)
    print("k = %3d gamma = %7.2f: Gaussian Kac-Rice %.1f   observed %s   ratio %.3f" % (k, g, N, obs.get(k, "?"), obs[k] / N if k in obs else float('nan')), flush=True)
