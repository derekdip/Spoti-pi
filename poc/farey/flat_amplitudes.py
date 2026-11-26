"""Growth of the Riemann-zero amplitudes for flat tori: Z_flat(rho) = 2 pi^{rho/2} E*(z, rho/2)/Gamma(rho/2), and
c_rho = Z_flat(rho)/(2 rho zeta'(rho)) (the amplitude of R^rho in the primitive count in an ellipse).
Prediction: |Z_flat(rho)|^2 grows like gamma (constant term ~ t^{1/2}); sum |c|^2 diverges like log T under
Gonek-Hejhal (sum_{gamma<T} 1/|zeta'|^2 ~ 6T/pi^3)."""
import sys, math, numpy as np, mpmath as mp
mp.mp.dps = 30
xi = lambda w: mp.pi ** (-w / 2) * mp.gamma(w / 2) * mp.zeta(w)
z = mp.mpc(0.5, mp.sqrt(3) / 2); x, y = mp.re(z), mp.im(z)
K = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rows = []
for k in range(1, K + 1):
    rho = mp.zetazero(k); s = rho / 2; t = float(rho.imag) / 2
    tot = xi(2 * s - 1) * y ** (1 - s); ct = tot
    for n in range(1, int(t / (2 * math.pi * float(y))) + 25):
        u = 2 * mp.pi * n * y
        sig = mp.fsum(mp.mpf(d) ** (1 - 2 * s) for d in range(1, n + 1) if n % d == 0)
        tot += 4 * mp.sqrt(y) * mp.mpf(n) ** (s - 0.5) * sig * mp.besselk(s - 0.5, u) * mp.cos(2 * mp.pi * n * x)
    Zf = 2 * mp.pi ** (rho / 2) * tot / mp.gamma(rho / 2); Zc = 2 * mp.pi ** (rho / 2) * ct / mp.gamma(rho / 2)
    zp = mp.zeta(rho, derivative=1); c = Zf / (2 * rho * zp)
    rows.append((float(rho.imag), float(abs(Zf)), float(abs(Zc)), float(abs(zp)), float(abs(c))))
r = np.array(rows); np.save("poc/farey/flat_amplitudes.npy", r)
g = r[:, 0]
print("hexagonal flat torus, %d zeros (gamma up to %.1f)" % (K, g[-1]))
for lo, hi in ((0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 400)):
    m = (g >= lo) & (g < hi)
    if m.sum() > 2:
        print("  gamma in [%3d,%3d): <|Z|^2>/gamma = %.3f   <|const term|^2>/gamma = %.3f   <1/|zeta'|^2> = %.4f   (%d zeros)" % (
            lo, hi, np.mean(r[m, 1] ** 2 / g[m]), np.mean(r[m, 2] ** 2 / g[m]), np.mean(1 / r[m, 3] ** 2), m.sum()))
S = np.cumsum(2 * r[:, 4] ** 2)
for T in (50, 100, 200, 300, 400):
    i = np.searchsorted(g, T) - 1
    if 0 <= i < len(g): print("  2 sum_{gamma<%d} |c|^2 = %.4f" % (T, S[i]))
print("  Gonek-Hejhal mean 1/|zeta'|^2 density: 6/pi^3 per unit gamma -> <1/|zeta'|^2> ~ (6/pi^3)/(density log(g/2pi)/2pi)")
