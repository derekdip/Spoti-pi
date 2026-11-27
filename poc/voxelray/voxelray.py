"""Exact voxel ray traversal with O(log) random access: the 3D analogue of Christoffel digital lines.

Ray P(t) = O + t D, origin O = (o_x, o_y, o_z)/S with integers o, S > 0, integer direction D.
Convention: at parameter t the ray is in the voxel containing P(t + 0); per axis the index is floor(x) for d >= 0 and
ceil(x) - 1 for d < 0. Per axis the plane crossings happen at t_j = (j - f)/|d|, j = 1, 2, ..., with offset
f = (x0 - floor x0) for d > 0 and (ceil x0 - x0) for d < 0, f in [0, 1). Everything is exact integer arithmetic:
with f = F/S, crossing j of axis a has time numerator (j S - F_a)/|d_a| over the common S.
Ties (edges, corners): policy 'face' steps the tied axes one at a time in order x, y, z (a 6-connected path);
'all' steps them together (26-connected).
"""
from fractions import Fraction as Fr
from math import floor

class Ray:
    def __init__(self, o, S, d):
        self.o, self.S, self.d = tuple(o), S, tuple(d)
        self.sgn = tuple((1 if di > 0 else -1 if di < 0 else 0) for di in d)
        self.ad = tuple(abs(di) for di in d)
        self.start, self.F = [], []
        for oi, di in zip(o, d):
            if di >= 0: v = oi // S; F = oi - v * S
            else: v = -((-oi) // S) - 1; F = (v + 1) * S - oi          # ceil(x0) - 1 and S (ceil x0 - x0)
            self.start.append(v); self.F.append(F)
    # ---------- sequential exact DDA
    def traverse(self, nsteps, policy="face"):
        v = list(self.start); j = [1, 1, 1]; out = [tuple(v)]
        def tnum(a): return (j[a] * self.S - self.F[a], self.ad[a])          # time = num/(ad * S)
        while len(out) <= nsteps:
            act = [a for a in range(3) if self.ad[a]]
            # earliest crossing by cross-multiplication
            best = None
            for a in act:
                n, dd = tnum(a)
                if best is None or n * best[2] < best[1] * dd: best = (a, n, dd)
            tied = [a for a in act if tnum(a)[0] * best[2] == best[1] * tnum(a)[1]]
            if policy == "face":
                for a in tied:                                   # x, y, z order
                    v[a] += self.sgn[a]; j[a] += 1; out.append(tuple(v))
                    if len(out) > nsteps: break
            else:
                for a in tied: v[a] += self.sgn[a]; j[a] += 1
                out.append(tuple(v))
        return out[: nsteps + 1]
    # ---------- counting and random access ('face' policy)
    def count_le(self, a, t):        # crossings of axis a with time <= t (t a Fraction), = floor(|d| t + f)
        if self.ad[a] == 0 or t < 0: return 0
        return max(0, floor(self.ad[a] * t + Fr(self.F[a], self.S)))
    def count_lt(self, a, t):
        if self.ad[a] == 0 or t <= 0: return 0
        x = self.ad[a] * t + Fr(self.F[a], self.S); c = floor(x)
        return max(0, c - 1 if x == c else c)
    def time(self, a, jj): return Fr(jj * self.S - self.F[a], self.ad[a] * self.S)
    def rank(self, a, jj):           # position (1-based) of event (axis a, crossing jj) in the merged (time, axis) order
        t = self.time(a, jj); r = 0
        for b in range(3):
            if not self.ad[b]: continue
            r += self.count_lt(b, t) + (self.count_le(b, t) - self.count_lt(b, t) if b <= a else 0)
        return r
    def voxel_at(self, k):
        """Voxel after exactly k steps ('face' policy), in O(log k) exact operations."""
        if k == 0: return tuple(self.start)
        n = [0, 0, 0]
        for a in range(3):
            if not self.ad[a]: continue
            lo, hi = 0, k                                   # largest jj with rank(a, jj) <= k
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if self.rank(a, mid) <= k: lo = mid
                else: hi = mid - 1
            n[a] = lo
        return tuple(self.start[a] + self.sgn[a] * n[a] for a in range(3))
    def traverse_chunk(self, k0, nsteps):
        """Exact traversal of steps k0..k0+nsteps, starting from the random-access state (for parallel chunks)."""
        if k0 == 0: return self.traverse(nsteps)
        v0 = self.voxel_at(k0)
        sub = Ray.__new__(Ray); sub.__dict__.update(self.__dict__)
        # crossings already used per axis
        used = [abs(v0[a] - self.start[a]) for a in range(3)]
        # rebuild a stepping state: next crossing indices = used + 1, then continue the DDA
        v = list(v0); j = [u + 1 for u in used]; out = [tuple(v)]
        while len(out) <= nsteps:
            act = [a for a in range(3) if self.ad[a]]
            tn = {a: (j[a] * self.S - self.F[a], self.ad[a]) for a in act}
            best = min(act, key=lambda a: Fr(tn[a][0], tn[a][1]))
            tied = [a for a in act if tn[a][0] * tn[best][1] == tn[best][0] * tn[a][1]]
            for a in tied:
                v[a] += self.sgn[a]; j[a] += 1; out.append(tuple(v))
                if len(out) > nsteps: break
        return out[: nsteps + 1]

def brute_events(ray, nsteps):
    """Independent reference: enumerate crossing events of each axis, sort by (time, axis), apply ('face')."""
    ev = []
    for a in range(3):
        if not ray.ad[a]: continue
        for jj in range(1, nsteps + 2): ev.append((ray.time(a, jj), a))
    ev.sort(); v = list(ray.start); out = [tuple(v)]
    for t, a in ev[:nsteps]: v[a] += ray.sgn[a]; out.append(tuple(v))
    return out

def amanatides_woo(o, d, nsteps, dtype=float):
    """Classic floating-point 3D DDA (Amanatides & Woo 1987), in the given float type."""
    import numpy as np
    f = np.float32 if dtype == "f32" else np.float64
    o = [f(x) for x in o]; d = [f(x) for x in d]
    v = [int(np.floor(o[a])) if d[a] >= 0 else int(np.ceil(o[a])) - 1 for a in range(3)]
    step = [1 if d[a] > 0 else -1 for a in range(3)]
    inf = f(np.inf)
    tdelta = [abs(f(1) / d[a]) if d[a] != 0 else inf for a in range(3)]
    tmax = []
    for a in range(3):
        if d[a] > 0: tmax.append((f(v[a] + 1) - o[a]) / d[a])
        elif d[a] < 0: tmax.append((f(v[a]) - o[a]) / d[a])
        else: tmax.append(inf)
    out = [tuple(v)]
    while len(out) <= nsteps:
        a = min(range(3), key=lambda b: (tmax[b], b))
        v[a] += step[a]; tmax[a] = f(tmax[a] + tdelta[a]); out.append(tuple(v))
    return out
