"""Two lemmas behind the meromorphic continuation of Z_B.
(L1) delta(t_u, t_w) = N(t_u) + N(t_w) - N(t_m), t_m = larger root of x^2 - t_u t_w x + t_u^2 + t_w^2 (cusp).
     H(x, y) = delta * e^{N_u + N_w} as a function of x = 1/t_u, y = 1/t_w on (0, 1/3]^2: continuous, extends to the
     closed square, bounded by its value at (1/3, 1/3) (= 15.23...), and H -> 8 at (0, 0).
(L2) D(t) = g(a,c) + g(c,b) + h(c) - g(a,b) equals e^{ct}(e^{delta t} - 1)/((e^{at}-1)(e^{bt}-1)(e^{ct}-1)), c = a+b-delta;
     its Laurent coefficients at t = 0: d_-2 = delta/(abc), d_-1 = 0."""
import mpmath as mp
mp.mp.dps = 60
Nn = lambda t: 2 * mp.acosh(t / 2)
def delta(tu, tw):
    tm = (tu * tw + mp.sqrt((tu * tw) ** 2 - 4 * (tu * tu + tw * tw))) / 2
    return Nn(tu) + Nn(tw) - Nn(tm)
def H(tu, tw): return delta(tu, tw) * mp.exp(Nn(tu) + Nn(tw))
print("(L1) H on a grid of traces (rows t_u, columns t_w):")
ts = [3, 3.5, 5, 10, 30, 100, 1e3, 1e5, 1e8]
for tu in ts:
    print("   t_u = %-6g " % tu + " ".join("%8.4f" % H(mp.mpf(tu), mp.mpf(tw)) for tw in ts))
print("   H(1e12, 1e12) = %s  (limit 8);  H(3, 1e12) = %s;  H(3,3) = %s" % (mp.nstr(H(mp.mpf(10)**12, mp.mpf(10)**12), 12), mp.nstr(H(mp.mpf(3), mp.mpf(10)**12), 12), mp.nstr(H(mp.mpf(3), mp.mpf(3)), 12)))
# monotonicity check: max over a fine grid
mx = max(H(mp.mpf(3) + i * mp.mpf("0.05"), mp.mpf(3) + j * mp.mpf("0.05")) for i in range(40) for j in range(40))
print("   max over [3, 5]^2 grid: %s" % mp.nstr(mx, 10))
print("\n(L2) closed form of D(t) and Laurent coefficients:")
a, b = mp.mpf("1.9248"), mp.mpf("3.5255"); dl = mp.mpf("0.0123"); c = a + b - dl
g = lambda p, q, t: 1 / ((mp.exp(p * t) - 1) * (mp.exp(q * t) - 1))
D1 = lambda t: g(a, c, t) + g(c, b, t) + 1 / (mp.exp(c * t) - 1) - g(a, b, t)
D2 = lambda t: mp.exp(c * t) * (mp.exp(dl * t) - 1) / ((mp.exp(a * t) - 1) * (mp.exp(b * t) - 1) * (mp.exp(c * t) - 1))
for t in (mp.mpf("0.01"), mp.mpf("0.3"), mp.mpf(2), mp.mpf(7)):
    print("   t = %-5s: definition %s   closed form %s" % (t, mp.nstr(D1(t), 15), mp.nstr(D2(t), 15)))
ser = mp.taylor(lambda t: t * t * D2(t) if t != 0 else dl / (a * b * c), mp.mpf("1e-30"), 2)
print("   t^2 D(t) Taylor at 0: %s  [d_-2 = delta/(abc) = %s, d_-1 should be 0]" % ([mp.nstr(x, 10) for x in ser], mp.nstr(dl / (a * b * c), 10)))
