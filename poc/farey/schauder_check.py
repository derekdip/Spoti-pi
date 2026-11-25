import mpmath as mp
mp.mp.dps = 300
ok = lambda n, c, extra="": print(('PASS ' if c else 'FAIL ') + n + (("  " + extra) if extra else ""))
F = lambda t: mp.acosh(t / 2)
def child(a, b): return a * b / 2 * (1 + mp.sqrt(1 - 4 / a**2 - 4 / b**2))
def Phi(a, b): return (mp.sqrt(1 - 4 / a**2) + mp.sqrt(1 - 4 / b**2) - 1 - mp.sqrt(1 - 4 / a**2 - 4 / b**2)) / 4
h = lambda t: (1 - mp.sqrt(1 - 4 / t**2)) / 2
# Farey tree from the root pair (e0, e1), traces (3, 3); cells (a, b, depth, vector x, vector y)
cells = [(mp.mpf(3), mp.mpf(3), 0, (1, 0), (0, 1))]; allc = []
while cells:
    a, b, d, x, y = cells.pop(); allc.append((a, b, d, x, y))
    if d < 14 and a < mp.mpf(10)**60 and b < mp.mpf(10)**60:
        c = child(a, b); m = (x[0] + y[0], x[1] + y[1]); cells += [(a, c, d + 1, x, m), (c, b, d + 1, m, y)]
# 1. child solves Markoff
ok("forward child solves a^2+b^2+c^2=abc", max(abs(a*a + b*b + child(a, b)**2 - a*b*child(a, b)) / (a*b*child(a, b)) for a, b, *_ in allc) < mp.mpf(10)**-200)
# 2. McShane cell recursion
ok("Phi(a,b) = Phi(a,c) + Phi(c,b) + h(c)", max(abs(Phi(a, b) - Phi(a, child(a, b)) - Phi(child(a, b), b) - h(child(a, b))) for a, b, *_ in allc) < mp.mpf(10)**-150)
# 3. heap: h(child) < h(parent ends)
ok("h decreases down the tree (max-heap)", all(h(child(a, b)) < min(h(a), h(b)) for a, b, *_ in allc))
# 4. gap law g_m = log(c^2/(c^2-4)) from fans: slope jump = lim F(km+x) + F(km-x) - 2k F(m)
import itertools
worst = 0
for a, b, d, x, y in allc[:200]:
    c = child(a, b); lam = c / 2 + mp.sqrt(c**2 / 4 - 1)
    t0, t1 = a, a * c - b            # tr(x), tr(x+m)
    s0, s1 = a, b                    # tr(-x)=tr(x), tr(m-x)=tr(y)
    k = 60; tp = [t0, t1]; sp = [s0, s1]
    for _ in range(k): tp.append(c * tp[-1] - tp[-2]); sp.append(c * sp[-1] - sp[-2])
    gap = F(tp[k]) + F(sp[k]) - 2 * k * F(c)
    worst = max(worst, abs(gap - mp.log(c**2 / (c**2 - 4))))
ok("gap law g_m = log(c^2/(c^2-4)) = 2 log coth F(m)", worst < mp.mpf(10)**-20, f"(max error {mp.nstr(worst, 3)})")
c = mp.mpf(39); ok("g = -2 log(1-2h), h = 1/(1+e^{2F})", abs(mp.log(c**2/(c**2-4)) + 2*mp.log(1-2*h(c))) < 1e-40 and abs(h(c) - 1/(1+mp.e**(2*F(c)))) < 1e-40 and abs(2*mp.log(mp.coth(F(c))) - mp.log(c**2/(c**2-4))) < 1e-40)
# 5. D/Phi expansion
worst = 0
for a, b, d, *_ in allc:
    if d < 3 or a > mp.mpf(10)**25 or b > mp.mpf(10)**25: continue
    D = F(a) + F(b) - F(child(a, b)); X, Y = 1 / a**2, 1 / b**2
    pred = 4 + 4*X*Y + 8*X*Y*(X + Y) + 4*X*Y/3*(15*X**2 + 37*X*Y + 15*Y**2)
    worst = max(worst, abs(D / Phi(a, b) - pred) / (X*Y*(X + Y)**3))
ok("D/Phi = 4 + 4xy + 8xy(x+y) + (4xy/3)(15x^2+37xy+15y^2) + ...", worst < 50, f"(remainder / xy(x+y)^3 at most {mp.nstr(worst, 3)}, bounded: next order)")
ok("D/h > 4 on every cell", all((F(a) + F(b) - F(child(a, b))) / h(child(a, b)) > 4 for a, b, *_ in allc if a < 1e25 and b < 1e25))
# 6. Green transform D(x,y) = sum over subtree mediants of min(alpha,beta) g
def green(a, b, depth=26):
    tot = mp.mpf(0); st = [(a, b, (1, 0), (0, 1), 0)]
    while st:
        p, q, u, v, dd = st.pop(); c = child(p, q); w = (u[0] + v[0], u[1] + v[1])
        tot += min(w) * mp.log(c**2 / (c**2 - 4))
        if dd < depth and c < mp.mpf(10)**30: st += [(p, c, u, w, dd + 1), (c, q, w, v, dd + 1)]
    return tot
for a, b in [(mp.mpf(3), mp.mpf(3)), (mp.mpf(3), mp.mpf(6)), (mp.mpf(6), mp.mpf(15))]:
    D = F(a) + F(b) - F(child(a, b)); G = green(a, b, 18)
    ok(f"Green transform at traces ({int(a)},{int(b)}): D = {mp.nstr(D, 12)}, sum = {mp.nstr(G, 12)}", abs(D - G) / D < 1e-6)
