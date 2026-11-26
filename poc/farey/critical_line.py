"""|Z_B(1/2 + it)| at generic heights on the modular torus (hypothesis (L) of Theorem 10), mpmath on the ray theta = pi/4
with dps 30 + (pi/4) t/ln10 + 10 and a Bernoulli series of length KSER = 0.75 t + 30 (fixes the gamma > 105 breakdown).
Flat comparison: hexagonal Epstein |Z_flat(1/2 + it)|, whose functional equation forces ~ |t|^{1/2} growth."""
import sys, math, time, mpmath as mp
src = open("poc/farey/zeros_rotated.py").read().split("cells = []")[0]
exec(src)
ts = [float(a) for a in sys.argv[1].split(",")]
for t in ts:
    t0 = time.time(); TH = math.pi / 4
    globals()["KSER"] = int(0.75 * t) + 30
    mp.mp.dps = 30 + int((math.pi / 2 - TH) * t / math.log(10)) + 10
    BN[:] = []; BN.extend(mp.bernoulli(n) for n in range(KSER + 4)); BN[1] = mp.mpf(-1) / 2
    s = mp.mpc(0.5, t); l3 = L(3)
    cl = []; st = [(3, 3, 3)] * 3
    while st:
        tu, tw, td = st.pop(); tm = tu * tw - td
        if max(L(tu), L(tw)) > 22: continue
        cl.append((L(tu), L(tw), L(tm))); st += [(tu, tm, tw), (tm, tw, tu)]
    Z = 6 * l3 ** (-s) * mp.zeta(s - 1) + 2 * mp.fsum(Delta_rot(s, a, b, c, mp.mpf(TH)) for a, b, c in cl)
    # flat hexagonal Epstein at the same s: Z_flat(s) = 2 pi^{s/2} E*(z, s/2)/Gamma(s/2) with E* via its Fourier series
    w = s / 2; xi = lambda u: mp.pi ** (-u / 2) * mp.gamma(u / 2) * mp.zeta(u); y = mp.sqrt(3) / 2; x = mp.mpf(0.5)
    Es = xi(2 * w) * y ** w + xi(2 * w - 1) * y ** (1 - w)
    for n in range(1, int(t / (4 * math.pi * float(y))) + 30):
        sg = mp.fsum(mp.mpf(d) ** (1 - 2 * w) for d in range(1, n + 1) if n % d == 0)
        Es += 4 * mp.sqrt(y) * mp.mpf(n) ** (w - 0.5) * sg * mp.besselk(w - 0.5, 2 * mp.pi * n * y) * mp.cos(2 * mp.pi * n * x)
    Zf = 2 * mp.pi ** (s / 2) * Es / mp.gamma(s / 2)
    print("t = %7.2f: |Z_B| = %9.4f   |Z_flat| = %9.4f   |Z_flat|/sqrt(t) = %.3f   (KSER %d, dps %d, %.0f s)" % (
        t, float(abs(Z)), float(abs(Zf)), float(abs(Zf)) / math.sqrt(t), KSER, mp.mp.dps, time.time() - t0), flush=True)
