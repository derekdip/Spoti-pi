"""(b) Long camera walks. Camera g in SL2(R) acting on the upper half-plane; a boundary point x is drawn at
C(g^-1 x) on the disk (C = Cayley map), at R_PIX pixels radius.
  float : g <- g @ delta in float64, draw with g^-1 applied to x = p/q.
  exact : g = gamma h, gamma in SL2(Z) as Python ints, h float64 kept near the fundamental domain by exact integer
          moves after every step; draw gamma^-1 x exactly (rational), then apply h^-1 in float.
Truth: the same delta sequence multiplied in mpmath at 300 digits. Errors over the vertices of all visible tiles."""
import math, random, sys
import mpmath as mp
from hypertile import farey_tiles, covering_arc
mp.mp.dps = 300
import os; RENORM = os.environ.get('RENORM') == '1'
R_PIX = 2000.0; STEP = 0.05; EPS = 5e-3
def mul(A, B): return (A[0]*B[0]+A[1]*B[2], A[0]*B[1]+A[1]*B[3], A[2]*B[0]+A[3]*B[2], A[2]*B[1]+A[3]*B[3])
def inv(A): return (A[3], -A[1], -A[2], A[0])          # det 1 assumed (exact for gamma)
def step_matrix(rng, heading):
    # rotate the heading a little, then translate by STEP: delta = R(phi) A(STEP) R(-phi) in float64
    c, s = math.cos(heading / 2), math.sin(heading / 2); e = math.exp(STEP / 2)
    R = (c, s, -s, c); Ri = (c, -s, s, c); A = (e, 0.0, 0.0, 1 / e)
    return mul(mul(R, A), Ri)
def reduce_h(h):
    """Integer moves sigma with sigma h . i in the standard fundamental domain. Returns (sigma, h')."""
    sig = (1, 0, 0, 1)
    for _ in range(200):
        a, b, c, d = h; z = complex(a * 1j + b) / complex(c * 1j + d)
        n = round(z.real)
        if n: T = (1, -n, 0, 1); h = mul(T, h); sig = mul(T, sig); continue
        if abs(z) < 1 - 1e-12: S = (0, -1, 1, 0); h = mul(S, h); sig = mul(S, sig); continue
        break
    return sig, h
def draw(M, p, q, ctx):     # disk point of M^-1 (p/q); ctx = float or mpmath
    a, b, c, d = inv(M); num = a * p + b * q; den = c * p + d * q
    if ctx is float:
        x = num / den if den != 0 else float('inf')
        return complex(1, 0) if math.isinf(x) else (x - 1j) / (x + 1j)
    x = num / den; return (x - 1j) / (x + 1j)
def visible(hm):            # Farey tiles drawn with arc >= EPS by camera hm (an mpmath matrix near the fund. domain)
    out = []
    for t in farey_tiles(EPS / 40):
        ws = [complex(draw(hm, mp.mpf(p), mp.mpf(q), 'mp')) for p, q in t]
        if covering_arc([math.atan2(w.imag, w.real) % (2*math.pi) for w in ws]) >= EPS: out.append(t)
    return out
def mp_reduce(M):
    """Exact-in-mpmath reduction: integer gamma with M = gamma * hm and hm . i in the fundamental domain."""
    gam = (1, 0, 0, 1); hm = M
    for _ in range(100000):
        a, b, c, d = hm; z = (a * 1j + b) / (c * 1j + d); n = int(mp.nint(z.real))
        if n: hm = mul((1, -n, 0, 1), hm); gam = mul(gam, (1, n, 0, 1)); continue
        if abs(z) < 1: hm = mul((0, -1, 1, 0), hm); gam = mul(gam, (0, 1, -1, 0)); continue
        return gam, hm
def errors(gam, hm, render):
    """Max pixel error over the visible tiles of camera gam*hm, rendering each vertex gamma.(p0/q0) with `render`."""
    e = 0.0; tiles = visible(hm)
    G = tuple(mp.mpf(v) for v in gam); M = mul(G, hm)
    for t in tiles:
        for p0, q0 in t:
            p, q = gam[0]*p0 + gam[1]*q0, gam[2]*p0 + gam[3]*q0
            wt = complex(draw(M, mp.mpf(p), mp.mpf(q), 'mp'))
            e = max(e, abs(render(p, q, p0, q0) - wt))
    return e * R_PIX, len(tiles)
def run(dist, seed=1):
    rng = random.Random(seed); heading = 0.0
    gf = (1.0, 0.0, 0.0, 1.0); gam = (1, 0, 0, 1); h = (1.0, 0.0, 0.0, 1.0)
    for _ in range(int(dist / STEP)):
        heading += rng.gauss(0, 0.02); dl = step_matrix(rng, heading)
        gf = mul(gf, dl)
        if RENORM: k = 1 / math.sqrt(abs(gf[0]*gf[3] - gf[1]*gf[2])); gf = tuple(k * v for v in gf)
        h = mul(h, dl); sig, h = reduce_h(h); gam = mul(gam, inv(sig))
    # float64 camera, judged against its own state (exact mpmath copy of the float entries)
    GF = tuple(mp.mpf(v) for v in gf); g1, h1 = mp_reduce(GF)
    ef, nf = errors(g1, h1, lambda p, q, p0, q0: draw(gf, float(p), float(q), float))
    # gamma*h camera, judged against its own state
    ex, nx = errors(gam, tuple(mp.mpf(v) for v in h), lambda p, q, p0, q0: draw(h, float(p0), float(q0), float))
    dh = float(mp.acosh((GF[0]**2 + GF[1]**2 + GF[2]**2 + GF[3]**2) / 2))
    return dh, nf, nx, max(map(abs, g1)), ef, ex, abs(float(GF[0]*GF[3] - GF[1]*GF[2]) - 1)
print("float64 camera renormalised to det 1 every step: %s" % RENORM)
print("each method is judged against an exact rendering of its OWN camera state; R = %d px" % R_PIX)
for dist in [float(a) for a in sys.argv[1:]] or [5, 10, 20, 30, 40, 60, 80, 100, 150, 200]:
    d, nf, nx, gmax, ef, ex, ddet = run(dist)
    print("distance %6.1f  rooms %5d/%5d  |gamma| ~ 1e%-3d  float64 g: max error %9.2e px (det-1 = %.0e) | gamma*h: %9.2e px" % (
        d, nf, nx, int(mp.log10(gmax)), ef, ddet, ex), flush=True)
