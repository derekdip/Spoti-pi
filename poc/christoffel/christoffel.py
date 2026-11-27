"""Christoffel words, digital lines and exact lattice counting from the Farey / Stern-Brocot tree.

The lower Christoffel word of slope p/q (gcd 1) has q letters 'x' (step right) and p letters 'y' (step up), and is
the step sequence of the lattice path just below the segment (0,0)-(q,p). It is built by mediant concatenation,
w(p/q) = w(a/b) w(c/d) for the Farey parents a/b < p/q < c/d, starting from w(0/1) = 'x' and w(1/0) = 'y'. That is
the same tree the Markoff numbers and simple geodesics live on.
"""
from math import gcd

# ---------------------------------------------------------------- words
def christoffel_closed(p, q):
    """Closed form: letter k (1..n), n = p+q, is 'x' iff k p mod n > (k-1) p mod n."""
    n = p + q
    return "".join("x" if (k * p) % n > ((k - 1) * p) % n else "y" for k in range(1, n + 1))

def christoffel(p, q):
    """Mediant (Stern-Brocot) construction."""
    assert gcd(p, q) == 1 and p >= 0 and q >= 0 and p + q > 0
    lo, hi = (0, 1, "x"), (1, 0, "y")             # (num, den, word)
    while True:
        mn, md = lo[0] + hi[0], lo[1] + hi[1]
        if (mn, md) == (p, q) or (p, q) in ((0, 1), (1, 0)):
            return {(0, 1): "x", (1, 0): "y"}.get((p, q), lo[2] + hi[2])
        if p * md < mn * q: hi = (mn, md, lo[2] + hi[2])
        else: lo = (mn, md, lo[2] + hi[2])

