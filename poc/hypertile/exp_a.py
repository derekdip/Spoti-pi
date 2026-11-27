"""(a) enumeration speed and equality; (c) crack width of the float BFS."""
import time, math
from fractions import Fraction
from hypertile import farey_tiles, float_bfs_tiles, boundary_angle, vec_angle, covering_arc
R_PIX = 2000.0
for eps in (2e-2, 5e-3, 2e-3, 1e-3):
    t0 = time.time(); ft = farey_tiles(eps); tf = time.time() - t0
    t0 = time.time(); bt = float_bfs_tiles(eps); tb = time.time() - t0
    # identify BFS tiles with exact ones: recover each float vertex as the nearest Farey vertex present in the exact set
    exact_keys = {tuple(sorted(round(boundary_angle(*v), 9) for v in t)) for t in ft}
    bfs_keys = {tuple(sorted(round(vec_angle(v), 9) for v in t)) for t in bt}
    # vertex accuracy of the float BFS: compare each float vertex with the nearest exact vertex angle
    exact_angles = sorted({boundary_angle(*v) for t in ft for v in t})
    import bisect
    def nearest(a):
        i = bisect.bisect_left(exact_angles, a); c = [exact_angles[j] for j in (i - 1, i) if 0 <= j < len(exact_angles)]
        return min(abs(a - x) for x in c)
    verr = max(nearest(vec_angle(v)) for t in bt for v in t)
    print("eps %.0e: exact Farey %6d tiles in %6.3f s (%.2f us/tile) | float BFS %6d tiles in %6.3f s (%.2f us/tile) | speedup %.1fx | same tile set: %s | max BFS vertex error %.1e rad = %.2e px" % (
        eps, len(ft), tf, 1e6 * tf / len(ft), len(bt), tb, 1e6 * tb / len(bt), tb / tf, exact_keys == bfs_keys, verr, verr * R_PIX))
