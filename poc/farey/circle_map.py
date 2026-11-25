"""Farey-ordered, best-first mapping of mode-locking in the sine circle map (a driven oscillator model):
    theta -> theta + Omega - (K / 2 pi) sin(2 pi theta).
For each rational p/q the rotation number locks at p/q on an interval of Omega (an Arnold tongue). Its edges are
where max over theta (lower edge) and min over theta (upper edge) of g(theta) = f^q(theta) - theta - p cross zero.

Prediction (before the run): for K < 1 the widths fall like exp(-q lambda(p/q)), so -log w is an approximately
homogeneous 'norm' on (q - p, p); best-first refinement in Farey order (by width) then leaves an unresolved locked
measure E_N = exp(-c sqrt(N)) with c = pi / sqrt(6 A), A = (1/2) int f^-2 over the slice, f(t) = -log w(t)/q
(the rate law with kappa = 1). At K = 1 the widths fall like a power of q and the convergence is a power of N.

Cost: a tongue's two edges are found by bisection in Omega on the extremum of g over theta; map evaluations are
counted, and compared with a uniform sweep of Omega that iterates the map at every grid point.

  python3 poc/farey/circle_map.py
"""
import heapq, math, sys
import numpy as np

EVALS = [0]


def g_ext(theta, Om, K, p, q, which):
    """max (which=+1) or min (which=-1) over theta of f^q(theta) - theta - p, refined around the best grid point."""
    th = theta.copy()
    for _ in range(q): th = th + Om - K / (2 * np.pi) * np.sin(2 * np.pi * th)
    EVALS[0] += q * len(theta); g = which * (th - theta - p); i = int(np.argmax(g)); h = theta[1] - theta[0]
    a, b = theta[i] - h, theta[i] + h; gr = (math.sqrt(5) - 1) / 2
    def G(t):
        x = t
        for _ in range(q): x = x + Om - K / (2 * math.pi) * math.sin(2 * math.pi * x)
        EVALS[0] += q; return which * (x - t - p)
    c, d = b - gr * (b - a), a + gr * (b - a); gc, gd = G(c), G(d)
    for _ in range(40):
        if gc > gd: b, d, gd = d, c, gc; c = b - gr * (b - a); gc = G(c)
        else: a, c, gc = c, d, gd; d = a + gr * (b - a); gd = G(d)
    return which * max(gc, gd)


def tongue(p, q, K, lo0=None, hi0=None):
    """Edges of the p/q tongue, searched in (lo0, hi0): between the tongues of its Farey parents (tongues are
    ordered like their rotation numbers)."""
    theta = np.linspace(0, 1, 48 * q, endpoint=False)
    def edge(which):   # which = +1: lower edge (max g = 0); -1: upper edge (min g = 0); g increases with Omega
        lo, hi = (p / q - 0.6 / q**2, p / q + 0.6 / q**2) if lo0 is None else (lo0, hi0)
        for _ in range(60):
            mid = (lo + hi) / 2
            if g_ext(theta, mid, K, p, q, which) < 0: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    return edge(+1), edge(-1)


def farey(Q):
    out = [(0, 1), (1, 2)]; a, b, c, d = 0, 1, 1, Q
    seq = []
    while c <= Q:   # Farey sequence of order Q on [0, 1]
        k = (Q + b) // d; a, b, c, d = c, d, k * c - a, k * d - b; seq.append((a, b))
    return [(0, 1)] + seq


