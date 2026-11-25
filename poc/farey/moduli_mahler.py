"""Extremal properties over the moduli space of cusped tori (Markoff triples a^2 + b^2 + c^2 = abc, a, b, c > 2):
Area(B) of the stable-norm ball, the dual area A* = Area(B*) = sum g N, and the Mahler volume Area(B) Area(B*)
(affine invariant; 8 <= . <= pi^2 for symmetric planar bodies). All three are invariant under change of homology basis.
Fundamental domain: 2 < a <= b <= c, c the smaller Vieta root (so ab - c >= c).
"""
import sys
import numpy as np, mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import dual_closed as D
mp.mp.dps = 40


def invariants(a, b, tol=mp.mpf(10)**-30):
    a, b = mp.mpf(a), mp.mpf(b); disc = (a * b)**2 - 4 * (a * a + b * b)
    if disc < -mp.mpf(10)**-30: return None
    c = (a * b - mp.sqrt(max(disc, 0))) / 2
    if c < b - mp.mpf(10)**-30: return None
    cv = D.all_curves((0, 0, 0), 0, a, b, tol)   # root (X, Y) = (a, b), opposite e0 - e1 = c
    As = sum(mp.log(t * t / (t * t - 4)) * D.F(t) for t in cv.values()); AB = D.ball_area(cv)
    return float(c), float(AB), float(As), float(AB * As)


if __name__ == "__main__":
    rows = []
    for a in np.linspace(2.02, 3.0, 36):
        lo = max(a, 2 * a / np.sqrt(a * a - 4)); hi = a / np.sqrt(a - 2)
        if lo > hi: continue
        for b in np.linspace(lo, hi, 14):
            r = invariants(a, b)
            if r: rows.append((a, b) + r)
    rows = np.array(rows); print(f"{len(rows)} points of the fundamental domain 2 < a <= 3, max(a, 2a/sqrt(a^2-4)) <= b <= a/sqrt(a-2)")
    for j, nm in ((3, "Area(B)"), (4, "Area(B*)"), (5, "Mahler volume")):
        i_lo, i_hi = np.argmin(rows[:, j]), np.argmax(rows[:, j])
        print(f"  {nm:<14} min {rows[i_lo, j]:.6f} at (a, b, c) = ({rows[i_lo, 0]:.3f}, {rows[i_lo, 1]:.3f}, {rows[i_lo, 2]:.3f});  "
              f"max {rows[i_hi, j]:.6f} at ({rows[i_hi, 0]:.3f}, {rows[i_hi, 1]:.3f}, {rows[i_hi, 2]:.3f})")
    for name, (a, b) in (("modular (3, 3, 3)", (3, 3)), ("square (2.828, 2.828, 4)", (2 * mp.sqrt(2), 2 * mp.sqrt(2)))):
        c, AB, As, M = invariants(a, b); print(f"  {name}: Area(B) = {AB:.6f}, Area(B*) = {As:.6f}, Mahler = {M:.6f} = {M / np.pi**2:.5f} pi^2")
    print("  degenerating: a -> 2 (a short geodesic), b at the middle of its range")
    for a in (2.3, 2.1, 2.03, 2.01, 2.003):
        lo = max(a, 2 * a / np.sqrt(a * a - 4)); hi = a / np.sqrt(a - 2); r = invariants(a, (lo + hi) / 2, mp.mpf(10)**-25)
        print(f"    a = {a}: c = {r[0]:.3f}  Area(B) = {r[1]:.4f}  Area(B*) = {r[2]:.4f}  Mahler = {r[3]:.5f}")
    # Mahler and A* along curves through the modular point inside the domain (the domain near (3,3,3) is the corner b = a, a <= 3)
    print("  along the edge b = a towards the square torus, and along the edge b = a/sqrt(a-2):")
    for a in (3.0, 2.98, 2.95, 2.9, 2.85, 2 * np.sqrt(2)):
        r = invariants(a, a); print(f"    b = a = {a:.4f}: c = {r[0]:.4f}  Area(B) = {r[1]:.6f}  Area(B*) = {r[2]:.6f}  Mahler = {r[3]:.6f}")
    for a in (3.0, 2.98, 2.95, 2.9, 2.8, 2.6):
        r = invariants(a, a / np.sqrt(a - 2)); print(f"    b = a/sqrt(a-2), a = {a:.3f}: (b, c) = ({a / np.sqrt(a - 2):.4f}, {r[0]:.4f})  Area(B) = {r[1]:.6f}  Area(B*) = {r[2]:.6f}  Mahler = {r[3]:.6f}")
