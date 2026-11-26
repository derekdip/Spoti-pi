"""High-t evaluator for Z_B on the modular torus via the hyperbolic Chowla-Selberg formula
   Z_B(s) = 2 zeta(s) l^-s + 2 zeta(s-1) h(0) + 2 sum_{m>=1} sigma_{1-s}(m) [h(m) + h(-m)],  h(m) = int N(x)^-s e^{-2 pi i m x} dx,
N(x) = stable norm on the line q = 1 (homology p alpha + beta), piecewise linear through Farey nodes (exact traces).
No 1/Gamma cancellation: double precision throughout, mpmath only for zeta values and the small-m tail integrals."""
import math, numpy as np, mpmath as mp
TA = 3.0; ELL = 2 * math.acosh(TA / 2)          # alpha: trace 3
K = 16; P = 8192; M = 1500; M2 = 400000
def L(t): return 2 * math.acosh(t / 2) if t < 1e8 else 2 * math.log(t) - 2 / t ** 2
def nodes():
    # integer nodes x = k: traces t_k of k alpha + beta, t_{k+1} = 3 t_k - t_{k-1}, t_0 = tr(beta) = 3, t_1 = tr(alpha beta) = 3
    t = {0: 3.0, 1: 3.0}
    for k in range(1, K + 2): t[k + 1] = TA * t[k] - t[k - 1]
    for k in range(0, -K - 2, -1): t[k - 1] = TA * t[k] - t[k + 1]
    xs, Ns, qs = [], [], []
    for k in range(-K - 1, K + 1):
        # Farey refinement of [k, k+1]: vectors u = (k,1), w = (k+1,1), difference w - u = alpha (trace 3)
        st = [((k, 1, t[k]), (k + 1, 1, t[k + 1]), TA)]
        xs.append(k); Ns.append(L(t[k])); qs.append(1)
        while st:
            (pu, qu, tu), (pw, qw, tw), td = st.pop()
            if L(tu) + L(tw) > 46: continue
            tm = tu * tw - td; pm, qm = pu + pw, qu + qw
            xs.append(pm / qm); Ns.append(L(tm) / qm); qs.append(qm)
            st += [((pu, qu, tu), (pm, qm, tm), tw), ((pm, qm, tm), (pw, qw, tw), tu)]
    o = np.argsort(xs); return np.array(xs)[o], np.array(Ns)[o], np.array(qs)[o]
XN, NN, QN = nodes()
def sigma_vec(a, MM):
    sg = np.zeros(MM + 1, complex); d = np.arange(1, MM + 1)
    pw = np.exp(a * np.log(d))
    for dd in range(1, MM + 1): sg[dd::dd] += pw[dd - 1]
    return sg
