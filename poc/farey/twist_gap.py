"""Twist gaps on higher-complexity surfaces are sums of orthogeodesic terms.

Conjecture: for a simple closed geodesic gamma and any closed geodesic beta crossing it, cut beta at gamma into arcs
a_1..a_m (m = i(gamma, beta)) with orthogeodesic lengths d_j (gamma to gamma, in the arc's class). Then
    lim_k [ l(T^k beta) + l(T^-k beta) - 2 k m l_gamma ] = 4 sum_j log cosh(d_j/2).
(In the complexity-one cases this is the gap law: torus e^g = cosh^2(d/2); sphere e^g = prod of the two arcs'
cosh^2(d/2), i.e. P(x; A, B) = cosh^2(d/2) for the return orthogeodesic in a pair of pants.)

Test surface: a five-holed sphere, the orientation-preserving subgroup of the reflection group in five disjoint
geodesics of the disc (the double of a right-angled decagon). Boundary loops a_i = r_i r_{i+1}, a1 a2 a3 a4 a5 = 1.
gamma = a1 a2 = r1 r3 separates holes {1,2} from {3,4,5}; pi_1 = A *_<gamma> B, A = <a1, a2>, B = <a3, a4, gamma>.
The Dehn twist conjugates A-side pieces: x -> gamma^k x gamma^-k. A word beta = x1 y1 x2 y2 ... (x in A, y in B) has
2m arcs; arc of a piece z has orthogeodesic d(axis gamma, z axis gamma):
    cosh d = |tr(G H) - tr(G H^-1)| / (4 sinh^2(l_gamma/2)),  H = z G z^-1.
"""
import mpmath as mp
mp.mp.dps = 80


def refl(c):
    """reflection in the geodesic of the disc with Euclidean centre c (|c| > 1): z -> (c conj z - 1)/(conj z - conj c)"""
    return mp.matrix([[c, -1], [1, -mp.conj(c)]])


def rr(Mi, Mj):
    """orientation-preserving product r_i r_j as an SL(2, C) matrix"""
    M = Mi * mp.matrix([[mp.conj(Mj[0, 0]), mp.conj(Mj[0, 1])], [mp.conj(Mj[1, 0]), mp.conj(Mj[1, 1])]])
    return M / mp.sqrt(mp.det(M))


def length(M): return 2 * mp.acosh(abs(mp.re(M[0, 0] + M[1, 1])) / 2)
def inv(M): return mp.inverse(M)


def orthogeodesic(G, z):
    H = z * G * inv(z); lg = length(G)
    tr = lambda M: mp.re(M[0, 0] + M[1, 1])
    return mp.acosh(abs(tr(G * H) - tr(G * inv(H))) / (4 * mp.sinh(lg / 2)**2))


def surface(angles, halfwidths):
    """five disjoint geodesics: endpoints at angle t +- w on the unit circle; centre at distance 1/cos w"""
    R = [refl(mp.expjpi(t / mp.pi) / mp.cos(w)) for t, w in zip(angles, halfwidths)]
    return [rr(R[i], R[(i + 1) % 5]) for i in range(5)], R


def test(name, angles, widths, words):
    a, R = surface(angles, widths)
    a1, a2, a3, a4, a5 = a
    prod = a1 * a2 * a3 * a4 * a5; print(f"{name}: a1 a2 a3 a4 a5 = +-I residual {mp.nstr(min(mp.norm(prod - mp.eye(2)), mp.norm(prod + mp.eye(2))), 3)}; "
                                           f"boundary lengths {[mp.nstr(length(x), 5) for x in a]}")
    G = a1 * a2; lg = length(G); print(f"   gamma = a1 a2: length {mp.nstr(lg, 8)}")
    names = {"a1": a1, "a2": a2, "a3": a3, "a4": a4, "A1": inv(a1), "A2": inv(a2), "A3": inv(a3), "A4": inv(a4), "g": G, "G": inv(G)}
    def mat(word): 
        M = mp.eye(2)
        for s in word.split(): M = M * names[s]
        return M
    for xs, ys, label in words:
        X = [mat(x) for x in xs]; Y = [mat(y) for y in ys]
        pred = 0
        for z in X + Y: pred += 4 * mp.log(mp.cosh(orthogeodesic(G, z) / 2))   # each piece is one arc
        m = len(X) + len(Y)
        def twisted(k):
            Gk, Gmk = G**k if k >= 0 else inv(G)**(-k), inv(G)**k if k >= 0 else G**(-k)
            M = mp.eye(2)
            for x, y in zip(X, Y): M = M * (Gk * x * Gmk) * y
            return length(M)
        rows = []
        for k in (2, 5, 10, 20):
            gap = twisted(k) + twisted(-k) - 2 * k * m * lg; rows.append(f"k={k}: {mp.nstr(gap, 14)}")
        print(f"   beta = {label} ({m} arcs): " + ";  ".join(rows) + f";  orthogeodesic sum 4 sum log cosh(d/2) = {mp.nstr(pred, 14)}")


if __name__ == "__main__":
    words = [(["a2"], ["a3"], "a2 . a3  (around holes 2, 3; simple)"),
             (["a1"], ["a4"], "a1 . a4"),
             (["a2", "a1"], ["a3", "a4"], "a2 a3 a1 a4"),
             (["a1 a2 a2", "a2"], ["a3 A4", "a4 a3"], "(a1 a2^2)(a3 a4^-1)(a2)(a4 a3)"),
             (["a2 A1 a2"], ["a3 a4 a4 a3"], "(a2 a1^-1 a2)(a3 a4^2 a3)")]
    test("five-holed sphere S1", [0.0, 1.3, 2.5, 3.7, 5.0], [0.35, 0.25, 0.4, 0.3, 0.33], words)
    test("five-holed sphere S2", [0.2, 1.1, 2.9, 3.9, 5.2], [0.15, 0.45, 0.2, 0.5, 0.25], words)


def pants_check():
    """P(x; A, B) = cosh^2(d/2): x = l(gamma), pants (gamma; a1, a2), d the return orthogeodesic of gamma around hole 2
    (piece a2) -- equivalently around hole 1 (piece a1) is the same arc class in that pants."""
    for name, ang, wid in (("S1", [0.0, 1.3, 2.5, 3.7, 5.0], [0.35, 0.25, 0.4, 0.3, 0.33]), ("S2", [0.2, 1.1, 2.9, 3.9, 5.2], [0.15, 0.45, 0.2, 0.5, 0.25])):
        a, _ = surface(ang, wid); G = a[0] * a[1]; x = length(G); A, B = length(a[0]), length(a[1])
        h = mp.cosh(x / 2); P = (h + mp.cosh((A + B) / 2)) * (h + mp.cosh((A - B) / 2)) / mp.sinh(x / 2)**2
        for lab, z in (("a2", a[1]), ("a1", a[0])):
            d = orthogeodesic(G, z); print(f"{name}: P(x; L1, L2) = {mp.nstr(P, 20)};  cosh^2(d/2) for piece {lab} = {mp.nstr(mp.cosh(d / 2)**2, 20)}")


if __name__ == "__main__":
    pants_check()
