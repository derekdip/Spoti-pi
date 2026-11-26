"""Exact cusp asymptotics of the stable-norm zeta: as alpha shrinks to length l,
   Z_X(s) = 2 zeta(s) l^-s + (2/l) zeta(s-1) I(s, W) + o(1/l),   W = 2 log(4/l),
   I(s, W) = 2 (W - 2 log 2)^{1-s}/(s-1) + int_R [ (W + F(y))^-s - (W + |y| - 2 log 2)^-s ] dy,   F = 2 log cosh(y/2).
 Compared with the cell sums l * (Z(-m) - 2 zeta(-m) l^m) at l = 0.4 ... 0.00625 (cusp_asymptotics.log)."""
import mpmath as mp
mp.mp.dps = 30
def I(s, W):
    A = W - 2 * mp.log(2)
    f = lambda y: (W + 2 * mp.log(mp.cosh(y / 2))) ** (-s) - (A + y) ** (-s)
    return 2 * A ** (1 - s) / (s - 1) + 2 * mp.quad(f, [0, 1, 5, 20, mp.inf])
def I_int(m, W):   # I(-m, W), stable: (A+y+h)^m - (A+y)^m = sum_{j>=1} C(m,j) (A+y)^{m-j} h^j,  h = 2 log(1 + e^-y)
    A = W - 2 * mp.log(2)
    h = lambda y: 2 * mp.log1p(mp.exp(-y))
    f = lambda y: sum(mp.binomial(m, j) * (A + y) ** (m - j) * h(y) ** j for j in range(1, m + 1))
    return -2 * A ** (m + 1) / (m + 1) + 2 * mp.quad(f, [0, 1, 5, 20, 80])
def P(m, l):   # predicted l (Z(-m) - 2 zeta(-m) l^m)
    W = 2 * mp.log(4 / mp.mpf(l))
    return 2 * mp.zeta(-m - 1) * I_int(m, W)
data = {0.4: (1.0921, 0.1745, -11.1716), 0.2: (1.5393, -0.4120, -18.5138), 0.1: (1.9981, -1.5707, -20.8113),
        0.05: (2.4595, -3.4923, -5.1740), 0.025: (2.9214, -6.3581, 49.6760), 0.0125: (3.3835, -10.3465, 175.3796), 0.00625: (3.8456, -15.6353, 415.9086)}
print("   l       |  m = 0: model / cells      |  m = 2: model / cells       |  m = 4: model / cells")
for l, (d0, d2, d4) in data.items():
    p = [P(m, l) for m in (0, 2, 4)]
    print("  %.5f  | %9.4f / %9.4f | %10.4f / %10.4f | %11.4f / %11.4f" % (l, p[0], d0, p[1], d2, p[2], d4))
L = mp.mpf(5.075); print("closed form m = 2 at l = 0.00625: %s" % mp.nstr(-(mp.mpf(4)/45)*(L+mp.log(2))**3 + mp.pi**2/45*(L+mp.log(2)) + 2*mp.zeta(3)/15, 8))