def run(K, Q, Qfit):
    EVALS[0] = 0; fr = [(p, q) for p, q in farey(Q) if 2 * p <= q]          # [0, 1/2] by the map's symmetry
    W = {}; E = {}
    def parents(m):
        L, R = (0, 1), (1, 1)
        while True:
            md = (L[0] + R[0], L[1] + R[1])
            if md == m: return L, R
            if m[0] * md[1] < md[0] * m[1]: R = md
            else: L = md
    E[(0, 1)] = tongue(0, 1, K); E[(1, 1)] = (1 + E[(0, 1)][0], 1 + E[(0, 1)][1])
    for p, q in sorted(fr, key=lambda m: m[1]):
        if (p, q) == (0, 1): continue
        L, R = parents((p, q)); E[(p, q)] = tongue(p, q, K, E[L][1], E[R][0])
    for m in fr: W[m] = max(E[m][1] - E[m][0], 0.0)
    cost_tongues = EVALS[0]
    # heap property on the Farey tree of [0, 1/2], and best-first order by width
    viol = 0; cells = [((0, 1), (1, 2))]; order = [(0, 1), (1, 2)]; h = []
    def push(L, R):
        m = (L[0] + R[0], L[1] + R[1])
        if m[1] <= Q: heapq.heappush(h, (-W[m], m, L, R))
    push((0, 1), (1, 2))
    while h:
        nw, m, L, R = heapq.heappop(h); order.append(m)
        for (a, b) in ((L, m), (m, R)):
            c = (a[0] + b[0], a[1] + b[1])
            if c[1] <= Q:
                viol += W[c] > W[m]; push(a, b)
    total = sum(W.values()); rem = total - np.cumsum([W[m] for m in order])
    # fit log E_N on sqrt N over the range where the frontier is still inside q <= Qfit
    qs = np.array([m[1] for m in order]); Nmax = int(np.argmax(qs > Qfit)) if (qs > Qfit).any() else len(order)
    N = np.arange(1, len(order) + 1); sel = (N > 8) & (N < Nmax) & (rem > 0)
    c_fit = -np.polyfit(np.sqrt(N[sel]), np.log(rem[sel]), 1)[0]
    pw = -np.polyfit(np.log(N[sel]), np.log(rem[sel]), 1)[0]
    # the 'norm' -log w(p/q) on the slice t = p/q: f(t) = -log w / q; area A = (1/2) int f^-2 dt over [0, 1], by symmetry 2x [0, 1/2]
    ts = sorted((p / q, -math.log(W[(p, q)]) / q) for p, q in fr if W[(p, q)] > 0 and q <= Qfit)
    A = 2 * 0.5 * sum((t1 - t0) / (f0 * f1) for (t0, f0), (t1, f1) in zip(ts, ts[1:]))
    return dict(W=W, viol=viol, c_fit=c_fit, pw=pw, A=A, c_pred=math.pi / math.sqrt(6 * A), n_tongues=len(fr), cost=cost_tongues, Nmax=Nmax, total=total)


def uniform_cost(K, w_min, T=2000):
    """Map evaluations for a uniform Omega sweep fine enough to hit every tongue of width >= w_min (two points per
    width), each point iterated T times to read its rotation number: (1/2 / (w_min/2)) T."""
    return int(0.5 / (w_min / 2)) * T


if __name__ == "__main__":
    for K, Q, Qfit in ((0.5, 22, 18), (0.8, 24, 20), (0.95, 26, 22), (1.0, 26, 22)):
        r = run(K, Q, Qfit); Wsorted = sorted(r["W"].values(), reverse=True)
        print(f"K = {K}: {r['n_tongues']} tongues with q <= {Q} in [0, 1/2], locked measure found {r['total']:.6f} (x2 for [0,1]); heap violations {r['viol']}")
        print(f"   best-first remainder: fit exp(-c sqrt N) c = {r['c_fit']:.3f}, predicted pi/sqrt(6A) = {r['c_pred']:.3f}; power-law fit N^-{r['pw']:.2f}")
        for w_min in (1e-4, 1e-6):
            k = sum(1 for w in Wsorted if w >= w_min)
            print(f"   tongues of width >= {w_min:g}: {k}; Farey best-first cost (all {r['n_tongues']} tongues computed) {r['cost']:.2e} map evaluations; uniform sweep needs {uniform_cost(K, w_min):.2e}")
