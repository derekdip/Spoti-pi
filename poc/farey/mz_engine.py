"""Fast Weil-Petersson intersection numbers via Mirzakhani-Zograf recursion (III) (arXiv 1112.1151, eqs. 2.2-2.4):
    [tau_{d1}...tau_{dn}]_{g,n} = A_d + B_d + C_d,   a_i = (1 - 2^{1-2i}) zeta(2i)  (a_0 = 1/2),
V_{g,n}(2L) = sum_d [tau_d]_{g,n} prod L_i^{2 d_i}/(2 d_i + 1)!.  Base: [tau_0^3]_{0,3} = 1, [tau_0]_{1,1} = pi^2/12, [tau_1]_{1,1} = 1/2.
Per-pair cusped corner average:  a_g = sum_k [tau_k]_{g,1} 16 (2k+2) (1 - 2^{-2k-4}) zeta(2k+4) / [tau_0^2]_{g,2}.
Conjecture: a_g -> 2.
"""
import sys, functools, itertools, time
import mpmath as mp
mp.mp.dps = 40
sys.setrecursionlimit(100000)


@functools.lru_cache(None)
def a(i):
    if i == 0: return mp.mpf(1) / 2
    return (1 - mp.mpf(2)**(1 - 2 * i)) * mp.zeta(2 * i)


def stable(g, n): return 2 * g - 2 + n > 0 and not (g == 0 and n < 3)


@functools.lru_cache(None)
def T(g, d):
    """[tau_d]_{g,n} for a sorted tuple d (symmetric in its entries)."""
    n = len(d)
    if not stable(g, n) or any(x < 0 for x in d): return mp.mpf(0)
    d0 = 3 * g - 3 + n - sum(d)
    if d0 < 0: return mp.mpf(0)
    if (g, n) == (0, 3): return mp.mpf(1) if d == (0, 0, 0) else mp.mpf(0)
    if (g, n) == (1, 1): return mp.pi**2 / 12 if d == (0,) else (mp.mpf(1) / 2 if d == (1,) else mp.mpf(0))
    # distinguished index: the largest (any choice is valid by symmetry)
    d1 = d[-1]; rest = d[:-1]
    tot = mp.mpf(0)
    # A: j over the other indices
    for jj, dj in enumerate(rest):
        others = rest[:jj] + rest[jj + 1:]
        for l in range(0, d0 + 1):
            idx = d1 + dj + l - 1
            if idx < 0: continue
            tot += 8 * (2 * dj + 1) * a(l) * T(g, tuple(sorted(others + (idx,))))
    # B: genus reduction
    if g >= 1:
        for l in range(0, d0 + 1):
            s = l + d1 - 2
            if s < 0: continue
            for k1 in range(0, s + 1):
                tot += 16 * a(l) * T(g - 1, tuple(sorted(rest + (k1, s - k1))))
    # C: splittings of the other indices (as positions, so multiplicities are counted correctly)
    m = len(rest)
    for mask in range(1 << m):
        I = tuple(rest[i] for i in range(m) if mask >> i & 1); J = tuple(rest[i] for i in range(m) if not mask >> i & 1)
        for g1 in range(0, g + 1):
            g2 = g - g1
            if not (stable(g1, len(I) + 1) and stable(g2, len(J) + 1)): continue
            for l in range(0, d0 + 1):
                s = l + d1 - 2
                if s < 0: continue
                for k1 in range(0, s + 1):
                    x = T(g1, tuple(sorted(I + (k1,))))
                    if x == 0: continue
                    tot += 16 * a(l) * x * T(g2, tuple(sorted(J + (s - k1,))))
    return tot


def per_pair(g):
    num = mp.mpf(0)
    for k in range(0, 3 * g - 1):
        num += T(g, (k,)) * 16 * (2 * k + 2) * (1 - mp.mpf(2)**(-2 * k - 4)) * mp.zeta(2 * k + 4)
    return num / T(g, (0, 0))


if __name__ == "__main__":
    # validation: known cusped volumes and our exact per-pair values
    print("V_{0,5}(0) =", mp.nstr(T(0, (0,) * 5) / mp.pi**4, 12), "pi^4 (10);  V_{1,2}(0) =", mp.nstr(T(1, (0, 0)) / mp.pi**4, 12), "pi^4 (1/4);  V_{2,2}(0) =", mp.nstr(T(2, (0, 0)) / mp.pi**10, 12), "pi^10 (787/480 =", mp.nstr(mp.mpf(787) / 480, 12), ")")
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    for g in range(1, G + 1):
        t0 = time.time(); ag = per_pair(g)
        print(f"g = {g:>2}: a_g = {mp.nstr(ag, 15)}  (= {mp.nstr(ag / mp.pi**2, 10)} pi^2);  a_g - 2 = {mp.nstr(ag - 2, 8)};  sqrt(g) (a_g - 2) = {mp.nstr(mp.sqrt(g) * (ag - 2), 8)}   [{time.time() - t0:.1f} s, cache {T.cache_info().currsize}]", flush=True)
