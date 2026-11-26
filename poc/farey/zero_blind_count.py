"""Spectral test on the zero-blind surface X* (Z_B(rho_1) = 0) versus the modular torus: project the exact sharp error
E_P(R)/sqrt R, R in [50, LMAX], onto R^{i gamma} (Hann window in log R). The explicit formula predicts a peak of
height |c_k| = |Z_B(rho_k)| / (2 |rho_k zeta'(rho_k)|) at gamma_k; on X* the gamma_1 = 14.13 peak must vanish."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, "poc/farey"); from zb_moduli import ZB
from cell_count_general import Torus
LMAX = 3000.0
def lengths_fast(x, y, z):
    """Simple-geodesic lengths <= LMAX from the sink; traces kept as log t (t_m = t_u t_w - t_d in log space)."""
    def L(lt): return 2 * math.acosh(math.exp(lt) / 2) if lt < 30 else 2 * lt - 2 * math.exp(-2 * lt)
    lx, ly, lz = math.log(x), math.log(y), math.log(z)
    out = [L(lx), L(ly), L(lz)]; st = [(lx, lz, ly), (lz, ly, lx), (ly, lx, lz)]
    while st:
        lu, lw, ld = st.pop(); lm = lu + lw + math.log1p(-math.exp(ld - lu - lw)); l = L(lm)
        if l > LMAX: continue
        out.append(l); st += [(lu, lm, lw), (lm, lw, lu)]
    return np.sort(np.array(out))
r1 = mp.zetazero(1)
GAM = np.linspace(5, 45, 801)
ZS = [float(mp.zetazero(k).imag) for k in range(1, 9)]
for name, tr in (("modular torus", (3.0, 3.0, 3.0)), ("zero-blind X*", tuple(np.load("poc/farey/zb_root.npy")))):
    X = Torus(*tr); Ns = lengths_fast(*tr)
    Rs = np.exp(np.linspace(math.log(50), math.log(LMAX * 0.999), 20000)); t = np.log(Rs)
    E = np.searchsorted(Ns, Rs, side="right") - 3 / math.pi ** 2 * X.area * Rs ** 2
    f = E / np.sqrt(Rs); w = 0.5 - 0.5 * np.cos(2 * math.pi * (t - t[0]) / (t[-1] - t[0]))
    spec = np.array([np.sum(f * w * np.exp(-1j * g * t)) / np.sum(w) for g in GAM])
    print("%s: traces %s, area %.6f, %d simple geodesics up to %g, rms E/sqrt R = %.3f" % (name, np.round(tr, 6), X.area, len(Ns), LMAX, f.std()))
    for k, g in enumerate(ZS, 1):
        rho = complex(mp.zetazero(k)); zb = ZB(rho, *tr, th=math.pi / 3)[0]; c = zb / (2 * rho * complex(mp.zeta(rho, derivative=1)))
        i = np.argmin(abs(GAM - g))
        print("   gamma_%d = %6.3f: measured |projection| %.4f   predicted |c_k| %.4f   (|Z_B(rho_k)| = %.4f)" % (k, g, abs(spec[i]), abs(c), abs(zb)))
    np.save("poc/farey/zero_blind_spec_%s.npy" % name.split()[0].replace("-", ""), np.array([GAM, spec]))
