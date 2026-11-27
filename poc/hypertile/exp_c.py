"""(c) Cracks. Float BFS in screen coordinates (projective 2-vectors already transformed by the camera), crossing
edges by reflection, as a renderer would. Each tile also carries its exact integer Farey label, so every float copy
of the same vertex can be grouped. Crack = max spread between copies of one vertex (px at R_PIX); drift = max distance
of a copy from the exact screen position. Exact Farey rendering has crack 0 by construction (one vertex, one value)."""
import math, sys
import numpy as np
from collections import deque
from hypertile import covering_arc
R_PIX = 2000.0
CAP = 120000
import warnings; warnings.filterwarnings('ignore')
def ireflect(P, Q, R):        # exact integer reflection fixing P, negating Q (det(P,Q) = +-1)
    det = P[0]*Q[1] - P[1]*Q[0]; al = (R[0]*Q[1] - R[1]*Q[0]) * det; be = (P[0]*R[1] - P[1]*R[0]) * det
    return (al*P[0] - be*Q[0], al*P[1] - be*Q[1])
def screen(V):                # projective vector (in camera frame) -> unit-circle point, Cayley map
    x0, x1 = complex(V[0]), complex(V[1]); return (x0 - 1j*x1) / (x0 + 1j*x1)
def run(eps, dt, cam):
    a, b, c, d = cam; ci = (d, -b, -c, a)                  # camera^-1 maps world vectors to camera frame
    def tocam(v, t): return (t(ci[0]*v[0] + ci[1]*v[1]), t(ci[2]*v[0] + ci[3]*v[1]))
    t = dt
    def frefl(P, Q, R):
        det = P[0]*Q[1] - P[1]*Q[0]; al = (R[0]*Q[1] - R[1]*Q[0]) / det; be = (P[0]*R[1] - P[1]*R[0]) / det
        return (al*P[0] - be*Q[0], al*P[1] - be*Q[1])
    def norm(V):              # keep float vectors O(1) (a renderer would)
        n = t(math.hypot(float(V[0]), float(V[1]))); return (V[0]/n, V[1]/n)
    ex0 = ((0, 1), (1, 1), (1, 0)); fl0 = tuple(norm(tocam(v, t)) for v in ex0)
    copies = {}; seen = {frozenset(ex0)}; q = deque([(ex0, fl0)])
    bad = 0
    while q and len(seen) < CAP:
        ex, fl = q.popleft()
        for v, w in zip(ex, fl): copies.setdefault(v, []).append(screen(w))
        for i in range(3):
            j, k = (i + 1) % 3, (i + 2) % 3
            ne = (ex[j], ex[k], ireflect(ex[j], ex[k], ex[i]))
            if frozenset(ne) in seen: continue
            nf = (fl[j], fl[k], norm(frefl(fl[j], fl[k], fl[i])))
            ang = [math.atan2(s.imag, s.real) % (2*math.pi) for s in map(screen, nf)]
            if any(a != a for a in ang): bad += 1; continue
            if covering_arc(ang) < eps: continue
            seen.add(frozenset(ne)); q.append((ne, nf))
    crack = drift = 0.0
    for v, ws in copies.items():
        wt = screen(tocam(v, float))
        crack = max(crack, max(abs(w - u) for w in ws for u in ws)); drift = max(drift, max(abs(w - wt) for w in ws))
    return len(seen), crack * R_PIX, drift * R_PIX, bad
th = 0.7; e = math.exp(1.3)       # an off-centre, rotated camera inside the fundamental region
R = (math.cos(th), math.sin(th), -math.sin(th), math.cos(th)); A = (math.sqrt(e), 0.0, 0.0, 1/math.sqrt(e))
cam = (R[0]*A[0], R[1]*A[3], R[2]*A[0], R[3]*A[3])
for name, dt in (("float64", np.float64), ("float32", np.float32)):
    for eps in (2e-2, 5e-3, 2e-3, 1e-3):
        n, cr, dr, bad = run(eps, dt, cam)
        print("%s eps %.0e: %6d tiles (cap %d, NaN vertices %d)" % (name, eps, n, CAP, bad), end=''); print("   max crack between shared-vertex copies %9.2e px  max drift from exact %9.2e px""" % (cr, dr), flush=True)
