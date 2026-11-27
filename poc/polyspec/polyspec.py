"""Exact DFT coefficients of a rasterised convex polygon in O(edges * log N) per coefficient.

F(kx, ky) = sum over integer points (x, y) in the closed polygon of w^x z^y, w = e^{-2 pi i kx/N}, z = e^{-2 pi i ky/N}.
Column decomposition: F = sum_x w^x (z^{U(x)+1} - z^{L(x)})/(z - 1), U = floor(upper edge), L = ceil(lower edge).
Along one edge U(x) = floor((A x + B)/D), so each edge needs G = sum_t w^t z^{floor((a t + b)/c)}: a product over the
edge's Christoffel word in the monoid
    (alpha, beta, gamma) . (alpha', beta', gamma') = (alpha alpha', beta beta', gamma + alpha beta gamma'),
    U-step = (1, z, 0),  R-step = (w, 1, 1),
evaluated by the universal Euclidean algorithm (the same recursion as floor_sum) in O(log) monoid products.
For z = 1 (the ky = 0 row) the sum needs sum_t w^t floor(...), done with a 4-component monoid."""
import math, cmath
from fractions import Fraction as Fr

def mpow(x, e, mul, one):
    r = one
    while e:
        if e & 1: r = mul(r, x)
        x = mul(x, x); e >>= 1
    return r
def ueuclid(p, q, r, l, U, R, mul, one):
    """Product of the word for t = 1..l in which the t-th R is preceded by floor((p t + r)/q) U's in total.
    Requires p >= 0, q > 0, 0 <= r < q."""
    if l == 0: return one
    if p >= q: return ueuclid(p % q, q, r, l, U, mul(mpow(U, p // q, mul, one), R), mul, one)
    m = (p * l + r) // q
    if m == 0: return mpow(R, l, mul, one)
    cnt = l - (q * m - r - 1) // p
    return mul(mul(mul(mpow(R, (q - r - 1) // p, mul, one), U), ueuclid(q, p, (q - r - 1) % p, m - 1, R, U, mul, one)), mpow(R, cnt, mul, one))

# exponential monoid
def emul(X, Y): return (X[0] * Y[0], X[1] * Y[1], X[2] + X[0] * X[1] * Y[2])
EONE = (1, 1, 0)
# linear-weight monoid for z = 1: maps (p, y, S) -> (al p, y + de, S + p (ga y + ep))
def lmul(X, Y): return (X[0] * Y[0], X[1] + Y[1], X[2] + X[0] * Y[2], X[3] + X[0] * (Y[2] * X[1] + Y[3]))
LONE = (1, 0, 0, 0)

def G_exp(n, a, b, c, w, z):
    """sum_{t=0}^{n-1} w^t z^{floor((a t + b)/c)}, integers a, b and c > 0."""
    if n <= 0: return 0
    pre = 1
    if a < 0: pre = w ** (n - 1); w = 1 / w; b = b + a * (n - 1); a = -a
    k, b0 = divmod(b, c)
    prod = emul((w, 1, 1), ueuclid(a, c, b0, n - 1, (1, z, 0), (w, 1, 1), emul, EONE))
    return pre * z ** k * prod[2]
def G_lin(n, a, b, c, w):
    """sum_{t=0}^{n-1} w^t floor((a t + b)/c)."""
    if n <= 0: return 0
    pre = 1
    if a < 0: pre = w ** (n - 1); w = 1 / w; b = b + a * (n - 1); a = -a
    k, b0 = divmod(b, c)
    pr = lmul((w, 0, 1, 0), ueuclid(a, c, b0, n - 1, (1, 1, 0, 0), (w, 0, 1, 0), lmul, LONE))
    return pre * (pr[2] * k + pr[3])

def _chains(verts):
    n = len(verts)
    i_min = min(range(n), key=lambda i: (verts[i][0], verts[i][1])); i_max = max(range(n), key=lambda i: (verts[i][0], -verts[i][1]))
    lower, upper = [], []
    i = i_min
    while i != i_max: lower.append((verts[i], verts[(i + 1) % n])); i = (i + 1) % n
    i = i_max
    while i != i_min: upper.append((verts[(i + 1) % n], verts[i])); i = (i + 1) % n
    upper.reverse()
    return lower, upper
def _edge_pieces(chain):
    """For each non-vertical edge: (xa, n, A, B, D) with y = (A x + B)/D over integer x in [xa, xa + n - 1], each
    integer column used once."""
    out = []; xprev = None
    for P, Q in chain:
        if P[0] == Q[0]: continue
        xa = math.ceil(P[0]); xb = math.floor(Q[0])
        if xprev is not None and xa <= xprev: xa = xprev + 1
        if xb < xa: continue
        s = (Q[1] - P[1]) / (Q[0] - P[0]); c0 = P[1] - s * P[0]
        D = s.denominator * c0.denominator // math.gcd(s.denominator, c0.denominator)
        out.append((xa, xb - xa + 1, int(s * D), int(c0 * D), D)); xprev = xb
    return out
def polygon_dft(verts, kx, ky, N):
    """Exact (up to float rounding) sum over integer points of the closed convex polygon (CCW Fraction vertices)."""
    w = cmath.exp(-2j * math.pi * kx / N); z = cmath.exp(-2j * math.pi * ky / N)
    lower, upper = _chains(verts)
    up, lo = _edge_pieces(upper), _edge_pieces(lower)
    if ky % N == 0:
        tot = 0
        for xa, n, A, B, D in up: tot += w ** xa * G_lin(n, A, A * xa + B, D, w)
        for xa, n, A, B, D in lo: tot += w ** xa * G_lin(n, -A, -(A * xa + B), D, w)     # -ceil(t) = floor(-t)
        xs = [v[0] for v in verts]; x0, x1 = math.ceil(min(xs)), math.floor(max(xs))
        cols = (x1 - x0 + 1) if kx % N == 0 else (w ** x0 * (1 - w ** (x1 - x0 + 1)) / (1 - w) if x1 >= x0 else 0)
        return tot + cols
    su = sum(w ** xa * G_exp(n, A, A * xa + B, D, w, z) for xa, n, A, B, D in up)
    sl = sum(w ** xa * G_exp(n, -A, -(A * xa + B), D, w, 1 / z) for xa, n, A, B, D in lo)   # z^ceil(t) = (1/z)^floor(-t)
    return (z * su - sl) / (z - 1)
