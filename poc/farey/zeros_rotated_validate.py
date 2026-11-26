import mpmath as mp, sys
src = open("poc/farey/zeros_rotated.py").read().split("K = int(sys.argv[1])")[0]
exec(src.replace("mp.mp.dps = 30", "mp.mp.dps = 40"))
l3 = L(3)
for k in (11, 16):
    r = mp.zetazero(k); g = float(r.imag)
    for eta in (1 / (1 + g), 2 / (1 + g)):
        th = mp.pi / 2 - eta
        Z = 6 * l3 ** (-r) * mp.zeta(r - 1) + 2 * mp.fsum(Delta_rot(r, a, b, c, th) for a, b, c in cells)
        print("k = %d, eta = %.4f (dps 40): Z_B(rho) = %s" % (k, eta, mp.nstr(Z, 10)), flush=True)
