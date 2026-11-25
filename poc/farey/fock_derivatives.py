"""One-sided derivatives of Fock's function psi(p/q) = (1/q) arccosh(3 m(p/q) / 2) at rationals, the question left
open in Sorrentino-Veselov (arXiv 1707.03901, section 5). Closed forms derived from the Markoff fan recurrence:
  with c = 3m, F = arccosh(c/2), lam = e^F, Farey parents u (left) and w (right), traces a_u = 3 m_u, a_w = 3 m_w,
  psi'(p/q +) = q log((a_w lam - a_u)/(lam - 1/lam)) - q_w F
  psi'(p/q -) = q_u F - q log((a_u lam - a_w)/(lam - 1/lam))
  jump = q log(c^2/(c^2 - 4)).
Checked here against psi computed directly from Markov numbers at points k/(...) approaching p/q from both sides.
"""
import mpmath as mp
mp.mp.dps = 80
# Markov numbers on the Farey tree of [0, 1]: m(0/1) = m(1/1) = 1, m(1/2) = 2; a cell (L, R) with mediant L+R is the
# Markov triple (m_L, m_R, m_{L+R}), and Vieta gives m_{L+R} = 3 m_L m_R - m_{R-L} (m of -v is m of v)
def canon(v): return v if (v[1] > 0 or (v[1] == 0 and v[0] > 0)) else (-v[0], -v[1])
def markov_tree(depth):
    M = {(0, 1): mp.mpf(1), (1, 1): mp.mpf(1), (1, 0): mp.mpf(1), (1, 2): mp.mpf(2)}; cells = [((0, 1), (1, 2)), ((1, 2), (1, 1))]
    for _ in range(depth):
        nxt = []
        for L, R in cells:
            mid = (L[0] + R[0], L[1] + R[1]); M[mid] = 3 * M[L] * M[R] - M[canon((R[0] - L[0], R[1] - L[1]))]; nxt += [(L, mid), (mid, R)]
        cells = nxt
    return M
M = markov_tree(15)
F = lambda m: mp.acosh(3 * m / 2)
psi = lambda pq: F(M[pq]) / pq[1]
def parents(pq):
    """Stern-Brocot search from (0/1, 1/1): the two Farey parents of p/q, left then right."""
    L, R = (0, 1), (1, 1)
    while True:
        mid = (L[0] + R[0], L[1] + R[1])
        if mid == pq: return L, R
        if pq[0] * mid[1] < mid[0] * pq[1]: R = mid
        else: L = mid
def closed(pq):
    (u, w) = parents(pq); c = 3 * M[pq]; Fm = mp.acosh(c / 2); lam = mp.e**Fm; au, aw = 3 * M[u], 3 * M[w]; q = pq[1]
    right = q * mp.log((aw * lam - au) / (lam - 1 / lam)) - w[1] * Fm; left = u[1] * Fm - q * mp.log((au * lam - aw) / (lam - 1 / lam))
    return left, right, q * mp.log(c**2 / (c**2 - 4))
def numeric(pq, k):
    (u, w) = parents(pq); x0 = mp.mpf(pq[0]) / pq[1]; out = []
    for nb in (u, w):   # fan points k*pq + nb lie in the tree for k up to the depth
        v = (k * pq[0] + nb[0], k * pq[1] + nb[1]); x = mp.mpf(v[0]) / v[1]; out.append((psi(v) - psi(pq)) / (x - x0))
    return out[0], out[1]
for pq in [(1, 2), (1, 3), (2, 5), (1, 4), (3, 8)]:
    l, r, j = closed(pq); nl, nr = numeric(pq, 10)
    print(f"x = {pq[0]}/{pq[1]} (m = {int(M[pq])}): psi'(-) = {mp.nstr(l, 12)} [numeric {mp.nstr(nl, 12)}], psi'(+) = {mp.nstr(r, 12)} [numeric {mp.nstr(nr, 12)}], jump {mp.nstr(j, 12)} = q log(9m^2/(9m^2-4))")
print("at x = 1/2 the closed form gives +-log(9/8) =", mp.nstr(mp.log(mp.mpf(9) / 8), 15))


# Sorrentino-Veselov's a-family (their Theorem 3): traces X^2 + Y^2 + Z^2 = XYZ + 4 - 4a^6, i.e. mu = 4 - 4a^6,
# psi_a(p/q) = (1/q) arccosh(X(p/q)/2). Their matrices A_a, B_a give traces a^2 + 2 at 0/1 and 4a^2 + 2 at 1/2; the
# third vertex of the root triple is the small root. One-sided derivatives use the same closed form with traces,
# and the jump becomes q log((c^2 - mu)/(c^2 - 4)).
def a_family(a, depth=15):
    mu = 4 - 4 * mp.mpf(a)**6; x, y = mp.mpf(a)**2 + 2, 4 * mp.mpf(a)**2 + 2
    z = (x * y - mp.sqrt((x * y)**2 - 4 * (x * x + y * y - mu))) / 2
    T = {(0, 1): x, (1, 2): y, (1, 1): z}; cells = [((0, 1), (1, 2)), ((1, 2), (1, 1))]
    for _ in range(depth):
        nxt = []
        for L, R in cells:
            mid = (L[0] + R[0], L[1] + R[1]); T[mid] = T[L] * T[R] - T[canon((R[0] - L[0], R[1] - L[1]))]; nxt += [(L, mid), (mid, R)]
        cells = nxt
    return T, mu
for a in (2, 3):
    T, mu = a_family(a); ps = lambda pq: mp.acosh(T[pq] / 2) / pq[1]
    for pq in [(1, 3), (2, 5), (1, 4)]:
        u, w = parents(pq); c = T[pq]; Fm = mp.acosh(c / 2); lam = mp.e**Fm; q = pq[1]; x0 = mp.mpf(pq[0]) / q
        right = q * mp.log((T[w] * lam - T[u]) / (lam - 1 / lam)) - w[1] * Fm; left = u[1] * Fm - q * mp.log((T[u] * lam - T[w]) / (lam - 1 / lam))
        k = 10; nl, nr = [(ps((k * pq[0] + nb[0], k * pq[1] + nb[1])) - ps(pq)) / (mp.mpf(k * pq[0] + nb[0]) / (k * pq[1] + nb[1]) - x0) for nb in (u, w)]
        print(f"a = {a}, x = {pq[0]}/{pq[1]}: psi_a'(-) {mp.nstr(left, 12)} [numeric {mp.nstr(nl, 12)}], psi_a'(+) {mp.nstr(right, 12)} [numeric {mp.nstr(nr, 12)}], jump {mp.nstr(right - left, 12)} vs q log((c^2-mu)/(c^2-4)) = {mp.nstr(q * mp.log((c * c - mu) / (c * c - 4)), 12)}")
