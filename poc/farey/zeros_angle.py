"""Z_B(rho_k) via Farey cells with Delta_cell on the ray arg t = THETA (default pi/4): D is smooth there (poles stay on the
imaginary axis), and the e^{(pi/2 - THETA) gamma} cancellation is absorbed by precision 30 + (pi/2 - THETA) gamma / ln 10 + 10.
Acceptance test: two angles must agree."""
import mpmath as mp, sys, time, numpy as np, math
src = open("poc/farey/zeros_rotated.py").read().split("K = int(sys.argv[1])")[0]
exec(src)
THETA = float(eval(sys.argv[2])) if len(sys.argv) > 2 else math.pi / 4
ks = [int(x) for x in sys.argv[1].split(",")] if "," in sys.argv[1] else list(range(1, int(sys.argv[1]) + 1))
out = []
for k in ks:
    t0 = time.time(); r0 = mp.zetazero(k); g = float(r0.imag)
    mp.mp.dps = 30 + int((math.pi / 2 - THETA) * g / math.log(10)) + 10
    BN[:] = [mp.bernoulli(n) for n in range(KSER + 4)]; BN[1] = mp.mpf(-1) / 2
    r = mp.zetazero(k); l3 = L(3)
    cl = []; st = [(3, 3, 3)] * 3
    while st:
        tu, tw, td = st.pop(); tm = tu * tw - td
        if max(L(tu), L(tw)) > 22: continue
        cl.append((L(tu), L(tw), L(tm))); st += [(tu, tm, tw), (tm, tw, tu)]
    Z = 6 * l3 ** (-r) * mp.zeta(r - 1) + 2 * mp.fsum(Delta_rot(r, a, b, c, mp.mpf(THETA)) for a, b, c in cl)
    cf = Z / (2 * r * mp.zeta(r, derivative=1)); out.append((complex(r), complex(cf), complex(Z)))
    print("k = %2d: gamma = %8.4f  theta = %.4f  dps %d  Z_B(rho) = %s  |c_k| = %.4f  (%.0f s)" % (k, g, THETA, mp.mp.dps, mp.nstr(Z, 10), abs(cf), time.time() - t0), flush=True)
tag = ("%.3f" % THETA).replace(".", "p")
np.save("poc/farey/zeros_angle_%s.npy" % tag, np.array([[o[0], o[1], o[2]] for o in out]))
