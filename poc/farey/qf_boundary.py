"""True Bowditch boundary along rays of the slice (tr e0 = 3, mu = 0): the first point where some simple curve's trace
reaches the segment [-2, 2] (a curve turns parabolic / elliptic), found by bisection on
    dist(s) = min over curves with |t| < 60 of dist(t, [-2, 2]),
then A* and the continued Mahler function on the approach. Curves enumerated breadth-first while |t| < 60 (deeper ones
cannot reach [-2, 2] on rising trees).
"""
import sys, cmath, math
sys.path.insert(0, __file__.rsplit("/", 1)[0]); import complex_limits as CL


def seg_dist(t): return abs(t.imag) if -2 <= t.real <= 2 else min(abs(t - 2), abs(t + 2))


def nearest(b, depth=22, cut=60):
    disc = cmath.sqrt((3 * b)**2 - 4 * (9 + b * b)); c = min(((3 * b - disc) / 2, (3 * b + disc) / 2), key=abs)
    tr = {(1, 0): 3 + 0j, (0, 1): b, (0, -1): b, (1, -1): c, (1, 1): 3 * b - c}
    for (e0, e1, opp) in (((1, 0), (0, 1), (1, -1)), ((1, 0), (0, -1), (1, 1))):
        lvl = [(e0, e1, opp)]
        for _ in range(depth):
            nxt = []
            for (L, R, o) in lvl:
                m = (L[0] + R[0], L[1] + R[1]); tr[m] = tr[L] * tr[R] - tr[o]
                if abs(tr[m]) < cut: nxt += [(L, m, R), (m, R, L)]
            lvl = nxt
    return min(((seg_dist(t), v, t) for v, t in tr.items() if v != (0, -1)), key=lambda x: x[0])


if __name__ == "__main__" and len(sys.argv) == 1:
    for th in (90, 120, 150, 175):
        u = cmath.exp(1j * math.radians(th)); prev = 0.0; hit = None
        for k in range(1, 401):                       # coarse scan for the first sign of a trace on [-2, 2]
            s = 0.01 * k; d, v, t = nearest(3 + s * u)
            if d < 1e-9 or (abs(t.imag) < 1e-12 and -2 <= t.real <= 2): hit = s; break
            # a trace crosses the segment between steps: imaginary part changes sign while the real part is inside
            dp, vp, tp = nearest(3 + prev * u) if prev else (None, None, None)
            if prev and vp == v and tp.imag * t.imag < 0 and -2 < (tp.real + t.real) / 2 < 2: hit = s; break
            prev = s
        lo, hi = hit - 0.01, hit
        for _ in range(40):
            mid = (lo + hi) / 2; d, v, t = nearest(3 + mid * u); dl = nearest(3 + lo * u)
            crossed = (dl[1] == v and dl[2].imag * t.imag <= 0 and -2 <= t.real <= 2) or d < 1e-12
            if crossed: hi = mid
            else: lo = mid
        d, v, t = nearest(3 + hi * u)
        print(f"ray {th} deg: true boundary at distance {hi:.6f} (b = {3 + hi * u:.5f}); curve {v} reaches [-2, 2] with trace {t.real:+.5f}{t.imag:+.5f}i")
        for f in (0.9, 0.99, 0.999):
            def path(s_, f=f): return 3.0 + 0j, 3 + s_ * f * hi * u, 0j
            AB, As, M, n, gs, Ns = CL.continued_invariants(path, steps=80)
            print(f"   {f} of the way: {n:>7} curves; A* = {As.real:+.5f}{As.imag:+.5f}i;  M = {M.real:+.5f}{M.imag:+.5f}i;  "
                  f"N of {v} = {Ns.get(v, Ns.get((v[0], -v[1]), 0j)):.4f}")


def cusp_approach():
    """Straight approach from b = 3 to cusp points of the slice boundary: A* -> 0 and M -> 8 (complex pinching)?"""
    for name, bstar, v in (("b* = 3 + 2i (e0 - e1 parabolic)", 3 + 2j, (1, -1)), ("b* = 2 (e1 parabolic; real pinching)", 2 + 0j, (0, 1))):
        print(f"approach to {name}:")
        for f in (0.9, 0.97, 0.99, 0.995, 0.998):
            def path(s_, f=f): return 3.0 + 0j, 3 + s_ * f * (bstar - 3), 0j
            try:
                AB, As, M, n, gs, Ns = CL.continued_invariants(path, steps=80)
                Nv = Ns.get(v, Ns.get((v[0], -v[1]), 0j))
                print(f"   {f}: {n:>7} curves; N({v}) = {Nv:.4f};  A* = {As.real:+.5f}{As.imag:+.5f}i;  M = {M.real:+.5f}{M.imag:+.5f}i;  "
                      f"(M - 8) log(1/|N|) = {abs(M - 8) * math.log(1 / abs(Nv)):.3f}")
            except Exception as e:
                print(f"   {f}: failed ({type(e).__name__})")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "cusps":
    cusp_approach()
