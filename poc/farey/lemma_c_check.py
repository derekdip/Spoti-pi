"""Lemma C (explicit per-cell bound) versus exact Delta_cell(s), 0 < sigma < 2, on the modular torus and on X*.
Bound (tau >= 0 by conjugation; eta = 1/(1+tau) if tau >= 1, else theta = 0):
  pref = e^{-theta tau}/|Gamma(s)|, r1 = pi/c, q1 = r1 sin eta, d2 = delta/(abc), kappa = 1/(a+b), m0 = 0.304554,
  M = e^{c r1} delta r1 e^{delta r1}/(m0^3 abc r1^3) + d2 r1^-2 e^{kappa r1}(1 + kappa r1)       (max principle, G on |t|<=r1)
  B = pref [ M r1^sigma/sigma + delta (sin eta)^{-sigma-1} int_{q1}^inf q^sigma e^{-cq} prod_x (1 + 1/(xq)) dq
             + d2 (1 + 1/(e sin eta)) r1^{sigma-2}/(2-sigma) ] + d2 kappa^{2-sigma}/|s-2|."""
import mpmath as mp, math, sys, time, numpy as np
src = open("poc/farey/zeros_rotated.py").read().split("cells = []")[0]
exec(src)
m0 = 0.304554
def bound(s, a, b, c, dl):
    sig, tau = float(s.real), abs(float(s.imag))
    if tau >= 1: eta = 1 / (1 + tau); th = math.pi / 2 - eta
    else: eta = math.pi / 2; th = 0.0
    se = math.sin(eta); pref = math.exp(-th * tau) / abs(complex(mp.gamma(mp.mpc(sig, tau))))
    d2 = dl / (a * b * c); kap = 1 / (a + b); r1 = math.pi / c; q1 = r1 * se
    M = math.exp(c * r1) * dl * r1 * math.exp(dl * r1) / (m0 ** 3 * a * b * c * r1 ** 3) + d2 * r1 ** -2 * math.exp(kap * r1) * (1 + kap * r1)
    f = lambda q: q ** sig * math.exp(-c * q) * (1 + 1 / (a * q)) * (1 + 1 / (b * q)) * (1 + 1 / (c * q))
    from scipy.integrate import quad
    I = quad(f, q1, q1 + 1 / c, limit=200)[0] + quad(f, q1 + 1 / c, np.inf, limit=200)[0]
    return pref * (M * r1 ** sig / sig + dl * se ** (-sig - 1) * I + d2 * (1 + 1 / (math.e * se)) * r1 ** (sig - 2) / (2 - sig)) + d2 * kap ** (2 - sig) / abs(complex(s) - 2)
def cells_of(x, y, z, smax):
    mp.mp.dps = 50; L = lambda t: 2 * mp.acosh(t / 2); out = []
    st = [(mp.mpf(x), mp.mpf(z), mp.mpf(y)), (mp.mpf(z), mp.mpf(y), mp.mpf(x)), (mp.mpf(y), mp.mpf(x), mp.mpf(z))]
    while st:
        tu, tw, td = st.pop(); a, b = L(tu), L(tw)
        if a + b > smax: continue
        tm = tu * tw - td; out.append((a, b, L(tm))); st += [(tu, tm, tw), (tm, tw, tu)]
    return out
surfs = {"modular": (3, 3, 3), "X*": tuple(float(v) for v in np.load("poc/farey/zb_root.npy"))}
worst = 0
for name, tr in surfs.items():
    cl = cells_of(*tr, 11.5)[:24]
    for sig in (0.3, 0.5, 1.5):
        for tau in (0.5, 5.0, 20.0, 60.0):
            t0 = time.time(); ratios = []
            th = math.pi / 4 if tau >= 1 else 0.0
            mp.mp.dps = 30 + int((math.pi / 2 - th) * tau / math.log(10)) + 10
            BN[:] = [mp.bernoulli(n) for n in range(KSER + 4)]; BN[1] = mp.mpf(-1) / 2
            s = mp.mpc(sig, tau)
            for a, b, c in cl:
                a, b, c = mp.mpf(a), mp.mpf(b), mp.mpf(c)
                d = Delta_rot(s, a, b, c, mp.mpf(th)); B = bound(complex(s), float(a), float(b), float(c), float(a + b - c))
                ratios.append(float(abs(d)) / B)
            ratios = np.array(ratios); worst = max(worst, ratios.max())
            print("%-8s s = %.1f + %4.1fi: %d cells, |Delta|/bound in [%.2e, %.2e]  (%.0f s)" % (name, sig, tau, len(cl), ratios.min(), ratios.max(), time.time() - t0), flush=True)
print("worst ratio over all cases: %.3e (must be < 1)" % worst)
