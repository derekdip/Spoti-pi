"""Exact sandwich for the Farey-cell deficiency (cusped torus; boundary: 16 -> 16 - 4 mu):
   t_Sigma - t_m = 8 / (X + sqrt(X^2 - 16)),  X = sigma_u sigma_w,  sigma = sqrt(t^2 - 4) = 2 sinh(N/2),
   8/(X sigma_Sigma) <= delta <= 16/((X + sqrt(X^2 - 16)) sigma_m),   t_Sigma = 2 cosh((N_u + N_w)/2).
Checked at 50 digits over Farey trees of surfaces with short curves, and for one-holed tori with boundary."""
import mpmath as mp
mp.mp.dps = 120
def check(x, y, mu, depth=14, label=""):
    W = (x * y + mp.sqrt(max((x * y) ** 2 - 4 * (x * x + y * y - mu), 0))) / 2
    st = [(x, W, y, 0), (W, y, x, 0), (y, x, W, 0)]; worst_lo = mp.inf; worst_hi = mp.inf; n = 0; idmax = 0
    while st:
        tu, tw, td, d = st.pop(); tm = tu * tw - td
        if d > depth: continue
        su, sw, sm = mp.sqrt(tu * tu - 4), mp.sqrt(tw * tw - 4), mp.sqrt(tm * tm - 4)
        Nu, Nw, Nm = 2 * mp.acosh(tu / 2), 2 * mp.acosh(tw / 2), 2 * mp.acosh(tm / 2)
        dl = Nu + Nw - Nm; X = su * sw; K = 16 - 4 * mu
        if Nu + Nw > 200: continue
        if tm <= td:   # mediant is the smaller root (not a Markoff-tree child); excluded: the sandwich is for cells oriented away from the sink
            st += [(tu, tm, tw, d + 1), (tm, tw, tu, d + 1)]; continue
        tS = 2 * mp.cosh((Nu + Nw) / 2); sS = mp.sqrt(tS * tS - 4)
        ident = abs((tS - tm) - K / (2 * (X + mp.sqrt(X * X - K))))
        lo = (K / 2) / (X * sS); hi = K / ((X + mp.sqrt(X * X - K)) * sm)
        worst_lo = min(worst_lo, dl / lo); worst_hi = min(worst_hi, hi / dl); idmax = max(idmax, ident / (tS - tm)); n += 1
        st += [(tu, tm, tw, d + 1), (tm, tw, tu, d + 1)]
    print("%-38s cells %5d | min delta/lower %.6f | min upper/delta %.6f | identity rel. error %.1e" % (label, n, worst_lo, worst_hi, idmax))
C = lambda l, mu=0: 2 * mp.sqrt((4 * mp.cosh(l / 2) ** 2 - mu) / (4 * mp.cosh(l / 2) ** 2 - 4))
check(mp.mpf(3), mp.mpf(3), 0, 13, "modular torus")
for l in (mp.mpf("0.5"), mp.mpf("0.05"), mp.mpf("0.005")):
    a = 2 * mp.cosh(l / 2)
    check(a, C(l) * mp.cosh(l / 4), 0, 12, "cusped, short alpha l = %s" % mp.nstr(l, 3))
for L in (mp.mpf(2), mp.mpf(6)):
    mu = 2 - 2 * mp.cosh(L / 2); a = 2 * mp.cosh(mp.mpf("0.7")); 
    check(a, C(mp.mpf("1.4"), mu) * mp.cosh(mp.mpf("0.3")), mu, 12, "boundary L = %s" % mp.nstr(L, 2))
