"""Explicit (no fitted constant) bound for |Delta_cell(s)| at s = rho_1, from the rotated-ray representation:
 Delta(s) = (1/Gamma(s)) [ int_ray t^{s-1} G(t) dt + d2 kappa^{2-s} Gamma(s-2)(s-1) ],
 G = D - d2 t^-2 e^{-kappa t}(1 + kappa t), d2 = delta/(abc), kappa = 1/(a+b), ray arg t = theta = pi/2 - eta.
 On |t| <= r1 = pi/c (max principle): |G| <= max over |t| = r1 of [ e^{c r1} delta r1 e^{delta r1} / (m0^3 a b c r1^3) + d2 r1^-2 e^{kappa r1}(1 + kappa r1) ],
 m0 = min_{|z|<=pi} |(e^z - 1)/z|.  Beyond r1 on the ray (q = r sin eta):
 |G| <= delta r e^{(c+delta) q} / prod_x (e^{x q} - 1) + d2 r^-2 e^{-kappa q}(1 + kappa r).
 Then |Delta| <= e^{-theta u}/|Gamma(s)| [ M r1^sigma/sigma + int_{r1}^inf r^{sigma-1} Gbound(r) dr ] + |d2 kappa^{2-s} Gamma(s-2)(s-1)/Gamma(s)|."""
import mpmath as mp, math, numpy as np, sys
mp.mp.dps = 25
s = mp.zetazero(1); sig, u = float(s.real), float(s.imag)
eta = 1 / (1 + u); theta = math.pi / 2 - eta; sin_eta = math.sin(eta)
zs = [math.pi * complex(math.cos(x), math.sin(x)) for x in np.linspace(0, 2 * math.pi, 200001)]
m0 = min(abs((complex(math.e) ** z - 1) / z) if False else abs((np.exp(z) - 1) / z) for z in zs)
print("m0 = min_{|z|=pi} |(e^z-1)/z| = %.6f  (minimum modulus principle: also the min over the disk)" % m0)
pref = math.exp(-theta * u) / abs(complex(mp.gamma(s)))
def bound(a, b, c, dl):
    if a + b > 25 or dl <= 0: dl = 15.24 * math.exp(-(a + b)); c = a + b - dl   # proved upper bound; the bound is increasing in delta
    d2 = dl / (a * b * c); kap = 1 / (a + b); r1 = math.pi / c
    M = math.exp(c * r1) * dl * r1 * math.exp(dl * r1) / (m0 ** 3 * a * b * c * r1 ** 3) + d2 * r1 ** -2 * math.exp(kap * r1) * (1 + kap * r1)
    def Gb(r):
        q = r * sin_eta
        lden = 0.0
        for x in (a, b, c):
            y = x * q; lden += math.log(math.expm1(y)) if y < 30 else y + math.log1p(-math.exp(-y))
        return math.exp(math.log(dl * r) + (c + dl) * q - lden) + d2 * r ** -2 * math.exp(-kap * q) * (1 + kap * r)
    # integrate r^{sig-1} Gb(r) on [r1, inf): substitute geometric grid, trapezoid on log scale (integrand smooth, decaying e^{-c q})
    rmax = r1 + 60 / (min(a, b, c) * sin_eta)
    xs = np.linspace(math.log(r1), math.log(rmax), 4000); rs = np.exp(xs)
    vals = np.array([r ** sig * Gb(r) for r in rs])        # r^{sig-1} * r dr/dlog r
    I = np.trapezoid(vals, xs) * 1.02                       # 2% safety for the quadrature of a smooth positive function
    gam = abs(complex(d2 * mp.power(kap, 2 - s) * mp.gamma(s - 2) * (s - 1) / mp.gamma(s)))
    return pref * (M * r1 ** sig / sig + I) + gam
# compare with the computed Delta for inner cells
exec(open("poc/farey/certify_rho1.py").read().split("NC = 22")[0])
L = lambda tr: 2 * mp.acosh(mp.mpf(tr) / 2)
cells = []; st = [(3, 3, 3)] * 3
while st:
    tu, tw, td = st.pop(); tm = tu * tw - td; a, b, c = L(tu), L(tw), L(tm)
    if max(a, b) > 60: continue
    cells.append((float(a), float(b), float(c), float(a + b - c), (a, b, c))); st += [(tu, tm, tw), (tm, tw, tu)]
inner = [x for x in cells if max(x[0], x[1]) <= 22]; outer = [x for x in cells if max(x[0], x[1]) > 22]
viol = 0; ratios = []
for a, b, c, dl, ex in inner[:120]:
    d, _ = Delta(s, *ex); B = bound(a, b, c, dl); ratios.append(B / float(abs(d)))
    if B < float(abs(d)): viol += 1
print("bound / |Delta| over 120 computed cells: min %.2f, median %.1f, max %.1f; violations %d" % (min(ratios), float(np.median(ratios)), max(ratios), viol))
tail = 2 * sum(bound(a, b, c, dl) for a, b, c, dl, ex in outer)
# beyond N = 60: delta <= 15.24 e^{-(a+b)}, bound(a,b,c,delta)/delta grows polynomially; estimate from the largest cells
gr = max(bound(a, b, c, dl) / (15.24 * math.exp(-(a + b))) / (a + b) ** 6 for a, b, c, dl, ex in outer if a + b > 40)
print('envelope beyond 60: bound/delta_up <= %.3e (a+b)^6 on cells with a+b > 40' % gr)
far = 2 * sum(gr * (S + 1) ** 8 * 15.24 * math.exp(-S) for S in range(60, 600))   # (S+1)^2 bounds the number of cells with a+b in [S, S+1]
print("rigorous tail bound: cells with max N in (22, 60]: %.3e; beyond 60 (envelope from the explicit bounds): %.3e" % (tail, far))
print("certified: |Z_B(rho_1)| >= 5.997696 - %.2e" % (tail + far + 3.1e-21))
