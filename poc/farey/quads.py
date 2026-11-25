"""Markoff-Hurwitz quads a^2 + b^2 + c^2 + d^2 = abcd: each region (one coordinate held fixed) is a
generalised Markoff tree. With a fixed and X = a b, Y = a c, Z = a d:
    X^2 + Y^2 + Z^2 - XYZ = a^2 (b^2 + c^2 + d^2 - a bcd) = -a^4,
and the quad move d -> abc - d is the Markoff move Z -> XY - Z. So the region of a is the one-holed-torus tree
with mu = -a^4, and generalise.py's properties hold in it. Checked here on the integer quads from (2, 2, 2, 6).
"""
import itertools, sys
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0]); import generalise as G
mp.mp.dps = 120


def region_values(quad, slot, depth):
    """Vieta moves on the three other slots, breadth first to `depth`: the region's vertices, as rescaled triples."""
    a = quad[slot]; seen = {tuple(quad)}; frontier = [tuple(quad)]; out = []
    for _ in range(depth):
        nxt = []
        for q in frontier:
            out.append(tuple(sorted(a * q[i] for i in range(4) if i != slot)))
            for i in range(4):
                if i == slot: continue
                p = list(q); p[i] = mp.mpf(1) * q[0] * q[1] * q[2] * q[3] / q[i] - q[i]
                if tuple(p) not in seen: seen.add(tuple(p)); nxt.append(tuple(p))
        frontier = nxt
    return a, out


q0 = (mp.mpf(2), mp.mpf(2), mp.mpf(2), mp.mpf(6))
print("root quad", [int(x) for x in q0], "on the surface:", q0[0]**2 + q0[1]**2 + q0[2]**2 + q0[3]**2 == q0[0] * q0[1] * q0[2] * q0[3])
# 1. every region vertex satisfies the rescaled generalised Markoff equation with mu = -a^4
for slot, quad in ((0, q0), (3, q0), (0, (mp.mpf(22), mp.mpf(2), mp.mpf(2), mp.mpf(6)))):
    if quad[0]**2 + quad[1]**2 + quad[2]**2 + quad[3]**2 != quad[0] * quad[1] * quad[2] * quad[3]: print("not a quad", quad); continue
    a, trip = region_values(quad, slot, 6); mu = -a**4
    err = max(abs(X * X + Y * Y + Z * Z - X * Y * Z - mu) / (X * Y * Z) for X, Y, Z in trip)
    print(f"region of slot {slot} = {int(a)} from {[int(x) for x in quad]}: {len(trip)} vertices, all on X^2+Y^2+Z^2-XYZ = {int(mu)}: {'PASS' if err < 1e-90 else 'FAIL'}")
# 2. the a = 2 region is generalise.py's mu = -16 tree from (4, 4): its first child is 12 = 2 x 6
mu = mp.mpf(-16); print("forward child of (4, 4) at mu = -16:", mp.nstr((16 + mp.sqrt(256 - 4 * (32 - mu))) / 2, 6), "(2 x 6 = 12)")
r = G.run(mu)
print(f"mu = -16 (region a = 2): P1 {'PASS' if r['P1'] else 'FAIL'}, P2 {'PASS' if r['P2'] else 'FAIL'}, P3 {'PASS' if r['P3'] else 'FAIL'}, gap error {mp.nstr(r['gap_err'], 3)}, D/Phi deep {mp.nstr(r['ratio_min'], 10)} (2(4-mu)/(2-mu) = {mp.nstr(2 * (4 - mu) / (2 - mu), 10)})")
