"""Farey tessellation of the hyperbolic plane, viewed in the Poincare disk.

Tiles are ideal triangles. Exact enumeration walks the Stern-Brocot tree: tile (u, m, v) with Farey neighbours
u = a/b < v = c/d and mediant m, plus the tiles (n, n+1, inf). Vertices are exact integers, every tile appears once,
and a subtree is pruned as soon as its covering arc on the boundary circle is below eps (children lie inside the arc).
The float BFS baseline crosses edges by reflecting the third vertex in float and deduplicates with a hash.
"""
import math, cmath
from collections import deque

TWO_PI = 2 * math.pi
def boundary_angle(p, q):
    """Angle on the unit circle of the ideal point p/q (q = 0 is infinity), after the Cayley map z -> (z - i)/(z + i)."""
    if q == 0: return 0.0
    x = p / q; w = (x - 1j) / (x + 1j); return cmath.phase(w) % TWO_PI
def covering_arc(angles):
    """Length of the smallest arc containing the given boundary angles (2 pi minus the largest gap)."""
    a = sorted(angles); gaps = [a[i + 1] - a[i] for i in range(len(a) - 1)] + [a[0] + TWO_PI - a[-1]]
    return TWO_PI - max(gaps)

def farey_tiles(eps, nmax=10**6):
    """Exact enumeration of all tiles with covering arc >= eps. Returns tiles as triples of (p, q) pairs."""
    out = []
    n = 0
    for direction in (1, -1):
        n = 0 if direction == 1 else -1
        while True:                                   # tiles (n, n+1, inf)
            t = ((n, 1), (n + 1, 1), (1, 0))
            if covering_arc([boundary_angle(*v) for v in t]) < eps: break
            out.append(t)
            # Stern-Brocot subtree under the interval [n, n+1]
            st = [((n, 1), (n + 1, 1))]
            while st:
                (a, b), (c, d) = st.pop(); m = (a + c, b + d)
                t2 = ((a, b), m, (c, d))
                if covering_arc([boundary_angle(*v) for v in t2]) < eps: continue
                out.append(t2); st.append(((a, b), m)); st.append((m, (c, d)))
            n += direction
            if abs(n) > nmax: break
    return out

# ---------------- float BFS baseline (projective vectors, reflection across the shared geodesic)
def reflect(P, Q, R):
    """Image of ideal point R (projective 2-vector) under the reflection in the geodesic with endpoints P, Q:
    the linear map fixing P and negating Q."""
    det = P[0] * Q[1] - P[1] * Q[0]
    # coordinates of R in the basis (P, Q)
    alpha = (R[0] * Q[1] - R[1] * Q[0]) / det; beta = (P[0] * R[1] - P[1] * R[0]) / det
    return (alpha * P[0] - beta * Q[0], alpha * P[1] - beta * Q[1])
def vec_angle(V):
    if abs(V[1]) < 1e-300 * max(1.0, abs(V[0])) or V[1] == 0: return 0.0
    x = V[0] / V[1]; w = (x - 1j) / (x + 1j); return cmath.phase(w) % TWO_PI
def float_bfs_tiles(eps, key_digits=9):
    start = ((0.0, 1.0), (1.0, 1.0), (1.0, 0.0))
    def key(t): return tuple(sorted(round(vec_angle(v), key_digits) for v in t))
    seen = {key(start)}; q = deque([start]); out = []
    while q:
        t = q.popleft(); out.append(t)
        for i in range(3):
            P, Qv, R = t[(i + 1) % 3], t[(i + 2) % 3], t[i]
            Rn = reflect(P, Qv, R); nb = (P, Qv, Rn)
            if covering_arc([vec_angle(v) for v in nb]) < eps: continue
            k = key(nb)
            if k in seen: continue
            seen.add(k); q.append(nb)
    return out
