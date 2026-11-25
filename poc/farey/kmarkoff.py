"""Gyoda-Matsushita k-Markoff equations  x^2 + y^2 + z^2 + k1 yz + k2 zx + k3 xy = S xyz,  S = 3 + k1 + k2 + k3.

Substitution tau_x = S x - k1, tau_y = S y - k2, tau_z = S z - k3 turns the equation into the Fricke cubic of a four-holed
sphere with boundary traces (k2, k3, k1, 2):
    tau_x^2 + tau_y^2 + tau_z^2 - tau_x tau_y tau_z + (2k1 + k2k3) tau_x + (2k2 + k1k3) tau_y + (2k3 + k1k2) tau_z
        + k1^2 + k2^2 + k3^2 + 2 k1k2k3 = 0.
(One cusp; a boundary of trace k: k = 0, 1 are cone points of order 2, 3; k = 2 a cusp; k >= 3 a geodesic boundary.)
The integer Vieta moves z -> S xy - k1 y - k2 x - z are the sphere's mediant rule, and the variable of a node is the
parity class of its slope. Checked on integer solution trees: the substitution, the gap law (sphere form = conic
invariant) against brute-force integer fans, the vector Hines identity, and the extended dual-area identity.
"""
import sys, itertools
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import general, dual_area
mp.mp.dps = 80
F = lambda t: mp.acosh(mp.mpf(t) / 2)


def small_root(k1, k2, k3):
    S = 3 + k1 + k2 + k3; best = None
    for x, y, z in itertools.product(range(1, 40), repeat=3):
        if x * x + y * y + z * z + k1 * y * z + k2 * z * x + k3 * x * y == S * x * y * z and (best is None or x + y + z < sum(best)): best = (x, y, z)
    return best


def run(k1, k2, k3):
    S = 3 + k1 + k2 + k3; r = small_root(k1, k2, k3)
    if r is None: print(f"k = ({k1},{k2},{k3}): no small positive solution"); return
    # climb to a root whose cone (x-node, y-node) grows: replace the largest coordinate by the larger Vieta root while needed
    x, y, z = r
    tau = lambda v, k: S * v - k
    tx, ty, tz = tau(x, k1), tau(y, k2), tau(z, k3)
    C, s = general.sphere_C(*map(mp.mpf, (k2, k3, k1, 2)))
    resid = tx * tx + ty * ty + tz * tz - tx * ty * tz + C[0] * tx + C[1] * ty + C[2] * tz + s
    # e0 = x (class (1,0), kappa p = 2k1 + k2k3), e1 = y (class (0,1)), e0 - e1 = z (class (1,1)): the root (X, Y) = (tau_x, tau_y)
    # needs the opposite z to be the smaller root; general.run solves it itself
    print(f"k = ({k1},{k2},{k3}), S = {S}: smallest solution {r}; tau = ({tx}, {ty}, {tz}); Fricke residual {resid}; "
          f"(p, q, r, s) = ({mp.nstr(C[0], 4)}, {mp.nstr(C[1], 4)}, {mp.nstr(C[2], 4)}, {mp.nstr(s, 4)})")
    # brute-force gap at the x-node from the raw integer fan (alternate y and z flips with x fixed), in tau units
    yy, zz = y, z; fwd = [tau(yy, k2), tau(zz, k3)]
    a, b = yy, zz
    for j in range(80):   # forward: y' = S x z - k1 z - k3 x - y, then z' = S x y' - k1 y' - k2 x - z
        if j % 2 == 0: a = S * x * b - k1 * b - k3 * x - a; fwd.append(tau(a, k2))
        else: b = S * x * a - k1 * a - k2 * x - b; fwd.append(tau(b, k3))
    a, b = yy, zz; bwd = [tau(zz, k3), tau(yy, k2)]
    for j in range(80):
        if j % 2 == 0: b = S * x * a - k1 * a - k2 * x - b; bwd.append(tau(b, k3))
        else: a = S * x * b - k1 * b - k3 * x - a; bwd.append(tau(a, k2))
    c = mp.mpf(tx); lam = c / 2 + mp.sqrt(c * c / 4 - 1)
    brute = mp.log(fwd[-1]) + mp.log(bwd[-1]) - (len(fwd) - 1 + len(bwd) - 1 - 1) * mp.log(lam)
    # sphere gap law at the x-node: own class (1,0), neighbours (0,1), (1,1)
    km, kx, ky = C[0], C[1], C[2]
    gl = mp.log((c * c + km * c + s) / (c * c - 4) + (kx * kx + ky * ky + kx * ky * c) / (c * c - 4)**2)
    M3 = mp.matrix([[1, -c / 2, kx / 2], [-c / 2, 1, ky / 2], [kx / 2, ky / 2, c * c + km * c + s]])
    print(f"   gap at the x-node (tau = {tx}): brute-force integer fan {mp.nstr(brute, 15)}, sphere law {mp.nstr(gl, 15)}, conic invariant {mp.nstr(mp.log(-4 * mp.det(M3) / (c * c - 4)**2), 15)}; diff {mp.nstr(abs(brute - gl), 3)}")
    if min(tx, ty) > 2 and tx * ty - C[2] - tz > max(tx, ty):
        print("   vector Hines on the cone (x-node, y-node):", end=" "); sys.stdout.flush()
        general.run("", C, s, mp.mpf(tx), mp.mpf(ty), 2500)
        dual_area.run("   dual-area identity", C, s, mp.mpf(tx), mp.mpf(ty))
    else:
        print("   root cone not growing / trace <= 2 at the root; identities skipped")


if __name__ == "__main__":
    for k in ((0, 0, 0), (1, 1, 1), (2, 2, 2), (1, 2, 3), (0, 0, 5), (3, 3, 3), (0, 1, 4)):
        run(*k)