SIG_CACHE = {}
def Z(s):
    s = complex(s); sm = mp.mpc(s)
    dx = 1.0 / P; xg = np.arange(-K * P, K * P + 1) * dx; Ng = np.interp(xg, XN, NN)
    g = np.exp(-s * np.log(Ng))
    # folded sums S0 = sum_{j<n} g_j e^{-i w x_j}, S1 = sum_{j>=1} ...; x_j = -K + j dx, e^{-2pi i m x_j} = e^{2pi i m K} e^{-2pi i m j/P}
    def fold(v):
        n = len(v); pad = (-n) % P; vv = np.concatenate([v, np.zeros(pad, complex)]).reshape(-1, P).sum(0); return np.fft.fft(vv)
    F0 = fold(g[:-1]); F1 = fold(np.concatenate([[0], g[1:]]))
    ms = np.concatenate([np.arange(0, M + 1), np.arange(-M, 0)])
    th = 2 * np.pi * ms * dx
    with np.errstate(divide="ignore", invalid="ignore"):
        E = np.exp(-1j * th)
        al = np.where(np.abs(th) < 1e-4, 0.5 - 1j * th / 6, -1j / th + (1 - E) / th ** 2)      # int_0^1 (1-u) e^{-i th u} du
        be = np.where(np.abs(th) < 1e-4, 0.5 - 1j * th / 3, 1j * E / th - (1 - E) / th ** 2)   # int_0^1 u e^{-i th u} du
    idx = ms % P; ph = np.exp(2j * np.pi * ms * K)
    S0 = F0[idx] * ph; S1 = F1[idx] * ph
    h = dx * (al * S0 + be * np.exp(1j * th) * S1)
    # tails |x| > K: N = cR + l (x - K) on the right, cL + l (-K - x) on the left
    cR, cL = np.interp(K, XN, NN), np.interp(-K, XN, NN)
    def tail(c, w):            # int_0^inf (c + l u)^-s e^{-i w u} du
        if w == 0: return complex(mp.mpf(c) ** (1 - sm) / (ELL * (sm - 1)))
        if abs(w) < 2 * math.pi * 25:
            with mp.workdps(30 + int(abs(s.imag) / 2)):
                iw = 1j * mp.mpf(w) / ELL; cc = mp.mpf(c); ss = mp.mpc(s)
                return complex(mp.exp(iw * cc) / ELL * mp.power(iw, ss - 1) * mp.gammainc(1 - ss, iw * cc))
        tot = 0j; term = c ** (-s) / (1j * w); k = 0
        while abs(term) > 1e-18 * abs(tot + 1e-300) and k < 60:
            tot += term; term *= -(s + k) * ELL / c / (1j * w); k += 1
        return tot
    for i, m in enumerate(ms):
        w = 2 * math.pi * m
        h[i] += np.exp(-1j * w * K) * tail(cR, w) + np.exp(1j * w * K) * tail(cL, -w)
    hp = h[1:M + 1]; hm = h[::-1][:M]       # h(m), h(-m) for m = 1..M
    key = round(s.real, 12), round(s.imag, 12)
    sg = sigma_vec(1 - s, M2)
    main = 2 * complex(mp.zeta(sm)) * ELL ** (-s) + 2 * complex(mp.zeta(sm - 1)) * h[0] + 2 * np.sum(sg[1:M + 1] * (hp + hm))
    # m > M: corner asymptotics h(m) ~ s sum_i N_i^{-s-1} db_i e^{-2pi i m x_i}/(4 pi^2 m^2), nodes with q <= 3
    slopes = np.diff(NN) / np.diff(XN); db = np.zeros(len(XN)); db[1:-1] = slopes[1:] - slopes[:-1]
    mm = np.arange(M + 1, M2 + 1); tailsum = 0j
    for r in (0.0, 0.5, 1 / 3, 2 / 3):
        sel = (QN <= 3) & (np.abs((XN - r) - np.round(XN - r)) < 1e-12) & (np.abs(XN) < K - 1)
        if not sel.any(): continue
        C = s * np.sum(NN[sel] ** (-s - 1) * db[sel]) / (4 * math.pi ** 2)
        tailsum += C * np.sum(sg[M + 1:] * 2 * np.cos(2 * math.pi * mm * r) / mm ** 2)
        if r == 0.0:   # complete the integer-node series exactly: sum_m sigma_{1-s}(m)/m^2 = zeta(2) zeta(1+s)
            tailsum += C * 2 * (complex(mp.zeta(2) * mp.zeta(1 + sm)) - np.sum(sg[1:] / np.arange(1, M2 + 1) ** 2))
    return main + 2 * tailsum
if __name__ == "__main__":
    import time
    print("nodes on the line: %d (x in [%d, %d]); l = %.6f" % (len(XN), XN[0], XN[-1], ELL))
    ref = np.load("poc/farey/zeros_angle_0p785.npy")
    for k in (1, 5, 10, 20):
        t0 = time.time(); r = ref[k - 1, 0]; z = Z(r)
        print("rho_%2d: Chowla-Selberg %+.6f%+.6fj   mpmath %+.6f%+.6fj   |diff| %.2e  (%.1f s)" % (k, z.real, z.imag, ref[k-1,2].real, ref[k-1,2].imag, abs(z - ref[k - 1, 2]), time.time() - t0))
    for t, v in ((14.53, 5.1809), (37.15, 20.5528), (77.67, 10.9767)):
        print("t = %.2f: |Z| CS %.4f   mpmath %.4f" % (t, abs(Z(complex(0.5, t))), v))
    print("s = 3: CS %.8f   (direct sum + tail earlier: 1.466432453)" % Z(3.0).real)
