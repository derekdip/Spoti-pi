"""Search for closed forms of natural sums over the Farey/Markoff tree of the modular torus (root traces 3, 3 at
directions (1,0), (0,1), opposite trace 3), by integer relations (PSLQ) against a basis of constants that occur here.

Cells v of the tree: endpoint traces a, b, mediant trace c, endpoint heights X, Y (p + q on the slice), M = X + Y.
D_v = F(a) + F(b) - F(c) (the Farey-Schauder defect), F = arccosh(t/2); h(c) = (1 - sqrt(1 - 4/c^2))/2 (McShane atom);
g(c) = log(c^2/(c^2 - 4)) (the slope jump at the mediant, per unit height).
Control: sum M g is Hines' identity (O'Sullivan Thm 9.14); PSLQ must recover it for a negative result to mean much.
Sums are taken best-first until every frontier term is below 1e-75.
"""
import heapq
import mpmath as mp
mp.mp.dps = 90
F = lambda t: mp.acosh(t / 2)
h = lambda t: (1 - mp.sqrt(1 - 4 / t**2)) / 2
g = lambda t: mp.log(t**2 / (t**2 - 4))


def sums(tol=mp.mpf(10)**-75):
    S = {k: mp.mpf(0) for k in ("D", "D/M", "D/(XYM)", "h", "M h", "M g", "g", "1/c^2", "M/c^2", "D M", "h/M", "X Y g")}
    hp = [(-1.0, mp.mpf(3), mp.mpf(3), mp.mpf(3), 1, 1)]; n = 0
    while hp:
        _, a, b, o, X, Y = heapq.heappop(hp); c = a * b - o; M = X + Y; D = F(a) + F(b) - F(c)
        terms = {"D": D, "D/M": D / M, "D/(XYM)": D / (X * Y * M), "h": h(c), "M h": M * h(c), "M g": M * g(c), "g": g(c),
                 "1/c^2": 1 / c**2, "M/c^2": M / c**2, "D M": D * M, "h/M": h(c) / M, "X Y g": X * Y * g(c)}
        for k, v in terms.items(): S[k] += v
        n += 1
        if max(abs(v) for v in terms.values()) > tol:
            for (aa, bb, oo, XX, YY) in ((a, c, b, X, M), (c, b, a, M, Y)):
                heapq.heappush(hp, (-float(1 / (aa * bb)**2 * (XX + YY)), aa, bb, oo, XX, YY))
    return S, n


if __name__ == "__main__":
    S, n = sums()
    l3 = mp.log((3 + mp.sqrt(5)) / 2); l6 = mp.log(3 + 2 * mp.sqrt(2)); s5 = mp.sqrt(5)
    basis_names = ["1", "log2", "log3", "log5", "log lam3", "log(3+2sqrt2)", "pi^2", "sqrt5", "sqrt5 log lam3"]
    basis = [mp.mpf(1), mp.log(2), mp.log(3), mp.log(5), l3, l6, mp.pi**2, s5, s5 * l3]
    print(f"{n} cells summed")
    mp.mp.dps = 60
    for k, v in S.items():
        rel = mp.pslq([v] + basis, maxcoeff=2000, maxsteps=200000)
        if rel and rel[0] != 0:
            expr = " + ".join(f"{-r}/{rel[0]}*{nm}" for r, nm in zip(rel[1:], basis_names) if r != 0)
            print(f"{k:>9} = {mp.nstr(v, 30)}   relation: {k} = {expr}")
        else:
            print(f"{k:>9} = {mp.nstr(v, 30)}   no relation with coefficients up to 2000")