# ---------------------------------------------------------------- compressed form (straight-line program)
class SLP:
    """Christoffel word as a straight-line program: node 0 = 'x', node 1 = 'y', node i = (left, right).
    Built along the continued fraction with repeated squaring, so it has O(log(p+q)) nodes even for huge p, q."""
    def __init__(self, p, q):
        self.nodes = ["x", "y"]; self.len = [1, 1]; self.ny = [0, 1]
        self.root = self._build(p, q)
    def _cat(self, a, b):
        self.nodes.append((a, b)); self.len.append(self.len[a] + self.len[b]); self.ny.append(self.ny[a] + self.ny[b])
        return len(self.nodes) - 1
    def _pow(self, a, k):                       # a^k by squaring (k >= 1)
        res = None; base = a
        while k:
            if k & 1: res = base if res is None else self._cat(res, base)
            k >>= 1
            if k: base = self._cat(base, base)
        return res
    def _build(self, p, q):
        # walk the Stern-Brocot tree in runs: each run of k equal moves is one power
        lo, hi = 0, 1                            # node ids of current parents' words, slopes 0/1 and 1/0
        lf, hf = (0, 1), (1, 0)
        if (p, q) == (0, 1): return 0
        if (p, q) == (1, 0): return 1
        while True:
            # number of consecutive moves toward lo side (mediant > target => replace hi) or hi side
            mn, md = lf[0] + hf[0], lf[1] + hf[1]
            if (mn, md) == (p, q): return self._cat(lo, hi)
            if p * md < mn * q:
                # target below mediant: hi <- lo^k hi for the largest k keeping target below
                # mediant_k = (k lf + hf); find max k with p*(k lf1+hf1) < (k lf0+hf0)*q
                num = hf[0] * q - p * hf[1]; den = p * lf[1] - lf[0] * q
                k = max(1, (num - 1) // den) if den > 0 else 1
                hi = self._cat(self._pow(lo, k), hi) if k > 0 else hi
                hf = (k * lf[0] + hf[0], k * lf[1] + hf[1])
            else:
                num = p * lf[1] - lf[0] * q; den = hf[0] * q - p * hf[1]
                k = max(1, (num - 1) // den) if den > 0 else 1
                lo = self._cat(lo, self._pow(hi, k))
                lf = (lf[0] + k * hf[0], lf[1] + k * hf[1])
    def expand(self, i=None):
        i = self.root if i is None else i; out = []; st = [i]
        while st:
            j = st.pop()
            if j < 2: out.append(self.nodes[j])
            else: a, b = self.nodes[j]; st += [b, a]
        return "".join(out)
    def letter(self, k):
        """k-th letter (0-based) in O(depth)."""
        j = self.root
        while j >= 2:
            a, b = self.nodes[j]
            if k < self.len[a]: j = a
            else: k -= self.len[a]; j = b
        return self.nodes[j]
    def height(self, k):
        """Number of 'y' among the first k letters, i.e. the digital line's y after k steps, in O(depth)."""
        j = self.root; h = 0
        while k > 0 and j >= 2:
            a, b = self.nodes[j]
            if k >= self.len[a]: h += self.ny[a]; k -= self.len[a]; j = b
            else: j = a
        return h + (1 if (k > 0 and j == 1) else 0)

# ---------------------------------------------------------------- digital lines
def digital_line(x0, y0, x1, y1):
    """Pixels of the digital segment between integer points, all octants, from the Christoffel word of the reduced
    slope (repeated g = gcd times). Rounds like Bresenham: y = round-half-down of the exact line in the major axis."""
    dx, dy = x1 - x0, y1 - y0; sx, sy = (1 if dx >= 0 else -1), (1 if dy >= 0 else -1); ax, ay = abs(dx), abs(dy)
    steep = ay > ax
    if steep: ax, ay = ay, ax
    pts = [(x0, y0)]
    if ax == 0: return pts
    # minor coordinate after i major steps: floor((2 i ay + ax) / (2 ax))  (nearest, ties down)
    x, y = x0, y0
    for i in range(1, ax + 1):
        m = (2 * i * ay + ax - 1) // (2 * ax)
        if steep: pts.append((x0 + sx * m, y0 + sy * i))
        else: pts.append((x0 + sx * i, y0 + sy * m))
    return pts

def bresenham(x0, y0, x1, y1):
    """Reference integer Bresenham (all octants)."""
    pts = []; dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; err = dx + dy
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1: return pts
        e2 = 2 * err
        if e2 >= dy: err += dy; x += sx
        if e2 <= dx: err += dx; y += sy

def spans(p, q):
    """Horizontal run lengths of the lower digital line of slope p/q < 1 over one period, read off the Christoffel
    word: the lengths of the 'x'-blocks. They take only two values, floor(q/p) and ceil(q/p) (balance property)."""
    w = christoffel(p, q); runs = []; c = 0
    for ch in w:
        if ch == "x": c += 1
        else: runs.append(c); c = 0
    if c: runs.append(c)
    return runs

# ---------------------------------------------------------------- exact counting
def floor_sum(n, m, a, b):
    """sum_{i=0}^{n-1} floor((a i + b)/m), m > 0, in O(log) (Euclid-like recursion)."""
    ans = 0
    while True:
        if a >= m or a < 0: ans += (n - 1) * n // 2 * (a // m); a %= m
        if b >= m or b < 0: ans += n * (b // m); b %= m
        y_max = a * n + b
        if y_max < m: return ans
        n, b, m, a = y_max // m, y_max % m, a, m

def lattice_points_in_convex_polygon(verts):
    """Exact number of integer points (interior + boundary) in a convex polygon with rational vertices, given as
    (Fraction, Fraction) pairs in counter-clockwise order. Column sums floor(upper) - ceil(lower) + 1 via floor sums
    on each edge (exact rational arithmetic)."""
    from fractions import Fraction as F
    import math
    xs = [v[0] for v in verts]; xmin, xmax = math.ceil(min(xs)), math.floor(max(xs))
    n = len(verts); total = 0
    # split boundary into upper and lower chains by x; each edge contributes over the integer x in its range
    def edge_sum(P, Q, upper, xa, xb):
        # sum over integer x in [xa, xb] of floor(y(x)) (upper) or -ceil(y(x)) (lower) for the line through P, Q
        (x1, y1), (x2, y2) = P, Q
        if xb < xa: return 0
        s = (y2 - y1) / (x2 - x1); c0 = y1 - s * x1            # y = s x + c0, rationals
        D = s.denominator * c0.denominator
        A = int(s * D); B = int(c0 * D)                        # y = (A x + B)/D
        if upper: return floor_sum(xb - xa + 1, D, A, A * xa + B)
        return floor_sum(xb - xa + 1, D, -A, -(A * xa + B))    # sum of -ceil(t) = sum of floor(-t)
    # integer columns, handling vertical edges and each column once: use chains
    import itertools
    i_min = min(range(n), key=lambda i: (verts[i][0], verts[i][1])); i_max = max(range(n), key=lambda i: (verts[i][0], -verts[i][1]))
    lower, upper = [], []
    i = i_min
    while i != i_max: lower.append((verts[i], verts[(i + 1) % n])); i = (i + 1) % n
    i = i_max
    while i != i_min: upper.append((verts[(i + 1) % n], verts[i])); i = (i + 1) % n   # each edge oriented left to right
    upper.reverse()                                                                  # and the chain ordered left to right
    def chain_sum(chain, up):
        tot = 0; xprev = None
        for P, Q in chain:
            if P[0] == Q[0]: continue
            xa = math.ceil(P[0]); xb = math.floor(Q[0])
            if xprev is not None and xa <= xprev: xa = xprev + 1
            if xb >= xa: tot += edge_sum(P, Q, up, xa, xb); xprev = xb
        return tot
    cols = xmax - xmin + 1 if xmax >= xmin else 0
    # vertical edges at integer x: chain_sum skips them; handle the extreme columns where the chain value is a vertex
    return chain_sum(upper, True) + chain_sum(lower, False) + cols

# ---------------------------------------------------------------- the bridge to Markoff numbers and geodesics
A_COHN = ((2, 1), (1, 1)); B_COHN = ((5, 2), (2, 1))
def matmul(X, Y): return ((X[0][0]*Y[0][0]+X[0][1]*Y[1][0], X[0][0]*Y[0][1]+X[0][1]*Y[1][1]), (X[1][0]*Y[0][0]+X[1][1]*Y[1][0], X[1][0]*Y[0][1]+X[1][1]*Y[1][1]))
def cohn_trace(p, q):
    """Trace of the Christoffel word of slope p/q with x -> A, y -> B: equals 3 m(p/q), m the Markoff number."""
    M = ((1, 0), (0, 1))
    for ch in christoffel(p, q): M = matmul(M, A_COHN if ch == "x" else B_COHN)
    return M[0][0] + M[1][1]
